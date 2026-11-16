# Quantitative Evaluation Framework Specification (v7.7)
## Quality & Moat Screener — Sure & Simple Explicit Mauboussin-Fade DCF & Bellman-Consistent 5Y IRR

---

## 1. Overview & Evaluator Mandate

This specification governs the **independent quantitative valuation** of individual public companies within the Quality & Moat Screener (v7.7). It can be executed entirely standalone by an AI agent or analyst to model fair value, margin of safety, and expected internal rate of return (IRR) across a 5-year business cycle.

### The Slump-Cannibal Compounder & Explicit DCF Doctrine
Grounded in the investment philosophies of **Charlie Munger**, **Warren Buffett**, **Michael Mauboussin**, and **Chris Hohn**, high-quality compounders that pass the 6 Munger Quality Gates are valued via a **Sure & Simple Explicit $N$-Year Mauboussin-Fade Discounted Cash Flow (DCF) model** at a discount rate of $r = 8.50\%$ ($r_{\text{fin}} = 10.25\%$ for Balance-Sheet Financials):
1. **4-Pillar Statistical Organic Growth Ceiling ($g_0$ / `g_org_exp`)**: Anchored on the **4-Pillar Statistical Organic Growth Estimator (`statistical_organic_g0`)** — combining a Dilution-Adjusted Per-Share Index $S_t$, Cycle-Spanning Theil–Sen non-parametric estimator ($\Delta t \ge 5\text{y}$, $P_{25}$ Lower Confidence Bound), 3-Driver Triangulation (`Revenue`, `NOPAT`, `Owner Earnings`), and Empirical Bayes precision shrinkage with smooth hyperbolic-tangent tail compression (`par_g_anchor_max = 13.0%`). Crucially, a temporary 1-year revenue slump (`sales_1y`) does not depress the company's structural organic growth ceiling, while V-shaped COVID rebounds (`AMS.ES`, `BKNG`) and stock-funded M&A dilution (`SPGI`, `ENX.FR`) are neutralized automatically.
2. **Miller–Modigliani Zero-Spread Invariant Explicit $N$-Year DCF ($r = 8.50\% / 10.25\%$, $100\%$ Weight)**: Year 1 starts at the active (trailing, normalized) Owner EPS treated as Year-1 earnings, $E_1 = 1.0$ — deliberately conservative by one year of growth versus a forward $E_1 = \text{EPS}(1+g_0)$. At the end of each year $t = 1 \dots N$ ($N = \text{Gate 4 CAP}$ years), reinvestment $\text{Reinv}_t = E_t \cdot \max(0, g_t) / \text{RONIC}_t$ is deducted from $E_t$ to fund Year-$(t+1)$ growth $E_{t+1} = E_t(1 + g_t)$, with $(g_t, \text{RONIC}_t)$ fading linearly from $(g_0, \text{RONIC}_0)$ at $t=1$ to $(\min(g_0, 3.0\%),\; \min(\text{RONIC}_0, 20.0\%, r + 0.5(\text{RONIC}_0 - r)))$ at $t=N$, and McKinsey Value-Driver terminal value $\text{TV}_N = E_{N+1}(1 - g_{\text{tv}}/\text{RONIC}_{\text{term}}) / (r - g_{\text{tv}})$ with $g_{\text{tv}} = \max(0, \min(g_0, 3.0\%))$. When $\text{RONIC}_t = r$, $\text{Fair P/E} \equiv 1/r$ identically for all $g_0 \ge 0$ and $N$.
3. **Bellman-Consistent 5-Year Expected IRR (`irr_5y`)**: Solves directly on the Year 1–5 DCF cash flows $\text{FCF}_1 \dots \text{FCF}_5$ plus the exact Year-5 DCF continuation value $V_5 = (\text{Fair P/E} - \sum_{t=1}^{5} \text{FCF}_t(1+r)^{-t})(1+r)^5$, guaranteeing $\text{IRR}_{5\text{y}} \equiv r$ whenever $\text{Price} = \text{Fair Value}$ with zero sign contradictions against `vs_par`.
4. **Prerequisite**: In standard screening workflow, quantitative valuation is performed on companies that achieve **`Quality pass`** across the 6 qualitative gates or **`Calamity pass`** (conditional override on Gates 3b, 5, and/or 6). For **`Calamity pass`** businesses, check whether normalized earning power or forward growth still reflects pre-calamity peaks. Since v7.6 there are **no analyst overrides**: every input comes from the statements, and data that cannot be valued reliably is shown as **No data** with an `[auto]` reason.

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
- **Shares Outstanding**: Historical period-end share count.

