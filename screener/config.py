"""Framework configuration (v6.26): the 6 Munger Quality Gates & Equity Bond Below PAR Framework.

Qualitative (6 Sequential Munger Reject Gates, all companies):
  Gate 1: Simple to Understand
  Gate 2: Essential Western Need & Low Societal / Legislative Risk
  Gate 3: Low Disruption Risk / 15+ Year Runway (CAP >= 15)
  Gate 4: Strong Moat & Pricing Power >= Inflation
  Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation
  Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Fortress Balance Sheet
-> Quantitative (Equity Bond Below PAR — 4–5Y Peak Owner EPS, PAR Multiple, Coupon & Timing)

Every qualitative step is a REJECT gate ("Tell me where I am going to die so that I never go there"):
a company leaves the funnel at the first gate it fails.
"""
from __future__ import annotations


def G(code, phase, section, short, name, seed, definition, reject):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="gate", seed=seed,
                definition=definition, rubric={"N": reject, "Y": "Passes the gate."})


def CAT(code, phase, section, short, name, seed, options, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="category", seed=seed,
                definition=definition, options=options)


def S(code, phase, section, short, name, seed, definition, r0, r1, r2, moat=False, soft=False):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="score", seed=seed,
                definition=definition, rubric={0: r0, 1: r1, 2: r2}, moat=moat, soft=soft)


def NUM(code, phase, section, short, name, seed, options, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="number", seed=seed,
                definition=definition, options=options)


def TXT(code, phase, section, short, name, seed, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="text", seed=seed,
                definition=definition)


MOAT_TYPES = [
    "Toll booth / Switching costs",
    "Scale economies shared",
    "Irreplaceable infrastructure",
    "R&D super-thinkers / Intangibles",
    "None",
]

S_G1 = "Gate 1: Simple to Understand"
S_G2 = "Gate 2: Essential Western Need & Entrenched Everyday Habits"
S_G3 = "Gate 3: Strong Moat & Pricing Power >= Inflation"
S_G4 = "Gate 4: Low Disruption Risk & Predictable Runway (15+ Yrs)"
S_G5 = "Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation"
S_G6 = "Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Fortress Balance Sheet"

