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
# Asset-light fee financials valued as operating companies (tangible ROIC, r = 8.5%). Deposit-funded brokers
# (`Investment Banking & Brokerage`: SCHW, IBKR, AZA, SAVE, FBK) are NOT excluded since v6.36: they earn net interest
# income on client deposits that never enter "equity + debt − cash", so their operating ROIC is meaningless (SCHW 85–147%).
FEE_FINANCIAL_KEYWORDS = ("Insurance Brokers", "Asset Management & Custody Banks")
BALANCE_SHEET_KEYWORDS = ("Insurance", "Reinsurance", "Multi-Sector Holdings", "Banks", "Investment Banking & Brokerage")
CONCESSION_KEYWORDS = ("Construction & Engineering", "Highways & Railtracks")
# v7.1: opt-in list of ids whose concession assets revert to the grantor at expiry (no terminal value). Empty by
# default: contractors and concession groups (Vinci, Eiffage, WSP, SPIE …) renew or replace concessions.
FINITE_CONCESSION_IDS: frozenset[str] = frozenset()


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
    peak_eps_est: float | None,
    mult_high_5y: float | None = None,
    ocf_ni_2y: float | None = None,
) -> bool:
    """Return True for Mark-to-Market HoldCos / Insurers where reported EPS already captures unrealized portfolio NAV
    appreciation: 5Y Owner FCF ÷ NI < 0.25, or latest-2Y OCF ÷ NI < 0.25 (catches III.GB, whose 5Y conversion still
    reads 0.43 while FY24–25 OCF/NI is 0.15 / 0.03)."""
    if not sub_industry or not isinstance(sub_industry, str) or peak_eps_est is not None:
        return False
    s = sub_industry.strip()
    if "Insurance Brokers" in s:
        return False
    if not ("Multi-Sector Holdings" in s or "Insurance" in s):
        return False
    if ocf_ni_2y is not None and ocf_ni_2y < 0.25:
        return True
    if fcf_conv is not None:
        return fcf_conv < 0.25
    return "Multi-Sector Holdings" in s and (mult_high_5y is None or mult_high_5y < 12.0)


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
) -> tuple[float, float, float, float, list[float], float]:
    """Explicit N-Year Mauboussin-Fade DCF Fair P/E and 5-Year continuation schedule.
    Returns (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share, fcfs_5, v_5).
    - E_1 = 1.0 is the active (trailing, normalized) Owner EPS treated as Year-1 earnings — conservative by one year
      of growth versus a forward E_1 = EPS × (1 + g0).
    - At the end of each year t = 1..N (N = Gate 4 CAP), Reinv_t = E_t * max(0, g_t) / RONIC_t is deducted from E_t
      to fund Year-(t+1) growth E_{t+1} = E_t * (1 + g_t), with g_t and RONIC_t fading linearly from (g0, roic0) at t=1
      to (min(g0, g_term), min(roic0, 20%, r + 0.5 * (roic0 - r))) at t=N.
    - Terminal value at t=N is McKinsey Value Driver TV_N = E_{N+1} * (1 - g_tv / RONIC_term) / (r - g_tv) with
      g_tv = max(0, min(g0, g_term)) (3.0% historical inflation pass-through, or g0 when g0 < 3.0%).
    - Exact Miller-Modigliani zero-spread invariance: when RONIC_t == r, total_dcf_pe == 1 / r for all g0 >= 0, N."""
    roic_start = max(0.05, float(roic0))
    if mtm_holdco:
        nav_pe = 1.0 / roic_start
        return nav_pe, nav_pe, 0.0, 1.0, [0.0] * 5, nav_pe * ((1.0 + r) ** 5)
    n = max(1, int(round(float(n_cap) if (n_cap is not None and n_cap > 0) else 20.0)))
    roic_fin = (
        max(0.05, min(roic_start, 0.20, r + 0.5 * (roic_start - r)))
        if roic_end is None
        else max(0.05, float(roic_end))
    )
    g_term_eff = min(g0, g_term)
    reinv_1 = max(0.0, g0) / roic_start
    pv_stage1 = 0.0
    e_t = 1.0
    fcfs: list[float] = []
    for t in range(1, n + 1):
        frac = (t - 1.0) / float(max(1, n - 1)) if n > 1 else 1.0
        g_t = g0 - frac * (g0 - g_term_eff)
        roic_t = roic_start - frac * (roic_start - roic_fin)
        reinv_t = max(0.0, g_t) / max(0.05, roic_t)
        fcf_t = e_t * (1.0 - reinv_t)
        fcfs.append(fcf_t)
        pv_stage1 += fcf_t / ((1.0 + r) ** t)
        e_t = e_t * (1.0 + g_t)
    g_tv = max(0.0, g_term_eff)
    reinv_tv = g_tv / max(0.05, roic_fin)
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
) -> tuple[float, float, float, float]:
    """Explicit N-Year Mauboussin-Fade DCF Fair P/E: (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share)."""
    return dcf_schedule_and_continuation(g0, roic0, n_cap, r, g_term, finite_conc, mtm_holdco, roic_end)[:4]


