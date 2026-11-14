# Quantitative Evaluation Framework Specification (v6.36)
## Quality & Moat Screener — Explicit Mauboussin-Fade DCF & Operating Cost Base Growth Ceiling

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent quantitative valuation** of individual public companies within the Quality & Moat Screener (v6.36). It can be executed entirely standalone by an AI agent or analyst to model fair value, margin of safety, and expected internal rate of return (IRR) across a 5-year business cycle.

### The Slump-Cannibal Compounder & Explicit DCF Doctrine
Grounded in the investment philosophies of **Charlie Munger**, **Warren Buffett**, **Michael Mauboussin**, and **Chris Hohn**, high-quality compounders that pass the 6 Munger Quality Gates are valued via an **Explicit $N$-Year Mauboussin-Fade Discounted Cash Flow (DCF) model** at a discount rate of $r = 8.50\%$:
1. **Normal Organic Growth Ceiling ($g_0$ / `g_org_exp`) Anchored on Operating Cost Base (`opcost_cagr`)**: Because companies passing the 6 Munger Quality Gates maintain roughly constant operating margins over the complete cycle (Gate 3b pricing power $\ge$ inflation, Gate 5 rejects SG&A bloat), the 3–5Y CAGR of the operating cost base ($\text{OpCost} = \text{Sales} - \text{EBIT} = \text{COGS} + \text{OpEx}$) is the cleanest, least volatile proxy for "normal" organic business growth (`g_org_exp`). Crucially, a temporary 1-year revenue slump (`sales_1y`) does not depress the company's structural organic growth ceiling.
2. **Explicit $N$-Year Mauboussin-Fade DCF ($r = 8.50\%$, $100\%$ Weight)**: Fair Value Multiple (`par_mult` / $\text{PE}_{\text{VD}}$) is computed via an explicit year-by-year cash flow simulation across the company's Gate 4 Competitive Advantage Period ($N = \text{CAP}$ years), where organic growth $g_t$ and return on incremental capital $\text{ROIC}_t$ fade linearly from $(g_0 = g_{\text{org,exp}},\, \text{ROIC}_0 = \text{ROIC}_{\text{exp}})$ in Year 1 down to terminal steady state ($g_{\text{term}} = 3.5\%$, $\text{ROIC}_{\text{term}} = \max(12.0\%, \min(\text{ROIC}_0, 20.0\%))$) at Year $N$, followed by a terminal value perpetuity discounted at $r = 8.50\%$.
3. **Buying Slump-Cannibal Compounders Below Fair Value**: The highest-probability path to superinvestor returns is purchasing world-class compounders during a temporary 1-year growth slump when the share price trades at a discount to Explicit DCF Fair Value ($\text{Price} \le \text{Fair Value}$) while the company cannibalizes its own shares at depressed multiples via strong Free Cash Flow.
4. **Prerequisite**: In standard screening workflow, quantitative valuation is performed on companies that achieve **`Quality pass`** across the 6 qualitative gates or **`Calamity pass`** (conditional override on Gates 3b, 5, and/or 6). For **`Calamity pass`** businesses, explicitly check whether normalized earning power (`peak_eps_est`) or forward growth (`g_est`) needs a haircut rather than extrapolating pre-calamity peaks unadjusted.

---

## 2. Input Context Provided to the Quantitative Evaluator

When an evaluation is triggered, the coordinator agent provides:

### 2.1 Identifiers & Market Quotes
- `id`: Unique identifier (e.g. `MSFT`, `SPGI`, `NESN.CH`).
- `ticker`: Trading ticker.
- `company`: Official company name.
- `universe`: `us`, `eu`, or `ca`.
- `price`: Current share price in quote currency.
- `market_cap_m`: Current market capitalization in reporting currency (millions).
- `quote_currency` & `fin_currency`: Quote vs reporting currencies (with FX conversion if differing).

### 2.2 Financial History & Statements (5–10 Fiscal Years)
- **Net Income (`ni_ttm_m`)**: Net income for latest fiscal year and historical series.
- **CapEx (`capex_ttm_m`)**: Capital expenditures (positive value).
- **Depreciation & Amortization (`da_ttm_m`)**: D&A (including intangible amortization).
- **Dividends (`dividends_ttm_m`)**: Cash dividends paid in latest fiscal year.
- **Balance Sheet**: Cash & equivalents (`cash_m`), Long-term debt (`lt_debt_m`).
- **Operating Earnings & Coverage**: EBIT (`ebit_ttm_m`), Interest Expense (`interest_m`).
- **Diluted Shares**: Historical diluted share count.

