# Quantitative Evaluation Framework Specification (v6.34)
## Quality & Moat Screener — Equity Bond Below PAR Valuation Model

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent quantitative valuation** of individual public companies within the Quality & Moat Screener (v6.34). It can be executed entirely standalone by an AI agent or analyst to model fair value, margin of safety, and expected internal rate of return (IRR) across a 5-year business cycle.

### The Equity Bond Below PAR Doctrine
Grounded in the investment philosophies of **Charlie Munger**, **Warren Buffett**, and **Chris Hohn**, high-quality compounders that pass the 6 Munger Quality Gates are treated as **equity bonds** paying an expanding owner cash coupon:
1. **Through-the-Cycle Fundamental Value (PAR Value)**: Market multiples fluctuate between irrational euphoria and panic. Fundamental PAR Multiple represents the intrinsic through-the-cycle multiple governed `75%` by the **Textbook Corporate Finance Organic Value Driver P/E** ($\text{PE}_{\text{VD}} = 0.50 \cdot \text{PE}_{\text{MM}} + 0.50 \cdot \text{PE}_{\text{McK}}$, driven by Gate 4 CAP $N$, Organic Expected Growth $g_{\text{org,exp}}$, and Expected ROIC $\text{ROIC}_{\text{exp}}$) and `25%` by the **Regime-Bounded 5-Year Historical Harmonic P/E** ($t_{\text{hist}} = \text{clamp}_{[0.50\text{x},\, 1.50\text{x}]\cdot\text{PE}_{\text{VD}}}\!\left(\frac{2 \cdot \text{Low}_{5\text{Y}} \cdot \text{High}_{5\text{Y}}}{\text{Low}_{5\text{Y}} + \text{High}_{5\text{Y}}}\right)$).
2. **Market Regime Calibration Without Bubble Contamination**: Blending `25%` of the 5-year Harmonic P/E (the midpoint of 5Y Earnings Yield $E/P$) naturally dampens single-year trough-earnings P/E dips while allowing actual market valuation regimes (bull vs. bear markets and US vs. European/Canadian multiple regimes) to calibrate the textbook P/E — bounded within $[0.50\text{x}, 1.50\text{x}]$ of $\text{PE}_{\text{VD}}$ so `70x–96x` speculative bubble or accounting-trough outliers cannot distort intrinsic PAR Value.
3. **Buying Below PAR**: The highest-probability path to superinvestor returns is purchasing world-class compounders when the current share price trades at a discount to fundamental PAR Value ($\text{Price} \le \text{PAR Value}$), capturing both the ongoing business coupon and the 5-year "Pull-to-PAR" multiple expansion.
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

## 3. Step-by-Step Valuation Methodology (v6.34)

---

### Step 1: Owner EPS Calculation & Peak Normalization

1. **Owner EPS Definition (Per Fiscal Year)**:
   $$\text{Owner EPS} = \frac{\text{Net Income} + \max(0, \text{D\&A} - \text{CapEx})}{\text{Diluted Shares}}$$
   *Scaled to reported diluted EPS when net income includes minority interests.*

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
     - If current Owner EPS ($\text{cur\_eps} = \text{Price} \times \frac{\text{Net Income} + \max(0, \text{D\&A} - \text{CapEx})}{\text{Market Cap}}$, latest fiscal year) falls below `peak_oe_eps`:
       $$\text{Active Peak EPS} = 0.5 \times \left(\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})\right)$$
     - If $\text{cur\_eps} \ge \text{peak\_oe\_eps}$: $\text{Active Peak EPS} = \text{peak\_oe\_eps}$.
     - *Both sides are on the same Owner EPS basis (identical D\&A − CapEx add-back), so amortisation-heavy compounders at peak are not spuriously haircut.*
   - **Active Peak EPS Summary**:
     $$\text{Active Peak EPS} = \begin{cases} \text{peak\_eps\_est} & \text{if populated} \\ 0.5 \times (\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})) & \text{if } \text{cur\_eps} < \text{peak\_oe\_eps} \\ \text{peak\_oe\_eps} & \text{otherwise} \end{cases}$$

---

### Step 2: Operating ROIC Normalization & Mauboussin Galton ROIC Regression (v6.32)