def terminal_multiple(
    roic0: float,
    r: float = 0.085,
    g_term: float = 0.030,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_end: float | None = None,
) -> float:
    """Standalone McKinsey Value-Driver Terminal P/E at 3.0% historical inflation pass-through and 'keeping the lights on'
    reinvestment (g_term / RONIC_term), where RONIC_term = max(0.05, min(roic_start, 0.20, r + 0.5 * (roic_start - r))).
    When RONIC_term <= r, growth adds no value so g_inf = 0.0 and Terminal P/E = 1 / r."""
    if finite_conc:
        return 0.0
    roic_start = max(0.05, float(roic0))
    if mtm_holdco:
        return 1.0 / roic_start
    roic_fin = (
        max(0.05, min(roic_start, 0.20, r + 0.5 * (roic_start - r)))
        if roic_end is None
        else max(0.05, float(roic_end))
    )
    if roic_fin <= r:
        return 1.0 / r
    g_inf = max(0.0, g_term)
    return (1.0 - g_inf / roic_fin) / max(0.01, r - g_inf)


def compress_g0(raw_g: float, g_base: float = 0.030, g_max: float = 0.130) -> float:
    """Smooth Bayesian hyperbolic-tangent tail compression above g_base with asymptote g_max."""
    if raw_g <= g_base:
        return max(0.0, raw_g)
    span = max(1e-6, g_max - g_base)
    return g_base + span * math.tanh((raw_g - g_base) / span)


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
    pe = lambda g: explicit_dcf_multiple(g, roic0, n_cap, r, g_term, finite_conc, False)[0]
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
    Priority: roic_est override > Balance-Sheet Financials: roe_median (unless roe_median < 8.5% while roic_median >= 12%
    due to Up-C non-controlling interest mismatch) > IFRIC-12 concessions: roic_median (GAAP) > everyone else:
    roic_operating (tangible) > roic_median."""
    def f(k):
        v = fin.get(k)
        return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None

    if f("roic_est") is not None:
        return f("roic_est"), "roic_est"
    if is_balance_sheet_financial(sub_industry):
        roe_v, gaap_v = f("roe_median"), f("roic_median")
        if roe_v is not None and gaap_v is not None and roe_v < 0.085 and gaap_v >= 0.12:
            return gaap_v, "roic_median"
        for k in ("roe_median", "roic_median", "roic_operating"):
            if f(k) is not None:
                return f(k), k
        return None, None
    order = ("roic_median", "roic_operating") if is_concession_sector(sub_industry) else ("roic_operating", "roic_median")
    for k in order:
        if f(k) is not None:
            return f(k), k
    return None, None


def ronic0(roic_est, roic_active, r_tang, r_gaap, ma_reinvest, g0, gaap_basis) -> tuple[float, float]:
    """Raw marginal return on new capital (before the 5% floor / par_roic_cap) and the bought-growth share w.
    When goodwill-heavy (r_tang > 1.25 × r_gaap) a serial acquirer keeps spending ma_reinvest of earnings on
    acquisitions earning GAAP ROIC, i.e. bought growth g_m = ma_reinvest × r_gaap and w = clip(g_m / g0, 0, 1); the
    reinvestment rate g0 / RONIC₀ = (1 − w)·g0 / r_tang + w·g0 / r_gaap gives the growth-weighted harmonic blend.
    Mirrored by the dashboard sandbox (screener/dashboard.py ronic0)."""
    if (roic_est is None and not gaap_basis and r_tang is not None and r_gaap is not None and r_gaap > 0
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
) -> dict:
    """Python reference implementation of the Explicit Mauboussin-Fade DCF & Bellman-Consistent 5Y IRR (v7.1)."""
    def f(k):
        v = fin.get(k)
        return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None

    p = p or {}
    k_op = p.get("par_cost_of_equity", 0.085)
    k_fin = p.get("par_cost_of_equity_fin", 0.1025)
    g_max = p.get("par_g_anchor_max", 0.130)
    roic_cap = p.get("par_roic_cap", 0.500)
    g_base = p.get("par_g_base", 0.030)

    price, mc, ni = f("price"), f("market_cap_m"), f("ni_ttm_m")
    note_auto = auto_note(fin)

    # Step 1 — Active Peak Owner EPS: override > 50/50 mid-cycle reversion toward the 5Y peak.
    peak_eps_override = f("peak_eps_est")
    oe_peak = f("peak_oe_eps")
    if peak_eps_override is not None:
        peak_eps = peak_eps_override
    else:
        cur_eps = f("cur_oe_eps")
        if cur_eps is None:
            add_stored = f("owner_add_m")
            if add_stored is not None:
                oe_add = max(0.0, add_stored)
            else:
                da_l, cx_l = f("da_ttm_m"), f("capex_ttm_m")
                oe_add = max(0.0, abs(da_l) - abs(cx_l or 0.0)) if da_l is not None else 0.0
            cur_eps = (price * ((ni + oe_add) / mc)) if (mc and mc > 0 and ni is not None and price and price > 0) else oe_peak
        if oe_peak is not None and cur_eps is not None:
            if "check share basis" in note_auto:
                cur_eps = oe_peak
            elif "non-cash earnings spike left out of peak" in note_auto or cur_eps > 1.5 * oe_peak:
                cur_eps = min(cur_eps, oe_peak)
        if oe_peak is not None and cur_eps is not None and cur_eps < oe_peak:
            peak_eps = 0.5 * (oe_peak + max(0.0, cur_eps))
        else:
            peak_eps = oe_peak

    ml, mh = f("mult_low_5y"), f("mult_high_5y")
    g = f("cagr_oe_eps")
    dy = (f("dividends_ttm_m") or 0.0) / mc if (mc and mc > 0 and f("dividends_ttm_m") is not None) else 0.0
    fund_cap = cap if isinstance(cap, (int, float)) else f("cap")
    moat_arch = moat if isinstance(moat, str) and moat else fin.get("moat")
    sub_ind = sub_industry if isinstance(sub_industry, str) and sub_industry else fin.get("sub_industry")
    roic, roic_source = active_roic(fin, sub_ind)
    roic_gaap = f("roic_median")
    roic_op = roic if roic is not None else 0.18

    # Step 3 — 4-Pillar Statistical Organic Growth Ceiling g0 (g_org_exp) and buyback accretion (g_exp).
    bb_raw = f("buyback_yield")
    bb_eff = max(-0.03, min(0.035, bb_raw)) if bb_raw is not None else 0.0
    bb_pos, bb_org = max(0.0, bb_eff), min(0.0, bb_eff)
    sales_1y_val, sales_cagr_val = f("sales_1y"), f("sales_cagr")
    opcost_1y_val, opcost_cagr_val = f("opcost_1y"), f("opcost_cagr")
    g_imp_in, g_est_in = f("g_implied"), f("g_est")
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
    elif g_imp_in is not None:
        raw_org = g_imp_in - bb_pos + bb_org
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
    ronic_raw, alpha = ronic0(f("roic_est"), roic_op, f("roic_operating"), roic_gaap, f("ma_reinvest"), g_org_exp, uses_gaap_roic(sub_ind))
    roic_exp = _r4(max(0.05, min(roic_cap, ronic_raw)) if f("roic_est") is None else max(0.05, ronic_raw))

    # Industry physics: discount rate, NAV-anchored HoldCos, opt-in finite concessions.
    bs_fin = is_balance_sheet_financial(sub_ind)
    k = max(0.05, k_fin if bs_fin else k_op)
    mtm_holdco = is_mtm_holdco(sub_ind, f("fcf_conv"), peak_eps_override, mh, f("ocf_ni_2y"))
    finite_conc = is_finite_concession(fin.get("id"))
    eq_m = f("equity_m")
    bvps = (eq_m * price / mc) if (eq_m is not None and eq_m > 0 and mc and mc > 0 and price) else None
    nav_anchor = bool(mtm_holdco and bvps)

    out = {
        "status": C.V_NODATA, "peak_eps": peak_eps, "cur_mult": None, "par_mult": None, "par_val": None,
        "vs_par": None, "term_mult": None, "term_val": None, "vs_term": None,
        "irr_5y": None, "cap_implied": None, "cap_gap": None,
        "g_market": None, "g_market_flag": None, "g_gap": None,
        "pe_mm": None, "pe_mck": None, "pe_vd": None, "reinv_eff": None,
        "bvps": bvps, "nav_anchor": nav_anchor, "mtm_holdco": mtm_holdco, "finite_conc": finite_conc,
        "bs_fin": bs_fin, "k": k, "roic_source": roic_source, "roic_active": roic, "roic_exp": roic_exp,
        "ma_reinvest": f("ma_reinvest"), "ma_alpha": alpha, "ronic_le_r": (not mtm_holdco) and roic_exp <= k,
        "g": g, "dy": dy, "g_start": g_start, "g_org_start": g_org_start,
        "g_1y": sales_1y_val, "g_hist": sales_cagr_val if sales_cagr_val is not None else g, "g_cap": opcost_cagr_val,
        "g_exp": g_exp, "g_org_exp": g_org_exp, "fund_cap": fund_cap,
        "opcost_1y": opcost_1y_val, "opcost_cagr": opcost_cagr_val, "bb_eff": bb_eff,
    }

    has_hist_mults = bool(ml and mh)
    has_moat_arch = bool(moat_arch and str(moat_arch).strip() not in ("", "None"))
    if (
        "stale fundamentals" in note_auto
        or not price or not peak_eps or peak_eps <= 0
        or (not has_hist_mults and not fund_cap and peak_eps_override is None and not has_moat_arch)
    ):
        return out

    # Step 4 — Explicit N-Year DCF & Standalone Terminal Price at r = 8.50% (10.25% for Balance-Sheet Financials).
    cur_mult = price / peak_eps
    n_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else 20.0
    roic_eff = max(roic_exp, 0.05)
    pe_vd, pe_mm, pe_mck, fcf_share, fcfs_5, v_5 = dcf_schedule_and_continuation(
        g_org_exp, roic_eff, n_cap, k, g_base, finite_conc, mtm_holdco
    )
    term_mult = terminal_multiple(roic_eff, k, g_base, finite_conc, mtm_holdco)
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
        # Growth funded at RONIC far below g: the DCF has no positive value, so the stock can never be "Below PAR".
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
    g_market, g_market_flag = solve_market_growth(cur_mult, g_org_exp, roic_eff, n_cap, k, g_base, finite_conc, mtm_holdco)
    g_gap = _r4(g_org_exp - g_market) if (g_market is not None and g_market_flag in G_GAP_FLAGS) else None
    out.update({
        "status": C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR,
        "vs_par": vs_par, "irr_5y": irr_5y, "cap_implied": cap_implied, "cap_gap": cap_gap,
        "g_market": g_market, "g_market_flag": g_market_flag, "g_gap": g_gap,
    })
    return out
