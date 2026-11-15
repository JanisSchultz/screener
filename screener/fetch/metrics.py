"""Phase 4.1 audit metrics from annual series ({fiscal_year: value}, money in units, not millions).

Shared by the SEC (US) and Yahoo (EU / gaps) fetchers so both produce identical definitions.
"""
from __future__ import annotations

import math
from statistics import median

DEFAULT_TAX = 0.21
ROIC_YEARS = 5                  # median ROIC over the latest 5 fiscal years (one cycle; matches the PAR window)
LEASE_DEP_RATE = 0.20           # IFRS-16 right-of-use depreciation ≈ 20% of average lease liabilities (~5y avg term)
DA_IMPAIRMENT_CAP = 1.5         # D&A above 1.5× the prior-3y median is treated as a one-off impairment / write-down
MA_STOCK_FUNDED = 1.03          # share count up ≥ 3% in a year = stock-funded deal (already netted out of g0 by S_t)
MA_GOODWILL_GROWTH = 0.02       # an acquisition year needs goodwill up > 2%; other intangible growth is not M&A


def clean_da(da: dict, capex: dict | None = None) -> dict:
    """Impairment guard: cap a year's D&A at DA_IMPAIRMENT_CAP × the median of the prior 3 reported years, but only when
    the spike is transient — so one-off write-downs folded into D&A (e.g. COLO B FY2026 Kerecis) are not added back
    as recurring earnings, while genuine step-ups are kept: capex rising ≥ 1.5× alongside (MSFT AI build-out) or the
    following year staying ≥ 1.25× the prior median (merger amortisation, e.g. NSIS / Chr. Hansen)."""
    out, capex = {}, capex or {}
    yrs = sorted(y for y, v in (da or {}).items() if v is not None)
    for idx, y in enumerate(yrs):
        v = abs(da[y])
        prior = [abs(da[p]) for p in yrs[max(0, idx - 3):idx] if 1 <= y - p <= 4]
        if len(prior) >= 3:
            ref = median(prior)
            if ref > 0 and v > DA_IMPAIRMENT_CAP * ref:
                cx_prior = [abs(capex[p]) for p in yrs[max(0, idx - 3):idx] if capex.get(p) is not None]
                cx_up = (capex.get(y) is not None and cx_prior and median(cx_prior) > 0
                         and abs(capex[y]) >= DA_IMPAIRMENT_CAP * median(cx_prior))
                nxt = da.get(y + 1)
                persistent = nxt is not None and abs(nxt) >= 1.25 * ref
                if not (cx_up or persistent):
                    v = DA_IMPAIRMENT_CAP * ref
        out[y] = v
    return out


def owner_addback(s: dict, y: int) -> float:
    """Owner-earnings add-back for fiscal year y: MAX(0, D&A − CapEx − IFRS-16 lease depreciation proxy).
    D&A above maintenance capex is added back to net income; lease depreciation (rent paid through financing cash
    flow under IFRS 16) is deducted first so it is not treated as free cash. s['lease'] is empty for US GAAP filers.
    When consolidated D&A/CapEx includes partially-owned subsidiaries (minority_interest / nci), scale the add-back
    to the common shareholders' share of consolidated profit/equity."""
    da, cx, lease = s.get("da") or {}, s.get("capex") or {}, s.get("lease") or {}
    if da.get(y) is None or cx.get(y) is None:
        return 0.0
    l_cur, l_prev = lease.get(y), lease.get(y - 1)
    l_avg = (abs(l_cur) + abs(l_prev)) / 2 if (l_cur is not None and l_prev is not None) else abs(l_cur or 0.0)
    raw_add = max(0.0, abs(da[y]) - abs(cx[y]) - LEASE_DEP_RATE * l_avg)
    if raw_add <= 0.0:
        return 0.0
    ni_y = (s.get("ni") or {}).get(y)
    mi_y = (s.get("minority_interest") or {}).get(y)
    if ni_y and ni_y > 0 and mi_y and abs(mi_y) > 0:
        common_share = ni_y / (ni_y + abs(mi_y))
        return raw_add * max(0.25, min(1.0, common_share))
    return raw_add


def _last_years(series: dict, n: int, last: int | None = None) -> list[int]:
    yrs = sorted(series)
    if last is not None:
        yrs = [y for y in yrs if last - n < y <= last]
    return yrs[-n:]


def cagr(series: dict, years: int):
    """CAGR between the latest year and `years` earlier; None if either end missing or non-positive."""
    if not series:
        return None
    end = max(series)
    start = end - years
    a, b = series.get(start), series.get(end)
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return (b / a) ** (1 / years) - 1