To prevent accounting distortions from penalizing capital-light compounders while eliminating arbitrary hard caps on ROIC:
1. **The M&A Goodwill Neutralization Principle & Denominator Floor**:
   - GAAP ROIC includes historical accumulated goodwill and acquired intangibles in the denominator:
     $$\text{GAAP ROIC} = \frac{\text{NOPAT}}{\text{Total Invested Capital (including Goodwill)}}$$
   - **Operating ROIC (Tangible Capital Return)** deducts Goodwill and Intangibles from Invested Capital, floored at $\frac{1}{3} \times \text{IC}_{\text{GAAP}}$ so goodwill deduction can reduce the capital base by at most two-thirds (eliminating artificial division-by-zero spikes when M&A goodwill or share buybacks exceed book equity):
     $$\text{Operating ROIC} = \frac{\text{NOPAT}}{\max\!\left(\text{Equity} + \text{Debt} - \text{Cash} - \text{Goodwill} - \text{Intangibles},\; \frac{1}{3}\text{IC}_{\text{GAAP}}\right)}$$
2. **Mauboussin Galton ROIC Regression ($\text{Expected ROIC}$)**:
   - Grounded in Michael Mauboussin's Galton regression formula ($\text{Expected ROIC} = r(\text{Current ROIC} - \text{Average ROIC}) + \text{Average ROIC}$), excess Operating ROIC above the corporate mean ($\text{ROIC}_{\text{avg}} = 12.0\%$) is first logarithmically compressed ($k_{\text{roic}} = 0.25$) and then faded by Gate 4 CAP persistence $r = \text{pers} \in \{0.85, 0.75, 0.62\}$:
     $$\text{ROIC}_{\text{log}} = 0.12 + 0.25 \times \ln\!\left(1 + \frac{\text{Active ROIC} - 0.12}{0.25}\right)$$
     $$\text{Expected ROIC} = r \times (\text{ROIC}_{\text{log}} - 0.12) + 0.12$$
3. **Active ROIC Selection**:
   - Priority: `roic_est` (override) > `roic_median` (for Balance-Sheet Financials & IFRIC-12 Concessions) > `roic_operating` (tangible) > `roic_median` (GAAP).
   - Feeds directly into $\text{Expected ROIC}$ for Anchor 3 Galton capital fade and Step 4 Corporate Finance Value Driver P/E ($\text{PE}_{\text{VD}}$).

---

### Step 3: 3-Anchor Starting Growth ($g_{\text{start}}$), Organic Firm Growth ($g_{\text{org}}$), Operating Cost Smoothing & Logarithmic Mauboussin Decay Curve ($g_{\text{exp}}$) (v6.34)

Grounded in empirical base-rate regression (Michael Mauboussin & Dan Callahan), operating cost verification ($\text{OpCost} = \text{Sales} - \text{EBIT}$), and Galton-regressed capital reinvestment physics, the growth engine computes **Per-Share Starting Growth ($g_0$ / `g_start`)** alongside **Organic Firm Starting Growth (`g_org_start`, stripping positive buybacks while retaining share dilution)** and fades both smoothly toward long-term nominal GDP (`par_g_base = 3.5%`) to produce **Per-Share Expected Growth (`g_exp`)** and **Organic Expected Growth (`g_org_exp`)**:

1. **Core Growth & Decay Curve Parameters**:
   - `par_g_base = 0.035` (`3.5%` long-term nominal GDP gravity anchor).
   - `par_g_anchor_max = 0.220` (`22.0%` ceiling on each individual starting growth anchor).
   - `par_g_1y_floor = -0.040` (`-4.0%` floor on Anchor 1 during single-year cyclical contractions).
   - `par_g_log_k = 0.120` ($k = 12.0\%$ logarithmic compression curvature constant above nominal GDP).
   - `par_fade_cap30 = 0.85`, `par_fade_cap20 = 0.75`, `par_fade_cap15 = 0.62`, `par_fade_default = 0.75` (Mauboussin Gate 4 CAP persistence weights).
   - `size_factor = clamp(1.08 - 0.11 * log10(max(1.0, Rev_USD_B)), 0.72, 1.05)` (continuous log-revenue size factor).

