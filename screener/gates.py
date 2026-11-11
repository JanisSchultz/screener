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
def par_valuation(fin: dict, p: dict = None, cap: float | int | None = None, moat: str | None = None) -> dict:
    """Python reference implementation of the v6.33 Equity Bond Below PAR, Value Driver P/E & 3-Anchor Logarithmic Mauboussin Growth valuation."""
    f = lambda k: None if (fin.get(k) is None or (isinstance(fin.get(k), float) and math.isnan(fin.get(k)))) else (fin.get(k) if isinstance(fin.get(k), (int, float)) else None)
    price = f("price")
    mc = f("market_cap_m")
    ni = f("ni_ttm_m")
    if f("peak_eps_est") is not None:
        peak_eps = f("peak_eps_est")
    else:
        oe_peak = f("peak_oe_eps")
        # Current TTM EPS inferred from reported Net Income and Market Cap / Price
        cur_eps = (price * (ni / mc)) if (mc and mc > 0 and ni is not None and price and price > 0) else oe_peak
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
    roic = f("roic_est") if f("roic_est") is not None else (f("roic_operating") if f("roic_operating") is not None else f("roic_median"))
    roic_gaap = f("roic_median")
    roic_op = roic if roic is not None else 0.18

    par_cost_of_equity = (p or {}).get("par_cost_of_equity", 0.0875)
    par_vd_weight = (p or {}).get("par_vd_weight", 0.75)
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

    # 3-Anchor Starting Growth (g_start) & Logarithmic Mauboussin Decay Curve (v6.32):
    bb_raw = f("buyback_yield")
    bb_eff = max(-0.03, min(0.025, bb_raw)) if bb_raw is not None else 0.0

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
        else:
            s1_eff = s1_base
        g_1y = round(max(par_g_1y_floor, min(par_g_anchor_max, s1_eff + bb_eff)), 4)

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

        # Anchor 3 — Operating Capital Growth with Mauboussin Galton ROIC Fade (g_cap):
        if cap_growth_val is not None:
            cg_base = cap_growth_val
        elif sales_cagr_val is not None:
            cg_base = s5_eff
        else:
            cg_base = g or 0.0
        g_cap = round(max(0.0, min(par_g_anchor_max, max(0.0, cg_base) * roic_fade_ratio + bb_eff)), 4)

        # 3-Anchor Starting Growth (g_start / g_0):
        g_start = round((g_1y + g_hist + g_cap) / 3.0, 4)
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

    # Logarithmic Compression (g_log) & Continuous Mauboussin Fade to Expected Growth (g_exp):
    if g_start > par_g_base:
        g_log = round(par_g_base + par_g_log_k * math.log(1.0 + (g_start - par_g_base) / par_g_log_k), 4)
    else:
        g_log = round(max(0.02, g_start), 4)

    if f("g_est") is not None:
        # Explicit analyst override sets g_exp directly (bounded by scale_cap) while preserving objective g_start
        g_exp = round(min(scale_cap, f("g_est")), 4)
    elif not has_stmt_growth and g_imp_in is not None:
        g_exp = round(min(scale_cap, max(0.02, g_imp_in)), 4)
    elif g_start > par_g_base:
        faded_g = par_g_base + (g_log - par_g_base) * pers * size_factor
        g_exp = round(min(scale_cap, faded_g), 4)
    else:
        # Asymmetric 'No Free Lunch' rule: slow growers <= 3.5% do not mean-revert upward
        g_exp = round(max(0.02, g_start), 4)

    # Backwards-compatibility aliases for downstream callers
    g_fund = g_cap
    g_demand = g_hist
    g_raw = g_start

    if not price or not peak_eps or peak_eps <= 0 or not ml or not mh:
        return {"status": C.V_NODATA, "peak_eps": peak_eps, "cur_mult": None, "par_mult": None,
                "par_val": None, "vs_par": None, "g": g, "dy": dy, "coupon": (g + dy) if g is not None else None,
                "g_start": g_start, "g_1y": g_1y, "g_hist": g_hist, "g_cap": g_cap,
                "g_log": g_log, "size_factor": size_factor,
                "g_exp": g_exp, "exp_coupon": (g_exp + dy) if g_exp is not None else None,
                "g_imp": g_exp, "imp_coupon": (g_exp + dy) if g_exp is not None else None, "irr_5y": None,
                "cap_implied": None, "cap_gap": None, "g_market": None, "g_gap": None,
                "scale_tier": scale_tier, "scale_cap": scale_cap,
                "g_fund": g_fund, "g_demand": g_demand, "g_raw": g_raw,
                "fund_cap": fund_cap, "pers": pers, "g_mult": g_mult,
                "reinv_eff": 1.0, "eff_g_mult": g_mult,
                "pe_mm": None, "pe_mck": None, "pe_vd": None,
                "t_growth": None, "t_hist": None, "t_roic": None, "raw_par": None,
                "roic_log": roic_log, "roic_exp": roic_exp, "roic_fade_ratio": roic_fade_ratio,
                "opcost_1y": opcost_1y_val, "opcost_cagr": opcost_cagr_val,
                "retention": retention, "r_inc": r_inc, "zc_pricing": zc_pricing, "bb_eff": bb_eff}
    cur_mult = price / peak_eps
    g_val = g_exp if (g_exp is not None and g_exp > 0) else par_g_base

    # Corporate Finance Value Driver P/E (v6.33):
    # 50/50 blend of Miller-Modigliani Finite-CAP P/E and McKinsey 2-Stage Compounding P/E
    k = max(0.05, par_cost_of_equity)
    n_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else 20.0
    roic_eff = max(roic_exp, 0.05)
    reinv_term = par_g_base / max(0.05, par_roic_avg)

    def _compute_vd(g_rate: float) -> tuple[float, float, float, float]:
        mm_val = (1.0 / k) * (1.0 + (g_rate * n_cap * (roic_eff - k)) / ((1.0 + k) * roic_eff))
        reinv_stage1 = min(0.95, max(0.0, g_rate) / roic_eff)
        q = (1.0 + g_rate) / (1.0 + k)
        pv_stage1 = (1.0 - reinv_stage1) * (n_cap if abs(1.0 - q) < 1e-9 else q * (1.0 - (q ** n_cap)) / (1.0 - q))
        pv_stage2 = ((1.0 - reinv_term) * ((1.0 + g_rate) ** n_cap) * (1.0 + par_g_base)) / (
            max(0.01, k - par_g_base) * ((1.0 + k) ** n_cap)
        )
        mck_val = pv_stage1 + pv_stage2
        return 0.5 * mm_val + 0.5 * mck_val, mm_val, mck_val, 1.0 - reinv_stage1

    pe_vd, pe_mm, pe_mck, reinv_eff = _compute_vd(g_val)
    pe_vd0, _, _, _ = _compute_vd(0.0)
    raw_slope = (pe_vd - pe_vd0) / g_val if g_val > 1e-6 else 100.0
    eff_g_mult = raw_slope if raw_slope > 10.0 else 100.0

    # Uncapped 5-Year Historical Harmonic P/E (midpoint of 5Y Earnings Yield E/P):
    t_hist = (2.0 * ml * mh) / (ml + mh)

    # Pure Uncapped 75/25 PAR Multiple:
    par_mult = par_vd_weight * pe_vd + (1.0 - par_vd_weight) * t_hist

    # Backwards-compatibility aliases for downstream callers
    t_growth = pe_mm
    t_roic = pe_mck
    raw_par = pe_vd

    par_val = par_mult * peak_eps
    vs_par = price / par_val - 1.0
    status = C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR
    irr_5y = ((1.0 + g_exp) * ((par_val / price) ** 0.2) + dy - 1.0) if (price and price > 0 and par_val and g_exp is not None) else None
    cap_implied = round(fund_cap * (price / par_val), 1) if (fund_cap and price and par_val and par_val > 0) else None
    cap_gap = round(fund_cap - cap_implied, 1) if (fund_cap is not None and cap_implied is not None) else None
    vd_implied = (cur_mult - (1.0 - par_vd_weight) * t_hist) / par_vd_weight
    g_market = round((vd_implied - pe_vd0) / eff_g_mult, 4) if (cur_mult and t_hist is not None and eff_g_mult > 0) else None
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
        "g_1y": g_1y,
        "g_hist": g_hist,
        "g_cap": g_cap,
        "g_log": g_log,
        "size_factor": size_factor,
        "g_exp": g_exp,
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
