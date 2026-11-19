# Empirical Quant Parity & Chart Data Challenge — `slides_challenger_iter1_2` (Hard Handoff)

**Explicit Verdict:** **`REQUEST_CHANGES`**

All on-slide text, tables, formulas, constants, attrition counts, cohorts, 6 case studies, `Growth at ~0g` examples, `.pptx` XML text, and all 3 generated charts (`funnel_waterfall.png`, `mauboussin_fade_dcf.png`, `case_study_irr_pe.png`) match live Screener v7.19 (`collect_screener_data()`, `price_updated_at = 2026-11-17`, `screener/gates.py`, `screener/fetch/metrics.py`, `screener/config.py`) **100%**.  
However, **one factual quantitative error exists in the live deck's Slide 13 speaker notes** (`slide_1795014495932258000_372`), synced in `output/deck/build_batch.py:532` and `output/deck/batch.json:4917`, which attributes `14.3% RONIC0` and `10.89x` terminal P/E to `HNR1.DE` — both numbers are false for `HNR1.DE` in live v7.19 (`RONIC₀ = 19.02%`, `term_mult = 10.97×`) and are mutually inconsistent under the `terminal_multiple` formula (`14.3%` at `10.25%` yields `10.42×`).

---

## 1. Observation

### 1.1 Independent Capture & Structural Parity Checks
1. **Live Google Slides API Read (`gslides readonly read`):**
   - Command: `gslides readonly read 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` (`BypassSandbox: false`) → exited `0`, returned all 16 slides (`p` + `slide_1795014495931708000_22` .. `slide_1795014495932534000_475`).
   - Command: `gslides readonly get-notes 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --slide slide_1795014495932258000_372` (`BypassSandbox: false`) → exited `0`, returned verbatim Slide 13 notes:
     > `"Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at (1 - 3%/20%)/(10.25% - 3%) = 11.72x—individual insurers like HNR1.DE at 14.3% RONIC0 sit at 10.89x. Reverse-DCF flips the model to ask what growth today's price already assumes."`
2. **`.pptx` XML vs `output/deck/pres_read.json` Token Parity:**
   - Inspected `output/Quality_Moat_Screener_v7.19.pptx` (`16` `ppt/slides/slide*.xml`, `16` `ppt/notesSlides/notesSlide*.xml`) vs `output/deck/pres_read.json` (`16` slides).
   - Result across all 16 slides: `PPTX_SLIDE_01..16: missing_tokens=[]` (100% body token parity).
3. **Unit Test Suite:**
   - Command: `python3 -m unittest discover -s tests` → `Ran 317 tests in 73.448s — OK`.

### 1.2 Full Empirical Parity Table (Live Deck vs. Live v7.19 Repo)

