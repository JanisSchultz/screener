# Per-Company Evaluation Framework Specification (v6.23)
## Quality & Moat Screener — 6 Munger Quality Gates & Equity Bond Below PAR

---

## 1. Overview & Evaluator Mandate

This specification defines the complete, rigorous end-to-end evaluation framework for analyzing individual public companies within the **Quality & Moat Screener (v6.23)**.

### The Evaluator Agent's Core Mindset
As an independent evaluator agent, your role is that of an uncompromising, disciplined superinvestor operating strictly under the principles of **Charlie Munger** and **Warren Buffett**:
> *"Tell me where I am going to die, that is, so I don't go there."* — Charlie Munger

1. **Default Stance is Rejection**: The global investment universe contains tens of thousands of equities, but fewer than ~250 companies worldwide possess the enduring economic moats, capital allocation discipline, and balance sheet resilience required to qualify as true long-term compounders. You do not search for reasons to include a company; you actively search for the structural flaw that eliminates it.
2. **Sequential Waterfall Invariant (with Conditional Calamity Tier on Gates 3b, 5 & 6 Only)**: The qualitative framework consists of **6 sequential reject gates**. Evaluation proceeds strictly in order (Gate 1 $\rightarrow$ Gate 6). Normally, at the first gate a company fails, it is immediately rejected and downstream fields are left blank/null. **Buffett Calamity Exception**: if Anchor Gates `1="Y"`, `2="Y"`, `3a!="None"`, and `4>=15` all pass and failure is strictly in Gates `3b`, `5`, and/or `6` due to a temporary, fixable calamity, keep the true failed gate value(s), set `calamity_flag: "Y"` with a structured `calamity_note` (broken metric + intact moat proof + fix catalyst & kill-switch), and evaluate all remaining downstream gates so the stock enters Quantitative valuation as **`Calamity pass`**.
3. **Evidence Over Narrative**: Assertions must be anchored in empirical financial reality: multi-cycle ROIC, free cash flow conversion, pricing history, competitive dynamics, and balance sheet endurance through crises.

---

## 2. Input Context Provided to the Evaluator Agent

When the coordinator agent delegates a company for evaluation, it will provide the following baseline inputs:

### 2.1 Identifiers & Classification
- `id`: Internal unique identifier (e.g. `MSFT`, `NESN.CH`, `CNR.CA`).
- `ticker`: Trading ticker (e.g. `MSFT`, `NESN`, `CNR`).
- `company`: Official company name.
- `country`: Country of primary listing / headquarters.
- `sector`: GICS Sector.
- `sub_industry`: GICS Sub-industry.
- `universe`: `us` (Nasdaq-100 / S&P 500), `eu` (STOXX Europe 600), or `ca` (S&P/TSX 60).

### 2.2 Pre-Screen Context
- `in_market`: `Y` or `N`. Whether the company's listing country is an approved rule-of-law Western developed market.
- `g6_default`: `N` or blank. Sub-industry default for Gate 6 (regulated utilities and deposit-taking commercial banks default to `N`).

### 2.3 Financial & Fundamental Context (Multi-Year History)
- **Share Price & Valuation**: Current share price, reporting currency, quote currency, market capitalization.
- **Earnings & Cash Flow**: 5–10 years of Net Income, CapEx, Depreciation & Amortization (D&A), Dividends, Operating Cash Flow (OCF), and Free Cash Flow (FCF).
- **Capital Structure**: Long-Term Debt, Total Cash & Equivalents, Interest Expense, EBIT, Interest Coverage (`EBIT / Interest`).
- **Return on Capital**: 5-Year Median GAAP ROIC (including goodwill), 5-Year Median Operating ROIC (NOPAT ÷ Net Tangible Invested Capital), and Incremental ROIIC.
- **Historical Cycle Multiples**: 5-Year Cycle Low Multiple (`mult_low_5y`) and Cycle High Multiple (`mult_high_5y`) relative to peak Owner EPS.
- **Earnings Compounding**: Cycle Owner EPS CAGR (`cagr_oe_eps`), Peak Owner EPS (`peak_oe_eps`), and peak-to-peak status (`p2p_ok`).