### 2.3 Computed Screening Metrics (from `screener/fetch/par.py`)
- `peak_oe_year`: Fiscal year in which the highest Owner EPS occurred within the last 5 years.
- `peak_oe_eps`: Last peak Owner EPS in quote currency.
- `mult_low_5y`: 5-year cycle low multiple (median of calendar-year lows over 60 monthly closes).
- `mult_high_5y`: 5-year cycle high multiple (median of calendar-year highs over 60 monthly closes).
- `cagr_oe_eps`: Peak-to-peak Owner EPS compound annual growth rate ($g$) across cycles.
- `p2p_ok`: Peak-to-peak test (`"Y"` = new peak vs prior cycle, `"N"` = not above prior cycle).
- `roic_median`: 5-year median GAAP ROIC (including accounting goodwill).
- `roic_operating`: 5-year median Operating ROIC (tangible capital return).
- `fcf_conv`: Multi-year Owner FCF conversion ($\text{Owner FCF} \div \text{Net Income}$).
- `fund_cap`: Fundamental Competitive Advantage Period from Gate 4 (e.g. 15, 20, 30 years).

---

## 3. Step-by-Step Valuation Methodology (v6.36)

---

### Step 1: Owner EPS Calculation, Lease/Impairment Normalization & Peak Selection (v6.36)

1. **Owner EPS Definition, Deterministic D&A & IFRS-16 Lease Normalization (Per Fiscal Year)**:
   $$\text{Owner Add-Back}_y = \max\!\left(0,\; \text{D\&A}_{y,\text{clean}} - \text{CapEx}_y - 0.20 \times \overline{\text{Lease}}_y\right), \qquad \text{Owner EPS}_y = \frac{\text{Net Income}_y + \text{Owner Add-Back}_y}{\text{Diluted Shares}_y}$$
   - **Deterministic D&A Priority**: Extracted in strict priority order: cash-flow statement `depreciation` $\to$ income-statement `depreciationAndAmortization` $\to$ `reconciledDepreciation` (replacing `max(...)` across tags).
   - **Impairment Guard (`clean_da`)**: Each year's D&A is capped at $1.5\times$ the median of the prior 3 fiscal years (`DA_IMPAIRMENT_CAP = 1.5`) so one-off goodwill or intangible write-downs folded into D&A are not added back as recurring earnings.
   - **IFRS-16 Right-of-Use Lease Depreciation Deduction (`LEASE_DEP_RATE = 0.20`)**: For IFRS universes (`eu`, `ca`), IFRS-16 capitalizes operating store/facility leases onto the balance sheet (`capitalLeaseObligations`), routing rent payments through D&A while excluding lease additions from cash CapEx. Deducting $20\%$ of average `capitalLeaseObligations` ($\overline{\text{Lease}}_y$) from the D&A add-back prevents lease amortization from inflating Owner EPS (e.g. luxury retail store leases). US GAAP filers (`us`) expense operating lease cost inside operating cash flow and are excluded (`lease` series cleared).
   - *Scaled to reported diluted EPS when net income includes minority interests. Latest fiscal-year add-back is stored in `owner_add_m`.*

2. **Spike Stripping (One-Off Earnings Spikes)**:
   Non-cash windfall gains (tax-allowance releases, subsidiary disposal gains, hedge marks) must be stripped from the Owner EPS series:
   - A year is flagged as an unrepeatable spike if:
     - $\text{Net Income} > 1.10 \times \text{Operating Cash Flow}$, **AND**
     - $\text{Net Income} > 1.30 \times \text{prior year Net Income}$, **AND**
     - $\text{Net Income} > 1.30 \times \text{following year Net Income}$ (or for latest year: $+50\%$ vs prior and $> 1.30 \times \text{OCF}$).

