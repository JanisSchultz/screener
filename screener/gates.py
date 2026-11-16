"""Python reference implementation of the 6 Munger Quality Gates and the Quantitative PAR maths."""
from __future__ import annotations

import math

from . import config as C


def params(meta: dict) -> dict:
    p = {nm: val for _, ps in C.PARAMETER_GROUPS for nm, _, val, _, _ in ps}
    p.update(meta.get("parameters", {}))
    return p


def _score_val(raw) -> int | None:
    """Parse a 0/1/2 score value, returning None if blank or invalid."""
    if raw is None or raw == "" or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        iv = int(raw)
        if iv == raw and iv in C.SCORE_VALUES:
            return iv
        return None
    if isinstance(raw, str):
        s = raw.strip()
        if s in ("0", "1", "2"):
            return int(s)
    return None


def normalize_moat_label(label: str | None) -> str | None:
    """Normalize a Gate 3a moat string to canonical C.MOAT_TYPES when known (preserving non-empty legacy test strings)."""
    if label is None:
        return None
    s = str(label).strip()
    if not s:
        return None
    return C.LEGACY_MOAT_ALIASES.get(s, s)


def compute_initial_cap_from_scores(scores: tuple[int, ...] | list[int]) -> int:
    """Step 1 deterministic Initial CAP (years) from the 4 Gate 3 Moat Archetype scores (0/1/2 each):
      - max == 0                  ->  0Y (no moat -> fails Gate 3)
      - max == 1, sum == 1        -> 15Y
      - max == 1, sum >= 2        -> 20Y (capped at 20Y without an elite score of 2)
      - max == 2, sum == 2        -> 20Y
      - max == 2, sum == 3        -> 25Y
      - max == 2, sum >= 4        -> 30Y"""
    m_max = max(scores) if scores else 0
    m_sum = sum(scores)
    if m_max <= 0:
        return 0
    if m_max == 1:
        return 15 if m_sum == 1 else 20
    if m_sum <= 2:
        return 20
    if m_sum == 3:
        return 25
    return 30


def moderate_force_haircut(count_ones: int) -> int:
    """Tiered Step 2 moderate haircut (years) from the count of Porter Forces scored 1:
      0 -> 0Y, 1–2 -> 5Y, 3–4 -> 10Y, 5 -> 15Y."""
    if count_ones <= 0:
        return 0
    if count_ones <= 2:
        return 5
    if count_ones <= 4:
        return 10
    return 15


def compute_final_cap_from_scores(cap_init: int, force_scores: tuple[int, ...] | list[int]) -> tuple[int, int, bool]:
    """Step 2 deterministic Final CAP (years) from Initial CAP and the 5 Gate 4 Competitive Force scores (0/1/2 each).
    Returns (cap_final, mod_haircut, fatal_flaw):
      - Any Force == 2 triggers the Fatal-Flaw Cap (<= 10Y; 5Y when >=2 twos or cap_init - 10 - h <= 5; 0Y when >=3 twos).
      - Otherwise Final CAP = max(5, cap_init - h(c1)) on 5-year steps [0, 5, 10, 15, 20, 25, 30]."""
    c2 = sum(1 for x in force_scores if x == 2)
    c1 = sum(1 for x in force_scores if x == 1)
    h = moderate_force_haircut(c1)
    if cap_init <= 0 or c2 >= 3:
        return 0, h, c2 >= 1
    if c2 == 2:
        return 5, h, True
    if c2 == 1:
        rem = cap_init - 10 - h
        return (10 if rem >= 10 else 5), h, True
    return max(5, cap_init - h), h, False


def cap_audit(company: dict) -> dict:
    """Inspect Gate 3 Moat sub-scores and Gate 4 Force sub-scores, computing deterministic Initial & Final CAP when
    present while falling back cleanly to stored `3a` and `4` on unscored legacy rows."""
    m_map = {code: _score_val(company.get(code)) for code in C.MOAT_SCORE_CODES}
    f_map = {code: _score_val(company.get(code)) for code in C.FORCE_SCORE_CODES}
    m_present = sum(1 for v in m_map.values() if v is not None)
    f_present = sum(1 for v in f_map.values() if v is not None)
    moat_complete = m_present == len(C.MOAT_SCORE_CODES)
    moat_partial = 0 < m_present < len(C.MOAT_SCORE_CODES)
    force_complete = f_present == len(C.FORCE_SCORE_CODES)
    force_partial = 0 < f_present < len(C.FORCE_SCORE_CODES)

    stored_3a = normalize_moat_label(company.get("3a"))
    cap_init: int | None = None
    primary_moat: str | None = None

    if moat_complete:
        m_tuple = tuple(m_map[c] for c in C.MOAT_SCORE_CODES)  # type: ignore[misc]
        cap_init = compute_initial_cap_from_scores(m_tuple)
        m_max = max(m_tuple)
        if m_max == 0:
            primary_moat = "None"
        else:
            top_archs = [arch for (code, arch, _) in C.MOAT_SCORE_SPEC if m_map[code] == m_max]
            primary_moat = stored_3a if stored_3a in top_archs else top_archs[0]
    elif not moat_partial:
        primary_moat = stored_3a

    audited = False
    mod_haircut: int | None = None
    fatal_flaw = False
    raw_g4 = company.get("4")
    stored_cap = raw_g4 if isinstance(raw_g4, (int, float)) and not isinstance(raw_g4, bool) else None
    cap_final: int | float | None = None

    if moat_partial or force_partial or (force_complete and not moat_complete):
        cap_final = None
    elif moat_complete and cap_init == 0:
        cap_final = None
    elif moat_complete and force_complete and cap_init is not None:
        f_tuple = tuple(f_map[c] for c in C.FORCE_SCORE_CODES)  # type: ignore[misc]
        cap_final, mod_haircut, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)
        audited = True
    else:
        cap_final = stored_cap

    return {
        "moat_scores": m_map,
        "force_scores": f_map,
        "moat_complete": moat_complete,
        "moat_partial": moat_partial,
        "force_complete": force_complete,
        "force_partial": force_partial,
        "audited": audited,
        "primary_moat": primary_moat,
        "cap_init": cap_init,
        "mod_haircut": mod_haircut,
        "fatal_flaw": fatal_flaw,
        "cap_final": cap_final,
    }