### 2.3 Computed Screening Metrics (from `screener/fetch/par.py`)
- `peak_oe_year`: Fiscal year in which the highest Owner EPS occurred within the last 5 years.
- `peak_oe_eps`: Last peak Owner EPS in quote currency.
- `mult_low_5y` / `mult_high_5y`: 5-year cycle low / high multiple = MIN / MAX of the calendar-year medians of monthly close ÷ the peak Owner EPS known at that month (a fiscal year counts from its period end + 3 months; informational, not used in Fair Value).
- `cagr_oe_eps`: Peak-to-peak Owner EPS growth ($g$): latest 5Y peak vs the prior-cycle peak, annualised over the actual gap between the two peak years.
- `ma_reinvest`: M&A reinvestment rate = $\sum \max(0, \Delta(\text{goodwill} + \text{intangibles})) \div \sum \text{NOPAT}$ over the same 10-year window as $g_0$, counting only acquisition years (goodwill itself up $> 2\%$; capitalised development, concession capex and purchase-price reallocations grow intangibles without a deal) and skipping stock-funded years (share count up $\ge 3\%$). Each year's addition is net of an FX / amortisation allowance of $0.035 \times \max(0, \text{goodwill} + \text{intangibles} - 3 \times \text{NOPAT})$; the rate is capped at 3.0.
- `cur_oe_year`: Fiscal year of the latest Owner EPS (`cur_oe_eps`).
- `p2p_ok`: Peak-to-peak test (`"Y"` = new peak vs prior cycle, `"N"` = not above prior cycle).
- `roic_median`: 5-year median GAAP ROIC (including accounting goodwill).
- `roic_operating`: 5-year median Operating ROIC (tangible capital return).
- `fcf_conv`: Multi-year Owner FCF conversion ($\text{Owner FCF} \div \text{Net Income}$).
- `fund_cap`: Fundamental Competitive Advantage Period from Gate 4 (`15`, `20`, `25`, or `30` years; deterministically derived from Gate 3 Moat Profile & Gate 4 Competitive Forces).

---

## 3. Step-by-Step Valuation Methodology (v7.7)

---

### Step 1: Owner EPS Calculation, Lease/Impairment Normalization & Peak Selection (v7.7)

