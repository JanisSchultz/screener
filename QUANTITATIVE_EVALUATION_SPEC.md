# Quantitative Evaluation Framework Specification (v6.31)
## Quality & Moat Screener — Equity Bond Below PAR Valuation Model

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent quantitative valuation** of individual public companies within the Quality & Moat Screener (v6.31). It can be executed entirely standalone by an AI agent or analyst to model fair value, margin of safety, and expected internal rate of return (IRR) across a 5-year business cycle.

### The Equity Bond Below PAR Doctrine
Grounded in the investment philosophies of **Charlie Munger**, **Warren Buffett**, and **Chris Hohn**, high-quality compounders that pass the 6 Munger Quality Gates are treated as **equity bonds** paying an expanding owner cash coupon:
1. **Through-the-Cycle Fundamental Value (PAR Value)**: Market multiples fluctuate between irrational euphoria and panic. Fundamental PAR Multiple represents the intrinsic through-the-cycle multiple governed by three fundamental pillars: (1) secular growth, (2) historical cycle multiple midpoint, and (3) operating capital efficiency.
2. **The 5-Year Cycle High Guardrail**: Through-the-cycle fair value can **never** exceed the highest multiple the market was willing to pay at the peak of the 5-year cycle (`mult_high_5y`). This prevents balance-sheet financials and cyclical peaks from inflating into fantasy multiples.
3. **Buying Below PAR**: The highest-probability path to superinvestor returns is purchasing world-class compounders when the current share price trades at a discount to fundamental PAR Value ($\text{Price} \le \text{PAR Value}$), capturing both the ongoing business coupon and the 5-year "Pull-to-PAR" multiple expansion.
4. **Prerequisite**: In standard screening workflow, quantitative valuation is performed on companies that achieve **`Quality pass`** across the 6 qualitative gates or **`Calamity pass`** (conditional override on Gates 3b, 5, and/or 6). For **`Calamity pass`** businesses, explicitly check whether normalized earning power (`peak_eps_est`) or forward growth (`g_est` / `g_implied`) needs a haircut rather than extrapolating pre-calamity peaks unadjusted.

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

## 3. Step-by-Step Valuation Methodology (v6.23)

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
     - If current TTM EPS ($\text{cur\_eps} = \text{Price} \times \frac{\text{Net Income}}{\text{Market Cap}}$) falls below `peak_oe_eps`:
       $$\text{Active Peak EPS} = 0.5 \times \left(\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})\right)$$
     - If $\text{cur\_eps} \ge \text{peak\_oe\_eps}$: $\text{Active Peak EPS} = \text{peak\_oe\_eps}$.
   - **Active Peak EPS Summary**:
     $$\text{Active Peak EPS} = \begin{cases} \text{peak\_eps\_est} & \text{if populated} \\ 0.5 \times (\text{peak\_oe\_eps} + \max(0.0, \text{cur\_eps})) & \text{if } \text{cur\_eps} < \text{peak\_oe\_eps} \\ \text{peak\_oe\_eps} & \text{otherwise} \end{cases}$$

---

### Step 2: Operating ROIC Normalization (v6.23 Tangible Capital Standard)