3. **Peak Owner EPS Selection, Override (`peak_eps_est`) & 50/50 Mid-Cycle Reversion Standard**:
   - `peak_oe_eps`: The highest valid Owner EPS in the last 5 fiscal years.
   - **Analyst Override (`peak_eps_est`)**: Required when:
     - The reported peak contains an unrepeatable operational windfall (e.g. pandemic freight rates, cyclical commodity peak).
     - Recent strategic spin-offs or restructurings distorted historical share counts or continuing operations.
   - **The 50/50 Mid-Cycle Reversion Standard**:
     When `peak_eps_est` is not explicitly populated, active earning power is protected against stale or bubble peaks:
     - If `fin_note` flags a multi-class share-basis mismatch (`"check share basis"`), $\text{cur\_eps}$ defaults to `peak_oe_eps` so whole-firm `market_cap_m` does not depress per-share `cur_eps`; if `fin_note` flags `"non-cash earnings spike left out of peak"` or $\text{cur\_eps} > 1.5 \times \text{peak\_oe\_eps}$, $\text{cur\_eps}$ is capped at `peak_oe_eps`.
     - If current Owner EPS ($\text{cur\_eps} = \text{Price} \times \frac{\text{Net Income} + \text{owner\_add\_m}}{\text{Market Cap}}$, latest fiscal year) falls below `peak_oe_eps`:
       $$\text{Active Peak EPS} = 0.5 \times \left(\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})\right)$$
     - If $\text{cur\_eps} \ge \text{peak\_oe\_eps}$: $\text{Active Peak EPS} = \text{peak\_oe\_eps}$.
     - *Both sides use the identical `owner_add_m` add-back (with impairment guard and IFRS-16 lease deduction), so compounders at peak are compared like-for-like.*
   - **Active Peak EPS Summary**:
     $$\text{Active Peak EPS} = \begin{cases} \text{peak\_eps\_est} & \text{if populated} \\ 0.5 \times (\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})) & \text{if } \text{cur\_eps} < \text{peak\_oe\_eps} \\ \text{peak\_oe\_eps} & \text{otherwise} \end{cases}$$

---

### Step 2: Operating ROIC Normalization, Short-Term Investments Netting & Mauboussin Galton Regression (v6.36)

To prevent accounting distortions from penalizing capital-light compounders while eliminating arbitrary hard caps on ROIC:
1. **Short-Term Investments Netting, M&A Goodwill Neutralization & Denominator Floor**:
   - Operating cash $\text{Cash}_{\text{op}}$ nets both cash & equivalents and marketable short-term treasury investments (`cashAndShortTermInvestments`, stored in `cash_sti`) from Invested Capital, so liquid T-bill portfolios (e.g. `VEEV`) are not misclassified as deployed operating assets:
     $$\text{IC}_{\text{GAAP}} = \text{Equity} + \text{Debt} - \text{Cash}_{\text{op}} \qquad \left(\text{floored at } 0.25 \times \text{Tangible Operating Assets when } \text{IC}_{\text{GAAP}} \le 0\right)$$
   - **Operating ROIC (Tangible Capital Return)** deducts Goodwill and Intangibles from Invested Capital, floored at $\frac{1}{3} \times \text{IC}_{\text{GAAP}}$ so goodwill deduction can reduce the capital base by at most two-thirds (eliminating artificial division-by-zero spikes when M&A goodwill or share buybacks exceed book equity):
     $$\text{Operating ROIC} = \frac{\text{NOPAT}}{\max\!\left(\text{Equity} + \text{Debt} - \text{Cash}_{\text{op}} - \text{Goodwill} - \text{Intangibles},\; \frac{1}{3}\text{IC}_{\text{GAAP}}\right)}$$
2. **Mauboussin Galton ROIC Regression ($\text{Expected ROIC}$)**:
   - Grounded in Michael Mauboussin's Galton regression formula ($\text{Expected ROIC} = r(\text{Current ROIC} - \text{Average ROIC}) + \text{Average ROIC}$), excess Active ROIC above the corporate mean ($\text{ROIC}_{\text{avg}} = 12.0\%$) is first logarithmically compressed ($k_{\text{roic}} = 0.25$) and then faded by Gate 4 CAP persistence $r = \text{pers} \in \{0.85, 0.75, 0.62\}$:
     $$\text{ROIC}_{\text{log}} = 0.12 + 0.25 \times \ln\!\left(1 + \frac{\text{Active ROIC} - 0.12}{0.25}\right)$$
     $$\text{Expected ROIC} = r \times (\text{ROIC}_{\text{log}} - 0.12) + 0.12$$