2. **Step A — 3-Anchor Starting Growth ($g_{\text{start}} = (g_{\text{1y}} + g_{\text{hist}} + g_{\text{cap}}) / 3$) & Parallel Organic Starting Growth ($g_{\text{org,start}}$)**:
   Let $\text{bb\_eff} = \text{clamp}_{[-0.03,\, 0.025]}(\text{buyback\_yield})$, $\text{bb\_org} = \min(0.0, \text{bb\_eff})$, and $\text{OpCost}_y = \text{Sales}_y - \text{EBIT}_y$ (with `opcost_1y` clamped to $[-40\%, +60\%]$ and `opcost_cagr` clamped to $[-25\%, +45\%]$):
   - **Anchor 1 — Near-Term 1Y Momentum with Operating Cost Smoothing ($g_{\text{1y}}$)**:
     $$\text{sales\_1y\_eff} = \begin{cases} 0.5 \cdot \text{sales\_1y} + 0.5 \cdot \min(\text{sales\_1y}, \text{opcost\_1y}) & \text{if } \text{sales\_1y} \ge 0 \text{ and } \text{opcost\_1y} \text{ present} \\ 0.5 \cdot \text{sales\_1y} + 0.5 \cdot \text{opcost\_1y} & \text{if } \text{sales\_1y} < 0 \text{ and } \text{opcost\_1y} \text{ present} \\ 0.5 \cdot \text{sales\_1y} + 0.5 \cdot \max(0, \text{sales\_cagr}) & \text{if } \text{opcost\_1y} \text{ missing and } \text{sales\_1y} > 25\% \\ \text{sales\_1y} & \text{otherwise} \end{cases}$$
     $$g_{\text{1y}} = \text{clamp}_{[-0.04,\, 0.22]}\!\left(\text{sales\_1y\_eff} + \text{bb\_eff}\right)$$
     Tempers one-off 1Y pricing/margin spikes while cushioning 1Y cyclical volume dips where operating capacity is retained, and never rewards cost bloat ($\text{opcost\_1y} > \text{sales\_1y}$).
   - **Anchor 2 — Medium-Term 3–5Y Evidence with Operating Cost Smoothing ($g_{\text{hist}}$)**:
     $$\text{sales\_5y\_eff} = 0.5 \cdot \text{sales\_cagr} + 0.5 \cdot \min(\text{sales\_cagr}, \text{opcost\_cagr})$$
     $$\text{top\_5y} = \max(0, \text{sales\_5y\_eff}) + \text{bb\_eff}$$
     $$g_{\text{hist}} = \text{clamp}_{[0.0,\, 0.22]}\!\left(\begin{cases} 0.5 \cdot \text{top\_5y} + 0.5 \cdot \max(0, \text{cagr\_oe\_eps}) & \text{if } \text{cagr\_oe\_eps} < \text{top\_5y} \\ \text{top\_5y} & \text{otherwise} \end{cases}\right)$$
   - **Anchor 3 — Operating Capital Growth with Mauboussin Galton ROIC Fade ($g_{\text{cap}}$)**:
     Existing capital earns $\text{ROIC}_{\text{log}}$ while incremental capital $\Delta \text{Capital}$ earns $\text{Expected ROIC}$, scaling organic capital expansion by $\text{ROIC\_Fade\_Ratio} = \frac{\text{Expected ROIC}}{\text{ROIC}_{\text{log}}}$:
     $$g_{\text{cap}} = \text{clamp}_{[0.0,\, 0.22]}\!\left(\max(0, \text{cap\_growth}) \times \frac{\text{Expected ROIC}}{\text{ROIC}_{\text{log}}} + \text{bb\_eff}\right)$$
     where `cap_growth` is the 5-year median annual growth rate of Operating Assets ($\text{Total Assets} - \text{Cash}$) blended 50/50 with positive Invested Capital ($\text{Equity} + \text{Debt} - \text{Cash}$) median annual growth.
   - **Parallel Organic Starting Growth (`g_org_start`)**: Computed identically across all three anchors replacing `bb_eff` with $\text{bb\_org} = \min(0.0, \text{bb\_eff})$ (and stripping $\max(0.0, \text{bb\_eff})$ from `cagr_oe_eps` in Anchor 2).