def compute_initial_cap(company: dict) -> int | None:
    return cap_audit(company)["cap_init"]


def derive_primary_moat(company: dict) -> str | None:
    return cap_audit(company)["primary_moat"]


def compute_final_cap(company: dict) -> int | float | None:
    return cap_audit(company)["cap_final"]


def gate_status(company: dict, p: dict, g6_default: str | None = None, in_market: str = "Y") -> dict:
    """'pass' / 'fail' / 'blank' (not yet reviewed) per gate key in C.GATES order."""
    v = lambda c: company.get(c) if company.get(c) not in (None, "") else None
    audit = cap_audit(company)
    g2 = v("2") or ("N" if in_market == "N" else "Y")
    g6 = v("6") or (g6_default or None)
    num_v = lambda val, thr: "blank" if not isinstance(val, (int, float)) else ("pass" if val >= thr else "fail")
    yn = lambda x: "blank" if x is None else ("fail" if x == "N" else "pass")
    eff_3a = audit["primary_moat"]
    if audit["moat_partial"]:
        g3 = "blank"
    elif v("3b") == "N" or eff_3a == "None":
        g3 = "fail"
    elif v("3b") is None or eff_3a is None:
        g3 = "blank"
    else:
        g3 = "pass"
    return {"1": yn(v("1")), "2": yn(g2), "3b": g3, "4": num_v(audit["cap_final"], p["thr_cap"]),
            "5": num_v(v("5"), p["thr_culture"]), "6": yn(g6)}


def gate_results(company: dict, p: dict, g6_default: str | None = None, in_market: str = "Y") -> dict:
    st = gate_status(company, p, g6_default, in_market)
    return {"status": st, "ok": {k: s_ == "pass" for k, s_ in st.items()}}


def phase_results(company: dict, p: dict, g6_default: str | None = None, in_market: str = "Y") -> dict:
    """First non-waived failure or blank decides; calamity='Y' may waive Gates 3b, 5, and/or 6 only."""
    audit = cap_audit(company)
    g = gate_results(company, p, g6_default, in_market)
    st = g["status"]
    calamity = company.get("calamity") == "Y"
    eff_3a = audit["primary_moat"]
    has_3a = eff_3a not in (None, "") and not audit["moat_partial"]
    no_moat = eff_3a == "None"
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
# Asset-light fee financials valued as operating companies (tangible ROIC, r = 8.5%). Deposit-funded brokers
# (`Investment Banking & Brokerage`: SCHW, IBKR, AZA, SAVE, FBK) are NOT excluded since v6.36: they earn net interest
# income on client deposits that never enter "equity + debt − cash", so their operating ROIC is meaningless (SCHW 85–147%).
FEE_FINANCIAL_KEYWORDS = ("Insurance Brokers", "Asset Management & Custody Banks")
BALANCE_SHEET_KEYWORDS = ("Insurance", "Reinsurance", "Multi-Sector Holdings", "Banks", "Investment Banking & Brokerage")
CONCESSION_KEYWORDS = ("Construction & Engineering", "Highways & Railtracks")
# v7.1: opt-in list of ids whose concession assets revert to the grantor at expiry (no terminal value). Empty by
# default: contractors and concession groups (Vinci, Eiffage, WSP, SPIE …) renew or replace concessions.
FINITE_CONCESSION_IDS: frozenset[str] = frozenset()
# v7.5: an operating / fee company whose invested capital is <= 0 in at least 2 of the 5 ROIC years (clearing or customer
# cash on balance sheet: DB1, ADYEN, ENX) has no usable capital base; a plausible ROE (0 < ROE <= 50%) is the capital
# return instead. Buyback-shrunk or negative equity (FTNT 234%, RR 644%, MCK, VRSN) keeps GAAP ROIC.
IC_NEG_YEARS_FOR_ROE = 2
ROE_AS_CAPITAL_MAX = 0.50
# '[auto]' fin_note markers written by fetch_market_data.py that make the statements unusable for a per-share
# valuation until refetched or reviewed (status 'No data'). Mirrored by the dashboard sandbox (BLOCKING_AUTO_NOTES).
BLOCKING_AUTO_NOTES = ("stale fundamentals", "share count changed since FY", "currency switch unresolved",
                       "earnings dominated by non-cash marks")


