"""Python reference implementation of the 6 Munger Quality Gates and the Quantitative PAR maths."""
from __future__ import annotations

import math

from . import config as C


def params(meta: dict) -> dict:
    p = {nm: val for _, ps in C.PARAMETER_GROUPS for nm, _, val, _, _ in ps}
    p.update(meta.get("parameters", {}))
    return p


def gate_status(company: dict, p: dict, g6_default: str | None = None, in_market: str = "Y") -> dict:
    """'pass' / 'fail' / 'blank' (not yet reviewed) per gate key in C.GATES order."""
    v = lambda c: company.get(c) if company.get(c) not in (None, "") else None
    g2 = v("2") or ("N" if in_market == "N" else "Y")
    g6 = v("6") or (g6_default or None)
    num = lambda c, thr: "blank" if not isinstance(v(c), (int, float)) else ("pass" if v(c) >= thr else "fail")
    yn = lambda x: "blank" if x is None else ("fail" if x == "N" else "pass")
    if v("3b") == "N" or v("3a") == "None":
        g3 = "fail"
    elif v("3b") is None or v("3a") is None:
        g3 = "blank"
    else:
        g3 = "pass"
    return {"1": yn(v("1")), "2": yn(g2), "3b": g3, "4": num("4", p["thr_cap"]),
            "5": num("5", p["thr_culture"]), "6": yn(g6)}


def gate_results(company: dict, p: dict, g6_default: str | None = None, in_market: str = "Y") -> dict:
    st = gate_status(company, p, g6_default, in_market)
    return {"status": st, "ok": {k: s_ == "pass" for k, s_ in st.items()}}


def phase_results(company: dict, p: dict, g6_default: str | None = None, in_market: str = "Y") -> dict:
    """First non-waived failure or blank decides; calamity='Y' may waive Gates 3b, 5, and/or 6 only."""
    g = gate_results(company, p, g6_default, in_market)
    st = g["status"]
    calamity = company.get("calamity") == "Y"
    has_3a = company.get("3a") not in (None, "")
    no_moat = company.get("3a") == "None"
    failed = [(k, lbl, ph) for k, lbl, ph in C.GATES if st[k] == "fail"]

    for k, lbl, ph in C.GATES:
        if k == "3b":
            if no_moat or (st[k] == "fail" and not calamity):
                return {**g, "failed": failed, "waived": [], "rejected_at": lbl, "review_at": "", "result": C.RES_REJ[ph]}
            if not has_3a or company.get("3b") in (None, ""):
                return {**g, "failed": failed, "waived": [], "rejected_at": "", "review_at": lbl, "result": C.RES_REVIEW}
        elif k in C.CALAMITY_GATES:
            if st[k] == "fail" and not calamity:
                return {**g, "failed": failed, "waived": [], "rejected_at": lbl, "review_at": "", "result": C.RES_REJ[ph]}
            if st[k] == "blank":
                return {**g, "failed": failed, "waived": [], "rejected_at": "", "review_at": lbl, "result": C.RES_REVIEW}
        else:
            if st[k] == "fail":
                return {**g, "failed": failed, "waived": [], "rejected_at": lbl, "review_at": "", "result": C.RES_REJ[ph]}
            if st[k] == "blank":
                return {**g, "failed": failed, "waived": [], "rejected_at": "", "review_at": lbl, "result": C.RES_REVIEW}

    waived = [(k, lbl, ph) for k, lbl, ph in C.GATES if k in C.CALAMITY_GATES and st[k] == "fail"]
    res = C.RES_CALAMITY if waived else C.RES_QPASS
    return {**g, "failed": failed, "waived": waived, "rejected_at": "", "review_at": "", "result": res}


def g6_default_lookup(meta: dict) -> dict:
    """Pre-Screen sub-industry default for a blank Gate 6 ('N' or None)."""
    return {(r["sector"], r["sub_industry"]): (r.get("g6_default") or None) for r in meta.get("prescreen", [])}


def market_lookup(meta: dict) -> dict:
    return {r["country"]: (r.get("in_market") or "Y") for r in meta.get("markets", [])}


def results(meta: dict) -> dict:
    """{company id: phase_results} using the Pre-Screen sub-industry and market tables."""
    p, d6, mk = params(meta), g6_default_lookup(meta), market_lookup(meta)
    return {c["id"]: phase_results(c, p, d6.get((c["sector"], c["sub_industry"])), mk.get(c.get("country"), "Y"))
            for c in meta["companies"]}


