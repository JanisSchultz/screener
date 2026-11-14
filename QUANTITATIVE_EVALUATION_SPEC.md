# Quantitative Evaluation Framework Specification (v7.0)
## Quality & Moat Screener — Sure & Simple Explicit Mauboussin-Fade DCF & Bellman-Consistent 5Y IRR

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent quantitative valuation** of individual public companies within the Quality & Moat Screener (v7.0). It can be executed entirely standalone by an AI agent or analyst to model fair value, margin of safety, and expected internal rate of return (IRR) across a 5-year business cycle.

### The Slump-Cannibal Compounder & Explicit DCF Doctrine
Grounded in the investment philosophies of **Charlie Munger**, **Warren Buffett**, **Michael Mauboussin**, and **Chris Hohn**, high-quality compounders that pass the 6 Munger Quality Gates are valued via a **Sure & Simple Explicit $N$-Year Mauboussin-Fade Discounted Cash Flow (DCF) model** at a discount rate of $r = 8.50\%$ ($r_{\text{fin}} = 10.25\%$ for Balance-Sheet Financials):
1. **Cost-Bloat Guarded Growth Ceiling ($g_0$ / `g_org_exp`)**: Anchored on $\min(\text{Sales WLS CAGR},\; 0.70 \times \text{OpCost WLS CAGR} + 0.30 \times \text{Sales WLS CAGR})$, capped at `par_g_anchor_max = 18.0%`. Crucially, a temporary 1-year revenue slump (`sales_1y`) does not depress the company's structural organic growth ceiling, while operating cost bloat ($\text{OpCost CAGR} > \text{Sales CAGR}$) can never award growth faster than top-line revenue compounding.
2. **Miller–Modigliani Zero-Spread Invariant Explicit $N$-Year DCF ($r = 8.50\% / 10.25\%$, $100\%$ Weight)**: Year 1 starts at normalized run-rate Owner Earnings $E_1 = 1.0$. At the end of each year $t = 1 \dots N$ ($N = \text{Gate 4 CAP}$ years), reinvestment $\text{Reinv}_t = E_t \cdot \max(0, g_t) / \text{RONIC}_t$ is deducted from $E_t$ to fund Year-$(t+1)$ growth $E_{t+1} = E_t(1 + g_t)$, with $(g_t, \text{RONIC}_t)$ fading linearly from $(g_0, \text{RONIC}_0)$ at $t=1$ to $(\min(g_0, 3.5\%), \min(\text{RONIC}_0, 20.0\%))$ at $t=N$, and terminal value $\text{TV}_N = E_{N+1} / r$. When $\text{RONIC}_t = r$, $\text{Fair P/E} \equiv 1/r$ identically for all $g_0$ and $N$.
3. **Bellman-Consistent 5-Year Expected IRR (`irr_5y`)**: Solves directly on the Year 1–5 DCF cash flows $\text{FCF}_1 \dots \text{FCF}_5$ plus the exact Year-5 DCF continuation value $V_5 = (\text{Fair P/E} - \sum_{t=1}^{5} \text{FCF}_t(1+r)^{-t})(1+r)^5$, guaranteeing $\text{IRR}_{5\text{y}} \equiv r$ whenever $\text{Price} = \text{Fair Value}$ with zero sign contradictions against `vs_par`.
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

## 3. Step-by-Step Valuation Methodology (v7.0)

---

### Step 1: Owner EPS Calculation, Lease/Impairment Normalization & Peak Selection (v7.0)