3. **Step B — Logarithmic Compression & Continuous Mauboussin Decay to Expected Growth ($g_{\text{exp}}$ & $g_{\text{org,exp}}$)**:
   - **Explicit Analyst Override (`g_est`) vs. Fallback (`g_implied`)**:
     - `g_est` is the sole explicit discretionary override for `g_exp` (clamped by `scale_cap`).
     - `g_implied` is strictly an informational bottom-up reference and missing-statement fallback (used only when all statement growth anchors are absent).
   - **Asymmetric "No Free Lunch" Rule ($g_{\text{start}} \le 3.5\%$ )**: Slow growers below $3.5\%$ never mean-revert upward:
     $$g_{\text{exp}} = \max(0.02, g_{\text{start}})$$
   - **Logarithmic Compression & Mauboussin Fade ($g_{\text{start}} > 3.5\%$ )**:
     $$g_{\text{log}} = 0.035 + 0.12 \times \ln\!\left(1 + \frac{g_{\text{start}} - 0.035}{0.12}\right)$$
     $$g_{\text{exp}} = \min\!\left(\text{Scale\_Cap}_{\text{rev}},\; 0.035 + (g_{\text{log}} - 0.035) \times \text{pers} \times \text{size\_factor}\right)$$
     where Gate 4 CAP sets persistence $\text{pers} \in \{0.85, 0.75, 0.62\}$ for CAP $\ge 30, \ge 20, \ge 15$ years. The identical curve maps `g_org_start` $\rightarrow$ `g_org_exp` (with $\text{bb\_contrib} = \max(0, g_{\text{exp}} - g_{\text{org,exp}})$).

### Step 4: Corporate Finance Organic Value Driver PAR Multiple & Regime-Bounded 5-Year Harmonic Market P/E (v6.34)

Because Corporate Finance Value Driver formulas already value `100%` of firm Free Cash Flow ($1 - g_{\text{org}}/\text{ROIC}_{\text{exp}}$) before deciding whether FCF is distributed as dividends or share buybacks, **$\text{PE}_{\text{VD}}$ is evaluated strictly on Organic Firm Expected Growth ($g_{\text{org,exp}}$)** — eliminating share-buyback double-counting in `PAR Multiple`. Fundamental PAR Multiple blends **$\text{PE}_{\text{VD}}$ (`75%` weight)** with **Regime-Bounded 5-Year Historical Harmonic P/E ($t_{\text{hist}}$, `25%` weight)**:

1. **Miller-Modigliani (1961) / Mauboussin Finite-CAP Linear Value Driver P/E ($\text{PE}_{\text{MM}}$)**:
   $$\text{PE}_{\text{MM}} = \frac{1}{k} \cdot \left[1 + \frac{g_{\text{org,exp}} \cdot N \cdot (\text{ROIC}_{\text{exp}} - k)}{(1 + k) \cdot \text{ROIC}_{\text{exp}}}\right]$$
   Separates the steady-state no-growth base value ($\frac{1}{k} = 11.43\text{x}$ at $k = 8.75\%$) from the present value of organic excess-return reinvestment over $N = \text{CAP}$ years.

2. **McKinsey *Valuation* (Koller, Goedhart & Wessels) 2-Stage Compounding Value Driver P/E ($\text{PE}_{\text{McK}}$)**:
   $$\text{PE}_{\text{McK}} = \left(1 - \frac{g_{\text{org,exp}}}{\text{ROIC}_{\text{exp}}}\right) \sum_{t=1}^{N} \left(\frac{1 + g_{\text{org,exp}}}{1 + k}\right)^t + \frac{\left(1 - \frac{g_{\text{term}}}{\text{ROIC}_{\text{term}}}\right)(1 + g_{\text{org,exp}})^N(1 + g_{\text{term}})}{(k - g_{\text{term}})(1 + k)^N}$$
   Captures geometric organic compounding during the $N$-year moat runway before transitioning to steady-state maturity ($g_{\text{term}} = 3.5\%$, $\text{ROIC}_{\text{term}} = 12.0\%$, $k = 8.75\%$).