def exp_weighted_ols_cagr(
    series: dict,
    max_years: int = 10,
    half_life: float = 5.0,
    last: int | None = None,
) -> tuple[float | None, int | None]:
    """Compute 10-Year Exponentially-Weighted Log-Linear OLS growth rate (half-life = 5.0y),
    with automatic permanent spinoff/divestiture perimeter reset and single-year M&A/outlier winsorization."""
    if not series:
        return None, None
    yrs_all = sorted(y for y, v in series.items() if v is not None and v > 0 and (last is None or y <= last))
    if len(yrs_all) < 2:
        return None, None
    end_y = yrs_all[-1]
    yrs = [y for y in yrs_all if end_y - max_years <= y <= end_y]
    if len(yrs) < 2:
        return None, None

    # 1. Detect permanent corporate breakup / spinoff perimeter resets (e.g. GE 2023, HWM 2019, G24.DE 2019):
    # where revenue/cost drops >32% in one year AND the 3-year post-reset window remains <78% of the pre-drop level.
    reset_idx = 0
    for i in range(1, len(yrs)):
        y0, y1 = yrs[i - 1], yrs[i]
        if series[y1] / series[y0] < 0.68 and len(yrs[i:]) >= 3:
            if i < 2 or series[y0] <= 1.35 * series[yrs[i - 2]]:
                post3_max = max(series[y] for y in yrs[i : i + 3])
                if post3_max < 0.78 * series[y0]:
                    reset_idx = i
    if reset_idx > 0:
        yrs = yrs[reset_idx:]

    # 2. Extract annual log-transitions and winsorize isolated 1-year M&A / restructuring jumps
    yoy_logs = []
    for i in range(1, len(yrs)):
        y0, y1 = yrs[i - 1], yrs[i]
        dt_y = y1 - y0
        if 1 <= dt_y <= 2:
            yoy_logs.append(math.log(series[y1] / series[y0]) / dt_y)
    if not yoy_logs:
        span_tot = yrs[-1] - yrs[0]
        if span_tot > 0:
            return (series[yrs[-1]] / series[yrs[0]]) ** (1.0 / span_tot) - 1.0, span_tot
        return None, None

    med_log = median(yoy_logs)
    clean_pts = [(yrs[0], 0.0)]
    cum = 0.0
    for i in range(1, len(yrs)):
        y0, y1 = yrs[i - 1], yrs[i]
        dt_y = y1 - y0
        raw_step = math.log(series[y1] / series[y0]) / dt_y
        if len(yoy_logs) >= 4 and (raw_step < med_log - 0.22 or raw_step > med_log + 0.30):
            adj_step = max(med_log - 0.15, min(med_log + 0.20, 0.5 * raw_step + 0.5 * med_log))
        else:
            adj_step = raw_step
        cum += adj_step * dt_y
        clean_pts.append((y1, cum))

    # 3. Exponentially-Weighted Least Squares (WLS) regression slope over clean_pts
    lam = math.log(2.0) / half_life
    ws, xs, ys = [], [], []
    for t_y, val_log in clean_pts:
        w = math.exp(-lam * (end_y - t_y))
        ws.append(w)
        xs.append(float(t_y - yrs[0]))
        ys.append(val_log)
    w_sum = sum(ws)
    x_bar = sum(w * x for w, x in zip(ws, xs)) / w_sum
    y_bar = sum(w * y for w, y in zip(ws, ys)) / w_sum
    num = sum(w * (x - x_bar) * (y - y_bar) for w, x, y in zip(ws, xs, ys))
    den = sum(w * ((x - x_bar) ** 2) for w, x in zip(ws, xs))
    if den <= 1e-9:
        return None, None
    beta = num / den
    wls_cagr = math.exp(beta) - 1.0
    span_tot = yrs[-1] - yrs[0]
    # Guard against asymmetric V-shaped slump/rebound inflation (e.g. 2020 COVID crash clipped on the way down
    # while multi-year recovery is accumulated on the way up): if any year dropped >15% and later recovered
    # above the pre-drop level, bound WLS by the actual post-reset full-span CAGR.
    if span_tot > 0 and any(
        series[yrs[i]] < 0.85 * series[yrs[i - 1]] and series[yrs[-1]] >= series[yrs[i - 1]]
        for i in range(1, len(yrs))
    ):
        span_cagr = (series[yrs[-1]] / series[yrs[0]]) ** (1.0 / span_tot) - 1.0
        wls_cagr = min(wls_cagr, span_cagr)
    return wls_cagr, span_tot


G_BASE_STAT = 0.030
G_MAX_STAT = 0.130
TAU_PRIOR_STAT = 0.060


def compress_g0(raw_g: float, g_base: float = G_BASE_STAT, g_max: float = G_MAX_STAT) -> float:
    """Pillar 4b: Smooth Bayesian hyperbolic-tangent tail compression above g_base with asymptote g_max."""
    if raw_g <= g_base:
        return max(0.0, raw_g)
    span = max(1e-6, g_max - g_base)
    return g_base + span * math.tanh((raw_g - g_base) / span)


