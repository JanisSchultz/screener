# Fact-Check & Live Data Verification Report — Quality & Moat Screener (v7.19)

**Summary:** Cross-checked all quantitative figures, attrition counts, formulas, thresholds, cohort counts, gate rules, and live ticker case studies in `ORIGINAL_REQUEST.md` against the `Screener` v7.19 codebase (`screener/*.py`, `screener/fetch/*.py`, specs, CSVs, and live `collect_screener_data()` output as of price date `2026-11-17`). Nearly every figure in `ORIGINAL_REQUEST.md` is 100% verified, **with one mathematical discrepancy found**: the maximum Standalone Terminal P/E (`0g` / `3%` inflation floor) for Balance-Sheet Financials is **`11.72×`** (`(1 - 0.030/0.20) / (0.1025 - 0.030)`), **not `10.89×`** as stated in `ORIGINAL_REQUEST.md` line 70.

---

## 1. Observation

### 1.1 Universe, Pre-Screen & Global Funnel Attrition (`v7.19`)
Source files inspected: `screener/config.py:319`, `screener/data.py:103-120`, `screener/gates.py:166-235`, `data/{us,eu,ca}/{inputs.csv,markets.csv,prescreen.csv}`, `screener/dashboard.py:54-285`.
Live execution via `python3 -c "... collect_screener_data() ..."` confirmed (`version = "7.19"`, `price_updated_at = "2026-11-17"`):

| Metric | `ORIGINAL_REQUEST.md` Claim | Verified Live Repo Value | Source / Evidence | Status |
| :--- | :--- | :--- | :--- | :--- |
| Total Universe | `1,175` (`us` 515, `eu` 602, `ca` 58) | `1,175` (`us`: 515, `eu`: 602, `ca`: 58) | `collect_screener_data()`, `data/{us,eu,ca}/inputs.csv` | **Exact Match** |
| Blank Gate Rule | `0` unreviewed (`blank`) across 1,175 | `0` (`RES_REVIEW` count = 0) | `screener/gates.py:206-212`, live check | **Exact Match** |
| Pre-Screen `in_market = N` | Greece, Poland = `N` (feeds Gate 2) | `28` companies in EU (`GR`, `PL`); US `0`, CA `0` | `data/eu/markets.csv:8,13`, `screener/gates.py:170` | **Exact Match** |
| Pre-Screen `g6_default = N` | Deposit Banks & Regulated Utilities | `143` companies (`us`: 44, `eu`: 89, `ca`: 10) | `data/{us,eu,ca}/prescreen.csv`, `screener/gates.py:171` | **Exact Match** |
| Gate 1 (`Simple to Understand`) | `-30 (-2.6%)` → `1,145` remain | `-30 (-2.55%)` → `1,145` remain | `results()` / `phase_results()`, `Rejected – G1 Understandability: 30` | **Exact Match** |
| Gate 2 (`Essential Western Need`) | `-156 (-13.3%)` → `989` remain | `-156 (-13.28%)` → `989` remain | `Rejected – G2 Essential Need: 156` (US 445, EU 495, CA 49 reach G3 per `bulk_scorer.py:70-75`) | **Exact Match** |
| Gate 3 (`Moat & Pricing >= Infl.`) | `-506 (-43.1%)` → `483` remain | `-506 (-43.06%)` → `483` remain | `Rejected – G3 Moat & Pricing: 506`; `483` advance to Stage 2 | **Exact Match** |
| Gate 4 (`CAP >= 15Y`) | `-108 (-9.2%)` → `375` remain | `-108 (-9.19%)` → `375` remain | `Rejected – G4 Runway (<15Y): 108` (`0` blank G5/G6 diagnostic) | **Exact Match** |
| Gate 5 (`Mgmt Score >= 1`) | `-16 (-1.4%)` → `359` remain | `-16 (-1.36%)` → `359` remain | `Rejected – G5 Management: 16` (`0` blank G6 diagnostic) | **Exact Match** |
| Gate 6 (`Cash & Fortress B/S`) | `-134 (-11.4%)` → `225` (`19.1%`) | `-134 (-11.40%)` → `225` (`19.15%`) | `Rejected – G6 Cash & Fortress Balance Sheet: 134`; `Quality pass: 225` | **Exact Match** |