3. **50/50 Textbook Value Driver Blend ($\text{PE}_{\text{VD}}$)**:
   $$\text{PE}_{\text{VD}} = 0.50 \cdot \text{PE}_{\text{MM}} + 0.50 \cdot \text{PE}_{\text{McK}}$$

4. **Regime-Bounded 5-Year Historical Harmonic P/E ($t_{\text{hist}}$)**:
   $$t_{\text{hist,raw}} = \frac{2 \cdot \text{mult\_low\_5y} \cdot \text{mult\_high\_5y}}{\text{mult\_low\_5y} + \text{mult\_high\_5y}}, \qquad t_{\text{hist}} = \text{clamp}_{[0.50\cdot\text{PE}_{\text{VD}},\, 1.50\cdot\text{PE}_{\text{VD}}]}(t_{\text{hist,raw}})$$
   Averaging 5-year Earnings Yields ($E/P$) dampens single-year denominator dips while the $[0.50\text{x}, 1.50\text{x}] \cdot \text{PE}_{\text{VD}}$ regime band preserves genuine compounder pricing (e.g. Hermès) while blocking `70x–96x` bubble/accounting-trough outliers.

5. **`75/25` PAR Multiple**:
   $$\text{PAR Multiple} = 0.75 \cdot \text{PE}_{\text{VD}} + 0.25 \cdot t_{\text{hist}}$$

6. **Industry-Specific Capital Base & Value Driver Physics**:
   - **GAAP ROIC (`roic_median`) Selection**: For **Balance-Sheet Financials** (`Insurance` excluding `Insurance Brokers`, `Reinsurance`, `Banks` excluding `Asset Management & Custody Banks` / `Investment Banking & Brokerage`, `Multi-Sector Holdings`) and **IFRIC-12 Infrastructure Concessions** (`Construction & Engineering`, `Highways & Railtracks`), active ROIC defaults to `roic_median` (GAAP ROIC) rather than `roic_operating` (Tangible ROIC), since statutory book equity, acquisition float, or concession intangible assets are the required operating capital base.
   - **Mark-to-Market HoldCo / Insurer NAV Physics**: For `Multi-Sector Holdings` and `Insurance` (excluding `Insurance Brokers`) with no `peak_eps_est` override where reported EPS already captures unrealized mark-to-market portfolio appreciation $\Delta\text{NAV}$ (`fcf_conv < 0.25`, or `fcf_conv is None` in `Multi-Sector Holdings` with `mult_high_5y < 12.0`), a fair $1.0\text{x}$ NAV ($\text{P/B} = 1.0\text{x}$) implies $\text{PE}_{\text{VD}} = \text{PE}_{\text{MM}} = \text{PE}_{\text{McK}} = \frac{1}{\text{ROIC}_{\text{exp}}}$ (insurers missing OCF tags in Yahoo still use standard $\text{PE}_{\text{VD}}$).
   - **IFRIC-12 Finite Concession Annuity Physics**: For `Construction & Engineering` and `Highways & Railtracks` with `fcf_conv > 1.25` (where concession assets amortize and revert to the state at expiry), Stage 2 terminal perpetuity is omitted ($\text{PV}_{\text{Stage 2}} = 0$) and $\text{PE}_{\text{MM}}$ replaces $\frac{1}{k}$ with the $N$-year finite annuity factor $A_{N,k} = \frac{1 - (1+k)^{-N}}{k}$.

---

### Step 5: Valuation Metrics & Status

1. **PAR Value**:
   $$\text{PAR Value} = \text{PAR Multiple} \times \text{Active Peak Owner EPS}$$
   *Strictly independent of current share price.*
2. **Current Multiple**:
   $$\text{Current Multiple} = \frac{\text{Current Share Price}}{\text{Active Peak Owner EPS}}$$
3. **% vs PAR**:
   $$\% \text{ vs PAR} = \frac{\text{Current Share Price}}{\text{PAR Value}} - 1.0$$
   - **Valuation Status**:
     - `Below PAR`: Current Price $\le$ PAR Value ($\% \text{ vs PAR} \le 0$). **ATTRACTIVE ENTRY**.
     - `Above PAR`: Current Price $>$ PAR Value ($\% \text{ vs PAR} > 0$). **PREMIUM / HOLD**.