def theil_sen_organic_cagr(
    series: dict,
    shares: dict | None = None,
    max_years: int = 10,
    min_span: int = 5,
    last: int | None = None,
) -> tuple[float | None, float | None, float | None, int | None]:
    """Pillar 1 & 2: Dilution-adjusted per-share series + Cycle-Spanning Theil-Sen non-parametric estimator.
    Returns (med_cagr, p25_cagr, mad_se, span_years)."""
    if not series:
        return None, None, None, None
    yrs_all = sorted(y for y, v in series.items() if v is not None and v > 0 and (last is None or y <= last))
    if len(yrs_all) < 2:
        return None, None, None, None
    end_y = yrs_all[-1]
    yrs = [y for y in yrs_all if end_y - max_years <= y <= end_y]
    if len(yrs) < 2:
        return None, None, None, None

    # 1. Permanent corporate breakup / spinoff perimeter reset (e.g. GE 2023, HWM 2019, G24.DE 2019)
    reset_idx = 0
    for i in range(1, len(yrs)):
        y0, y1 = yrs[i - 1], yrs[i]
        if series[y1] / series[y0] < 0.68 and len(yrs[i:]) >= 3:
            if i < 2 or series[y0] <= 1.35 * series[yrs[i - 2]]:
                post3_max = max(series[y] for y in yrs[i : i + 3])
                if post3_max < 0.78 * series[y0]:
                    reset_idx = i
    if reset_idx > 0:
        yrs = yrs[reset_idx:]

    span_tot = yrs[-1] - yrs[0]
    if span_tot <= 0:
        return None, None, None, None

    # 2. Dilution-Only Share Index S_t: penalizes SBC & stock-merger share issuance (up to +65%/yr)
    # in the exact year it occurs, without double-counting share buybacks (Shares_t < Shares_{t-1}).
    sh_idx = {yrs[0]: 1.0}
    cur_idx = 1.0
    if shares:
        for i in range(1, len(yrs)):
            y0, y1 = yrs[i - 1], yrs[i]
            s0, s1 = shares.get(y0), shares.get(y1)
            dt_y = y1 - y0
            if s0 and s1 and s0 > 0 and s1 > s0 and dt_y > 0:
                ann_ratio = (s1 / s0) ** (1.0 / dt_y)
                if ann_ratio <= 1.65:
                    cur_idx *= (s1 / s0)
            sh_idx[y1] = cur_idx
    else:
        for y in yrs:
            sh_idx[y] = 1.0

    log_vals = {y: math.log(series[y] / sh_idx[y]) for y in yrs}

    # 3. Cycle-Spanning Theil-Sen pairwise annualized log-slopes (span >= min_span, fallback >= 3, >= 1)
    slopes = []
    for req_span in (min_span, 3, 1):
        slopes = [
            (log_vals[yrs[j]] - log_vals[yrs[i]]) / (yrs[j] - yrs[i])
            for i in range(len(yrs))
            for j in range(i + 1, len(yrs))
            if yrs[j] - yrs[i] >= req_span
        ]
        if slopes:
            break
    if not slopes:
        return None, None, None, None

    slopes.sort()
    n = len(slopes)
    med_b = median(slopes)
    p25_b = slopes[max(0, int(0.25 * (n - 1)))]
    mad = median([abs(s - med_b) for s in slopes])
    return math.exp(med_b) - 1.0, math.exp(p25_b) - 1.0, 1.4826 * mad, span_tot


def statistical_organic_g0(
    sales: dict,
    nopat: dict | None = None,
    owner_earn: dict | None = None,
    shares: dict | None = None,
    max_years: int = 10,
    last: int | None = None,
) -> tuple[float | None, int | None]:
    """Pillar 3 & 4a: 3-driver triangulation (Revenue, NOPAT, Owner Earnings) on dilution-adjusted
    per-share series via Cycle-Spanning Theil-Sen, followed by Empirical Bayes precision shrinkage
    of excess growth above G_BASE_STAT (3.0%)."""
    rev_med, rev_p25, rev_se, span = theil_sen_organic_cagr(sales, shares=shares, max_years=max_years, min_span=5, last=last)
    if rev_p25 is None or span is None:
        return None, None

    nop_med, nop_p25, _, nop_span = (
        theil_sen_organic_cagr(nopat, shares=shares, max_years=max_years, min_span=5, last=last)
        if nopat else (None, None, None, None)
    )
    oe_med, oe_p25, _, oe_span = (
        theil_sen_organic_cagr(owner_earn, shares=shares, max_years=max_years, min_span=5, last=last)
        if owner_earn else (None, None, None, None)
    )

    cands_med = [rev_med]
    cands_p25 = [rev_p25]
    if nop_med is not None and nop_p25 is not None and (nop_span or 0) >= 3:
        cands_med.append(nop_med)
        cands_p25.append(nop_p25)
    if oe_med is not None and oe_p25 is not None and (oe_span or 0) >= 3:
        cands_med.append(oe_med)
        cands_p25.append(oe_p25)
    tri_med = median(cands_med)
    tri_p25 = median(cands_p25)
    g_tri = min(tri_p25, tri_med, rev_med + 0.015)

    # Refranchising guard (e.g. MCD, KO): if top-line revenue stagnated (<3.0%) due to gross-to-net royalty
    # transition while BOTH operating profit (NOPAT) and Owner Earnings P25 grew faster than revenue:
    if (
        rev_med is not None and rev_med < G_BASE_STAT
        and nop_p25 is not None and (nop_span or 0) >= 5
        and oe_p25 is not None and (oe_span or 0) >= 5
        and min(nop_p25, oe_p25) > rev_med
    ):
        g_tri = min(0.060, nop_p25, oe_p25)

    # Pillar 4a & 4b: Empirical Bayes precision shrinkage toward G_BASE_STAT = 3.0%
    # followed by smooth hyperbolic-tangent tail compression with asymptote G_MAX_STAT = 13.0%.
    se = rev_se if rev_se is not None else 0.030
    w = (TAU_PRIOR_STAT ** 2) / (TAU_PRIOR_STAT ** 2 + se ** 2)
    g_eb = G_BASE_STAT + w * (g_tri - G_BASE_STAT) if g_tri > G_BASE_STAT else g_tri
    return compress_g0(g_eb, G_BASE_STAT, G_MAX_STAT), span