#### A. Universe, Pre-Screen, Funnel, Archetypes & CAP Distribution (Slides 1–8)
| Metric | Deck Claim (Slide / Chart) | Live v7.19 Repo Value | Source / Verification | Status |
| :--- | :--- | :--- | :--- | :--- |
| Version & Price Date | `v7.19`, `2026-11-17` (S1, S4, S14, S15, Chart 1, Chart 3) | `version = "7.19"`, `price_updated_at = "2026-11-17"` | `collect_screener_data()` | **MATCH** |
| Global Universe | `1,175` = `515` US (`44%`) + `602` EU (`51%`) + `58` CA (`5%`) (S1, S2) | `1,175` (`us`: 515 [43.83%], `eu`: 602 [51.23%], `ca`: 58 [4.94%]) | `Counter(c["universe"])` | **MATCH** |
| Blank Gate Rule | `0 unreviewed gates across all 1,175` (S3) | `RES_REVIEW` count = `0` | `collect_screener_data()` | **MATCH** |
| Stage 1 / Stage 2 | Stage 1 fail = `186` (`−15.8%`), Stage 2 full diagnostic on all `483` G3-passers (S3, S5) | `692` Stage 1 fails (`0` non-blank G4–G6); `483` Stage 2 firms (`0` blank G4–G6) | `collect_screener_data()` | **MATCH** |
| Pre-Screen `in_market` | Greece & Poland = `N` → auto-fail G2 (S3) | `28` EU (`Greece`, `Poland` = `N`); US/CA `0` | `data/eu/markets.csv` | **MATCH** |
| Pre-Screen `g6_default` | Deposit Banks & Utilities → G6 = `N` (S3) | `143` (`us`: 44, `eu`: 89, `ca`: 10) | `data/*/prescreen.csv` | **MATCH** |
| Funnel: G1 | `1,175 → 1,145`, `−30 (−2.6%)` (S4, S5, Chart 1) | `-30` (`-2.55%`), `1,145` remain (`97.45%`) | `C.RES_REJ[1]` | **MATCH** |
| Funnel: G2 | `1,145 → 989`, `−156 (−13.3%)` (S4, S5, Chart 1) | `-156` (`-13.28%`), `989` remain (`84.17%`) | `C.RES_REJ[2]` | **MATCH** |
| Funnel: G3 | `989 → 483`, `−506 (−43.1%)` (S4, S6, Chart 1) | `-506` (`-43.06%`), `483` remain (`41.11%`) | `C.RES_REJ[3]` | **MATCH** |
| Funnel: G4 | `483 → 375`, `−108 (−9.2%)` (S4, S7, Chart 1) | `-108` (`-9.19%`), `375` remain (`31.91%`) | `C.RES_REJ[4]` | **MATCH** |
| Funnel: G5 | `375 → 359`, `−16 (−1.4%)` (S4, S8, Chart 1) | `-16` (`-1.36%`), `359` remain (`30.55%`) | `C.RES_REJ[5]` | **MATCH** |
| Funnel: G6 / Prime | `359 → 225 (19.1%)`, `−134 (−11.4%)` (S4, S8, Chart 1) | `-134` (`-11.40%`), `225` remain (`19.15%`) | `C.RES_REJ[6]`, `C.RES_QPASS` | **MATCH** |
| Prime Archetypes (225) | `124` (`55%`), `71` (`32%`), `17` (`8%`), `13` (`6%`) (S6) | `Toll booth`: 124 (55.1%), `Irrepl. infra`: 71 (31.6%), `Scale econ`: 17 (7.6%), `R&D`: 13 (5.8%) | `Counter(g3a_moat_archetype)` | **MATCH** |
| Archetype Examples | `MSFT, SPGI` (TB); `WM, RMS.FR` (IA); `COST, PGR` (SE); `ASML.NL` (RD) (S6) | All 7 are `Quality pass` and match exact listed archetype | `by_id[tid]["g3a_moat_archetype"]` | **MATCH** |
| Gate 3b Hurdle | `5Y Median GAAP ROIC ≥ 12% (or Tangible ROIC ≥ 15%) AND Incremental ROIIC ≥ 12%` (S6) | Exact match | `QUALITATIVE_EVALUATION_SPEC.md:136` | **MATCH** |
| Gate 4 Step 1 & Step 2 | `0Y (m_max=0), 15Y (1,1), 20Y (1,≥2 or 2,2), 25Y (2,3), 30Y (2,≥4)`; `h(c1): 0→0, 1-2→-5, 3-4→-10, 5→-15`; `any Force=2 → ≤10Y` (S7) | Exact match | `screener/gates.py:41-90` | **MATCH** |
| Prime CAP Dist. (225) | `15Y: 51`, `20Y: 114`, `25Y: 57`, `30Y: 3` (S7) | `15: 51`, `20: 114`, `25: 57`, `30: 3` | `Counter(c["g4_cap"])` | **MATCH** |
| Gate 5 & Gate 6 Pillars | G5 `0-2, pass ≥ 1`, 5 vectors; G6 `FCF/NI ≥ 80%`, `Net Debt/OE ≤ 4.0y`, `EBIT/Int > 5.0×`, Solvency II `> 200%`, `< 3 flags` (S8) | `thr_culture=1`, `a_fcfconv=0.8`, `g6_netdebt_yrs=4.0`, `g6_intcov=5.0`, `QUALITATIVE_EVALUATION_SPEC.md:215-236` | `screener/config.py`, `gates.py:338-359` | **MATCH** |