3. **Active ROIC Selection (`active_roic`)**:
   - Priority:
     1. `roic_est` (analyst override, if populated)
     2. **Balance-Sheet Financials** (`Insurance` excl. `Insurance Brokers`, `Reinsurance`, `Banks` excl. `Asset Management & Custody Banks`, `Investment Banking & Brokerage`, and `Multi-Sector Holdings`): **`roe_median`** (5-year median Return on Equity, since the DCF is an equity-level EPS model where reinvestment is $g/\text{ROE}$ and customer deposits/float do not enter $\text{Equity} + \text{Debt} - \text{Cash}$) $\to$ `roic_median` $\to$ `roic_operating`
     3. **IFRIC-12 Infrastructure Concessions** (`Construction & Engineering`, `Highways & Railtracks`): **`roic_median`** (5-year median GAAP ROIC including concession intangibles) $\to$ `roic_operating`
     4. **All Other Operating & Fee Businesses**: **`roic_operating`** (5-year median Tangible Operating ROIC) $\to$ `roic_median` (GAAP).

---

### Step 3: Operating Cost Base Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Buyback Accretion (`g_exp`) (v6.35)

Because companies passing the 6 Munger Quality Gates maintain roughly constant operating margins over the business cycle (Gate 3b verifies pricing power $\ge$ inflation; Gate 5 rejects SG&A bloat), the 3–5Y CAGR of the operating cost base ($\text{OpCost}_y = \text{Sales}_y - \text{EBIT}_y = \text{COGS}_y + \text{OpEx}_y$, stored in `opcost_cagr`) serves as the primary anchor for the company's **Normal Organic Growth Ceiling ($g_0$ / `g_org_exp`)**:

1. **Core Growth Ceiling & Scale Parameters**:
   - `par_g_base = 0.035` (`3.5%` long-term nominal GDP terminal growth rate $g_{\text{term}}$).
   - Revenue-Anchored Scale Ceilings (`scale_cap`, normalized to USD revenue):
     - `HYPER` ($\ge \$250\text{B}$ USD revenue): `par_g_cap_hyper = 0.095` (`9.5%`).
     - `MEGA` ($\$50\text{B}\text{–}\$250\text{B}$ USD revenue): `par_g_cap_mega = 0.098` (`9.8%`).
     - `LARGE` ($\$15\text{B}\text{–}\$50\text{B}$ USD revenue): `par_g_cap_large = 0.105` (`10.5%`).
     - `MID/SM` ($< \$15\text{B}$ USD revenue): `par_g_cap = 0.120` (`12.0%`).
   - Share Buyback / Dilution Split:
     $$\text{bb\_eff} = \text{clamp}_{[-0.03,\, 0.035]}(\text{buyback\_yield}), \qquad \text{bb\_pos} = \max(0.0, \text{bb\_eff}), \qquad \text{bb\_org} = \min(0.0, \text{bb\_eff})$$

2. **Normal Organic Growth Base (`base_org`) & Fallback Hierarchy**:
   - **Primary**: `opcost_cagr` (3–5Y CAGR of $\text{OpCost} = \text{Sales} - \text{EBIT}$, clamped to $[-25\%, +45\%]$).
   - **Fallback 1**: `sales_cagr` (3–5Y top-line revenue CAGR, if `opcost_cagr` is unavailable).
   - **Fallback 2**: $\text{cagr\_oe\_eps} - \text{bb\_pos}$ (cycle Owner EPS CAGR net of positive buybacks).
   - **Fallback 3**: `sales_1y` (1Y sales growth).
   - **Fallback 4**: $\text{g\_implied} - \text{bb\_pos}$ (when all statement growth metrics are absent).
   - **Fallback 5**: `par_g_base = 0.035` (`3.5%`).