Note on dual-listed mirrors (`screener/bulk_scorer.py:738-746`, `data/us/universe.json`): `ASML` (US) mirrors `ASML.NL` (EU) and `FER` (US) mirrors `FER.ES` (EU); both lines are counted in the `1,175` total (`515` US + `602` EU + `58` CA).

### 1.2 Part I Qualitative Gates & Deterministic CAP Engine
Source files inspected: `screener/config.py:43-223`, `screener/gates.py:41-215, 338-359`, `screener/apply_evaluation.py:154-268`, `screener/bulk_scorer.py:86-104`, `QUALITATIVE_EVALUATION_SPEC.md:109-237`.

- **Gate 3 Archetype Counts among `225` Prime Grade** (`passes_prime_grade == True`):
  - `Toll booth & switching costs`: **124**
  - `Irreplaceable infrastructure & intangibles`: **71**
  - `Scale economies shared`: **17**
  - `R&D & innovation leadership`: **13**
  - Sum = `124 + 71 + 17 + 13 = 225` → **100% Exact Match**.
- **Gate 3b ROIC / Pricing Threshold**:
  - `QUALITATIVE_EVALUATION_SPEC.md:136`: `5-Year Median GAAP ROIC >= 12% AND Incremental ROIIC >= 12% across the business cycle. (Operating companies failing both tangible ROIC >= 15% and GAAP ROIC >= 12% are automatically rejected).` Matches `ORIGINAL_REQUEST.md` line 58.
- **Gate 4 CAP Engine (`screener/gates.py:41-90`)**:
  - Step 1 `compute_initial_cap_from_scores`: `m_max=0 -> 0Y`, `(1,1) -> 15Y`, `(1,>=2) -> 20Y`, `(2,2) -> 20Y`, `(2,3) -> 25Y`, `(2,>=4) -> 30Y`. **Exact Match**.
  - Step 2 `moderate_force_haircut(c1)`: `0 -> 0Y`, `1-2 -> 5Y`, `3-4 -> 10Y`, `5 -> 15Y`. **Exact Match**.
  - Fatal-Flaw Cap (`c2 >= 1` in `compute_final_cap_from_scores`): `c2 >= 3 -> 0Y`, `c2 == 2 -> 5Y`, `c2 == 1 -> 10Y if cap_init - 10 - h >= 10 else 5Y`; otherwise `max(5, cap_init - h)`. **Exact Match**.
  - 5 Macrotrends & Clock Speed (`QUALITATIVE_EVALUATION_SPEC.md:161-170`, `bulk_scorer.py:87-104`): 1 sector (`Information Technology`) + 15 sub-industries carry presumptive `4_sub >= 1`. **Exact Match**.
  - 3 Anti-Drift Rules (`QUALITATIVE_EVALUATION_SPEC.md:181-184`): (1) Sub-Industry Peer Benchmarking, (2) `4_sub/4_riv = 1 vs 2` Boundary (UI Seat Layer `2` vs Proprietary Data/Statutory Engine `1`), (3) Gate 4 vs Gate 5/6 Orthogonality. **Exact Match**.
  - **Prime Grade CAP Distribution (`225` companies)**:
    - `15Y`: **51**
    - `20Y`: **114**
    - `25Y`: **57**
    - `30Y`: **3** (`COST`, `MCO`, `SPGI`)
    - Sum = `51 + 114 + 57 + 3 = 225` → **100% Exact Match**.
- **Gate 5 (`screener/config.py:195-204`, `QUALITATIVE_EVALUATION_SPEC.md:194-206`)**:
  - 5 Superinvestor Vectors: (a) Integrity & Candor (Fisher/Buffett), (b) Rational Capital Allocation (Murphy/Thorndike), (c) Customer Value-for-Money / Consumer Surplus (Bezos/Sleep), (d) Product-Led Execution, (e) Anti-Bureaucracy & Planned Abandonment (Wallenberg/Drucker). Pass threshold `thr_culture = 1` (`0 = REJECT`). **Exact Match**.