def peak_weight(cur_year, peak_year) -> float:
    """v7.2 weight of the 5Y peak in the active Owner EPS when the latest year is below it: 50% while the peak is at
    most 1 year old, fading linearly to 0% at 4 years (a peak that old is no longer mid-cycle evidence)."""
    if not isinstance(cur_year, (int, float)) or not isinstance(peak_year, (int, float)):
        return 0.5
    age = cur_year - peak_year
    if age <= 1:
        return 0.5
    return max(0.0, 0.5 * (4.0 - age) / 3.0)


RONIC_FLOOR = 0.05                # floor on any RONIC used for reinvestment (avoids division blow-ups)
ROIC_TERM_MAX = 0.20              # default of config par_roic_term_max (terminal RONIC ceiling)
BUYBACK_CLAMP = (-0.03, 0.035)    # buyback_yield clamp before splitting into accretion (+) / dilution (−)


def roic_terminal(roic_start: float, r: float, roic_term_max: float = ROIC_TERM_MAX) -> float:
    """Terminal RONIC at the end of the CAP fade: min(RONIC_0, roic_term_max, r + 0.5 · (RONIC_0 − r)), floored."""
    return max(RONIC_FLOOR, min(roic_start, roic_term_max, r + 0.5 * (roic_start - r)))


def _r4(x: float) -> float:
    """Round half up to 4 dp — identical to the dashboard's JS Math.round(x * 1e4) / 1e4."""
    return math.floor(x * 10000.0 + 0.5) / 10000.0


def _r1(x: float) -> float:
    return math.floor(x * 10.0 + 0.5) / 10.0


def uses_gaap_roic(sub_industry: str | None) -> bool:
    """Return True where the operating-ROIC capital base is not used: Balance-Sheet Financials (valued on ROE, see
    is_balance_sheet_financial) and IFRIC-12 Infrastructure Concessions (GAAP ROIC incl. concession intangibles)."""
    return is_balance_sheet_financial(sub_industry) or is_concession_sector(sub_industry)


def is_concession_sector(sub_industry: str | None) -> bool:
    return isinstance(sub_industry, str) and any(kw in sub_industry for kw in CONCESSION_KEYWORDS)


def is_balance_sheet_financial(sub_industry: str | None) -> bool:
    """Return True for Balance-Sheet Financials (Insurers, Reinsurers, Banks, deposit-funded Brokers and Multi-Sector
    HoldCos), excluding asset-light fee financials (Insurance Brokers, Asset Management & Custody Banks)."""
    if not sub_industry or not isinstance(sub_industry, str):
        return False
    s = sub_industry.strip()
    if any(kw in s for kw in FEE_FINANCIAL_KEYWORDS):
        return False
    return any(kw in s for kw in BALANCE_SHEET_KEYWORDS)


def is_mtm_holdco(
    sub_industry: str | None,
    fcf_conv: float | None,
    mult_high_5y: float | None = None,
    ocf_ni_2y: float | None = None,
) -> bool:
    """Return True for Mark-to-Market HoldCos / Insurers where reported EPS already captures unrealized portfolio NAV
    appreciation: 5Y Owner FCF ÷ NI < 0.25, or latest-2Y OCF ÷ NI < 0.25 (catches III.GB, whose 5Y conversion still
    reads 0.43 while FY24–25 OCF/NI is 0.15 / 0.03)."""
    if not sub_industry or not isinstance(sub_industry, str):
        return False
    s = sub_industry.strip()
    if "Insurance Brokers" in s:
        return False
    if not ("Multi-Sector Holdings" in s or "Insurance" in s):
        return False
    if ocf_ni_2y is not None and ocf_ni_2y < 0.25:
        return True
    if fcf_conv is not None and fcf_conv < 0.25:
        return True
    if mult_high_5y is not None and mult_high_5y < 10.0:
        if (fcf_conv is not None and fcf_conv < 0.35) or (ocf_ni_2y is not None and ocf_ni_2y < 0.35):
            return True
    if fcf_conv is not None:
        return False
    return "Multi-Sector Holdings" in s and (mult_high_5y is None or mult_high_5y < 12.0)


def g6_checks(fin: dict, sub_industry: str | None, p: dict | None = None) -> dict:
    """v7.6 Gate 6 rule check — review flags only (your qualitative Gate 6 decides; never used by phase_results or
    par_valuation). {check: "ok" | "flag" | "n/a" | "info"} for net debt ÷ owner earnings (<= g6_netdebt_yrs),
    EBIT ÷ interest (> g6_intcov), 5Y owner FCF ÷ NI (>= a_fcfconv) and the peak-to-peak test. Balance-sheet
    financials: net debt and interest cover are n/a (debt and interest are their raw material), cash conversion is
    informational."""
    p = p or {}

    def f(k):
        v = fin.get(k)
        return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None

    bs = is_balance_sheet_financial(sub_industry)
    nd, ic, fc, pp = f("g6_netdebt_yrs"), f("g6_intcov"), f("fcf_conv"), fin.get("p2p_ok")
    lim_nd, lim_ic, lim_fc = p.get("g6_netdebt_yrs", 4.0), p.get("g6_intcov", 5.0), p.get("a_fcfconv", 0.80)
    grade = lambda ok: "n/a" if ok is None else ("ok" if ok else "flag")
    return {
        "netdebt": "n/a" if bs else grade(None if nd is None else nd <= lim_nd),
        "intcov": "n/a" if bs else grade(None if ic is None else ic > lim_ic),
        "fcfconv": ("info" if fc is not None else "n/a") if bs else grade(None if fc is None else fc >= lim_fc),
        "p2p": grade(None if pp not in ("Y", "N") else pp == "Y"),
    }


