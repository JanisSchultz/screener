# Qualitative Evaluation Framework Specification (v7.16)
## Quality & Moat Screener — 6 Sequential Munger Reject Gates

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent qualitative screening** of individual public companies within the Quality & Moat Screener (v7.16). It can be executed entirely standalone by an AI agent to determine whether a company qualifies as a world-class compounder.

### The Evaluator Agent's Core Mindset
As an independent qualitative evaluator agent, your mandate is inspired by **Charlie Munger** and **Warren Buffett**:
> *"Tell me where I am going to die, that is, so I don't go there."* — Charlie Munger

1. **Default Stance is Rejection**: Fewer than ~250 companies across the US, European, and Canadian large-cap universes possess the enduring business quality required to compound capital over decades. You do not search for reasons to include a company; you actively hunt for the fatal flaw that eliminates it.
2. **Strict Sequential Waterfall Invariant (with Conditional Calamity Tier on Gates 3b, 5 & 6 Only)**: Evaluation proceeds strictly in order (Gate 1 $\rightarrow$ Gate 6). Normally, at the first gate a company fails, it is immediately rejected and downstream fields are left blank/null. **Exception (Buffett Temporary Fixable Calamities)**: if a company passes all Anchor Gates (`1="Y"`, `2="Y"`, `3a!="None"`, and `4>=15`) and fails **only Gate `3b`, `5`, and/or `6`** due to an identifiable, temporary, fixable calamity, record the raw failing values honestly, set `calamity_flag: "Y"` with a three-part `calamity_note` (broken metric, intact moat proof, fix catalyst/kill-switch), and evaluate all remaining downstream gates so it enters Quantitative valuation under the separate **`Calamity pass`** tier.
3. **Evidence Over Narrative**: Assertions must be anchored in empirical financial reality: multi-cycle ROIC, free cash flow conversion, pricing power history, competitive dynamics, and balance sheet endurance through crises.

---

## 2. Input Context Provided to the Qualitative Evaluator

When an evaluation is triggered, the coordinator agent provides:

### 2.1 Identifiers & Classification
- `id`: Unique identifier (e.g. `MSFT`, `AIR.FR`, `CNR.CA`).
- `ticker`: Trading ticker (e.g. `MSFT`, `AIR`, `CNR`).
- `company`: Official company name.
- `country`: Country of primary listing / headquarters.
- `sector`: GICS Sector.
- `sub_industry`: GICS Sub-industry.
- `universe`: `us`, `eu`, or `ca`.

### 2.2 Pre-Screen Context
- `in_market`: `Y` or `N`. Whether the company's listing country is an approved rule-of-law Western developed market (`markets.csv`).
- `g6_default`: `N` or blank. Pre-Screen sub-industry default for Gate 6 (regulated utilities and commercial deposit banks default to `N`).

### 2.3 Financial & Historical Operating Context
- **Business Model Overview**: Product/service lines, revenue models (recurring SaaS, consumable replacement, transactional, project-based), customer concentration.
- **Capital Efficiency History**: 5–10 years of reported GAAP ROIC, Operating ROIC (tangible), operating margins, gross margins.
- **Cash Flow & Balance Sheet**: 5–10 years of Net Income, Free Cash Flow (FCF), Owner FCF conversion (`FCF / Net Income`), Long-Term Debt, Total Cash, Interest Expense, and Interest Coverage (`EBIT / Interest`).

---

## 3. The 6 Sequential Munger Reject Gates (Rubric & Scoring)

Evaluation must execute strictly in sequence. The first failed gate triggers an immediate reject verdict.

```
Gate 1: Simple to Understand
  │ [Pass: Y]
  ▼
Gate 2: Essential Western Need & Entrenched Everyday Habits ('Likely To' Standard)
  │ [Pass: Y]
  ▼
Gate 3: Strong Moat & Pricing Power >= Inflation (3a Archetype + 3b ROIC >= 12% & Pricing)
  │ [Pass: Y]
  ▼
Gate 4: Low Disruption Risk & Predictable Runway (CAP >= 15 Yrs via Mauboussin Persistence)
  │ [Pass: Y]
  ▼
Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation (Score >= 1)
  │ [Pass: Y]
  ▼
Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Peace-of-Mind Balance Sheet
  │ [Pass: Y]
  ▼
QUALITY PASS (Qualifies for Quantitative PAR Valuation Funnel)
```