- **Gate 6 (`screener/gates.py:338-359`, `screener/dashboard.py:112-122`, `QUALITATIVE_EVALUATION_SPEC.md:215-236`)**:
  - 3 Pillars: (1) Peak-to-Peak Cycle Owner EPS Compounding (`p2p_ok`), (2) Multi-year Owner FCF ÷ GAAP NI >= 80% (`a_fcfconv = 0.80`), (3) Peace-of-Mind Fortress Balance Sheet (`g6_netdebt_yrs <= 4.0y`, `g6_intcov > 5.0x`; contextual standards for inflation-indexed infrastructure `> 5x` coverage and Solvency II `> 200%` insurers).
  - `< 3` numeric flags (`g6_flags < 3` across the 4 `g6_checks`) required for `Prime Grade` and `Quality Grade` tabs (`screener/dashboard.py:117, 121`). Note: `g6_flags` never rejects in `phase_results()`, and currently `0` of the `225` `Quality pass` companies have `>= 3` flags. **Exact Match**.

### 1.3 Part II Quantitative Valuation Formulas & Parameters
Source files inspected: `screener/config.py:283-290`, `screener/gates.py:238-795`, `screener/fetch/metrics.py:12-386`, `screener/fetch/par.py:1-170`, `screener/dashboard.py:4120-4184`, `QUANTITATIVE_EVALUATION_SPEC.md:10-233`, `tests/test_quantitative_growth.py:163,499`.

- **Step 1 — Sanitized Owner EPS & Age-Weighted Active EPS**:
  - Formula (`metrics.py:44-70`, `par.py:58-70`): `Owner EPS_y = (NI_y + max(0, min(clean_DA_y, max(0, OCF_y - NI_y)) - CapEx_y - 0.20 * AvgLease_y)) / Shares_y` (scaled by `max(0.25, min(1.0, NI / (NI + |MI|)))` if material minority interest; `0` add-back for Balance-Sheet Financials or missing/zero CapEx). **Exact Match**.
  - `DA_IMPAIRMENT_CAP = 1.5` (`metrics.py:15, 20-41`), `LEASE_DEP_RATE = 0.20` (`metrics.py:14`, US-GAAP filers exempt per `QUANTITATIVE_EVALUATION_SPEC.md:69`), spike stripping (`par.py:38-55`), pre-IPO year stripping (`par.py:97-114`). **Exact Match**.
  - `peak_weight` (`gates.py:259-267`): `w = 0.5` for `age <= 1`, fading linearly `0.5 * (4 - age) / 3` to `0.0` at `age >= 4`; `Active Peak EPS = cur+ + w * (peak_oe_eps - cur+)` when `cur_eps < peak_oe_eps`. **Exact Match**.
- **Step 2 — Capital Base & M&A-Matched `RONIC_0`**:
  - `IC_GAAP = Equity + NCI + Debt_LT + Debt_ST - Cash_op` (floored at `0.25 * Tangible Operating Assets` if `<= 0`).
  - `Operating ROIC = NOPAT / max(IC_GAAP - Goodwill - Intangibles, 1/3 * IC_GAAP)` (`metrics.py:371`, when `IC_GAAP > 0`). **Exact Match**.
  - `active_roic` (`gates.py:557-583`): `roe_median` for Balance-Sheet Financials (with Up-C consolidated equity, and GAAP ROIC fallback if `roe < 8.5%` & `gaap >= 12%`) and for operating firms with `ic_neg_years >= 2` and `0 < roe_median <= 50%`; `roic_median` (GAAP) for IFRIC-12 Concessions; `roic_operating` otherwise. **Exact Match**.
  - `ronic0` (`gates.py:586-596`): Trigger `r_tang > 1.25 * r_gaap` (for `not gaap_basis`, `ma_reinvest > 0`, `g_0 > 0`), `w = clip(ma_reinvest * r_gaap / g_0, 0, 1)`, harmonic blend `1 / ((1 - w)/r_tang + w/r_gaap)`, clamped to `[5.0%, 50.0%]` (`RONIC_FLOOR = 0.05`, `par_roic_cap = 0.50`). **Exact Match**.
