"""Phase 4.1 audit metrics from annual series ({fiscal_year: value}, money in units, not millions).

Shared by the SEC (US) and Yahoo (EU / gaps) fetchers so both produce identical definitions.
"""
from __future__ import annotations

from statistics import median

DEFAULT_TAX = 0.21
ROIC_YEARS = 5                  # median ROIC over the latest 5 fiscal years (one cycle; matches the PAR window)


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


def true_fcf(ocf: dict, capex: dict, sbc: dict, da: dict | None = None) -> dict:
    """Owner FCF = OCF − maintenance capex − SBC. Maintenance capex = MIN(capex, depreciation & amortisation); all
    capex when D&A is missing (or D&A when capex is not tagged separately). Outflows taken as positive."""
    out, da = {}, da or {}
    for y, o in ocf.items():
        if o is None:
            continue
        c_val, d_val = capex.get(y), da.get(y)
        if c_val is None and d_val is None:
            continue
        cx = min(abs(c_val), abs(d_val)) if (c_val is not None and d_val is not None) else abs(c_val if c_val is not None else d_val)
        out[y] = o - cx - abs(sbc.get(y) or 0)
    return out


def roic_series(ebit: dict, tax_rate: dict, equity: dict, debt: dict, cash: dict, goodwill: dict, intang: dict,
                assets: dict | None = None):
    """Per-year ROIC = EBIT × (1 − t) / average invested capital (equity + debt − cash).
    Tangible ROIC deducts goodwill and other intangibles from invested capital, floored at 1/3 of GAAP invested
    capital (so goodwill deduction can reduce the capital denominator by at most 2/3, eliminating artificial
    200% division-by-zero spikes when goodwill/buybacks exceed book equity)."""
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
        if ic_g <= 0:
            return None
        return max(raw_g - gw_ig, (1.0 / 3.0) * ic_g)

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

    fcf = true_fcf(g("ocf"), g("capex"), g("sbc"), g("da"))
    tax_rate = {y: (tax[y] / pretax[y]) for y in tax if pretax.get(y)}
    roic, roic_t = roic_series(ebit, tax_rate, g("equity"), g("debt"), g("cash"), g("goodwill"), g("intang"), g("assets"))
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
        if (last - 1) in ser and ser[last - 1] is not None and not default_zero:
            return ser[last - 1]
        return 0.0 if default_zero else None

    srcs = {"ni": ni, "ocf": g("ocf"), "sbc": g("sbc"), "debt": g("debt"),
            "interest": interest, "ebit": ebit, "assets": g("assets"), "sales": g("sales"), "cash": g("cash")}
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
    yt = _last_years(roic_t, ROIC_YEARS, last)
    if yt:
        out["roic_tangible_median"] = median(roic_t[y] for y in yt)
        if (out.get("roic_median") or 0) > 0 and out["roic_tangible_median"] < out["roic_median"]:
            out["roic_tangible_median"] = out["roic_median"]
    # Operating ROIC = 5Y median of Tangible ROIC; falls back to GAAP ROIC if tangible data is unavailable
    out["roic_operating"] = out.get("roic_tangible_median") if out.get("roic_tangible_median") is not None else out.get("roic_median")

    conv_years = [y for y in _last_years(fcf, 5, last) if ni.get(y) is not None]
    ni_sum = sum(ni[y] for y in conv_years)
    if conv_years and ni_sum > 0:
        out["fcf_conv"] = sum(fcf[y] for y in conv_years) / ni_sum
        out["fcf_conv_years"] = len(conv_years)

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

    for key, tangible in (("roe_median", False), ("rote_median", True)):
        ser = {}
        for y, n in ni.items():
            cur, prev = eq(y, tangible), eq(y - 1, tangible)
            base = (cur + prev) / 2 if cur is not None and prev is not None else cur
            if n is not None and base and base > 0:
                ser[y] = n / base
        yrs_e = _last_years(ser, 10, last)
        if yrs_e:
            out[key] = median(ser[y] for y in yrs_e)
    if g("equity"):
        ly = max(g("equity"))
        out["equity_m"] = g("equity")[ly] / 1e6
        out["tbv_m"] = eq(ly, True) / 1e6

    for name, ser in (("bv", g("equity")), ("eps", g("eps")), ("sales", g("sales")), ("fcf", fcf)):
        for n in (10, 5, 3):
            out[f"cagr_{name}_{n}"] = cagr(ser, n)

    # v6.32 3-Anchor + Logarithmic Mauboussin Growth Engine multi-year inputs (incl. OpCost = Sales - EBIT)
    if sales:
        s_end = max(sales)
        s1_val = cagr(sales, 1)
        if s1_val is not None:
            out["sales_1y"] = round(s1_val, 4)
        for span in (5, 4, 3, 2):
            s0, s1 = sales.get(s_end - span), sales.get(s_end)
            if s0 is not None and s1 is not None and s0 > 0 and s1 > 0:
                out["sales_cagr"] = round((s1 / s0) ** (1.0 / span) - 1.0, 4)
                out["sales_cagr_yrs"] = span
                break

    opcost_ser = {
        y: sales[y] - ebit[y]
        for y in set(sales) & set(ebit)
        if sales.get(y) is not None and ebit.get(y) is not None and sales[y] > ebit[y] > 0
    }
    if opcost_ser:
        oc_end = max(opcost_ser)
        oc1_val = cagr(opcost_ser, 1)
        if oc1_val is not None and -0.40 <= oc1_val <= 0.60:
            out["opcost_1y"] = round(oc1_val, 4)
        for span in (5, 4, 3, 2):
            oc0, oc1 = opcost_ser.get(oc_end - span), opcost_ser.get(oc_end)
            if oc0 is not None and oc1 is not None and oc0 > 0 and oc1 > 0:
                oc_c = (oc1 / oc0) ** (1.0 / span) - 1.0
                if -0.25 <= oc_c <= 0.45:
                    out["opcost_cagr"] = round(oc_c, 4)
                break

    shares = implied_shares(ni, g("eps"), g("shares"))
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

    eq_ser, debt_ser, cash_ser = g("equity"), g("debt"), g("cash")
    ic_ser = {y: eq_ser[y] + (debt_ser.get(y) or 0) - (cash_ser.get(y) or 0)
              for y in eq_ser if eq_ser.get(y) is not None}
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
    nopat_ser = {}
    for y, e_val in ebit.items():
        if e_val is not None:
            tr = tax_rate.get(y)
            tr = DEFAULT_TAX if tr is None or not (0 <= tr <= 0.40) else tr
            nopat_ser[y] = e_val * (1.0 - tr)
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
    out["fiscal_year"] = last
    return out