def is_finite_concession(cid: str | None) -> bool:
    """Return True only for ids explicitly listed in FINITE_CONCESSION_IDS (v7.1 opt-in; no automatic trigger)."""
    return isinstance(cid, str) and cid in FINITE_CONCESSION_IDS


def dcf_schedule_and_continuation(
    g0: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.030,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_end: float | None = None,
    roic_term_max: float = ROIC_TERM_MAX,
) -> tuple[float, float, float, float, list[float], float]:
    """Explicit N-Year Mauboussin-Fade DCF Fair P/E and 5-Year continuation schedule.
    Returns (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share, fcfs_5, v_5).
    - E_1 = 1.0 is the active (trailing, normalized) Owner EPS treated as Year-1 earnings — conservative by one year
      of growth versus a forward E_1 = EPS × (1 + g0).
    - At the end of each year t = 1..N (N = Gate 4 CAP), Reinv_t = E_t * max(0, g_t) / RONIC_t is deducted from E_t
      to fund Year-(t+1) growth E_{t+1} = E_t * (1 + g_t), with g_t and RONIC_t fading linearly from (g0, roic0) at t=1
      to (min(g0, g_term), min(roic0, roic_term_max = 20%, r + 0.5 * (roic0 - r))) at t=N.
    - Terminal value at t=N is McKinsey Value Driver TV_N = E_{N+1} * (1 - g_tv / RONIC_term) / (r - g_tv) with
      g_tv = max(0, min(g0, g_term)) (3.0% historical inflation pass-through, or g0 when g0 < 3.0%).
    - Exact Miller-Modigliani zero-spread invariance: when RONIC_t == r, total_dcf_pe == 1 / r for all g0 >= 0, N."""
    roic_start = max(RONIC_FLOOR, float(roic0))
    if mtm_holdco:
        nav_pe = 1.0 / roic_start
        return nav_pe, nav_pe, 0.0, 1.0, [0.0] * 5, nav_pe * ((1.0 + r) ** 5)
    n = max(1, int(round(float(n_cap) if (n_cap is not None and n_cap > 0) else 20.0)))
    roic_fin = roic_terminal(roic_start, r, roic_term_max) if roic_end is None else max(RONIC_FLOOR, float(roic_end))
    g_term_eff = min(g0, g_term)
    reinv_1 = max(0.0, g0) / roic_start
    pv_stage1 = 0.0
    e_t = 1.0
    fcfs: list[float] = []
    for t in range(1, n + 1):
        frac = (t - 1.0) / float(max(1, n - 1)) if n > 1 else 1.0
        g_t = g0 - frac * (g0 - g_term_eff)
        roic_t = roic_start - frac * (roic_start - roic_fin)
        reinv_t = max(0.0, g_t) / max(RONIC_FLOOR, roic_t)
        fcf_t = e_t * (1.0 - reinv_t)
        fcfs.append(fcf_t)
        pv_stage1 += fcf_t / ((1.0 + r) ** t)
        e_t = e_t * (1.0 + g_t)
    g_tv = max(0.0, g_term_eff)
    reinv_tv = g_tv / max(RONIC_FLOOR, roic_fin)
    fcf_tv = e_t * (1.0 - reinv_tv)
    tv_n = 0.0 if finite_conc else (fcf_tv / max(0.01, r - g_tv))
    pv_stage2 = tv_n / ((1.0 + r) ** n)
    total_pe = pv_stage1 + pv_stage2
    fcfs_5 = (fcfs + [fcf_tv] * 5)[:5]
    pv_first5 = sum(fcfs[t] / ((1.0 + r) ** (t + 1)) for t in range(min(5, n)))
    v_5 = max(0.0, (total_pe - pv_first5) * ((1.0 + r) ** min(5, n)))
    return total_pe, pv_stage1, pv_stage2, 1.0 - reinv_1, fcfs_5, v_5


def explicit_dcf_multiple(
    g0: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.030,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_end: float | None = None,
    roic_term_max: float = ROIC_TERM_MAX,
) -> tuple[float, float, float, float]:
    """Explicit N-Year Mauboussin-Fade DCF Fair P/E: (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share)."""
    return dcf_schedule_and_continuation(g0, roic0, n_cap, r, g_term, finite_conc, mtm_holdco, roic_end, roic_term_max)[:4]