- **Step 3 — 4-Pillar Statistical Organic Growth (`g_0 <= 13%`)**:
  - `S_t` (`metrics.py:230-243`): Dilution-only index (`s1 > s0`, annualized ratio `<= 1.65`). **Exact Match**.
  - `Theil-Sen` (`metrics.py:250-269`): Pairwise log-slopes `dt >= 5y` (fallbacks `>= 3y`, `>= 1y`), `P50`, `P25`, `1.4826 * MAD`. **Exact Match**.
  - `3-Driver Triangulation` (`metrics.py:300-320`): Revenue, NOPAT (`>=3y`), Owner Earnings (`>=3y`); `g_tri = min(med(P25), med(P50), rev_med + 1.5pp)`; refranchising guard `min(6.0%, nop_p25, oe_p25)` when `rev_med < 3.0%` and both `>=5y` profit `P25`s `> rev_med`. **Exact Match**.
  - `Empirical Bayes & tanh` (`metrics.py:180-192, 324-327`): `TAU_PRIOR_STAT = 0.060` (`6%`), `w = tau_0^2 / (tau_0^2 + se^2)`, shrinkage toward `3.0%`, `compress_g0` `tanh` asymptote `13.0%`. **Exact Match**.
  - `BUYBACK_CLAMP = (-0.03, 0.035)` (`[-3.0%, +3.5%]`, `gates.py:272`), kept out of firm-level DCF (`g_org_exp` feeds `dcf_schedule_and_continuation`). **Exact Match**.
- **Step 4 — Explicit N-Year Mauboussin-Fade DCF (`gates.py:367-432`)**:
  - `r = 8.50%` operating / `10.25%` financials (`config.py:284-285`).
  - `E_1 = 1.0 * Active EPS`, `t = 1..N` (`N = CAP`, default `20`), `g_t` linear `g_0 -> min(g_0, 3.0%)`, `RONIC_t` linear `RONIC_0 -> min(RONIC_0, 20.0%, r + 0.5 * (RONIC_0 - r))` (floored at `5%`), `FCF_t = E_t * (1 - max(0, g_t)/RONIC_t)`.
  - Stage 2 McKinsey terminal value at `3.0%` (`g_tv = max(0, min(g_0, 3.0%))`), zero-spread invariance (`RONIC_t = r => Fair P/E = 1/r`). **Exact Match**.
- **Step 5 — 3-Price Anchor, Bellman 5Y IRR, Reverse-DCF & Special Physics**:
  - **DISCREPANCY FOUND on Standalone Terminal P/E (`0g` / `3%` inflation floor) max for Balance-Sheet Financials**:
    - Formula (`gates.py:453-456` & `dashboard.py:4183`): `term_mult = (1 - g_inf / roic_fin) / max(0.01, r - g_inf)` where `g_inf = 0.030` and `max roic_fin = roic_term_max = 0.20`.
    - Operating (`r = 0.085`): `(1 - 0.030 / 0.20) / (0.085 - 0.030) = 0.85 / 0.055 = 15.4545...` → **`15.45×`** (zero-spread floor `1/0.085 = 11.76×`). **Exact Match**.
    - Balance-Sheet Financials (`r_fin = 0.1025`): `(1 - 0.030 / 0.20) / (0.1025 - 0.030) = 0.85 / 0.0725 = 11.7241...` → **`11.72×`** (zero-spread floor `1/0.1025 = 9.76×`). Live `bs_fin` `term_mult` values in the repo span **`9.76×` to `11.72×`**.
    - `ORIGINAL_REQUEST.md` line 70 states `10.89× financials` — **this is incorrect** (should be **`11.72×`**).
  - Bellman 5Y IRR (`gates.py:531-554`): 60-step bisection on `[-99%, +250%]` across `FCF_1..FCF_5` + exact `V_5`, guaranteeing `IRR == r` iff `Price == Fair Value`. **Exact Match**.
  - Reverse-DCF (`gates.py:470-525`): `[-20%, +50%]` grid in `1pp` steps + 40-step bisection. **Exact Match**.
  - Special Physics (`gates.py:310-336, 362-364, 722-723, 742-747`): `1.0x BVPS` MTM HoldCo anchor, `No value` (`Fair Value <= 0`; `13` companies in full universe, `0` in Prime Grade), `No data` (`BLOCKING_AUTO_NOTES`; `105` in full universe, `5` in Prime Grade: `CPG.GB`, `WISE.GB`, `SAF.FR`, `BRK.B`, `WAT`). **Exact Match**.