---

### Gate 1: Simple to Understand
- **Code**: `1`
- **Output Type**: Gate (`Y` / `N`)
- **Core Principle**: Circle of competence and external verifiability. Negative check favoring established, transparent business models with long public operating histories over opaque, complex, or unproven models.
- **Pass Standard (`Y`)**:
  - Established economic engine with a long public operating track record.
  - Transparent financial statements where key risks are directly visible in reported figures.
  - Conventional holding companies, transparent banks, and standard insurers pass if their balance sheets, reserves, and investment portfolios are verifiable from the outside.
- **Reject Standard (`N`)**:
  - *(a) Not Established*: Novel, unproven, or pre-profit business models lacking a multi-cycle public operating record.
  - *(b) Not Verifiable from Outside*: Key economic risks are invisible in reported figures (e.g. large proprietary trading operations, opaque long-tail insurance reserves, complex unconsolidated affiliate webs, crypto treasuries, or valuation hinging on a single binary regulatory/clinical trial event).
- **Waterfall Action**: If `1 == "N"`, set `result = "Rejected – G1 Understandability"`. Leave Gates 2–6 completely blank/null.

---

### Gate 2: Essential Western Need & Entrenched Everyday Habits
- **Code**: `2` (Gate: `Y` / `N`) & `2r` (Text: Reason if `N`)
- **Core Principle**: Charlie Munger & Warren Buffett's *"likely to spend"* standard and societal acceptance risk.
- **Pre-Screen Geographic Condition**: If the listing country is outside rule-of-law Western markets (`in_market == "N"`), Gate 2 automatically fails (`N`).
- **Pass Standard (`Y`)**:
  - Serves an essential customer need or an entrenched, high-propensity everyday habit/ritual (*"likely to"* spend) in the Western world with low societal and legislative acceptance risk.
  - *Functional Necessities*: Healthcare, basic hygiene, critical logistics/transportation, grocery staples, water/power utilities, mission-critical enterprise software.
  - *Entrenched Everyday Habits & Cultural Staples*: High-frequency daily rituals and Lindy consumer staples (iconic beverages/snacks, everyday quick-service dining, staple household entertainment, Lindy-luxury compounders like Hermès, LVMH, Ferrari).
- **Reject Standard (`N`)**:
  - True discretionary big-ticket or deferrable cyclicals (cruise lines, airlines, cyclical homebuilders, luxury yachts).
  - Speculative commodity price-takers (gold, copper, lithium, upstream exploration).
  - Revenue bases concentrated in non-Western, autocratic, or pariah jurisdictions lacking property rights and rule of law.
  - Predatory, addictive, or socially destructive business models with high legislative, regulatory, or societal ruin risk (tobacco, CFD retail spread-betting, predatory subprime lending, private prisons).
- **Required Reason (`2r`)**: If `2 == "N"`, provide a concise, rigorous explanation in `2r` (e.g. *"Discretionary big-ticket purchase deferrable in recessions"*, *"Commodity price taker lacking pricing power"*, or *"High societal acceptance and regulatory taxation risk"*).
- **Waterfall Action**: If `2 == "N"`, set `result = "Rejected – G2 Essential Need"`. Leave Gates 3–6 completely blank/null.

---

### Gate 3: Strong Moat Profile & Pricing Power >= Inflation
Gate 3 evaluates the company's **4-Archetype Moat Profile** (establishing Step 1 **Initial CAP** and auto-deriving `3a`), Empirical Proof of Moat, and Pricing Power *before* adjusting longevity for competitive & disruptive forces in Gate 4.

