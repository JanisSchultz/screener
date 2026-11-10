"""Framework configuration (v3): the 5-Phase MECE Stock Evaluation Framework.

Pre-Screen (circle of competence) -> Phase 1 WHY -> Phase 2 WHAT -> Phase 3 HOW   [qualitative, all companies]
-> Phase 4 PROOF & ENTRY (audit, valuation, Stage 2) -> Phase 5 LIFECYCLE           [quantitative, funnel only]

Edit this file to change the framework, then run `python3 build.py`. Parameter values are the defaults written
into each workbook's Methodology sheet (universe.json "parameters" can override them per universe).
The v2 framework is archived in screener/v2/.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Qualitative fields (Inputs sheet). Order = column order.
#   type "score": 0/1/2 with rubric; "category": one of options; "number": numeric; "text": free text
#   legacy: v2 criterion code the value is carried over from (None = new in v3, pre-scored by Claude)
#   power: True for the 3.2 sub-types that feed "3.2 Strongest Power" through MAX()
# ---------------------------------------------------------------------------
def S(code, phase, section, short, name, legacy, definition, r0, r1, r2, power=False):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="score", legacy=legacy,
                definition=definition, rubric={0: r0, 1: r1, 2: r2}, power=power)


def CAT(code, phase, section, short, name, options, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="category", legacy=None,
                definition=definition, options=options)


def NUM(code, phase, section, short, name, options, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="number", legacy=None,
                definition=definition, options=options)


def TXT(code, phase, section, short, name, legacy, definition):
    return dict(code=code, phase=phase, section=section, short=short, name=name, type="text", legacy=legacy,
                definition=definition)


FIELDS = [
    # ------------------------------------------------------------- PHASE 1: THE WHY
    S("1.1a", 1, "1.1 Drucker's Purpose & Dual-Customer Mapping", "Outside-In Purpose", "Outside-In Orientation", None,
      "The business exists to create and serve a customer starting from their daily reality; profit is a test of validity, not the primary goal.",
      "Inside-out: exists mainly for financial engineering, rent extraction, a captive/forced customer, or the product is secondary to the deal.",
      "Real customer purpose but mixed — product-, capacity- or Wall-Street-driven; customer focus inconsistent.",
      "Clearly built around a specific customer problem; decisions start from the customer's daily reality."),
    S("1.1b", 1, "1.1 Drucker's Purpose & Dual-Customer Mapping", "Dual-Customer Map", "Who & Where Is the Customer", None,
      "Every decision-maker in the chain — ultimate end-user and intermediate gatekeepers (contractors, surgeons, grocers, platforms) — is served; losing either blocks the sale.",
      "Wins one side but the other is hostile, conflicted or able to block/disintermediate the sale.",
      "Strong with one side, merely tolerated by the other (or gatekeeper position fragile).",
      "Preferred by both end-user and every gatekeeper (or the chain has no independent gatekeeper)."),
    S("1.2", 1, "1.2 Functional Utility & Compelling Value", "Compelling Value", "Compelling Value Origination", None,
      "Strength of the utility: mission-critical risk reduction, search-cost/friction reduction, customer cost reduction, or identity/status. Timeless status assets with strict supply control count; fashion fads do not.",
      "Weak or replicable utility; commodity, fad-driven identity, or value mostly in marketing.",
      "Genuine but moderate utility, or strong utility that is easily matched by alternatives.",
      "Compelling, hard-to-replace utility of a clear type (mission-critical, trusted consistency, cost saving, or timeless status with supply control)."),
    CAT("1.2t", 1, "1.2 Functional Utility & Compelling Value", "Value Type", "Primary Compelling-Value Type",
        ["Risk reduction", "Search-cost reduction", "Cost reduction", "Identity & status", "Other"],
        "Dominant source of compelling value (one choice)."),
    CAT("1.2i", 1, "1.2 Functional Utility & Compelling Value", "Invention Path", "Invention Path (Strategy Dynamics)",
        ["Customer-led", "Capabilities-led", "Competitor-led"],
        "How compelling value is created: customer-led (known unmet need), capabilities-led (unknown need, high uncertainty), competitor-led (follows rivals)."),
    S("1.3", 1, "1.3 Agency & Tail-Risk Screen", "Voluntary Test", "Voluntary Goodwill vs Compulsive/Predatory Trap", None,
      "Customers buy willingly because the product improves their life or operations. Demand driven by physiological addiction or predatory mechanics creates regulatory tail-risk, sin taxes and permanent multiple compression. 0 = knock-out.",
      "Compulsive or predatory demand (tobacco/nicotine, gambling, predatory lending, addictive mechanics as the core model).",
      "Mostly voluntary but with habit-forming or contested elements (alcohol, sugary products, ad-driven attention, aggressive fee models).",
      "Clearly voluntary goodwill; customers would choose it again with full information."),
    S("1.4", 1, "1.4 Organic Deprivation Test", "Deprivation", "Organic Deprivation Test", None,
      "Immediate physical, operational or psychological pain if the product disappeared tomorrow, assuming zero contractual or data lock-in.",
      "Little pain — easily substituted or simply forgone.",
      "Noticeable inconvenience or cost, resolved within months by alternatives.",
      "Severe immediate pain (operations stop, health/safety at risk, daily life disrupted)."),
    # ------------------------------------------------------------- PHASE 2: THE WHAT
    S("2.1a", 2, "2.1 Consumption Profile (2x2 Demand Matrix)", "Essentiality", "Essentiality", "P1.2",
      "Non-discretionary with a high cost of failure or absence; industry unit volume holds flat or grows in recessions.",
      "Discretionary; volume falls sharply or is deferred in downturns.",
      "Partly discretionary; moderate cyclical deferral.",
      "Non-discretionary; volume holds or grows through recessions."),
    S("2.1b", 2, "2.1 Consumption Profile (2x2 Demand Matrix)", "Repeat Frequency", "Repeat Frequency", "P1.3",
      "Consumption is continuous via fast wear-out, daily/monthly replenishment, or ongoing subscriptions — not inflated by mandates, fads or short hardware cycles.",
      "One-off or long-cycle purchase (durables that lengthen their own replacement cycle, projects).",
      "Periodic / multi-year cycle or mixed recurring share.",
      "Daily/monthly consumption, replenishment or mandatory recurring subscription."),
    S("2.2a", 2, "2.2 Secular Volume Drivers & Gatekeeper Test", "Secular Tailwinds", "Structural Volume Tailwinds", "P1.4",
      "Industry unit volume stable or growing over 5–10 years, driven by demographics, technology adoption or regulatory mandates.",
      "Structurally shrinking volume.",
      "Flat / GDP-like volume, or tailwinds offset by headwinds.",
      "Clear multi-year structural volume growth."),
    S("2.2b", 2, "2.2 Secular Volume Drivers & Gatekeeper Test", "Must-Carry", "The \"Must-Carry\" Gatekeeper Test", None,
      "Would a retailer, distributor or platform lose customers if it failed to carry this specific brand/product?",
      "No — easily delisted or replaced by a private label / rival.",
      "Partly — carried for breadth; delisting causes some complaints but little churn.",
      "Yes — gatekeepers must carry it or lose customers (or the company sells direct with no gatekeeper able to block it)."),
    S("2.2c", 2, "2.2 Secular Volume Drivers & Gatekeeper Test", "Reinvestment Runway", "Organic Reinvestment Runway", None,
      "Capacity to grow unit volume across new geographies or adjacent segments without costly low-hit-rate line extensions.",
      "Saturated; growth needs acquisitions or low-hit-rate extensions.",
      "Some runway (a few geographies/segments) or runway with execution risk.",
      "Long organic runway in new geographies/adjacencies at attractive returns."),
    S("2.3a", 2, "2.3 Standalone Pricing Power", "Benefit-Cost Asymmetry", "Benefit-to-Cost Asymmetry", None,
      "The product is a tiny fraction of the buyer's budget while delivering disproportionate operational or emotional value.",
      "Large budget line that buyers actively shop and negotiate.",
      "Moderate share of budget or value not clearly disproportionate.",
      "Small share of buyer's budget with outsized value (cost of failure ≫ price)."),
    S("2.3b", 2, "2.3 Standalone Pricing Power", "Real Price Pass-Through", "Real Inflation Pass-Through", "P5.2",
      "Demonstrated ability to raise prices above inflation without losing unit volume (or intentional scale-economies-shared price give-back that compounds volume).",
      "Price taker; discounts or loses volume when raising prices.",
      "Passes through inflation but little real pricing.",
      "Consistent real price increases without volume loss, or deliberate price give-back that widens the moat."),
    # ------------------------------------------------------------- PHASE 3: THE HOW
    S("3.1a", 3, "3.1 Industry Structure & Two Paths to ROIC", "Rational Structure", "Five Forces & Rational Structure", "P4.1",
      "Natural monopoly, toll bridge or rational duopoly/oligopoly competing on reliability and quality; #1/#2 with stable share. Avoid profitless-growth industries.",
      "Fragmented or price-competitive structure, or weak share position.",
      "Oligopoly with periodic price competition, or #3+ in a rational market.",
      "Monopoly / toll bridge / rational duopoly; company #1 or #2 with stable share."),
    S("3.1b", 3, "3.1 Industry Structure & Two Paths to ROIC", "Low Buyer Power", "Buyer Power (2 = low)", "P2.2",
      "Sales spread across a broad, unorganized customer base with low bargaining power rather than a few giant buyers.",
      "Concentrated, powerful buyers dictate terms.",
      "Some large customers but no single buyer controls economics.",
      "Fragmented buyers with little bargaining power."),
    S("3.1c", 3, "3.1 Industry Structure & Two Paths to ROIC", "Low Supplier/Labor Power", "Supplier & Labor Power (2 = low)", "P2.4",
      "No reliance on concentrated suppliers, unionized labor or star talent that can extract the profit pool.",
      "Dominant supplier, union or star talent captures much of the profit pool.",
      "Some dependence, but contained.",
      "Independent of concentrated suppliers and labor."),
    CAT("3.1p", 3, "3.1 Industry Structure & Two Paths to ROIC", "ROIC Path", "DuPont ROIC Path (Margin vs Velocity)",
        ["Margin", "Velocity", "Both", "Neither"],
        "Whether high ROIC comes from high operating margins (pricing power) or high asset velocity (Total Asset Turnover = Sales / Assets > 1.0)."),
    S("3.2a", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Switching Costs", "Switching Costs (Lock-In)", "P4.2",
      "Financial, procedural (retraining risk) or relational friction incurred after purchase.",
      "None.", "Moderate lock-in.", "Strong lock-in (system of record, implanted/installed base, retraining risk).", power=True),
    S("3.2b", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Scale Economies", "Scale Economies & Scale Economies Shared", "P4.3b",
      "Fixed-cost spreading or purchasing leverage; in Scale Economies Shared (e.g. Costco) savings are passed back to buyers to build a volume moat.",
      "None.", "Some scale benefit, copyable.", "Structural scale / density advantage rivals cannot match.", power=True),
    S("3.2c", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Network Economies", "Network Economies & Fragmented Aggregators", "P4.3a",
      "Installed-base growth increases value for all users (e.g. Visa, exchanges), or aggregation of fragmented supply and demand.",
      "None.", "Weak or radial network.", "Strong multi-node network or aggregator.", power=True),
    S("3.2d", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Intangibles/Cornered", "Intangible Assets & Cornered Resources", "P4.3d",
      "Patents, regulatory licenses, trade secrets, scarce resources or brands that prevent replication or reduce uncertainty.",
      "None.", "Some protection, eroding or replicable.", "Durable, behaviour-changing intangible or cornered resource.", power=True),
    S("3.2e", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Efficient Scale", "Efficient Scale (Dorsey)", "P4.3c",
      "Niche market too small for a new entrant to earn its cost of capital.",
      "None.", "Partial.", "Clear efficient-scale niche.", power=True),
    S("3.2f", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Counter-Pos./Process", "Counter-Positioning & Process Power", None,
      "A superior business model incumbents refuse to mimic due to self-cannibalization, or opaque operational processes evolved over decades.",
      "None.", "Some model or process edge, imitable within a few years.",
      "Incumbents structurally cannot copy the model, or decades-evolved process advantage.", power=True),
    TXT("3.2bb", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Power: Benefit", "Primary Power — Benefit (cash-flow improvement)", "moat",
        "How the primary Power improves cash flow."),
    TXT("3.2br", 3, "3.2 Structural Competitive Advantage (7 Powers & Moats)", "Power: Barrier", "Primary Power — Barrier (what prevents arbitrage)", None,
        "What prevents competitors from arbitraging the benefit away."),
    S("3.3a", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Tech Disruption Resist.", "Technological Disruption Resistance", "P3.2",
      "Low risk over 20–30 years that a new technology supplants the category's underlying mechanism.",
      "High risk.", "Moderate risk.", "Low risk."),
    S("3.3b", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Counter-Position Resist.", "Counter-Positioning Resistance", "P3.3",
      "Low vulnerability to a challenger's superior, lower-cost model the incumbent cannot copy without cannibalizing profits.",
      "High vulnerability.", "Moderate.", "Low vulnerability."),
    S("3.3c", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Substitution Resist.", "Substitution & Disintermediation Resistance", "P3.4",
      "Few affordable cross-industry substitutes and low risk of disintermediation capping the price ceiling.",
      "Many substitutes / disintermediation under way.", "Some substitutes.", "Few substitutes; no credible disintermediation."),
    S("3.3d", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Regulatory/Patent Resist.", "Regulatory Intervention & Patent-Cliff Resistance", None,
      "Low risk of regulatory intervention (price controls, break-up, licence loss) or patent cliffs eroding the moat over two decades.",
      "Material regulatory or patent-cliff threat.", "Moderate exposure, manageable.", "Low exposure."),
    S("3.3e", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Brand Integrity", "Brand Tampering & Dilution Risk (2 = no dilution)", None,
      "Management is not cheapening the product formula (Schlitz) or chasing down-market volume that ruins exclusivity (Halston). Non-brand businesses: product/service quality integrity.",
      "Evidence of cheapening, over-extension or down-market dilution.", "Some risk or mixed record.", "Product/brand integrity actively protected."),
    S("3.3f", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Talent Magnetism", "Drucker's Talent Warning Sign", None,
      "The company and its industry still attract top-tier, ambitious talent (loss of talent appeal is the earliest sign of secular decline).",
      "Talent is leaving the company or the industry.", "Neutral / average employer.", "Magnet for top talent in its field."),
    NUM("3.3n", 3, "3.3 Hohn's Moat Duration & Erosion Stress-Test", "Qualitative CAP (yrs)", "Qualitative Competitive Advantage Period",
        [0, 5, 10, 15, 20, 30],
        "Years of moat visibility after the erosion stress-test (0/5/10/15/20/30). Compared with the market-implied CAP in Phase 4."),
    S("3.4a", 3, "3.4 Culture, Character & Capital Allocation", "Owner Leadership", "\"Divine Discontent\" vs \"The Locker Room Set\"", "P3.1",
      "Owner-oriented leaders driven by an internal compass to improve customer value rather than social proof or quarterly targets; evolve delivery without an innovation treadmill.",
      "Promotional, short-termist or value-destroying leadership.", "Competent but conventional.", "Owner-oriented, customer-obsessed, long-term."),
    S("3.4b", 3, "3.4 Culture, Character & Capital Allocation", "Planned Abandonment", "Drucker's Planned Abandonment", None,
      "Management systematically prunes dying legacy products and channels instead of defending yesterday.",
      "Defends declining legacy businesses with capital.", "Occasional pruning.", "Systematic, timely abandonment and portfolio renewal."),
    S("3.4c", 3, "3.4 Culture, Character & Capital Allocation", "Capital Allocation", "Capital Allocation Discipline", None,
      "Excess cash reinvested at high incremental ROIC or returned via dividends and undervalued buybacks — never empire-building M&A.",
      "Empire-building M&A, overpriced buybacks or chronic dilution.", "Average / mixed record.", "Disciplined, high-return reinvestment and sensible returns."),
]

FIELD_BY_CODE = {f["code"]: f for f in FIELDS}
SCORE_CODES = [f["code"] for f in FIELDS if f["type"] == "score"]
POWER_CODES = [f["code"] for f in FIELDS if f.get("power")]
SCORE_VALUES = (0, 1, 2)

# Scored items per phase (powers collapse into the derived "3.2" MAX and "3.2x" breadth)
PHASE_ITEMS = {
    1: ["1.1a", "1.1b", "1.2", "1.3", "1.4"],
    2: ["2.1a", "2.1b", "2.2a", "2.2b", "2.2c", "2.3a", "2.3b"],
    3: ["3.1a", "3.1b", "3.1c", "3.2", "3.2x", "3.3a", "3.3b", "3.3c", "3.3d", "3.3e", "3.3f", "3.4a", "3.4b", "3.4c"],
}
PHASE_MAX = {p: 2 * len(items) for p, items in PHASE_ITEMS.items()}
PHASE_NAMES = {0: "Pre-Screen: Circle of Competence", 1: "THE WHY", 2: "THE WHAT", 3: "THE HOW",
               4: "THE PROOF & ENTRY", 5: "THE LIFECYCLE"}
PHASE_LONG = {
    0: "Pre-Screen: Investor Circle of Competence (\"Meaning\")",
    1: "Phase 1: THE WHY (Customer Problem & Outside-In Utility)",
    2: "Phase 2: THE WHAT (Top-Line Demand Engine: Revenue = Volume × Price)",
    3: "Phase 3: THE HOW (Supply-Side Moat, Duration, Culture & Capital Allocation)",
    4: "Phase 4: THE PROOF & ENTRY (Financial Audit, Hohn / Bird-in-Hand Valuation & Stage 2)",
    5: "Phase 5: THE LIFECYCLE (Post-Purchase Hold Band & Objective Sell Triggers)",
}
DERIVED = {
    "3.2": ("Strongest Power", "MAX of the six Power sub-types (3.2a–3.2f); one strong Power is enough."),
    "3.2x": ("Power Breadth", "2 = two or more Powers scored 2; 1 = one Power scored 2 plus another scored 1; else 0."),
}

# ---------------------------------------------------------------------------
# Parameters -> Methodology input cells (Excel defined names). (name, label, default, fmt, note)
# ---------------------------------------------------------------------------
V2 = "Carried over from v2."
NEW = "New in v3; default set during the v3 rebuild — adjust to taste."
FW = "From the framework text."

PARAMETER_GROUPS = [
    ("Phase 1–3 gates", [
        ("thr_P1", "Phase 1 WHY: min subtotal (of 10)", 7, "0", NEW),
        ("thr_P2", "Phase 2 WHAT: min subtotal (of 14)", 10, "0", NEW),
        ("thr_P3", "Phase 3 HOW: min subtotal (of 28)", 20, "0", NEW),
        ("ko_voluntary", "Phase 1 knock-out: Voluntary Test (1.3) below this fails", 1, "0", FW + " (compulsive/predatory trap)."),
        ("ko_traps", "Phase 2 knock-out: Fad Trap / Long-Cycle Trap quadrant fails (1 = yes)", 1, "0", FW),
        ("quad_high", "2x2 matrix: score counted as 'High'", 2, "0", NEW),
        ("thr_power", "Phase 3: min Strongest Power (3.2)", 2, "0", "Same rule as v2 (one strong barrier is enough)."),
        ("thr_structure", "Phase 3: min Rational Structure (3.1a)", 1, "0", V2),
        ("thr_cap", "Phase 3: min Qualitative CAP (years)", 15, "0", NEW + " Framework asks for 20–30-yr visibility; 15 is the pass floor."),
        ("thr_capalloc", "Phase 3: min Capital Allocation (3.4c)", 1, "0", NEW),
        ("nm_phases", "Near-miss: min phases passed (of 3)", 2, "0", NEW),
        ("nm_score", "Near-miss: min quality score (of 100)", 75, "0.0", V2),
    ]),
    ("Quality score weights (score = Σ weight × phase% ÷ Σ weights × 100)", [
        ("w_P1", "Weight: Phase 1 WHY", 1 / 3, "0%", NEW),
        ("w_P2", "Weight: Phase 2 WHAT", 1 / 3, "0%", NEW),
        ("w_P3", "Weight: Phase 3 HOW", 1 / 3, "0%", NEW),
        ("conf_H", "Confidence multiplier: H", 1.00, "0.00", V2),
        ("conf_M", "Confidence multiplier: M", 0.95, "0.00", V2),
        ("conf_L", "Confidence multiplier: L", 0.85, "0.00", V2),
        ("rank_basis", "Rank by: 1 = quality score, 2 = confidence-adjusted score", 1, "0", V2),
        ("funnel_nearmiss", "Phase 4 funnel includes Near-miss (1 = yes, 0 = Quality pass only)", 0, "0", NEW),
    ]),
    ("Phase 4.1 Quantitative moat & accounting audit", [
        ("a_roic", "Median ROIC (5–10 yr) min", 0.15, "0.0%", FW + " (15%–20%)."),
        ("a_fcfconv", "True FCF / Net income (multi-year) min", 0.90, "0%", FW + " (90%–100%)."),
        ("a_cagr", "Big Five growth: CAGR min", 0.10, "0.0%", FW),
        ("a_cagr_count", "Big Five: min # of available CAGRs (of 12) meeting the bar", 8, "0", NEW),
        ("a_cagr_minavail", "Big Five: min # of CAGRs available to judge", 4, "0", NEW + " 4 = the four 3-yr CAGRs (Yahoo gives ~4 yrs for non-SEC filers)."),
        ("a_dollar", "Buffett $1 test: Δ market cap ÷ retained earnings min", 1.0, "0.00\"x\"", FW + " (ideally ≥ 1.5×)."),
        ("a_debt_yrs", "Long-term debt ÷ True FCF max (years)", 5, "0.0", FW + " (3–5 years)."),
        ("a_intcov", "Interest coverage (EBIT ÷ interest) min", 10, "0.0\"x\"", FW),
        ("a_roic_basis", "ROIC test basis: 1 = GAAP (incl. goodwill), 2 = tangible, 3 = either", 1, "0", NEW + " Framework: evaluate both; GAAP is the stricter default."),
        ("a_req", "Audit pass: tests passed ≥ MIN(a_req, tests with data)", 5, "0", NEW),
        ("a_min_tests", "Audit: min # of tests with data, else 'No data'", 4, "0", NEW),
    ]),
    ("Phase 4.2 Valuation gate (Bird-in-the-Hand v2 + Hohn CAP)", [
        ("v_r", "Discount rate / WACC (r)", 0.09, "0.0%", FW),
        ("v_gt", "Terminal growth (g_T)", 0.03, "0.0%", FW),
        ("v_gcap", "Growth cap for g fallback and valuation", 0.15, "0.0%", NEW),
        ("v_mult_cap", "Multiple ceiling cap (×) for steady-state firms", 25, "0.0", FW + " (~25×)."),
        ("v_bith", "Bird-in-the-Hand hurdle: Y_c + 0.5g >", 0.10, "0.0%", FW),
        ("v_yc_floor", "Minimum cash-yield floor Y_c", 0.025, "0.0%", FW),
        ("v_hohn", "Hohn napkin return: FCF yield + g_moat ≥", 0.09, "0.0%", FW),
        ("v_n_ratio", "Implied CAP n must be ≤ this share of Qualitative CAP", 0.67, "0%", NEW + " ('well below')."),
        ("v_dcf_years", "Hohn super-company DCF growth years (N)", 15, "0", FW + " (15–20 yrs)."),
        ("v_marr", "Town sticker price: minimum acceptable return", 0.15, "0.0%", "Phil Town Rule #1 convention."),
        ("v_pe_cap", "Town sticker price: future P/E cap", 40, "0", NEW),
        ("v_mos", "Margin of safety min (vs lower of the two intrinsic values)", 0.30, "0%", FW + " (30%–50%)."),
        ("v_funding", "Funding break-even rate", 0.07, "0.0%", FW),
        ("v_req_mos", "Valuation pass requires margin of safety (1 = yes)", 1, "0", NEW),
    ]),
    ("Phase 4.3 Technical entry (Weinstein Stage 2)", [
        ("t_slope", "30-wk MA slope (5-wk change) counted as rising/falling beyond ±", 0.01, "0.0%", NEW),
        ("t_near_high", "Within this % of 52-wk high = topping zone (Stage 3 when flat)", 0.10, "0%", NEW),
        ("t_vol", "Breakout volume: last week ÷ 10-wk average ≥", 1.5, "0.0", NEW),
        ("t_req_market", "Entry requires market in Stage 2 (1 = yes)", 1, "0", FW),
        ("t_req_sector", "Entry requires sector in Stage 2 where sector data exists (1 = yes)", 1, "0", FW),
        ("t_req_vol", "Entry requires breakout volume (1 = yes; 0 = informational)", 0, "0", NEW + " Weekly snapshot rarely coincides with the breakout week."),
    ]),
    ("Phase 5 Lifecycle (hold band & sell triggers)", [
        ("l_hold_lo", "Stretched hold band: Y_c + 0.5g lower bound", 0.08, "0.0%", FW),
        ("l_fcf_decay", "Trigger 1: True FCF conversion below", 0.80, "0%", FW),
        ("l_unadj", "Trigger 2: unadjusted return Y_c + 1.0g below", 0.08, "0.0%", FW),
        ("l_mult_max", "Trigger 2: conservative multiple M_c above (×)", 35, "0", FW + " (35×–40×)."),
        ("l_hyper_g", "Trigger 2: multiple trigger waived if g ≥ (hyper-growth)", 0.20, "0%", NEW),
        ("l_opp", "Trigger 3: superior opportunity if an equal-quality name offers Y_c + 0.5g >", 0.11, "0.0%", FW + " (11%–12%)."),
    ]),
]

# Results
RES_EXCL = "Excluded (pre-screen)"
RES_QPASS = "Quality pass"
RES_NEAR = "Near-miss"
RES_FAIL = "Fail"
Q_RESULTS = [RES_QPASS, RES_NEAR, RES_FAIL, RES_EXCL]

V_NOTFUNNEL = "Not in funnel"
V_NODATA = "No data"
V_AUDIT = "Audit fail"
V_VAL = "Watch – valuation"
V_TIME = "Watch – timing"
V_ENTRY = "Entry candidate"
V_RESULTS = [V_ENTRY, V_TIME, V_VAL, V_AUDIT, V_NODATA, V_NOTFUNNEL]

LIST_CAPACITY = {"top": 25, RES_QPASS: 250, RES_NEAR: 300, V_ENTRY: 100, V_TIME: 150, V_VAL: 250}
OVERRIDE_ROWS = 500
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
        "Phases 1–3 (qualitative) for every company: 12 v2 criteria carried over, 16 new fields pre-scored by Claude (see Confidence v3 / v3 note).",
        "Dropped v2 criteria with no counterpart: Customer Viability, End-Market Diversity, Volume Predictability.",
        "Pre-Screen sheet: circle-of-competence by sub-industry and company exclusions (investor inputs).",
        "Phase 4 (funnel): accounting audit (ROIC, True FCF conversion, Big Five, Buffett $1 test, balance sheet), "
        "Bird-in-the-Hand v2 and Hohn CAP valuation incl. closed-form market-implied CAP, Hohn DCF, Town sticker price, Weinstein stage.",
        "Phase 5: Holdings sheet with stretched-hold band and the three objective sell triggers.",
        "fetch_market_data.py: SEC EDGAR fundamentals (US) and Yahoo Finance prices/statements.",
    ],
}