1. **Owner EPS Definition, Deterministic D&A, Cash-Flow Backing & IFRS-16 Lease Normalization (Per Fiscal Year)**:
   $$\text{D\&A}_{y,\text{eff}} = \min\!\left(\text{D\&A}_{y,\text{clean}},\; \max(0,\; \text{OCF}_y - \text{Net Income}_y)\right)$$
   $$\text{Owner Add-Back}_y = \max\!\left(0,\; \text{D\&A}_{y,\text{eff}} - \text{CapEx}_y - 0.20 \times \overline{\text{Lease}}_y\right), \qquad \text{Owner EPS}_y = \frac{\text{Net Income}_y + \text{Owner Add-Back}_y}{\text{Shares Outstanding}_y}$$
   (Shares = period-end outstanding; a latest-year count deviating > 15% from the prior year while the balance-sheet count agrees with it is replaced by the balance-sheet count. $\text{Owner Add-Back}_y = 0$ for Balance-Sheet Financials or when $\text{CapEx}_y \le 0$ / unreported.)
   - **Cash-Flow Backing Ceiling (`OCF − NI`)**: D&A is only added back to the extent it survived in Operating Cash Flow above Net Income ($\max(0, \text{OCF}_y - \text{NI}_y)$), preventing operating-cash-flow capital spend (e.g., streaming content additions at `NFLX` or leased vehicle additions at `AYV.FR` / `VOW3.DE`) from inflating Owner EPS while preserving genuine M&A intangible amortization add-backs (`CSU.CA`, `ROP`, `DHR`).
   - **Deterministic D&A Priority**: Extracted in strict priority order: cash-flow statement `depreciation` $\to$ income-statement `depreciationAndAmortization` $\to$ `reconciledDepreciation` (replacing `max(...)` across tags).
   - **Impairment Guard (`clean_da`)**: A year's D&A above $1.5\times$ the median of the prior 3 fiscal years (`DA_IMPAIRMENT_CAP = 1.5`) is capped only when the spike is transient, so one-off write-downs folded into D&A are not added back as recurring earnings, while genuine step-ups are kept: capex rising $\ge 1.5\times$ alongside (capacity build-out) or the following year staying $\ge 1.25\times$ the prior median (merger amortisation).
   - **IFRS-16 Right-of-Use Lease Depreciation Deduction (`LEASE_DEP_RATE = 0.20`)**: For IFRS filers in `eu` and `ca`, IFRS-16 capitalizes operating store/facility leases onto the balance sheet (`capitalLeaseObligations`), routing rent payments through D&A and financing cash flows while excluding lease additions from cash CapEx. Deducting $20\%$ of average `capitalLeaseObligations` ($\overline{\text{Lease}}_y$) from both `owner_addback` and `true_fcf` (`fcf_conv`) prevents lease amortization from inflating Owner EPS or FCF conversion. US GAAP filers (`us`, plus `US_GAAP_IDS` in `fetch_market_data.py`: `ABBN.CH`, `ALC.CH`, `LOGN.CH`, `QIA.DE`, `STMMI.FR`, `ENB.CA`, `TRP.CA`, `IMO.CA`, `CNR.CA`, `FTS.CA`, `EMA.CA`, `H.CA`, `WCN.CA`, `CP.CA`, `QSR.CA`) already expense operating lease cost inside operating cash flow and are excluded (`lease` series cleared).
   - **Non-cash marks** (v7.6, `[auto] earnings dominated by non-cash marks` → **No data**): net income changes sign at least twice over the latest 5 fiscal years while operating cash flow stays positive in all of them and a profitable year shows NI $> 1.2\times$ OCF — reported earnings are dominated by hedge marks or investment gains (SAF.FR, BRK.B), so no Owner EPS is reliable.
   - **Statement rows & capex** (v7.4): when several statement dates fall into one fiscal year (52/53-week year ends next to calendar stubs), the row carrying revenue / net income is primary and stubs only fill fields it lacks (SBRY capex no longer zeroed). Capex is cross-checked against cached Yahoo statements: a systematic gap (median Yahoo ÷ EODHD $> 1.3$) replaces all matched years, otherwise only broken years ($> 1.5\times$, e.g. near-zero recent EODHD capex at LSEG / REL); banks keep EODHD capex. Cash-flow dividends more than $1.3\times$ the DPS-implied figure are replaced by DPS × shares.
   - **Statement integrity** (any of these `[auto]` notes values the company as **No data** until refetched or reviewed — `gates.BLOCKING_AUTO_NOTES`):
     - `stale fundamentals`: revenue / balance sheet end $\ge 2$ fiscal years before cash flow (or $\ge 3$ years ago).
     - `currency switch unresolved`: reporting-currency switches are converted section by section (income, balance sheet, cash flow, each on its own label) at the FX rate of each fiscal period end (spot rate when no FX history is cached). For close pairs ($|\ln \text{fx}| < 0.4$, e.g. GBP/USD, CHF/USD) the old-currency block before the switch is decided as one unit on 3-year medians; far pairs (DKK/NOK/SEK → EUR) use a per-year value test. The note is written (for switches inside the 10-year valuation window) when the block decision is ambiguous (margin $< 0.05$ log points), the revenue jump at the switch lies outside $0.75$–$1.33\times$, or the latest year (within 2 years of the switch) deviates more than 25% from TTM revenue. Verified cases are settled in `fetch_market_data.CCY_SWITCH_OVERRIDES`.
     - `share count changed since FY`: the current share count (SharesStats, agreeing with the market cap) is outside $0.75$–$1.33\times$ the latest statement count without a multi-class explanation — a merger, issuance, consolidation or buyback after the fiscal year, or a statement glitch. Splits / consolidations of any ratio dated after the fiscal year are first applied to all statement share counts when SharesStats confirms the factor. Reviewed ids go in `fetch_market_data.SHARE_BASIS_REVIEWED_IDS`.
   - *Shares are period-end counts and EPS = Net Income ÷ Shares (no diluted-EPS rescaling). Latest fiscal-year add-back is stored in `owner_add_m`.*

2. **Spike Stripping (One-Off Earnings Spikes)**:
   Non-cash windfall gains (tax-allowance releases, subsidiary disposal gains, hedge marks) must be stripped from the Owner EPS series:
   - A year is flagged as an unrepeatable spike if:
     - $\text{Net Income} > 1.10 \times \text{Operating Cash Flow}$, **AND**
     - $\text{Net Income} > 1.30 \times \text{prior year Net Income}$, **AND**
     - $\text{Net Income} > 1.30 \times \text{following year Net Income}$ (or for latest year: $+50\%$ vs prior and $> 1.30 \times \text{OCF}$).

3. **Peak Owner EPS Selection & Age-Weighted Mid-Cycle Reversion Standard**:
   - `peak_oe_eps`: The highest valid Owner EPS in the last 5 fiscal years. Fiscal years ending before the first trading day of the primary listing (pre-IPO, spin-off carve-out years) are left out of the Owner EPS series.
   - `cur_oe_eps`: Latest fiscal-year Owner EPS (falling back to implied $\text{Price} \times \frac{\text{Net Income} + \text{owner\_add\_m}}{\text{Market Cap}}$ only if `cur_oe_eps` is absent).
   - **The Age-Weighted Mid-Cycle Reversion Standard** (v7.2):
     Active earning power is protected against stale or bubble peaks:
     - If `fin_note` flags a multi-class share-basis mismatch (`"check share basis"`), $\text{cur\_eps}$ defaults to `peak_oe_eps`; if `fin_note` flags `"non-cash earnings spike left out of peak"` or $\text{cur\_eps} > 1.5 \times \text{peak\_oe\_eps}$, $\text{cur\_eps}$ is capped at `peak_oe_eps`.
     - If $\text{cur\_eps} < \text{peak\_oe\_eps}$, with $\text{age} = \text{cur\_oe\_year} - \text{peak\_oe\_year}$ and $w = 0.5$ for age $\le 1$, $w = 0.5\,(4 - \text{age})/3$ for ages 2–3, $w = 0$ from age 4 (`gates.peak_weight`; $w = 0.5$ when `cur_oe_year` is missing):
       $$\text{Active Peak EPS} = \max(0, \text{cur\_eps}) + w \times \left(\text{peak\_oe\_eps} - \max(0.0, \text{cur\_eps})\right)$$
     - If $\text{cur\_eps} \ge \text{peak\_oe\_eps}$: $\text{Active Peak EPS} = \text{peak\_oe\_eps}$.
   - **Active Peak EPS Summary**:
     $$\text{Active Peak EPS} = \begin{cases} \text{cur}^{+} + w\,(\text{peak\_oe\_eps} - \text{cur}^{+}) & \text{if } \text{cur\_eps} < \text{peak\_oe\_eps} \\ \text{peak\_oe\_eps} & \text{otherwise} \end{cases}$$

