# Qualitative Evaluation Framework Specification (v6.23)
## Quality & Moat Screener — 6 Sequential Munger Reject Gates

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent qualitative screening** of individual public companies within the Quality & Moat Screener (v6.23). It can be executed entirely standalone by an AI agent to determine whether a company qualifies as a world-class compounder.

### The Evaluator Agent's Core Mindset
As an independent qualitative evaluator agent, your mandate is inspired by **Charlie Munger** and **Warren Buffett**:
> *"Tell me where I am going to die, that is, so I don't go there."* — Charlie Munger

1. **Default Stance is Rejection**: Fewer than ~250 companies across the US, European, and Canadian large-cap universes possess the enduring business quality required to compound capital over decades. You do not search for reasons to include a company; you actively hunt for the fatal flaw that eliminates it.
2. **Strict Sequential Waterfall Invariant**: The qualitative framework consists of **6 sequential reject gates**. Evaluation proceeds strictly in order (Gate 1 $\rightarrow$ Gate 6). **At the first gate a company fails, it is immediately rejected and removed from the quality funnel.** Downstream gate evaluations are immediately terminated, and their corresponding fields are left blank/null to maintain analytical integrity.
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

### Gate 3: Strong Moat & Pricing Power >= Inflation
Gate 3 diagnoses Moat Existence, Proof of Moat, and Pricing Power *before* evaluating longevity in Gate 4.

#### Gate 3a: Primary Moat Archetype
- **Code**: `3a`
- **Output Type**: Categorical choice (exact string from the following 5 options):
  1. `Toll booth / Switching costs`: Network effects, high customer switching barriers, mission-critical software/data workflow lock-in (e.g. Visa, Mastercard, Microsoft, S&P Global).
  2. `Scale economies shared`: Nick Sleep / Costco / Amazon model; passing operational scale efficiencies back to customers to build an insurmountable cost advantage (e.g. Costco, Geico).
  3. `Irreplaceable infrastructure`: Physically unreplicable assets with high barriers to entry (e.g. permitted solid waste landfills, transcontinental freight rails, deep-water port terminals).
  4. `R&D super-thinkers / Intangibles`: Deep proprietary patent estates, regulatory licenses, mission-critical engineering know-how, or Lindy brand power (e.g. ASML, Danaher, Hermès).
  5. `None`: Commodity business, fragmented competition, or lack of defensible barriers.

#### Gate 3b: Pricing Power & Proof of Moat
- **Code**: `3b`
- **Output Type**: Gate (`Y` / `N`)
- **Pass Standard (`Y`)**:
  - Must have a verified structural moat archetype (`3a != "None"`).
  - **Proof of Moat**: Empirically verified by historical capital efficiency: **5-Year Median GAAP ROIC $\ge$ 12%** AND **Incremental ROIIC $\ge$ 12%** across the business cycle. (Operating companies failing both tangible ROIC $\ge$ 15% and GAAP ROIC $\ge$ 12% are automatically rejected).
  - **Pricing Power $\ge$ Inflation**: Demonstrated ability to raise prices at or above inflation across the cycle without losing customer volume or market share (e.g. basis-point ad valorem toll booths, CPI-indexed concession contracts, inelastic mission-critical workflows).
  - *Look-Through Holding Companies*: Evaluated on look-through portfolio operating moats and look-through pricing power.
- **Reject Standard (`N`)**:
  - Moat archetype is `None`.
  - Commodity price-taker whose margins fluctuate with spot commodity prices.
  - Sub-hurdle historical returns on capital (ROIC < 12%).
  - State price caps, utility rate freezes, or customer churn upon price hikes indicating zero pricing power.
- **Moat & Erosion Note (`3m`)**:
  - Required text summarizing: (1) what prevents competitors from arbitraging away returns, (2) empirical proof of moat (ROIC, gross margin stability), and (3) primary erosion threats.
- **Waterfall Action**: If `3a == "None"` or `3b == "N"`, set `result = "Rejected – G3 Moat & Pricing"`. Leave Gates 4–6 completely blank/null.

---

### Gate 4: Low Disruption Risk & Predictable Runway (15+ Years)
- **Code**: `4`
- **Output Type**: Number: `0`, `5`, `10`, `15`, `20`, or `30` (Competitive Advantage Period — CAP, in years).
- **Threshold**: `thr_cap = 15`. A CAP score $< 15$ is an immediate **REJECT**.

#### The Two-Step Mauboussin & Callahan Engine
Evaluates structural longevity using Michael Mauboussin & Dan Callahan's empirical persistence research (1970–2024, Counterpoint Global):