def funnel_ids(meta: dict, include_calamity: bool = True) -> list[str]:
    res = results(meta)
    allowed = C.FUNNEL_RESULTS if include_calamity else (C.RES_QPASS,)
    return [c["id"] for c in meta["companies"] if res[c["id"]]["result"] in allowed]


# ------------------------------------------------------------------ Quantitative PAR maths (reference)
def uses_gaap_roic(sub_industry: str | None) -> bool:
    """Return True for Balance-Sheet Financials and IFRIC-12 Infrastructure Concessions where book capital / concession intangibles are the true operating capital base."""
    if not sub_industry or not isinstance(sub_industry, str):
        return False
    s = sub_industry.strip()
    if "Insurance Brokers" in s or "Asset Management & Custody Banks" in s or "Investment Banking & Brokerage" in s:
        return False
    return any(
        kw in s
        for kw in (
            "Insurance",
            "Reinsurance",
            "Multi-Sector Holdings",
            "Banks",
            "Construction & Engineering",
            "Highways & Railtracks",
        )
    )


def is_mtm_holdco(
    sub_industry: str | None,
    fcf_conv: float | None,
    peak_eps_est: float | None,
    mult_high_5y: float | None = None,
) -> bool:
    """Return True for Mark-to-Market HoldCos / Insurers where reported EPS already captures unrealized portfolio NAV appreciation."""
    if not sub_industry or not isinstance(sub_industry, str) or peak_eps_est is not None:
        return False
    s = sub_industry.strip()
    if "Insurance Brokers" in s:
        return False
    if not ("Multi-Sector Holdings" in s or "Insurance" in s):
        return False
    if fcf_conv is not None:
        return fcf_conv < 0.25
    return "Multi-Sector Holdings" in s and (mult_high_5y is None or mult_high_5y < 12.0)


def is_finite_concession(sub_industry: str | None, fcf_conv: float | None) -> bool:
    """Return True for IFRIC-12 Infrastructure Concessions where concession assets amortize and revert to the state at expiry (D&A >> CapEx)."""
    if not sub_industry or not isinstance(sub_industry, str):
        return False
    s = sub_industry.strip()
    if not ("Construction & Engineering" in s or "Highways & Railtracks" in s):
        return False
    return fcf_conv is not None and fcf_conv > 1.25


def explicit_dcf_multiple(
    g0: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.035,
    roic_term_base: float = 0.12,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
) -> tuple[float, float, float, float]:
    """Compute Explicit N-Year Mauboussin-Fade DCF Fair Value P/E Multiple (v6.35):
    Returns (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share).
    Each year t = 1..N (N = Gate 4 CAP), organic growth g_t and ROIC_t fade linearly from
    (g0, roic0) at t=1 down to (g_term, roic_term) at the end of CAP, generating
    FCF_t = E_t * (1 - g_t / ROIC_t), plus Year-N Gordon Growth terminal value."""
    roic_start = max(0.05, float(roic0))
    if mtm_holdco:
        nav_pe = 1.0 / roic_start
        return nav_pe, nav_pe, 0.0, 1.0
    n = max(1, int(round(float(n_cap) if (n_cap is not None and n_cap > 0) else 20.0)))
    roic_end = max(roic_term_base, min(roic_start, 0.20))
    reinv_1 = min(0.95, max(0.0, g0) / roic_start)
    pv_stage1 = 0.0
    e_t = 1.0
    for t in range(1, n + 1):
        frac = (t - 1.0) / float(n)
        g_t = g0 - frac * (g0 - g_term)
        roic_t = roic_start - frac * (roic_start - roic_end)
        e_t = e_t * (1.0 + g_t)
        reinv_t = min(0.95, max(0.0, g_t) / max(0.05, roic_t))
        fcf_t = e_t * (1.0 - reinv_t)
        pv_stage1 += fcf_t / ((1.0 + r) ** t)
    if finite_conc:
        return pv_stage1, pv_stage1, 0.0, 1.0 - reinv_1
    reinv_term = max(0.0, g_term) / roic_end
    fcf_n1 = e_t * (1.0 + g_term) * (1.0 - reinv_term)
    tv_n = fcf_n1 / max(0.01, r - g_term)
    pv_stage2 = tv_n / ((1.0 + r) ** n)
    return pv_stage1 + pv_stage2, pv_stage1, pv_stage2, 1.0 - reinv_1


