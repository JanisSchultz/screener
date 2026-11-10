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
PRE, CUST, MASLOW_S, DEPR, AGENCY = ("Pre-Screen: Simplicity & Meaning", "1.1 The Customer Profile",
                                     "1.2 The Core Customer Problem (Maslow)", "1.3 The Deprivation Gate",
                                     "1.4 The Agency & Tail-Risk Gate")
MATRIX, VOLUME, PRICING = ("2.1 Purchase Frequency Matrix", "2.2 Secular Volume & Gatekeepers", "2.3 The Pricing Power Gate")
STRUCT, MOATS, VISIB, CULT = ("3.1 Industry Structure & ROIC Paths", "3.2 The Structural Defense (6 Moats)",
                              "3.3 The 20-Year Visibility Gate (Qualitative CAP)", "3.4 Culture & Capital Allocation")

FIELDS = [
    # ------------------------------------------------------------- PRE-SCREEN
    CAT("0.0", 0, PRE, "Model type", "Business-model type", "sub-industry rule, Claude review",
        MODEL_TYPES,
        "Operating / Bank / Insurer / Holding — selects the Phase 4 tests (Valuation). Information, not a gate."),
    G("0.1", 0, PRE, "Understandability", "Gate 1 — Understandability (Simplicity of choice)", "Claude re-score (v4.1)",
      "Negative check, default Y. Favours established, known business models over opaque or unknown ones. Holding "
      "companies, banks and insurers with known models pass.",
      "(a) Not established: novel or unproven model without a long public track record; or (b) not verifiable from "
      "outside: key risks invisible in reported numbers (large proprietary trading books, long-tail reserves only "
      "management can judge, complex structures / related-party webs, crypto treasury or single binary event)."),
    G("0.2", 0, PRE, "Sole-Owner", "Gate 2 — The Proud Sole-Owner", "v3 ps_exclude (blank = Pre-Screen sub-industry default)",
      "If this were your only investment and the market closed for 20 years, would you be a proud and completely "
      "comfortable owner? Blank = use the sub-industry default on the Pre-Screen sheet.",
      "Not comfortable as sole owner for 20 years, or violates your ethics."),
    TXT("0.2r", 0, PRE, "Sole-Owner reason", "Gate 2 — reason (if N)", "v3 ps_reason", "Why the company fails Gate 2."),
    # ------------------------------------------------------------- PHASE 1: THE WHY
    TXT("1.1w", 1, CUST, "Who (decision chain)", "The \"Who\": end-user → gatekeepers", "blank (optional)",
        "Map the decision chain from the ultimate end-user to the intermediate gatekeepers."),
    S("1.1b", 1, CUST, "Breadth", "Customer Breadth", "v3 3.1b buyer power, Claude review",
      "Is the customer base diverse (insulating against localized shocks) or narrowly concentrated? Information only.",
      "Narrowly concentrated (few customers, one region or one end-market).",
      "Moderately diverse; some concentration.",
      "Broad, diverse base across customers, geographies and end-markets."),
    G("1.1g", 1, CUST, "Geo \"Where\"", "Geopolitical \"Where\"", "Claude pre-score",
      "Does the customer base reside in stable, globally accepted jurisdictions?",
      "Heavily concentrated in pariah states subject to severe tail-risks (sanctions, embargoes)."),
    NUM("1.2", 1, MASLOW_S, "Maslow level", "Maslow need satisfied (1 = strongest … 5 = weakest)", "Claude pre-score",
        [1, 2, 3, 4, 5],
        "1 Physiological/Survival; 2 Safety & Security; 3 Belonging & Connection; 4 Esteem & Efficiency; "
        "5 Self-Actualization & Identity. Information only (ranking and breakdowns)."),
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
    S("2.2a", 2, VOLUME, "Runway", "Secular Runway (organic TAM growth)", "v3 2.2a",
      "Is the total addressable market growing organically? Soft item: rejects only on 0.",
      "Structurally shrinking volume.",
      "Flat / GDP-like volume.",
      "Clear multi-year organic volume growth.", soft=True),
    S("2.2b", 2, VOLUME, "Must-Carry", "The \"Must-Carry\" Gatekeeper Test", "v3 2.2b",
      "Would a distributor or retailer lose their own clients if they refused to carry this brand? Soft item: rejects only on 0. "
      "Bank: would customers lose their primary-account relationship / payment rails? Insurer: must brokers and partners carry "
      "it (leading position, specialty capacity)? Holding: look-through on the portfolio.",
      "No — easily delisted or replaced by a private label / rival.",
      "Partly — carried for breadth; delisting causes little churn.",
      "Yes — gatekeepers must carry it (or the company sells direct with no gatekeeper able to block it).", soft=True),
    G("2.3", 2, PRICING, "Pricing Power", "The Pricing Power Gate",
      "v3 2.3b Real Pass-Through = 2, or = 1 with 2.3a Benefit-Cost Asymmetry = 2",
      "Can the company raise prices above real inflation without bleeding unit volume? Bank: deposit franchise — cheap, "
      "sticky deposits, reprices without losing customers. Insurer: underwriting discipline — holds rate through the soft "
      "cycle with combined ratio < 100%. Holding: look-through on the portfolio.",
      "Price taker, or merely passes through inflation."),
    # ------------------------------------------------------------- PHASE 3: THE HOW
    S("3.1a", 3, STRUCT, "Structure", "Industry Structure", "v3 3.1a",
      "Favor natural monopolies and rational duopolies. Soft item: rejects only on 0. "
      "The ROIC path (Margin vs Velocity, TATO > 1.0) is computed on Valuation.",
      "Fragmented or price-competitive structure, or weak share position.",
      "Oligopoly with periodic price competition, or #3+ in a rational market.",
      "Natural monopoly / toll bridge / rational duopoly; #1 or #2 with stable share.", soft=True),
    S("3.2a", 3, MOATS, "Switching Costs", "Switching Costs (lock-in / retraining risk)", "v3 3.2a",
      "Financial, procedural or relational friction after purchase.",
      "None.", "Moderate lock-in.", "Strong lock-in (system of record, installed base, retraining risk).", moat=True),
    S("3.2b", 3, MOATS, "Scale Economies", "Scale Economies & Scale Economies Shared", "v3 3.2b",
      "Fixed-cost spreading or purchasing leverage; savings passed back to customers (e.g. Costco).",
      "None.", "Some scale benefit, copyable.", "Structural scale / density advantage rivals cannot match.", moat=True),
    S("3.2c", 3, MOATS, "Network Effects", "Network Effects (or Fragmented Aggregators)", "v3 3.2c",
      "Value rises with the installed base, or aggregation of fragmented supply and demand.",
      "None.", "Weak or radial network.", "Strong multi-node network or aggregator.", moat=True),
    S("3.2d", 3, MOATS, "Physical Assets", "Irreplaceable Physical Assets", "Claude re-score (v3 Efficient Scale as baseline)",
      "High replacement cost or NIMBY infrastructure (pipelines, quarries, airports, rail, towers, landfills).",
      "None.", "Valuable but replicable assets.", "Irreplaceable / unpermittable assets.", moat=True),
    S("3.2e", 3, MOATS, "Intangibles", "Intangibles (patents, licenses, trusted brands)", "v3 3.2d",
      "Patents, regulatory licenses, trade secrets or trusted brands that prevent replication.",
      "None.", "Some protection, eroding or replicable.", "Durable, behaviour-changing intangible.", moat=True),
    S("3.2f", 3, MOATS, "Counter-Pos./Process", "Counter-Positioning & Process Power", "v3 3.2f",
      "A model incumbents refuse to copy (self-cannibalization), or opaque processes evolved over decades.",
      "None.", "Some edge, imitable within a few years.", "Incumbents structurally cannot copy it.", moat=True),
    TXT("3.2br", 3, MOATS, "Moat barrier", "The exact barrier preventing arbitrage", "v3 3.2br, else v3 3.2bb",
        "What stops competitors from arbitraging the returns away."),
    NUM("3.3n", 3, VISIB, "CAP (yrs)", "Qualitative CAP — years of moat visibility", "v3 3.3n",
        [0, 5, 10, 15, 20, 30],
        "Does the moat predictably exceed your 8–10-year horizon? After the erosion test (technology, regulation, "
        "patent cliffs) and brand & talent check. Below thr_cap (10) = REJECT."),
    TXT("3.3t", 3, VISIB, "Erosion threats", "Main erosion threats (tech, regulation, patents, brand, talent)",
        "built from v3 3.3a–f items scored below 2", "The threats that cap the CAP."),
    S("3.4", 3, CULT, "Culture & Cap. Alloc.", "Culture & Capital Allocation", "MIN(v3 3.4a Owner Leadership, 3.4c Capital Allocation)",
      "\"Divine Discontent\" owner-oriented leaders, Planned Abandonment, rational reinvestment rather than "
      "empire-building. Soft item: rejects only on 0.",
      "\"Locker Room Set\": promotional, empire-building M&A, chronic dilution.",
      "Competent but conventional; mixed record.",
      "Owner-oriented, prunes dying products, disciplined high-return reinvestment.", soft=True),
]