---

### Step 2: Operating ROIC Normalization, M&A Capital Matching & Single Initial Cap (`par_roic_cap = 50%`) (v7.7)

To prevent accounting distortions from penalizing capital-light compounders while ensuring M&A goodwill is matched to M&A-driven growth:
1. **Short-Term Investments Netting, M&A Goodwill Neutralization & Denominator Floor**:
   - Operating cash $\text{Cash}_{\text{op}}$ nets both cash & equivalents and marketable short-term treasury investments (`cashAndShortTermInvestments`, stored in `cash_sti` and exported in `cash_m`) from Invested Capital:
     $$\text{IC}_{\text{GAAP}} = \text{Equity} + \text{NCI} + \text{Debt}_{\text{LT}} + \text{Debt}_{\text{ST}} - \text{Cash}_{\text{op}} \qquad \left(\text{floored at } 0.25 \times \text{Tangible Operating Assets when } \text{IC}_{\text{GAAP}} \le 0\right)$$
     Non-controlling interests (NCI) are included so the capital base matches consolidated EBIT (e.g. Heineken Holding).
   - **Operating ROIC (Tangible Capital Return, v7.3)** earns the same NOPAT on Invested Capital less Goodwill and Intangibles, floored at $\frac{1}{3} \times \text{IC}_{\text{GAAP}}$. There is no D&A add-back: taking acquired assets out of capital and also adding their amortisation back to NOPAT counted the same thing twice. When $\text{IC}_{\text{GAAP}} \le 0$ (customer cash, buyback-driven negative equity) the tangible figure is not defined and `roic_operating` falls back to GAAP ROIC:
     $$\text{Operating ROIC} = \frac{\text{NOPAT}}{\max\!\left(\text{IC}_{\text{GAAP}} - \text{Goodwill} - \text{Intangibles},\; \frac{1}{3}\text{IC}_{\text{GAAP}}\right)} \quad (\text{IC}_{\text{GAAP}} > 0)$$
2. **M&A-Matched RONIC & Single Initial Cap (`par_roic_cap = 0.50`)**:
   - Replaces the legacy two-step log compression + Galton pre-fade ($\text{ROIC}_{\text{log}} \to \text{ROIC}_{\text{exp}}$) with a single initial cap $\text{RONIC}_0 \le 50.0\%$ (`par_roic_cap = 0.50`), leaving all mean-reversion to the explicit Stage-1 linear fade ($\text{RONIC}_0 \to \min(\text{RONIC}_0, 20.0\%, r + 0.5(\text{RONIC}_0 - r))$ over $N$ years).
   - When goodwill-heavy ($r_{\text{tang}} > 1.25 \times r_{\text{GAAP}}$), the business is assumed to keep spending `ma_reinvest` of earnings on acquisitions that earn GAAP ROIC. Bought growth $g_m = \text{ma\_reinvest} \times r_{\text{GAAP}}$ is the share $w = \text{clip}_{[0,1]}(g_m / g_0)$ of the growth ceiling, and the reinvestment rate $g_0/\text{RONIC}_0 = (1-w)\,g_0/r_{\text{tang}} + w\,g_0/r_{\text{GAAP}}$ gives:
     $$\text{RONIC}_{\text{raw}} = \left(\frac{1 - w}{r_{\text{tang}}} + \frac{w}{r_{\text{GAAP}}}\right)^{-1}, \qquad \text{RONIC}_0 = \text{roic\_exp} = \min(0.50,\; \max(0.05,\; \text{RONIC}_{\text{raw}}))$$
     `ma_reinvest` sums cash-funded goodwill + intangibles additions over the 10-year $g_0$ window, so serial acquirers (CSU, BNZL) and one-off cash deals (LVMH/Tiffany) both carry their acquisition cost, while stock-funded deals (SPGI/IHS, ADI/Maxim) are skipped because the dilution index $S_t$ already strips their acquired growth from $g_0$ (`gates.ronic0`).
   - **RONIC₀ ≤ r review flag (`ronic_le_r`)**: growth then adds no value (Fair P/E ≤ 1/r) — review the capital base (goodwill, minorities) against the moat gates.
