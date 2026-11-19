# Iteration 2 Empirical Quant Parity & Chart Data Challenge — `slides_challenger_iter2_2` (Hard Handoff)

**Explicit Verdict:** **`APPROVE`**

All empirical checks across the live Google Slides presentation (`1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`), `output/Quality_Moat_Screener_v7.19.pptx`, `output/deck/pres_read.json`, `output/deck/batch.json`, `output/deck/build_batch.py`, and all 3 chart PNGs (`output/charts/*.png` + rendered `output/verify/slide_{04,12,15}.png`) pass **100% parity** against live Screener v7.19 (`screener.dashboard.collect_screener_data()`, `price_updated_at = 2026-11-17`, `screener/gates.py`, `screener/fetch/metrics.py`, `screener/config.py`) with **0** discrepancies. The Iteration 1 Slide 13 speaker notes defect (`HNR1.DE 14.3% / 10.89x`) is resolved and verified identically across live Google Slides, `notesSlide13.xml`, `pres_read.json`, `batch.json`, and `build_batch.py`.

---

## 1. Observation

### 1.1 Live Google Slides Queries (`gslides readonly`)
1. `gslides readonly read 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` (`BypassSandbox: false`) → exited `0`, returned all 16 slides (`p` + `slide_1795014495931708000_22` .. `slide_1795014495932534000_475`).
   - Exact token sequence comparison against `output/deck/pres_read.json` across all 16 slides: `True` (`0` differences, `0` stale slides).
2. `gslides readonly get-notes 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --slide slide_1795014495932258000_372` (Slide 13, `BypassSandbox: false`) → exited `0`, returned verbatim:
   > `Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at the exact formula ceiling (1 - 3%/20%)/(10.25% - 3%) = 11.72x (superseding the earlier 10.89x draft ref)—individual insurers like MUV2.DE at 18.2% RONIC0 sit at 10.88x and HNR1.DE at 19.0% RONIC0 sit at 10.97x. Reverse-DCF flips the model to ask what growth today's price already assumes.`
3. `gslides readonly get-notes` on Slide 11 (`slide_1795014495932144000_313`) and Slide 9 (`slide_1795014495931957000_247`) (`BypassSandbox: false`) → exited `0`, returned clean plain-English speaker notes matching `batch.json`, `pres_read.json`, and `notesSlide*.xml`.

### 1.2 `.pptx` XML, `pres_read.json` & `batch.json` Parity
- **PPTX Archive & XML Check (`output/Quality_Moat_Screener_v7.19.pptx`):**
  - `zipfile.ZipFile.testzip()` → `None` (valid ZIP).
  - `16` `ppt/slides/slide*.xml`, `16` `ppt/notesSlides/notesSlide*.xml`.
  - Slide body token parity (`pres_read.json` tokens vs `ppt/slides/slide*.xml`):
    - `PPTX_SLIDE_01..16`: `missing_tokens=[]` on all 16/16 slides (`pres_tokens`: 41, 100, 130, 56, 124, 115, 150, 128, 126, 128, 115, 91, 120, 132, 87, 121).
  - Speaker notes parity across all 16 slides (`batch.json` `set-notes` == `pres_read.json` `notesPage` == `ppt/notesSlides/notesSlide*.xml`): **`True` (16/16 exact match)**, including `notesSlide13.xml` matching live `gslides readonly get-notes` verbatim.
- **Batch Body Text Parity (`output/deck/batch.json` vs `output/deck/pres_read.json`):**
  - `276 / 276` body text strings checked (`add-textbox`, `add-shape`, `set-table-cell`), `missing: 0`.
  - `output/deck/build_batch.py` (`lines 467–534`) matches `batch.json` for Slide 11 (`lines 470, 487`) and Slide 13 (`lines 515–533`).

### 1.3 Slide 11 & Slide 13 Targeted Iteration 2 Verification
- **Slide 11 (`slide_1795014495932144000_313`, `output/verify/slide_11.png`):**
  - Card ③ (`textbox_...339`): `"Balances Rev, NOPAT & Owner EPS (6% refranchising cap)."` — accurately reflects `g_tri = min(0.060, nop_p25, oe_p25)` in `screener/fetch/metrics.py:320` (removing the Iteration 1 `+6%` ambiguity).
  - Other Slide 11 constants verified: `10Y`, `S_t`, `Δt ≥ 5y`, `P50`/`P25`, `τ₀=6%`, `3.0%`, `13.0%`, `bb_eff` `[−3.0%, +3.5%]` (`M.TAU_PRIOR_STAT = 0.06`, `G.BUYBACK_CLAMP = (-0.03, 0.035)`).