FIELDS = [
    # ------------------------------------------------------------- GATE 1
    G("1", 1, S_G1, "Understandability", "Gate 1 — Simple to Understand", "",
      "Negative check, default Y. Favours established, transparent business models over opaque or unproven ones. "
      "Holding companies, banks and insurers with transparent, conventional models pass.",
      "(a) Not established: novel or unproven model without a long public track record; or (b) not verifiable from "
      "outside: key risks invisible in reported numbers (large proprietary trading books, opaque long-tail reserves, "
      "complex structures / related-party webs, crypto treasury or single binary event)."),
    # ------------------------------------------------------------- GATE 2
    G("2", 2, S_G2, "Essential Western Need", "Gate 2 — Essential Western Need & Entrenched Everyday Habits", "",
      "Does the company serve an essential customer need or an entrenched, high-propensity everyday habit / ritual ('likely to' spend) "
      "in the Western / rule-of-law world with low societal and legislative acceptance risk? Blank = N if the listing country is outside "
      "your markets (Pre-Screen), else Y. "
      "Encompasses both absolute functional necessities (utilities, healthcare, basic hygiene, critical infrastructure/logistics, grocery staples) "
      "and resilient, high-frequency everyday habits and cultural staples (iconic snacks/beverages, everyday dining, personal care, staple household entertainment, "
      "and Lindy-luxury compounders). "
      "Rejects true discretionary big-ticket / deferrable cyclicals (cruises, airlines, cyclical housing), speculative commodity price-takers, "
      "non-Western / pariah revenue bases, and addictive, predatory or socially destructive models exposed to legislative or societal ruin.",
      "Discretionary big-ticket / deferrable cyclical purchase, outside rule-of-law Western markets, or relies on addictive / predatory "
      "mechanics with high societal or legislative acceptance risk."),
    TXT("2r", 2, S_G2, "Essential Need reason", "Gate 2 — reason (if N)", "",
        "Why the company fails Gate 2 (e.g. discretionary big-ticket, outside target markets, or societal/legislative tail risk)."),
    # ------------------------------------------------------------- GATE 3
    CAT("3a", 3, S_G3, "Moat Archetype", "Gate 3a — Primary Moat Archetype", "",
        MOAT_TYPES,
        "Which structural moat protects the business: (1) Toll booth / Switching costs (incl. network effects & "
        "mission-critical workflow lock-in), (2) Scale economies shared, (3) Irreplaceable infrastructure / physical "
        "assets, (4) R&D super-thinkers / Intangibles (patents, licences, regulatory/engineering barriers), or None. "
        "Holding companies are evaluated on their look-through portfolio moats."),
    G("3b", 3, S_G3, "Pricing >= Inflation", "Gate 3b — Strong Moat, Proof of Moat & Ability to Raise Prices >= Inflation", "",
      "Protected by a strong moat (3a <> None) demonstrated by historical returns on capital (5Y median GAAP ROIC >= 12% "
      "and incremental ROIIC >= 12%) with the ability to raise prices at or above inflation over the cycle "
      "— whether via direct toll-booth / switching-cost pricing power, irreplaceable infrastructure, R&D differentiation, "
      "or scale economies shared with customers. Holding companies are evaluated on look-through portfolio moats and pricing power.",
      "No structural moat (None), commodity price taker, sub-hurdle historical returns (ROIC < 12%), or state-capped / eroding real economics unable to keep pace with inflation."),
    TXT("3m", 3, S_G3, "Moat & erosion note", "Gate 3m — Moat barrier, proof of moat and main erosion threats", "",
        "What stops competitors arbitraging the returns away, empirical proof of moat, and what could erode it."),
    # ------------------------------------------------------------- GATE 4
    NUM("4", 4, S_G4, "Runway — CAP (yrs)", "Gate 4 — Low Disruption Risk & Predictable Runway (CAP, yrs)", "",
        [0, 5, 10, 15, 20, 30],
        "Evaluates the structural longevity of the company's competitive advantage (Competitive Advantage Period, CAP) "
        "over a 15–20+ year horizon using Michael Mauboussin & Dan Callahan's two-step base-rate and haircut engine: "
        "(1) Outside View (Industry Base-Rate Persistence): Anchors on 54-year empirical persistence data (1970–2024): "
        "Tier 1 (Staples, Food/Bev, Personal Care: p=0.90, f=0.10 -> baseline 20–30Y); "
        "Tier 2 (MedTech Devices, Mission-Critical Hardware, Services: p=0.81–0.87, f=0.13–0.19 -> baseline 15–20Y); "
        "Tier 3 (Software, Pharma/Biotech, Semis, Capital Goods, Rails: p=0.75–0.79, f=0.21–0.25 -> baseline 10–15Y); "
        "Tier 4 (Energy, Telecom, Regulated Utilities: p=0.70–0.71, f=0.29–0.30 -> baseline 5–10Y, natural REJECT). "
        "(2) Inside View (5-Macrotrend Deductive Haircut Filter): Deductively reduces the baseline by -5 to -10 years if the business "
        "faces an active terminal headwind on: [1] Automation & Cognitive Tech (AI disruption of seat SaaS or IT consulting), "
        "[2] Demographic Aging & Labor Scarcity (human labor cost squeeze), [3] Geopolitical Realignment & Reshoring (single-source supply fragility), "
        "[4] Energy Transition & Resource Limits (carbon/grid bottlenecks), or [5] Structural Inflation & Cost of Capital (eroding real pricing power). "
        "Below thr_cap (15 years) = REJECT; blank = to review."),
    # ------------------------------------------------------------- GATE 5
    S("5", 5, S_G5, "Management (0/1/2)", "Gate 5 — Honest, Able, Customer-Focused Management & Capital Allocation", "",
      "Evaluates leadership across 5 vectors: (a) Integrity & Candor (Fisher/Buffett), (b) Rational Capital Allocation "
      "(Murphy/Thorndike — per-share compounding vs. empire M&A), (c) Customer Value-for-Money / Consumer Surplus "
      "(Bezos/Sleep), (d) Product-Led Execution, and (e) Anti-Bureaucracy & Planned Abandonment (Wallenberg/Drucker). "
      "Rejects on any fatal red flag below thr_culture (default: 0 = REJECT).",
      "Red flag triggered: promotional ego / aggressive accounting; value-destructive empire M&A; predatory price "
      "gouging that erodes customer trust; SG&A bloat; or bureaucratic complacency.",
      "Standard pass: honest, able stewardship and sensible capital allocation across all 5 vectors without red flags.",
      "Elite compounder: true owner-operator / Outsider CEO; radical candor, high customer surplus, product obsession, "
      "and exceptional per-share capital allocation."),
    # ------------------------------------------------------------- GATE 6
    G("6", 6, S_G6, "Cash & Peace-of-Mind Balance Sheet", "Gate 6 — Real Cash Conversion, Peak-to-Peak Compounding & Peace-of-Mind Balance Sheet", "",
      "Demonstrates a proven track record and structural visibility of achieving a new high in Owner EPS at the peak of each succeeding "
      "business cycle (temporary intra-cycle dips are normal, provided peak-to-peak secular growth continues). Accounting profits convert cleanly "
      "into free cash flow (FCF >= 80% of net income), free of maintenance capex or working-capital black holes. "
      "The balance sheet is structured for peace of mind: the company can comfortably survive a multi-year economic shock or complete credit market closure "
      "without permanently impairing common equity, and all leverage strictly amplifies an already superior, cash-generative engine rather than "
      "masking or compensating for a mediocre one. "
      "Exemptions/special cases: essential physical infrastructure and float institutions (insurers/holding companies) are evaluated on look-through "
      "operating earnings, solvency, and underwriting strength across cycles rather than GAAP accounting noise or mark-to-market swings. "
      "Surplus cash and T-bills held as dry powder count toward the fortress, never against the hurdle. "
      "Blank = the Pre-Screen sub-industry default (N for regulated utilities and deposit-taking banks), otherwise to review. "
      "Quantitative → 'G6 rule check' flags numeric indicators (net debt, coverage, peak status) for contextual review.",
      "Eroding or stagnant peak-to-peak earnings power (prior peak EPS represents an unrepeatable windfall or secular ceiling); reported "
      "accounting profits fail to convert cleanly into actual free cash flow (trapped on a capex treadmill or in working capital black holes); "
      "or the company relies on the 'kindness of strangers' — requiring continuous access to debt markets, short-term paper, or high-multiple equity issuance "
      "to fund operations, where an economic downturn, interest rate spike, or closed credit window risks permanent capital loss via bankruptcy, forced liquidation, "
      "or massive equity dilution."),
]

FIELD_BY_CODE = {f["code"]: f for f in FIELDS}
GATE_CODES = [f["code"] for f in FIELDS if f["type"] == "gate"]
SCORE_CODES = [f["code"] for f in FIELDS if f["type"] == "score"]
SCORE_VALUES = (0, 1, 2)