#### Gate 3 Moat Archetype Scores (`3_tb`, `3_ia`, `3_se`, `3_rd`) & Primary Moat (`3a`)
Score each of the four orthogonal moat archetypes on **`0 / 1 / 2`** (`0` = Absent/Negligible, `1` = Supporting/Moderate Moat, `2` = Primary/Elite Moat):
1. **`3_tb` — `Toll booth & switching costs`**: Network effects, embedded mission-critical software/data workflow lock-in, high contractual or operational customer switching barriers (e.g. Visa, Mastercard, Microsoft, S&P Global).
2. **`3_ia` — `Irreplaceable infrastructure & intangibles`**: Physically or legally unreplicable infrastructure, physical distribution/hub density networks, concessions/permits, regulatory licenses, proprietary datasets, and Lindy brands (e.g. Waste Management, CN Rail, Hermès, Hershey).
3. **`3_se` — `Scale economies shared`**: **Strictly the Nick Sleep model** — deliberately passing operational unit-cost scale efficiencies back to customers via lower prices or superior consumer surplus to compound volume and widen unit-cost superiority (e.g. Costco, Walmart, Progressive). Standard margin-maximizing businesses with physical hub/network scale score on `3_ia`, not `3_se`.
4. **`3_rd` — `R&D & innovation leadership`**: Deep proprietary engineering know-how, continuous R&D velocity, and active product/process frontier leadership (e.g. ASML, KLA, Intuitive Surgical).