3. **Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Per-Share Growth Ceiling (`g_exp`)**:
   - Because the Explicit Mauboussin-Fade DCF already fades growth linearly every year from $g_0$ down to $g_{\text{term}} = 3.5\%$, legacy pre-fade revenue scale caps (`scale_cap`) and the `2.0%` floor are not applied:
   - If explicit analyst override `g_est` is populated:
     $$g_0 = g_{\text{org,exp}} = \text{clamp}_{[0.0,\, 0.22]}(g_{\text{est}} - \text{bb\_pos}), \qquad g_{\text{exp}} = \text{clamp}_{[0.0,\, 0.22 + \text{bb\_pos}]}(g_{\text{est}})$$
   - Otherwise:
     $$g_0 = g_{\text{org,exp}} = \text{clamp}_{[0.0,\, 0.22]}(\text{base\_org} + \text{bb\_org}), \qquad g_{\text{exp}} = g_{\text{org,exp}} + \text{bb\_pos}$$
   - Crucially, a temporary 1-year growth slump (`sales_1y`) does not penalize $g_0$ (`g_org_exp`), allowing the screener to identify compounders whose current 1Y growth has slumped well below their normal Operating Cost Base growth ceiling while their share price is temporarily depressed.

---

### Step 4: Explicit $N$-Year Mauboussin-Fade DCF Valuation ($r = 8.50\% / r_{\text{fin}} = 10.25\%$) (v6.36)

Because the DCF explicitly values `100%` of firm Free Cash Flow ($1 - g_t/\text{ROIC}_t$) before deciding whether FCF is distributed as dividends or share buybacks, the explicit DCF is evaluated strictly on the **Normal Organic Growth Ceiling ($g_0 = g_{\text{org,exp}}$)** — eliminating share-buyback double-counting in `Fair P/E` (`par_mult`) while removing the legacy 5-year historical multiple (`t_hist`) blend (`par_vd_weight = 1.00`):

1. **Stage 1 — Explicit Year-by-Year Mauboussin Fade Over Gate 4 CAP ($t = 1 \dots N$)**:
   Starting from normalized Year-0 Owner Earnings $E_0 = 1.0$, initial organic growth $g_0 = g_{\text{org,exp}}$, and initial return on incremental capital $\text{ROIC}_0 = \text{ROIC}_{\text{exp}}$, both growth and incremental ROIC fade linearly across the $N$-year Competitive Advantage Period ($N = \text{Gate 4 CAP}$, default `20` years) toward terminal steady state ($g_{\text{term}} = \min(g_0, 3.5\%)$, $\text{ROIC}_{\text{term}} = \max(12.0\%, \min(\text{ROIC}_0, 20.0\%))$):
   $$\text{frac}_t = \frac{t - 1}{N}, \qquad g_t = g_0 - \text{frac}_t \cdot (g_0 - g_{\text{term}}), \qquad \text{ROIC}_t = \text{ROIC}_0 - \text{frac}_t \cdot (\text{ROIC}_0 - \text{ROIC}_{\text{term}})$$
   $$E_t = E_{t-1} \cdot (1 + g_t), \qquad \text{Reinv}_t = \frac{\max(0.0, g_t)}{\max(0.05, \text{ROIC}_t)}, \qquad \text{FCF}_t = E_t \cdot (1 - \text{Reinv}_t)$$
   $$\text{PV}_{\text{Stage 1}} = \sum_{t=1}^{N} \frac{\text{FCF}_t}{(1 + r)^t} \qquad (\text{stored in } \text{pe\_mm},\; r = 8.50\% \text{ or } 10.25\%)$$
   *Reinvestment $\text{Reinv}_t$ is uncapped: when $g_t > \text{ROIC}_t$, $\text{FCF}_t < 0$ (externally funded growth), ensuring growth never becomes "free" and $\text{DCF\_PE}(g)$ remains strictly monotonic wherever $\text{ROIC} > r$.*

2. **Stage 2 — Post-CAP Terminal Perpetuity Value ($t > N$)**:
   At the end of the Competitive Advantage Period ($t = N$), competitive advantage has expired, so any post-CAP growth beyond Year $N$ earns exactly the cost of capital ($\text{RONIC} = r$) and adds zero net present value ($\text{ROIC}_{\text{term}}$ governs only the Stage-1 linear fade):
   $$\text{TV}_N = \frac{E_N}{r}, \qquad \text{PV}_{\text{Stage 2}} = \frac{\text{TV}_N}{(1 + r)^N} \qquad (\text{stored in } \text{pe\_mck},\; r = 8.50\% \text{ or } 10.25\%)$$

