# Empirical Quant Parity & Chart Data Challenge — `slides_challenger_iter2_2b` (Hard Handoff)

**Explicit Verdict:** **`APPROVED`** (`0` factual, numerical, token, speaker-note, or chart discrepancies across all 16 live slides, `.pptx`, `pres_read.json`, `batch.json`, and 3 PNG charts).

---

## 1. Observation

### 1.1 Live Google Slides API Verification (`gslides readonly`)
1. `gslides readonly read 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` (`BypassSandbox: false`) → exited `0`, returned all 16 slides (`p` + `slide_1795014495931708000_22` .. `slide_1795014495932534000_475`).
2. `gslides readonly get-notes 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --slide slide_1795014495932258000_372` (Slide 13, `BypassSandbox: false`) → exited `0`, verbatim:
   > `"Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at the exact formula ceiling (1 - 3%/20%)/(10.25% - 3%) = 11.72x (superseding the earlier 10.89x draft ref)—individual insurers like MUV2.DE at 18.2% RONIC0 sit at 10.88x and HNR1.DE at 19.0% RONIC0 sit at 10.97x. Reverse-DCF flips the model to ask what growth today's price already assumes."`
3. `gslides readonly get-notes` also verified Slide 9 (`slide_1795014495931957000_247`, exited `0`) and Slide 11 (`slide_1795014495932144000_313`, exited `0`).

### 1.2 Synchronization Across Live Deck, `pres_read.json`, `batch.json`, and `.pptx` XML
- **Live Slides ↔ `output/deck/pres_read.json`:** `LIVE_VS_PRES_SLIDE_01..16: missing=[]` and reverse check (`live -> pres_read.json`) `extra_any: False` across all 16 slides.
- **`output/deck/batch.json` ↔ `pres_read.json`:** `batch->pres_read checked=276, missing=[]`.
- **`output/Quality_Moat_Screener_v7.19.pptx` (`testzip: None`, `16` slides, `16` `notesSlides`):**
  - `PPTX_SLIDE_01..16: missing_tokens=[]` (100% body token parity across all 16 slides).
  - `notesSlide13.xml` text is **byte-for-byte identical** (`notes13 exact prefix match: True`, `notes13 trailing suffix: ''`) to the live Slide 13 speaker notes returned by `gslides readonly get-notes`.
  - All 16 `batch.json` `set-notes` operations match `ppt/notesSlides/notesSlide1..16.xml` exactly (`True`).

### 1.3 Read-Only Python Parity Checks vs. `collect_screener_data()`, `screener/gates.py`, `screener/fetch/metrics.py`
1. **Slide 13 Speaker Notes & `terminal_multiple` Parity:**
   - Operating 0g/3% ceiling: `G.terminal_multiple(0.50, 0.085, 0.030) = 15.4545×` → **`15.45×`** (matches Slide 13 subtitle, Quad ①, and speaker notes).
   - BS Financials 0g/3% ceiling: `G.terminal_multiple(0.50, 0.1025, 0.030) = 11.7241×` → **`11.72×`** (matches Slide 13 subtitle, Quad ①, and speaker notes).
   - Zero-spread invariance (`RONIC = r`): `G.terminal_multiple(0.085, 0.085, 0.030) = 11.7647×` (`11.76×`), `G.terminal_multiple(0.1025, 0.1025, 0.030) = 9.7561×` (`9.76×`) (matches Slide 12 & Slide 13 Quad ①).
   - **`MUV2.DE`:** `bs_fin=True`, `disc_rate=10.25%`, `roic_exp=18.16%` (`18.2%`), `term_mult=10.8801×` (`10.88×`); `G.terminal_multiple(0.1816, 0.1025, 0.030) = 10.8801×`. **MATCH.**
   - **`HNR1.DE`:** `bs_fin=True`, `disc_rate=10.25%`, `roic_exp=19.02%` (`19.0%`), `term_mult=10.9657×` (`10.97×`); `G.terminal_multiple(0.1902, 0.1025, 0.030) = 10.9657×`. **MATCH.**