- **Primary Moat Archetype (`3a`)**:
  - Must be one of the 4 canonical labels above (matching an archetype achieving the company's maximum score $m_{\max}$), or `None` when $m_{\max} = 0$.
  - `apply_evaluation.py` automatically enforces `3a = "None"` when all four scores are `0` and aligns `3a` to the top-scoring archetype.
- **Step 1 Deterministic Initial CAP (`CAP_init`)**:
  Let $m_{\max} = \max(s_{\text{tb}}, s_{\text{ia}}, s_{\text{se}}, s_{\text{rd}})$ and $m_{\text{sum}} = s_{\text{tb}} + s_{\text{ia}} + s_{\text{se}} + s_{\text{rd}}$:
  - $m_{\max} = 0 \implies \text{CAP}_{\text{init}} = 0\text{Y}$ (`3a = "None"`, automatic Gate 3 **REJECT**)
  - $m_{\max} = 1, m_{\text{sum}} = 1 \implies \text{CAP}_{\text{init}} = 15\text{Y}$
  - $m_{\max} = 1, m_{\text{sum}} \ge 2 \implies \text{CAP}_{\text{init}} = 20\text{Y}$ *(capped at 20Y without at least one elite `2` moat)*
  - $m_{\max} = 2, m_{\text{sum}} = 2 \implies \text{CAP}_{\text{init}} = 20\text{Y}$
  - $m_{\max} = 2, m_{\text{sum}} = 3 \implies \text{CAP}_{\text{init}} = 25\text{Y}$
  - $m_{\max} = 2, m_{\text{sum}} \ge 4 \implies \text{CAP}_{\text{init}} = 30\text{Y}$

#### Gate 3b: Pricing Power & Proof of Moat
- **Code**: `3b`
- **Output Type**: Gate (`Y` / `N`)
- **Pass Standard (`Y`)**:
  - Must have a verified structural moat (`m_max >= 1`, `3a != "None"`).
  - **Proof of Moat**: Empirically verified by historical capital efficiency: **5-Year Median GAAP ROIC $\ge$ 12%** AND **Incremental ROIIC $\ge$ 12%** across the business cycle. (Operating companies failing both tangible ROIC $\ge$ 15% and GAAP ROIC $\ge$ 12% are automatically rejected).
  - **Pricing Power $\ge$ Inflation**: Demonstrated ability to raise prices at or above inflation across the cycle without losing customer volume or market share (e.g. basis-point ad valorem toll booths, CPI-indexed concession contracts, inelastic mission-critical workflows, or scale-shared surplus resilience).
  - *Look-Through Holding Companies*: Evaluated on look-through portfolio operating moats and look-through pricing power.
- **Reject Standard (`N`)**:
  - All moat scores are `0` (`3a == "None"`).
  - Commodity price-taker whose margins fluctuate with spot commodity prices.
  - Sub-hurdle historical returns on capital (ROIC < 12%).
  - State price caps, utility rate freezes, or customer churn upon price hikes indicating zero pricing power.
- **Moat & Erosion Note (`3m`)**:
  - Required text summarizing: (1) the scored moat archetypes preventing competitors from arbitraging away returns, (2) empirical proof of moat (ROIC, gross margin stability), and (3) primary erosion vectors.
- **Waterfall Action**: If `3a == "None"` or (unwaived) `3b == "N"`, set `result = "Rejected – G3 Moat & Pricing"`. Leave Gates 4–6 completely blank/null.

---

### Gate 4: Low Disruption Risk & Predictable Runway (15+ Years)
- **Codes**: `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub` (`0`, `1`, `2` each), `4` (deterministic Final CAP: `0`, `5`, `10`, `15`, `20`, `25`, or `30` years), and `4n` (Runway & Forces Note).
- **Threshold**: `thr_cap = 15`. A Final CAP $< 15$ is an immediate **REJECT**.
- **No Manual CAP Override**: Whenever Gate 3 and Gate 4 sub-scores are present, `4` is computed **100% deterministically** from `CAP_init` and the 5 Competitive Force scores.

#### Step 2: Porter's 5 Competitive Forces Evaluated via the 5 Macrotrends & Industry Clock Speed
Score the **secular 15–30 year trajectory ($\Delta$)** of each of Porter's Five Forces on **`0 / 1 / 2`** (`0` = Benign / Insulated / Tailwind, `1` = Moderate / Manageable Secular Pressure, `2` = Severe / Terminal Structural Threat):
1. **`4_ent` — Threat of New Entrants**: Secular risk of falling entry barriers (e.g. AI coding/cloud lowering software build costs, regulatory deregulation, subsidized challengers).
2. **`4_riv` — Competitive Rivalry**: Secular risk of intensifying price, promotional, or capital-expenditure rivalry among incumbents (e.g. hyperscaler AI capex arms race, private-label competition).
3. **`4_buy` — Customer Bargaining Power**: Secular risk of rising buyer leverage (e.g. customer consolidation, AI-driven enterprise seat-count compression, multi-homing, state healthcare reimbursement caps).
4. **`4_sup` — Supplier Bargaining Power**: Secular risk of rising upstream input/labor leverage (e.g. single-source foundry/optics bottlenecks, demographic skilled-labor scarcity, geopolitical supply concentration, energy/resource limits).
5. **`4_sub` — Threat of Substitution & Clock Speed**:
   - Secular paradigm substitution (e.g. agentic AI replacing seat-based SaaS, routine lookup, or billable-hour IT staffing; GLP-1s; energy transition).
   - **Mauboussin Outside-View Clock-Speed Rule**: Fast-clock-speed technology, semiconductor, pharma/biotech, and hardware sub-industries carry a **presumptive `4_sub >= 1`** due to continuous technological product resets unless protected by an unbypassable physical or protocol standard (e.g. ASML's EUV physics).

**Mandatory 5-Macrotrend Lens** (check every force against all 5 macrotrends):
- `[1] Automation & Cognitive Tech (AI)`
- `[2] Demographic Aging & Labor Scarcity`
- `[3] Geopolitical Realignment & Supply Chain Reshoring`
- `[4] Energy Transition & Resource Limits`
- `[5] Structural Inflation & Cost of Capital`

#### Deterministic Final CAP Formula (`compute_final_cap_from_scores`)
Let $c_2 = \sum \mathbf{1}(f_i = 2)$ and $c_1 = \sum \mathbf{1}(f_i = 1)$, with tiered moderate haircut $h(0)=0\text{Y}$, $h(1\text{–}2)=5\text{Y}$, $h(3\text{–}4)=10\text{Y}$, $h(5)=15\text{Y}$ (preventing double-counting of correlated moderate frictions):
- **Fatal-Flaw Cap ($c_2 \ge 1$)**: Any single Force $= 2$ caps $\text{CAP}_{\text{final}} \le 10\text{Y}$ (**immediate REJECT**):
  - $c_2 \ge 3 \implies 0\text{Y}$
  - $c_2 = 2 \implies 5\text{Y}$
  - $c_2 = 1 \implies 10\text{Y}$ if $\text{CAP}_{\text{init}} - 10 - h(c_1) \ge 10$, else $5\text{Y}$.
- **No Fatal Flaw ($c_2 = 0$)**:
  $$\text{CAP}_{\text{final}} = \max\!\big(5,\; \text{CAP}_{\text{init}} - h(c_1)\big)$$
- **Runway & Forces Note (`4n`)**: Mandatory concise text whenever any Force $\ge 1$, explaining the specific competitive force adjustments (recommended briefly even when all Forces $= 0$).
- **Three Anti-Drift Calibration Rules**:
  1. **Sub-Industry Peer Benchmarking**: Always cross-check `CAP_init` and Force scores against same-sub-industry peers so global oligopoly twins (e.g. `SU.FR` vs `ETN`, `DHR` vs `TMO`, `CME` vs `ICE` / `DB1.DE`, `WM` vs `RSG` / `WCN.CA`) are evaluated on an identical yardstick.
  2. **`4_sub / 4_riv = 1 vs. 2` Boundary (UI Seat Layer vs. Proprietary Data/Statutory Engine)**: Reserve `2` (Terminal Threat $\implies \text{CAP} \le 10\text{Y}$) for seat-licensed application/UI workflows or discretionary research workstations (`CRM`, `ADBE`, `NOW`, `FDS`, `TRI`). Score proprietary non-seat risk/compliance datasets & statutory calculation standards (`REL.GB`, `WKL.NL`, `FICO`) at `1` (Moderate Pressure).
  3. **Gate 4 vs. Gate 5/6 Orthogonality (No Gate-Bleed)**: Gate 4 measures *business-model and moat longevity only*. Value-dilutive PE M&A rollups (`ROP`), predatory price gouging, or debt-funded buybacks creating negative equity (`FICO`, `MSCI`) must be rejected at **Gate 5 (`5 = 0`)** and/or **Gate 6 (`6 = "N"`)**, never by artificially compressing Gate 4 CAP.
- **Waterfall Action**: If `4 < 15`, set `result = "Rejected – G4 Runway (<15Y)"` (keeping `4_*`, `4`, and `4n` populated for auditability) and leave Gates 5–6 completely blank/null.

---

### Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation
- **Code**: `5`
- **Output Type**: Score: `0`, `1`, or `2`
- **Threshold**: `thr_culture = 1`. A score of `0` is an immediate **REJECT**.

#### Five-Vector Elimination Rubric
Management is evaluated across five distinct superinvestor vectors:
1. **(a) Integrity & Candor (Phil Fisher / Warren Buffett)**: Radical transparency in shareholder communications; candid admission of operating errors; conservative accounting without promotional non-GAAP adjustments; transparent stock-based compensation (SBC).
2. **(b) Rational Capital Allocation (Tom Murphy / Will Thorndike — *"The Outsiders"*)**: Ruthless focus on per-share intrinsic value growth; disciplined reinvestment hurdle rates ($\ge 12\%$); counter-cyclical share repurchases executed only below intrinsic value; avoidance of dilutive, empire-building mega-M&A.
3. **(c) Customer Value-for-Money / Consumer Surplus (Jeff Bezos / Nick Sleep)**: Obsessive focus on delivering superior value to customers; refusal to employ predatory price gouging or dark patterns that build customer resentment.
4. **(d) Product-Led Execution**: Deep technical and operational domain expertise; product and engineering excellence rather than financial engineering.
5. **(e) Anti-Bureaucracy & Planned Abandonment (Marcus Wallenberg / Peter Drucker)**: Lean corporate headquarters; radical decentralization; disciplined pruning of sub-hurdle divisions.

#### Scoring Rules
- **`0` (REJECT — Red Flag Triggered)**: Promotional executive ego; aggressive non-GAAP accounting or repeated "one-off" adjustments; value-destructive M&A rollups; predatory customer pricing; bureaucratic bloat; or management compensation decoupled from per-share compounding.
- **`1` (Standard Pass)**: Honest, capable stewardship; sensible capital allocation; good alignment with shareholders; clean accounting without red flags.
- **`2` (Elite Compounder)**: True owner-operator or exceptional "Outsider" CEO; multi-decade track record of exceptional per-share value creation; substantial insider skin in the game; high consumer surplus.
- **Waterfall Action**: If `5 < 1` (i.e. `0`), set `result = "Rejected – G5 Management"`. Leave Gate 6 completely blank/null.

---

### Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Peace-of-Mind Balance Sheet
- **Code**: `6`
- **Output Type**: Gate (`Y` / `N`)
- **Core Principle**: Charlie Munger's qualitative triad and Warren Buffett's solvency standard: peak-to-peak earnings power, genuine cash generation, and freedom from the *"kindness of strangers"*.

#### The Three Compounding Pillars
1. **Pillar 1: Peak-to-Peak Business Cycle EPS Compounding**:
   - Demonstrated track record and structural visibility of reaching a **new high in Owner EPS at the peak of each succeeding business cycle**.
   - Normal intra-cycle dips during general economic recessions are fully acceptable, provided peak-to-peak secular growth remains intact.
   - The prior peak must represent repeatable earnings power, not an unrepeatable windfall spike.
2. **Pillar 2: Real Free Cash Flow Conversion**:
   - Reported accounting profits convert cleanly into free cash flow: **Multi-Year Owner FCF $\ge$ 80% of GAAP Net Income** (`fcf_conv >= 0.80`).
   - The business is free from maintenance capex sinkholes, heavy capitalization of intangible costs, or working-capital black holes.
3. **Pillar 3: Peace-of-Mind Balance Sheet (No "Kindness of Strangers")**:
   - The capital structure is built to comfortably endure a multi-year economic depression or complete credit market freeze without permanently impairing common equity.
   - Leverage strictly amplifies an already superior, cash-generative engine rather than masking or funding a mediocre one.
   - **Quantitative Baseline**:
     - Net Debt repayable from normal Owner Earnings in $\le 4.0$ years (`lt_debt_m / ni_ttm_m <= 4.0` or net cash).
     - Interest Coverage: $\text{EBIT} / \text{Interest} > 5.0\text{x}$ through the cycle (ideally $> 10\text{x}$).
   - **Essential Infrastructure & Concession Standards**: Contractually formula-indexed physical infrastructure (freight rails, permitted landfills, regulated toll concessions) with non-displaceable cash flows pass provided interest coverage remains $> 5\text{x}$.
   - **Float Institutions & Holding Companies**: Insurers and holding companies are evaluated on Solvency II ratios ($> 200\%$), conservative underwriting discipline, and look-through operating earnings. Commercial fractional-reserve banks fail.
   - **Surplus Cash Rule**: Cash and short-term sovereign T-bills held as dry powder count *toward* balance sheet fortress strength, never against return hurdles.
   - **Disqualifying Red Flags (Automatic `N`)**:
     - Financial engineering: debt-funded share buybacks at peak cycle multiples resulting in negative tangible equity.
     - Serial M&A rollups relying on continuous debt issuance or high-multiple equity dilution.
     - Reliance on short-term commercial paper or continuous access to capital markets to fund ongoing operations.
- **Waterfall Action**: If `6 == "N"`, set `result = "Rejected – G6 Cash & Fortress Balance Sheet"`. If `6 == "Y"`, the company achieves **Quality Pass**!

---

## 4. Qualitative Synthesis: Notes & Evidence Standards

### 4.1 The `note` Field
- **For Quality Pass Companies**:
  - Summarize the core economic engine, primary moat barrier, 5-macrotrend resilience, and balance sheet verdict.
  - **Mandatory Forward Growth Formula**: End the note with an explicit, bracketed 5–10 year forward growth breakdown:
    `[5-10Y g: volume % + price % + mix/reinvestment % - margin drags % + buybacks %]`
  - *Example*:
    `Passes all 6 gates. Unassailable enterprise software and cloud infrastructure duopoly. Pricing power demonstrated by 9-15% M365 price hikes with zero churn. Balance sheet fortress with $80B+ net cash. [5-10Y g: cloud volume 6.5% + enterprise price 2.0% - AI GPU capex D&A drag 0.5% + net share repurchases 1.0%]`
- **For Rejected Companies**:
  - State the exact failing gate, the specific operational or financial failure mechanism, and why the company fails the Munger bar.
  - *Example*:
    `Fails Gate 4 (CAP = 10, REJECT). Enterprise CRM seat-based SaaS model faces severe terminal headwinds from AI automation agents reducing corporate customer headcount. Gross margins under pressure as compute costs rise.`

### 4.2 The `evidence` Field
Provide a comprehensive synthesis including:
- Multi-cycle financial track record (historical ROIC, operating margin trends, cash conversion).
- Segment revenue and profit breakdowns.
- Key customer lock-in mechanisms and empirical proof of pricing power.
- Historical M&A record, capital allocation behavior, and debt repayment history.

---

## 5. Output Contract: Qualitative JSON Result Schema

An independent agent evaluating a company qualitatively must return a strictly validated JSON payload matching this exact schema:

```json
{
  "id": "MSFT",
  "ticker": "MSFT",
  "universe": "us",
  "company": "Microsoft Corporation",
  "country": "United States",
  "sector": "Information Technology",
  "sub_industry": "Systems Software",
  "qualitative": {
    "gate_1": "Y",
    "gate_2": "Y",
    "gate_2_reason": null,
    "gate_3_moat_toll_booth": 2,
    "gate_3_moat_infrastructure": 2,
    "gate_3_moat_scale_shared": 0,
    "gate_3_moat_rd": 1,
    "gate_3a_moat_archetype": "Toll booth & switching costs",
    "gate_3b_pricing_and_proof": "Y",
    "gate_3m_moat_note": "Extreme enterprise switching costs across M365, Entra ID, and Azure plus global hyperscale cloud footprint proved by repeated 9-15% E3/E5 price hikes with near-zero churn.",
    "gate_4_force_entrants": 0,
    "gate_4_force_rivalry": 1,
    "gate_4_force_buyers": 0,
    "gate_4_force_suppliers": 0,
    "gate_4_force_substitution": 1,
    "gate_4_runway_cap": 25,
    "gate_4n_runway_note": "Initial CAP 30Y reduced by -5Y for hyperscaler AI infrastructure Rivalry (4_riv=1) and fast software/AI technology clock speed (4_sub=1).",
    "gate_5_management_score": 1,
    "gate_6_cash_and_balance_sheet": "Y",
    "calamity_flag": null,
    "calamity_note": null,
    "note": "Indispensable enterprise software and cloud oligopolist. Pricing power demonstrated by repeated price hikes with zero churn. $80B+ net cash balance sheet. [5-10Y g: cloud volume 6.5% + enterprise price 2.0% - AI GPU capex D&A drag 0.5% + net buyback 1.0%]",
    "evidence": "30%+ Operating ROIC over 10 years. FCF conversion >100%. Azure and Office 365 form an indispensable productivity layer for modern enterprise."
  },
  "evaluation_metadata": {
    "verdict": "Quality pass",
    "failing_gate": null,
    "evaluated_at": "2026-11-09T20:15:00Z",
    "evaluator": "qualitative-agent"
  }
}
```

### Field Mapping & Waterfall Invariant Rules

| CSV Field | JSON Key (`qualitative`) | Allowed Values | Nullable Rules |
| :--- | :--- | :--- | :--- |
| `1` | `gate_1` | `"Y"`, `"N"` | Never null |
| `2` | `gate_2` | `"Y"`, `"N"` | Null if Gate 1 is `"N"` |
| `2r` | `gate_2_reason` | String | Populated only if `gate_2 == "N"`, else null |
| `3_tb` | `gate_3_moat_toll_booth` | `0`, `1`, `2` | Null if Gate 1 or 2 is `"N"` |
| `3_ia` | `gate_3_moat_infrastructure` | `0`, `1`, `2` | Null if Gate 1 or 2 is `"N"` |
| `3_se` | `gate_3_moat_scale_shared` | `0`, `1`, `2` | Null if Gate 1 or 2 is `"N"` |
| `3_rd` | `gate_3_moat_rd` | `0`, `1`, `2` | Null if Gate 1 or 2 is `"N"` |
| `3a` | `gate_3a_moat_archetype` | `"Toll booth & switching costs"`, `"Irreplaceable infrastructure & intangibles"`, `"Scale economies shared"`, `"R&D & innovation leadership"`, `"None"` | Null if Gate 1 or 2 is `"N"`; derived/validated from max Gate 3 moat score (`"None"` if all `0`) |
| `3b` | `gate_3b_pricing_and_proof` | `"Y"`, `"N"` | Null if Gate 1 or 2 is `"N"` |
| `3m` | `gate_3m_moat_note` | String | Null if Gate 1 or 2 is `"N"` |
| `4_ent` | `gate_4_force_entrants` | `0`, `1`, `2` | Null if Gate 1, 2, or (3a=`"None"` / unwaived 3b=`"N"`) fails |
| `4_riv` | `gate_4_force_rivalry` | `0`, `1`, `2` | Null if Gate 1, 2, or (3a=`"None"` / unwaived 3b=`"N"`) fails |
| `4_buy` | `gate_4_force_buyers` | `0`, `1`, `2` | Null if Gate 1, 2, or (3a=`"None"` / unwaived 3b=`"N"`) fails |
| `4_sup` | `gate_4_force_suppliers` | `0`, `1`, `2` | Null if Gate 1, 2, or (3a=`"None"` / unwaived 3b=`"N"`) fails |
| `4_sub` | `gate_4_force_substitution` | `0`, `1`, `2` | Null if Gate 1, 2, or (3a=`"None"` / unwaived 3b=`"N"`) fails |
| `4` | `gate_4_runway_cap` | `0`, `5`, `10`, `15`, `20`, `25`, `30` | Deterministically computed from `3_*` and `4_*` (no manual override); null if Gate 1, 2, or unwaived Gate 3 fails |
| `4n` | `gate_4n_runway_note` | String | Mandatory when any `4_* >= 1`; null if Gate 1, 2, or unwaived Gate 3 fails |
| `5` | `gate_5_management_score` | `0`, `1`, `2` | Null if Gate 1, 2, unwaived 3, or 4 fails |
| `6` | `gate_6_cash_and_balance_sheet` | `"Y"`, `"N"` | Null if Gate 1, 2, unwaived 3, 4, or unwaived 5 fails |
| `calamity` | `calamity_flag` | `"Y"`, null | Set `"Y"` only when Anchor Gates `1,2,3a,4` pass and failure is solely in `{3b, 5, 6}` |
| `calamity_note` | `calamity_note` | String, null | Mandatory when `calamity_flag == "Y"` (broken metric, moat proof, catalyst + kill-switch); else null |
| `note` | `note` | String | Mandatory summary text (include `[5-10Y g: ...]` for both `Quality pass` and `Calamity pass`) |
| `evidence` | `evidence` | String | Mandatory empirical evidence |

---

## 6. Ingestion via `screener/apply_evaluation.py`

When the agent returns this JSON payload, apply it directly to `data/<universe>/inputs.csv`:
```bash
python3 screener/apply_evaluation.py --input qualitative_result.json
```
The script validates the waterfall, strips illegal downstream values if any gate failed, updates `inputs.csv`, and reports the diff.