- **Slide 13 (`slide_1795014495932258000_372`, `output/verify/slide_13.png`):**
  - Subtitle (`textbox_...377`): `"Exact formula 0g / 3% max terminal P/E: 15.45× operating  |  11.72× BS financials"`.
  - Quad ① (`textbox_...383`): `"Current Price vs Fair Value vs 0g Floor (3% inflation, max 15.45× op / 11.72× BS fin; zero-spread 11.76× / 9.76×)."`
  - Quad ④ (`textbox_...398`): `"• 1.0× BVPS: MTM HoldCo anchor.\n• No value: Fair Value ≤ 0.\n• No data: BLOCKING_AUTO_NOTES."`
  - Speaker notes verified against `screener.dashboard.collect_screener_data()` & `screener/gates.py`:
    - `G.terminal_multiple(0.50, 0.085, 0.030) = 15.4545` (`15.45×`)
    - `G.terminal_multiple(0.50, 0.1025, 0.030) = 11.7241` (`11.72×`)
    - Zero-spread `1/0.085 = 11.7647` (`11.76×`), `1/0.1025 = 9.7561` (`9.76×`)
    - `MUV2.DE`: `bs_fin = True`, `disc_rate = 0.1025`, `roic_exp = 18.16%` (`18.2%`), `term_mult = 10.8801` (`10.88×`), `terminal_multiple(roic_exp, 0.1025, 0.030) = 10.8801`
    - `HNR1.DE`: `bs_fin = True`, `disc_rate = 0.1025`, `roic_exp = 19.02%` (`19.0%`), `term_mult = 10.9657` (`10.97×`), `terminal_multiple(roic_exp, 0.1025, 0.030) = 10.9657`

### 1.4 Full v7.19 Live Data Re-Verification (`collect_screener_data()`, `gates.py`, `metrics.py`, `config.py`)
- **Version & Universe:** `version = 7.19`, `price_updated_at = 2026-11-17`; `1,175` companies (`us: 515`, `eu: 602`, `ca: 58`); `RES_REVIEW = 0`.
- **Pre-Screen & Stages:**
  - `data/eu/markets.csv`: `Greece` (`N`) & `Poland` (`N`) = `28` companies (`Greece: 10, Poland: 18`), all `Rejected – G2 Essential Need`.
  - `data/*/prescreen.csv`: `18` sub-industries (`us: 7, eu: 8, ca: 3`) with `g6_default = N` → `143` companies (`us: 44, eu: 89, ca: 10`).
  - Stage 1 fails: `692` (`0` non-blank G4–G6); Stage 2 firms: `483` (`0` blank G4–G6).
- **Funnel Attrition (`1,175 → 225`):**
  - G1 `−30 (−2.6%) → 1,145`; G2 `−156 (−13.3%) → 989`; G3 `−506 (−43.1%) → 483`; G4 `−108 (−9.2%) → 375`; G5 `−16 (−1.4%) → 359`; G6 `−134 (−11.4%) → 225 (19.1%)`.
- **Prime Grade Archetypes & CAP (225):**
  - Archetypes: `Toll booth & switching costs: 124 (55.1%)`, `Irreplaceable infrastructure & intangibles: 71 (31.6%)`, `Scale economies shared: 17 (7.6%)`, `R&D & innovation leadership: 13 (5.8%)`.
  - Archetype examples (`MSFT`, `SPGI`, `WM`, `RMS.FR`, `COST`, `PGR`, `ASML.NL`): all `Quality pass` and match exact archetype.
  - Prime CAP distribution: `{15: 51, 20: 114, 25: 57, 30: 3}`.
  - Gate 4 deterministic rules (`screener/gates.py:41-90`): `0Y (m_max=0), 15Y (1,1), 20Y (1,>=2 or 2,2), 25Y (2,3), 30Y (2,>=4)`; haircut `0→0, 1-2→5, 3-4→10, 5→15`; any Force `= 2` → Fatal-Flaw Cap (`<= 10Y`).
- **Decision Cohorts & Examples:**
  - `Prime Grade`: `225` (`110 US, 104 EU, 11 CA`), `220 Valued, 5 No data, 0 No value`, `median_excess_irr = -11.7061pp` (`−11.7pp`).
  - `Growth at ~0g`: `25` (`11 US, 14 EU`; `9 Quality pass, 6 G6-fail, 10 G4-fail [6 at 5Y, 4 at 10Y]`).
  - `Quality Grade`: `443` (`221 US, 204 EU, 18 CA`).
  - `Growth at ~0g` examples: `ZTS` (`+22.43%` IRR, `$83.48` vs `$146.23` FV / `$94.19` 0g), `PGHN.CH` (`+16.55%`), `PGR` (`+18.33%`).
- **6 Case Studies (`MSFT`, `SPGI`, `ASML.NL`, `COST`, `WM`, `CRM`):**
  - `MSFT`: `cap=25`, `curPE=28.24`, `fairPE=30.51`, `g_org_start=11.51%`, `g_mkt=10.52%`, `irr=+10.29%`, `vs_par=-7.47%`, `Quality pass`.
  - `SPGI`: `cap=30`, `curPE=25.38`, `fairPE=20.33`, `g_org_start=7.01%`, `g_mkt=9.87%`, `irr=+3.50%`, `vs_par=+24.83%`, `Quality pass`.
  - `ASML.NL`: `cap=25`, `curPE=49.81`, `fairPE=32.49`, `g_org_start=12.30%`, `g_mkt=17.51%`, `irr=-0.74%`, `vs_par=+53.32%`, `Quality pass`.
  - `COST`: `cap=30`, `curPE=53.47`, `fairPE=28.91`, `g_org_start=10.00%`, `g_mkt=16.51%`, `irr=-4.57%`, `vs_par=+84.91%`, `Quality pass`.
  - `WM`: `cap=25`, `curPE=35.96`, `fairPE=14.45`, `g_org_start=5.62%`, `g_mkt=23.51%`, `irr=-10.51%`, `vs_par=+148.86%`, `Quality pass`.
  - `CRM`: `cap=5`, `curPE=17.83`, `fairPE=15.06`, `g_org_start=11.63%`, `g_mkt=26.59%`, `irr=+4.74%`, `vs_par=+18.39%`, `Rejected – G4 Runway (<15Y)`.
