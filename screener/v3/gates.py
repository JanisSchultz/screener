"""Python reference implementation of the Phase 1–3 gates and the Phase 4 maths.

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


def effective_scores(company: dict, overrides: list[dict]) -> dict:
    """Base scores with valid, non-duplicate overrides applied (same rule as the Overrides sheet)."""
    s = {c: company.get(c) for c in C.SCORE_CODES}
    seen = {}
    for o in overrides:
        if o.get("id") == company["id"]:
            seen.setdefault(o.get("code"), []).append(o.get("new_score"))
    for code, vals in seen.items():
        if code in s and len(vals) == 1 and vals[0] in C.SCORE_VALUES:
            s[code] = vals[0]
    return s


def quadrant(ess, rep, high):
    if ess is None or rep is None:
        return "n/a"
    e, r = ess >= high, rep >= high
    return "Target" if e and r else "Fad Trap" if r else "Long-Cycle Trap" if e else "Low/Low"


def phase_results(company: dict, overrides: list[dict], p: dict, in_circle: bool = True) -> dict:
    s = effective_scores(company, overrides)
    v = lambda c: s.get(c) if isinstance(s.get(c), (int, float)) else 0
    powers = [v(c) for c in C.POWER_CODES]
    s["3.2"] = max(powers)
    twos, ones = sum(x == 2 for x in powers), sum(x == 1 for x in powers)
    s["3.2x"] = 2 if twos >= 2 else 1 if twos == 1 and ones >= 1 else 0
    sub = {ph: sum(v(c) for c in items) for ph, items in C.PHASE_ITEMS.items()}
    quad = quadrant(s.get("2.1a"), s.get("2.1b"), p["quad_high"])
    cap = company.get("3.3n") if isinstance(company.get("3.3n"), (int, float)) else 0
    passed = {
        1: sub[1] >= p["thr_P1"] and v("1.3") >= p["ko_voluntary"],
        2: sub[2] >= p["thr_P2"] and not (p["ko_traps"] == 1 and quad in ("Fad Trap", "Long-Cycle Trap")),
        3: (sub[3] >= p["thr_P3"] and s["3.2"] >= p["thr_power"] and v("3.1a") >= p["thr_structure"]
            and cap >= p["thr_cap"] and v("3.4c") >= p["thr_capalloc"]),
    }
    wsum = p["w_P1"] + p["w_P2"] + p["w_P3"]
    score = 0 if wsum == 0 else round(100 * sum(p[f"w_P{ph}"] * sub[ph] / C.PHASE_MAX[ph] for ph in (1, 2, 3)) / wsum, 1)
    n = sum(passed.values())
    excluded = company.get("ps_exclude") == "Y" or not in_circle
    if excluded:
        res = C.RES_EXCL
    elif n == 3:
        res = C.RES_QPASS
    elif n >= p["nm_phases"] and score >= p["nm_score"]:
        res = C.RES_NEAR
    else:
        res = C.RES_FAIL
    return {"scores": s, "sub": sub, "quadrant": quad, "passed": passed, "score": score, "result": res}


def in_funnel(result: str, p: dict) -> bool:
    return result == C.RES_QPASS or (p.get("funnel_nearmiss") == 1 and result == C.RES_NEAR)


def circle_lookup(meta: dict) -> dict:
    return {(r["sector"], r["sub_industry"]): (r.get("in_circle") or "Y") != "N" for r in meta.get("prescreen", [])}


def funnel_ids(meta: dict) -> list[str]:
    p, circ = params(meta), circle_lookup(meta)
    out = []
    for c in meta["companies"]:
        r = phase_results(c, meta["overrides"], p, circ.get((c["sector"], c["sub_industry"]), True))
        if in_funnel(r["result"], p):
            out.append(c["id"])
    return out


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
