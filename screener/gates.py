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


def is_finite_concession(sub_industry: str | None, fcf_conv: float | None) -> bool:
    """Return True for IFRIC-12 Infrastructure Concessions where concession assets amortize and revert to the state at expiry (D&A >> CapEx)."""
    if not is_concession_sector(sub_industry):
        return False
    return fcf_conv is not None and fcf_conv > 1.25


def dcf_schedule_and_continuation(
    g0: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.035,
    roic_term_base: float = 0.12,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_end: float | None = None,
) -> tuple[float, float, float, float, list[float], float]:
    """Compute Explicit N-Year Mauboussin-Fade DCF Fair P/E and 5-Year Continuation Schedule (v7.0):
    Returns (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share, fcfs_5, v_5).
    - Year 1 starts at normalized run-rate earnings E_1 = 1.0 on current capital IC_0.
    - At the end of each year t = 1..N (N = Gate 4 CAP), Reinv_t = E_t * max(0, g_t) / RONIC_t is deducted from E_t
      to fund Year-(t+1) growth E_{t+1} = E_t * (1 + g_t), with g_t and RONIC_t fading linearly from (g0, roic0) at t=1
      to (min(g0, g_term), min(roic0, 20%)) at t=N.
    - Terminal value at t=N is TV_N = E_{N+1} / r (post-CAP growth earns RONIC = r and adds zero NPV).
    - Guarantees exact Miller-Modigliani zero-spread invariance: when RONIC_t == r, total_dcf_pe == 1 / r for all g0, N."""
    roic_start = max(0.05, float(roic0))
    if mtm_holdco:
        nav_pe = 1.0 / roic_start
        return nav_pe, nav_pe, 0.0, 1.0, [0.0] * 5, nav_pe * ((1.0 + r) ** 5)
    n = max(1, int(round(float(n_cap) if (n_cap is not None and n_cap > 0) else 20.0)))
    roic_fin = min(roic_start, 0.20) if roic_end is None else max(0.05, float(roic_end))
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
    tv_n = 0.0 if finite_conc else (e_t / max(0.01, r))
    pv_stage2 = tv_n / ((1.0 + r) ** n)
    total_pe = pv_stage1 + pv_stage2
    fcfs_5 = (fcfs + [e_t] * 5)[:5]
    pv_first5 = sum(fcfs[t] / ((1.0 + r) ** (t + 1)) for t in range(min(5, n)))
    v_5 = max(0.0, (total_pe - pv_first5) * ((1.0 + r) ** min(5, n)))
    return total_pe, pv_stage1, pv_stage2, 1.0 - reinv_1, fcfs_5, v_5


def explicit_dcf_multiple(
    g0: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.035,
    roic_term_base: float = 0.12,
    finite_conc: bool = False,
    mtm_holdco: bool = False,
    roic_end: float | None = None,
) -> tuple[float, float, float, float]:
    """Compute Explicit N-Year Mauboussin-Fade DCF Fair Value P/E Multiple (v7.0):
    Returns (total_dcf_pe, pv_stage1, pv_stage2, stage1_fcf_share)."""
    return dcf_schedule_and_continuation(
        g0, roic0, n_cap, r, g_term, roic_term_base, finite_conc, mtm_holdco, roic_end
    )[:4]


G_MARKET_LO, G_MARKET_HI, G_MARKET_STEP = -0.20, 0.50, 0.01
G_FLAG_OK = "ok"
G_FLAG_SAT_LO = "saturated_low"
G_FLAG_SAT_HI = "saturated_high"
G_FLAG_NO_VALUE = "no_value_creation"
G_FLAG_MULTI = "multi_root"
G_FLAG_NAV = "nav_anchored"
G_GAP_FLAGS = (G_FLAG_OK, G_FLAG_SAT_LO, G_FLAG_SAT_HI)