1. **Owner EPS Definition, Deterministic D&A & IFRS-16 Lease Normalization (Per Fiscal Year)**:
   $$\text{Owner Add-Back}_y = \max\!\left(0,\; \text{D\&A}_{y,\text{clean}} - \text{CapEx}_y - 0.20 \times \overline{\text{Lease}}_y\right), \qquad \text{Owner EPS}_y = \frac{\text{Net Income}_y + \text{Owner Add-Back}_y}{\text{Diluted Shares}_y}$$
   - **Deterministic D&A Priority**: Extracted in strict priority order: cash-flow statement `depreciation` $\to$ income-statement `depreciationAndAmortization` $\to$ `reconciledDepreciation` (replacing `max(...)` across tags).
   - **Impairment Guard (`clean_da`)**: Each year's D&A is capped at $1.5\times$ the median of the prior 3 fiscal years (`DA_IMPAIRMENT_CAP = 1.5`) so one-off goodwill or intangible write-downs folded into D&A are not added back as recurring earnings.
   - **IFRS-16 Right-of-Use Lease Depreciation Deduction (`LEASE_DEP_RATE = 0.20`)**: For IFRS filers in `eu` and `ca`, IFRS-16 capitalizes operating store/facility leases onto the balance sheet (`capitalLeaseObligations`), routing rent payments through D&A and financing cash flows while excluding lease additions from cash CapEx. Deducting $20\%$ of average `capitalLeaseObligations` ($\overline{\text{Lease}}_y$) from both `owner_addback` and `true_fcf` (`fcf_conv`) prevents lease amortization from inflating Owner EPS or FCF conversion. US GAAP filers (`us`, plus Canadian US-GAAP filers `WCN.CA`, `CP.CA`, `QSR.CA`, `SHOP.CA`) already expense operating lease cost inside operating cash flow and are excluded (`lease` series cleared).
   - *Scaled to reported diluted EPS (`cur_oe_eps` exported directly on the diluted share basis) when net income includes minority interests. Latest fiscal-year add-back is stored in `owner_add_m`.*

2. **Spike Stripping (One-Off Earnings Spikes)**:
   Non-cash windfall gains (tax-allowance releases, subsidiary disposal gains, hedge marks) must be stripped from the Owner EPS series:
   - A year is flagged as an unrepeatable spike if:
     - $\text{Net Income} > 1.10 \times \text{Operating Cash Flow}$, **AND**
     - $\text{Net Income} > 1.30 \times \text{prior year Net Income}$, **AND**
     - $\text{Net Income} > 1.30 \times \text{following year Net Income}$ (or for latest year: $+50\%$ vs prior and $> 1.30 \times \text{OCF}$).

3. **Peak Owner EPS Selection, Override (`peak_eps_est`) & 50/50 Mid-Cycle Reversion Standard**:
   - `peak_oe_eps`: The highest valid Owner EPS in the last 5 fiscal years.
   - `cur_oe_eps`: Latest fiscal-year Owner EPS on the exact diluted share basis (falling back to implied $\text{Price} \times \frac{\text{Net Income} + \text{owner\_add\_m}}{\text{Market Cap}}$ only if `cur_oe_eps` is absent).
   - **Analyst Override (`peak_eps_est`)**: Required when:
     - The reported peak contains an unrepeatable operational windfall (e.g. pandemic freight rates, cyclical commodity peak).
     - Recent strategic spin-offs or restructurings distorted historical share counts or continuing operations.
   - **The 50/50 Mid-Cycle Reversion Standard**:
     When `peak_eps_est` is not explicitly populated, active earning power is protected against stale or bubble peaks:
     - If `fin_note` flags a multi-class share-basis mismatch (`"check share basis"`), $\text{cur\_eps}$ defaults to `peak_oe_eps`; if `fin_note` flags `"non-cash earnings spike left out of peak"` or $\text{cur\_eps} > 1.5 \times \text{peak\_oe\_eps}$, $\text{cur\_eps}$ is capped at `peak_oe_eps`.
     - If $\text{cur\_eps} < \text{peak\_oe\_eps}$:
       $$\text{Active Peak EPS} = 0.5 \times \left(\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})\right)$$
     - If $\text{cur\_eps} \ge \text{peak\_oe\_eps}$: $\text{Active Peak EPS} = \text{peak\_oe\_eps}$.
   - **Active Peak EPS Summary**:
     $$\text{Active Peak EPS} = \begin{cases} \text{peak\_eps\_est} & \text{if populated} \\ 0.5 \times (\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})) & \text{if } \text{cur\_eps} < \text{peak\_oe\_eps} \\ \text{peak\_oe\_eps} & \text{otherwise} \end{cases}$$

---

### Step 2: Operating ROIC Normalization, M&A Capital Matching & Single Initial Cap (`par_roic_cap = 50%`) (v7.0)