def implied_shares(ni: dict, eps: dict, shares: dict) -> dict:
    """Diluted shares per year. Where net income and reported diluted EPS imply a count more than 15% away from
    the tagged share count (multi-class structures, XBRL unit errors, wrong period-end counts), use NI ÷ EPS."""
    out = dict(shares or {})
    for y, n_val in (ni or {}).items():
        e_val = (eps or {}).get(y)
        if n_val and e_val and n_val > 0 and e_val > 0:
            imp_sh = n_val / e_val
            cur_sh = out.get(y)
            if cur_sh is None or cur_sh <= 0 or not (0.85 <= cur_sh / imp_sh <= 1.18):
                out[y] = imp_sh
    return out


def true_fcf(ocf: dict, capex: dict, sbc: dict, da: dict | None = None, lease: dict | None = None) -> dict:
    """Owner FCF = OCF − IFRS-16 lease depreciation proxy − maintenance capex − SBC. Maintenance capex =
    MIN(capex, D&A − lease_dep); all capex when D&A is missing (or D&A when capex is not tagged separately)."""
    out, da, lease = {}, da or {}, lease or {}
    for y, o in ocf.items():
        if o is None:
            continue
        c_val, d_val = capex.get(y), da.get(y)
        if c_val is None and d_val is None:
            continue
        l_cur, l_prev = lease.get(y), lease.get(y - 1)
        l_avg = (abs(l_cur) + abs(l_prev)) / 2 if (l_cur is not None and l_prev is not None) else abs(l_cur or 0.0)
        lease_dep = LEASE_DEP_RATE * l_avg
        d_clean = max(0.0, abs(d_val) - lease_dep) if d_val is not None else None
        cx = min(abs(c_val), d_clean) if (c_val is not None and d_clean is not None) else abs(c_val if c_val is not None else d_clean)
        out[y] = (o - lease_dep) - cx - abs(sbc.get(y) or 0)
    return out


def roic_series(ebit: dict, tax_rate: dict, equity: dict, debt: dict, cash: dict, goodwill: dict, intang: dict,
                assets: dict | None = None):
    """Per-year ROIC = EBIT × (1 − t) / average invested capital (equity + debt − cash). Pass consolidated equity
    (incl. non-controlling interests) and total debt so the capital base matches consolidated EBIT.
    Tangible ROIC (v7.3) = the same NOPAT on invested capital less goodwill and other intangibles, floored at 1/3 of
    GAAP invested capital (so goodwill deduction can reduce the denominator by at most 2/3). No D&A add-back: removing
    the acquired assets from capital AND adding their amortisation back to NOPAT counted the same thing twice.
    Only defined while GAAP invested capital is positive — customer cash or buyback-driven negative capital (ADYEN, COR)
    leaves the tangible figure blank and roic_operating falls back to GAAP ROIC."""
    assets = assets or {}

    def ic(y, tangible):
        if y not in equity or equity[y] is None:
            return None
        raw_g = equity[y] + (debt.get(y) or 0) - (cash.get(y) or 0)
        gw_ig = (goodwill.get(y) or 0) + (intang.get(y) or 0)
        tang_oa = max(0.0, (assets.get(y) or 0) - (cash.get(y) or 0) - gw_ig)
        ic_g = raw_g if raw_g > 0 else (0.25 * tang_oa if tang_oa > 0 else raw_g)
        if not tangible:
            return ic_g
        if raw_g <= 0:
            return None
        return max(raw_g - gw_ig, (1.0 / 3.0) * raw_g)

    gaap, tang = {}, {}
    for y, e in ebit.items():
        if e is None:
            continue
        t = tax_rate.get(y)
        t = DEFAULT_TAX if t is None or not (0 <= t <= 0.40) else t
        nopat = e * (1 - t)
        for tangible, out in ((False, gaap), (True, tang)):
            cur, prev = ic(y, tangible), ic(y - 1, tangible)
            base = (cur + prev) / 2 if (cur is not None and prev is not None and cur > 0 and prev > 0) else cur
            if base is None or base <= 0:
                continue
            out[y] = max(-1.0, nopat / base)
    return gaap, tang


def ic_inputs(s: dict) -> tuple[dict, dict]:
    """Consolidated invested-capital inputs: equity + non-controlling interests, long-term + short-term debt."""
    eq, nci = s.get("equity") or {}, s.get("nci") or {}
    debt, st = s.get("debt") or {}, s.get("st_debt") or {}
    eq_ic = {y: v + (nci.get(y) or 0.0) for y, v in eq.items() if v is not None}
    debt_ic = {y: (debt.get(y) or 0.0) + (st.get(y) or 0.0) for y in set(debt) | set(st)}
    return eq_ic, debt_ic