---

## 3. The 6 Sequential Munger Reject Gates (Qualitative Rubric)

Evaluation must execute strictly in sequence. The first failed gate triggers an immediate reject verdict.

```
Gate 1: Simple to Understand
  │ [Pass: Y]
  ▼
Gate 2: Essential Western Need & Entrenched Habits ('Likely To' Standard)
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
QUALITY PASS (Enters Quantitative PAR Valuation Funnel)
```

---

### Gate 1: Simple to Understand
- **Code**: `1`
- **Output Type**: Gate (`Y` / `N`)
- **Core Principle**: Circle of competence and external verifiability. Favors established, transparent business models with long public operating histories over opaque, complex, or unproven models.
- **Pass Standard (`Y`)**:
  - The core economic engine is established and straightforward to analyze.
  - Financial statements accurately reflect the primary business risks without hidden off-balance-sheet structures.
  - Conventional holding companies, transparent banks, and standard insurers pass if their balance sheets and investment portfolios are verifiable from the outside.
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
Gate 3 establishes that a structural economic moat exists and produces demonstrable excess returns on capital before evaluating how long it will last (Gate 4).

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
  - Must have a verified moat archetype (`3a != "None"`).
  - **Proof of Moat**: Empirically verified by historical capital efficiency: **5-Year Median GAAP ROIC $\ge$ 12%** AND **Incremental ROIIC $\ge$ 12%** across the business cycle. (Operating companies failing both tangible ROIC $\ge$ 15% and GAAP ROIC $\ge$ 12% are automatically rejected).
  - **Pricing Power $\ge$ Inflation**: Demonstrated ability to raise prices at or above inflation across the cycle without losing customer volume or market share (e.g. basis-point ad valorem toll booths, CPI-indexed concession contracts, inelastic mission-critical workflows).
  - *Look-Through Holding Companies*: Evaluated on look-through portfolio operating moats and look-through pricing power.
- **Reject Standard (`N`)**:
  - Moat is `None`.
  - Commodity price-taker whose margins fluctuate with spot commodity prices.
  - Sub-hurdle historical returns on capital (ROIC < 12%).
  - Government price caps, utility rate freezes, or customer churn upon price hikes indicating zero pricing power.
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

Every evaluation must provide rigorous, standardized documentation in the `note` and `evidence` fields:

### 4.1 The `note` Field (Summary Verdict & 5–10Y Growth Engine)
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

### 4.2 The `evidence` Field (Empirical Background & History)
Provide a comprehensive synthesis including:
- Multi-cycle financial track record (historical ROIC, operating margin trends, cash conversion).
- Segment revenue and profit breakdowns.
- Key customer lock-in mechanisms and empirical proof of pricing power.
- Historical M&A record, capital allocation behavior, and debt repayment history.

---

## 5. Quantitative Evaluation: Equity Bond Below PAR Model (v6.26)

> **Important**: Quantitative PAR valuation is evaluated for companies achieving **`Quality pass`** across all 6 gates, as well as **`Calamity pass`** candidates (conditional waiver on Gates 3b, 5, and/or 6). Rejected companies are designated `"Not in funnel"` for quantitative valuation. For `Calamity pass` companies, verify whether normalized earning power (`peak_eps_est`) or forward growth (`g_est` / `g_implied`) requires an explicit adjustment.

The Equity Bond Below PAR model treats high-quality compounders as equity bonds paying an expanding owner cash coupon. It calculates fair through-the-cycle value (PAR Value) based on three fundamental pillars.

---

### 5.1 Core Valuation Inputs

1. **Owner EPS**:
   $$\text{Owner EPS} = \frac{\text{Net Income} + \max(0, \text{D\&A} - \text{CapEx})}{\text{Diluted Shares}}$$
   *One-off non-cash earnings spikes (disposal gains, hedge marks, tax allowances) are stripped out.*