3. **Active ROIC Selection (`active_roic`) & Up-C Consolidated ROE**:
   - Priority:
     1. **Balance-Sheet Financials** (`Insurance` excl. `Insurance Brokers`, `Reinsurance`, `Banks` excl. `Asset Management & Custody Banks`, `Investment Banking & Brokerage`, and `Multi-Sector Holdings`): **`roe_median`** (5-year median Return on Equity; where consolidated Net Income before non-controlling interest is used — Up-C structures like `IBKR` where `commonStockTotalEquity` is missing and `minorityInterest` is material — the equity base is consolidated too: total assets − total liabilities, bounded by parent equity and parent equity + NCI, v7.4) $\to$ `roic_median` $\to$ `roic_operating`
     2. **IFRIC-12 Infrastructure Concessions** (`Construction & Engineering`, `Highways & Railtracks`): **`roic_median`** (5-year median GAAP ROIC including concession intangibles) $\to$ `roic_operating`
     3. **All Other Operating & Fee Businesses**: **`roic_operating`** (5-year median Tangible Operating ROIC) $\to$ `roic_median` (GAAP). *Exception (v7.5):* when invested capital is $\le 0$ in at least 2 of the 5 years (`ic_neg_years`; clearing / customer cash on balance sheet — DB1, ADYEN, ENX, custody banks) and $0 < \text{ROE} \le 50\%$, **`roe_median`** is the capital return (no M&A blend, operating $r = 8.50\%$). Buyback-shrunk or negative equity (implausible ROE, e.g. FTNT, RR, MCK, VRSN) keeps GAAP ROIC.

---

### Step 3: 4-Pillar Statistical Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Buyback Accretion (`g_exp`) (v7.7)

1. **Core Growth Parameters**:
   - `par_g_base = 0.030` (`3.0%` long-term historical inflation pass-through terminal growth rate $g_{\text{term}}$).
   - `par_g_anchor_max = 0.130` (`13.0%` maximum organic starting growth asymptote $g_0$).
   - Share Buyback / Dilution Split:
     $$\text{bb\_eff} = \text{clamp}_{[-0.03,\, 0.035]}(\text{buyback\_yield}), \qquad \text{bb\_pos} = \max(0.0, \text{bb\_eff}), \qquad \text{bb\_org} = \min(0.0, \text{bb\_eff})$$
2. **The 4-Pillar Statistical Organic Growth Estimator (`sales_cagr` via `statistical_organic_g0`)**:
   - **Pillar 1 — Dilution-Adjusted Per-Share Index ($S_t$)**: Over the post-reset 10-year window, $S_t = S_{t-1} \times \max(1.0, \text{Shares}_t / \text{Shares}_{t-1})$ (for $1.0 < \text{ratio} \le 1.65$) penalizes SBC and stock-merger equity issuance (`SPGI`, `ENX.FR`) in the exact year it occurs without double-counting share buybacks.
   - **Pillar 2 — Cycle-Spanning Theil–Sen Estimator ($\Delta t \ge 5\text{y}$)**: Computes all pairwise annualized log-slopes $b_{ij} = (\ln \tilde{Y}_{t_j} - \ln \tilde{Y}_{t_i}) / (t_j - t_i)$ spanning $\ge 5$ years (falling back to $\ge 3\text{y}$, $\ge 1\text{y}$), extracting the median ($P_{50}$), 25th-percentile Lower Confidence Bound ($P_{25}$), and MAD dispersion $\hat{\sigma}_b = 1.4826 \times \text{MAD}(b_{ij})$.
   - **Pillar 3 — 3-Driver Triangulation**: Evaluates Pillar 1 & 2 on dilution-adjusted Revenue, NOPAT, and Owner Earnings:
     $$\hat{g}_{\text{tri}} = \min\!\Big(\text{median}\big(\hat{g}_{\text{Rev}, P25},\, \hat{g}_{\text{NOPAT}, P25},\, \hat{g}_{\text{OE}, P25}\big),\; \text{median}\big(\hat{g}_{\text{Rev}, P50},\, \hat{g}_{\text{NOPAT}, P50},\, \hat{g}_{\text{OE}, P50}\big),\; \hat{g}_{\text{Rev}, P50} + 1.5\text{pp}\Big)$$
     (NOPAT and Owner Earnings enter only with $\ge 3$ years of span.) *Refranchising guard:* when $\hat{g}_{\text{Rev}, P50} < g_{\text{base}}$ and both $\hat{g}_{\text{NOPAT}, P25}$ and $\hat{g}_{\text{OE}, P25}$ (each with $\ge 5$ years of span) exceed it, $\hat{g}_{\text{tri}} = \min(6.0\%,\, \hat{g}_{\text{NOPAT}, P25},\, \hat{g}_{\text{OE}, P25})$.
   - **Pillar 4 — Empirical Bayes Precision Shrinkage & Smooth $\tanh$ Tail Compression**:
     $$w = \frac{\tau_0^2}{\tau_0^2 + \hat{\sigma}_{b,\text{Rev}}^2} \quad (\tau_0 = 0.060;\ \hat{\sigma} = 3\% \text{ if unavailable}), \qquad \hat{g}_{\text{EB}} = g_{\text{base}} + w(\hat{g}_{\text{tri}} - g_{\text{base}}) \quad (\text{for } \hat{g}_{\text{tri}} > g_{\text{base}})$$
     (one weight from the revenue Theil–Sen spread; $g_{\text{base}}$ / $g_{\max}$ are the config parameters `par_g_base` / `par_g_anchor_max`, read at fetch time)
     $$\text{sales\_cagr} = \text{compress\_g0}(\hat{g}_{\text{EB}}) = g_{\text{base}} + (g_{\max} - g_{\text{base}})\tanh\!\left(\frac{\hat{g}_{\text{EB}} - g_{\text{base}}}{g_{\max} - g_{\text{base}}}\right) \quad (\text{for } \hat{g}_{\text{EB}} > g_{\text{base}}, \text{ else } \max(0, \hat{g}_{\text{EB}}))$$
   - **Fallbacks**: `opcost_cagr` (Theil–Sen $P_{50}$) $\to$ $\text{cagr\_oe\_eps} - \text{bb\_pos}$ $\to$ $\text{sales\_1y} + \text{bb\_org}$ $\to$ `0.030` ($g_{\text{base}}$).
