# Per-Company Evaluation Framework Specification (v7.1)
## Quality & Moat Screener — 6 Munger Quality Gates & Explicit Mauboussin-Fade DCF

---

## 1. Overview & Evaluator Mandate

This specification defines the complete, rigorous end-to-end evaluation framework for analyzing individual public companies within the **Quality & Moat Screener (v7.1)**.

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

## 5. Quantitative Evaluation: Sure & Simple Explicit Mauboussin-Fade DCF & Bellman-Consistent 5Y IRR (v7.1)

> **Important**: Quantitative valuation is evaluated for companies achieving **`Quality pass`** across all 6 gates, as well as **`Calamity pass`** candidates (conditional waiver on Gates 3b, 5, and/or 6). Rejected companies are designated `"Not in funnel"` for quantitative valuation. Since v7.6 the quantitative valuation takes **no analyst overrides**: every input comes from the statements, and data that cannot support a per-share valuation is shown as **No data** with an `[auto]` reason. An evaluator supplies only the qualitative gates.

The v7.1 valuation model identifies **Slump-Cannibal Compounders** — world-class businesses experiencing a temporary 1-year growth slump (`sales_1y`) while their structural cost-bloat guarded growth ceiling (`g_org_exp`) remains intact — using a **Miller–Modigliani Zero-Spread Invariant Explicit $N$-Year Mauboussin-Fade DCF** at discount rate $r = 8.50\%$ ($r_{\text{fin}} = 10.25\%$ for Balance-Sheet Financials) and a **Bellman-Consistent 5-Year Expected IRR** (`irr_5y`).

---

### 5.1 Core Valuation Inputs

1. **Owner EPS & IFRS-16 Lease Deduction**:
   $$\text{Owner EPS}_y = \frac{\text{Net Income}_y + \max(0,\; \text{D\&A}_{y,\text{clean}} - \text{CapEx}_y - 0.20 \times \overline{\text{Lease}}_y)}{\text{Shares Outstanding}_y}$$
   *Shares are period-end outstanding and EPS = NI ÷ shares. One-off non-cash earnings spikes (disposal gains, hedge marks, tax allowances) are stripped out. For IFRS filers $20\%$ of average right-of-use lease obligations is deducted from both `owner_addback` and `true_fcf` (`fcf_conv`); US-GAAP filers (`us`, plus `US_GAAP_IDS` in `fetch_market_data.py`: ABB, Alcon, Logitech, Qiagen, STMicro and the Canadian ENB, TRP, IMO, CNR, FTS, EMA, H, WCN, CP, QSR) are exempt. Rows whose statements are stale (`[auto] stale fundamentals`) are valued as No data until refetched.*
2. **Peak Owner EPS, Direct `cur_oe_eps` & Age-Weighted Mid-Cycle Reversion Standard**:
   - `peak_oe_eps`: The highest Owner EPS achieved over the last 5 fiscal years (converted to quote currency).
   - `cur_oe_eps`: Latest fiscal-year Owner EPS (converted to quote currency).
   - **Active Peak EPS**: apply the age-weighted Mid-Cycle Reversion standard using `cur_oe_eps` (falling back to implied `cur_eps` if absent): if $\text{cur\_eps} < \text{peak\_oe\_eps}$, $\text{Active Peak EPS} = \text{cur}^{+} + w \times (\text{peak\_oe\_eps} - \text{cur}^{+})$ with $w = 0.5$ for a peak at most 1 year older than `cur_oe_year`, fading linearly to 0 at 4 years; otherwise `peak_oe_eps`. Fiscal years before the listing date are not part of the Owner EPS series.
3. **5-Year Historical Cycle Multiples (Informational Reference)**:
   - `mult_low_5y` and `mult_high_5y`: 5-year cycle low and high multiples.

---

### 5.2 Operating ROIC Normalization, M&A Capital Matching & Single Initial Cap (`par_roic_cap = 50%`) (v7.1)

1. **GAAP ROIC vs Operating ROIC**:
   - Invested Capital = equity + non-controlling interests + long- and short-term debt − cash & short-term investments (`cash_sti`), so the capital base matches consolidated EBIT.
   - **Operating ROIC (Tangible Capital Return)** deducts Goodwill and Intangibles from Invested Capital (floored at $\frac{1}{3}\text{IC}_{\text{GAAP}}$) on the same NOPAT — no D&A add-back since v7.3; when GAAP invested capital is $\le 0$ it falls back to GAAP ROIC.
2. **M&A-Matched RONIC & Single Initial Cap (`par_roic_cap = 0.50`)**:
   - When goodwill-heavy ($r_{\text{tang}} > 1.25 \times r_{\text{GAAP}}$), a serial acquirer keeps spending `ma_reinvest` ($\Sigma$ cash-funded $\Delta$(goodwill + intangibles) ÷ $\Sigma$ NOPAT over the 10-year $g_0$ window; only acquisition years with goodwill up > 2%; stock-funded years skipped) on acquisitions earning GAAP ROIC: bought growth $g_m = \text{ma\_reinvest} \times r_{\text{GAAP}}$, bought share $w = \text{clip}_{[0,1]}(g_m / g_0)$ and $1/\text{RONIC}_0 = (1-w)/r_{\text{tang}} + w/r_{\text{GAAP}}$, capped at `par_roic_cap = 0.50`. One transformational merger moves the median little; organic capital growth never counts as M&A.
   - A $\text{RONIC}_0 \le r$ is flagged (`ronic_le_r`) for review: growth then adds no value and Fair P/E $\le 1/r$.
