"""Framework configuration (v4): the gate-based 5-Phase Stock Evaluation Framework.

Pre-Screen (Simplicity & Sole-Owner) -> Phase 1 WHY -> Phase 2 WHAT -> Phase 3 HOW   [qualitative gates, all companies]
-> Phase 4 PROOF & ENTRY (audit, principal protection, equity bond, Stage 2) -> Phase 5 LIFECYCLE   [funnel only]

Every step is a REJECT gate: a company leaves the funnel at the first gate it fails. Gates are Y/N inputs;
the 2x2 matrix, moats and the "soft" items stay 0/1/2 (soft items reject only on 0).

Edit this file to change the framework, then run `python3 build.py`. Parameter values are the defaults written
into each workbook's Methodology sheet (universe.json "parameters" can override them per universe).
Earlier frameworks are archived in screener/v2/ and screener/v3/.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Qualitative fields (Inputs sheet). Order = column order.
#   type "gate": Y/N (blank = not yet reviewed -> passes, flagged on Data Checks)
#   type "score": 0/1/2 with rubric; "number": numeric with allowed values; "text": free text
#   seed: how migrate_v4.py filled the field from v3 data
# ---------------------------------------------------------------------------
def G(code, phase, section, short, name, seed, definition, reject):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="gate", seed=seed,
                definition=definition, rubric={"N": reject, "Y": "Passes the gate."})


def CAT(code, phase, section, short, name, seed, options, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="category", seed=seed,
                definition=definition, options=options)


def FLAG(code, phase, section, short, name, seed, definition):
    """Y/N information flag (not a gate)."""
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="flag", seed=seed,
                definition=definition)


def S(code, phase, section, short, name, seed, definition, r0, r1, r2, moat=False, soft=False):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="score", seed=seed,
                definition=definition, rubric={0: r0, 1: r1, 2: r2}, moat=moat, soft=soft)


def NUM(code, phase, section, short, name, seed, options, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="number", seed=seed,
                definition=definition, options=options)


def TXT(code, phase, section, short, name, seed, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="text", seed=seed,
                definition=definition)


MODEL_TYPES = ["Operating", "Bank", "Insurer", "Holding"]
MOAT_TYPES = ["Switching costs", "Scale economies", "Network effects", "Physical assets", "Intangibles",
              "Counter-positioning / process", "None"]
PRE, DEPR, AGENCY = ("Pre-Screen: Simplicity & Meaning", "1.3 The Deprivation Gate", "1.4 The Agency & Tail-Risk Gate")
MATRIX, PRICING = ("2.1 Purchase Frequency Matrix", "2.3 The Pricing Power Gate")
MOATS, VISIB, CULT = ("3.2 The Structural Defense (6 Moats)", "3.3 The 20-Year Visibility Gate (Qualitative CAP)",
                      "3.4 Culture & Capital Allocation")

FIELDS = [
    # ------------------------------------------------------------- PRE-SCREEN
    CAT("0.0", 0, PRE, "Model type", "Business-model type", "sub-industry rule, Claude review (v4.1)",
        MODEL_TYPES,
        "Operating / Bank / Insurer / Holding — selects the Phase 4 tests (Valuation). Information, not a gate."),
    G("0.1", 0, PRE, "Understandability", "Gate 1 — Understandability (Simplicity of choice)", "Claude re-score (v4.1)",
      "Negative check, default Y. Favours established, known business models over opaque or unknown ones. Holding "
      "companies, banks and insurers with known models pass.",
      "(a) Not established: novel or unproven model without a long public track record; or (b) not verifiable from "
      "outside: key risks invisible in reported numbers (large proprietary trading books, long-tail reserves only "
      "management can judge, complex structures / related-party webs, crypto treasury or single binary event)."),
    G("0.2", 0, PRE, "Sole-Owner", "Gate 2 — The Proud Sole-Owner (incl. your markets)",
      "v3 ps_exclude; v4.2: former Geopolitics N and London-listed businesses earning outside your markets",
      "If this were your only investment and the market closed for 20 years, would you be a proud and completely "
      "comfortable owner? Blank = N if the listing country is outside your markets (Pre-Screen), else the "
      "sub-industry default. Includes the geopolitical 'Where': N if customers sit mainly in sanctioned / pariah "
      "states or outside your markets.",
      "Not comfortable as sole owner for 20 years, violates your ethics, or the business lives outside your markets."),
    TXT("0.2r", 0, PRE, "Sole-Owner reason", "Gate 2 — reason (if N)", "v3 ps_reason / v4.2 migration", "Why the company fails Gate 2."),
    # ------------------------------------------------------------- PHASE 1: THE WHY
    G("1.3", 1, DEPR, "Deprivation", "The Deprivation Gate", "v3 1.4 Organic Deprivation ≥ 1",
      "If the product vanished tomorrow (zero contractual lock-in), would the end-user suffer a material impairment "
      "to their physical, operational, financial or psychological quality of existence?",
      "No material impairment — easily substituted or simply forgone."),
    G("1.4", 1, AGENCY, "Agency", "The Agency & Tail-Risk Gate", "v3 1.3 Voluntary Test ≥ 1",
      "Demand must not rely on physiological addiction or predatory mechanics (regulatory ruin, permanent multiple compression).",
      "Demand relies on addiction or predatory mechanics (tobacco/nicotine, gambling, predatory lending, addictive core model)."),
    # ------------------------------------------------------------- PHASE 2: THE WHAT
    S("2.1a", 2, MATRIX, "Essentiality", "Essentiality", "v3 2.1a",
      "Non-discretionary with a high cost of absence; unit volume holds in recessions.",
      "Discretionary; volume falls sharply or is deferred in downturns.",
      "Partly discretionary; moderate cyclical deferral.",
      "Non-discretionary; volume holds or grows through recessions."),
    S("2.1b", 2, MATRIX, "Repeat Frequency", "Repeat Frequency", "v3 2.1b",
      "Daily consumables, habitual purchases or mandatory subscriptions.",
      "One-off or long-cycle purchase.",
      "Periodic / multi-year cycle or mixed recurring share.",
      "Daily/monthly consumption, replenishment or mandatory recurring subscription."),
    FLAG("2.1c", 2, MATRIX, "Cyclical", "Cyclical earnings (Y)", "Claude pre-score (v4.1)",
         "Y = sales and margins swing with an economic or commodity cycle. Valuation then uses cycle-average earnings "
         "and sales / book-value growth (peak-earnings guard). Information, not a gate."),
    G("2.3", 2, PRICING, "Pricing Power", "The Pricing Power Gate",
      "v3 2.3b Real Pass-Through = 2, or = 1 with 2.3a Benefit-Cost Asymmetry = 2; v4.1 financial readings",
      "Can the company raise prices above real inflation without bleeding unit volume? Evidence includes the "
      "'Must-Carry' test (would gatekeepers lose clients without it?). Bank: deposit franchise — cheap, sticky "
      "deposits, reprices without losing customers. Insurer: underwriting discipline — holds rate through the soft "
      "cycle with combined ratio < 100%. Holding: look-through on the portfolio.",
      "Price taker, or merely passes through inflation."),
    # ------------------------------------------------------------- PHASE 3: THE HOW
    CAT("3.2", 3, MOATS, "Primary moat", "Primary moat (the exact barrier type)", "strongest of the v4.1 six moat scores",
        MOAT_TYPES,
        "Which of the 6 moats protects the returns: switching costs, scale economies (incl. shared), network effects / "
        "aggregators, irreplaceable physical assets, intangibles (patents, licences, brands), counter-positioning & "
        "process power. Description; the gate is 3.3 CAP."),
    NUM("3.3n", 3, VISIB, "CAP (yrs)", "Qualitative CAP — years of moat visibility (the moat gate)",
        "v3 3.3n; v4.2: capped at 5 where no moat scored 2 in v4.1",
        [0, 5, 10, 15, 20, 30],
        "Does the moat predictably exceed your 8–10-year horizon? After the erosion test (technology, regulation, "
        "patent cliffs) and brand & talent check. No strong moat ⇒ CAP ≤ 5. Below thr_cap (10) = REJECT."),
    TXT("3.3m", 3, VISIB, "Moat & erosion note", "Moat barrier and main erosion threats", "v4.1 3.2br + 3.3t",
        "What stops competitors arbitraging the returns away, and what could erode it."),
    S("3.4", 3, CULT, "Culture & Cap. Alloc.", "Culture & Capital Allocation", "MIN(v3 3.4a Owner Leadership, 3.4c Capital Allocation)",
      "\"Divine Discontent\" owner-oriented leaders, Planned Abandonment, rational reinvestment rather than "
      "empire-building. Rejects only below thr_culture (default: a 0).",
      "\"Locker Room Set\": promotional, empire-building M&A, chronic dilution.",
      "Competent but conventional; mixed record.",
      "Owner-oriented, prunes dying products, disciplined high-return reinvestment."),
]

FIELD_BY_CODE = {f["code"]: f for f in FIELDS}
GATE_CODES = [f["code"] for f in FIELDS if f["type"] == "gate"]
FLAG_CODES = [f["code"] for f in FIELDS if f["type"] == "flag"]
SCORE_CODES = [f["code"] for f in FIELDS if f["type"] == "score"]
SCORE_VALUES = (0, 1, 2)

# Ordered gate chain (Screen columns, "Rejected at", Summary funnel). (key, label, phase)
#   keys equal to a field code test that field; "quad" is derived on Screen / in gates.py
GATES = [
    ("0.1", "0.1 Understandability", 0), ("0.2", "0.2 Sole-Owner / markets", 0),
    ("1.3", "1.3 Deprivation", 1), ("1.4", "1.4 Agency", 1),
    ("quad", "2.1 2x2 Trap", 2), ("2.3", "2.3 Pricing Power", 2),
    ("3.3n", "3.3 Visibility (CAP)", 3), ("3.4", "3.4 Culture", 3),
]
PHASE_NAMES = {0: "Pre-Screen", 1: "THE WHY", 2: "THE WHAT", 3: "THE HOW", 4: "THE PROOF & ENTRY", 5: "THE LIFECYCLE"}
PHASE_LONG = {
    0: "Pre-Screen: Simplicity & Meaning (The Sole-Owner Gate)",
    1: "Phase 1: THE WHY (Customer Problem & Outside-In Utility)",
    2: "Phase 2: THE WHAT (Top-Line Demand Engine: Revenue = Volume × Price)",
    3: "Phase 3: THE HOW (Supply-Side Moat, Duration, Culture & Capital Allocation)",
    4: "Phase 4: THE PROOF & ENTRY (Financial Audit, Valuation Gates & Stage 2)",
    5: "Phase 5: THE LIFECYCLE (Post-Purchase Hold Band & Objective Sell Triggers)",
}

# ---------------------------------------------------------------------------
# Parameters -> Methodology input cells (Excel defined names). (name, label, default, fmt, note)
# ---------------------------------------------------------------------------
FW = "From the framework text."
NEW = "New in v4; adjust to taste."
NEW41 = "New in v4.1; adjust to taste."
NEW42 = "New in v4.2; adjust to taste."
V3 = "Carried over from v3."

PARAMETER_GROUPS = [
    ("Phase 1–3 gates", [
        ("ko_traps", "2.1 matrix: Fad Trap / Long-Cycle Trap rejects (1 = yes)", 1, "0", FW),
        ("quad_high", "2.1 matrix: score counted as 'High'", 2, "0", V3),
        ("thr_cap", "3.3 Visibility: min Qualitative CAP (years)", 10, "0", FW + " (< 10 years = REJECT)."),
        ("thr_culture", "3.4 Culture & Capital Allocation: min score", 1, "0", NEW + " 1 = reject only on 0."),
    ]),
    ("Phase 4 earnings", [
        ("n_peak", "'Peak margin' flag: latest net margin above median by more than", 0.20, "0%", NEW41),
        ("a_hist", "'Short history' flag: fewer years of data than", 7, "0", NEW42 + " ≈ one cycle; EU (Yahoo) has ~4 years."),
    ]),
    ("Phase 4.1 Quality & accounting gates", [
        ("a_roic", "Efficiency: median tangible ROIC (up to 10 yrs) min", 0.15, "0.0%", FW),
        ("a_roic_gaap", "Efficiency: median GAAP ROIC (incl. goodwill) min", 0.10, "0.0%", NEW42 +
         " Acquisitions must still earn above the cost of capital."),
        ("a_fcfconv", "Cash Integrity: owner FCF (after SBC & maintenance capex) ÷ net income min", 0.90, "0%", FW),
        ("a_dollar", "Buffett $1 test: Δ market cap ÷ retained earnings min", 1.0, "0.00\"x\"", FW),
        ("a_debt_yrs", "Resilience: long-term debt ÷ owner FCF max (years)", 5, "0.0", FW + " (3–5 years)."),
        ("a_intcov", "Resilience: interest coverage (EBIT ÷ interest) min", 10, "0.0\"x\"", FW),
    ]),
    ("Phase 4 tests for Bank / Insurer / Holding types", [
        ("f_roe", "Bank (ROTE) / Insurer (ROE) efficiency: median min", 0.12, "0.0%", NEW41),
        ("f_cr", "Insurer: combined ratio max (cycle average)", 1.00, "0.0%", NEW41),
        ("f_cet1", "Bank: CET1 ratio min", 0.12, "0.0%", NEW41),
        ("f_solv", "Insurer: solvency ratio min", 1.50, "0%", NEW41),
        ("f_nav_g", "Holding: NAV per share CAGR min", 0.10, "0.0%", NEW41),
        ("f_ltv", "Holding: loan-to-value max", 0.20, "0%", NEW41),
        ("f_navdisc", "Holding: principal protection = discount to NAV min", 0.10, "0%", NEW41),
    ]),
    ("Phase 4.2 Principal Protection", [
        ("v_mult_cap", "Multiple limit: M_c ≤ MIN(ROIC% × 100, this cap)", 35, "0", FW),
        ("v_hold_yrs", "Exit buffer: market-implied CAP n must be < holding period (years)", 10, "0", FW + " (8–10-year horizon)."),
        ("v_r", "Discount rate / WACC (r)", 0.09, "0.0%", V3),
        ("v_gt", "Terminal growth (g_T)", 0.03, "0.0%", V3),
        ("v_gcap", "Growth cap for g fallback", 0.15, "0.0%", V3),
    ]),
    ("Phase 4.3 Equity Bond", [
        ("v_eb", "Core hurdle: Y_c + g ≥", 0.12, "0.0%", FW),
    ]),
    ("Phase 4.4 Technical entry (Weinstein Stage 2)", [
        ("t_slope", "30-wk MA slope (5-wk change) counted as rising/falling beyond ±", 0.01, "0.0%", V3),
        ("t_near_high", "Within this % of 52-wk high = topping zone (Stage 3 when flat)", 0.10, "0%", V3),
    ]),
    ("Phase 5 Lifecycle (hold band & sell triggers)", [
        ("l_hold_hi", "Hold band: Y_c + 0.5g ≥ this = normal hold", 0.10, "0.0%", FW),
        ("l_hold_lo", "Stretched hold floor / Trigger 2: Y_c + 0.5g below", 0.08, "0.0%", FW),
        ("l_fcf_decay", "Trigger 1: owner FCF conversion below", 0.80, "0%", FW),
        ("l_opp", "Trigger 3: equal-quality alternative offers Y_c + g >", 0.12, "0.0%", FW),
    ]),
    ("Guard rails (inversion)", [
        ("r_max_age", "Review overdue after (days since your last review)", 365, "0", NEW41),
        ("p_max_pos", "Max position weight", 0.15, "0%", NEW41),
        ("p_min_cash", "Min cash weight", 0.05, "0%", NEW41 + " No margin / leverage assumed."),
    ]),
]

# Results
RES_QPASS = "Quality pass"
RES_REJ = {p: f"Rejected – {'Pre-Screen' if p == 0 else f'P{p} {PHASE_NAMES[p]}'}" for p in (0, 1, 2, 3)}
Q_RESULTS = [RES_QPASS] + [RES_REJ[p] for p in (3, 2, 1, 0)]

V_NOTFUNNEL = "Not in funnel"
V_NODATA = "No data"
V_AUDIT = "Audit fail"
V_VAL = "Watch – valuation"
V_TIME = "Watch – timing"
V_ENTRY = "Entry candidate"
V_UNREV = "Entry – unreviewed"
V_RESULTS = [V_ENTRY, V_UNREV, V_TIME, V_VAL, V_AUDIT, V_NODATA, V_NOTFUNNEL]

LIST_CAPACITY = {V_ENTRY: 100, "watch": 250, RES_QPASS: 300}
HOLDING_ROWS = 100

# US sector benchmarks (SPDR); EU sector map left empty (edit universe.json "sector_benchmarks")
US_SECTOR_ETFS = {"Communication Services": "XLC", "Consumer Discretionary": "XLY", "Consumer Staples": "XLP",
                  "Energy": "XLE", "Financials": "XLF", "Health Care": "XLV", "Industrials": "XLI",
                  "Information Technology": "XLK", "Materials": "XLB", "Real Estate": "XLRE", "Utilities": "XLU"}

CHANGELOG = {
    "2.0": [
        "Rebuilt from a Python generator; Inputs/Screen split; Overrides log; editable pillar weights; "
        "Quality – ROIC not met category; live shortlists; unique IDs; data validation and Data Checks.",
    ],
    "3.0": [
        "Framework replaced by the 5-Phase MECE Stock Evaluation Framework (Pre-Screen, WHY, WHAT, HOW, PROOF & ENTRY, LIFECYCLE).",
        "Phases 1–3 scored 0/1/2 for every company; Phase 4 audit and valuation for the funnel; Phase 5 Holdings sheet.",
        "fetch_market_data.py: SEC EDGAR fundamentals (US) and Yahoo Finance prices/statements.",
    ],
    "4.0": [
        "Gate-based framework: every step is a REJECT gate; 'Rejected at' shows the first failed gate.",
        "Dropped quality score, phase subtotals and weights, confidence multipliers, Near-miss, rank and the Overrides sheet.",
        "Inputs cut from 36 to 24 framework fields: Y/N gates (Simplicity, Sole-Owner, Geopolitics, Deprivation, Agency, "
        "Pricing Power) plus the 2x2 matrix, 6 moats, CAP years and four soft items that reject only on 0.",
        "New fields pre-scored by Claude (Simplicity, Geopolitics, Maslow level, Customer Breadth, Irreplaceable Physical "
        "Assets) — see 'Confidence v4' / 'v4 note'. Other v3 scores converted mechanically (see Methodology 'Seeded from').",
        "Phase 4: four audit gates (ROIC, Cash Integrity, $1 test, Resilience; growth CAGRs informational, 'No data' never rejects), "
        "Principal Protection (M_c ≤ MIN(ROIC×100, 35), implied CAP n < holding period, 30% MoS vs super-company DCF), "
        "Equity Bond Y_c + g ≥ 12% with Hohn floor; Town sticker price, justified P/E and Big Five gate removed.",
        "Phase 5: hold band and triggers on Y_c + 0.5g (8%/10%), implied n > CAP, opportunity Y_c + g > 12%.",
    ],
    "4.2": [
        "Simplified ('sure and simple'): gates cut from 13 to 8 and inputs from 27 to 14 fields after a redundancy "
        "check — dropped 1.1 Breadth, 1.1 Geopolitics (folded into Gate 2), 1.2 Maslow, 2.2 Runway, 2.2 Must-Carry "
        "(evidence for Pricing Power), 3.1 Structure; the six moat scores became one 'Primary moat' and CAP is the only "
        "moat gate (CAP capped at 5 where no strong moat).",
        "Market filter: only your markets (US; Nordics, DE, UK, FR, IT, ES, CH, AT, NL, BE, IE, PT) pass Gate 2.",
        "Audit fixes: ROIC test = tangible ROIC ≥ 15% and GAAP ROIC ≥ 10%; owner FCF uses maintenance capex "
        "(MIN(capex, depreciation)) instead of all capex.",
        "Valuation: three tests (multiple limit, exit buffer n, Equity Bond); DCF margin of safety, Hohn's floor and "
        "information-only columns removed; new buy-below price; intermediate columns grouped (collapsed).",
    ],
    "4.1": [
        "0.1 Simplicity → Understandability: negative check (reject only if not established or not verifiable from outside); "
        "120-second test dropped; all companies re-scored.",
        "Business-model type (Operating / Bank / Insurer / Holding) selects the Phase 4 tests: ROTE/ROE, CET1, solvency, "
        "combined ratio, NAV growth, loan-to-value, NAV discount. Financial readings of Pricing Power and Must-Carry; "
        "holding companies re-scored look-through.",
        "Normalised earnings: Y_c = MIN(latest, normalised) for earnings and FCF (median margin × sales; cycle-average "
        "earnings for cyclicals; median ROE × equity for banks/insurers); flags Peak margin / Below-normal / Short cycle; "
        "new 2.1c Cyclical flag; cyclicals' g from sales and book value.",
        "Guard rails: 'Entry candidate' requires your review date; review-overdue, position-size and cash warnings on "
        "Holdings; parameter-change log on Methodology; SELL only with 2+ triggers or Trigger 1.",
    ],
}