# Ordered 6-gate chain (Qualitative columns, "Rejected at", Summary funnel). (key, label, phase)
GATES = [
    ("1", "G1 Simple to Understand", 1),
    ("2", "G2 Essential Western Need", 2),
    ("3b", "G3 Moat & Pricing >= Infl.", 3),
    ("4", "G4 Runway (15+ Yrs)", 4),
    ("5", "G5 Management & Allocation", 5),
    ("6", "G6 Cash & Fortress Balance Sheet", 6),
]
# Gates eligible for a conditional temporary-fixable-calamity exception (Gates 1, 2, 3a, 4 are never waivable).
CALAMITY_GATES = ("3b", "5", "6")
CALAMITY_FLAG_DEF = (
    "Set to 'Y' only if the business fails Gate 3b, Gate 5, and/or Gate 6 due to a temporary, fixable calamity "
    "(Buffett principle) while Gates 1, 2, 3a (not None), and 4 (CAP >= 15) all pass and remaining downstream gates are evaluated. "
    "Requires calamity_note with broken metric, moat-intact evidence, and fix catalyst/kill-switch."
)
PHASE_NAMES = {
    1: "G1 Understandability",
    2: "G2 Essential Need",
    3: "G3 Moat & Pricing",
    4: "G4 Runway (<15Y)",
    5: "G5 Management",
    6: "G6 Cash & Fortress Balance Sheet",
    7: "QUANTITATIVE (PAR)",
}
PHASE_LONG = {
    1: "Gate 1: Simple to Understand (Transparent, Verifiable Business Model)",
    2: "Gate 2: Essential Western Need, Entrenched Everyday Habits & Low Societal / Legislative Acceptance Risk",
    3: "Gate 3: Strong Moat, Proof of Moat (ROIC >= 12%) & Ability to Raise Prices >= Inflation",
    4: "Gate 4: Low Disruption Risk & Predictable Runway (5-Macrotrend Secular Resilience, CAP >= 15 Years)",
    5: "Gate 5: Honest, Able, Customer-Value-Focused Management & Capital Allocation",
    6: "Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Fortress Balance Sheet",
    7: "Quantitative: Equity Bond Below PAR (4–5Y Peak Owner EPS, PAR Multiple, Coupon & Timing)",
}

# ---------------------------------------------------------------------------
# Parameters -> Methodology thresholds & valuation caps (universe.json can override).
# ---------------------------------------------------------------------------
FW = "From the framework text."
NEW = "Adjust to taste."

PARAMETER_GROUPS = [
    ("Qualitative Munger Reject Gates (Gates 1–6)", [
        ("thr_cap", "Gate 4 Runway: min predictable moat runway CAP (years)", 15, "0", FW + " (< 15 years = REJECT)."),
        ("thr_culture", "Gate 5 Management: min management & capital allocation score (0/1/2)", 1, "0", NEW + " 1 = reject on any red flag (score 0)."),
    ]),
    ("Financial health indicators (colour-coded context on Quantitative)", [
        ("a_roic_gaap", "Efficiency indicator: median GAAP ROIC (incl. goodwill) green threshold", 0.10, "0.0%", NEW),
        ("a_fcfconv", "Cash conversion indicator: owner FCF ÷ net income green threshold", 0.80, "0%", FW),
        ("a_debt_yrs", "Debt indicator: long-term debt ÷ owner earnings green max (years)", 4.0, "0.0", FW + " (≤ 4 years green)."),
        ("a_intcov", "Interest coverage indicator: EBIT ÷ interest green threshold", 10.0, "0.0\"x\"", FW),
    ]),
    ("Gate 6 rule check (flags on Quantitative for your review — never rejects on its own)", [
        ("g6_netdebt_yrs", "Gate 6: max net debt ÷ owner earnings (years)", 4.0, "0.0", FW + " (net debt repayable in ≤ 4 years)."),
        ("g6_intcov", "Gate 6: min interest coverage EBIT ÷ interest", 5.0, "0.0\"x\"", FW + " (> 5x through the cycle)."),
    ]),
    ("Timing context (Weinstein Stage 2 & Dip)", [
        ("t_slope", "30-wk MA slope (5-wk change) counted as rising/falling beyond ±", 0.01, "0.0%", NEW),
        ("t_near_high", "Within this % of 52-wk high = topping zone (Stage 3 when flat)", 0.10, "0%", NEW),
    ]),
    ("PAR Valuation parameters (Quantitative sheet)", [
        ("par_roic_cap", "Max ROIC points counted toward PAR multiple (operating-side ROIC proxy, neutralizes buyback/negative equity distortions)", 35.0, "0.0", NEW + " Caps ROIC*100 at 35.0 (proxy for true uncorrupted operating ROIC: OTIS 32.7%, AZO 35.7%, AAPL 35.2%)."),
        ("par_g_cap", "Max sustainable forward growth rate (Mauboussin 75-year large-cap ceiling)", 0.12, "0.0%", NEW + " Caps forward through-the-cycle growth at 12.0% based on empirical regression data (Ex. 18/19)."),
        ("par_g_base", "Baseline mature growth anchor for fallback regression", 0.07, "0.0%", NEW + " Empirical baseline large-cap growth rate (7.0%)."),
        ("par_fade_cap30", "Mauboussin growth persistence for Gate 4 CAP >= 30 years (fortress moats/monopolies)", 0.25, "0.00", NEW + " Slower autoregressive fade for ultra-long runway compounders."),
        ("par_fade_cap20", "Mauboussin growth persistence for Gate 4 CAP >= 20 years (standard quality compounders)", 0.15, "0.00", NEW + " Empirical 75-year market-wide autoregressive baseline."),
        ("par_fade_cap15", "Mauboussin growth persistence for Gate 4 CAP >= 15 years (shorter runway / higher transition risk)", 0.10, "0.00", NEW + " Faster autoregressive fade towards baseline."),
        ("par_fade_default", "Fallback growth persistence when CAP is unpopulated", 0.15, "0.00", NEW + " Default fallback persistence coefficient."),
    ]),
]