### 1.4 Part III Cohorts & Live Case Studies (Verified v7.19 Numbers, Price Date `2026-11-17`)

#### Decision Cohorts
- **`Prime Grade`**: **225** (`us`: **110**, `eu`: **104**, `ca`: **11**; `220 Valued`, `5 No data`, `0 No value`; median 5Y IRR vs hurdle = **`-11.71pp`**). **Exact Match**.
- **`Growth at ~0g`**: **25** (`us`: **11**, `eu`: **14**, `ca`: **0**). Breakdown matches `README.md:25` and `screener/config.py:706`: **9** `Quality pass` (Prime Grade), **6** `CAP >= 15Y` failing Gate 6 (all 6 are `Rejected – G6 Cash & Fortress Balance Sheet`), **10** `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`). **Exact Match**.
- **`Quality Grade`**: **443** (`us`: **221**, `eu`: **204**, `ca`: **18**; `225 Quality pass` + `109 Rejected – G6` + `98 Rejected – G4` + `11 Rejected – G5`). Note: `483` pass G1–G3, of which `40` are excluded by `g6_flags >= 3` (`25` G6-rejected, `10` G4-rejected, `5` G5-rejected), leaving `443`. **Exact Match**.

#### Live Case Studies (`MSFT`, `COST`, `ASML.NL`, `SPGI`, `WM`, `CRM`)
All figures below come directly from `collect_screener_data()` (v7.19, `price_updated_at = 2026-11-17`):

| Ticker | Gate Status & CAP | Cur Price | Fair Value | 0g Price | vs FV / vs 0g | Cur P/E | Fair P/E | Term P/E | `g_0` | `g_market` | `RONIC_0` | 5Y IRR | Match vs `ORIGINAL_REQUEST.md` |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **`MSFT`** | `Quality pass`, 25Y (30Y init, `-5Y` `4_riv=1, 4_sub=1`), G5=1, G6=Y | `$506.24` | `$547.10` | `$277.08` | `-7.5%` / `+82.7%` | `28.2×` | `30.5×` | `15.45×` | `11.5%` | `10.5%` | `50.0%` | **`+10.3%`** | **100% Match** (`30.5× vs 28.2×`, `10.3%`) |
| **`COST`** | `Quality pass`, 30Y (30Y init, all forces 0), G5=2, G6=Y | `$1,110.08` | `$600.33` | `$320.87` | `+84.9%` / `+246.0%` | `53.5×` | `28.9×` | `15.45×` | `10.0%` | `16.5%` | `43.1%` | **`-4.6%`** | **100% Match** (`28.9× vs 53.5×`, `-4.6%`) |
| **`ASML.NL`** | `Quality pass`, 25Y (30Y init, `-5Y` `4_buy=1, 4_sup=1`), G5=2, G6=Y | `€1,236.80` | `€806.65` | `€383.74` | `+53.3%` / `+222.3%` | `49.8×` | `32.5×` | `15.45×` | `12.3%` | `17.5%` | `50.0%` | **`-0.7%`** | **100% Match** (`32.5× vs 49.8×`, `-0.7%`) |
| **`SPGI`** | `Quality pass`, 30Y (30Y init, all forces 0), G5=1, G6=Y | `$452.35` | `$362.36` | `$264.91` | `+24.8%` / `+70.8%` | `25.4×` | `20.3×` | `14.86×` | `7.0%` | `9.9%` | `24.4%` | **`+3.5%`** | **100% Match** (`20.3× vs 25.4×`, `3.5%`) |
| **`WM`** | `Quality pass`, 25Y (25Y init, all forces 0), G5=1, G6=Y (`1` flag) | `$242.69` | `$97.52` | `$87.38` | `+148.9%` / `+177.7%` | `36.0×` | `14.4×` | `12.95×` | `5.6%` | `23.5%` | `12.3%` | **`-10.5%`** | **100% Match** (`14.4× vs 36.0×`, `-10.5%`) |
| **`CRM`** | `Rejected – G4 Runway (<15Y)`, 5Y (20Y init, `4_sub=2` Fatal Flaw + `4_ent=1,4_riv=1,4_buy=1`), diag G5=0, G6=Y | `$194.52` | `$164.31` | `$148.19` | `+18.4%` / `+31.3%` | `17.8×` | `15.1×` | `13.58×` | `11.6%` | `26.6%` | `15.2%` | **`+4.7%`** | **100% Match** (`4_sub=2 -> 5Y CAP, Reject @ G4`) |