To prevent accounting distortions from penalizing capital-light compounders while ensuring M&A goodwill is matched to M&A-driven growth:
1. **Short-Term Investments Netting, M&A Goodwill Neutralization & Denominator Floor**:
   - Operating cash $\text{Cash}_{\text{op}}$ nets both cash & equivalents and marketable short-term treasury investments (`cashAndShortTermInvestments`, stored in `cash_sti` and exported in `cash_m`) from Invested Capital:
     $$\text{IC}_{\text{GAAP}} = \text{Equity} + \text{Debt} - \text{Cash}_{\text{op}} \qquad \left(\text{floored at } 0.25 \times \text{Tangible Operating Assets when } \text{IC}_{\text{GAAP}} \le 0\right)$$
   - **Operating ROIC (Tangible Capital Return)** deducts Goodwill and Intangibles from Invested Capital, floored at $\frac{1}{3} \times \text{IC}_{\text{GAAP}}$:
     $$\text{Operating ROIC} = \frac{\text{NOPAT}}{\max\!\left(\text{Equity} + \text{Debt} - \text{Cash}_{\text{op}} - \text{Goodwill} - \text{Intangibles},\; \frac{1}{3}\text{IC}_{\text{GAAP}}\right)}$$
2. **M&A-Matched Harmonic RONIC & Single Initial Cap (`par_roic_cap = 0.50`)**:
   - Replaces the legacy two-step log compression + Galton pre-fade ($\text{ROIC}_{\text{log}} \to \text{ROIC}_{\text{exp}}$) with a single initial cap $\text{RONIC}_0 \le 50.0\%$ (`par_roic_cap = 0.50`, unless overridden by `roic_est`), leaving all mean-reversion to the explicit Stage-1 linear fade ($\text{RONIC}_0 \to \min(\text{RONIC}_0, 20.0\%)$ over $N$ years).
   - When Goodwill exceeds $20\%$ of Invested Capital ($r_{\text{tang}} > 1.25 \times r_{\text{GAAP}}$) and Invested Capital is actively growing ($\text{cap\_growth} > 0$), marginal return on new capital $\text{RONIC}_0$ blends harmonically between Tangible Operating ROIC ($r_{\text{tang}}$) and GAAP ROIC ($r_{\text{GAAP}}$) in proportion to the M&A capital-growth share $\alpha = \text{clip}_{[0, 1]}\!\left(\frac{\text{cap\_growth}}{\max(0.04, \text{base\_org})}\right)$:
     $$\text{RONIC}_{\text{raw}} = \left(\frac{1 - \alpha}{r_{\text{tang}}} + \frac{\alpha}{r_{\text{GAAP}}}\right)^{-1}, \qquad \text{RONIC}_0 = \text{roic\_exp} = \min(0.50,\; \max(0.05,\; \text{RONIC}_{\text{raw}}))$$
3. **Active ROIC Selection (`active_roic`) & Up-C Consolidated ROE**:
   - Priority:
     1. `roic_est` (analyst override, if populated)
     2. **Balance-Sheet Financials** (`Insurance` excl. `Insurance Brokers`, `Reinsurance`, `Banks` excl. `Asset Management & Custody Banks`, `Investment Banking & Brokerage`, and `Multi-Sector Holdings`): **`roe_median`** (5-year median Return on Equity, adjusted for consolidated Net Income before non-controlling interest on Up-C structures like `IBKR` where `commonStockTotalEquity` is missing and `minorityInterest` is material) $\to$ `roic_median` $\to$ `roic_operating`
     3. **IFRIC-12 Infrastructure Concessions** (`Construction & Engineering`, `Highways & Railtracks`): **`roic_median`** (5-year median GAAP ROIC including concession intangibles) $\to$ `roic_operating`
     4. **All Other Operating & Fee Businesses**: **`roic_operating`** (5-year median Tangible Operating ROIC) $\to$ `roic_median` (GAAP).

---

### Step 3: Cost-Bloat Guarded Growth Ceiling ($g_0$ / `g_org_exp`) & Buyback Accretion (`g_exp`) (v7.0)

