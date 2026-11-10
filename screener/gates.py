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
def par_valuation(fin: dict, p: dict = None, cap: float | int | None = None) -> dict:
    """Python reference implementation of the v6.22 Equity Bond Below PAR valuation."""
    f = lambda k: None if (fin.get(k) is None or (isinstance(fin.get(k), float) and math.isnan(fin.get(k)))) else (fin.get(k) if isinstance(fin.get(k), (int, float)) else None)
    price = f("price")
    mc = f("market_cap_m")
    peak_eps = f("peak_eps_est") if f("peak_eps_est") is not None else f("peak_oe_eps")
    ml = f("mult_low_5y")
    mh = f("mult_high_5y")
    g = f("cagr_oe_eps")
    dy = (f("dividends_ttm_m") or 0.0) / mc if (mc and mc > 0 and f("dividends_ttm_m") is not None) else 0.0
    fund_cap = cap if isinstance(cap, (int, float)) else f("cap")
    par_roic_cap = (p or {}).get("par_roic_cap", 35.0)
    par_g_cap = (p or {}).get("par_g_cap", 0.12)
    par_g_base = (p or {}).get("par_g_base", 0.07)

    # Mauboussin Base-Rate Regression for forward implied growth
    if f("g_est") is not None:
        g_imp = f("g_est")
    elif f("g_implied") is not None:
        g_imp = min(par_g_cap, f("g_implied"))
    elif g is not None:
        g_imp = min(par_g_cap, max(0.02, 0.15 * (max(0.0, g) - par_g_base) + par_g_base))
    else:
        g_imp = par_g_base

    if not price or not peak_eps or peak_eps <= 0 or not ml or not mh:
        return {"status": C.V_NODATA, "peak_eps": peak_eps, "cur_mult": None, "par_mult": None,
                "par_val": None, "vs_par": None, "g": g, "dy": dy, "coupon": (g + dy) if g is not None else None,
                "g_imp": g_imp, "imp_coupon": (g_imp + dy) if g_imp is not None else None, "irr_5y": None,
                "cap_implied": None, "cap_gap": None, "g_market": None, "g_gap": None}
    cur_mult = price / peak_eps
    g_val = g_imp if (g_imp is not None and g_imp > 0) else par_g_base
    t_growth = min(40.0, 200.0 * max(0.0, g_val))
    t_hist = 0.5 * (ml + mh)
    roic = f("roic_est") if f("roic_est") is not None else (f("roic_operating") if f("roic_operating") is not None else f("roic_median"))
    t_roic = min(roic * 100.0, par_roic_cap) if roic is not None else 18.0
    raw_par = (t_growth + t_hist + t_roic) / 3.0
    par_mult = min(raw_par, mh)
    par_val = par_mult * peak_eps
    vs_par = price / par_val - 1.0
    status = C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR
    irr_5y = ((1.0 + g_imp) * ((par_val / price) ** 0.2) + dy - 1.0) if (price and price > 0 and par_val and g_imp is not None) else None
    cap_implied = round(fund_cap * (price / par_val), 1) if (fund_cap and price and par_val and par_val > 0) else None
    cap_gap = round(fund_cap - cap_implied, 1) if (fund_cap is not None and cap_implied is not None) else None
    g_market = round((3.0 * cur_mult - t_hist - t_roic) / 200.0, 4) if (cur_mult and t_hist is not None) else None
    g_gap = round(g_imp - g_market, 4) if (g_imp is not None and g_market is not None) else None
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
        "g_imp": g_imp,
        "imp_coupon": (g_imp + dy) if g_imp is not None else None,
        "irr_5y": irr_5y,
        "cap_implied": cap_implied,
        "cap_gap": cap_gap,
        "g_market": g_market,
        "g_gap": g_gap,
    }