def terminal_multiple(
    roic0: float,
    r: float = 0.085,
    g_term: float = 0.030,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_end: float | None = None,
    roic_term_max: float = ROIC_TERM_MAX,
) -> float:
    """Standalone McKinsey Value-Driver Terminal P/E at 3.0% historical inflation pass-through and 'keeping the lights on'
    reinvestment (g_term / RONIC_term), where RONIC_term = roic_terminal(roic_start, r, roic_term_max).
    When RONIC_term <= r, growth adds no value so g_inf = 0.0 and Terminal P/E = 1 / r."""
    if finite_conc:
        return 0.0
    roic_start = max(RONIC_FLOOR, float(roic0))
    if mtm_holdco:
        return 1.0 / roic_start
    roic_fin = roic_terminal(roic_start, r, roic_term_max) if roic_end is None else max(RONIC_FLOOR, float(roic_end))
    if roic_fin <= r:
        return 1.0 / r
    g_inf = max(0.0, g_term)
    return (1.0 - g_inf / roic_fin) / max(0.01, r - g_inf)


G_MARKET_LO, G_MARKET_HI, G_MARKET_STEP = -0.20, 0.50, 0.01
G_FLAG_OK = "ok"
G_FLAG_SAT_LO = "saturated_low"
G_FLAG_SAT_HI = "saturated_high"
G_FLAG_NO_VALUE = "no_value_creation"
G_FLAG_MULTI = "multi_root"
G_FLAG_NAV = "nav_anchored"
# v7.1: a saturated g_market is only a grid bound (≤ −20% / ≥ +50%), so the growth gap is left blank there.
G_GAP_FLAGS = (G_FLAG_OK,)


def solve_market_growth(
    target_pe: float | None,
    g0_ref: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.030,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_term_max: float = ROIC_TERM_MAX,
) -> tuple[float | None, str | None]:
    """Root-safe inversion of the Explicit DCF: starting organic growth g_market (fading to g_term over CAP N at r)
    whose DCF P/E equals target_pe. Scans a [-20%, +50%] grid in 1pp steps, bisects inside every sign-change bracket
    and returns (g_market, flag):
      ok                 unique root on a monotonic DCF_PE(g) curve
      saturated_low/high target outside the grid on a monotonic curve (g_market clamped to the grid edge)
      no_value_creation  DCF_PE falls as growth rises (ROIC <= r, or a finite concession without TV); root nearest g0
      multi_root         non-monotonic curve with several roots; root nearest g0
      nav_anchored       mark-to-market HoldCo valued at 1.0x NAV (growth inversion not meaningful)
    The dashboard sandbox (screener/dashboard.py solveImpliedDcfGrowth) mirrors this exactly."""
    if target_pe is None or target_pe <= 0:
        return None, None
    if mtm_holdco:
        return None, G_FLAG_NAV
    pe = lambda g: explicit_dcf_multiple(g, roic0, n_cap, r, g_term, finite_conc, False, None, roic_term_max)[0]
    n_pts = int(round((G_MARKET_HI - G_MARKET_LO) / G_MARKET_STEP))
    grid = [G_MARKET_LO + i * G_MARKET_STEP for i in range(n_pts + 1)]
    pes = [pe(g) for g in grid]
    increasing = all(b >= a - 1e-9 for a, b in zip(pes, pes[1:]))
    roots = []
    for i in range(n_pts):
        d0, d1 = pes[i] - target_pe, pes[i + 1] - target_pe
        if d0 == 0.0:
            roots.append(grid[i])
            continue
        if d0 * d1 < 0:
            lo, hi, f_lo = grid[i], grid[i + 1], d0
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                f_mid = pe(mid) - target_pe
                if (f_mid < 0) == (f_lo < 0):
                    lo, f_lo = mid, f_mid
                else:
                    hi = mid
            roots.append(0.5 * (lo + hi))
    if pes[-1] - target_pe == 0.0:
        roots.append(grid[-1])
    nearest = (lambda rs: _r4(min(rs, key=lambda x: abs(x - g0_ref)))) if roots else (lambda rs: None)
    if increasing:
        if roots:
            return _r4(roots[0]), G_FLAG_OK
        return (_r4(G_MARKET_LO), G_FLAG_SAT_LO) if target_pe < pes[0] else (_r4(G_MARKET_HI), G_FLAG_SAT_HI)
    i0, i10 = int(round(-G_MARKET_LO / G_MARKET_STEP)), int(round((0.10 - G_MARKET_LO) / G_MARKET_STEP))
    if pes[i10] < pes[i0]:
        return nearest(roots), G_FLAG_NO_VALUE
    return nearest(roots), G_FLAG_MULTI


IRR_LO, IRR_HI = -0.99, 2.50


