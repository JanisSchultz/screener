"""Framework configuration: criteria, pillars and default parameters.

Edit this file to change the framework, then run `python build.py` to compile
new workbook versions. Parameter values below are only the *defaults* written
into each workbook's Methodology sheet; they stay editable in Excel afterwards.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Criteria. Order matters: it defines the column order of the score block on
# the Inputs and Screen sheets. `scored=False` marks the four barrier
# sub-types, which feed the scored "Durable Barriers" criterion through MAX().
# ---------------------------------------------------------------------------
CRITERIA = [
    # code,   pillar, short label,                     full name, definition
    ("P1.1", "P1", "Permanent Need", "Permanent Customer Need (Dynamic Longevity)",
     "The underlying human or business need is permanent and durable, even if the product's form factor or delivery mechanism evolves over time."),
    ("P1.2", "P1", "Essentiality", "Essentiality",
     "The product or service is non-discretionary with a high cost of failure or absence. Total industry unit volume holds flat or grows during recessions rather than suffering deferrals."),
    ("P1.3", "P1", "Repeatability", "Repeatability",
     "Consumption is continuous via fast wear-out, daily/monthly replenishment, or ongoing subscriptions. Demand is organic and habitual, not inflated by temporary mandates, fads, or short hardware cycles."),
    ("P1.4", "P1", "Industry Trajectory", "Industry Trajectory",
     "Total industry unit volume is stable or growing over a 5- to 10-year cycle."),
    ("P2.1", "P2", "Customer Viability", "Customer Viability",
     "End-customers are financially healthy, profitable, and operating in durable or expanding markets."),
    ("P2.2", "P2", "Buyer Fragmentation", "Buyer Fragmentation",
     "Sales are spread across a broad, unorganized customer base with low bargaining power rather than concentrated in a few giant buyers."),
    ("P2.3", "P2", "End-Market Diversity", "End-Market Diversity (Niche Test)",
     "Specialized niche products serve multiple unrelated industries rather than relying on a single challenged sector."),
    ("P2.4", "P2", "Supplier & Labor Independence", "Supplier & Labor Independence",
     "The company does not rely on concentrated suppliers, unionized labor forces, or star talent that can extract the majority of the profit pool."),
    ("P3.1", "P3", "Adaptive Management", "Adaptive Management vs. Obsolescence",
     "Management demonstrates a deep understanding of the customer need and the ability to evolve product delivery over time without falling into a capital-intensive \"innovation treadmill\" or destroying the core business model."),
    ("P3.2", "P3", "Tectonic Shift risk (2=low)", "Tectonic Technology Shifts",
     "Low risk that a new technology completely supplants the category's underlying mechanism (e.g., cloud leapfrogging on-premise software, or digital replacing mechanical)."),
    ("P3.3", "P3", "Counter-Positioning risk (2=low)", "Counter-Positioning",
     "Low vulnerability to challengers introducing a superior, lower-cost business model that the incumbent cannot copy without cannibalizing its existing profits."),
    ("P3.4", "P3", "Cross-Industry Substitutes (2=few)", "Cross-Industry Substitutes",
     "Few affordable alternatives outside the industry fulfill the same function and cap the pricing ceiling."),
    ("P4.1", "P4", "Industry Structure & Share", "Industry Structure & Share",
     "The market is a monopoly, duopoly, or rational oligopoly where competitors compete on reliability and quality rather than price. The company holds a #1 or #2 position with stable multi-year market share."),
    ("P4.2", "P4", "Switching Costs", "Switching Costs",
     "Customers are locked in by deep workflow integration, high retraining time, long-term aftermarket service attaches on an installed base, or high benefit-to-cost asymmetry."),
    ("P4.3a", "P4", "Barrier: Network Effects", "Durable Barriers to Entry — Network Effects",
     "Interactive multi-node networks (not vulnerable radial spokes) or fragmented demand/supply aggregators."),
    ("P4.3b", "P4", "Barrier: Cost Advantage", "Durable Barriers to Entry — Cost Advantages",
     "Structural scale-based or distribution-density advantages (high Surplus Leader Margin), rather than easily copied process-based advantages."),
    ("P4.3c", "P4", "Barrier: Efficient Scale", "Durable Barriers to Entry — Efficient Scale",
     "Niche market too small for a new entrant to earn its cost of capital."),
    ("P4.3d", "P4", "Barrier: Intangibles", "Durable Barriers to Entry — Intangible Assets",
     "Regulatory licenses, patents, or brands that actively change behavior (driving price premiums via aspiration/scarcity or lowering search/uncertainty costs via consistency)."),
    ("P5.1", "P5", "Volume Predictability", "Volume Predictability & Inventory Discipline",
     "Steady industry demand and locked-in share yield predictable volume growth, with inventory and net earnings rising smoothly together rather than in boom-bust spikes."),
    ("P5.2", "P5", "Pricing Power", "Real Pricing Power vs. Intentional Price-Giveback",
     "The company consistently raises prices above inflation without losing unit volume or discounting—OR intentionally shares scale economies via low prices to compound volume and widen the moat without draining long-term customer trust."),
]
BARRIER_CODES = ["P4.3a", "P4.3b", "P4.3c", "P4.3d"]
SCORE_VALUES = (0, 1, 2)

PILLARS = {
    "P1": "Demand Side",
    "P2": "Customer & Supplier Health",
    "P3": "Obsolescence Test",
    "P4": "The Moat",
    "P5": "Financial Output",
}
PILLAR_LONG = {
    "P1": '1. Demand Side ("Meaning" — Industry Volume & Need Durability)',
    "P2": "2. Customer & Supplier Health (Value-Chain Power)",
    "P3": "3. Technical Disruption & Substitution Risk (Obsolescence Test)",
    "P4": '4. Supply Side ("The Moat" — Relative Position & Barriers)',
    "P5": "5. Financial Output (Volume & Pricing Power)",
}
# Max points per pillar (P4: structure + switching + MAX(barriers) = 3 criteria)
PILLAR_MAX = {"P1": 8, "P2": 8, "P3": 8, "P4": 6, "P5": 4}

# ---------------------------------------------------------------------------
# Parameters -> Methodology sheet input cells, each exposed as an Excel
# defined name. (name, label, default, number format, note)
# ---------------------------------------------------------------------------
V1 = "Carried over from v1."
NEW = "New in v2; default chosen during the v2 rebuild — adjust to taste."

PARAMETER_GROUPS = [
    ("Pillar pass thresholds", [
        ("thr_P1", "P1 Demand Side: min subtotal (of 8)", 6, "0", V1),
        ("thr_P2", "P2 Customer & Supplier Health: min subtotal (of 8)", 6, "0", V1),
        ("thr_P3", "P3 Obsolescence Test: min subtotal (of 8)", 6, "0", V1),
        ("thr_P4", "P4 The Moat: min subtotal (of 6)", 5, "0", V1),
        ("thr_P4_barrier", "P4: min Durable Barriers score (MAX of 4 sub-types)", 2, "0", V1),
        ("thr_P4_structure", "P4: min Industry Structure & Share score", 1, "0", V1),
        ("thr_P5", "P5 Financial Output: min subtotal (of 4)", 3, "0", V1),
        ("req_nonzero", "P1–P3: require no criterion scored 0 (1 = yes, 0 = no)", 1, "0", V1),
    ]),
    ("Hurdle and result rules", [
        ("roic_hurdle", "10-year average ROIC hurdle (min)", 0.15, "0.0%", V1),
        ("nm_pillars", "Near-miss: min pillars passed", 4, "0", V1),
        ("nm_score", "Near-miss: min weighted score (of 100)", 75, "0.0",
         "New in v2 (replaces 26 of 34 = 76.5%). Now measured on the weighted /100 score."),
    ]),
    ("Pillar weights (weighted score = Σ weight × pillar% ÷ Σ weights × 100)", [
        ("w_P1", "Weight: P1 Demand Side", 0.20, "0%", NEW + " Equal weights by default; v1 implicitly weighted 8/8/8/6/4."),
        ("w_P2", "Weight: P2 Customer & Supplier Health", 0.20, "0%", NEW),
        ("w_P3", "Weight: P3 Obsolescence Test", 0.20, "0%", NEW),
        ("w_P4", "Weight: P4 The Moat", 0.20, "0%", NEW),
        ("w_P5", "Weight: P5 Financial Output", 0.20, "0%", NEW),
    ]),
    ("Confidence adjustment and ranking", [
        ("conf_H", "Confidence multiplier: H", 1.00, "0.00", NEW),
        ("conf_M", "Confidence multiplier: M", 0.95, "0.00", NEW),
        ("conf_L", "Confidence multiplier: L", 0.85, "0.00", NEW),
        ("rank_basis", "Rank by: 1 = weighted score, 2 = confidence-adjusted score", 1, "0", NEW),
    ]),
]

# Only written for universes that carry financial reference data (US / EDGAR).
P5_CHECK_PARAMETERS = ("P5 data check (flags disagreement; never changes a score)", [
    ("p5_ni_good", "Net-income down-years share ≤ this → implied Volume = 2", 0.20, "0%", NEW),
    ("p5_ni_ok", "Net-income down-years share ≤ this → implied Volume = 1", 0.40, "0%", NEW),
    ("p5_inv_gap", "Inventory − revenue growth above this (pp/yr) → implied Volume −1", 3, "0.0", NEW),
    ("p5_gm_good", "Gross-margin range ≤ this (pp) → implied Pricing = 2", 5, "0.0", NEW),
    ("p5_gm_ok", "Gross-margin range ≤ this (pp) → implied Pricing = 1", 12, "0.0", NEW),
    ("p5_flag_gap", "Flag 'Review' when |analyst − implied| ≥ this", 2, "0", NEW),
])

# Result labels (used in formulas and conditional formatting)
RES_PASS = "PASS"
RES_QROIC = "Quality – ROIC not met"
RES_NEAR = "Near-miss"
RES_FAIL = "Fail"
RESULTS = [RES_PASS, RES_QROIC, RES_NEAR, RES_FAIL]

# Capacity of the formula-driven lists on the Shortlists sheet / Overrides log
LIST_CAPACITY = {"top": 25, RES_PASS: 150, RES_QROIC: 150, RES_NEAR: 300}
OVERRIDE_ROWS = 500

CHANGELOG = {
    "2.0": [
        "Rebuilt from a Python generator (build.py); data lives in data/<universe>/*.csv.",
        "Inputs / Screen split: analyst inputs on 'Inputs', all calculation on 'Screen'.",
        "Overrides log: criterion-level analyst overrides with reason, analyst, date; base scores preserved.",
        "Editable pillar weights; weighted score /100 replaces raw /34 as the headline score (raw /34 kept).",
        "Confidence-adjusted score (H/M/L multipliers) with switchable ranking basis.",
        "New result category 'Quality – ROIC not met' (all 5 pillars pass, ROIC hurdle not met) — split out of Near-miss.",
        "Live Excel-native shortlists (INDEX/MATCH) replace the frozen Google-Sheets export formulas.",
        "Weak points (criteria scored 0) and failed pillars are computed live, not typed into the rationale.",
        "Unique company ID (EU: ticker.country) — fixes duplicate tickers SAN, BOL, UNI.",
        "EU ROIC: numeric ROIC column added (blank) alongside the v1 Pass/Fail judgement; KION's corrupted value ('KNEBV') cleared → 'Missing'.",
        "US: formula-driven P5 data check against EDGAR reference metrics.",
        "Data validation on all score/confidence inputs and a Data Checks sheet.",
    ],
}