2. **Peak Owner EPS**:
   - `peak_oe_eps`: The highest Owner EPS achieved over the last 5 fiscal years (converted to quote currency).
   - `peak_eps_est`: Analyst override for Peak Owner EPS if the reported peak contains unrepeatable windfalls or pre-spin-off distortions.
   - **Active Peak EPS**: Use `peak_eps_est` if populated, otherwise `peak_oe_eps`.
3. **5-Year Historical Cycle Multiples**:
   - `mult_low_5y`: 5-year cycle low multiple (median of yearly lows).
   - `mult_high_5y`: 5-year cycle high multiple (median of yearly highs).
   - `Cycle Midpoint Multiple`: $\text{t\_hist} = 0.5 \times (\text{mult\_low\_5y} + \text{mult\_high\_5y})$.

---

### 5.2 Operating ROIC Normalization (v6.23 Standard)

To prevent accounting distortions from penalizing capital-light compounders that completed strategic M&A:
1. **GAAP ROIC vs Operating ROIC**:
   - GAAP ROIC includes accumulated goodwill and acquired intangibles in the denominator, severely understating ongoing operating quality (e.g. S&P Global's IHS Markit acquisition added \$52.8B of goodwill, depressing GAAP ROIC to 11.8%).
   - **Operating ROIC (Tangible Capital Return)**:
     $$\text{Operating ROIC} = \frac{\text{NOPAT}}{\text{Tangible Invested Capital}} = \frac{\text{NOPAT}}{\text{Equity} + \text{Debt} - \text{Cash} - \text{Goodwill} - \text{Intangibles}}$$
2. **Negative Tangible Capital Standard**:
   - Pure asset-light monopolies operating on negative net working capital and deferred customer subscription revenues earn structurally unbounded returns on tangible capital. They automatically receive the maximum cap: `par_roic_cap = 35.0%`.
3. **Active ROIC**:
   - Use `roic_est` (override) if provided; else `roic_operating` (tangible) if available; else `roic_median` (GAAP).
   - Multiple ROIC Contribution:
     $$\text{t\_roic} = \min(\text{Active ROIC} \times 100, 35.0)$$

---

### 5.3 Expected Growth Engine ($g_{\text{exp}}$) & Gate 4 CAP-Linked Persistence

Grounded in Michael Mauboussin and Dan Callahan's 75-year empirical growth persistence research (Counterpoint Global):
1. **Growth Parameters**:
   - `par_g_base = 0.07` (7.0% mature large-cap base rate anchor).
   - `par_g_cap = 0.12` (12.0% empirical ceiling for through-the-cycle large-cap EPS growth).
2. **Gate 4 CAP-Linked Growth Persistence ($\lambda$)**:
   - **CAP $\ge$ 30 Years** (Fortress Moats & Secular Monopolies: SPGI, MCO, MSFT, V): $\lambda = 0.25$.
   - **CAP $\ge$ 20 Years** (Standard Quality Compounders: OTIS, ZTS, CPRT): $\lambda = 0.15$.
   - **CAP $\ge$ 15 Years** (Shorter Runway / Higher Transition Risk): $\lambda = 0.10$.
   - **Fallback / Unpopulated**: $\lambda = 0.15$.
3. **Growth Hierarchy**:
   - If analyst override `g_est` is populated $\rightarrow g_{\text{exp}} = g_{\text{est}}$.
   - Else if bottom-up estimate `g_implied` (or `g_exp`) is populated $\rightarrow g_{\text{exp}} = \min(\text{par\_g\_cap}, g_{\text{implied}})$.
   - Else apply the **Mauboussin CAP-Linked Fade Formula** to historical cycle CAGR $g$:
     $$g_{\text{exp}} = \min\left(0.12, \max\left(0.02, \lambda \times (\max(0, g) - 0.07) + 0.07\right)\right)$$
   - Fallback: $g_{\text{exp}} = 0.07$ (7.0%).

---

### 5.4 3-Pillar Fundamental PAR Multiple & Cycle High Guardrail

The fundamental fair value multiple is governed by three equal pillars:
1. **Pillar 1: Secular Growth Factor**: $\text{t\_growth} = \min(40.0, 200.0 \times \max(0, g_{\text{exp}}))$. *(Adds $+16$ to $+24$ turns for 8%–12% compounders).*
2. **Pillar 2: Historical Cycle Midpoint Multiple**: $\text{t\_hist} = 0.5 \times (\text{mult\_low\_5y} + \text{mult\_high\_5y})$.
3. **Pillar 3: Operating ROIC Factor**: $\text{t\_roic} = \min(\text{Active ROIC} \times 100, 35.0)$.

$$\text{Raw PAR Multiple} = \frac{\text{t\_growth} + \text{t\_hist} + \text{t\_roic}}{3}$$

#### The 5-Year Cycle High Guardrail
A core tenet of value investing: through-the-cycle fair value can **never** exceed the highest multiple the market was willing to pay at the peak of the 5-year cycle:
$$\text{PAR Multiple} = \min(\text{Raw PAR Multiple}, \text{mult\_high\_5y})$$

---

### 5.5 Valuation Metrics & Status

1. **PAR Value**:
   $$\text{PAR Value} = \text{PAR Multiple} \times \text{Active Peak Owner EPS}$$
2. **Current Multiple**:
   $$\text{Current Multiple} = \frac{\text{Current Share Price}}{\text{Active Peak Owner EPS}}$$
3. **% vs PAR**:
   $$\% \text{ vs PAR} = \frac{\text{Current Share Price}}{\text{PAR Value}} - 1.0$$
   - **Valuation Status**:
     - `Below PAR`: Current Price $\le$ PAR Value ($\% \text{ vs PAR} \le 0$). **BUYING OPPORTUNITY**.
     - `Above PAR`: Current Price $>$ PAR Value ($\% \text{ vs PAR} > 0$). **OVERVALUED**.
4. **5-Year Expected Cycle IRR (Pull-to-PAR)**:
   $$\text{5Y Expected IRR} = (1 + g_{\text{imp}}) \times \left(\frac{\text{PAR Value}}{\text{Current Share Price}}\right)^{0.2} + \text{Dividend Yield} - 1.0$$
5. **Market-Implied Growth ($g_{\text{market}}$) & Growth Margin of Safety**:
   - Inversion of the 3-Pillar PAR Multiple formula reveals the growth rate priced into the current market multiple:
     $$g_{\text{market}} = \frac{3 \times \text{Current Multiple} - \text{t\_hist} - \text{t\_roic}}{200}$$
   - **Growth Margin of Safety**:
     $$\text{Growth Margin} = g_{\text{imp}} - g_{\text{market}}$$
6. **Market-Implied CAP & Moat Runway Margin**:
   - Years of competitive advantage priced into the current stock price:
     $$\text{Market-Implied CAP} = \text{Fundamental CAP} \times \frac{\text{Current Share Price}}{\text{PAR Value}}$$
   - **Moat Runway Margin**:
     $$\text{Moat Margin} = \text{Fundamental CAP} - \text{Market-Implied CAP}$$

---

## 6. Output Contract: Standardized JSON Result Format

When the independent agent completes an evaluation, it must return a strictly validated JSON payload matching this exact schema:

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
    "calamity_flag": null,
    "calamity_note": null,
    "note": "Indispensable enterprise software and cloud oligopolist. Pricing power demonstrated by repeated price hikes with zero churn. $80B+ net cash balance sheet. [5-10Y g: cloud volume 6.5% + enterprise price 2.0% - AI GPU capex D&A drag 0.5% + net buyback 1.0%]",
    "evidence": "30%+ Operating ROIC over 10 years. FCF conversion >100%. Azure and Office 365 form an indispensable productivity layer for modern enterprise."
  },
  "quantitative_overrides": {
    "peak_eps_est": null,
    "g_est": null,
    "g_implied": 0.09,
    "roic_est": null,
    "fin_note": "5-10Y g anchored in cloud volume and enterprise price expansion."
  },
  "evaluation_metadata": {
    "verdict": "Quality pass",
    "failing_gate": null,
    "evaluated_at": "2026-11-09T19:50:00Z",
    "evaluator": "independent-agent"
  }
}
```

### Schema Rules & Field Mapping Table

| CSV Field | JSON Key (`qualitative`) | Allowed Values | Nullable Rules |
| :--- | :--- | :--- | :--- |
| `1` | `gate_1` | `"Y"`, `"N"` | Never null |
| `2` | `gate_2` | `"Y"`, `"N"` | Null if Gate 1 is `"N"` |
| `2r` | `gate_2_reason` | String | Populated only if `gate_2 == "N"`, else null |
| `3a` | `gate_3a_moat_archetype` | `"Toll booth / Switching costs"`, `"Scale economies shared"`, `"Irreplaceable infrastructure"`, `"R&D super-thinkers / Intangibles"`, `"None"` | Null if Gate 1 or 2 is `"N"` |
| `3b` | `gate_3b_pricing_and_proof` | `"Y"`, `"N"` | Null if Gate 1 or 2 is `"N"` |
| `3m` | `gate_3m_moat_note` | String | Null if Gate 1 or 2 is `"N"` |
| `4` | `gate_4_runway_cap` | `0`, `5`, `10`, `15`, `20`, `30` | Null if Gate 1, 2, or (3a=`"None"` / unwaived 3b=`"N"`) fails |
| `5` | `gate_5_management_score` | `0`, `1`, `2` | Null if Gate 1, 2, unwaived 3, or 4 fails |
| `6` | `gate_6_cash_and_balance_sheet` | `"Y"`, `"N"` | Null if Gate 1, 2, unwaived 3, 4, or unwaived 5 fails |
| `calamity` | `calamity_flag` | `"Y"`, null | Set `"Y"` only when Anchor Gates `1,2,3a,4` pass and failure is solely in `{3b, 5, 6}` |
| `calamity_note` | `calamity_note` | String, null | Mandatory if `calamity_flag == "Y"` (broken metric, moat proof, fix catalyst + kill-switch); else null |
| `note` | `note` | String | Mandatory summary text |
| `evidence` | `evidence` | String | Mandatory empirical evidence |

#### `quantitative_overrides` Object (for `Quality pass` and `Calamity pass`)
- `peak_eps_est`: Float or null.
- `g_est`: Float (e.g. `0.095` for 9.5%) or null.
- `g_implied`: Float (e.g. `0.10` for 10.0%) or null.
- `roic_est`: Float (e.g. `0.35` for 35.0%) or null.
- `fin_note`: String or null.

---

## 7. Concrete Worked Examples

### Example 1: Quality Pass Compounder (Visa Inc. `V`)
```json
{
  "id": "V",
  "ticker": "V",
  "universe": "us",
  "company": "Visa Inc.",
  "country": "United States",
  "sector": "Financials",
  "sub_industry": "Transaction & Payment Processing Services",
  "qualitative": {
    "gate_1": "Y",
    "gate_2": "Y",
    "gate_2_reason": null,
    "gate_3a_moat_archetype": "Toll booth / Switching costs",
    "gate_3b_pricing_and_proof": "Y",
    "gate_3m_moat_note": "Supreme pricing power: charges basis points on gross nominal dollar volume; price increases flow directly to operating profit with zero incremental capital required.",
    "gate_4_runway_cap": 20,
    "gate_5_management_score": 2,
    "gate_6_cash_and_balance_sheet": "Y",
    "note": "Passes all 6 gates. The ultimate electronic payment toll booth with 67% operating margins, zero credit risk, and perpetual owner earnings compounding. Balance sheet fortress with net cash/minimal debt. [5-10Y g: payments volume 6% + cross-border travel 2% + value-added services (cyber/fraud) 2% + buyback 1% - credit card competition act drag 1%]",
    "evidence": "10-year average GAAP ROIC exceeds 45%. Free cash flow conversion consistently 100%+. Duopoly with Mastercard processes over $14 trillion in annual volume. Network effects across 4 billion credentials and 100 million merchants."
  },
  "quantitative_overrides": {
    "peak_eps_est": null,
    "g_est": null,
    "g_implied": 0.10,
    "roic_est": 0.35,
    "fin_note": "5-10Y g anchored in global nominal PCE growth, cross-border recovery, and value-added services."
  },
  "evaluation_metadata": {
    "verdict": "Quality pass",
    "failing_gate": null,
    "evaluated_at": "2026-11-09T19:50:00Z",
    "evaluator": "independent-agent"
  }
}
```

---

### Example 2: Gate 2 Rejection (Cruise Operator `CCL`)
```json
{
  "id": "CCL",
  "ticker": "CCL",
  "universe": "us",
  "company": "Carnival Corporation & plc",
  "country": "United States",
  "sector": "Consumer Discretionary",
  "sub_industry": "Hotels, Restaurants & Leisure",
  "qualitative": {
    "gate_1": "Y",
    "gate_2": "N",
    "gate_2_reason": "Discretionary big-ticket vacation purchase easily deferred or cancelled during economic downturns.",
    "gate_3a_moat_archetype": null,
    "gate_3b_pricing_and_proof": null,
    "gate_3m_moat_note": null,
    "gate_4_runway_cap": null,
    "gate_5_management_score": null,
    "gate_6_cash_and_balance_sheet": null,
    "note": "Fails Gate 2 (REJECT). Discretionary big-ticket leisure purchase with high cyclicality, immense fixed vessel capital costs, and fuel exposure. Downstream gates bypassed per waterfall.",
    "evidence": "Revenues collapsed over 70% during the pandemic, forcing billions in dilutive equity issuance and high-yield debt to stay afloat. Negative free cash flow in downturns."
  },
  "quantitative_overrides": {},
  "evaluation_metadata": {
    "verdict": "Rejected – G2 Essential Need",
    "failing_gate": "Gate 2",
    "evaluated_at": "2026-11-09T19:50:00Z",
    "evaluator": "independent-agent"
  }
}
```

---

### Example 3: Gate 3b Rejection (Steel Producer `NUE`)
```json
{
  "id": "NUE",
  "ticker": "NUE",
  "universe": "us",
  "company": "Nucor Corporation",
  "country": "United States",
  "sector": "Materials",
  "sub_industry": "Steel",
  "qualitative": {
    "gate_1": "Y",
    "gate_2": "Y",
    "gate_2_reason": null,
    "gate_3a_moat_archetype": "None",
    "gate_3b_pricing_and_proof": "N",
    "gate_3m_moat_note": "Commodity price taker. Although Nucor is the low-cost EAF mini-mill operator, hot-rolled coil prices are set by global marginal production costs.",
    "gate_4_runway_cap": null,
    "gate_5_management_score": null,
    "gate_6_cash_and_balance_sheet": null,
    "note": "Fails Gate 3 (REJECT). Commodity price-taker lacking pricing power above inflation over the complete cycle. Downstream gates bypassed per waterfall.",
    "evidence": "Operating margins swing from +35% at cycle peaks to near-zero or negative in troughs. Historical through-the-cycle GAAP ROIC averages 8-11%, failing the 12% hurdle."
  },
  "quantitative_overrides": {},
  "evaluation_metadata": {
    "verdict": "Rejected – G3 Moat & Pricing",
    "failing_gate": "Gate 3",
    "evaluated_at": "2026-11-09T19:50:00Z",
    "evaluator": "independent-agent"
  }
}
```

---

### Example 4: Gate 4 Rejection (Seat-Based SaaS `CRM`)
```json
{
  "id": "CRM",
  "ticker": "CRM",
  "universe": "us",
  "company": "Salesforce Inc.",
  "country": "United States",
  "sector": "Information Technology",
  "sub_industry": "Application Software",
  "qualitative": {
    "gate_1": "Y",
    "gate_2": "Y",
    "gate_2_reason": null,
    "gate_3a_moat_archetype": "Toll booth / Switching costs",
    "gate_3b_pricing_and_proof": "Y",
    "gate_3m_moat_note": "High enterprise switching costs in core Sales/Service Cloud, but seat monetization vulnerable.",
    "gate_4_runway_cap": 10,
    "gate_5_management_score": null,
    "gate_6_cash_and_balance_sheet": null,
    "note": "Fails Gate 4 (CAP = 10, REJECT). Capped at CAP 10 under Macrotrend #1 (Automation & Cognitive Tech): core seat-based pricing model faces structural deflation as AI agents reduce corporate sales/support headcounts.",
    "evidence": "Organic growth slowed from 25%+ to high single digits. Customer IT budgets shifting to generative AI infrastructure. Agentforce is nascent while core seat growth stalls."
  },
  "quantitative_overrides": {},
  "evaluation_metadata": {
    "verdict": "Rejected – G4 Runway (<15Y)",
    "failing_gate": "Gate 4",
    "evaluated_at": "2026-11-09T19:50:00Z",
    "evaluator": "independent-agent"
  }
}
```

---

### Example 5: Gate 6 Rejection (Financial Engineering `MSCI`)
```json
{
  "id": "MSCI",
  "ticker": "MSCI",
  "universe": "us",
  "company": "MSCI Inc.",
  "country": "United States",
  "sector": "Financials",
  "sub_industry": "Financial Exchanges & Data",
  "qualitative": {
    "gate_1": "Y",
    "gate_2": "Y",
    "gate_2_reason": null,
    "gate_3a_moat_archetype": "Toll booth / Switching costs",
    "gate_3b_pricing_and_proof": "Y",
    "gate_3m_moat_note": "AUM-linked global benchmark index toll booth with 95%+ client retention and supreme pricing power.",
    "gate_4_runway_cap": 20,
    "gate_5_management_score": 1,
    "gate_6_cash_and_balance_sheet": "N",
    "note": "Fails Gate 6 (REJECT). While the index toll booth is world-class, the balance sheet has been compromised by financial engineering: $4.5B+ in long-term debt funded share repurchases at 40-50x earnings, resulting in negative stockholders' equity (-$800M) and Net Debt > 4.5x Owner Earnings.",
    "evidence": "Negative book equity of -$820M. Total debt of $4.5B represents over 4.5 years of normalized net income, violating the peace-of-mind fortress standard."
  },
  "quantitative_overrides": {},
  "evaluation_metadata": {
    "verdict": "Rejected – G6 Cash & Fortress Balance Sheet",
    "failing_gate": "Gate 6",
    "evaluated_at": "2026-11-09T19:50:00Z",
    "evaluator": "independent-agent"
  }
}
```

---

## 8. Handoff & Update Protocol for the Coordinator Agent

When the independent agent hands back the JSON evaluation payload, the coordinator agent or user performs the following steps:

### Step 1: Validate Payload & Invariants
Run the automated companion ingestion tool `screener/apply_evaluation.py` to validate and apply the results:
```bash
python3 screener/apply_evaluation.py --input path/to/result.json
```

The script verifies:
1. All required fields are present.
2. The waterfall invariant is respected (e.g. if Gate 2 failed, Gates 3–6 must be null).
3. If Quality Pass, Gate 4 $\ge 15$, Gate 5 $\ge 1$, and Gates 1, 2, 3b, 6 are `"Y"`.
4. Overrides in `quantitative_overrides` match supported formats.

### Step 2: Apply Updates to Datasets
`screener/apply_evaluation.py` automatically updates:
- `data/<universe>/inputs.csv`: updates columns `1`, `2`, `2r`, `3a`, `3b`, `3m`, `4`, `5`, `6`, `calamity`, `calamity_note`, `note`, `evidence`.
- `data/<universe>/financials.csv`: updates columns `peak_eps_est`, `g_est`, `g_implied`, `roic_est`, `fin_note` (if provided).

### Step 3: Rebuild HTML Cockpit
After updating, compile the standalone HTML cockpit (`output/screener.html`, `output/index.html`, `docs/index.html`):
```bash
python3 build.py
```
The newly evaluated company will immediately reflect its updated status across `★ Below PAR Shortlist`, `🛡️ Quality Pass Funnel`, `⚠️ Calamity Watchlist`, and `🔍 Full Universe & Waterfall`.