1. **Step 1: Outside View (Industry Base-Rate Persistence Anchor)**:
   - **Tier 1 (Persistence $p=0.90$, Fade $f=0.10$) $\rightarrow$ Baseline CAP: 20–30 Years**:
     - Consumer Staples, Food & Beverage, Household & Personal Care, Lindy Luxury.
   - **Tier 2 (Persistence $p=0.81\text{–}0.87$, Fade $f=0.13\text{–}0.19$) $\rightarrow$ Baseline CAP: 15–20 Years**:
     - Medical Devices / MedTech, Mission-Critical Tech Hardware, Testing/Inspection/Certification, Niche B2B Services.
   - **Tier 3 (Persistence $p=0.75\text{–}0.79$, Fade $f=0.21\text{–}0.25$) $\rightarrow$ Baseline CAP: 10–15 Years**:
     - Enterprise Software & IT Services, Pharmaceuticals / Biotechnology, Semiconductors, Capital Goods, Freight Rails.
   - **Tier 4 (Persistence $p=0.70\text{–}0.71$, Fade $f=0.29\text{–}0.30$) $\rightarrow$ Baseline CAP: 5–10 Years (Natural REJECT)**:
     - Upstream Energy, Telecom Carriers, Traditional Regulated Utilities.

2. **Step 2: Inside View (5-Macrotrend Deductive Haircut Filter)**:
   Deduct **$-5$ to $-10$ years** from the industry baseline if the business faces an active, unhedged terminal headwind on any of the 5 Macrotrends:
   - **[1] Automation & Cognitive Tech (AI Disruption)**:
     - *Fatal Headwind*: Seat-based SaaS models vulnerable to agentic headcount reduction; billable-hour IT consulting/staffing; routine data aggregation/lookup services. Capped at $\text{CAP} \le 10$ (REJECT).
     - *Beneficiary / Insulated*: Full-stack vertically integrated AI hegemons owning proprietary infrastructure, models, and distribution (e.g. Alphabet, Microsoft); businesses operating entirely in the physical world (landfills, railways, plumbing distribution).
   - **[2] Demographic Aging & Labor Scarcity**: Heavy reliance on low-cost manual labor without automation potential.
   - **[3] Geopolitical Realignment & Supply Chain Reshoring**: Vulnerability to single-source foreign manufacturing (e.g. Taiwan/China foundry concentration) or cross-border trade embargoes.
   - **[4] Energy Transition & Resource Limits**: Carbon-heavy operating profiles, grid interconnect bottlenecks, or heavy stranded-asset risk.
   - **[5] Structural Inflation & Cost of Capital**: Capital-intensive businesses requiring frequent refinancing at higher interest rates unable to pass through real cost increases.

- **The Rule of Secular Resilience**: To achieve $\text{CAP} \ge 15$, the business must be an active beneficiary of, or structurally insulated from (indifferent to), all 5 macrotrends. An active terminal headwind on *any* single pillar caps $\text{CAP} \le 10$ (**REJECT**).
- **Waterfall Action**: If `4 < 15`, set `result = "Rejected – G4 Runway (<15Y)"`. Leave Gates 5–6 completely blank/null.

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
    "gate_3a_moat_archetype": "Toll booth / Switching costs",
    "gate_3b_pricing_and_proof": "Y",
    "gate_3m_moat_note": "Extreme enterprise switching costs proved by repeated 9-15% M365 E3/E5 price hikes and Copilot tiering with near-zero churn.",
    "gate_4_runway_cap": 20,
    "gate_5_management_score": 1,
    "gate_6_cash_and_balance_sheet": "Y",
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
| `3a` | `gate_3a_moat_archetype` | `"Toll booth / Switching costs"`, `"Scale economies shared"`, `"Irreplaceable infrastructure"`, `"R&D super-thinkers / Intangibles"`, `"None"` | Null if Gate 1 or 2 is `"N"` |
| `3b` | `gate_3b_pricing_and_proof` | `"Y"`, `"N"` | Null if Gate 1 or 2 is `"N"` |
| `3m` | `gate_3m_moat_note` | String | Null if Gate 1 or 2 is `"N"` |
| `4` | `gate_4_runway_cap` | `0`, `5`, `10`, `15`, `20`, `30` | Null if Gate 1, 2, or 3 fails |
| `5` | `gate_5_management_score` | `0`, `1`, `2` | Null if Gate 1, 2, 3, or 4 fails |
| `6` | `gate_6_cash_and_balance_sheet` | `"Y"`, `"N"` | Null if Gate 1, 2, 3, 4, or 5 fails |
| `note` | `note` | String | Mandatory summary text |
| `evidence` | `evidence` | String | Mandatory empirical evidence |

---

## 6. Ingestion via `screener/apply_evaluation.py`

When the agent returns this JSON payload, apply it directly to `data/<universe>/inputs.csv`:
```bash
python3 screener/apply_evaluation.py --input qualitative_result.json
```
The script validates the waterfall, strips illegal downstream values if any gate failed, updates `inputs.csv`, and reports the diff.