def solve_implied_dcf_growth(
    target_pe: float | None,
    g0_ref: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.035,
    roic_term_base: float = 0.12,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
) -> float | None:
    """Solve for the exact starting organic growth rate g_market (fading to g_term over CAP N at discount rate r)
    that equates Explicit Mauboussin-Fade DCF P/E to target_pe (Current Multiple)."""
    if target_pe is None or target_pe <= 0:
        return None
    if mtm_holdco:
        base_pe = 1.0 / max(0.05, float(roic0))
        return round(g0_ref * (target_pe / base_pe), 4) if base_pe > 0 else None
    ref_pe, _, _, _ = explicit_dcf_multiple(g0_ref, roic0, n_cap, r, g_term, roic_term_base, finite_conc, mtm_holdco)
    if abs(ref_pe - target_pe) < 1e-6:
        return round(g0_ref, 4)
    lo, hi = -0.25, 0.60
    for _ in range(36):
        mid = 0.5 * (lo + hi)
        pe_mid, _, _, _ = explicit_dcf_multiple(mid, roic0, n_cap, r, g_term, roic_term_base, finite_conc, mtm_holdco)
        if pe_mid < target_pe:
            lo = mid
        else:
            hi = mid
    return round(0.5 * (lo + hi), 4)


def solve_irr_5y(
    price: float | None,
    par_val: float | None,
    g_exp: float | None,
    dy: float | None = 0.0,
) -> float | None:
    """Solve for the textbook 5-Year Cash-Flow IRR satisfying:
    Price = sum_{t=1..5} [D_0 * (1 + g_exp)^t / (1 + IRR)^t] + [PAR_Val * (1 + g_exp)^5 / (1 + IRR)^5]
    Using the substitution u = (1 + g_exp) / (1 + IRR), this reduces to the strictly monotonic polynomial:
    dy * (u + u^2 + u^3 + u^4 + u^5) + (PAR_Val / Price) * u^5 = 1."""
    if not price or price <= 0 or not par_val or par_val <= 0 or g_exp is None or g_exp <= -1.0:
        return None
    d = max(0.0, float(dy or 0.0))
    r_par = float(par_val) / float(price)
    if d <= 1e-12:
        return (1.0 + g_exp) * (r_par ** 0.2) - 1.0
    u = (r_par ** -0.2) / (1.0 + d)
    for _ in range(12):
        u2 = u * u
        u3 = u2 * u
        u4 = u3 * u
        u5 = u4 * u
        f_val = d * (u + u2 + u3 + u4 + u5) + r_par * u5 - 1.0
        if abs(f_val) < 1e-12:
            break
        f_deriv = d * (1.0 + 2.0 * u + 3.0 * u2 + 4.0 * u3 + 5.0 * u4) + 5.0 * r_par * u4
        if f_deriv <= 0:
            break
        u = max(1e-6, u - f_val / f_deriv)
    return (1.0 + g_exp) / u - 1.0