- **Chart PNGs & Rendered Slides:**
  - Directly inspected `output/deck/generate_charts.swift:145-442`, `output/charts/funnel_waterfall.png`, `output/charts/mauboussin_fade_dcf.png`, `output/charts/case_study_irr_pe.png`, and rendered `output/verify/slide_04.png`, `slide_11.png`, `slide_12.png`, `slide_13.png`, `slide_15.png` — all plotted data, labels, hurdle lines, and layouts match live v7.19 values cleanly with zero clipping or overlap.
- **Unit Test Suite:**
  - `python3 -m unittest discover -s tests` → `Ran 317 tests in 63.689s — OK`.

---

## 2. Logic Chain

1. Querying `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` directly via `gslides readonly read` and `gslides readonly get-notes` and comparing token sequences against `output/deck/pres_read.json` proves the local JSON AST and live Google Slides deck are 100% synchronized (`16/16` slides).
2. Inspecting `output/Quality_Moat_Screener_v7.19.pptx` via `zipfile` and `xml.etree.ElementTree` proves `0` missing body tokens across all 16 slides (`PPTX_SLIDE_01..16`), `testzip() == None`, and `16/16` exact speaker-note equality across `batch.json`, `pres_read.json`, and `ppt/notesSlides/notesSlide*.xml` (with `notesSlide13.xml` matching live Slide 13 speaker notes verbatim).
3. Executing `collect_screener_data()` and `screener.gates.terminal_multiple()` directly proves the Iteration 1 Slide 13 speaker-notes defect is fully cured (`MUV2.DE`: `18.16% → 10.8801×`; `HNR1.DE`: `19.02% → 10.9657×`; BS Financials ceiling `11.7241×`; operating ceiling `15.4545×`), Slide 11's `(6% refranchising cap)` unambiguously matches `metrics.py:320`, Slide 13 Quad ①/④ retain every exact threshold after `14 pt` reflow, and all universe/funnel/archetype/CAP/cohort/case-study/chart figures match live v7.19 with 0 discrepancies and 317/317 passing tests.
4. Therefore, all empirical quant parity and chart data acceptance criteria are satisfied and the verdict is **`APPROVE`**.

---

## 3. Caveats

No caveats — all live Google Slides reads, speaker notes, `.pptx` XML, `pres_read.json`, `batch.json`, `build_batch.py`, `collect_screener_data()`, `screener/gates.py`, `screener/fetch/metrics.py`, `output/charts/*.png`, rendered `output/verify/slide_*.png`, and the 317-test suite were directly executed and verified.

---

## 4. Conclusion

**Verdict: `APPROVE`**

Iteration 2 fixes on `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` (`https://docs.google.com/presentation/d/1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ/edit`) achieve **100% empirical quantitative parity** across all 16 slides, all 16 speaker notes (including Slide 13 `MUV2.DE`/`HNR1.DE`/`11.72×`), all 3 chart PNGs, `output/Quality_Moat_Screener_v7.19.pptx` XML, `output/deck/pres_read.json`, `output/deck/batch.json`, and `output/deck/build_batch.py`.

---

## 5. Verification Method

Run from `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`:
1. Live Google Slides read-only verification (`BypassSandbox: false`):
   - `gslides readonly read 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`
   - `gslides readonly get-notes 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --slide slide_1795014495932258000_372`
2. Live v7.19 insurer & ceiling parity check:
   ```bash
   python3 -c 'from screener import gates as G; from screener.dashboard import collect_screener_data; d=collect_screener_data(); by_id={c["id"]:c for c in d["companies"]}; print("ceilings:", round(G.terminal_multiple(0.5,0.085,0.03),4), round(G.terminal_multiple(0.5,0.1025,0.03),4)); print("MUV2.DE:", round(by_id["MUV2.DE"]["roic_exp"]*100,2), round(by_id["MUV2.DE"]["term_mult"],4)); print("HNR1.DE:", round(by_id["HNR1.DE"]["roic_exp"]*100,2), round(by_id["HNR1.DE"]["term_mult"],4))'
   ```
3. Full unit test suite: `python3 -m unittest discover -s tests` (`Ran 317 tests — OK`).
- **Invalidation condition:** Any subsequent mutation to `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`, `output/Quality_Moat_Screener_v7.19.pptx`, `output/deck/*`, `output/charts/*`, or `data/{us,eu,ca}/*` invalidates this approval and requires re-verification.