FIELD_BY_CODE = {f["code"]: f for f in FIELDS}
GATE_CODES = [f["code"] for f in FIELDS if f["type"] == "gate"]
FLAG_CODES = [f["code"] for f in FIELDS if f["type"] == "flag"]
SCORE_CODES = [f["code"] for f in FIELDS if f["type"] == "score"]
MOAT_CODES = [f["code"] for f in FIELDS if f.get("moat")]
SOFT_CODES = [f["code"] for f in FIELDS if f.get("soft")]
SCORE_VALUES = (0, 1, 2)

# Ordered gate chain (Screen columns, "Rejected at", Summary funnel). (key, label, phase)
#   keys equal to a field code test that field; the others are derived on Screen / in gates.py
GATES = [
    ("0.1", "0.1 Understandability", 0), ("0.2", "0.2 Sole-Owner", 0),
    ("1.1g", "1.1 Geopolitics", 1), ("1.3", "1.3 Deprivation", 1), ("1.4", "1.4 Agency", 1),
    ("quad", "2.1 2x2 Trap", 2), ("2.2a", "2.2 Runway", 2), ("2.2b", "2.2 Must-Carry", 2), ("2.3", "2.3 Pricing Power", 2),
    ("3.1a", "3.1 Structure", 3), ("moat", "3.2 Moat", 3), ("3.3n", "3.3 Visibility (CAP)", 3), ("3.4", "3.4 Culture", 3),
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
V3 = "Carried over from v3."

PARAMETER_GROUPS = [
    ("Phase 1–3 gates", [
        ("ko_traps", "2.1 matrix: Fad Trap / Long-Cycle Trap rejects (1 = yes)", 1, "0", FW),
        ("quad_high", "2.1 matrix: score counted as 'High'", 2, "0", V3),
        ("thr_soft", "Soft items (Runway, Must-Carry, Structure, Culture): min score", 1, "0", NEW + " 1 = reject only on 0."),
        ("thr_power", "3.2 Moat: min score of the strongest moat", 2, "0", V3 + " One strong barrier is enough."),
        ("thr_cap", "3.3 Visibility: min Qualitative CAP (years)", 10, "0", FW + " (< 10 years = REJECT)."),
    ]),
    ("Phase 3.1 ROIC path (information)", [
        ("p_margin", "High operating margin: EBIT ÷ sales ≥", 0.20, "0%", NEW),
        ("p_tato", "High asset velocity: Total Asset Turnover (sales ÷ assets) >", 1.0, "0.0", FW),
    ]),
    ("Phase 4 normalised earnings (peak-earnings guard)", [
        ("n_peak", "'Peak margin' flag: latest net margin above median by more than", 0.20, "0%", NEW41),
        ("n_min_years", "'Short cycle' flag: fewer margin years than", 7, "0", NEW41 + " EU (Yahoo) has ~4 years."),
    ]),
    ("Phase 4.1 Quality & accounting gates", [
        ("a_roic", "Efficiency: median ROIC (up to 10 yrs) min", 0.15, "0.0%", FW),
        ("a_fcfconv", "Cash Integrity: True FCF (after SBC & CapEx) ÷ net income min", 0.90, "0%", FW),
        ("a_dollar", "Buffett $1 test: Δ market cap ÷ retained earnings min", 1.0, "0.00\"x\"", FW),
        ("a_debt_yrs", "Resilience: long-term debt ÷ True FCF max (years)", 5, "0.0", FW + " (3–5 years)."),
        ("a_intcov", "Resilience: interest coverage (EBIT ÷ interest) min", 10, "0.0\"x\"", FW),
        ("a_hist", "History shorter than this many years is flagged 'short history'", 10, "0", NEW),
    ]),
    ("Phase 4 tests for Bank / Insurer / Holding types", [
        ("f_roe", "Bank (ROTE) / Insurer (ROE) efficiency: median min", 0.12, "0.0%", NEW41),
        ("f_cr", "Insurer: combined ratio max (cycle average)", 1.00, "0.0%", NEW41),
        ("f_cet1", "Bank: CET1 ratio min", 0.12, "0.0%", NEW41),
        ("f_solv", "Insurer: solvency ratio min", 1.50, "0%", NEW41),
        ("f_nav_g", "Holding: NAV per share CAGR min", 0.10, "0.0%", NEW41),
        ("f_ltv", "Holding: loan-to-value max", 0.20, "0%", NEW41),
        ("f_navdisc", "Holding: margin of safety = discount to NAV min", 0.10, "0%", NEW41),
    ]),
    ("Phase 4.2 Principal Protection", [
        ("v_mult_cap", "ROIC limit: M_c ≤ MIN(ROIC% × 100, this cap)", 35, "0", FW),
        ("v_hold_yrs", "Exit buffer: market-implied CAP n must be < holding period (years)", 10, "0", FW + " (8–10-year horizon)."),
        ("v_r", "Discount rate / WACC (r)", 0.09, "0.0%", V3),
        ("v_gt", "Terminal growth (g_T)", 0.03, "0.0%", V3),
        ("v_gcap", "Growth cap for g fallback", 0.15, "0.0%", V3),
        ("v_dcf_years", "Super-company DCF growth years (N)", 15, "0", FW + " (15–20 yrs)."),
        ("v_mos", "Margin of safety min (vs super-company DCF)", 0.30, "0%", FW),
    ]),
    ("Phase 4.3 Equity Bond", [
        ("v_eb", "Core hurdle: Y_c + g ≥", 0.12, "0.0%", FW),
        ("v_hohn", "Hohn's floor: Y_c + g_moat ≥", 0.09, "0.0%", FW),
        ("v_funding", "Funding break-even yield on cost", 0.07, "0.0%", FW),
    ]),
    ("Phase 4.4 Technical entry (Weinstein Stage 2)", [
        ("t_slope", "30-wk MA slope (5-wk change) counted as rising/falling beyond ±", 0.01, "0.0%", V3),
        ("t_near_high", "Within this % of 52-wk high = topping zone (Stage 3 when flat)", 0.10, "0%", V3),
        ("t_vol", "Heavy volume: last week ÷ 10-wk average ≥ (information only)", 1.5, "0.0", V3),
    ]),
    ("Phase 5 Lifecycle (hold band & sell triggers)", [
        ("l_hold_hi", "Hold band: Y_c + 0.5g ≥ this = normal hold", 0.10, "0.0%", FW),
        ("l_hold_lo", "Stretched hold floor / Trigger 2: Y_c + 0.5g below", 0.08, "0.0%", FW),
        ("l_fcf_decay", "Trigger 1: True FCF conversion below", 0.80, "0%", FW),
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
