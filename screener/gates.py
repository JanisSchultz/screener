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
    """Python reference implementation of the v6.30 Equity Bond Below PAR & 4-Filter Credible Growth valuation."""
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

    par_roic_cap = (p or {}).get("par_roic_cap", 35.0)
    par_hist_cap = (p or {}).get("par_hist_cap", 35.0)
    par_g_prefade_cap = (p or {}).get("par_g_prefade_cap", 0.180)
    par_g_cap_default = (p or {}).get("par_g_cap", 0.120)
    par_g_cap_large = (p or {}).get("par_g_cap_large", 0.100)
    par_g_cap_mega = (p or {}).get("par_g_cap_mega", 0.085)
    par_g_cap_hyper = (p or {}).get("par_g_cap_hyper", 0.080)
    par_g_turnaround = (p or {}).get("par_g_turnaround", 0.010)
    par_g_base = (p or {}).get("par_g_base", 0.035)
    par_fade_cap30 = (p or {}).get("par_fade_cap30", 0.75)
    par_fade_cap20 = (p or {}).get("par_fade_cap20", 0.60)
    par_fade_cap15 = (p or {}).get("par_fade_cap15", 0.45)
    par_fade_default = (p or {}).get("par_fade_default", 0.60)
    par_g_mult_cap30 = (p or {}).get("par_g_mult_cap30", 240.0)
    par_g_mult_cap20 = (p or {}).get("par_g_mult_cap20", 200.0)
    par_g_mult_cap15 = (p or {}).get("par_g_mult_cap15", 170.0)
    par_g_mult_default = (p or {}).get("par_g_mult_default", 200.0)

    # Filter 4b — Revenue-Anchored Size Gravity (Law of Large Numbers):
    # Normalized to USD equivalent using standard currency cross rates; falls back to Market Cap only if revenue missing.
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

    # CAP-Linked Step-Down Persistence (pers) & Pillar 1 Growth Slope (g_mult):
    # CAP >= 30y (fortress monopolies) -> 0.75 step-down weight & 240.0 growth slope (2.4x per 1% g)
    # CAP >= 20y (standard quality compounders) -> 0.60 step-down weight & 200.0 growth slope (2.0x per 1% g)
    # CAP >= 15y (shorter runway) -> 0.45 step-down weight & 170.0 growth slope (1.7x per 1% g)
    if fund_cap is not None:
        if fund_cap >= 30:
            pers, g_mult = par_fade_cap30, par_g_mult_cap30
        elif fund_cap >= 20:
            pers, g_mult = par_fade_cap20, par_g_mult_cap20
        else:
            pers, g_mult = par_fade_cap15, par_g_mult_cap15
    else:
        pers, g_mult = par_fade_default, par_g_mult_default

    # 4-Filter Credible Growth Engine (v6.30):
    bb_raw = f("buyback_yield")
    bb_eff = max(-0.03, min(0.025, bb_raw)) if bb_raw is not None else 0.0
    retention = None
    r_inc = None
    zc_pricing = None

    if f("g_est") is not None:
        # Explicit analyst override bypasses automated supply/demand/fade filters, bounded by Size Gravity
        g_fund = None
        g_demand = None
        g_raw = f("g_est")
        g_exp = min(scale_cap, g_raw)
    else:
        # Filter 1 — Capital Supply Ceiling (g_fund):
        # Retention * Incremental/GAAP ROIC + Zero-Capital Pricing allowance + Share Dilution deduction
        ret_stored = f("retention_rate")
        div_m = f("dividends_ttm_m")
        if ret_stored is not None:
            retention = max(0.0, min(1.0, ret_stored))
        elif ni is not None and ni > 0 and div_m is not None:
            retention = max(0.0, min(1.0, 1.0 - div_m / ni))
        else:
            retention = None

        roiic_val = f("roiic")
        r_cap = par_roic_cap / 100.0
        # Zero-Capital Pricing rule (Filter 1): pure Tollbooths earning >= 35% tangible Operating ROIC
        # require near-zero incremental capital to compound organically (only recurring share dilution deducts)
        is_zero_cap_tollbooth = (moat_arch == "Toll booth / Switching costs" and roic_op >= r_cap)
        if is_zero_cap_tollbooth:
            g_fund = round(max(0.0, par_g_prefade_cap + min(0.0, bb_eff)), 4)
        elif retention is not None and (roic is not None or roiic_val is not None):
            if roiic_val is not None and roic_gaap is not None:
                r_inc = min(r_cap, 0.5 * max(0.0, roiic_val) + 0.5 * min(r_cap, max(0.0, roic_gaap)))
            elif roiic_val is not None:
                r_inc = min(r_cap, 0.5 * max(0.0, roiic_val) + 0.5 * min(r_cap, max(0.0, roic_op)))
            elif roic_gaap is not None:
                r_inc = min(r_cap, 0.5 * min(r_cap, max(0.0, roic_gaap)) + 0.5 * min(r_cap, max(0.0, roic_op)))
            else:
                r_inc = min(r_cap, max(0.0, roic_op))
            zc_pricing = 0.025 if (moat_arch == "Toll booth / Switching costs" or roic_op >= 0.30) else 0.015
            dilution_adj = min(0.0, bb_eff)
            g_fund = round(max(0.0, retention * r_inc + zc_pricing + dilution_adj), 4)
        else:
            g_fund = None

        # Filter 2 & 4a — Bottom-Up Objective Demand & Margin Ceiling (g_demand, unfaded):
        sales_g = f("sales_cagr")
        sales_yrs = f("sales_cagr_yrs")
        g_imp_in = f("g_implied")
        already_faded = False
        if sales_g is not None:
            top_per_share = max(0.0, sales_g) + bb_eff
            # Short 3Y statement window safeguard: when p2p_ok == 'Y', blend 3Y sales with 5Y cycle OE CAGR
            if (sales_yrs is not None and sales_yrs < 5) and fin.get("p2p_ok") == "Y" and g is not None and g > top_per_share:
                top_per_share = 0.5 * top_per_share + 0.5 * g
            # Margin Ceiling: disallow perpetual margin expansion; blend downward if historical OE lagged revenue + buybacks
            if g is not None and g < top_per_share:
                hist_demand = 0.5 * top_per_share + 0.5 * max(0.0, g)
            else:
                hist_demand = top_per_share + 0.005
            raw_demand = min(par_g_prefade_cap, hist_demand)
            # Short-Window (<5Y) & Inorganic M&A Goodwill Demand Haircut ('Free Optionality' rule):
            is_short_window = (sales_yrs is not None and sales_yrs < 5)
            is_ma_heavy = (roic_gaap is not None and roic_gaap < 0.15 and roiic_val is not None and roiic_val < 0.10 and roic_op >= 0.25)
            if (is_short_window or is_ma_heavy) and raw_demand > 0.060:
                raw_demand = min(0.140, 0.060 + 0.75 * (raw_demand - 0.060))
            g_demand = round(raw_demand, 4)
        elif g is not None:
            g_demand = round(min(par_g_prefade_cap, g), 4)
        elif g_imp_in is not None:
            g_demand = round(max(0.02, g_imp_in), 4)
            already_faded = True
        else:
            g_demand = par_g_base
            already_faded = True

        g_raw = min(g_fund, g_demand) if g_fund is not None else g_demand

        # Filter 3 — CAP-Linked Step-Down Fade toward 3.5% Nominal GDP (par_g_base):
        if already_faded:
            faded_g = max(0.02, g_raw)
        elif g_raw >= par_g_base:
            faded_g = pers * g_raw + (1.0 - pers) * par_g_base
        else:
            # Asymmetric Fade ('No Free Lunch'): low growers never fade upward
            faded_g = max(0.02, g_raw)

        # Filter 4b — Revenue Size Gravity:
        g_exp = min(scale_cap, faded_g)

    if not price or not peak_eps or peak_eps <= 0 or not ml or not mh:
        return {"status": C.V_NODATA, "peak_eps": peak_eps, "cur_mult": None, "par_mult": None,
                "par_val": None, "vs_par": None, "g": g, "dy": dy, "coupon": (g + dy) if g is not None else None,
                "g_exp": g_exp, "exp_coupon": (g_exp + dy) if g_exp is not None else None,
                "g_imp": g_exp, "imp_coupon": (g_exp + dy) if g_exp is not None else None, "irr_5y": None,
                "cap_implied": None, "cap_gap": None, "g_market": None, "g_gap": None,
                "scale_tier": scale_tier, "scale_cap": scale_cap,
                "g_fund": g_fund, "g_demand": g_demand, "g_raw": g_raw,
                "fund_cap": fund_cap, "pers": pers, "g_mult": g_mult,
                "reinv_eff": 1.0, "eff_g_mult": g_mult,
                "t_growth": None, "t_hist": None, "t_roic": None, "raw_par": None,
                "retention": retention, "r_inc": r_inc, "zc_pricing": zc_pricing, "bb_eff": bb_eff}
    cur_mult = price / peak_eps
    g_val = g_exp if (g_exp is not None and g_exp > 0) else par_g_base

    # Multiplicative Reinvestment Efficiency (eta_reinv):
    # Scales growth slope by FCF payout capacity (1 - g/ROIC) relative to the 35% ROIC capital-light standard, clamped to [0.25, 1.0]
    roic_bench = max(0.15, par_roic_cap / 100.0)
    if roic is not None:
        roic_eff = min(max(roic, 0.05), roic_bench)
        g_ref = min(max(g_val, 0.0), scale_cap)
        denom = max(0.10, 1.0 - g_ref / roic_bench)
        numer = max(0.0, 1.0 - g_ref / max(roic_eff, g_ref + 0.005))
        reinv_eff = max(0.25, min(1.0, numer / denom))
    else:
        reinv_eff = 1.0

    eff_g_mult = g_mult * reinv_eff
    t_growth = min(40.0, eff_g_mult * max(0.0, g_val))
    t_hist = min(par_hist_cap, 0.5 * (ml + mh))
    t_roic = min(roic * 100.0, par_roic_cap) if roic is not None else 18.0
    raw_par = (t_growth + t_hist + t_roic) / 3.0
    par_mult = min(raw_par, mh)
    par_val = par_mult * peak_eps
    vs_par = price / par_val - 1.0
    status = C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR
    irr_5y = ((1.0 + g_exp) * ((par_val / price) ** 0.2) + dy - 1.0) if (price and price > 0 and par_val and g_exp is not None) else None
    cap_implied = round(fund_cap * (price / par_val), 1) if (fund_cap and price and par_val and par_val > 0) else None
    cap_gap = round(fund_cap - cap_implied, 1) if (fund_cap is not None and cap_implied is not None) else None
    g_market = round((3.0 * cur_mult - t_hist - t_roic) / eff_g_mult, 4) if (cur_mult and t_hist is not None and eff_g_mult > 0) else None
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
        "t_growth": t_growth,
        "t_hist": t_hist,
        "t_roic": t_roic,
        "raw_par": raw_par,
        "retention": retention,
        "r_inc": r_inc,
        "zc_pricing": zc_pricing,
        "bb_eff": bb_eff,
    }