# Results
RES_QPASS = "Quality pass"
RES_CALAMITY = "Calamity pass"
FUNNEL_RESULTS = (RES_QPASS, RES_CALAMITY)
RES_REJ = {p: f"Rejected – {PHASE_NAMES[p]}" for p in (1, 2, 3, 4, 5, 6)}
RES_REVIEW = "To review (blank gate)"
Q_RESULTS = [RES_QPASS, RES_CALAMITY, RES_REVIEW] + [RES_REJ[p] for p in (6, 5, 4, 3, 2, 1)]

V_NOTFUNNEL = "Not in funnel"
V_NODATA = "No data"
V_BELOW_PAR = "Below PAR"
V_ABOVE_PAR = "Above PAR"
V_CALAMITY = "Calamity Watchlist"
V_RESULTS = [V_BELOW_PAR, V_ABOVE_PAR, V_NODATA, V_NOTFUNNEL]

LIST_CAPACITY = {V_BELOW_PAR: 150, V_ABOVE_PAR: 200, V_CALAMITY: 100}

CHANGELOG = {
    "6.0": [
        "Two-Part Qualitative & Quantitative Architecture ('Equity Bond Below PAR'): "
        "(1) Unified 'Qualitative' sheet ('The Best Street') and 'Quantitative' sheet ('Equity Bond Below PAR') "
        "using one universal Owner EPS definition (Continuing Net Income + max(0, D&A - CapEx) per diluted share). "
        "(2) 4–5 Year Business Cycle PAR Valuation comparing Current Price to PAR Value (PAR Multiple × Last Peak Owner EPS) "
        "alongside both Historical Coupon (g + DY) and 5–10Y forward Implied Coupon (Implied Owner EPS g + DY).",
    ],
    "6.1": [
        "6 Munger Quality Gates & Clean v6 Schema: "
        "(1) Streamlined the 'Qualitative' sheet into 6 sequential Munger Reject Gates ('Tell me where I am going to die so that I never go there'): "
        "G1 Simple to Understand, G2 Essential Western Need & Low Societal/Legislative Risk, "
        "G3 Low Disruption Risk / 15+ Year Runway (CAP >= 15 yrs), G4 Strong Moat & Pricing Power >= Inflation "
        "(Toll booths / Switching costs, Scale economies shared, Irreplaceable infrastructure, R&D super-thinkers / Intangibles), "
        "G5 Honest, Able, Customer-Focused Management & Capital Allocation, and "
        "G6 Predictable FCF Conversion Across Cycles, Minimal Leverage & High Incremental ROIC. "
        "(2) Removed all legacy v2.0–v5.9 residuals (retired 'Re-evaluation history' tab, 'Shortlists' Table 3 duplicate, "
        "and 18 unused legacy qualitative/financial columns).",
    ],
    "6.2": [
        "Excel Formula Consistency & Green-Triangle Suppression: "
        "(1) Replaced single-cell SUM(Bx:Bx) formulas on 'Summary' with direct subtraction (=B5-B6) and unified 'Shortlists' "
        "row-index MATCH formulas so all rows share identical formula patterns. "
        "(2) Added worksheet-level OpenXML <ignoredErrors> rules across all 8 tabs to suppress false-positive Excel green triangles.",
    ],
    "6.3": [
        "Company-by-Company Munger Gate Review, Strict AI Disruption Test & Bottom-Up Implied Growth: "
        "(1) Full bottom-up audit of all 426 companies across US, Europe, and Canada against the 6 Munger Quality Gates. "
        "(2) Strict Gate 3 AI Disruption rule applied: routine info lookup/research (WKL.NL, RELX, TRI, FDS) and vulnerable seat software "
        "capped at CAP <= 10 (Rejected) where LLM/AI agents credibly substitute the core offering. "
        "(3) Bottom-up 5–10Y cycle Implied Owner EPS Growth (g_implied) populated from fundamental drivers (pricing + unit growth + reinvestment). "
        "(4) Quantitative data sanitization: fixed IBKR Class A peak Owner EPS (eliminating non-controlling interest spike), normalized customer "
        "float cash conversion (WISE.GB, ADYEN.NL), corrected serial acquirer D&A distortion (CSU.CA, TYL), replaced placeholder ROIC caps, "
        "and normalized tech ramp-up denominator-inflated PAR multiples (>55x).",
    ],
    "6.4": [
        "Gate 6 Qualitative Re-Framing (Real Cash Conversion, Hurdle ROIC & Anti-Fragile Balance Sheet): "
        "(1) Re-anchored Gate 6 to Charlie Munger's qualitative triad: real cash conversion (no maintenance capex/working capital traps), "
        "incremental capital reinvestment at or above hurdle rates (>=12%, avoiding profitless growth), and anti-fragile balance sheets "
        "(rejecting debt-funded buybacks at peak multiples, serial M&A rollups, and fragile leverage). "
        "(2) Rescued non-fragile fortress compounders previously caught in mechanical tripwires: Munich Re (MUV2.DE, 280%+ Solvency II, "
        "50-year unbroken dividend record), Hannover Re (HNR1.DE), Otis Worldwide (OTIS, 42% ROIC, 102% FCF conversion, organic deleveraging), "
        "Canadian National Railway (CNR.CA, 100% FCF conversion, 14.5% ROIC, essential 3-coast rail monopoly), Union Pacific (UNP), "
        "GTT (GTT.FR, 75% ROIC, net cash), Admiral (ADM.GB), and Sampo (SAMPO.FI). "
        "(3) Strictly maintained rejection on financial engineers (MSCI, MCD), debt-fueled serial rollups (AJG, BRO, INF.GB), "
        "heavy concession project debt (FER.ES, DG.FR, FGR.FR), and private-equity debt structures (TDG).",
    ],
    "6.5": [
        "Sovereign-Grade & Contractual Infrastructure Audit (Vinci, Eiffage, Vopak, Waste Management, Siemens Healthineers): "
        "(1) Admitted non-displaceable, contractually formula-indexed physical infrastructure and essential healthcare utilities to Gate 6 pass status: "
        "Vinci (DG.FR, 14.8% ROIC, 149% FCF conversion, 6.3x interest coverage, 4.5% cash dividend yield), "
        "Eiffage (FGR.FR, 13.4% ROIC, 238% FCF conversion, 6.4x interest coverage, 8.7% cash dividend yield), "
        "Vopak (VPK.NL, 12.0% ROIC, 173% FCF conversion, 6.6x coverage, deep-water port terminal monopoly), "
        "Siemens Healthineers (SHL.DE, 13.2% ROIC, 97% FCF conversion, 8.1x coverage, hospital MRI/oncology utility), and "
        "Waste Management (WM, 12.3% ROIC, 112% FCF conversion, unreplicable permitted landfill network). "
        "(2) These businesses demonstrate real cash conversion, earn returns above the 12% hurdle, and their debt is non-displaceable and anti-fragile, "
        "backed by essential national services and contractual inflation indexation. "
        "(3) Maintained strict rejection on financial engineers (MSCI, MCD), debt rollups (AJG, BRO), and sub-hurdle concessions (FER.ES).",
    ],
    "6.6": [
        "Gate 6 Definition & Rubric Clarification (Anti-Fragile Infrastructure & Float vs. Financial Engineering): "
        "(1) Clarified the Gate 6 definition and rejection rubric across Methodology, Read Me, and Qualitative tooltips to explicitly "
        "document the anti-fragile nature of essential physical infrastructure (contractual inflation indexation, >5x interest coverage) "
        "and fortress float institutions (Solvency II >200%, multi-decade unbroken dividend records). "
        "(2) Explicitly codified the fatal fragility traps: financial engineering (debt-funded buybacks at peak multiples), serial M&A rollups, "
        "and sub-12% reinvestment returns.",
    ],
    "6.7": [
        "5-Year Expected Cycle IRR Metric (Pull-to-PAR): "
        "(1) Added '5Y Expected IRR (Pull-to-PAR)' across Quantitative, Shortlists (Tables 1 & 2), and Python reference gates. "
        "(2) Formula: (1 + g_imp) * (PAR Value / Price)^(1/5) + DY - 1, capturing both the ongoing business coupon and the "
        "annualized multiple expansion return from buying Below PAR.",
    ],
    "6.8": [
        "Gate 6 Evolution: Peak-to-Peak Cycle Compounding & Fortress Balance Sheet: "
        "(1) Explicitly codified the Peak-to-Peak Business Cycle EPS Test as a fundamental prerequisite for the PAR Valuation "
        "methodology: companies must achieve a new high in Owner EPS at the peak of each succeeding business cycle, with clear indications "
        "of reaching new earnings highs in future cycles (while intra-cycle dips remain normal). "
        "(2) Replaced the ambiguous 'anti-fragile' terminology with concrete Fortress & Self-Funding Balance Sheet standards: "
        "net debt repayable from normal owner earnings in <= 4 years (or net cash), interest coverage > 5–10x through the cycle, contractual inflation indexation "
        "for infrastructure (>5x coverage), Solvency II > 200% for float institutions, and an explicit ban on financial engineering (debt-funded "
        "buybacks at peak multiples creating negative equity) and serial M&A debt rollups.",
    ],
    "6.9": [
        "Intelligent Waterfall Architecture & Sequential Funnel Cleanup: "
        "(1) Visual Waterfall on Qualitative sheet: downstream gate cells automatically gray out and bypass once a company fails an earlier gate, "
        "eliminating noise and preventing premature evaluation. "
        "(2) Dedicated 'Review Stage / Action' filter column on Qualitative: provides a one-click AutoFilter view ('Stage 6: G6 Candidate', "
        "'Quality Pass (Funnel)', or 'Rejected @ G<x>') to focus immediately on active review queues. "
        "(3) Cleaned 4,392 phantom downstream entries in inputs.csv across US, Europe, and Canada where companies had been scored on later gates "
        "despite failing early gates (preserving all qualitative notes and evidence while maintaining 100% funnel consistency).",
    ],
    "6.10": [
        "SEC tag fixes: dividends read from PaymentsOfOrdinaryDividends (JNJ, ZTS, CL, CRH, HWM showed 0% yield); D&A adds "
        "separately tagged intangible amortisation (AVGO, ADI, ABT, PH were understated).",
    ],
    "6.11": [
        "Computed PAR inputs (screener/fetch/par.py): Last Peak Owner EPS (best of 5 fiscal years), cycle low/high multiples "
        "(min/max of yearly medians of monthly price ÷ peak Owner EPS known at the time), peak-to-peak g and a 'New peak vs prior "
        "cycle' flag now come from code instead of hand entry; one-off non-cash earnings spikes are left out; split restatement "
        "and minority-interest EPS fixed; analyst overrides only in 'My Peak EPS' / 'My growth g' with a note "
        "(SAF.FR, ULVR.GB, RR..GB, MUV2.DE, QIA.DE, BIM.FR, EXPD). fetch_market_data.py --offline recomputes from the cache; "
        "diff report output/par_recompute_report.csv; dual listings mirror the primary line (ASML, FER).",
        "Median ROIC = 5-year median from code; negative-invested-capital years left out (no 100% placeholders); hand-typed "
        "ROIC values removed.",
        "Gate 2 uses only your markets; the sub-industry defaults moved to Gate 6 (N for regulated utilities and deposit banks). "
        "Asset managers scored per company (blanket 'non-essential' override removed); custody banks NTRS/STT Gate 6 N; KKR Gate 1 N "
        "(consistent with APO).",
        "Gate 6 rule check (Quantitative, flags only): net debt > g6_netdebt_yrs, interest cover < g6_intcov, no new peak. Flagged "
        "passes re-scored with notes: WM and OTIS → N (same basis as RSG / MSCI); rails, MUV2, cyclical dips, BNZL, CSU, X.CA stay Y "
        "with the reason.",
        "Gate 3 AI-disruption rule written into the definition and applied consistently: RELX, Wolters Kluwer, LSEG, CoStar CAP 10 → 15.",
        "A blank gate input never passes: the company stops as 'To review (blank gate)'. Downstream entries after the first failed "
        "gate cleared consistently (incl. market-table rejections). Health-note labels follow the parameters; unused a_roic removed.",
    ],
    "6.12": [
        "Live fetch for the v6.11 funnel (BLK, BX, CVC, EQT, PGHN, VZN, BAM now with data; Eiffage / Blackstone dividends from "
        "dividends per share). 'My Peak EPS' now also caps each year's Owner EPS for the cycle multiples, so excluded windfall / "
        "one-off years no longer depress them (EXPD, QIA, BIM, ULVR, RR, MUV2). BAM.CA Gate 6 'no new peak' noted as a "
        "pre-spin-off data artefact; SAF.FR PAR flagged unreliable (IFRS hedge-mark losses).",
    ],
    "6.13": [
        "Gate 6 surplus-cash rule: cash and T-bills held as dry powder count toward the fortress balance sheet, never against the "
        "hurdle ROIC; incremental ROIC is judged on deployed operating capital, float-funded holding companies on per-share book "
        "value / look-through operating earnings (GAAP mark-to-market gains excluded). BRK.B Gate 6 N → Y (computed median ROIC "
        "16.7%, net cash at the parent, new peak vs prior cycle; the prior N penalised its cash pile).",
    ],
    "6.14": [
        "Gate 6 Qualitative Re-Framing (Peace of Mind vs. Kindness of Strangers & 4 Compounding Pillars): "
        "(1) Replaced mechanical accounting cut-offs (such as blanket bans on negative book equity from share repurchases or "
        "spin-off debt) with Charlie Munger's qualitative triad and Warren Buffett's solvency standard across 4 pillars: "
        "(a) Peak-to-Peak secular compounding, (b) Real Cash Conversion (FCF >= 80% NI), (c) High incremental ROIC (>= 12%), and "
        "(d) Peace-of-Mind Balance Sheet: structured to survive a multi-year economic shock or closed credit market without permanently "
        "impairing equity, where all leverage strictly amplifies a high-ROIC engine rather than relying on the 'kindness of strangers'. "
        "(2) Rescued high-conviction compounders previously caught by mechanical accounting tripwires: "
        "Otis Worldwide (OTIS, 42% ROIC, 102% FCF conversion, 12x coverage, non-discretionary maintenance), "
        "MSCI (MSCI, 40%+ ROIC, ~100% FCF conversion, 95% subscription renewal toll booth with self-funding buyback leverage), "
        "Synopsys (SNPS, EDA software duopoly with Cadence, Ansys bridge debt rapidly amortized from $2.5B+ cash flow), "
        "Waste Management (WM, 12.3% ROIC, 112% FCF conversion, irreplaceable landfill monopoly with municipal cash generation), and "
        "Fairfax Financial (FFH.CA, Canada's mini-Berkshire aligned with BRK.B under the float institution standard).",
    ],
    "6.15": [
        "Gate 3 Secular Resilience & 5-Macrotrend Evolution: "
        "(1) Replaced the narrow single-factor 'Strict AI Disruption Rule' with a comprehensive 5-Macrotrend Secular Resilience Test "
        "evaluating Competitive Advantage Period (CAP >= 15 yrs) across: "
        "(a) Automation & Cognitive Tech (AI, software, robotics), "
        "(b) Demographic Aging & Structural Labor Scarcity, "
        "(c) Geopolitical Realignment & Supply Chain Reshoring, "
        "(d) Energy Transition, Electrification & Resource Limits, and "
        "(e) Structural Inflation, Fiscal Deficits & Cost of Capital. "
        "(2) Codified the Rule of Secular Resilience: CAP >= 15 requires the core moat to be an active beneficiary of, or structurally "
        "insulated from (indifferent to), all 5 macrotrends; an active terminal headwind on any single pillar caps CAP <= 10 (REJECT).",
    ],
    "6.16": [
        "Batch 1 Gate 6 Consistency Audit & Re-Scores: "
        "(1) Rescored solid waste / landfill monopolies: Republic Services (RSG) and Waste Connections (WCN.CA) aligned with WM. "
        "(2) Rescored middle-market P&C insurance brokers: Arthur J. Gallagher (AJG) and Brown & Brown (BRO) aligned with AON. "
        "(3) Rescored life sciences tools scale leaders: Danaher (DHR, >30% tangible ROIC, FDA bioprocess lock-in) and Thermo Fisher (TMO). "
        "(4) Rescored digital savings and wealth compounders: Avanza (AZA.SE), FinecoBank (FBK.IT), and Nordnet (SAVE.SE) recognized as "
        "capital-light fintech platforms with zero commercial credit risk (distinguished from fractional-reserve commercial banks). "
        "(5) Rescored global franchise royalty machine: McDonald's (MCD, 30%+ ROIC, prime real estate, self-funding cash generation).",
    ],
    "6.17": [
        "Batch 2 Gate 3 Evaluation — Alphabet (GOOGL): "
        "(1) Upgraded Alphabet (GOOGL) to CAP 20 (Quality Pass) under the 5-Macrotrend Secular Resilience standard: "
        "recognized as a full-stack vertically integrated AI hegemon with 3B+ Android/Chrome distribution moat, YouTube UGC monopoly, "
        "profitable Google Cloud (+30% growth), custom TPU infrastructure, and $80B+ net cash balance sheet. "
        "(2) Confirmed Gate 3 rejections (CAP <= 10) for seat-based SaaS (CRM, WDAY), discretionary workstations (FDS, TRI), "
        "billable-hours IT services (ACN, CTSH, CAP.FR), and creative tools (ADBE) under Macrotrend #1.",
    ],
    "6.18": [
        "3-Pillar Fundamental PAR Multiple & Cycle High Guardrail: "
        "(1) Replaced the rigid market-multiple approach with Charlie Munger & Warren Buffett's 3-Pillar Fundamental PAR Multiple: "
        "Raw PAR Multiple = (2 * (g_imp * 100) + 5Y Cycle Midpoint Multiple + min(ROIC * 100, par_roic_cap)) / 3. "
        "(2) 5Y Cycle High Guardrail: Enforced PAR Multiple = min(Raw PAR Multiple, mult_high_5y). Codifies the core value investing rule "
        "that a stock's through-the-cycle fair value can never exceed the highest multiple the market was willing to pay at the peak of the cycle. "
        "Protects balance-sheet financials and reinsurers (MUV2.DE capped at 11.4x, moving to Above PAR; III.GB clamped to 7.9x; BAM.CA to 11.3x) "
        "from being inflated into fantasy multiples while leaving pure operating compounders (OTIS, ZTS, MSFT, CPRT) completely untouched. "
        "(3) Secular Growth Factor (Benjamin Graham / Peter Lynch): Integrates 2 * (g_imp * 100) directly into the multiple (+16 to +24 turns for "
        "8%-12% compounders), aligning valuation with intrinsic earnings compounding. "
        "(4) Operating ROIC Normalization (Neutralizing Buyback Distortions): Set par_roic_cap = 35.0 as the empirical proxy for uncorrupted "
        "operating-side ROIC (NOPAT / Operating Invested Capital, which yields 32.7% for OTIS, 35.7% for AZO, 35.2% for AAPL, and 30.1% for MCK), "
        "neutralizing negative-equity denominator collapses from share repurchases or spin-off debt without penalizing true operating quality. "
        "(5) Anti-Bubble Deflation: Deflated bubble multiples from the ZIRP era (SNPS PAR deflated from 54.9x to 34.0x; WM PAR deflated from "
        "34.3x to 20.8x, properly warning against paying peak multiples for asset-heavy 12% ROIC). "
        "(6) Normalized Berkshire Hathaway (BRK.B) Class A vs. Class B share basis in data/us/financials.csv (peak operating EPS ~31.29, "
        "cycle multiples 16-22x), resolving share-count distortion.",
    ],
    "6.19": [
        "Gate 2 Evolution: Essential Needs & Entrenched Everyday Habits ('Likely To' Standard): "
        "(1) Expanded Gate 2 beyond bare biological survival ('water and bread') to Charlie Munger and Warren Buffett's "
        "enduring consumer habit principle ('likely to' spend): admitting resilient, high-frequency daily rituals, cultural "
        "staples, low-cost household entertainment, and Lindy-luxury compounders (e.g. PEP, MDLZ, HSY, MNST, SBUX, CMG, DPZ, "
        "YUM, QSR, NFLX, NKE, ITX, RMS, MC, CFR, BEI, HEIA, DGE, LISP, LOTB). "
        "(2) Maintained strict rejection on discretionary big-ticket/deferrable cyclicals (cruises, airlines, homebuilders), "
        "speculative commodity miners (gold), non-Western/pariah revenue concentrations, and predatory/addictive harm (tobacco, CFD trading). "
        "(3) Rescued high-quality consumer compounders to be rigorously tested by downstream Gates 3–6 (moat, pricing power, "
        "macro resilience, and real cash conversion).",
    ],
    "6.20": [
        "Gate 3 Base-Rate & Haircut Engine (Mauboussin & Callahan 1970–2024 Persistence) & Market-Implied CAP: "
        "(1) Formalized Gate 3 as a two-step Outside View -> Inside View evaluation: Anchored default baseline CAP in Michael "
        "Mauboussin and Dan Callahan's 54-year empirical industry persistence data (Ex. 25: Tier 1 Staples 20-30Y, Tier 2 MedTech/Hardware 15-20Y, "
        "Tier 3 Software/Capital Goods 10-15Y, Tier 4 Utilities/Energy 5-10Y), and applied deductive haircuts (-5 to -10 years) for active "
        "headwinds across the 5 Macrotrends (AI disruption of seat SaaS/consulting, labor scarcity, supply chain realignment, energy bottlenecks, inflation). "
        "(2) Codified Incremental Return on Invested Capital (ROIIC >= 12%) into the Proof-of-Moat test, ensuring capital compounding is not profitless growth. "
        "(3) Added Market-Implied CAP and Moat Runway Margin to Quantitative sheet, revealing the exact number of years of excess return "
        "the market price implies relative to our fundamental CAP.",
    ],
    "6.21": [
        "Gate 3 & Gate 4 Architectural Reordering (Moat Existence Precedes Moat Duration) & Look-Through Holdcos: "
        "(1) Reordered Gates 3 and 4 into their proper logical hierarchy: Gate 3 now diagnoses Moat Existence, Proof of Moat "
        "(5Y median ROIC >= 12% & incremental ROIIC >= 12%), and Pricing Power >= Inflation (3a Moat Archetype, 3b Pricing Gate, 3m Moat Note). "
        "Gate 4 now evaluates Moat Duration / Runway (4 Runway CAP >= 15 Years) using the Mauboussin Base-Rate & 5-Macrotrend Haircut Engine. "
        "Commodity price takers fail cleanly at Gate 3b, while businesses with moats today but facing terminal AI disruption fail at Gate 4. "
        "(2) Holding Company Look-Through Moat Standard: Holding companies (such as Lundbergsföretagen LUND.B and Industrivärden INDU.C) "
        "are evaluated on the basis of their look-through portfolio moats and pricing power, unlocking fortress Nordic owner-operators. "
        "(3) Gate 6 Refinement (3-Pillar Cash Reality & Fortress Architecture): Streamlined Gate 6 by removing the redundant hurdle rate clause "
        "(already verified at Gate 3b on ROIC & ROIIC >= 12%), focusing Gate 6 strictly on its distinct triad: peak-to-peak secular EPS compounding "
        "across cycles, clean FCF conversion (>=80%), and a peace-of-mind balance sheet free from the kindness of strangers.",
    ],
    "6.22": [
        "Mauboussin Growth Engine (Base-Rate Regression & Market-Implied Growth): "
        "(1) Grounded forward implied growth (g_imp) in Michael Mauboussin and Dan Callahan's 75-year empirical growth research "
        "(Counterpoint Global, April 2026): Enforced par_g_cap = 12.0% as the empirical ceiling for through-the-cycle large-cap EPS growth, "
        "and replaced raw historical CAGR extrapolation with Mauboussin's autoregressive fade formula: "
        "Expected g = 0.15 * (Hist g - 7.0%) + 7.0%, anchoring growth to the 7.0% mature base rate. "
        "(2) Market-Implied Growth (g_market) & Growth Margin: Inverted the 3-Pillar Fundamental PAR formula on the Quantitative and "
        "Shortlists sheets to display the exact annual growth rate priced into the current market multiple (g_market) alongside the "
        "Growth Margin of Safety (g_imp - g_market), paired symmetrically with Market-Implied CAP and Moat Runway Margin.",
    ],
    "6.23": [
        "Operating ROIC Normalization (Uncorrupted Operating Capital & M&A Goodwill Neutralization): "
        "(1) Switched the 3-Pillar Fundamental PAR Multiple and Market-Implied Growth formulas from reported GAAP ROIC "
        "to uncorrupted Operating ROIC (Tangible Capital Return). "
        "(2) M&A Goodwill Neutralization: Replaced accounting-distorted GAAP ROIC (NOPAT / Total Invested Capital including goodwill) "
        "with uncorrupted Operating ROIC (NOPAT / Tangible Invested Capital = Equity + Debt - Cash - Goodwill - Intangibles). "
        "Eliminates the artificial valuation penalty on capital-light toll booths that completed strategic mega-mergers "
        "(e.g., S&P Global's 2022 IHS Markit acquisition added $52.8B in goodwill/intangibles, depressing GAAP ROIC to 11.8% and "
        "collapsing its PAR multiple to 19.9x; Operating ROIC normalizes SPGI to 35.0% and a proper 27.6x PAR multiple). "
        "(3) Negative Tangible Capital Standard: Codified the principle that asset-free compounders operating on negative net "
        "tangible capital (from deferred subscription revenues and upfront payments) earn structurally unbounded returns on tangible "
        "capital, automatically aligning with par_roic_cap = 35.0%. True asset-heavy businesses (WM, UNP, CAT) retain their low "
        "operating multiples. "
        "(4) Added 'Operating ROIC 5Y (Tangible)' and 'My ROIC (override)' to the Quantitative sheet alongside GAAP ROIC, giving "
        "investors full transparency into both the ongoing operating engine and retrospective total capital deployment.",
    ],
    "6.25": [
        "Conditional Calamity Pass Tier (Buffett Temporary Fixable Calamities on Gates 3b, 5 & 6): "
        "(1) Introduced explicit `calamity` ('Y'/blank) and `calamity_note` fields so temporary, fixable business or balance-sheet "
        "calamities failing Gate 3b (trailing ROIC/pricing dip with intact 3a moat), Gate 5 (outgoing/remediating management blunder), "
        "or Gate 6 (temporary M&A bridge debt, capex spike, or one-off cash outflow) can enter Quantitative PAR valuation as "
        "'Calamity pass' without falsifying raw gate scores or contaminating the pristine 'Quality pass' funnel. "
        "(2) Anchor Gates 1 (Understandability), 2 (Essential Need), 3a (Moat != None), and 4 (CAP >= 15Y secular runway) remain "
        "strictly non-waivable; when `calamity = 'Y'`, downstream gates (4, 5, 6) remain active so hidden second flaws or secular "
        "disruption still reject cleanly. "
        "(3) Surfaced separately in the HTML cockpit ('⚠️ Calamity Watchlist' tab, amber badges, off-by-default Shortlist toggle, "
        "and dossier kill-switch callout).",
    ],
    "6.26": [
        "Gate 4 CAP-Linked Growth Engine & Expected Growth Renaming (g_exp): "
        "(1) Linked Mauboussin autoregressive growth persistence (lambda) directly to Gate 4 CAP: "
        "CAP >= 30 (fortress monopolies, e.g. SPGI, MCO, MSFT, V) uses lambda = 0.25 (slower fade, higher weighting of historical compounding); "
        "CAP >= 20 (standard quality compounders) uses lambda = 0.15 (empirical 75-year autoregressive baseline); "
        "CAP >= 15 (shorter runway / higher transition risk) uses lambda = 0.10 (faster fade towards 7.0% base rate). "
        "(2) Renamed 'Forward Implied g' (g_imp) to 'Expected Growth' (g_exp) across documentation, specs, and dashboard UI, "
        "eliminating terminology collision with Market-Implied Growth (g_market) while maintaining backwards compatibility.",
    ],
}