#### Recommended `💎 Growth at ~0g` Live Examples (for Slide 11 / 12)
From the `9` Prime Grade companies in the `25`-stock `Growth at ~0g` cohort, these 3 are the cleanest examples of world-class compounders priced near or below their `0g` inflation-only floor:
1. **`ZTS` (Zoetis — US, Prime Grade, 25Y CAP):** Price `$83.48` vs Fair Value `$146.23` (`-42.9%` discount) and **below** `0g` Terminal Price `$94.19` (`-11.4%`); `Cur P/E 13.7×` vs `Fair P/E 24.0×`; `g_0 = 8.7%` vs `g_market = +1.6%` (`+7.1pp` growth margin); `RONIC_0 = 40.7%`; **`5Y IRR = +22.4%`**.
2. **`PGHN.CH` (Partners Group — EU, Prime Grade, 20Y CAP):** Price `CHF 644.40` vs Fair Value `CHF 891.33` (`-27.7%` discount) and **below** `0g` Terminal Price `CHF 763.76` (`-15.6%`); `Cur P/E 13.0×` vs `Fair P/E 18.0×`; `g_0 = 5.1%` vs `g_market = +1.2%`; `RONIC_0 = 36.4%`; **`5Y IRR = +16.5%`**.
3. **`PGR` (Progressive Corp — US, Prime Grade, 25Y CAP):** Price `$234.67` vs Fair Value `$327.53` (`-28.4%` discount) vs `0g` Terminal Price `$214.85` (`+9.2%`); `Cur P/E 12.2×` vs `Fair P/E 17.0×`; `g_0 = 11.2%` vs `g_market = +4.3%`; `RONIC_0 = 21.4%`; **`5Y IRR = +18.3%`**.
*(Plus `WKL.NL` — Wolters Kluwer: `€88.20` vs `€104.55` FV and `€88.55` `0g` Terminal Price (`-0.4%`), `g_0 = 5.5%` vs `g_market = +2.8%`, `5Y IRR = +12.6%`.)*

---

## 2. Logic Chain

