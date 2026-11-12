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
    """Python reference implementation of the v6.34 Equity Bond Below PAR, Organic Value Driver P/E & 3-Anchor Logarithmic Mauboussin Growth valuation."""
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

    par_cost_of_equity = (p or {}).get("par_cost_of_equity", 0.0875)
    par_vd_weight = (p or {}).get("par_vd_weight", 0.75)
    par_thist_min_ratio = (p or {}).get("par_thist_min_ratio", 0.50)
    par_thist_max_ratio = (p or {}).get("par_thist_max_ratio", 1.50)
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

    # Revenue-Anchored Size Gravity & Continuous Log-Revenue Size Factor:
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
    # CAP >= 30y (fortress monopolies) -> 0.85 persistence factor
    # CAP >= 20y (standard quality compounders) -> 0.75 persistence factor
    # CAP >= 15y (shorter runway) -> 0.62 persistence factor
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

    # Mauboussin Galton ROIC Regression (v6.32):
    # Expected ROIC = r * (ROIC_log - Average_ROIC) + Average_ROIC
    if roic_op > par_roic_avg:
        roic_log = round(par_roic_avg + par_roic_log_k * math.log(1.0 + (roic_op - par_roic_avg) / par_roic_log_k), 4)
        roic_exp = round(pers * (roic_log - par_roic_avg) + par_roic_avg, 4)
        roic_fade_ratio = round(roic_exp / roic_log, 4)
    else:
        roic_log = round(max(0.05, roic_op), 4)
        roic_exp = roic_log
        roic_fade_ratio = 1.0

    # 3-Anchor Starting Growth (g_start) & Parallel Organic Growth (g_org_start -> g_org_exp) (v6.34):
    bb_raw = f("buyback_yield")
    bb_eff = max(-0.03, min(0.025, bb_raw)) if bb_raw is not None else 0.0
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
    has_stmt_growth = any(x is not None for x in (sales_1y_val, sales_cagr_val, g, cap_growth_val))

    if has_stmt_growth:
        # Anchor 1 — Near-Term 1Y Momentum with Operating Cost Smoothing (g_1y):
        s1_base = sales_1y_val if sales_1y_val is not None else (sales_cagr_val if sales_cagr_val is not None else (g or 0.0))
        if sales_1y_val is not None and opcost_1y_val is not None:
            if sales_1y_val >= 0.0:
                s1_eff = 0.5 * sales_1y_val + 0.5 * min(sales_1y_val, opcost_1y_val)
            else:
                s1_eff = 0.5 * sales_1y_val + 0.5 * opcost_1y_val
        elif sales_1y_val is not None and sales_1y_val > 0.25 and sales_cagr_val is not None:
            s1_eff = 0.5 * sales_1y_val + 0.5 * max(0.0, sales_cagr_val)
        else:
            s1_eff = s1_base
        g_1y = round(max(par_g_1y_floor, min(par_g_anchor_max, s1_eff + bb_eff)), 4)
        g_1y_org = round(max(par_g_1y_floor, min(par_g_anchor_max, s1_eff + bb_org)), 4)

        # Anchor 2 — Medium-Term 3–5Y Evidence with Operating Cost Smoothing (g_hist):
        s5_base = sales_cagr_val if sales_cagr_val is not None else (g if g is not None else (sales_1y_val or 0.0))
        if sales_cagr_val is not None and opcost_cagr_val is not None:
            s5_eff = 0.5 * sales_cagr_val + 0.5 * min(sales_cagr_val, opcost_cagr_val)
        else:
            s5_eff = s5_base
        top_5y = max(0.0, s5_eff) + bb_eff
        if sales_cagr_val is not None and g is not None and g < top_5y:
            hist_val = 0.5 * top_5y + 0.5 * max(0.0, g)
        else:
            hist_val = top_5y
        g_hist = round(max(0.0, min(par_g_anchor_max, hist_val)), 4)

        top_5y_org = max(0.0, s5_eff) + bb_org
        g_oe_org = (g - bb_pos) if g is not None else None
        if sales_cagr_val is not None and g_oe_org is not None and g_oe_org < top_5y_org:
            hist_val_org = 0.5 * top_5y_org + 0.5 * max(0.0, g_oe_org)
        else:
            hist_val_org = top_5y_org
        g_hist_org = round(max(0.0, min(par_g_anchor_max, hist_val_org)), 4)

        # Anchor 3 — Operating Capital Growth with Mauboussin Galton ROIC Fade (g_cap):
        if cap_growth_val is not None:
            cg_base = cap_growth_val
        elif sales_cagr_val is not None:
            cg_base = s5_eff
        else:
            cg_base = g or 0.0
        g_cap = round(max(0.0, min(par_g_anchor_max, max(0.0, cg_base) * roic_fade_ratio + bb_eff)), 4)
        g_cap_org = round(max(0.0, min(par_g_anchor_max, max(0.0, cg_base) * roic_fade_ratio + bb_org)), 4)

        # 3-Anchor Starting Growth (per-share g_start & firm-level organic g_org_start):
        g_start = round((g_1y + g_hist + g_cap) / 3.0, 4)
        g_org_start = round((g_1y_org + g_hist_org + g_cap_org) / 3.0, 4)
    else:
        g_1y = None
        g_hist = None
        g_cap = None
        if f("g_est") is not None:
            g_start = round(f("g_est"), 4)
        elif g_imp_in is not None:
            g_start = round(max(0.02, g_imp_in), 4)
        else:
            g_start = par_g_base
        g_org_start = round(max(0.02, g_start - bb_pos), 4) if g_start > 0.02 else g_start

    # Logarithmic Compression (g_log) & Continuous Mauboussin Fade to Expected Growth (g_exp & g_org_exp):
    if g_start > par_g_base:
        g_log = round(par_g_base + par_g_log_k * math.log(1.0 + (g_start - par_g_base) / par_g_log_k), 4)
    else:
        g_log = round(max(0.02, g_start), 4)

    if g_org_start > par_g_base:
        g_org_log = round(par_g_base + par_g_log_k * math.log(1.0 + (g_org_start - par_g_base) / par_g_log_k), 4)
    else:
        g_org_log = round(max(0.02, g_org_start), 4)

    if f("g_est") is not None:
        # Explicit analyst override sets g_exp directly (bounded by scale_cap) while preserving objective g_start
        g_exp = round(min(scale_cap, f("g_est")), 4)
        g_org_exp = round(max(0.02, g_exp - bb_pos), 4) if g_exp > 0.02 else g_exp
    elif not has_stmt_growth and g_imp_in is not None:
        g_exp = round(min(scale_cap, max(0.02, g_imp_in)), 4)
        g_org_exp = round(max(0.02, g_exp - bb_pos), 4) if g_exp > 0.02 else g_exp
    else:
        if g_start > par_g_base:
            faded_g = par_g_base + (g_log - par_g_base) * pers * size_factor
            g_exp = round(min(scale_cap, faded_g), 4)
        else:
            # Asymmetric 'No Free Lunch' rule: slow growers <= 3.5% do not mean-revert upward
            g_exp = round(max(0.02, g_start), 4)

        if g_org_start > par_g_base:
            faded_g_org = par_g_base + (g_org_log - par_g_base) * pers * size_factor
            g_org_exp = round(min(scale_cap, faded_g_org), 4)
        else:
            g_org_exp = round(max(0.02, g_org_start), 4)

    g_org_exp = min(g_exp, g_org_exp)
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

    # Corporate Finance Value Driver P/E (v6.34):
    # Evaluated strictly on firm-level organic growth (g_org_val) so share buybacks are never double-counted as ROIC_exp reinvestment.
    k = max(0.05, par_cost_of_equity)
    n_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else 20.0
    roic_eff = max(roic_exp, 0.05)
    reinv_term = par_g_base / max(0.05, par_roic_avg)
    mtm_holdco = is_mtm_holdco(sub_ind, fcf_conv_val, peak_eps_override, mh)
    finite_conc = is_finite_concession(sub_ind, fcf_conv_val)

    def _compute_vd(g_rate: float) -> tuple[float, float, float, float]:
        if mtm_holdco:
            nav_pe = 1.0 / roic_eff
            return nav_pe, nav_pe, nav_pe, 1.0
        reinv_stage1 = min(0.95, max(0.0, g_rate) / roic_eff)
        q = (1.0 + g_rate) / (1.0 + k)
        pv_stage1 = (1.0 - reinv_stage1) * (n_cap if abs(1.0 - q) < 1e-9 else q * (1.0 - (q ** n_cap)) / (1.0 - q))
        if finite_conc:
            ann_n = (1.0 - ((1.0 + k) ** (-n_cap))) / k
            mm_val = ann_n * (1.0 + (g_rate * n_cap * (roic_eff - k)) / ((1.0 + k) * roic_eff))
            mck_val = pv_stage1
            return 0.5 * mm_val + 0.5 * mck_val, mm_val, mck_val, 1.0 - reinv_stage1
        mm_val = (1.0 / k) * (1.0 + (g_rate * n_cap * (roic_eff - k)) / ((1.0 + k) * roic_eff))
        pv_stage2 = ((1.0 - reinv_term) * ((1.0 + g_rate) ** n_cap) * (1.0 + par_g_base)) / (
            max(0.01, k - par_g_base) * ((1.0 + k) ** n_cap)
        )
        mck_val = pv_stage1 + pv_stage2
        return 0.5 * mm_val + 0.5 * mck_val, mm_val, mck_val, 1.0 - reinv_stage1

    pe_vd, pe_mm, pe_mck, reinv_eff = _compute_vd(g_org_val)
    pe_vd0, _, _, _ = _compute_vd(0.0)
    raw_slope = (pe_vd - pe_vd0) / g_org_val if g_org_val > 1e-6 else 100.0
    eff_g_mult = raw_slope if raw_slope > 10.0 else 100.0

    # Regime-Bounded 5-Year Historical Harmonic P/E (bounded within [0.50x, 1.50x] of PE_VD; falls back to PE_VD when 5Y history is unavailable):
    if has_hist_mults:
        t_hist_raw = (2.0 * ml * mh) / (ml + mh)
        t_hist = max(par_thist_min_ratio * pe_vd, min(par_thist_max_ratio * pe_vd, t_hist_raw))
    else:
        t_hist_raw = None
        t_hist = pe_vd

    # 75/25 PAR Multiple:
    par_mult = par_vd_weight * pe_vd + (1.0 - par_vd_weight) * t_hist

    # Backwards-compatibility aliases for downstream callers
    t_growth = pe_mm
    t_roic = pe_mck
    raw_par = pe_vd

    par_val = par_mult * peak_eps
    vs_par = price / par_val - 1.0
    status = C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR

    # FCF Payout Conservation in 5Y IRR: bound buyback accretion at current multiple by available Owner FCF after dividends
    if bb_contrib > 0 and cur_mult > 0 and g_exp is not None and g_org_exp is not None:
        bb_fcf_cap = max(0.0, (max(0.0, reinv_eff) / cur_mult) - dy)
        g_irr = round(min(g_exp, g_org_exp + bb_fcf_cap), 4)
    else:
        g_irr = g_exp
    irr_5y = solve_irr_5y(price, par_val, g_irr, dy)

    # Market-Implied CAP scaled above zero-moat steady-state base multiple (1 / k = 11.43x):
    pe_base = 1.0 / k
    if fund_cap and price and par_val and par_val > 0:
        if not mtm_holdco and par_mult > pe_base + 0.5:
            cap_implied = round(max(0.0, fund_cap * (cur_mult - pe_base) / (par_mult - pe_base)), 1)
        else:
            cap_implied = round(fund_cap * (price / par_val), 1)
    else:
        cap_implied = None
    cap_gap = round(fund_cap - cap_implied, 1) if (fund_cap is not None and cap_implied is not None) else None

    if mtm_holdco:
        g_market = round(g_exp * (cur_mult / par_mult), 4) if (g_exp is not None and par_mult > 0) else None
    else:
        vd_implied = (cur_mult - (1.0 - par_vd_weight) * t_hist) / par_vd_weight
        g_org_market = (vd_implied - pe_vd0) / eff_g_mult if (cur_mult and t_hist is not None and eff_g_mult > 0) else None
        g_market = round(g_org_market + bb_contrib, 4) if g_org_market is not None else None
    g_gap = round(g_exp - g_market, 4) if (g_exp is not None and g_market is not None) else None
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