def solve_market_growth(
    target_pe: float | None,
    g0_ref: float,
    roic0: float,
    n_cap: float | int | None,
    r: float = 0.085,
    g_term: float = 0.035,
    roic_term_base: float = 0.12,
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
    pe = lambda g: explicit_dcf_multiple(g, roic0, n_cap, r, g_term, roic_term_base, finite_conc, False)[0]
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
    nearest = (lambda rs: round(min(rs, key=lambda x: abs(x - g0_ref)), 4)) if roots else (lambda rs: None)
    if increasing:
        if roots:
            return round(roots[0], 4), G_FLAG_OK
        return (round(G_MARKET_LO, 4), G_FLAG_SAT_LO) if target_pe < pes[0] else (round(G_MARKET_HI, 4), G_FLAG_SAT_HI)
    i0, i10 = int(round(-G_MARKET_LO / G_MARKET_STEP)), int(round((0.10 - G_MARKET_LO) / G_MARKET_STEP))
    if pes[i10] < pes[i0]:
        return nearest(roots), G_FLAG_NO_VALUE
    return nearest(roots), G_FLAG_MULTI


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
    """Backwards-compatible wrapper: g_market only (see solve_market_growth for the flag)."""
    return solve_market_growth(target_pe, g0_ref, roic0, n_cap, r, g_term, roic_term_base, finite_conc, mtm_holdco)[0]


def solve_irr_5y(
    price_or_cur_pe: float | None,
    fcfs_or_par_val: list[float] | tuple[float, ...] | float | None,
    v5_or_g_exp: float | None,
    dy: float | None = 0.0,
) -> float | None:
    """Solve for the 5-Year Expected IRR (v7.0):
    1. Primary Bellman-Consistent DCF Schedule Mode (when fcfs_or_par_val is the 5-year FCF list):
       Solves sum_{t=1..5} [FCF_t / (1 + IRR)^t] + [V_5 / (1 + IRR)^5] = Cur_PE via 60-step bisection.
       Guarantees IRR == r (8.50% / 10.25%) whenever Price == Fair Value (Cur_PE == Fair_PE).
    2. Legacy 4-scalar Mode (price, par_val, g_exp, dy) kept for backwards-compatible unit test callers."""
    if isinstance(fcfs_or_par_val, (list, tuple)):
        cur_pe = price_or_cur_pe
        fcfs_5 = fcfs_or_par_val
        v_5 = v5_or_g_exp
        if not cur_pe or cur_pe <= 0 or v_5 is None or len(fcfs_5) < 5:
            return None
        if sum(fcfs_5[:5]) + v_5 <= 0:
            return None

        def npv(rate: float) -> float:
            d = 1.0 + rate
            if d <= 1e-4:
                return 1e9
            return sum(fcfs_5[t] / (d ** (t + 1)) for t in range(5)) + v_5 / (d ** 5) - cur_pe

        lo, hi = -0.50, 2.50
        f_lo, f_hi = npv(lo), npv(hi)
        if f_lo * f_hi > 0:
            return None
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if npv(mid) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    price, par_val, g_exp = price_or_cur_pe, fcfs_or_par_val, v5_or_g_exp
    if not price or price <= 0 or not par_val or par_val <= 0 or g_exp is None or g_exp <= -1.0:
        return None
    d = max(0.0, float(dy or 0.0))
    r_par = float(par_val) / float(price)
    if d <= 1e-12:
        return (1.0 + g_exp) * (r_par ** 0.2) - 1.0
    poly = lambda x: d * (x + x * x + x ** 3 + x ** 4 + x ** 5) + r_par * x ** 5 - 1.0
    u = (r_par ** -0.2) / (1.0 + d)
    converged = False
    for _ in range(50):
        u2 = u * u
        u3 = u2 * u
        u4 = u3 * u
        u5 = u4 * u
        f_val = d * (u + u2 + u3 + u4 + u5) + r_par * u5 - 1.0
        if abs(f_val) < 1e-12:
            converged = True
            break
        f_deriv = d * (1.0 + 2.0 * u + 3.0 * u2 + 4.0 * u3 + 5.0 * u4) + 5.0 * r_par * u4
        if f_deriv <= 0:
            break
        u = max(1e-6, u - f_val / f_deriv)
    if not converged and abs(poly(u)) > 1e-9:
        lo, hi = 0.0, 1.0
        while poly(hi) < 0 and hi < 1e6:
            hi *= 2.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if poly(mid) < 0:
                lo = mid
            else:
                hi = mid
        u = 0.5 * (lo + hi)
    return (1.0 + g_exp) / u - 1.0


def active_roic(fin: dict, sub_industry: str | None) -> tuple[float | None, str | None]:
    """Capital-return input to the DCF reinvestment rate, with its source label (v7.0).
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


def par_valuation(
    fin: dict,
    p: dict = None,
    cap: float | int | None = None,
    moat: str | None = None,
    sub_industry: str | None = None,
) -> dict:
    """Python reference implementation of the v7.0 Sure & Simple Explicit Mauboussin-Fade DCF & Bellman-Consistent 5Y IRR."""
    f = lambda k: None if (fin.get(k) is None or (isinstance(fin.get(k), float) and math.isnan(fin.get(k)))) else (fin.get(k) if isinstance(fin.get(k), (int, float)) else None)
    price = f("price")
    mc = f("market_cap_m")
    ni = f("ni_ttm_m")
    peak_eps_override = f("peak_eps_est")
    if peak_eps_override is not None:
        peak_eps = peak_eps_override
    else:
        oe_peak = f("peak_oe_eps")
        cur_oe = f("cur_oe_eps")
        if cur_oe is not None and cur_oe > 0:
            cur_eps = cur_oe
        else:
            add_stored = f("owner_add_m")
            if add_stored is not None:
                oe_add = max(0.0, add_stored)
            else:
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
    roic, roic_source = active_roic(fin, sub_ind)
    roic_gaap = f("roic_median")
    roic_op = roic if roic is not None else 0.18

    par_cost_of_equity = (p or {}).get("par_cost_of_equity", 0.085)
    par_cost_of_equity_fin = (p or {}).get("par_cost_of_equity_fin", 0.1025)
    par_g_anchor_max = (p or {}).get("par_g_anchor_max", 0.180)
    par_roic_cap = (p or {}).get("par_roic_cap", 0.500)
    par_g_base = (p or {}).get("par_g_base", 0.035)
    par_fade_cap30 = (p or {}).get("par_fade_cap30", 0.85)
    par_fade_cap20 = (p or {}).get("par_fade_cap20", 0.75)
    par_fade_cap15 = (p or {}).get("par_fade_cap15", 0.62)
    par_fade_default = (p or {}).get("par_fade_default", 0.62)

    ccy = fin.get("fin_currency") or fin.get("quote_currency") or "USD"
    fx_rate = C.FX_TO_USD.get(ccy, 1.0)
    mc_usd_b = ((mc or 0.0) * fx_rate) / 1000.0
    rev = f("sales_ttm_m") if f("sales_ttm_m") is not None else (f("revenue_ttm_m") if f("revenue_ttm_m") is not None else f("revenue_m"))
    rev_usd_b = (rev * fx_rate) / 1000.0 if (rev is not None and rev > 0) else None

    if rev_usd_b is not None:
        scale_tier = "HYPER" if rev_usd_b >= 250.0 else ("MEGA" if rev_usd_b >= 50.0 else ("LARGE" if rev_usd_b >= 15.0 else "MID/SM"))
    else:
        scale_tier = "HYPER" if mc_usd_b >= 1000.0 else ("MEGA" if mc_usd_b >= 250.0 else ("LARGE" if mc_usd_b >= 50.0 else "MID/SM"))
    scale_cap = par_g_anchor_max
    size_factor = 1.0

    if fund_cap is not None:
        pers = par_fade_cap30 if fund_cap >= 30 else (par_fade_cap20 if fund_cap >= 20 else par_fade_cap15)
    else:
        pers = par_fade_default
    g_mult = 200.0

    # Cost-Bloat Guarded Growth Ceiling (g_org_exp / g_0) & Buyback Accretion (v7.0):
    bb_raw = f("buyback_yield")
    bb_eff = max(-0.03, min(0.035, bb_raw)) if bb_raw is not None else 0.0
    bb_pos = max(0.0, bb_eff)
    bb_org = min(0.0, bb_eff)

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
        # Cost-bloat guard: 70/30 blend of OpCost & Sales WLS CAGR, bounded above by Sales WLS CAGR so
        # margin contraction (OpCost > Sales) never awards growth faster than revenue growth.
        if opcost_cagr_val is not None and sales_cagr_val is not None:
            base_org = min(sales_cagr_val, 0.70 * opcost_cagr_val + 0.30 * sales_cagr_val)
        elif opcost_cagr_val is not None:
            base_org = opcost_cagr_val
        elif sales_cagr_val is not None:
            base_org = sales_cagr_val
        else:
            base_org = (g - bb_pos) if g is not None else (sales_1y_val if sales_1y_val is not None else par_g_base)
        g_org_start = round(max(0.0, min(par_g_anchor_max, base_org + bb_org)), 4)
        g_start = round(max(-0.04, min(par_g_anchor_max + bb_pos, g_org_start + bb_pos)), 4)
    else:
        if f("g_est") is not None:
            g_start = round(f("g_est"), 4)
        elif g_imp_in is not None:
            g_start = round(max(0.0, g_imp_in), 4)
        else:
            g_start = par_g_base
        base_org = g_start - bb_pos
        g_org_start = round(max(0.0, min(par_g_anchor_max, base_org)), 4)

    if f("g_est") is not None:
        g_est_val = f("g_est")
        g_org_exp = round(max(0.0, min(par_g_anchor_max, g_est_val - bb_pos)), 4)
        g_exp = round(max(0.0, min(par_g_anchor_max + bb_pos, g_est_val)), 4)
    elif not has_stmt_growth and g_imp_in is not None:
        g_org_exp = round(max(0.0, min(par_g_anchor_max, g_imp_in - bb_pos)), 4)
        g_exp = round(g_org_exp + bb_pos, 4)
    else:
        g_org_exp = g_org_start
        g_exp = round(g_org_exp + bb_pos, 4)

    # M&A-Matched Harmonic RONIC & Single Initial Cap (par_roic_cap = 50%):
    # Serial acquirers whose Goodwill-inclusive capital base grows alongside top-line growth (cap_growth / g_raw)
    # blend harmonically from Tangible Operating ROIC toward GAAP ROIC (only when Goodwill > 20% of IC: r_tang > 1.25 * r_gaap).
    r_tang = f("roic_operating")
    if (
        f("roic_est") is None
        and not uses_gaap_roic(sub_ind)
        and r_tang is not None
        and roic_gaap is not None
        and r_tang > 1.25 * roic_gaap
        and roic_gaap > 0
        and cap_growth_val is not None
        and cap_growth_val > 0
    ):
        g_ref = max(0.04, base_org if has_stmt_growth else par_g_base)
        alpha = max(0.0, min(1.0, cap_growth_val / g_ref))
        ronic_raw = 1.0 / ((1.0 - alpha) / r_tang + alpha / roic_gaap)
    else:
        ronic_raw = roic_op
    roic_log = round(max(0.05, ronic_raw), 4)
    roic_exp = round(max(0.05, min(par_roic_cap, ronic_raw)) if f("roic_est") is None else max(0.05, ronic_raw), 4)
    roic_fade_ratio = round(roic_exp / roic_log, 4) if roic_log > 0 else 1.0

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

    g_log = g_org_exp
    g_fund = g_cap
    g_demand = g_hist
    g_raw = g_start

    has_hist_mults = bool(ml and mh)
    has_moat_arch = bool(moat_arch and str(moat_arch).strip() not in ("", "None"))
    if not price or not peak_eps or peak_eps <= 0 or (not has_hist_mults and not fund_cap and peak_eps_override is None and not has_moat_arch):
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
    g_org_val = g_org_exp if g_org_exp is not None else par_g_base

    # Explicit N-Year Mauboussin-Fade DCF at r = 8.50% (10.25% for Balance-Sheet Financials) (v7.0):
    bs_fin = is_balance_sheet_financial(sub_ind)
    k = max(0.05, par_cost_of_equity_fin if bs_fin else par_cost_of_equity)
    n_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else 20.0
    roic_eff = max(roic_exp, 0.05)
    mtm_holdco = is_mtm_holdco(sub_ind, fcf_conv_val, peak_eps_override, mh, f("ocf_ni_2y"))
    finite_conc = is_finite_concession(sub_ind, fcf_conv_val)

    pe_vd, pe_mm, pe_mck, reinv_eff, fcfs_5, v_5 = dcf_schedule_and_continuation(
        g_org_val, roic_eff, n_cap, k, par_g_base, 0.12, finite_conc, mtm_holdco
    )
    eq_m = f("equity_m")
    bvps = (eq_m * price / mc) if (eq_m is not None and eq_m > 0 and mc and mc > 0 and price) else None
    nav_anchor = bool(mtm_holdco and bvps)
    if nav_anchor:
        pe_vd = pe_mm = bvps / peak_eps
        pe_mck = 0.0
        fcfs_5 = [0.0] * 5
        v_5 = pe_vd * ((1.0 + k) ** 5)
    pe_vd0, _, _, _ = explicit_dcf_multiple(
        0.0, roic_eff, n_cap, k, par_g_base, 0.12, finite_conc, mtm_holdco
    )
    raw_slope = (pe_vd - pe_vd0) / g_org_val if g_org_val > 1e-6 else 100.0
    eff_g_mult = raw_slope if raw_slope > 10.0 else 100.0

    if has_hist_mults:
        t_hist_raw = (2.0 * ml * mh) / (ml + mh)
        t_hist = t_hist_raw
    else:
        t_hist_raw = None
        t_hist = pe_vd

    par_mult = pe_vd
    t_growth = pe_mm
    t_roic = pe_mck
    raw_par = pe_vd

    par_val = bvps if nav_anchor else par_mult * peak_eps
    vs_par = price / par_val - 1.0
    status = C.V_BELOW_PAR if vs_par <= 0 else C.V_ABOVE_PAR

    # Bellman-Consistent 5Y Expected IRR directly from Stage-1 DCF FCF_1..5 and Year-5 continuation Fair Value V_5:
    g_term_eff = min(g_org_val, par_g_base)
    g_irr = round(g_org_val - (2.0 / max(5.0, n_cap)) * (g_org_val - g_term_eff), 4) if not mtm_holdco else g_org_val
    pe5_ratio = (v_5 / (pe_vd * ((1.0 + g_irr) ** 5))) if (pe_vd > 0 and not mtm_holdco) else 1.0
    irr_5y = solve_irr_5y(cur_mult, fcfs_5, v_5)

    # Market-Implied CAP scaled above zero-moat steady-state base multiple (1 / r = 11.76x):
    pe_base = 1.0 / k
    eff_cap = float(fund_cap) if (fund_cap is not None and fund_cap > 0) else (20.0 if has_moat_arch else None)
    if eff_cap and price and par_val and par_val > 0:
        if not mtm_holdco and par_mult > pe_base + 0.5:
            cap_implied = round(max(0.0, eff_cap * (cur_mult - pe_base) / (par_mult - pe_base)), 1)
        else:
            cap_implied = round(eff_cap * (price / par_val), 1)
    else:
        cap_implied = None
    cap_gap = round(eff_cap - cap_implied, 1) if (eff_cap is not None and cap_implied is not None) else None

    g_market, g_market_flag = solve_market_growth(
        cur_mult, g_org_val, roic_eff, n_cap, k, par_g_base, 0.12, finite_conc, mtm_holdco
    )
    g_gap = (
        round(g_org_val - g_market, 4)
        if (g_org_val is not None and g_market is not None and g_market_flag in G_GAP_FLAGS)
        else None
    )
    return {
        "status": status,
        "peak_eps": peak_eps,
        "cur_mult": cur_mult,
        "par_mult": par_mult,
        "par_val": par_val,
        "vs_par": vs_par,
        "g_market_flag": g_market_flag,
        "pe5_ratio": round(pe5_ratio, 4),
        "bvps": bvps,
        "nav_anchor": nav_anchor,
        "mtm_holdco": mtm_holdco,
        "finite_conc": finite_conc,
        "bs_fin": bs_fin,
        "k": k,
        "roic_source": roic_source,
        "roic_active": roic,
        "fcf_share": reinv_eff,
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