3. **Organic Growth Ceiling ($g_0$ / `g_org_exp`) & Per-Share Growth Ceiling (`g_exp`)**:
     $$g_0 = g_{\text{org,exp}} = \text{clamp}_{[0.0,\, 0.13]}(\text{raw\_org}), \qquad g_{\text{exp}} = g_{\text{org,exp}} + \text{bb\_pos}$$

---

### Step 4: Miller–Modigliani Zero-Spread Invariant Explicit $N$-Year DCF ($r = 8.50\% / r_{\text{fin}} = 10.25\%$) (v7.7)

1. **Stage 1 — Explicit Year-by-Year Mauboussin Fade Over Gate 4 CAP ($t = 1 \dots N$)**:
   Starting from Year-1 normalized run-rate Owner Earnings $E_1 = 1.0$ on existing capital $\text{IC}_0$, initial organic growth $g_0 = g_{\text{org,exp}}$, and initial marginal return $\text{RONIC}_0 = \text{ROIC}_{\text{exp}}$, both growth and marginal RONIC fade linearly across $t = 1 \dots N$ ($N = \text{Gate 4 CAP}$, default `20` years) toward terminal steady state ($g_{\text{term}} = \min(g_0, 3.0\%)$, $\text{RONIC}_{\text{term}} = \max(0.05,\; \min(\text{RONIC}_0, 20.0\%, r + 0.5(\text{RONIC}_0 - r)))$):
   $$\text{frac}_t = \frac{t - 1}{\max(1, N - 1)}, \qquad g_t = g_0 - \text{frac}_t \cdot (g_0 - g_{\text{term}}), \qquad \text{RONIC}_t = \text{RONIC}_0 - \text{frac}_t \cdot (\text{RONIC}_0 - \text{RONIC}_{\text{term}})$$
   $$\text{Reinv}_t = \frac{\max(0.0, g_t)}{\max(0.05, \text{RONIC}_t)}, \qquad \text{FCF}_t = E_t \cdot (1 - \text{Reinv}_t), \qquad E_{t+1} = E_t \cdot (1 + g_t)$$
   $$\text{PV}_{\text{Stage 1}} = \sum_{t=1}^{N} \frac{\text{FCF}_t}{(1 + r)^t} \qquad (\text{stored in } \text{pe\_mm},\; r = 8.50\% \text{ or } 10.25\%)$$
2. **Stage 2 — Post-CAP Terminal Perpetuity Value ($t > N$)**:
   At the end of the Competitive Advantage Period ($t = N$), Year-$(N+1)$ earnings are $E_{N+1} = E_N(1 + g_N)$, and terminal inflation pass-through $g_{\text{tv}} = \max(0.0, g_{\text{term}})$ is reinvested at $\text{RONIC}_{\text{term}}$ via the McKinsey Value Driver formula:
   $$\text{Reinv}_{\text{tv}} = \frac{g_{\text{tv}}}{\max(0.05, \text{RONIC}_{\text{term}})}, \qquad \text{TV}_N = \frac{E_{N+1}(1 - \text{Reinv}_{\text{tv}})}{\max(0.01, r - g_{\text{tv}})}, \qquad \text{PV}_{\text{Stage 2}} = \frac{\text{TV}_N}{(1 + r)^N} \qquad (\text{stored in } \text{pe\_mck})$$