1. **Core Growth Parameters**:
   - `par_g_base = 0.035` (`3.5%` long-term nominal GDP terminal growth rate $g_{\text{term}}$).
   - `par_g_anchor_max = 0.180` (`18.0%` maximum organic starting growth ceiling $g_0$).
   - Share Buyback / Dilution Split:
     $$\text{bb\_eff} = \text{clamp}_{[-0.03,\, 0.035]}(\text{buyback\_yield}), \qquad \text{bb\_pos} = \max(0.0, \text{bb\_eff}), \qquad \text{bb\_org} = \min(0.0, \text{bb\_eff})$$
2. **Cost-Bloat Guarded Organic Growth Base (`base_org`) & Fallback Hierarchy**:
   - **Primary (both `opcost_cagr` and `sales_cagr` present)**:
     $$\text{base\_org} = \min\!\left(\text{sales\_cagr},\; 0.70 \times \text{opcost\_cagr} + 0.30 \times \text{sales\_cagr}\right)$$
     *Strips one-off margin expansion when $\text{OpCost CAGR} < \text{Sales CAGR}$, while ensuring cost bloat ($\text{OpCost CAGR} > \text{Sales CAGR}$) never awards growth above revenue compounding.*
   - **Fallbacks**: `opcost_cagr` $\to$ `sales_cagr` $\to$ $\text{cagr\_oe\_eps} - \text{bb\_pos}$ $\to$ `sales_1y` $\to$ $\text{g\_implied} - \text{bb\_pos}$ $\to$ `0.035`.
3. **Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Per-Share Growth Ceiling (`g_exp`)**:
   - If explicit analyst override `g_est` is populated:
     $$g_0 = g_{\text{org,exp}} = \text{clamp}_{[0.0,\, 0.18]}(g_{\text{est}} - \text{bb\_pos}), \qquad g_{\text{exp}} = \text{clamp}_{[0.0,\, 0.18 + \text{bb\_pos}]}(g_{\text{est}})$$
   - Otherwise:
     $$g_0 = g_{\text{org,exp}} = \text{clamp}_{[0.0,\, 0.18]}(\text{base\_org} + \text{bb\_org}), \qquad g_{\text{exp}} = g_{\text{org,exp}} + \text{bb\_pos}$$

---

### Step 4: Miller–Modigliani Zero-Spread Invariant Explicit $N$-Year DCF ($r = 8.50\% / r_{\text{fin}} = 10.25\%$) (v7.0)

1. **Stage 1 — Explicit Year-by-Year Mauboussin Fade Over Gate 4 CAP ($t = 1 \dots N$)**:
   Starting from Year-1 normalized run-rate Owner Earnings $E_1 = 1.0$ on existing capital $\text{IC}_0$, initial organic growth $g_0 = g_{\text{org,exp}}$, and initial marginal return $\text{RONIC}_0 = \text{ROIC}_{\text{exp}}$, both growth and marginal RONIC fade linearly across $t = 1 \dots N$ ($N = \text{Gate 4 CAP}$, default `20` years) toward terminal steady state ($g_{\text{term}} = \min(g_0, 3.5\%)$, $\text{RONIC}_{\text{term}} = \min(\text{RONIC}_0, 20.0\%)$):
   $$\text{frac}_t = \frac{t - 1}{\max(1, N - 1)}, \qquad g_t = g_0 - \text{frac}_t \cdot (g_0 - g_{\text{term}}), \qquad \text{RONIC}_t = \text{RONIC}_0 - \text{frac}_t \cdot (\text{RONIC}_0 - \text{RONIC}_{\text{term}})$$
   $$\text{Reinv}_t = \frac{\max(0.0, g_t)}{\max(0.05, \text{RONIC}_t)}, \qquad \text{FCF}_t = E_t \cdot (1 - \text{Reinv}_t), \qquad E_{t+1} = E_t \cdot (1 + g_t)$$
   $$\text{PV}_{\text{Stage 1}} = \sum_{t=1}^{N} \frac{\text{FCF}_t}{(1 + r)^t} \qquad (\text{stored in } \text{pe\_mm},\; r = 8.50\% \text{ or } 10.25\%)$$
