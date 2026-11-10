"""Python reference implementation of the Phase 1–3 gate chain and the Phase 4 maths.

The workbook formulas are the source of truth for users; this module mirrors them so that
(a) the fetcher can select the Phase 4 funnel without Excel and (b) tests can cross-check formulas.
"""
from __future__ import annotations

import math

from . import config as C


def params(meta: dict) -> dict:
    p = {nm: val for _, ps in C.PARAMETER_GROUPS for nm, _, val, _, _ in ps}
    p.update(meta.get("parameters", {}))
    return p


def quadrant(ess, rep, high):
    if ess is None or rep is None:
        return "n/a"
    e, r = ess >= high, rep >= high
    return "Target" if e and r else "Fad Trap" if r else "Long-Cycle Trap" if e else "Low/Low"


def gate_results(company: dict, p: dict, sole_owner_default: str = "Y", in_market: str = "Y") -> dict:
    """Pass (True) / reject (False) per gate key in C.GATES order, plus the 2x2 quadrant."""
    num = lambda c: company.get(c) if isinstance(company.get(c), (int, float)) else 0
    quad = quadrant(company.get("2.1a"), company.get("2.1b"), p["quad_high"])
    sole = company.get("0.2") or ("N" if in_market == "N" else sole_owner_default) or "Y"
    ok = {}
    for key, _, _ in C.GATES:
        if key == "0.2":
            ok[key] = sole != "N"
        elif key in C.GATE_CODES:
            ok[key] = company.get(key) != "N"
        elif key == "quad":
            ok[key] = not (p["ko_traps"] == 1 and quad in ("Fad Trap", "Long-Cycle Trap"))
        elif key == "3.3n":
            ok[key] = num(key) >= p["thr_cap"]
        elif key == "3.4":
            ok[key] = num(key) >= p["thr_culture"]
    return {"ok": ok, "quadrant": quad}


def phase_results(company: dict, p: dict, sole_owner_default: str = "Y", in_market: str = "Y") -> dict:
    g = gate_results(company, p, sole_owner_default, in_market)
    failed = [(k, lbl, ph) for k, lbl, ph in C.GATES if not g["ok"][k]]
    res = C.RES_REJ[failed[0][2]] if failed else C.RES_QPASS
    return {**g, "failed": failed, "rejected_at": failed[0][1] if failed else "", "result": res}


def sole_owner_lookup(meta: dict) -> dict:
    return {(r["sector"], r["sub_industry"]): (r.get("sole_owner") or "Y") for r in meta.get("prescreen", [])}


def market_lookup(meta: dict) -> dict:
    return {r["country"]: (r.get("in_market") or "Y") for r in meta.get("markets", [])}


def results(meta: dict) -> dict:
    """{company id: phase_results} using the Pre-Screen sub-industry and market tables."""
    p, so, mk = params(meta), sole_owner_lookup(meta), market_lookup(meta)
    return {c["id"]: phase_results(c, p, so.get((c["sector"], c["sub_industry"]), "Y"), mk.get(c.get("country"), "Y"))
            for c in meta["companies"]}


def funnel_ids(meta: dict) -> list[str]:
    res = results(meta)
    return [c["id"] for c in meta["companies"] if res[c["id"]]["result"] == C.RES_QPASS]


# ------------------------------------------------------------------ Phase 4 maths (reference)
def implied_cap_years(mc, fcf, g, r, gt):
    """Years n of growth at g priced in: MC/FCF = a/(1−a) + a^n·(K − a/(1−a)), a=(1+g)/(1+r), K=(1+gt)/(r−gt)."""
    if not mc or not fcf or fcf <= 0 or r <= gt or g == r:
        return None
    a, K = (1 + g) / (1 + r), (1 + gt) / (r - gt)
    A = a / (1 - a)
    x = (mc / fcf - A) / (K - A)
    if x <= 0 or a == 1:
        return None
    return math.log(x) / math.log(a)


def hohn_dcf(fcf, g, r, gt, n):
    a, K = (1 + g) / (1 + r), (1 + gt) / (r - gt)
    return fcf * (a * (1 - a ** n) / (1 - a) + a ** n * K)


def normalised_yc(fin: dict, model_type: str = "Operating", cyclical: str = "N"):
    """Reference for Valuation 'Y_c': MIN(latest, normalised) earnings and owner-FCF yields (Bank / Insurer earnings only,
    Holding dividend yield). Returns (yc, e_norm, fcf_norm) or (None, ...) when data is missing."""
    f = lambda k: fin.get(k) if isinstance(fin.get(k), (int, float)) else None
    mc, ni, sales = f("market_cap_m"), f("ni_ttm_m"), f("sales_ttm_m")
    if f("e_norm_est") is not None:
        e_norm = f("e_norm_est")
    elif cyclical == "Y":
        e_norm = f("ni_avg_m")
    elif model_type in ("Bank", "Insurer"):
        e_norm = f("roe_median") * f("equity_m") if None not in (f("roe_median"), f("equity_m")) else None
    else:
        e_norm = f("ni_margin_med") * sales if None not in (f("ni_margin_med"), sales) else None
    capex = min(f("capex_ttm_m"), f("da_ttm_m")) if None not in (f("capex_ttm_m"), f("da_ttm_m")) else f("capex_ttm_m")
    fcf = (f("ocf_ttm_m") - capex - (f("sbc_ttm_m") or 0)) if None not in (f("ocf_ttm_m"), capex) else None
    fcf_norm = f("fcf_margin_med") * sales if None not in (f("fcf_margin_med"), sales) else None
    if not mc:
        return None, e_norm, fcf_norm
    lo = lambda *xs: min(x for x in xs if x is not None)
    ep = lo(ni, e_norm) / mc if ni is not None else None
    fy = lo(fcf, fcf_norm) / mc if fcf is not None else None
    if model_type == "Holding":
        yc = (f("dividends_ttm_m") or 0) / mc
    elif model_type in ("Bank", "Insurer"):
        yc = ep
    else:
        yc = min(ep, fy) if None not in (ep, fy) else None
    return yc, e_norm, fcf_norm