#### B. Part II Quantitative Valuation Formulas & Constants (Slides 9–13)
| Formula / Constant | Deck Claim (Slide / Notes) | Live Repo Implementation | Source | Status |
| :--- | :--- | :--- | :--- | :--- |
| Owner EPS Formula | `(NI + max(0, min(clean_DA, max(0, OCF − NI)) − CapEx − 0.20 × AvgLease)) / Shares` (S9) | Exact match | `metrics.py:44-70`, `par.py:58-70` | **MATCH** |
| `clean_DA` & Lease | `1.5×` impairment cap; `20%` AvgLease (US-GAAP exempt) (S9) | `DA_IMPAIRMENT_CAP = 1.5`, `LEASE_DEP_RATE = 0.20` | `metrics.py:14-41` | **MATCH** |
| `peak_weight` Decay | `w = 50% (≤1y) → 33% (2y) → 17% (3y) → 0% (≥4y)` (S9) | `50.0, 50.0, 33.33, 16.67, 0.0` | `gates.py:259-267` | **MATCH** |
| Capital Base & `RONIC₀` | `max(IC − GW − Intang, 1/3 IC)`; BS Fin & `IC≤0 (≥2/5y)` ROE; `r_tang > 1.25 × r_GAAP`, `w = clip(ma_reinvest × r_GAAP / g₀, 0, 1)`, `[5.0%, 50.0%]` (S10) | `1/3`, `IC_NEG_YEARS_FOR_ROE=2`, `1.25`, `RONIC_FLOOR=0.05`, `par_roic_cap=0.50` | `metrics.py:371`, `gates.py:251, 557-596` | **MATCH** |
| `g₀` 4-Pillar & Buybacks | `Δt ≥ 5y` Theil–Sen (`P50`/`P25`), 3-Driver + `6%` refranchising guard, `τ₀ = 6%` EB toward `3.0%`, `tanh` cap `13.0%`, buybacks `[−3.0%, +3.5%]` outside DCF (S11) | `min_span=5`, `0.060` cap, `TAU_PRIOR_STAT=0.060`, `par_g_base=0.03`, `par_g_anchor_max=0.13`, `BUYBACK_CLAMP=(-0.03, 0.035)` | `metrics.py:180-328`, `gates.py:272, 678-706` | **MATCH** |
| Explicit N-Year DCF | `E₁ = 1.0 × Active EPS`, `r = 8.50% / 10.25%`, linear fade `g_t → min(g₀, 3.0%)`, `RONIC_t → min(RONIC₀, 20%, r+0.5(RONIC₀−r))`, `FCF_t = E_t(1−g_t/RONIC_t)`, M-M `11.76× / 9.76×` (S12, Chart 2) | Exact match (`1/0.085 = 11.7647×`, `1/0.1025 = 9.7561×`) | `gates.py:275-277, 367-432` | **MATCH** |
| 0g Max Terminal P/E | `15.45×` op / `11.72×` BS fin; zero-spread `11.76× / 9.76×` (S13) | `terminal_multiple(0.50, 0.085, 0.030) = 15.4545×`; `terminal_multiple(0.50, 0.1025, 0.030) = 11.7241×` | `gates.py:435-456` | **MATCH** |
| **Slide 13 Notes (`HNR1.DE`)** | **`"individual insurers like HNR1.DE at 14.3% RONIC0 sit at 10.89x"`** (S13 speaker notes) | **`HNR1.DE` has `RONIC₀ = 19.02%` (`roic_exp = 0.1902`, `RONIC_term = 14.64%`) and `term_mult = 10.97×` (`10.9657×`)** | `collect_screener_data()` (`by_id["HNR1.DE"]`) | **MISMATCH (BUG)** |
| Reverse-DCF & Breakers | `[−20%, +50%]` grid + bisection; Bellman IRR (`IRR==r iff P==FV`); `1.0× BVPS`; `No value (FV≤0)`; `No data (BLOCKING_AUTO_NOTES)` (S13) | Exact match | `gates.py:459-554, 719-772` | **MATCH** |