def summarize(s: dict, price_at_year_end: dict | None = None) -> dict:
    """s: dict of annual series. Keys used: sales, ni, eps, ocf, capex, sbc, da, dividends, equity, debt, cash,
    goodwill, intang, ebit, pretax, tax, interest, assets, shares. Returns financials.csv fields."""
    g = lambda k: s.get(k) or {}
    ni, tax, interest = g("ni"), g("tax"), g("interest")
    pretax = dict(g("pretax"))
    for y, n_val in ni.items():
        if pretax.get(y) is None and n_val is not None and tax.get(y) is not None:
            pretax[y] = n_val + tax[y]
    ebit = dict(g("ebit"))
    for y, pt_val in pretax.items():
        if ebit.get(y) is None and pt_val is not None:
            ebit[y] = pt_val + abs(interest.get(y) or 0)

    fcf = true_fcf(g("ocf"), g("capex"), g("sbc"), g("da"), g("lease"))
    tax_rate = {y: (tax[y] / pretax[y]) for y in tax if pretax.get(y)}
    # Operating capital nets cash AND short-term investments (liquid treasury assets are not operating capital);
    # falls back to cash & equivalents where the combined figure is not reported.
    cash_op = {**g("cash"), **g("cash_sti")}
    eq_ic, debt_ic = ic_inputs(s)
    roic, roic_t = roic_series(ebit, tax_rate, eq_ic, debt_ic, cash_op, g("goodwill"), g("intang"), g("assets"))
    out = {}

    all_years = set(ni) | set(g("sales")) | set(g("ocf")) | set(g("equity"))
    last = max(all_years) if all_years else None

    def latest(ser, default_zero=False):
        if not ser:
            return 0.0 if (default_zero and last is not None) else None
        if last is None:
            return ser[max(ser)]
        if last in ser and ser[last] is not None:
            return ser[last]
        if (last - 1) in ser and ser[last - 1] is not None:
            return ser[last - 1]
        return 0.0 if default_zero else None

    srcs = {"ni": ni, "ocf": g("ocf"), "sbc": g("sbc"), "debt": g("debt"),
            "interest": interest, "ebit": ebit, "assets": g("assets"), "sales": g("sales"), "cash": cash_op}
    zero_default_keys = {"debt", "sbc", "interest"}
    for key, src in (("ni_ttm_m", "ni"), ("ocf_ttm_m", "ocf"), ("sbc_ttm_m", "sbc"), ("lt_debt_m", "debt"),
                     ("interest_m", "interest"), ("ebit_ttm_m", "ebit"), ("total_assets_m", "assets"),
                     ("sales_ttm_m", "sales"), ("cash_m", "cash")):
        v = latest(srcs[src], default_zero=(src in zero_default_keys))
        out[key] = None if v is None else abs(v) / 1e6 if src in ("interest", "sbc") else v / 1e6
    cx, dv, da = latest(g("capex")), latest(g("dividends"), default_zero=True), latest(g("da"))
    if cx is None and da is not None and out.get("ocf_ttm_m") is not None:
        cx = da
    out["da_ttm_m"] = None if da is None else abs(da) / 1e6
    out["capex_ttm_m"] = None if cx is None else abs(cx) / 1e6
    out["dividends_ttm_m"] = None if dv is None else abs(dv) / 1e6

    yrs = _last_years(roic, ROIC_YEARS, last)
    if yrs:
        out["roic_median"] = median(roic[y] for y in yrs)
        out["roic_years"] = len(yrs)
    # Tangible ROIC only when it exists in all but at most one year of the GAAP window: repeated years with GAAP
    # invested capital <= 0 (clearing / customer cash DB1, ADYEN; working-capital swings MCK) mean the capital base is
    # unstable and a median over the few remaining years (DB1: one tiny positive year -> 5,596%) is meaningless ->
    # GAAP ROIC. A single net-cash year (SPGI FY2021 before IHS) is tolerated.
    yt = [y for y in yrs if y in roic_t] if yrs else []
    if len(yt) < max(1, len(yrs) - 1):
        yt = []
    if yt:
        out["roic_tangible_median"] = median(roic_t[y] for y in yt)
        if (out.get("roic_median") or 0) > 0 and out["roic_tangible_median"] < out["roic_median"]:
            out["roic_tangible_median"] = out["roic_median"]
    # Operating ROIC = 5Y median of Tangible ROIC; falls back to GAAP ROIC if tangible data is unavailable
    out["roic_operating"] = out.get("roic_tangible_median") if out.get("roic_tangible_median") is not None else out.get("roic_median")
    # v7.5: years of the ROIC window with invested capital (equity + NCI + debt − cash) <= 0 — customer / clearing cash
    # (DB1, ADYEN) or buyback-shrunk equity (FTNT, VRSN); gates.active_roic then prefers a plausible ROE
    if yrs:
        out["ic_neg_years"] = sum(1 for y in yrs if y in eq_ic and eq_ic[y] + (debt_ic.get(y) or 0) - (cash_op.get(y) or 0) <= 0)

    conv_years = [y for y in _last_years(fcf, 5, last) if ni.get(y) is not None]
    ni_sum = sum(ni[y] for y in conv_years)
    if conv_years and ni_sum > 0:
        out["fcf_conv"] = sum(fcf[y] for y in conv_years) / ni_sum
        out["fcf_conv_years"] = len(conv_years)

    # Recent cash backing of earnings (latest 2 FYs): Σ OCF ÷ Σ NI. Catches mark-to-market HoldCos / insurers whose
    # latest earnings are unrealised NAV gains even when the 5Y fcf_conv still looks healthy (e.g. III.GB).
    ocf_s = g("ocf")
    yrs2 = [y for y in _last_years({y: v for y, v in ni.items() if v is not None}, 2, last) if ocf_s.get(y) is not None]
    ni2 = sum(ni[y] for y in yrs2)
    if len(yrs2) == 2 and ni2 > 0:
        out["ocf_ni_2y"] = round(sum(ocf_s[y] for y in yrs2) / ni2, 4)

    # Latest-FY owner-earnings add-back (same definition as screener/fetch/par.py owner_eps_series)
    if last is not None and g("da").get(last) is not None:
        out["owner_add_m"] = owner_addback(s, last) / 1e6

    # v4.1 normalised earnings: mid-cycle margins and cycle-average NI (up to 10 years)
    sales = g("sales")
    ni_m = {y: ni[y] / sales[y] for y in ni if ni[y] is not None and (sales.get(y) or 0) > 0}
    fcf_m = {y: fcf[y] / sales[y] for y in fcf if (sales.get(y) or 0) > 0}
    ym = _last_years(ni_m, 10, last)
    if ym:
        out["ni_margin_med"] = median(ni_m[y] for y in ym)
        out["margin_years"] = len(ym)
    yf = _last_years(fcf_m, 10, last)
    if yf:
        out["fcf_margin_med"] = median(fcf_m[y] for y in yf)
    yn = _last_years({y: v for y, v in ni.items() if v is not None}, 10, last)
    if yn:
        out["ni_avg_m"] = sum(ni[y] for y in yn) / len(yn) / 1e6

    # v4.1 banks / insurers: return on (tangible) equity on average equity
    def eq(y, tangible):
        e = g("equity").get(y)
        if e is None:
            return None
        return e - ((g("goodwill").get(y) or 0) + (g("intang").get(y) or 0) if tangible else 0)

    mi_ser, nci_ser, liab_ser = g("minority_interest"), g("nci"), g("liab")

    def cons_eq(y, tangible):
        """Consolidated equity incl. non-controlling interests = total assets − total liabilities (robust to whether the
        reported equity field already includes NCI: IBKR yes, BX no); parent equity + NCI when liabilities are missing."""
        e = eq(y, tangible)
        if e is None:
            return None
        with_nci = e + (nci_ser.get(y) or 0.0)
        a, l_ = g("assets").get(y), liab_ser.get(y)
        if a is not None and l_ is not None:
            tot = (a - l_) - ((g("goodwill").get(y) or 0) + (g("intang").get(y) or 0) if tangible else 0)
            # plausible only between parent equity and parent equity + NCI (bank liability totals can be partial: ACA)
            if 0.95 * min(e, with_nci) <= tot <= 1.05 * max(e, with_nci):
                return tot
        return with_nci

    def avg_base(y, tangible, consolidated):
        f_ = cons_eq if consolidated else eq
        cur, prev = f_(y, tangible), f_(y - 1, tangible)
        return (cur + prev) / 2 if cur is not None and prev is not None else cur

    for key, tangible in (("roe_median", False), ("rote_median", True)):
        ser = {}
        for y, n in ni.items():
            base = avg_base(y, tangible, False)
            if n is not None and base and base > 0:
                mi_y = mi_ser.get(y)
                n_eff = n
                if mi_y is not None and abs(mi_y) > 0.15 * abs(n):
                    pt_y, tx_y = pretax.get(y), tax.get(y)
                    cons_ni = n + abs(mi_y)
                    if pt_y is None or tx_y is None or abs(cons_ni - (pt_y - tx_y)) < abs(n - (pt_y - tx_y)):
                        # v7.4: consolidated profit over consolidated equity (assets − liabilities), not parent-only
                        n_eff, base = cons_ni, (avg_base(y, tangible, True) or base)
                ser[y] = n_eff / base
        yrs_e = _last_years(ser, ROIC_YEARS, last)
        if yrs_e:
            out[key] = median(ser[y] for y in yrs_e)
    if g("equity"):
        ly = max(g("equity"))
        out["equity_m"] = g("equity")[ly] / 1e6
        out["tbv_m"] = eq(ly, True) / 1e6

    for name, ser in (("bv", g("equity")), ("eps", g("eps")), ("sales", g("sales")), ("fcf", fcf)):
        for n in (10, 5, 3):
            out[f"cagr_{name}_{n}"] = cagr(ser, n)

    shares = implied_shares(ni, g("eps"), g("shares"))
    nopat_ser = {}
    for y, e_val in ebit.items():
        if e_val is not None:
            tr = tax_rate.get(y)
            tr = DEFAULT_TAX if tr is None or not (0 <= tr <= 0.40) else tr
            nopat_ser[y] = e_val * (1.0 - tr)
    owner_earn_ser = {
        y: ni[y] + owner_addback(s, y)
        for y in ni
        if ni.get(y) is not None and (ni[y] + owner_addback(s, y)) > 0
    }

    # 4-Pillar Statistical Organic Growth Estimator (Dilution-Adjusted Cycle-Spanning Theil-Sen + Empirical Bayes)
    if sales:
        s1_val = cagr(sales, 1)
        if s1_val is not None:
            out["sales_1y"] = round(s1_val, 4)
        s_stat, s_span = statistical_organic_g0(
            sales, nopat=nopat_ser, owner_earn=owner_earn_ser, shares=shares, max_years=10, last=last
        )
        if s_stat is not None and s_span is not None:
            out["sales_cagr"] = round(s_stat, 4)
            out["sales_cagr_yrs"] = s_span

    opcost_ser = {
        y: sales[y] - ebit[y]
        for y in set(sales) & set(ebit)
        if sales.get(y) is not None and ebit.get(y) is not None and sales[y] > ebit[y] and sales[y] > 0
    }
    for y, oc_v in g("opcost").items():
        if oc_v is not None and oc_v > 0:
            opcost_ser[y] = oc_v
    if opcost_ser:
        oc1_val = cagr(opcost_ser, 1)
        if oc1_val is not None:
            out["opcost_1y"] = round(max(-0.40, min(0.60, oc1_val)), 4)
        oc_med, _, _, _ = theil_sen_organic_cagr(opcost_ser, shares=shares, max_years=10, min_span=5, last=last)
        if oc_med is not None:
            out["opcost_cagr"] = round(max(-0.25, min(0.45, oc_med)), 4)

    sh_yrs = sorted(y for y, v in shares.items() if v and v > 0 and (last is None or y <= last))
    if len(sh_yrs) >= 2:
        # Use median annual YoY share reduction over latest 5 transitions so a single-year
        # M&A stock merger or IPO share-basis jump does not masquerade as chronic dilution
        yoy_bb = []
        for idx in range(1, len(sh_yrs)):
            y_prev, y_cur = sh_yrs[idx - 1], sh_yrs[idx]
            span_y = y_cur - y_prev
            if 1 <= span_y <= 2:
                ann = (shares[y_prev] / shares[y_cur]) ** (1.0 / span_y) - 1.0
                if -0.25 <= ann <= 0.20:
                    yoy_bb.append(ann)
        if yoy_bb:
            raw_bb = median(yoy_bb[-5:])
            out["buyback_yield"] = round(max(-0.05, min(0.04, raw_bb)), 4)

    pos_ni_yrs = _last_years({y: v for y, v in ni.items() if v is not None and v > 0}, 5, last)
    if pos_ni_yrs:
        ret_by_yr = [max(0.0, min(1.0, 1.0 - abs(g("dividends").get(y) or 0) / ni[y])) for y in pos_ni_yrs]
        out["retention_rate"] = round(median(ret_by_yr), 4)

    cash_ser = cash_op
    ic_ser = {y: eq_ic[y] + (debt_ic.get(y) or 0) - (cash_ser.get(y) or 0) for y in eq_ic}
    assets_ser = g("assets")
    op_assets_ser = {
        y: assets_ser[y] - (cash_ser.get(y) or 0)
        for y in assets_ser
        if assets_ser.get(y) is not None and assets_ser[y] > (cash_ser.get(y) or 0)
    }

    def _median_cap_yoy(ser: dict) -> float | None:
        yrs_pos = sorted(y for y, v in ser.items() if v is not None and v > 0 and (last is None or y <= last))
        if len(yrs_pos) < 2:
            return None
        yoy = []
        for idx in range(1, len(yrs_pos)):
            y0_c, y1_c = yrs_pos[idx - 1], yrs_pos[idx]
            sp = y1_c - y0_c
            if 1 <= sp <= 2:
                ann_g = (ser[y1_c] / ser[y0_c]) ** (1.0 / sp) - 1.0
                if -0.30 <= ann_g <= 0.50:
                    yoy.append(ann_g)
        return median(yoy[-5:]) if yoy else None

    g_oa = _median_cap_yoy(op_assets_ser)
    g_ic = _median_cap_yoy(ic_ser)
    if g_oa is not None and g_ic is not None and g_ic > 0:
        out["cap_growth"] = round(0.5 * g_oa + 0.5 * g_ic, 4)
    elif g_oa is not None:
        out["cap_growth"] = round(g_oa, 4)
    elif g_ic is not None:
        out["cap_growth"] = round(g_ic, 4)
    # M&A reinvestment rate (v7.2) = Σ max(0, Δ(goodwill + intangibles)) ÷ Σ NOPAT over the same 10-year window as g0:
    # the share of earnings spent buying growth that g0 still contains. Cash-funded deals count whether serial (CSU,
    # BNZL) or one-off (LVMH/Tiffany); stock-funded years (shares +3% or more) are skipped because the dilution index
    # S_t already strips that acquired growth from g0 (SPGI/IHS, ADI/Maxim). Feeds the RONIC blend in screener/gates.py.
    gwi = {y: (g("goodwill").get(y) or 0.0) + (g("intang").get(y) or 0.0) for y in nopat_ser
           if g("goodwill").get(y) is not None or g("intang").get(y) is not None}
    gw_yrs = sorted(y for y in gwi if last is None or y <= last)
    spend_sum = nopat_sum = 0.0
    n_trans = 0
    for y0, y1 in zip(gw_yrs, gw_yrs[1:]):
        if y1 - y0 != 1 or not nopat_ser.get(y1) or nopat_ser[y1] <= 0 or (last is not None and y1 <= last - 10):
            continue
        n_trans += 1
        nopat_sum += nopat_ser[y1]
        s0, s1 = shares.get(y0), shares.get(y1)
        if s0 and s1 and s0 > 0 and s1 > MA_STOCK_FUNDED * s0:
            continue
        # v7.4: only acquisition years (goodwill itself up > 2%) count — capitalised development (WKL, JKHY),
        # concession capex (AENA) and purchase-price reallocations (SIKA) grow intangibles without any deal
        gw0, gw1 = g("goodwill").get(y0) or 0.0, g("goodwill").get(y1) or 0.0
        if gw1 - gw0 <= MA_GOODWILL_GROWTH * max(gw0, 0.0):
            continue
        spend_sum += max(0.0, (gwi[y1] - gwi[y0]) - 0.035 * max(0.0, gwi[y0] - 3.0 * nopat_ser[y1]))
    if n_trans >= 3 and nopat_sum > 0:
        out["ma_reinvest"] = round(min(3.0, spend_sum / nopat_sum), 4)

    common_ic = sorted(y for y in set(ic_ser) & set(nopat_ser) if last is None or y <= last)
    if len(common_ic) >= 3:
        y1 = common_ic[-1]
        ic_3_5 = [y for y in common_ic[:-1] if 3 <= y1 - y <= 5]
        ic_2_5 = [y for y in common_ic[:-1] if 2 <= y1 - y <= 5]
        y0 = ic_3_5[0] if ic_3_5 else (ic_2_5[0] if ic_2_5 else None)
        if y0 is not None and y1 > y0:
            sum_pos_nopat = sum(nopat_ser[y] for y in common_ic if y0 < y <= y1 and nopat_ser[y] > 0)
            d_ic = ic_ser[y1] - ic_ser[y0]
            if sum_pos_nopat > 0 and d_ic > 0.15 * sum_pos_nopat:
                d_nopat = nopat_ser[y1] - nopat_ser[y0]
                out["roiic"] = round(max(0.0, d_nopat / d_ic), 4)

    # Buffett $1 test over the longest window up to 10 years (min 5) with prices and shares at both ends
    if price_at_year_end and shares and last:
        for window in range(10, 4, -1):
            y0 = last - window
            p0, p1 = price_at_year_end.get(y0), price_at_year_end.get(last)
            sh0, sh1 = shares.get(y0), shares.get(last)
            if None in (p0, p1, sh0, sh1):
                continue
            retained = sum((ni.get(y) or 0) - abs(g("dividends").get(y) or 0) for y in range(y0 + 1, last + 1))
            if retained <= 0:
                continue
            out["mcap_delta_m"] = (p1 * sh1 - p0 * sh0) / 1e6
            out["retained_m"] = retained / 1e6
            out["dollar_years"] = window
            break
    # v7.6 Gate 6 review numbers (3-year medians, "through the cycle"; flags only, see gates.g6_checks)
    g6_yrs = [y for y in sorted(ni) if last is not None and last - 3 < y <= last]
    nd_vals, ic_vals = [], []
    for y in g6_yrs:
        net_debt = (g("debt").get(y) or 0.0) + (g("st_debt").get(y) or 0.0) - (cash_op.get(y) or 0.0)
        oe = (ni.get(y) or 0.0) + owner_addback(s, y)
        if ni.get(y) is not None:
            nd_vals.append(net_debt / oe if oe > 0 else (0.0 if net_debt <= 0 else 99.0))
        e_y, i_y = ebit.get(y), abs(interest.get(y) or 0.0)
        if e_y is not None:
            ic_vals.append(e_y / i_y if i_y > 0 else 99.0)
    if nd_vals:
        out["g6_netdebt_yrs"] = round(median(nd_vals), 2)
    if ic_vals:
        out["g6_intcov"] = round(median(ic_vals), 2)

    out["fiscal_year"] = last
    return out