2. **Stage 2 — Post-CAP Terminal Perpetuity Value ($t > N$)**:
   At the end of the Competitive Advantage Period ($t = N$), Year-$(N+1)$ earnings are $E_{N+1} = E_N(1 + g_N)$, and any post-CAP growth beyond Year $N$ earns $\text{RONIC} = r$ (zero NPV):
   $$\text{TV}_N = \frac{E_{N+1}}{r}, \qquad \text{PV}_{\text{Stage 2}} = \frac{\text{TV}_N}{(1 + r)^N} \qquad (\text{stored in } \text{pe\_mck},\; r = 8.50\% \text{ or } 10.25\%)$$
3. **100% Explicit DCF Fair Value Multiple (`par_mult` / `pe_vd`) & Zero-Spread Invariance**:
   $$\text{Fair P/E} = \text{par\_mult} = \text{pe\_vd} = \text{PV}_{\text{Stage 1}} + \text{PV}_{\text{Stage 2}}$$
   *Exact Miller–Modigliani Theorem: When $\text{RONIC}_t = r$ for all $t$, $\text{Fair P/E} \equiv \frac{1}{r}$ for every $g_0$ and $N$.*
4. **Industry-Specific Capital Base, Discount Rate ($r_{\text{fin}} = 10.25\%$) & Value Driver Physics**:
   - **Balance-Sheet Financial Discount Rate ($r_{\text{fin}} = 10.25\%$) & ROE Capital Base (`roe_median`)**: Used for Insurance (excl. Brokers), Reinsurance, Banks (excl. Custody), Investment Banking & Brokerage, and Multi-Sector Holdings.
   - **IFRIC-12 Concession Capital Base (`roic_median`)**: Used for Construction & Engineering and Highways & Railtracks.
   - **Mark-to-Market HoldCo / Insurer NAV Physics (`1.0x BVPS`)**: Anchored to $1.0\times$ Book Value per Share ($\text{BVPS}$).
   - **IFRIC-12 Finite Concession Annuity Physics**: When `fcf_conv > 1.25`, $\text{PV}_{\text{Stage 2}} = 0$ and $\text{par\_mult} = \text{PV}_{\text{Stage 1}}$.

---

### Step 5: Valuation Metrics & Bellman-Consistent 5Y Expected IRR (v7.0)

1. **Fair Value Price (`par_val`)**: $\text{Fair Value Price} = \text{Fair P/E} \times \text{Active Peak Owner EPS}$.
2. **Current Multiple (`cur_mult`)**: $\text{Current Multiple} = \frac{\text{Current Share Price}}{\text{Active Peak Owner EPS}}$.
3. **Discount / Premium vs Fair Value (`vs_par`)**: $\text{Discount vs Fair Value} = \frac{\text{Current Share Price}}{\text{Fair Value Price}} - 1.0$ (`Below PAR` when $\le 0$, `Above PAR` when $> 0$).
4. **Bellman-Consistent 5-Year Expected IRR (`irr_5y`)**:
   - Uses the exact Year 1–5 DCF free cash flows $\text{FCF}_1 \dots \text{FCF}_5$ and the exact Year-5 DCF continuation value $V_5$:
     $$V_5 = \left(\text{Fair P/E} - \sum_{t=1}^{\min(5, N)} \frac{\text{FCF}_t}{(1 + r)^t}\right)(1 + r)^{\min(5, N)}$$
   - Solves (via 60-step bisection on $[-50\%, +250\%]$) for the unique $\text{IRR}_{5\text{y}}$ satisfying:
     $$\text{Current Multiple} = \sum_{t=1}^{5} \frac{\text{FCF}_t}{(1 + \text{IRR}_{5\text{y}})^t} + \frac{V_5}{(1 + \text{IRR}_{5\text{y}})^5}$$
   - **Exact Identity at Fair Value**: When $\text{Price} = \text{Fair Value}$ ($\text{Current Multiple} = \text{Fair P/E}$), $\text{IRR}_{5\text{y}} \equiv r$ ($8.50\%$ or $10.25\%$) identically across all companies; $\text{IRR}_{5\text{y}} > r \iff \text{vs\_par} < 0$.
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