1. By inspecting `screener/gates.py`, `screener/config.py`, `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/fetch/metrics.py`, `screener/fetch/par.py`, and `screener/dashboard.py` alongside `QUALITATIVE_EVALUATION_SPEC.md`, `QUANTITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, and `README.md`, we verified the exact code implementations of all qualitative waterfall rules, CAP matrices, and DCF equations.
2. By executing `collect_screener_data()` in read-only mode against `data/{us,eu,ca}/`, we computed the exact v7.19 live counts (`1,175` total, funnel attrition, `225` Prime Grade, `443` Quality Grade, `25` Growth at ~0g, CAP distribution, archetypes) and exact valuation metrics for all 6 case study tickers (`MSFT`, `COST`, `ASML.NL`, `SPGI`, `WM`, `CRM`) plus all 25 `Growth at ~0g` names.
3. Comparing `terminal_multiple()` in `screener/gates.py:435-456` and `screener/dashboard.py:4173-4184` against `ORIGINAL_REQUEST.md` line 70 revealed that for `r_fin = 10.25%`, `g_term = 3.0%`, and `roic_term_max = 20.0%`, `(1 - 0.030 / 0.20) / (0.1025 - 0.030) = 11.7241x` (`11.72×`), whereas `ORIGINAL_REQUEST.md` mistakenly wrote `10.89×`. All other parameters, formulas, attrition numbers, cohort counts, and case-study metrics matched verbatim.

---

## 3. Caveats

- **Pre-built HTML timestamp:** We verified the live data via `screener/dashboard.py:collect_screener_data()` directly from `data/{us,eu,ca}/` rather than parsing the HTML blob inside `output/screener.html`; unless `data/` changed after the last `build.py` run, they are identical.
- **`0g` max P/E nuance for MTM HoldCos:** The `15.45×` / `11.72×` max terminal P/E bounds apply to DCF-valued operating companies (`r = 8.50%`) and Balance-Sheet Financials (`r_fin = 10.25%`); Mark-to-Market HoldCos / Insurers (`mtm_holdco == True`) bypass the DCF terminal multiple and anchor both Fair Value and Terminal Value directly to `1.0× BVPS`.
- **Dual-listed mirrors:** `ASML` (US) and `FER` (US) mirror `ASML.NL` (EU) and `FER.ES` (EU) in `inputs.csv` and are counted inside the `1,175` total (`515` US + `602` EU + `58` CA).
- **`g_0` vs `g_exp`:** Note for slide clarity that the DCF uses organic `g_0` (`g_org_exp <= 13.0%`), while display column `g_exp = g_org_exp + bb_pos` adds positive buybacks (clamped `<= +3.5%`, so `g_exp` can reach `16.5%`). For example, `MSFT` has `g_0 = 11.5%`, `bb_eff = +0.1%`, `g_exp = 11.6%`.

---

## 4. Conclusion

1. **Use `11.72×` (not `10.89×`)** for the Balance-Sheet Financials maximum Standalone Terminal P/E (`0g` / `3%` inflation floor) on Slide 10 (and in speaker notes).
2. **All other figures in `ORIGINAL_REQUEST.md` are 100% factually verified** against the v7.19 repository (`1,175` universe, funnel attrition `1,175 → 1,145 → 989 → 483 → 375 → 359 → 225`, archetypes `124/71/17/13`, CAP distribution `51/114/57/3`, all Part II formulas/thresholds, cohorts `225 / 25 / 443`, and all 6 live case studies `MSFT`, `COST`, `ASML.NL`, `SPGI`, `WM`, `CRM`).
3. **Recommended Slide 11/12 addition:** Include **`ZTS` (Zoetis)** (`$83.48` vs `$146.23` Fair Value & `$94.19` `0g` Terminal Price, `g_0 = 8.7%` vs `g_market = +1.6%`, `+22.4%` 5Y IRR) and/or **`PGHN.CH` (Partners Group)** (`CHF 644.40` vs `891.33` FV & `763.76` `0g`, `+16.5%` 5Y IRR) as live `💎 Growth at ~0g` Prime Grade examples.

---

## 5. Verification Method

Run these read-only commands from `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`:

1. Verify terminal multiples (`15.45x` op, `11.72x` fin):
   ```bash
   python3 -c "from screener import gates as G; print(round(G.terminal_multiple(0.50, 0.085, 0.030), 2), round(G.terminal_multiple(0.50, 0.1025, 0.030), 2))"
   ```
2. Verify all counts, cohorts, and case studies (`MSFT`, `COST`, `ASML.NL`, `SPGI`, `WM`, `CRM`, `ZTS`, `PGHN.CH`):
   ```bash
   python3 -c "from collections import Counter; from screener.dashboard import collect_screener_data; d=collect_screener_data(); cos=d['companies']; print(d['version'], d['price_updated_at'], d['summary']); print(Counter(c['result'] for c in cos))"
   ```
3. Run existing unit test suite for quantitative & gate parity (verified: `Ran 317 tests in 62.373s — OK`, and `term_mult: 15.45 11.72`):
   ```bash
   python3 -m unittest discover -s tests
   ```
- **Invalidation condition:** Any new `fetch_market_data.py` price/fundamental refresh or `inputs.csv` edit after `2026-11-17` would update live market prices, multiples, IRRs, and cohort counts.