NONCASH_FLIPS, NONCASH_NI_OCF = 2, 1.2


def noncash_marks(s: dict, years: int = 5) -> str | None:
    """v7.6 data check: reported earnings dominated by non-cash marks (FX-hedge marks SAF, investment gains BRK) —
    net income changes sign >= 2 times over the latest `years` fiscal years while operating cash flow stays positive
    in every one of them, and at least one profitable year shows NI > 1.2 × OCF (gains, not just impairment losses as
    at CARL / MTX). Returns the '[auto]' note text (valuation No data) or None."""
    ni, ocf = s.get("ni") or {}, s.get("ocf") or {}
    if not ni:
        return None
    last = max(ni)
    yrs = [y for y in range(last - years + 1, last + 1) if ni.get(y) is not None]
    if len(yrs) < 4 or not all((ocf.get(y) or 0) > 0 for y in yrs):
        return None
    flips = sum(1 for a, b in zip(yrs, yrs[1:]) if (ni[a] > 0) != (ni[b] > 0))
    ratios = [ni[y] / ocf[y] for y in yrs if ni[y] > 0]
    if flips >= NONCASH_FLIPS and ratios and max(ratios) > NONCASH_NI_OCF:
        return f"earnings dominated by non-cash marks (NI sign changes {flips}x in {len(yrs)}y, NI up to {max(ratios):.1f}x OCF)"
    return None