3. **Active ROIC Priority**:
   - Balance-Sheet Financials: `roe_median` (consolidated for Up-C structures like `IBKR`) $\rightarrow$ IFRIC-12 Concessions: `roic_median` $\rightarrow$ All others: `roic_operating` $\rightarrow$ `roic_median` — except `roe_median` when invested capital is $\le 0$ in $\ge 2$ of 5 years and $0 < \text{ROE} \le 50\%$ (v7.5, clearing / customer cash: DB1, ADYEN).

---

### 5.3 4-Pillar Statistical Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Buyback Accretion (`g_exp`) (v7.1)

1. **Share Buyback / Dilution Split**:
   $$\text{bb\_eff} = \text{clamp}_{[-0.03,\, 0.035]}(\text{buyback\_yield}), \qquad \text{bb\_pos} = \max(0.0, \text{bb\_eff}), \qquad \text{bb\_org} = \min(0.0, \text{bb\_eff})$$
2. **4-Pillar Statistical Organic Growth Base (`sales_cagr` via `statistical_organic_g0`)**:
   - **Primary**: `sales_cagr`, computed via:
     1. **Pillar 1 (Dilution-Adjusted Share Index)**: $S_t = S_{t-1} \times \max(1.0, \text{Shares}_t / \text{Shares}_{t-1})$ (up to $+65\%/\text{yr}$), deducting stock-merger and SBC dilution in the exact year it occurs without double-counting share buybacks.
     2. **Pillar 2 (Cycle-Spanning Theil–Sen)**: All pairwise annualized log-slopes spanning $\Delta t \ge 5\text{y}$, extracting median ($P_{50}$), Lower Confidence Bound ($P_{25}$), and MAD dispersion ($\hat{\sigma}_b$).
     3. **Pillar 3 (3-Driver Triangulation)**: $\hat{g}_{\text{tri}} = \min(\text{median of the three } P_{25},\; \text{median of the three } P_{50},\; \hat{g}_{\text{Rev}, P50} + 1.5\text{pp})$ over Revenue, NOPAT and Owner Earnings (refranchising guard: $\min(6\%, \hat{g}_{\text{NOPAT}, P25}, \hat{g}_{\text{OE}, P25})$ when revenue $P_{50} < g_{\text{base}}$ and both profit $P_{25}$s exceed it).
     4. **Pillar 4 (Empirical Bayes Shrinkage & $\tanh$ Tail Compression)**: Precision shrinkage $w = \tau_0^2 / (\tau_0^2 + \hat{\sigma}_{b,\text{Rev}}^2)$ ($\tau_0 = 0.060$, one weight from the revenue spread) toward $g_{\text{base}} = 3.0\%$, compressed via $\text{compress\_g0}$ with asymptote `par_g_anchor_max = 0.130` (`13.0%`).
   - **Fallbacks**: `opcost_cagr` $\rightarrow$ $\text{cagr\_oe\_eps} - \text{bb\_pos}$ $\rightarrow$ $\text{sales\_1y} + \text{bb\_org}$ $\rightarrow$ `0.030`.
3. **Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Per-Share Ceiling (`g_exp`)**:
   $$g_0 = g_{\text{org,exp}} = \text{clamp}_{[0.0,\, 0.13]}(\text{raw\_org}), \qquad g_{\text{exp}} = g_{\text{org,exp}} + \text{bb\_pos}$$

---

### 5.4 Explicit $N$-Year Mauboussin-Fade DCF Valuation ($r = 8.50\% / 10.25\%$) (v7.1)

1. **Stage 1 — Explicit Year-by-Year Mauboussin Fade ($t = 1 \dots N$)**:
   Starting at $E_1 = 1.0$ — the active (trailing, normalized) Owner EPS treated as Year-1 earnings, deliberately conservative by one year of growth versus a forward $E_1 = \text{EPS}(1 + g_0)$ — $\text{frac}_t = \frac{t - 1}{\max(1, N - 1)}$, $g_t = g_0 - \text{frac}_t(g_0 - \min(g_0, 0.030))$, $\text{RONIC}_t = \text{RONIC}_0 - \text{frac}_t(\text{RONIC}_0 - \text{RONIC}_{\text{term}})$ with $\text{RONIC}_{\text{term}} = \max(0.05,\; \min(\text{RONIC}_0, 0.20, r + 0.5(\text{RONIC}_0 - r)))$, $\text{FCF}_t = E_t\left(1 - \frac{\max(0, g_t)}{\max(0.05, \text{RONIC}_t)}\right)$, $E_{t+1} = E_t(1 + g_t)$, and $\text{PV}_{\text{Stage 1}} = \sum_{t=1}^{N} \text{FCF}_t (1 + r)^{-t}$.