def solve_irr_5y(cur_pe: float | None, fcfs_5: list[float] | tuple[float, ...] | None, v_5: float | None) -> float | None:
    """Bellman-consistent 5-Year Expected IRR: solves sum_{t=1..5} FCF_t / (1 + IRR)^t + V_5 / (1 + IRR)^5 = Cur_PE
    by 60-step bisection on [-99%, +250%]. IRR == r (8.50% / 10.25%) whenever Price == Fair Value."""
    if not cur_pe or cur_pe <= 0 or v_5 is None or fcfs_5 is None or len(fcfs_5) < 5:
        return None
    if sum(fcfs_5[:5]) + v_5 <= 0:
        return None

    def npv(rate: float) -> float:
        d = 1.0 + rate
        if d <= 1e-4:
            return 1e9
        return sum(fcfs_5[t] / (d ** (t + 1)) for t in range(5)) + v_5 / (d ** 5) - cur_pe

    lo, hi = IRR_LO, IRR_HI
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def active_roic(fin: dict, sub_industry: str | None) -> tuple[float | None, str | None]:
    """Capital-return input to the DCF reinvestment rate, with its source label.
    Priority (no analyst overrides since v7.6): Balance-Sheet Financials: roe_median (unless roe_median < 8.5% while roic_median >= 12%
    due to Up-C non-controlling interest mismatch) > IFRIC-12 concessions: roic_median (GAAP) > everyone else:
    roic_operating (tangible) > roic_median; except that an operating company with invested capital <= 0 in >= 2 of 5
    years and 0 < roe_median <= 50% uses roe_median (v7.5, customer / clearing cash balance sheets)."""
    def f(k):
        v = fin.get(k)
        return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None

    if is_balance_sheet_financial(sub_industry):
        roe_v, gaap_v = f("roe_median"), f("roic_median")
        if roe_v is not None and gaap_v is not None and roe_v < 0.085 and gaap_v >= 0.12:
            return gaap_v, "roic_median"
        for k in ("roe_median", "roic_median", "roic_operating"):
            if f(k) is not None:
                return f(k), k
        return None, None
    if not is_concession_sector(sub_industry):
        neg, roe_v = f("ic_neg_years"), f("roe_median")
        if neg is not None and neg >= IC_NEG_YEARS_FOR_ROE and roe_v is not None and 0 < roe_v <= ROE_AS_CAPITAL_MAX:
            return roe_v, "roe_median"
    order = ("roic_median", "roic_operating") if is_concession_sector(sub_industry) else ("roic_operating", "roic_median")
    for k in order:
        if f(k) is not None:
            return f(k), k
    return None, None


def ronic0(roic_active, r_tang, r_gaap, ma_reinvest, g0, gaap_basis) -> tuple[float, float]:
    """Raw marginal return on new capital (before the 5% floor / par_roic_cap) and the bought-growth share w.
    When goodwill-heavy (r_tang > 1.25 × r_gaap) the business keeps spending ma_reinvest (v7.2: Σ cash-funded
    Δ goodwill+intangibles ÷ Σ NOPAT over the g0 window) of earnings on acquisitions earning GAAP ROIC, i.e. bought growth g_m = ma_reinvest × r_gaap and w = clip(g_m / g0, 0, 1); the
    reinvestment rate g0 / RONIC₀ = (1 − w)·g0 / r_tang + w·g0 / r_gaap gives the growth-weighted harmonic blend.
    Mirrored by the dashboard sandbox (screener/dashboard.py ronic0)."""
    if (not gaap_basis and r_tang is not None and r_gaap is not None and r_gaap > 0
            and r_tang > 1.25 * r_gaap and ma_reinvest and ma_reinvest > 0 and g0 and g0 > 0):
        w = max(0.0, min(1.0, ma_reinvest * r_gaap / g0))
        return 1.0 / ((1.0 - w) / r_tang + w / r_gaap), w
    return roic_active, 0.0


def auto_note(fin: dict) -> str:
    """The machine-written '[auto] …' part of fin_note (rewritten by fetch_market_data.set_auto_note)."""
    s = str(fin.get("fin_note") or "")
    return s.split("[auto]", 1)[1] if "[auto]" in s else ""