3. **100% Explicit DCF Fair Value Multiple (`par_mult` / `pe_vd`)**:
   $$\text{Fair P/E} = \text{par\_mult} = \text{pe\_vd} = \text{PV}_{\text{Stage 1}} + \text{PV}_{\text{Stage 2}}$$

4. **Industry-Specific Capital Base, Discount Rate ($r_{\text{fin}} = 10.25\%$) & Value Driver Physics**:
   - **Balance-Sheet Financial Discount Rate ($r_{\text{fin}} = 10.25\%$) & ROE Capital Base (`roe_median`)**: For **Balance-Sheet Financials** (`Insurance` excluding `Insurance Brokers`, `Reinsurance`, `Banks` excluding `Asset Management & Custody Banks`, `Investment Banking & Brokerage`, and `Multi-Sector Holdings`), the Explicit Mauboussin-Fade DCF and Market-Implied Growth inversion use $r_{\text{fin}} = 10.25\%$ (`par_cost_of_equity_fin = 0.1025`) rather than $r = 8.50\%$, and `active_roic` selects 5-year median Return on Equity (`roe_median`) so equity reinvestment equals $g_t / \text{ROE}_t$.
   - **IFRIC-12 Concession Capital Base (`roic_median`)**: For **IFRIC-12 Infrastructure Concessions** (`Construction & Engineering`, `Highways & Railtracks`), `active_roic` defaults to `roic_median` (GAAP ROIC including concession intangibles).
   - **Mark-to-Market HoldCo / Insurer NAV Physics (`1.0x BVPS`)**: For `Multi-Sector Holdings` and `Insurance` (excluding `Insurance Brokers`) with no `peak_eps_est` override where reported EPS already captures unrealized mark-to-market portfolio appreciation $\Delta\text{NAV}$ (5Y `fcf_conv < 0.25`, **or** latest 2Y `ocf_ni_2y < 0.25`, **or** `fcf_conv is None` in `Multi-Sector Holdings` with `mult_high_5y < 12.0`), Fair Value is anchored directly to $1.0\times$ Book Value per Share ($\text{BVPS} = \text{equity\_m} \times \frac{\text{Price}}{\text{Market Cap}}$, so $\text{par\_val} = \text{BVPS}$ and $\text{par\_mult} = \frac{\text{BVPS}}{\text{Active Peak EPS}}$, falling back to $\frac{1}{\text{ROIC}_{\text{exp}}}$ only if `equity_m` is unavailable).
   - **IFRIC-12 Finite Concession Annuity Physics**: For `Construction & Engineering` and `Highways & Railtracks` with `fcf_conv > 1.25` (where concession assets amortize and revert to the state at expiry), Stage 2 terminal perpetuity is omitted ($\text{PV}_{\text{Stage 2}} = 0$) and $\text{par\_mult} = \text{PV}_{\text{Stage 1}}$.

---

### Step 5: Valuation Metrics & Status (v6.36)

1. **Fair Value Price (`par_val`)**:
   $$\text{Fair Value Price} = \text{Fair P/E} \times \text{Active Peak Owner EPS}$$
   *Strictly independent of current share price.*
2. **Current Multiple (`cur_mult`)**:
   $$\text{Current Multiple} = \frac{\text{Current Share Price}}{\text{Active Peak Owner EPS}}$$
3. **Discount / Premium vs Fair Value (`vs_par`)**:
   $$\text{Discount vs Fair Value} = \frac{\text{Current Share Price}}{\text{Fair Value Price}} - 1.0$$
   - **Valuation Status**:
     - `Below PAR`: Current Price $\le$ Fair Value Price ($\text{vs\_par} \le 0$). **ATTRACTIVE ENTRY**.
     - `Above PAR`: Current Price $>$ Fair Value Price ($\text{vs\_par} > 0$). **PREMIUM / HOLD**.