2. **Stage 2 — Post-CAP Terminal Perpetuity Value ($t > N$)**:
   With $g_{\text{tv}} = \max(0.0, \min(g_0, 0.030))$ and $\text{Reinv}_{\text{tv}} = \frac{g_{\text{tv}}}{\max(0.05, \text{RONIC}_{\text{term}})}$:
   $$\text{TV}_N = \frac{E_{N+1}(1 - \text{Reinv}_{\text{tv}})}{\max(0.01, r - g_{\text{tv}})}, \qquad \text{PV}_{\text{Stage 2}} = \frac{\text{TV}_N}{(1 + r)^N}, \qquad \text{Fair P/E} = \text{par\_mult} = \text{pe\_vd} = \text{PV}_{\text{Stage 1}} + \text{PV}_{\text{Stage 2}}$$
   *Guarantees exact Miller–Modigliani zero-spread invariance ($\text{Fair P/E} \equiv 1/r$ when $\text{RONIC}_t = r$). A zero terminal value applies only to concessions explicitly listed in `FINITE_CONCESSION_IDS` (empty by default).*

---

### 5.5 The 3-Price Valuation Framework & Bellman-Consistent 5-Year Expected IRR (v7.1)

1. **Fair Value Price (`par_val`)**: $\text{Fair P/E} \times \text{Active Peak Owner EPS}$.
2. **Standalone Terminal P/E (`term_mult`), Terminal Price (`term_val`) & `% vs Terminal` (`vs_term`)**:
   $$\text{term\_mult} = \frac{1 - 0.030 / \text{RONIC}_{\text{term}}}{\max(0.01,\; r - 0.030)} \quad (\text{when } \text{RONIC}_{\text{term}} > r,\text{ else } 1/r), \qquad \text{term\_val} = \text{term\_mult} \times \text{Active Peak Owner EPS}, \qquad \text{vs\_term} = \frac{\text{Current Share Price}}{\text{term\_val}} - 1.0$$
3. **Current Multiple (`cur_mult`)**: $\text{Current Share Price} \div \text{Active Peak Owner EPS}$.
4. **Discount vs Fair Value (`vs_par`)**: $\text{Current Share Price} \div \text{Fair Value Price} - 1.0$ (negative = discount; there is no Below / Above PAR label since v7.2 — the status of a valued company is `Valued`). When the DCF fair value is $\le 0$ the status is **`No value`** and `vs_par`, IRR and runway metrics are left blank.
4. **Bellman-Consistent 5-Year Expected IRR (`irr_5y`)**:
   Solves $\text{Current Multiple} = \sum_{t=1}^{5} \text{FCF}_t (1 + \text{IRR})^{-t} + V_5 (1 + \text{IRR})^{-5}$ directly on the Year 1–5 DCF cash flows and Year-5 DCF continuation value $V_5 = (\text{Fair P/E} - \sum_{t=1}^{\min(5, N)} \text{FCF}_t(1+r)^{-t})(1+r)^{\min(5, N)}$, guaranteeing $\text{IRR}_{5\text{y}} \equiv r$ at $\text{Price} = \text{Fair Value}$.
5. **Root-Safe DCF-Inverted Market-Implied Growth ($g_{\text{market}}$) & Growth Margin (`g_gap`)**:
   Solves $\text{DCF\_PE}(g_{\text{market}},\, \text{RONIC}_0,\, N,\, r) = \text{Current Multiple}$, with $\text{Growth Margin} = g_0 - g_{\text{market}}$ reported only for a unique root (flag `ok`; grid-saturated results are shown as ≤ −20% / ≥ +50% without a margin).
6. **Market-Implied CAP & Moat Runway Margin**:
   $$\text{Market-Implied CAP} = \max\!\left(0.0,\; \text{Fundamental CAP} \times \frac{\text{Current Multiple} - \frac{1}{r}}{\text{Fair P/E} - \frac{1}{r}}\right), \qquad \text{Moat Margin} = \text{Fundamental CAP} - \text{Market-Implied CAP}$$

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

#### No `quantitative_overrides` (v7.6)
The quantitative valuation uses statement data only; a `quantitative_overrides` block in a payload is ignored with a warning.

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
4. No `quantitative_overrides` are applied (ignored with a warning).

### Step 2: Apply Updates to Datasets
`screener/apply_evaluation.py` automatically updates:
- `data/<universe>/inputs.csv`: updates columns `1`, `2`, `2r`, `3a`, `3b`, `3m`, `4`, `5`, `6`, `calamity`, `calamity_note`, `note`, `evidence`.

### Step 3: Rebuild HTML Cockpit
After updating, compile the standalone HTML cockpit (`output/screener.html`, `output/index.html`, `docs/index.html`):
```bash
python3 build.py
```
The newly evaluated company will immediately reflect its updated status across `🛡️ Quality Pass Funnel`, `⚠️ Calamity Watchlist`, and `🔍 Full Universe & Waterfall`.