def par_valuation(
    fin: dict,
    p: dict = None,
    cap: float | int | None = None,
    moat: str | None = None,
    sub_industry: str | None = None,
    scenario: dict | None = None,
) -> dict:
    """Python reference implementation of the Explicit Mauboussin-Fade DCF & Bellman-Consistent 5Y IRR.
    No analyst overrides (v7.6): every input comes from the statements. `scenario` is the dashboard sandbox's what-if
    mirror only (keys peak_eps, g (per-share growth incl. buybacks), ronic0) — used by the sandbox parity tests, never
    by data."""
    scenario = scenario or {}
    def f(k):
        v = fin.get(k)
        return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None

    p = p or {}
    k_op = p.get("par_cost_of_equity", 0.085)
    k_fin = p.get("par_cost_of_equity_fin", 0.1025)
    g_max = p.get("par_g_anchor_max", 0.130)
    roic_cap = p.get("par_roic_cap", 0.500)
    roic_term_max = p.get("par_roic_term_max", ROIC_TERM_MAX)
    g_base = p.get("par_g_base", 0.030)

    price, mc, ni = f("price"), f("market_cap_m"), f("ni_ttm_m")
    note_auto = auto_note(fin)

    sub_ind = sub_industry if isinstance(sub_industry, str) and sub_industry else fin.get("sub_industry")

    # Step 1 — Active Peak Owner EPS: age-weighted mid-cycle reversion toward the 5Y peak (scenario: sandbox what-if).
    peak_eps_override = scenario.get("peak_eps")
    oe_peak = f("peak_oe_eps")
    w_peak = None
    if peak_eps_override is not None:
        peak_eps = peak_eps_override
    else:
        cur_eps = f("cur_oe_eps")
        if cur_eps is None:
            add_stored = f("owner_add_m")
            if add_stored is not None:
                oe_add = max(0.0, add_stored)
            else:
                da_l, cx_l, ocf_l = f("da_ttm_m"), f("capex_ttm_m"), f("ocf_ttm_m")
                is_bs_fin = is_balance_sheet_financial(sub_ind) or ("Consumer Finance" in str(sub_ind or ""))
                if is_bs_fin or da_l is None or cx_l is None or abs(cx_l) <= 0.0:
                    oe_add = 0.0
                else:
                    da_eff = min(abs(da_l), max(0.0, ocf_l - ni)) if (ocf_l is not None and ni is not None) else abs(da_l)
                    oe_add = max(0.0, da_eff - abs(cx_l))
            cur_eps = (price * ((ni + oe_add) / mc)) if (mc and mc > 0 and ni is not None and price and price > 0) else oe_peak
        if oe_peak is not None and cur_eps is not None:
            if "check share basis" in note_auto:
                cur_eps = oe_peak
            elif "non-cash earnings spike left out of peak" in note_auto or cur_eps > 1.5 * oe_peak:
                cur_eps = min(cur_eps, oe_peak)
        if oe_peak is not None and cur_eps is not None and cur_eps < oe_peak:
            w_peak = peak_weight(f("cur_oe_year"), f("peak_oe_year"))
            cur_pos = max(0.0, cur_eps)
            peak_eps = cur_pos + w_peak * (oe_peak - cur_pos)
        else:
            peak_eps = oe_peak

    ml, mh = f("mult_low_5y"), f("mult_high_5y")
    g = f("cagr_oe_eps")
    dy = (f("dividends_ttm_m") or 0.0) / mc if (mc and mc > 0 and f("dividends_ttm_m") is not None) else 0.0
    fund_cap = cap if isinstance(cap, (int, float)) else f("cap")
    moat_arch = moat if isinstance(moat, str) and moat else fin.get("moat")
    roic, roic_source = active_roic(fin, sub_ind)
    roic_gaap = f("roic_median")
    roic_op = roic if roic is not None else 0.18

    # Step 3 — 4-Pillar Statistical Organic Growth Ceiling g0 (g_org_exp) and buyback accretion (g_exp).
    bb_raw = f("buyback_yield")
    bb_eff = max(BUYBACK_CLAMP[0], min(BUYBACK_CLAMP[1], bb_raw)) if bb_raw is not None else 0.0
    bb_pos, bb_org = max(0.0, bb_eff), min(0.0, bb_eff)
    sales_1y_val, sales_cagr_val = f("sales_1y"), f("sales_cagr")
    opcost_1y_val, opcost_cagr_val = f("opcost_1y"), f("opcost_cagr")
    g_est_in = scenario.get("g")
    has_stmt_growth = any(x is not None for x in (sales_cagr_val, opcost_cagr_val, sales_1y_val, g))

    if has_stmt_growth:
        # Anchor directly on 4-Pillar Statistical Organic Growth (sales_cagr, already dilution-adjusted via S_t),
        # with OpCost Theil-Sen CAGR, cycle Owner EPS CAGR (net of buybacks), and 1Y Sales (+ bb_org) as fallbacks.
        if sales_cagr_val is not None:
            raw_org = sales_cagr_val
        elif opcost_cagr_val is not None:
            raw_org = opcost_cagr_val
        elif g is not None:
            raw_org = g - bb_pos
        else:
            raw_org = sales_1y_val + bb_org
    else:
        raw_org = g_base
    g_org_start = _r4(max(0.0, min(g_max, raw_org)))
    g_start = _r4(min(g_max + bb_pos, g_org_start + bb_pos))
    if g_est_in is not None:
        g_org_exp = _r4(max(0.0, min(g_max, g_est_in - bb_pos)))
        g_exp = _r4(max(0.0, min(g_max + bb_pos, g_est_in)))
    else:
        g_org_exp = g_org_start
        g_exp = _r4(g_org_exp + bb_pos)

    # Step 2 — M&A-matched RONIC₀ (screener/gates.ronic0): bought growth earns GAAP ROIC, organic growth tangible ROIC.
    # ROE sits on goodwill-inclusive equity, so (like GAAP-basis sectors) no tangible / GAAP M&A blend
    gaap_basis = uses_gaap_roic(sub_ind) or roic_source == "roe_median"
    ronic_raw, alpha = ronic0(roic_op, f("roic_operating"), roic_gaap, f("ma_reinvest"), g_org_exp, gaap_basis)
    roic_exp = _r4(max(0.05, min(roic_cap, ronic_raw)))
    if scenario.get("ronic0") is not None:
        roic_exp, alpha = _r4(max(0.05, scenario["ronic0"])), 0.0

    # Industry physics: discount rate, NAV-anchored HoldCos, opt-in finite concessions.
    bs_fin = is_balance_sheet_financial(sub_ind)
    k = max(0.05, k_fin if bs_fin else k_op)
    mtm_holdco = is_mtm_holdco(sub_ind, f("fcf_conv"), mh, f("ocf_ni_2y"))
    finite_conc = is_finite_concession(fin.get("id"))
    eq_m = f("equity_m")
    bvps = (eq_m * price / mc) if (eq_m is not None and eq_m > 0 and mc and mc > 0 and price) else None
    nav_anchor = bool(mtm_holdco and bvps)

    out = {
        "status": C.V_NODATA, "peak_eps": peak_eps, "peak_weight": w_peak, "cur_mult": None, "par_mult": None, "par_val": None,
        "vs_par": None, "term_mult": None, "term_val": None, "vs_term": None,
        "irr_5y": None, "cap_implied": None, "cap_gap": None,
        "g_market": None, "g_market_flag": None, "g_gap": None,
        "pe_mm": None, "pe_mck": None, "pe_vd": None, "reinv_eff": None,
        "bvps": bvps, "nav_anchor": nav_anchor, "mtm_holdco": mtm_holdco, "finite_conc": finite_conc,
        "bs_fin": bs_fin, "k": k, "roic_source": roic_source, "roic_basis_gaap": gaap_basis, "roic_active": roic, "roic_exp": roic_exp,
        "ma_reinvest": f("ma_reinvest"), "ma_alpha": alpha, "ronic_le_r": (not mtm_holdco) and roic_exp <= k,
        "g": g, "dy": dy, "g_start": g_start, "g_org_start": g_org_start,
        "g_1y": sales_1y_val, "g_hist": sales_cagr_val if sales_cagr_val is not None else g, "g_cap": opcost_cagr_val,
        "g_exp": g_exp, "g_org_exp": g_org_exp, "fund_cap": fund_cap,
        "opcost_1y": opcost_1y_val, "opcost_cagr": opcost_cagr_val, "bb_eff": bb_eff,
    }

    has_hist_mults = bool(ml and mh)
    has_moat_arch = bool(moat_arch and str(moat_arch).strip() not in ("", "None"))
    if (
        any(tok in note_auto for tok in BLOCKING_AUTO_NOTES)
        or not price or not peak_eps or peak_eps <= 0
        or (not has_hist_mults and not fund_cap and peak_eps_override is None and not has_moat_arch)
    ):
        return out

    # Step 4 — Explicit N-Year DCF & Standalone Terminal Price at r = 8.50% (10.25% for Balance-Sheet Financials).
    cur_mult = price / peak_eps
    n_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else 20.0
    roic_eff = max(roic_exp, 0.05)
    pe_vd, pe_mm, pe_mck, fcf_share, fcfs_5, v_5 = dcf_schedule_and_continuation(
        g_org_exp, roic_eff, n_cap, k, g_base, finite_conc, mtm_holdco, None, roic_term_max
    )
    term_mult = terminal_multiple(roic_eff, k, g_base, finite_conc, mtm_holdco, None, roic_term_max)
    if nav_anchor:
        pe_vd = pe_mm = term_mult = bvps / peak_eps
        pe_mck = 0.0
        fcfs_5 = [0.0] * 5
        v_5 = pe_vd * ((1.0 + k) ** 5)
    par_mult = pe_vd
    par_val = bvps if nav_anchor else par_mult * peak_eps
    term_val = bvps if nav_anchor else term_mult * peak_eps
    vs_term = (price / term_val - 1.0) if (term_val and term_val > 0) else None
    out.update({"cur_mult": cur_mult, "par_mult": par_mult, "par_val": par_val,
                "term_mult": term_mult, "term_val": term_val, "vs_term": vs_term,
                "pe_mm": pe_mm, "pe_mck": pe_mck, "pe_vd": pe_vd, "reinv_eff": fcf_share})
    if par_val <= 0:
        # Growth funded at RONIC far below g: the DCF has no positive value (no discount / IRR is meaningful).
        out["status"] = C.V_NOVALUE
        return out

    # Step 5 — Valuation metrics, 5Y IRR, market-implied CAP and growth.
    vs_par = price / par_val - 1.0
    irr_5y = solve_irr_5y(cur_mult, fcfs_5, v_5)
    pe_base = 1.0 / k
    eff_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else (20.0 if has_moat_arch else None)
    if eff_cap:
        if not mtm_holdco and par_mult > pe_base + 0.5:
            cap_implied = _r1(max(0.0, eff_cap * (cur_mult - pe_base) / (par_mult - pe_base)))
        else:
            cap_implied = _r1(eff_cap * (price / par_val))
        cap_gap = _r1(eff_cap - cap_implied)
    else:
        cap_implied = cap_gap = None
    g_market, g_market_flag = solve_market_growth(cur_mult, g_org_exp, roic_eff, n_cap, k, g_base, finite_conc,
                                                  mtm_holdco, roic_term_max)
    g_gap = _r4(g_org_exp - g_market) if (g_market is not None and g_market_flag in G_GAP_FLAGS) else None
    out.update({
        "status": C.V_VALUED,
        "vs_par": vs_par, "irr_5y": irr_5y, "cap_implied": cap_implied, "cap_gap": cap_gap,
        "g_market": g_market, "g_market_flag": g_market_flag, "g_gap": g_gap,
    })
    return out