def par_valuation(
    fin: dict,
    p: dict = None,
    cap: float | int | None = None,
    moat: str | None = None,
    sub_industry: str | None = None,
) -> dict:
    """Python reference implementation of the v6.35 Explicit Mauboussin-Fade DCF (r = 8.5%) & Operating Cost Growth Ceiling valuation."""
    f = lambda k: None if (fin.get(k) is None or (isinstance(fin.get(k), float) and math.isnan(fin.get(k)))) else (fin.get(k) if isinstance(fin.get(k), (int, float)) else None)
    price = f("price")
    mc = f("market_cap_m")
    ni = f("ni_ttm_m")
    peak_eps_override = f("peak_eps_est")
    if peak_eps_override is not None:
        peak_eps = peak_eps_override
    else:
        oe_peak = f("peak_oe_eps")
        # Current Owner EPS inferred from latest-FY Net Income + max(0, D&A − CapEx) and Market Cap / Price,
        # so both sides of the comparison are on the same Owner EPS basis as peak_oe_eps (add-back identical to
        # screener/fetch/par.py owner_eps_series); a GAAP EPS here would spuriously haircut amortisation-heavy names.
        da_l, cx_l = f("da_ttm_m"), f("capex_ttm_m")
        oe_add = max(0.0, abs(da_l) - abs(cx_l or 0.0)) if da_l is not None else 0.0
        cur_eps = (price * ((ni + oe_add) / mc)) if (mc and mc > 0 and ni is not None and price and price > 0) else oe_peak
        fin_note_str = str(fin.get("fin_note") or "")
        auto_note = fin_note_str.split("[auto]", 1)[1] if "[auto]" in fin_note_str else ""
        if oe_peak is not None and cur_eps is not None:
            if "check share basis" in auto_note:
                cur_eps = oe_peak
            elif "non-cash earnings spike left out of peak" in auto_note or cur_eps > 1.5 * oe_peak:
                cur_eps = min(cur_eps, oe_peak)
        if oe_peak is not None and cur_eps is not None and cur_eps < oe_peak:
            # 50/50 Mid-Cycle Reversion Standard: when current earnings fall below peak,
            # active earning power normalizes to the mid-cycle average between peak capacity and current reality.
            peak_eps = 0.5 * (oe_peak + max(0.0, cur_eps))
        else:
            peak_eps = oe_peak
    ml = f("mult_low_5y")
    mh = f("mult_high_5y")
    g = f("cagr_oe_eps")
    dy = (f("dividends_ttm_m") or 0.0) / mc if (mc and mc > 0 and f("dividends_ttm_m") is not None) else 0.0
    fund_cap = cap if isinstance(cap, (int, float)) else f("cap")
    moat_arch = moat if isinstance(moat, str) and moat else fin.get("moat")
    sub_ind = sub_industry if isinstance(sub_industry, str) and sub_industry else fin.get("sub_industry")
    fcf_conv_val = f("fcf_conv")
    if f("roic_est") is not None:
        roic = f("roic_est")
    elif uses_gaap_roic(sub_ind):
        roic = f("roic_median") if f("roic_median") is not None else f("roic_operating")
    else:
        roic = f("roic_operating") if f("roic_operating") is not None else f("roic_median")
    roic_gaap = f("roic_median")
    roic_op = roic if roic is not None else 0.18

    par_cost_of_equity = (p or {}).get("par_cost_of_equity", 0.085)
    par_roic_avg = (p or {}).get("par_roic_avg", 0.120)
    par_roic_log_k = (p or {}).get("par_roic_log_k", 0.250)
    par_g_anchor_max = (p or {}).get("par_g_anchor_max", 0.220)
    par_g_1y_floor = (p or {}).get("par_g_1y_floor", -0.040)
    par_g_log_k = (p or {}).get("par_g_log_k", 0.120)
    par_g_cap_default = (p or {}).get("par_g_cap", 0.120)
    par_g_cap_large = (p or {}).get("par_g_cap_large", 0.105)
    par_g_cap_mega = (p or {}).get("par_g_cap_mega", 0.098)
    par_g_cap_hyper = (p or {}).get("par_g_cap_hyper", 0.095)
    par_g_base = (p or {}).get("par_g_base", 0.035)
    par_fade_cap30 = (p or {}).get("par_fade_cap30", 0.85)
    par_fade_cap20 = (p or {}).get("par_fade_cap20", 0.75)
    par_fade_cap15 = (p or {}).get("par_fade_cap15", 0.62)
    par_fade_default = (p or {}).get("par_fade_default", 0.75)
    par_size_intercept = (p or {}).get("par_size_factor_intercept", 1.08)
    par_size_slope = (p or {}).get("par_size_factor_slope", 0.11)
    par_size_min = (p or {}).get("par_size_factor_min", 0.72)
    par_size_max = (p or {}).get("par_size_factor_max", 1.05)

    # Revenue-Anchored Size Gravity & Scale Ceiling:
    # Normalized to USD equivalent using standard currency cross rates; falls back to Market Cap / 4.0 only if revenue missing.
    ccy = fin.get("fin_currency") or fin.get("quote_currency") or "USD"
    fx_rate = C.FX_TO_USD.get(ccy, 1.0)
    mc_usd_b = ((mc or 0.0) * fx_rate) / 1000.0
    rev = f("sales_ttm_m") if f("sales_ttm_m") is not None else (f("revenue_ttm_m") if f("revenue_ttm_m") is not None else f("revenue_m"))
    rev_usd_b = (rev * fx_rate) / 1000.0 if (rev is not None and rev > 0) else None

    if rev_usd_b is not None:
        if rev_usd_b >= 250.0:
            scale_tier, scale_cap = "HYPER", par_g_cap_hyper
        elif rev_usd_b >= 50.0:
            scale_tier, scale_cap = "MEGA", par_g_cap_mega
        elif rev_usd_b >= 15.0:
            scale_tier, scale_cap = "LARGE", par_g_cap_large
        else:
            scale_tier, scale_cap = "MID/SM", par_g_cap_default
    else:
        if mc_usd_b >= 1000.0:
            scale_tier, scale_cap = "HYPER", par_g_cap_hyper
        elif mc_usd_b >= 250.0:
            scale_tier, scale_cap = "MEGA", par_g_cap_mega
        elif mc_usd_b >= 50.0:
            scale_tier, scale_cap = "LARGE", par_g_cap_large
        else:
            scale_tier, scale_cap = "MID/SM", par_g_cap_default

    eff_rev_b = rev_usd_b if (rev_usd_b is not None and rev_usd_b > 0) else (max(0.5, mc_usd_b / 4.0) if mc_usd_b > 0 else 5.0)
    size_factor = round(
        max(par_size_min, min(par_size_max, par_size_intercept - par_size_slope * math.log10(max(1.0, eff_rev_b)))),
        4,
    )

    # Gate 4 CAP-Linked Persistence (pers / r):
    if fund_cap is not None:
        if fund_cap >= 30:
            pers = par_fade_cap30
        elif fund_cap >= 20:
            pers = par_fade_cap20
        else:
            pers = par_fade_cap15
    else:
        pers = par_fade_default
    g_mult = 200.0

    # Mauboussin Galton ROIC Regression:
    # Expected ROIC = r * (ROIC_log - Average_ROIC) + Average_ROIC
    if roic_op > par_roic_avg:
        roic_log = round(par_roic_avg + par_roic_log_k * math.log(1.0 + (roic_op - par_roic_avg) / par_roic_log_k), 4)
        roic_exp = round(pers * (roic_log - par_roic_avg) + par_roic_avg, 4)
        roic_fade_ratio = round(roic_exp / roic_log, 4)
    else:
        roic_log = round(max(0.05, roic_op), 4)
        roic_exp = roic_log
        roic_fade_ratio = 1.0

    # Operating Cost Base Growth Ceiling (g_org_exp / g_0) & Buyback Accretion (v6.35):
    bb_raw = f("buyback_yield")
    bb_eff = max(-0.03, min(0.035, bb_raw)) if bb_raw is not None else 0.0
    bb_pos = max(0.0, bb_eff)
    bb_org = min(0.0, bb_eff)

    ret_stored = f("retention_rate")
    div_m = f("dividends_ttm_m")
    if ret_stored is not None:
        retention = max(0.0, min(1.0, ret_stored))
    elif ni is not None and ni > 0 and div_m is not None:
        retention = max(0.0, min(1.0, 1.0 - div_m / ni))
    else:
        retention = None
    roiic_val = f("roiic")
    r_inc = max(0.0, roiic_val if roiic_val is not None else roic_exp) if (roiic_val is not None or roic is not None) else None
    zc_pricing = None

    sales_1y_val = f("sales_1y")
    sales_cagr_val = f("sales_cagr")
    opcost_1y_val = f("opcost_1y")
    opcost_cagr_val = f("opcost_cagr")
    cap_growth_val = f("cap_growth")
    g_imp_in = f("g_implied")
    has_stmt_growth = any(x is not None for x in (opcost_cagr_val, sales_cagr_val, sales_1y_val, g, cap_growth_val))

    g_1y = round(sales_1y_val, 4) if sales_1y_val is not None else None
    g_hist = round(sales_cagr_val, 4) if sales_cagr_val is not None else (round(g, 4) if g is not None else None)
    g_cap = round(opcost_cagr_val, 4) if opcost_cagr_val is not None else (round(cap_growth_val, 4) if cap_growth_val is not None else None)

    if has_stmt_growth:
        # Primary normal organic growth anchor: 3-5Y Operating Cost Base CAGR (OpCost = Sales - EBIT = COGS + OpEx)
        base_org = (
            opcost_cagr_val
            if opcost_cagr_val is not None
            else (sales_cagr_val if sales_cagr_val is not None else ((g - bb_pos) if g is not None else (sales_1y_val or par_g_base)))
        )
        g_org_start = round(max(par_g_1y_floor, min(par_g_anchor_max, base_org + bb_org)), 4)
        g_start = round(max(par_g_1y_floor, min(par_g_anchor_max, base_org + bb_eff)), 4)
    else:
        if f("g_est") is not None:
            g_start = round(f("g_est"), 4)
        elif g_imp_in is not None:
            g_start = round(max(0.02, g_imp_in), 4)
        else:
            g_start = par_g_base
        g_org_start = round(max(0.02, g_start - bb_pos), 4) if g_start > 0.02 else g_start

    # Organic Growth Ceiling (g_0 / g_org_exp) bounded by [2.0%, scale_cap], and Per-Share Growth Ceiling (g_exp):
    if f("g_est") is not None:
        g_est_val = f("g_est")
        g_org_exp = round(max(0.02, min(scale_cap, g_est_val - bb_pos if g_est_val > 0.02 else g_est_val)), 4)
        g_exp = round(min(scale_cap + bb_pos, max(0.02, g_est_val)), 4)
    elif not has_stmt_growth and g_imp_in is not None:
        g_org_exp = round(max(0.02, min(scale_cap, g_imp_in - bb_pos if g_imp_in > 0.02 else g_imp_in)), 4)
        g_exp = round(g_org_exp + bb_pos, 4)
    else:
        g_org_exp = round(max(0.02, min(scale_cap, g_org_start)), 4)
        g_exp = round(g_org_exp + bb_pos, 4)

    g_log = g_org_exp
    bb_contrib = round(max(0.0, g_exp - g_org_exp), 4)

    # Backwards-compatibility aliases for downstream callers
    g_fund = g_cap
    g_demand = g_hist
    g_raw = g_start

    has_hist_mults = bool(ml and mh)
    if not price or not peak_eps or peak_eps <= 0 or (not has_hist_mults and not fund_cap and peak_eps_override is None):
        return {"status": C.V_NODATA, "peak_eps": peak_eps, "cur_mult": None, "par_mult": None,
                "par_val": None, "vs_par": None, "g": g, "dy": dy, "coupon": (g + dy) if g is not None else None,
                "g_start": g_start, "g_org_start": g_org_start, "g_1y": g_1y, "g_hist": g_hist, "g_cap": g_cap,
                "g_log": g_log, "size_factor": size_factor,
                "g_exp": g_exp, "g_org_exp": g_org_exp, "g_irr": g_exp, "exp_coupon": (g_exp + dy) if g_exp is not None else None,
                "g_imp": g_exp, "imp_coupon": (g_exp + dy) if g_exp is not None else None, "irr_5y": None,
                "cap_implied": None, "cap_gap": None, "g_market": None, "g_gap": None,
                "scale_tier": scale_tier, "scale_cap": scale_cap,
                "g_fund": g_fund, "g_demand": g_demand, "g_raw": g_raw,
                "fund_cap": fund_cap, "pers": pers, "g_mult": g_mult,
                "reinv_eff": 1.0, "eff_g_mult": g_mult,
                "pe_mm": None, "pe_mck": None, "pe_vd": None,
                "t_growth": None, "t_hist": None, "t_hist_raw": None, "t_roic": None, "raw_par": None,
                "roic_log": roic_log, "roic_exp": roic_exp, "roic_fade_ratio": roic_fade_ratio,
                "opcost_1y": opcost_1y_val, "opcost_cagr": opcost_cagr_val,
                "retention": retention, "r_inc": r_inc, "zc_pricing": zc_pricing, "bb_eff": bb_eff}
    cur_mult = price / peak_eps
    g_org_val = g_org_exp if (g_org_exp is not None and g_org_exp > 0) else par_g_base

    # Explicit N-Year Mauboussin-Fade DCF at r = 8.50% (v6.35):
    k = max(0.05, par_cost_of_equity)
    n_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else 20.0
    roic_eff = max(roic_exp, 0.05)
    mtm_holdco = is_mtm_holdco(sub_ind, fcf_conv_val, peak_eps_override, mh)
    finite_conc = is_finite_concession(sub_ind, fcf_conv_val)

    pe_vd, pe_mm, pe_mck, reinv_eff = explicit_dcf_multiple(
        g_org_val, roic_eff, n_cap, k, par_g_base, par_roic_avg, finite_conc, mtm_holdco
    )
    pe_vd0, _, _, _ = explicit_dcf_multiple(
        0.0, roic_eff, n_cap, k, par_g_base, par_roic_avg, finite_conc, mtm_holdco
    )
    raw_slope = (pe_vd - pe_vd0) / g_org_val if g_org_val > 1e-6 else 100.0
    eff_g_mult = raw_slope if raw_slope > 10.0 else 100.0

    if has_hist_mults:
        t_hist_raw = (2.0 * ml * mh) / (ml + mh)
        t_hist = t_hist_raw
    else:
        t_hist_raw = None
        t_hist = pe_vd

    # 100% Explicit Mauboussin-Fade DCF Fair Value Multiple:
    par_mult = pe_vd

    # Backwards-compatibility aliases for downstream callers
    t_growth = pe_mm
    t_roic = pe_mck
    raw_par = pe_vd

    par_val = par_mult * peak_eps
    vs_par = price / par_val - 1.0
    status = C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR

    # 5Y IRR along the Mauboussin fade trajectory + FCF-conserved buyback accretion:
    g_org_5y = round(g_org_val - (2.0 / max(5.0, n_cap)) * (g_org_val - par_g_base), 4) if not mtm_holdco else g_org_val
    if bb_pos > 0 and cur_mult > 0:
        bb_fcf_cap = max(0.0, (max(0.0, reinv_eff) / cur_mult) - dy)
        g_irr = round(g_org_5y + min(bb_pos, bb_fcf_cap), 4)
    else:
        g_irr = round(g_org_5y, 4)
    irr_5y = solve_irr_5y(price, par_val, g_irr, dy)

    # Market-Implied CAP scaled above zero-moat steady-state base multiple (1 / r = 11.76x):
    pe_base = 1.0 / k
    if fund_cap and price and par_val and par_val > 0:
        if not mtm_holdco and par_mult > pe_base + 0.5:
            cap_implied = round(max(0.0, fund_cap * (cur_mult - pe_base) / (par_mult - pe_base)), 1)
        else:
            cap_implied = round(fund_cap * (price / par_val), 1)
    else:
        cap_implied = None
    cap_gap = round(fund_cap - cap_implied, 1) if (fund_cap is not None and cap_implied is not None) else None

    # Exact DCF-inverted Market-Implied Organic Growth (g_market at r = 8.5%) & Growth Margin of Safety (g_gap):
    g_market = solve_implied_dcf_growth(
        cur_mult, g_org_val, roic_eff, n_cap, k, par_g_base, par_roic_avg, finite_conc, mtm_holdco
    )
    g_gap = round(g_org_val - g_market, 4) if (g_org_val is not None and g_market is not None) else None
    return {
        "status": status,
        "peak_eps": peak_eps,
        "cur_mult": cur_mult,
        "par_mult": par_mult,
        "par_val": par_val,
        "vs_par": vs_par,
        "g": g,
        "dy": dy,
        "coupon": (g + dy) if g is not None else None,
        "g_start": g_start,
        "g_org_start": g_org_start,
        "g_1y": g_1y,
        "g_hist": g_hist,
        "g_cap": g_cap,
        "g_log": g_log,
        "size_factor": size_factor,
        "g_exp": g_exp,
        "g_org_exp": g_org_exp,
        "g_irr": g_irr,
        "exp_coupon": (g_exp + dy) if g_exp is not None else None,
        # Backwards compatibility aliases
        "g_imp": g_exp,
        "imp_coupon": (g_exp + dy) if g_exp is not None else None,
        "irr_5y": irr_5y,
        "cap_implied": cap_implied,
        "cap_gap": cap_gap,
        "g_market": g_market,
        "g_gap": g_gap,
        "scale_tier": scale_tier,
        "scale_cap": scale_cap,
        "g_fund": g_fund,
        "g_demand": g_demand,
        "g_raw": g_raw,
        "fund_cap": fund_cap,
        "pers": pers,
        "g_mult": g_mult,
        "reinv_eff": reinv_eff,
        "eff_g_mult": eff_g_mult,
        "pe_mm": pe_mm,
        "pe_mck": pe_mck,
        "pe_vd": pe_vd,
        "t_growth": t_growth,
        "t_hist": t_hist,
        "t_hist_raw": t_hist_raw,
        "t_roic": t_roic,
        "raw_par": raw_par,
        "roic_log": roic_log,
        "roic_exp": roic_exp,
        "roic_fade_ratio": roic_fade_ratio,
        "opcost_1y": opcost_1y_val,
        "opcost_cagr": opcost_cagr_val,
        "retention": retention,
        "r_inc": r_inc,
        "zc_pricing": zc_pricing,
        "bb_eff": bb_eff,
    }