4. **5-Year Expected Cycle IRR (FCF-Conserved Pull-to-Fair-Value Cash-Flow IRR with Rolled-Forward Exit Multiple)**:
   - **5-Year Average Organic Fade Growth ($g_{\text{org,5y}}$)**: Over Years 1–5 along the linear Mauboussin fade trajectory, average annual organic growth is:
     $$g_{\text{org,5y}} = g_0 - \frac{2}{\max(5, N)}(g_0 - g_{\text{term}})$$
   - **Cash-Flow Conservation Cap on Buybacks ($g_{\text{irr}}$)**: Total cash returned to shareholders ($\text{Dividends} + \text{Buybacks}$) cannot exceed Stage-1 Free Cash Flow Yield $\frac{1 - g_0/\text{ROIC}_0}{\text{Current Multiple}}$:
     $$\text{bb\_fcf\_cap} = \max\!\left(0,\; \frac{\max(0, 1 - g_0/\text{ROIC}_0)}{\text{Current Multiple}} - \text{dy}\right), \qquad g_{\text{irr}} = g_{\text{org,5y}} + \min\!\left(\text{bb\_pos},\; \text{bb\_fcf\_cap}\right)$$
   - **Rolled-Forward Year-5 Exit Fair Value ($\text{PAR\_Val}_{5\text{y}}$)**: Because 5 years of the Competitive Advantage Period have elapsed by Year 5, the exit Fair P/E $\text{PE}_5$ is evaluated at Year-6 growth $g_6 = g_0 - \frac{5}{N}(g_0 - g_{\text{term}})$, $\text{ROIC}_6 = \text{ROIC}_0 - \frac{5}{N}(\text{ROIC}_0 - \text{ROIC}_{\text{term}})$, and remaining runway $N - 5$ (`year5_multiple_ratio` $= \text{PE}_5 / \text{PE}_0$, or $1.0$ for NAV-anchored MTM HoldCos):
     $$\text{PAR\_Val}_{5\text{y}} = \text{Fair Value Price} \times \frac{\text{PE}_5}{\text{PE}_0}$$
   - Solves (via Newton-Raphson with convergence check and bisection fallback) for the exact 5-year internal rate of return ($\text{IRR}$) equating current share price $P_0$ to 5 years of growing dividends $D_t = D_0(1 + g_{\text{irr}})^t$ plus Year-5 terminal Fair Value $P_5 = \text{PAR\_Val}_{5\text{y}} \times (1 + g_{\text{irr}})^5$:
     $$P_0 = \sum_{t=1}^{5} \frac{D_0 (1 + g_{\text{irr}})^t}{(1 + \text{IRR})^t} + \frac{\text{PAR\_Val}_{5\text{y}} \cdot (1 + g_{\text{irr}})^5}{(1 + \text{IRR})^5}$$
5. **Root-Safe DCF-Inverted Market-Implied Growth ($g_{\text{market}}$) & Growth Margin of Safety (`g_gap`)**:
   - Scans a $[-20.0\%, +50.0\%]$ grid in $1\text{pp}$ steps and bisects inside every sign-change bracket to solve for the starting organic growth rate $g_{\text{market}}$ satisfying:
     $$\text{DCF\_PE}(g_{\text{market}},\, \text{ROIC}_0,\, N,\, r) = \text{Current Multiple}$$
   - Returns `(g_market, g_market_flag)`:
     - `ok`: Unique root on a monotonically increasing $\text{DCF\_PE}(g)$ curve (guarantees $g_{\text{market}} = g_0$ and $g_{\text{gap}} = 0$ when $\text{Price} = \text{Fair Value Price}$).
     - `saturated_low` / `saturated_high`: Target P/E lies below $-20\%$ or above $+50\%$ on a monotonic curve (`g_market` clamped to grid bound).
     - `no_value_creation`: $\text{DCF\_PE}(g)$ declines with growth ($\text{ROIC} \le r$ or finite-horizon concession without terminal value); `g_gap` is left blank (`None`).
     - `multi_root`: Non-monotonic curve with multiple roots; root nearest $g_0$ is reported and `g_gap` is left blank (`None`).
     - `nav_anchored`: Mark-to-market HoldCo valued at $1.0\times\text{BVPS}$; both `g_market` and `g_gap` are `None`.
   - **Growth Margin of Safety (`g_gap`, populated when `g_market_flag` $\in \{\text{ok}, \text{saturated\_low}, \text{saturated\_high}\}$)**:
     $$\text{Growth Margin} = g_0 - g_{\text{market}} = g_{\text{org,exp}} - g_{\text{market}}$$