To prevent accounting distortions from penalizing capital-light compounders:
1. **The M&A Goodwill Neutralization Principle**:
   - GAAP ROIC includes historical accumulated goodwill and acquired intangibles in the denominator:
     $$\text{GAAP ROIC} = \frac{\text{NOPAT}}{\text{Total Invested Capital (including Goodwill)}}$$
   - When a capital-light toll booth completes a strategic acquisition (e.g. S&P Global's 2022 IHS Markit merger added \$52.8B of goodwill), its GAAP ROIC collapses (11.8%), artificially deflating its fundamental multiple.
   - **Operating ROIC (Tangible Capital Return)** restores economic reality:
     $$\text{Operating ROIC} = \frac{\text{NOPAT}}{\text{Tangible Invested Capital}} = \frac{\text{NOPAT}}{\text{Equity} + \text{Debt} - \text{Cash} - \text{Goodwill} - \text{Intangibles}}$$
2. **Negative Tangible Capital Standard**:
   - Monopolies operating on negative net working capital and deferred customer revenues earn structurally unbounded returns on tangible capital. They automatically receive the maximum parameter cap:
     $$\text{par\_roic\_cap} = 35.0\%$$
   - True asset-heavy businesses (WM, UNP, CAT) retain their lower physical capital ROIC (12%–15%).
3. **Active ROIC & Multiple Factor**:
   - Priority: `roic_est` (override) > `roic_operating` (tangible) > `roic_median` (GAAP).
   - ROIC Multiple Factor:
     $$\text{t\_roic} = \min(\text{Active ROIC} \times 100, 35.0)$$

---

### Step 3: 3-Anchor Starting Growth ($g_{\text{start}}$) & Logarithmic Mauboussin Decay Curve ($g_{\text{exp}}$) (v6.31)

Grounded in empirical base-rate regression (Michael Mauboussin & Dan Callahan) and constant-ROIC capital reinvestment physics, the growth engine computes an objective **Starting Growth Rate ($g_0$ / `g_start`)** from three equal-weighted anchors and fades it smoothly toward long-term nominal GDP (`par_g_base = 3.5%`) to produce **Expected Growth ($g_{\text{exp}}$ / `g_exp`)**:

1. **Core Growth & Decay Curve Parameters**:
   - `par_g_base = 0.035` (`3.5%` long-term nominal GDP gravity anchor).
   - `par_g_anchor_max = 0.220` (`22.0%` ceiling on each individual starting growth anchor).
   - `par_g_1y_floor = -0.040` (`-4.0%` floor on Anchor 1 during single-year cyclical contractions).
   - `par_g_log_k = 0.120` ($k = 12.0\%$ logarithmic compression curvature constant above nominal GDP).
   - `par_fade_cap30 = 0.85`, `par_fade_cap20 = 0.75`, `par_fade_cap15 = 0.62`, `par_fade_default = 0.75` (Mauboussin Gate 4 CAP persistence weights).
   - `size_factor = clamp(1.08 - 0.11 * log10(max(1.0, Rev_USD_B)), 0.72, 1.05)` (continuous log-revenue size factor).

2. **Step A — 3-Anchor Starting Growth ($g_{\text{start}} = (g_{\text{1y}} + g_{\text{hist}} + g_{\text{cap}}) / 3$)**:
   Let $\text{bb\_eff} = \text{clamp}_{[-0.03,\, 0.025]}(\text{buyback\_yield})$:
   - **Anchor 1 — Near-Term 1Y Momentum ($g_{\text{1y}}$)**:
     $$g_{\text{1y}} = \text{clamp}_{[-0.04,\, 0.22]}\!\left(\text{sales\_1y} + \text{bb\_eff}\right)$$
     Captures immediate operating momentum (if last year was weak, recovery takes time; if strong, near-term momentum carries forward).
   - **Anchor 2 — Medium-Term 3–5Y Evidence ($g_{\text{hist}}$)**:
     $$\text{top\_5y} = \max(0, \text{sales\_cagr}) + \text{bb\_eff}$$
     $$g_{\text{hist}} = \text{clamp}_{[0.0,\, 0.22]}\!\left(\begin{cases} 0.5 \cdot \text{top\_5y} + 0.5 \cdot \max(0, \text{cagr\_oe\_eps}) & \text{if } \text{cagr\_oe\_eps} < \text{top\_5y} \\ \text{top\_5y} & \text{otherwise} \end{cases}\right)$$
     Captures verified multi-year top-line compounding, tempered 50/50 if bottom-line per-share earnings lagged top-line + buybacks (margin contraction check).
   - **Anchor 3 — Operating Capital Growth at Constant ROIC ($g_{\text{cap}}$)**:
     At constant Operating ROIC ($\text{ROIC} = \text{NOPAT}/\text{Capital}$), the organic growth rate sustainable from actual capital expansion is identically the growth rate of the operating capital base ($\text{Reinvestment Rate} \times \text{ROIC} = \frac{\Delta \text{Capital}}{\text{NOPAT}} \times \frac{\text{NOPAT}}{\text{Capital}} = g_{\text{Capital}}$):
     $$g_{\text{cap}} = \text{clamp}_{[0.0,\, 0.22]}\!\left(\max(0, \text{cap\_growth}) + \text{bb\_eff}\right)$$
     where `cap_growth` is the 5-year median annual growth rate of Operating Assets ($\text{Total Assets} - \text{Cash}$) blended 50/50 with positive Invested Capital ($\text{Equity} + \text{Debt} - \text{Cash}$) median annual growth.

3. **Step B — Logarithmic Compression & Continuous Mauboussin Decay to Expected Growth ($g_{\text{exp}}$)**:
   - **Asymmetric "No Free Lunch" Rule ($g_{\text{start}} \le 3.5\%$ )**: Slow growers below $3.5\%$ never mean-revert upward:
     $$g_{\text{exp}} = \max(0.02, g_{\text{start}})$$
   - **Logarithmic Compression & Mauboussin Fade ($g_{\text{start}} > 3.5\%$ )**:
     $$g_{\text{log}} = 0.035 + 0.12 \times \ln\!\left(1 + \frac{g_{\text{start}} - 0.035}{0.12}\right)$$
     $$g_{\text{exp}} = \min\!\left(\text{Scale\_Cap}_{\text{rev}},\; 0.035 + (g_{\text{log}} - 0.035) \times \text{pers} \times \text{size\_factor}\right)$$
     where Gate 4 CAP sets both persistence ($\text{pers} \in \{0.85, 0.75, 0.62\}$) and Pillar 1 growth slope ($M_{\text{cap}} \in \{240.0, 200.0, 170.0\}$ for CAP $\ge 30, \ge 20, \ge 15$ years).

4. **Multiplicative Reinvestment Efficiency ($\eta_{\text{reinv}}$) & Growth Multiple Factor**:
   - Scales growth credit by implied free-cash-flow payout capacity $(1 - g_{\text{exp}}/\text{ROIC})$ relative to the $35\%$ capital-light compounder standard (`par_roic_cap / 100`), clamped to $[0.25, 1.00]$:
     $$\eta_{\text{reinv}} = \text{clamp}_{[0.25,\, 1.00]}\!\left(\frac{1 - \frac{g_{\text{exp}}}{\text{ROIC}_{\text{eff}}}}{1 - \frac{g_{\text{exp}}}{0.35}}\right)$$
   - **Effective Growth Slope**: $M_{\text{eff}} = M_{\text{cap}} \times \eta_{\text{reinv}}$.
   - **Growth Multiple Factor**:
     $$\text{t\_growth} = \min(40.0, M_{\text{eff}} \times \max(0, g_{\text{exp}}))$$

---

### Step 4: 3-Pillar Fundamental PAR Multiple & Cycle High Guardrail

The fundamental multiple is governed by three equal pillars:
1. **Pillar 1: Secular Growth Factor**: $\text{t\_growth} = \min(40.0, M_{\text{eff}} \times \max(0, g_{\text{exp}}))$.
2. **Pillar 2: Historical Cycle Midpoint Multiple**: $\text{t\_hist} = \min(\text{par\_hist\_cap}, 0.5 \times (\text{mult\_low\_5y} + \text{mult\_high\_5y}))$, where `par_hist_cap = 35.0` neutralizes 2021 ZIRP bubble and depressed-denominator spikes.
3. **Pillar 3: Operating ROIC Factor**: $\text{t\_roic} = \min(\text{Active ROIC} \times 100, 35.0)$.

$$\text{Raw PAR Multiple} = \frac{\text{t\_growth} + \text{t\_hist} + \text{t\_roic}}{3}$$

#### The 5-Year Cycle High Guardrail
A core tenet of value investing: through-the-cycle fair value can **never** exceed the highest multiple the market was willing to pay at the peak of the 5-year cycle:
$$\text{PAR Multiple} = \min(\text{Raw PAR Multiple}, \text{mult\_high\_5y})$$

---

### Step 5: Valuation Metrics & Status

1. **PAR Value**:
   $$\text{PAR Value} = \text{PAR Multiple} \times \text{Active Peak Owner EPS}$$
2. **Current Multiple**:
   $$\text{Current Multiple} = \frac{\text{Current Share Price}}{\text{Active Peak Owner EPS}}$$
3. **% vs PAR**:
   $$\% \text{ vs PAR} = \frac{\text{Current Share Price}}{\text{PAR Value}} - 1.0$$
   - **Valuation Status**:
     - `Below PAR`: Current Price $\le$ PAR Value ($\% \text{ vs PAR} \le 0$). **ATTRACTIVE ENTRY**.
     - `Above PAR`: Current Price $>$ PAR Value ($\% \text{ vs PAR} > 0$). **PREMIUM / HOLD**.
4. **5-Year Expected Cycle IRR (Pull-to-PAR)**:
   $$\text{5Y Expected IRR} = (1 + g_{\text{exp}}) \times \left(\frac{\text{PAR Value}}{\text{Current Share Price}}\right)^{0.2} + \text{Dividend Yield} - 1.0$$
   *Where $\text{Dividend Yield} = \text{dividends\_ttm\_m} \div \text{market\_cap\_m}$.*
5. **Market-Implied Growth ($g_{\text{market}}$) & Growth Margin of Safety**:
   - Exact closed-form inversion of the 3-Pillar PAR Multiple formula reveals the growth rate priced into the current market multiple:
     $$g_{\text{market}} = \frac{3 \times \text{Current Multiple} - \text{t\_hist} - \text{t\_roic}}{M_{\text{eff}}}$$
   - **Growth Margin of Safety**:
     $$\text{Growth Margin} = g_{\text{exp}} - g_{\text{market}}$$
6. **Market-Implied CAP & Moat Runway Margin**:
   - Years of excess returns priced into the market quote:
     $$\text{Market-Implied CAP} = \text{Fundamental CAP} \times \frac{\text{Current Share Price}}{\text{PAR Value}}$$
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
    "roic_est": 0.35,
    "fin_note": "Operating ROIC normalized to 35.0% cap neutralizing $52.8B IHS Markit accounting goodwill. 5-10Y g of 10.5% driven by bond issuance recovery, Market Intelligence recurring analytics, and index volume."
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
| `g_est` | `g_est` | Float or null | Discretionary forward growth override (e.g. `0.09`) |
| `g_implied` | `g_implied` | Float or null | Fundamental bottom-up growth estimate (e.g. `0.105`) |
| `roic_est` | `roic_est` | Float or null | Normalized Operating ROIC override (e.g. `0.35`) |
| `fin_note` | `fin_note` | String or null | Financial rationale for overrides & capital structure |

---

## 5. Ingestion via `screener/apply_evaluation.py`

When the agent returns this JSON payload, apply it directly to `data/<universe>/financials.csv`:
```bash
python3 screener/apply_evaluation.py --input quantitative_result.json
```
The script locates the company in `financials.csv`, applies any overrides present in `quantitative_overrides`, reports the diff, and maintains file integrity.