2. **Slide 11 & Slide 13 Quad ①/④ Thresholds & Code Alignment:**
   - **Slide 11 Card ③:** `(6% refranchising cap).` matches `screener/fetch/metrics.py:320` (`g_tri = min(0.060, nop_p25, oe_p25)`). Buyback clamp `[−3.0%, +3.5%]`, `τ₀=6%`, `3.0%` target, `13.0%` cap, `Δt ≥ 5y` all match.
   - **Slide 13 Quad ①:** `Current Price vs Fair Value vs 0g Floor (3% inflation, max 15.45× op / 11.72× BS fin; zero-spread 11.76× / 9.76×).` — all thresholds intact and exact.
   - **Slide 13 Quad ④:** `• 1.0× BVPS: MTM HoldCo anchor.`, `• No value: Fair Value ≤ 0.`, `• No data: BLOCKING_AUTO_NOTES.` — matches `screener/gates.py:723, 743, 757, 769` (`G.BLOCKING_AUTO_NOTES = ('stale fundamentals', 'share count changed since FY', 'currency switch unresolved', 'earnings dominated by non-cash marks')`).
3. **Universe, Funnel, Archetypes, CAP, Cohorts, `Growth at ~0g`, and 6 Case Studies (`collect_screener_data()`):**
   - **Version & Price Date:** `version = "7.19"`, `price_updated_at = "2026-11-17"`.
   - **Universe (`1,175`):** `eu: 602` (`51.23%` → `51%`), `us: 515` (`43.83%` → `44%`), `ca: 58` (`4.94%` → `5%`); `RES_REVIEW = 0` (`0` unreviewed gates); `data/eu/markets.csv` has `2` `in_market=N` (`Greece`, `Poland`); `data/{us,eu,ca}/prescreen.csv` have `7`, `8`, `3` `g6_default=N` sub-industries.
   - **Funnel (`1,175 → 225`):** Stage 1 fails `692` (`G1: -30` → `1,145`, `G2: -156` → `989`, `G3: -506` → `483`); Stage 2 (`483` firms): `G4: -108` → `375`, `G5: -16` → `359`, `G6: -134` → `225` Prime Grade (`19.15%` → `19.1%`).
   - **Prime Grade (`225`):** `110 US | 104 EU | 11 CA`; `220 Valued, 5 No data, 0 No value`; median excess 5Y IRR `−11.7061pp` (`−11.7pp`).
   - **Prime Archetypes (`225`):** `Toll booth & switching costs`: `124` (`55%`), `Irreplaceable infrastructure & intangibles`: `71` (`32%`), `Scale economies shared`: `17` (`8%`), `R&D & innovation leadership`: `13` (`6%`).
   - **Prime CAP Distribution (`225`):** `15Y: 51`, `20Y: 114`, `25Y: 57`, `30Y: 3`.
   - **Quality Grade (`443`):** `221 US | 204 EU | 18 CA` (`G1–G3 pass & g6_flags < 3`).
   - **Growth at ~0g (`25`):** Using `g_org_exp >= 0.05` and `g_market < 0.05` on Valued Quality Grade: `25` (`11 US, 14 EU`; `9 Quality pass`, `6 Rejected – G6`, `10 Rejected – G4` [`6` at `5Y`, `4` at `10Y`]).
     - `ZTS`: `irr=22.43%` (`+22.4%`), `price=$83.48` (`$83`), `par_val=$146.23` (`$146`), `term_val=$94.19` (`$94`).
     - `PGHN.CH`: `irr=16.55%` (`+16.5%`).
     - `PGR`: `irr=18.33%` (`+18.3%`).
   - **6 Case Studies (Slide 15 & Chart 3):**
     - `MSFT`: `cap=25`, `cur_mult=28.24×`, `par_mult=30.51×`, `g_org_exp=11.51%`, `g_market=10.52%`, `irr=10.29%`, `vs_par=-7.47%` (`✓ Prime −7.5%`).
     - `SPGI`: `cap=30`, `cur_mult=25.38×`, `par_mult=20.33×`, `g_org_exp=7.01%`, `g_market=9.87%`, `irr=3.50%`, `vs_par=+24.83%` (`Prime +24.8%`).
     - `ASML.NL`: `cap=25`, `cur_mult=49.81×`, `par_mult=32.49×`, `g_org_exp=12.30%`, `g_market=17.51%`, `irr=-0.74%`, `vs_par=+53.32%` (`Prime +53.3%`).
     - `COST`: `cap=30`, `cur_mult=53.47×`, `par_mult=28.91×`, `g_org_exp=10.00%`, `g_market=16.51%`, `irr=-4.57%`, `vs_par=+84.91%` (`Prime +84.9%`).
     - `WM`: `cap=25`, `cur_mult=35.96×`, `par_mult=14.45×`, `g_org_exp=5.62%`, `g_market=23.51%`, `irr=-10.51%`, `vs_par=+148.86%` (`Prime +148.9%`).
     - `CRM`: `cap=5` (`4_sub=2`), `cur_mult=17.83×`, `par_mult=15.06×`, `g_org_exp=11.63%`, `g_market=26.59%`, `irr=4.74%`, `Rejected – G4 Runway (<15Y)` (`Reject`, `✗ G4 (4_sub=2)` on slide, `+4.7% ✗ G4 FAIL` in Chart 3).