3. **100% Explicit DCF Fair Value Multiple (`par_mult` / `pe_vd`) & Zero-Spread Invariance**:
   $$\text{Fair P/E} = \text{par\_mult} = \text{pe\_vd} = \text{PV}_{\text{Stage 1}} + \text{PV}_{\text{Stage 2}}$$
   *Exact Miller–Modigliani Theorem: When $\text{RONIC}_t = r$ for all $t$, $\text{Fair P/E} \equiv \frac{1}{r}$ for every $g_0$ and $N$.*
4. **Industry-Specific Capital Base, Discount Rate ($r_{\text{fin}} = 10.25\%$) & Value Driver Physics**:
   - **Balance-Sheet Financial Discount Rate ($r_{\text{fin}} = 10.25\%$) & ROE Capital Base (`roe_median`)**: Used for Insurance (excl. Brokers), Reinsurance, Banks (excl. Custody), Investment Banking & Brokerage, and Multi-Sector Holdings.
   - **IFRIC-12 Concession Capital Base (`roic_median`)**: Used for Construction & Engineering and Highways & Railtracks.
   - **Mark-to-Market HoldCo / Insurer NAV Physics (`1.0x BVPS`)**: Anchored to $1.0\times$ IFRS/GAAP Book Value per Share ($\text{BVPS}$). *Limitation:* holdcos that consolidate subsidiaries at historical cost (e.g. Investor AB's Patricia Industries) carry book value below their reported NAV — the 1.0× BVPS anchor is then conservative.
   - **Expiring Concession Annuity Physics (opt-in)**: Only for ids listed in `screener/gates.py` `FINITE_CONCESSION_IDS` (empty by default — contractors and concession groups renew or replace concessions): $\text{PV}_{\text{Stage 2}} = 0$ and $\text{par\_mult} = \text{PV}_{\text{Stage 1}}$.

---

### Step 5: The 3-Price Valuation Framework & Bellman-Consistent 5Y Expected IRR (v7.7)

1. **Fair Value Price (`par_val`)**: $\text{Fair Value Price} = \text{Fair P/E} \times \text{Active Peak Owner EPS}$.
2. **Standalone Terminal P/E (`term_mult`), Terminal Price (`term_val`) & `% vs Terminal` (`vs_term`)**:
   - Values the business today as if its high-growth CAP runway ended immediately and it merely grew at $3.0\%$ historical inflation forever with "keeping-the-lights-on" reinvestment ($3.0\% / \text{RONIC}_{\text{term}}$):
     $$\text{term\_mult} = \frac{1 - g_{\text{term}} / \text{RONIC}_{\text{term}}}{\max(0.01,\; r - g_{\text{term}})} \quad (\text{when } \text{RONIC}_{\text{term}} > r,\text{ else } 1/r;\text{ or } \text{BVPS}/\text{Peak EPS}\text{ for MTM HoldCos; } 0\text{ for finite concessions})$$
     $$\text{term\_val} = \text{term\_mult} \times \text{Active Peak Owner EPS}, \qquad \text{vs\_term} = \frac{\text{Current Share Price}}{\text{term\_val}} - 1.0$$
3. **Current Multiple (`cur_mult`)**: $\text{Current Multiple} = \frac{\text{Current Share Price}}{\text{Active Peak Owner EPS}}$.
4. **Price vs Fair Value (`vs_par`)**: $\text{vs Fair Value} = \frac{\text{Current Share Price}}{\text{Fair Value Price}} - 1.0$ (negative = discount, positive = premium). There is no Below / Above PAR classification (v7.2): a valued company has status **`Valued`** and is read from price, fair price and terminal price. When the DCF fair value is $\le 0$ (growth funded at a RONIC far below $g$) the status is **`No value`** and `vs_par`, `irr_5y`, `g_market`, `g_gap` and the runway metrics are blank; failed statement-integrity checks give **`No data`**.
4. **Bellman-Consistent 5-Year Expected IRR (`irr_5y`)**:
   - Uses the exact Year 1–5 DCF free cash flows $\text{FCF}_1 \dots \text{FCF}_5$ and the exact Year-5 DCF continuation value $V_5$:
     $$V_5 = \left(\text{Fair P/E} - \sum_{t=1}^{\min(5, N)} \frac{\text{FCF}_t}{(1 + r)^t}\right)(1 + r)^{\min(5, N)}$$
   - Solves (via 60-step bisection on $[-99\%, +250\%]$) for the unique $\text{IRR}_{5\text{y}}$ satisfying:
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
   - **Growth Margin of Safety (`g_gap`, populated only when `g_market_flag` = `ok`; a saturated `g_market` is a grid bound shown as ≤ / ≥ without a margin)**:
     $$\text{Growth Margin} = g_0 - g_{\text{market}} = g_{\text{org,exp}} - g_{\text{market}}$$
6. **Market-Implied CAP & Moat Runway Margin**:
   - Scales excess multiple above the zero-moat steady-state base multiple $\text{PE}_{\text{base}} = \frac{1}{r} = 11.76\text{x}$ (at $r = 8.50\%$):
     $$\text{Market-Implied CAP} = \max\!\left(0.0,\; \text{Fundamental CAP} \times \frac{\text{Current Multiple} - \frac{1}{r}}{\text{Fair P/E} - \frac{1}{r}}\right)$$
     When $\text{Fair P/E} \le \frac{1}{r} + 0.5$ (no meaningful growth premium) or for mark-to-market HoldCos: $\text{Market-Implied CAP} = \text{Fundamental CAP} \times \text{Price} / \text{Fair Value}$. With no CAP assigned, a moat archetype implies the default 20 years.
   - **Moat Runway Margin**:
     $$\text{Moat Margin} = \text{Fundamental CAP} - \text{Market-Implied CAP}$$

---

### Step 6: Gate 6 Rule Check (review flags only, v7.6)

Gate 6 is decided qualitatively by the investor (balance-sheet-heavy compounders such as railways, waste and brewers are deliberately passed). The numeric checks are computed at fetch time and shown as ✓ / ⚠ / – in the dashboard ("G6 Checks" column, dossier panel, filter "Gate 6 = Y but numeric ⚠"); they **never reject and never feed the valuation** (`gates.g6_checks`):
1. **Net Debt Check**: 3-year median of $(\text{LT} + \text{ST Debt} - \text{Cash \& ST Investments}) \div (\text{NI} + \text{Owner Add-Back}) \le 4.0$ years (`g6_netdebt_yrs`).
2. **Interest Coverage Check**: 3-year median of $\text{EBIT} \div \text{Interest Expense} > 5.0\times$ (`g6_intcov`).
3. **Cash Conversion Check**: 5-year $\text{Owner FCF} \div \text{Net Income} \ge 80\%$ (`a_fcfconv = 0.80`).
4. **Peak-to-Peak Compounding Check**: `p2p_ok == "Y"`.

For Balance-Sheet Financials the net-debt and interest-cover checks are n/a (debt and interest are their raw material) and cash conversion is informational.

5. **Value-Creation Check** (valuation flag): $\text{RONIC}_0 > r$ (`ronic_le_r` false) — otherwise growth adds no value (Fair P/E $\le 1/r$).

---

## 4. No Analyst Overrides (v7.6)

The quantitative valuation takes no analyst inputs: there are no `peak_eps_est`, `g_est`, `roic_est` or `g_implied` fields, and `fin_note` holds only machine-written `[auto]` data notes. Where statement data cannot support a per-share valuation (stale statements, share count changed since the fiscal year, unresolved currency switch, earnings dominated by non-cash marks) the company is **No data** with the reason in its `[auto]` note. The dashboard sandbox sliders are what-if tools only and export nothing. `screener/apply_evaluation.py` ingests qualitative gate evaluations; a `quantitative_overrides` block in a payload is ignored with a warning.

## 5. Model Constants (v7.7)

**Parameters in `screener/config.py` (`PARAMETER_GROUPS`; per-universe overrides in `universe.json` "parameters" reach both the fetch-time growth estimate and the valuation):**

| Parameter | Value | Use |
| :--- | :--- | :--- |
| `par_cost_of_equity` | 8.50% | Hurdle rate r for operating companies and fee financials |
| `par_cost_of_equity_fin` | 10.25% | Hurdle rate r for balance-sheet financials |
| `par_g_base` | 3.0% | Terminal growth, EB shrinkage target and tanh floor |
| `par_g_anchor_max` | 13.0% | g₀ asymptote (tanh compression) and hard clamp |
| `par_roic_cap` | 50.0% | Ceiling on RONIC₀ |
| `par_roic_term_max` | 20.0% | Terminal RONIC ceiling at the end of the CAP fade |

**Fixed in code (`screener/gates.py`, `screener/fetch/metrics.py`, mirrored in the dashboard sandbox):** RONIC floor 5% (`RONIC_FLOOR`); buyback clamp −3% / +3.5% (`BUYBACK_CLAMP`); EB prior τ = 6%; default CAP 20 years when a moat archetype is set but Gate 4 is blank; g_market grid −20% … +50% in 1pp steps with 40-step bisection; IRR bisection on −99% … +250%; M&A blend trigger tangible ROIC > 1.25 × GAAP ROIC; stock-funded year = shares +3%; acquisition year = goodwill +2%; ROE as capital return when invested capital ≤ 0 in ≥ 2 of 5 years and 0 < ROE ≤ 50%; mark-to-market HoldCo tests (5Y FCF ÷ NI or 2Y OCF ÷ NI < 0.25, or < 0.35 with a 5Y high multiple < 10); peak weight 50% → 0% over 4 years; Gate 6 flags 4.0 years / 5.0× / 80% (config `g6_netdebt_yrs`, `g6_intcov`, `a_fcfconv`).