4. **5-Year Expected Cycle IRR (FCF-Conserved Pull-to-PAR Cash-Flow IRR)**:
   - **Cash-Flow Conservation Cap on Buybacks ($g_{\text{irr}}$)**: Total cash returned to shareholders ($\text{Dividends} + \text{Buybacks}$) cannot exceed total Stage-1 Free Cash Flow Yield $\frac{1 - g_{\text{org,exp}}/\text{ROIC}_{\text{exp}}}{\text{Current Multiple}}$:
     $$\text{bb\_fcf\_cap} = \max\!\left(0,\; \frac{\max(0, 1 - g_{\text{org,exp}}/\text{ROIC}_{\text{exp}})}{\text{Current Multiple}} - \text{dy}\right), \qquad g_{\text{irr}} = \min\!\left(g_{\text{exp}},\; g_{\text{org,exp}} + \text{bb\_fcf\_cap}\right)$$
   - Solves for the exact 5-year internal rate of return ($\text{IRR}$) equating current share price $P_0$ to 5 years of growing dividends $D_t = D_0(1 + g_{\text{irr}})^t$ plus Year-5 terminal PAR value $P_5 = \text{PAR Value} \times (1 + g_{\text{irr}})^5$:
     $$P_0 = \sum_{t=1}^{5} \frac{D_0 (1 + g_{\text{irr}})^t}{(1 + \text{IRR})^t} + \frac{\text{PAR Value} \cdot (1 + g_{\text{irr}})^5}{(1 + \text{IRR})^5}$$
     Using $u = \frac{1 + g_{\text{irr}}}{1 + \text{IRR}}$ and $\text{dy} = \frac{D_0}{P_0} = \frac{\text{dividends\_ttm\_m}}{\text{market\_cap\_m}}$, this reduces to the strictly monotonic polynomial $\text{dy} \sum_{t=1}^{5} u^t + \left(\frac{\text{PAR Value}}{P_0}\right) u^5 = 1$, solved to machine precision via Newton-Raphson with $\text{5Y Expected IRR} = \frac{1 + g_{\text{irr}}}{u} - 1$.
5. **Market-Implied Growth ($g_{\text{market}}$) & Growth Margin of Safety**:
   - Exact inversion of the `75/25` Organic Value Driver PAR Multiple formula using $\text{PE}_{\text{VD}}(0)$, organic slope $M_{\text{eff}} = \frac{\text{PE}_{\text{VD}}(g_{\text{org,exp}}) - \text{PE}_{\text{VD}}(0)}{g_{\text{org,exp}}}$, and buyback contribution $\text{bb\_contrib} = g_{\text{exp}} - g_{\text{org,exp}}$ (guaranteeing $g_{\text{market}} = g_{\text{exp}}$ and $g_{\text{gap}} = 0$ at $\text{Price} = \text{PAR Value}$; for MTM HoldCos, $g_{\text{market}} = g_{\text{exp}} \cdot \frac{\text{Current Multiple}}{\text{PAR Multiple}}$):
     $$g_{\text{market}} = \frac{\frac{\text{Current Multiple} - 0.25 \cdot t_{\text{hist}}}{0.75} - \text{PE}_{\text{VD}}(0)}{M_{\text{eff}}} + \text{bb\_contrib}$$
   - **Growth Margin of Safety**:
     $$\text{Growth Margin} = g_{\text{exp}} - g_{\text{market}}$$
6. **Market-Implied CAP & Moat Runway Margin**:
   - Scales excess multiple above the zero-moat steady-state base multiple $\text{PE}_{\text{base}} = \frac{1}{k} = 11.43\text{x}$ (so a stock trading at $\le \frac{1}{k}$ prices in `0.0` years of moat, while $\text{Price} = \text{PAR Value}$ prices in `Fundamental CAP`):
     $$\text{Market-Implied CAP} = \max\!\left(0.0,\; \text{Fundamental CAP} \times \frac{\text{Current Multiple} - \frac{1}{k}}{\text{PAR Multiple} - \frac{1}{k}}\right)$$
     *(For Mark-to-Market HoldCos or when $\text{PAR Multiple} \le \frac{1}{k} + 0.5$, falls back to $\text{Fundamental CAP} \times \frac{\text{Price}}{\text{PAR Value}}$.)*
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