4. **Chart PNGs & Rendered Slides (`view_file`) + Unit Tests:**
   - Inspected `output/charts/funnel_waterfall.png`, `output/charts/mauboussin_fade_dcf.png`, `output/charts/case_study_irr_pe.png`, and re-exported `output/verify/slide_04.png`, `slide_11.png`, `slide_12.png`, `slide_13.png`, `slide_15.png` via `view_file`: all chart bars, labels, fade curves (`50% → 20%`, `11.5% → 3.0%`, `r = 8.50%`), and IRRs (`+10.3%`, `+3.5%`, `−0.7%`, `−4.6%`, `−10.5%`, `+4.7% ✗ G4 FAIL`) are exact and clean, and Slides 11 & 13 render with zero truncation or overflow.
   - `python3 -m unittest discover -s tests` → `Ran 317 tests in 55.317s — OK`.

---

## 2. Logic Chain

1. Live read-only queries against `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` and cross-verification against `output/deck/pres_read.json`, `output/deck/batch.json`, and `output/Quality_Moat_Screener_v7.19.pptx` prove all four artifacts are 100% synchronized (`0` missing body tokens across 16/16 slides, `276/276` batch text parity, `16/16` speaker-notes parity, and verbatim match between live Slide 13 notes and `notesSlide13.xml`).
2. Executing `collect_screener_data()` and `G.terminal_multiple()` proves the Iteration 2 Slide 13 speaker note update resolves the sole Iteration 1 factual defect: `MUV2.DE` (`roic_exp = 18.16%`, `term_mult = 10.88×`), `HNR1.DE` (`roic_exp = 19.02%`, `term_mult = 10.97×`), BS Financials ceiling (`11.72×`), and operating ceiling (`15.45×`) all match live Screener v7.19.
3. Re-checking Slide 11 (`(6% refranchising cap)`), Slide 13 Quad ①/④, all 1,175 universe/funnel/archetype/CAP/cohort/case-study metrics (`g_org_exp` as `g₀`), all 3 chart PNGs, re-exported PNGs (`slide_04`, `11`, `12`, `13`, `15`), and the 317-test suite confirms zero regressions and 100% quantitative parity.

---

## 3. Caveats

- In `collect_screener_data()`, the pure organic model growth plotted/tabulated as `g₀` in the screener and deck corresponds to `c["g_org_exp"]` (not `c["g_exp"]`, which includes `bb_eff`); verified `Growth at ~0g` (`25` firms) and all 6 case studies use `g_org_exp`, matching the screener's Buyback Discipline rule (`bb_eff` excluded from DCF `g₀`).
- No caveats on data freshness (`price_updated_at = 2026-11-17`, `version = "7.19"`) or synchronization.

---

## 4. Conclusion

**Verdict: `APPROVED`**

The Iteration 2 Google Slides presentation (`1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`), local `.pptx` (`output/Quality_Moat_Screener_v7.19.pptx`), `output/deck/pres_read.json`, `output/deck/batch.json`, and 3 chart PNGs achieve **100% empirical quantitative, gate, formula, speaker-note, and chart parity** with live Screener v7.19 (`collect_screener_data()`, `screener/gates.py`, `screener/fetch/metrics.py`).

---

## 5. Verification Method

Run from `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`:
1. Standalone read-only Google Slides checks (`BypassSandbox: false`):
   - `gslides readonly read 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`
   - `gslides readonly get-notes 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --slide slide_1795014495932258000_372`
2. Parity & test suite checks:
   - `python3 -m unittest discover -s tests` (`Ran 317 tests — OK`)
   - Cross-check `output/Quality_Moat_Screener_v7.19.pptx` XML, `output/deck/pres_read.json`, and `output/deck/batch.json` against `screener.dashboard.collect_screener_data()` and `screener.gates.terminal_multiple(...)`.
3. Visual chart/slide checks via `view_file` on `output/charts/*.png` and `output/verify/slide_04.png`, `slide_11.png`, `slide_12.png`, `slide_13.png`, `slide_15.png`.
- **Invalidation condition:** Any subsequent edit to `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`, `output/deck/*`, `output/Quality_Moat_Screener_v7.19.pptx`, `screener/*`, or `data/{us,eu,ca}/*` invalidates this verification.