6. **Market-Implied CAP & Moat Runway Margin**:
   - Scales excess multiple above the zero-moat steady-state base multiple $\text{PE}_{\text{base}} = \frac{1}{r} = 11.76\text{x}$ (at $r = 8.50\%$):
     $$\text{Market-Implied CAP} = \max\!\left(0.0,\; \text{Fundamental CAP} \times \frac{\text{Current Multiple} - \frac{1}{r}}{\text{Fair P/E} - \frac{1}{r}}\right)$$
   - **Moat Runway Margin**:
     $$\text{Moat Margin} = \text{Fundamental CAP} - \text{Market-Implied CAP}$$

---

### Step 6: Quantitative Health Checks (Gate 6 Rule Check)

These checks generate flags on the Quantitative sheet to alert the investor to potential structural risks:
1. **Net Debt Check**: $\text{Long-Term Debt} \div \text{Owner Earnings} \le 4.0\text{ years}$ (`g6_netdebt_yrs = 4.0`).
2. **Interest Coverage Check**: $\text{EBIT} \div \text{Interest Expense} > 5.0\text{x}$ (`g6_intcov = 5.0`).
3. **Cash Conversion Check**: $\text{Owner FCF} \div \text{Net Income} \ge 80\%$ (`a_fcfconv = 0.80`).
4. **Peak-to-Peak Compounding Check**: `p2p_ok == "Y"`.

---

## 4. Output Contract: Quantitative JSON Result Schema

An independent agent evaluating a company quantitatively must return a strictly validated JSON payload matching this exact schema:

```json
{
  "id": "SPGI",
  "ticker": "SPGI",
  "universe": "us",
  "company": "S&P Global Inc.",
  "price": 505.20,
  "quote_currency": "USD",
  "quantitative_overrides": {
    "peak_eps_est": null,
    "g_est": null,
    "g_implied": 0.105,
    "roic_est": null,
    "fin_note": "Uncorrupted Operating ROIC neutralizes $52.8B IHS Markit accounting goodwill via Galton regression. Bottom-up reference g_implied of 10.5% reflects bond issuance recovery, Market Intelligence recurring analytics, and index volume."
  },
  "valuation_metrics": {
    "active_peak_eps": 19.34,
    "current_multiple": 26.12,
    "par_multiple": 27.60,
    "par_value": 533.78,
    "percent_vs_par": -0.0535,
    "status": "Below PAR",
    "g_implied": 0.105,
    "dividend_yield": 0.0075,
    "expected_irr_5y": 0.1162,
    "market_implied_cap": 18.9,
    "moat_runway_margin": 1.1,
    "market_implied_growth": 0.0934,
    "growth_margin_of_safety": 0.0116
  },
  "health_checks": {
    "net_debt_years": 2.1,
    "net_debt_ok": true,
    "interest_coverage": 8.4,
    "interest_cov_ok": true,
    "fcf_conversion": 0.94,
    "fcf_conv_ok": true,
    "peak_to_peak_ok": true
  },
  "evaluation_metadata": {
    "evaluated_at": "2026-11-09T20:20:00Z",
    "evaluator": "quantitative-agent"
  }
}
```

### Schema Rules & Field Mapping Table

| CSV Field (`financials.csv`) | JSON Key (`quantitative_overrides`) | Type | Usage |
| :--- | :--- | :--- | :--- |
| `peak_eps_est` | `peak_eps_est` | Float or null | Analyst Peak Owner EPS override |
| `g_est` | `g_est` | Float or null | Sole explicit discretionary forward growth override for `g_exp` (e.g. `0.09`) |
| `g_implied` | `g_implied` | Float or null | Informational bottom-up growth reference & fallback when statement growth is missing (e.g. `0.105`) |
| `roic_est` | `roic_est` | Float or null | Normalized Operating ROIC override when reported capital is distorted (leave `null` by default) |
| `fin_note` | `fin_note` | String or null | Financial rationale for overrides & capital structure |

---

## 5. Ingestion via `screener/apply_evaluation.py`

When the agent returns this JSON payload, apply it directly to `data/<universe>/financials.csv`:
```bash
python3 screener/apply_evaluation.py --input quantitative_result.json
```
The script locates the company in `financials.csv`, applies any overrides present in `quantitative_overrides`, reports the diff, and maintains file integrity.