#### C. Cohorts, `Growth at ~0g` Examples & 6 Case Studies (Slides 14–16, Chart 3)
| Entity / Metric | Deck Claim (Slide / Chart) | Live v7.19 Repo Value | Status |
| :--- | :--- | :--- | :--- |
| `Prime Grade` | `225` (`110 US \| 104 EU \| 11 CA`), `220 Valued (5 No data, 0 No value)`, median excess 5Y IRR `−11.7pp` (S14) | `225` (`us: 110, eu: 104, ca: 11`), `Valued: 220, No data: 5`, `median_excess_irr = -11.7061pp` | **MATCH** |
| `Growth at ~0g` | `25` (`9 Prime, 6 G6-fail, 10 CAP 5–10Y`) (S14) | `25` (`us: 11, eu: 14, ca: 0`; `Quality pass: 9`, `G6-fail: 6`, `G4-fail: 10` [6 at 5Y, 4 at 10Y]) | **MATCH** |
| `Quality Grade` | `443` (`221 US \| 204 EU \| 18 CA`) (S14) | `443` (`us: 221, eu: 204, ca: 18`) | **MATCH** |
| `ZTS` | `+22.4% IRR ($83 vs $146 FV / $94 0g)` (S14) | `irr=22.43%`, `price=$83.48`, `par_val=$146.23`, `term_val=$94.19` | **MATCH** |
| `PGHN.CH` / `PGR` | `PGHN.CH: +16.5% \| PGR: +18.3%` (S14) | `PGHN.CH irr=16.5497%`, `PGR irr=18.3349%` | **MATCH** |
| `MSFT` | `25Y`, `28.2×/30.5×`, `11.5%→10.5%`, `+10.3%`, `✓ Prime −7.5%` (S15, Chart 3) | `cap=25`, `cur=28.24×`, `fair=30.51×`, `g0=11.51%`, `gmkt=10.52%`, `irr=+10.29%`, `vs_par=-7.47%` | **MATCH** |
| `SPGI` | `30Y`, `25.4×/20.3×`, `7.0%→9.9%`, `+3.5%`, `Prime +24.8%` (S15, Chart 3) | `cap=30`, `cur=25.38×`, `fair=20.33×`, `g0=7.01%`, `gmkt=9.87%`, `irr=+3.50%`, `vs_par=+24.83%` | **MATCH** |
| `ASML.NL` | `25Y`, `49.8×/32.5×`, `12.3%→17.5%`, `−0.7%`, `Prime +53.3%` (S15, Chart 3) | `cap=25`, `cur=49.81×`, `fair=32.49×`, `g0=12.30%`, `gmkt=17.51%`, `irr=-0.74%`, `vs_par=+53.32%` | **MATCH** |
| `COST` | `30Y`, `53.5×/28.9×`, `10.0%→16.5%`, `−4.6%`, `Prime +84.9%` (S15, Chart 3) | `cap=30`, `cur=53.47×`, `fair=28.91×`, `g0=10.00%`, `gmkt=16.51%`, `irr=-4.57%`, `vs_par=+84.91%` | **MATCH** |
| `WM` | `25Y`, `36.0×/14.4×`, `5.6%→23.5%`, `−10.5%`, `Prime +148.9%` (S15, Chart 3) | `cap=25`, `cur=35.96×`, `fair=14.45×`, `g0=5.62%`, `gmkt=23.51%`, `irr=-10.51%`, `vs_par=+148.86%` | **MATCH** |
| `CRM` | `5Y`, `17.8×/15.1×`, `11.6%→26.6%`, `Reject`, `✗ G4 (4_sub=2)`, Chart 3 `+4.7% ✗ G4 FAIL` (S15, Chart 3) | `cap=5` (`4_sub=2` Fatal Flaw), `cur=17.83×`, `fair=15.06×`, `g0=11.63%`, `gmkt=26.59%`, `irr=+4.74%`, `Rejected – G4 Runway (<15Y)` | **MATCH** |

### 1.3 Chart PNGs & `output/deck/generate_charts.swift` Audit
Inspected `output/deck/generate_charts.swift` (lines 148–442), the 3 source PNGs (`output/charts/funnel_waterfall.png`, `output/charts/mauboussin_fade_dcf.png`, `output/charts/case_study_irr_pe.png`), and the 3 rendered slide PNGs (`output/verify/slide_04.png`, `output/verify/slide_12.png`, `output/verify/slide_15.png`):
- **Chart 1 (`funnel_waterfall.png`, lines 150–241):** Bar widths scale linearly (`CGFloat(row.rem) / 1175.0 * 670.0`), cuts (`30, 156, 506, 108, 16, 134`) and remainders (`1175, 1145, 989, 483, 375, 359, 225`) and percentages (`-2.6%, -13.3%, -43.1%, -9.2%, -1.4%, -11.4%, 19.1%`) match live v7.19 values; dashed connectors align with the prior row's remaining bar edge.
- **Chart 2 (`mauboussin_fade_dcf.png`, lines 246–335):** Illustrates `N = 25Y` (`MSFT` baseline: `RONIC₀ = 50%`, `g₀ = 11.5%`, `r = 8.50%`), fading linearly over `t = 1..25` to `RONIC_term = 20%` (`min(0.50, 0.20, 0.085 + 0.5*(0.50 - 0.085)) = 0.20`) and `g_term = 3.0%`, matching `gates.py:399-412` (`frac = (t - 1) / (N - 1)`). Zero clipping or label overlap.
- **Chart 3 (`case_study_irr_pe.png`, lines 340–437):** Plots exact live Bellman 5Y IRRs (`MSFT +10.3%`, `SPGI +3.5%`, `ASML.NL -0.7%`, `COST -4.6%`, `WM -10.5%`, `CRM +4.7%` hollow warning bar with `✗ G4 FAIL`) against the `8.5%` hurdle line. Zero label overlap or axis error.

---

## 2. Logic Chain

1. By running `gslides readonly read` and `gslides readonly get-notes` directly against `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` and cross-checking `output/deck/pres_read.json` and `output/Quality_Moat_Screener_v7.19.pptx` XML, we verified that the live Google Slides deck, JSON AST, and PPTX export are synchronized (`0` missing body tokens across 16/16 slides).
2. By executing `collect_screener_data()` and `screener.gates` functions in read-only mode (plus `unittest discover -s tests` passing 317/317), we verified every quantitative metric on all 16 slides and all 3 charts (`generate_charts.swift` + PNGs) matches live v7.19 data.
3. Checking Slide 13 speaker notes revealed the specific claim `"individual insurers like HNR1.DE at 14.3% RONIC0 sit at 10.89x"`. Live `collect_screener_data()` shows `HNR1.DE` has `roic_exp (RONIC₀) = 19.02%` (`roe_median = 19.02%`) and `term_mult = 10.97×` (`10.9657×`), not `14.3%` and `10.89×`. Furthermore, `G.terminal_multiple(0.143, 0.1025, 0.030) = 10.42×`. Grepping `output/` located `output/par_recompute_report.csv:557` where `HNR1.DE` had `mult_low_5y = 10.89` (5-year low P/E) and `cagr_oe_eps = 0.143` (Owner EPS CAGR) — proving those two unrelated historical columns were mistakenly cited as `RONIC₀` and `0g` terminal P/E.
4. Because `ORIGINAL_REQUEST.md` requires zero factual discrepancies across the presentation and Slide 13 speaker notes are live in `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`, the verdict must be **`REQUEST_CHANGES`** until that single speaker note line is corrected and synced.

---

## 3. Caveats

- **Slide 6 rounded archetype percentages:** `124/225 = 55.1% → 55%`, `71/225 = 31.6% → 32%`, `17/225 = 7.6% → 8%`, `13/225 = 5.8% → 6%` (sum `101%` purely from integer rounding). Acceptable.
- **Slide 11 shorthand `(+6% refranchising guard)`:** In `screener/fetch/metrics.py:320`, the refranchising guard is a `6.0%` ceiling (`min(0.060, nop_p25, oe_p25)`), not an additive `+6pp` boost; contextually clear as "plus the 6% refranchising guard," though `"6% cap refranchising guard"` would be even less ambiguous if desired.
- **PPTX media SHA256 re-encoding:** Embedded `ppt/media/image1..3.png` differ in byte hash from `output/charts/*.png` due to Google Slides' standard export PNG re-compression; visual inspection of `output/verify/slide_04.png`, `slide_12.png`, and `slide_15.png` confirms identical rendered charts.

---

## 4. Conclusion

**Verdict: `REQUEST_CHANGES`**

1. **Required Fix (Slide 13 Speaker Notes):** Update `slide_1795014495932258000_372` speaker notes (via `gslides mutate set-notes`), `output/deck/build_batch.py:532`, and `output/deck/batch.json:4917` to replace `"individual insurers like HNR1.DE at 14.3% RONIC0 sit at 10.89x"` with live verified v7.19 values — e.g.:
   - `"individual insurers like HNR1.DE at 19.0% RONIC0 sit at 10.97x"` (verified: `HNR1.DE` `roic_exp = 0.1902`, `term_mult = 10.9657`), **or**
   - `"individual insurers like MUV2.DE at 18.2% RONIC0 sit at 10.88x"` (verified: `MUV2.DE` `roic_exp = 0.1816`, `term_mult = 10.8801`).
   Then re-export `output/Quality_Moat_Screener_v7.19.pptx` and refresh `output/deck/pres_read.json`.
2. **All other content passes 100%:** Every on-slide number, formula, threshold, attrition count, cohort count, 6 case studies, 3 `Growth at ~0g` examples, and all 3 PNG charts (`generate_charts.swift`) are empirically verified against live Screener v7.19.

---

## 5. Verification Method

Run from `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`:
1. Confirm live Slide 13 speaker notes (standalone, `BypassSandbox: false`):
   `gslides readonly get-notes 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --slide slide_1795014495932258000_372`
2. Confirm `HNR1.DE` live v7.19 values (`roic_exp = 0.1902`, `term_mult = 10.9657`) and `terminal_multiple(0.143, 0.1025, 0.030) = 10.42`:
   ```bash
   python3 -c 'from screener import gates as G; from screener.dashboard import collect_screener_data; d=collect_screener_data(); h=[c for c in d["companies"] if c["id"]=="HNR1.DE"][0]; print(h["roic_exp"], round(h["term_mult"],4), round(G.terminal_multiple(0.143,0.1025,0.030),4))'
   ```
3. Confirm full unit test suite: `python3 -m unittest discover -s tests` (`Ran 317 tests — OK`).
- **Invalidation condition:** Any update to `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`, `output/deck/*`, or `data/{us,eu,ca}/*` requires re-running steps 1–2.
