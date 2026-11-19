# Wordings & Speaker-Note Patch Design — `slides_explorer_iter2_3` (Hard Handoff)

**Summary:** Designed and verified exact, layout-safe patches (no source edits made) for `output/deck/build_batch.py` and live Google Slides (`1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`) covering: (1) replacing the erroneous `HNR1.DE` (`14.3% / 10.89x`) claim in Slide 13 speaker notes with live verified v7.19 values (`MUV2.DE` at `18.2% RONIC0` → `10.88x`, `HNR1.DE` at `19.0% RONIC0` → `10.97x`) plus explicit `11.72x` vs `10.89x` draft-ref reconciliation; (2) prepending concise 1-sentence plain-English intuition hooks to Slides 9 and 11 speaker notes; and (3) replacing `(+6% refranchising guard)` with `(6% refranchising cap)` on Slide 11 (shrinking text by 3 chars to guarantee 4-line wrap) while keeping Slide 13 on-slide `11.72×` clean (with an optional `"Exact formula"` footer tweak).

Unified diff saved to: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_explorer_iter2_3/build_batch_iter2_3.patch`

---

## 1. Observation

### 1.1 Live v7.19 Repo Values (`collect_screener_data()` & `screener/gates.py`)
Executed read-only Python query against `screener.dashboard.collect_screener_data()` and `screener.gates.terminal_multiple()`:
- Formula ceilings (`screener/gates.py:435-456`):
  - Operating (`r = 0.085`, `RONIC_term = 0.20`, `g_term = 0.030`): `(1 - 0.03/0.20)/(0.085 - 0.03) = 15.4545×` → **`15.45×`**
  - Balance-Sheet Financials (`r = 0.1025`, `RONIC_term = 0.20`, `g_term = 0.030`): `(1 - 0.03/0.20)/(0.1025 - 0.03) = 11.7241×` → **`11.72×`** (achieved live by `ADM.GB`, `AZA.SE`, `SAVE.SE`)
- Live v7.19 individual insurers (`collect_screener_data()`):
  - `HNR1.DE`: `roic_exp (RONIC₀) = 0.1902` (`19.02%`), `ronic_term = 0.1464` (`14.64%`), `term_mult = 10.9657` (**`10.97×`**)
  - `MUV2.DE`: `roic_exp (RONIC₀) = 0.1816` (`18.16%`), `ronic_term = 0.1421` (`14.21%`), `term_mult = 10.8801` (**`10.88×`**)
  - `PGR`: `roic_exp (RONIC₀) = 0.2137` (`21.37%`), `ronic_term = 0.1581` (`15.81%`), `term_mult = 11.1758` (**`11.18×`**)
- Origin of the erroneous `10.89×` / `14.3%` reference:
  - `data/eu/financials.csv:279` (`HNR1.DE`) contains `mult_low_5y = 10.89` and `cagr_oe_eps = 0.143`, while `roe_median = 0.1902`. Those two unrelated historical columns were mistakenly carried into `ORIGINAL_REQUEST.md:70` (`10.89× financials`) and `slides_spec_miner_deck/handoff.md:340` (`HNR1.DE (RONIC₀ = 14.3%) is 10.89×`).
- Refranchising guard (`screener/fetch/metrics.py:314-320`):
  - `g_tri = min(0.060, nop_p25, oe_p25)` when `rev_med < g_base` and `min(nop_p25, oe_p25) > rev_med` — it is a **`6.0%` ceiling**, not an additive `+6%` boost.

### 1.2 Live Deck AST (`output/deck/pres_read.json`), `output/deck/build_batch.py`, & Rendered PNGs (`output/verify/slide_{09,11,13}.png`)

| Slide | Target | `build_batch.py` Line | Live Slide / Element ID (`pres_read.json`) | Geometry / Run Style | Current Verbatim Text |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Slide 9** | Speaker Notes | `build_batch.py:404` | `slide_1795014495931957000_247` (`SLIDES_API1447910102_15`) | Speaker notes (50 words) | `"Part II computes intrinsic value purely from financial statements with zero analyst overrides. Owner EPS caps depreciation add-backs by operating cash flow minus net income, strips 1.5x impairment spikes and pre-IPO noise, deducts 20 percent of IFRS-16 leases, and decays stale earnings peaks to zero over four years."` |
| **Slide 11** | Card ③ Body | `build_batch.py:469` | `textbox_1795014495932194000_339` (on `slide_1795014495932144000_313`) | `x=380, y=166, w=130, h=92`, `12.5pt` Roboto, single textRun, `lineSpacing=112` | `"Balances Rev, NOPAT & Owner EPS (+6% refranchising guard)."` (58 chars; renders as 4 lines: `Balances Rev,` / `NOPAT & Owner EPS` / `(+6% refranchising` / `guard).`) |
| **Slide 11** | Speaker Notes | `build_batch.py:486` | `slide_1795014495932144000_313` (`SLIDES_API1447910102_19`) | Speaker notes (54 words) | `"Growth g0 comes from a four-pillar statistical pipeline over 10 years of statements: a dilution-only share index, cycle-spanning Theil-Sen slopes over 5-plus-year spans to ignore 1-year COVID flukes, three-driver triangulation across revenue, NOPAT, and Owner EPS, and Empirical Bayes shrinkage toward 3 percent inflation capped smoothly at 13 percent."` |
| **Slide 13** | Footer Left | `build_batch.py:514` | `textbox_1795014495932265000_377` (on `slide_1795014495932258000_372`) | `x=30, y=360, w=540, h=15`, `10pt` Roboto, single textRun, `lineSpacing=105` | `"Verified 0g / 3% max terminal P/E: 15.45× operating  \|  11.72× BS financials"` (74 chars; occupies ~62% of `w=540` on 1 line) |
| **Slide 13** | Quadrant ① Body | `build_batch.py:517` | `textbox_1795014495932275000_383` (on `slide_1795014495932258000_372`) | `x=44, y=130, w=292, h=76`, `13.5pt` Roboto, single textRun, `lineSpacing=116` | `"Current Price vs DCF Fair Value vs Standalone 0g Floor (3% inflation, max 15.45× op / 11.72× BS fin; zero-spread 11.76× / 9.76×)."` (127 chars; renders cleanly in 3 balanced lines) |
| **Slide 13** | Speaker Notes | `build_batch.py:532` | `slide_1795014495932258000_372` (`SLIDES_API1447910102_23`) | Speaker notes (74 words) | `"Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at (1 - 3%/20%)/(10.25% - 3%) = 11.72x—individual insurers like HNR1.DE at 14.3% RONIC0 sit at 10.89x. Reverse-DCF flips the model to ask what growth today's price already assumes."` |

---

## 2. Logic Chain

1. **Slide 13 Speaker Notes (`REQUEST_CHANGES` fix):** Live `collect_screener_data()` proves `HNR1.DE` has `RONIC₀ = 19.02%` and `term_mult = 10.97×` (not `14.3%` and `10.89×`), and `MUV2.DE` has `RONIC₀ = 18.16%` and `term_mult = 10.88×`. Replacing the erroneous clause with both verified insurers (`MUV2.DE at 18.2% RONIC0 sit at 10.88x and HNR1.DE at 19.0% RONIC0 sit at 10.97x`) and explicitly noting `(superseding the earlier 10.89x draft ref)` resolves both `slides_challenger_iter1_2`'s factual bug and `slides_challenger_iter1_1`'s spec-audit question. All 16 speaker notes in `build_batch.py` use plain ASCII `x` (`1.5x`, `15.45x`, `11.72x`, `17.8x`) and `g0`/`RONIC0` for spoken readability, so keeping `x` and `RONIC0` preserves uniform style inside the note.
2. **Slides 9 & 11 Speaker Notes (Brother pedagogy polish):** Prepending one ~20-word plain-English sentence to Slide 9 (`Accounting Net Income can be distorted by non-cash charges or stale boom years, so Owner EPS measures true cash earnings.`) and Slide 11 (`Rather than trusting noisy short-term surges, the model extracts durable organic growth and gently pulls extreme outliers back toward normal.`) gives non-quant readers the everyday intuition before introducing accrual/impairment mechanics and `"Empirical Bayes shrinkage"`, while staying within the deck's `37–74` word speaker-note cadence (`69` and `74` words respectively).
3. **Slide 11 On-Slide Clarity (`textbox_1795014495932194000_339`):** Because `screener/fetch/metrics.py:320` implements `g_tri = min(0.060, nop_p25, oe_p25)`, `(+6% refranchising guard)` can be misread as an additive `+6%` boost. Comparing exact character counts inside the `w=130` (`12.5pt` Roboto) box rendered in `slide_11.png`:
   - `"(6% cap refranchising guard)."` (`62` chars total) turns line 3 into `"(6% cap refranchising"` (`21` chars, exceeding the `18`-char `"(+6% refranchising"` line), likely forcing a 5-line wrap (`refranchising` / `guard).`).
   - **`"(6% refranchising cap)."`** (`55` chars total — 3 chars *shorter* than current) produces `"(6% refranchising"` (`17` chars) + `"cap)."` (`5` chars), guaranteeing an identical 4-line wrap matching Cards ①–④ while removing the `+6%` ambiguity completely.
4. **Slide 13 On-Slide Clarity (`textbox_1795014495932275000_383` & `textbox_1795014495932265000_377`):**
   - Quadrant ① (`textbox_...383`) renders as 3 balanced lines (`127` chars) matching Quadrants ② and ③. Adding `(vs 10.89× draft ref)` on-slide would either force a 4th line or confuse the user's brother with stale draft artifacts. Keeping Quadrant ① untouched preserves 100% mathematical accuracy (`11.72× BS fin; zero-spread 11.76× / 9.76×`) and visual symmetry.
   - Footer (`textbox_...377`, `w=540`, `10pt` Roboto) uses ~62% of its width. Changing `"Verified 0g / 3% max terminal P/E: ..."` to `"Exact formula 0g / 3% max terminal P/E: 15.45× operating  |  11.72× BS financials"` (`79` chars, +5 chars) explains *why* the ceiling is `11.72×` in plain English while staying comfortably on 1 line.

---

## 3. Caveats

- **Read-only scope:** No files in `output/deck/`, `screener/`, or Google Slides were modified by `slides_explorer_iter2_3`.
- **Line-wrap verification:** Because Pillow (`PIL`) is not installed in the Python environment, wrapping for Slide 11 Card ③ and Slide 13 Footer was verified by exact character-count and glyph-width comparison against the rendered `output/verify/slide_11.png` and `slide_13.png` screenshots. Both edits are net-shorter (`55` vs `58` chars on Slide 11 Card ③) or well inside slack (`79` chars in a `w=540` footer using ~62% width on Slide 13), and should be visually confirmed on re-rendered `slide_11.png` / `slide_13.png` after applying.
- **Unicode vs ASCII in speaker notes:** `build_batch.py` consistently uses ASCII `x` and `RONIC0`/`g0` across all 16 speaker notes (e.g., `1.5x`, `15.45x`, `11.72x`, `17.8x`). If Unicode `×` and `RONIC₀` are preferred in Slide 13 speaker notes, replace all occurrences (`15.45×`, `11.72×`, `10.89×`, `10.88×`, `10.97×`, `RONIC₀`) uniformly so the note never mixes `15.45x` with `10.97×`.

---

## 4. Conclusion

1. **Apply `build_batch_iter2_3.patch` to `output/deck/build_batch.py`** and run `python3 output/deck/build_batch.py` to regenerate and validate `output/deck/batch.json`.
2. **Apply the live `gslides` patch ops** (`set-notes` for Slides 9, 11, 13; `update-text` for `textbox_1795014495932194000_339` and optionally `textbox_1795014495932265000_377`) against `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`, then refresh `output/deck/pres_read.json`, re-export `output/Quality_Moat_Screener_v7.19.pptx` + PDF, and re-render `slide_11.png` / `slide_13.png`.

### 4.1 `output/deck/build_batch.py` (see `build_batch_iter2_3.patch`)

| Priority | Target | Before | After |
| :--- | :--- | :--- | :--- |
| **REQUIRED** | Slide 13 Notes (`build_batch.py:532`) | `"Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at (1 - 3%/20%)/(10.25% - 3%) = 11.72x—individual insurers like HNR1.DE at 14.3% RONIC0 sit at 10.89x. Reverse-DCF flips the model to ask what growth today's price already assumes."` | `"Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at the exact formula ceiling (1 - 3%/20%)/(10.25% - 3%) = 11.72x (superseding the earlier 10.89x draft ref)—individual insurers like MUV2.DE at 18.2% RONIC0 sit at 10.88x and HNR1.DE at 19.0% RONIC0 sit at 10.97x. Reverse-DCF flips the model to ask what growth today's price already assumes."` |
| **RECOMMENDED** | Slide 9 Notes (`build_batch.py:404`) | `"Part II computes intrinsic value purely from financial statements with zero analyst overrides. Owner EPS caps depreciation add-backs by operating cash flow minus net income, strips 1.5x impairment spikes and pre-IPO noise, deducts 20 percent of IFRS-16 leases, and decays stale earnings peaks to zero over four years."` | `"Accounting Net Income can be distorted by non-cash charges or stale boom years, so Owner EPS measures true cash earnings. Part II computes intrinsic value purely from audited statements with zero analyst overrides: Owner EPS caps depreciation add-backs by operating cash flow minus net income, strips 1.5x impairment spikes and pre-IPO noise, deducts 20 percent of IFRS-16 leases, and decays stale earnings peaks to zero over four years."` |
| **RECOMMENDED** | Slide 11 Notes (`build_batch.py:486`) | `"Growth g0 comes from a four-pillar statistical pipeline over 10 years of statements: a dilution-only share index, cycle-spanning Theil-Sen slopes over 5-plus-year spans to ignore 1-year COVID flukes, three-driver triangulation across revenue, NOPAT, and Owner EPS, and Empirical Bayes shrinkage toward 3 percent inflation capped smoothly at 13 percent."` | `"Rather than trusting noisy short-term surges, the model extracts durable organic growth and gently pulls extreme outliers back toward normal. Growth g0 comes from a four-pillar statistical pipeline over 10 years of statements: a dilution-only share index, cycle-spanning Theil-Sen slopes over 5-plus-year spans to ignore 1-year COVID flukes, three-driver triangulation across revenue, NOPAT, and Owner EPS, and Empirical Bayes shrinkage toward 3 percent inflation capped smoothly at 13 percent."` |
| **RECOMMENDED** | Slide 11 Card ③ (`build_batch.py:469`) | `"Balances Rev, NOPAT & Owner EPS (+6% refranchising guard)."` | `"Balances Rev, NOPAT & Owner EPS (6% refranchising cap)."` |
| **OPTIONAL** | Slide 13 Footer (`build_batch.py:514`) | `"Verified 0g / 3% max terminal P/E: 15.45× operating  \|  11.72× BS financials"` | `"Exact formula 0g / 3% max terminal P/E: 15.45× operating  \|  11.72× BS financials"` |
| **NO CHANGE** | Slide 13 Quad ① (`build_batch.py:517`) | `"Current Price vs DCF Fair Value vs Standalone 0g Floor (3% inflation, max 15.45× op / 11.72× BS fin; zero-spread 11.76× / 9.76×)."` | *(Keep as-is to preserve 3-line symmetry and avoid on-slide draft-ref clutter.)* |

### 4.2 Live Google Slides `gslides` Batch Patch Ops (for `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ`)
Exact `batch` operations matching `output/deck/patch_3_slides.json` format (verified single-run elements in `pres_read.json`):
```json
[
  {
    "op": "set-notes",
    "slide": "slide_1795014495932258000_372",
    "text": "Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at the exact formula ceiling (1 - 3%/20%)/(10.25% - 3%) = 11.72x (superseding the earlier 10.89x draft ref)—individual insurers like MUV2.DE at 18.2% RONIC0 sit at 10.88x and HNR1.DE at 19.0% RONIC0 sit at 10.97x. Reverse-DCF flips the model to ask what growth today's price already assumes."
  },
  {
    "op": "set-notes",
    "slide": "slide_1795014495931957000_247",
    "text": "Accounting Net Income can be distorted by non-cash charges or stale boom years, so Owner EPS measures true cash earnings. Part II computes intrinsic value purely from audited statements with zero analyst overrides: Owner EPS caps depreciation add-backs by operating cash flow minus net income, strips 1.5x impairment spikes and pre-IPO noise, deducts 20 percent of IFRS-16 leases, and decays stale earnings peaks to zero over four years."
  },
  {
    "op": "set-notes",
    "slide": "slide_1795014495932144000_313",
    "text": "Rather than trusting noisy short-term surges, the model extracts durable organic growth and gently pulls extreme outliers back toward normal. Growth g0 comes from a four-pillar statistical pipeline over 10 years of statements: a dilution-only share index, cycle-spanning Theil-Sen slopes over 5-plus-year spans to ignore 1-year COVID flukes, three-driver triangulation across revenue, NOPAT, and Owner EPS, and Empirical Bayes shrinkage toward 3 percent inflation capped smoothly at 13 percent."
  },
  {
    "op": "update-text",
    "element": "textbox_1795014495932194000_339",
    "text": "Balances Rev, NOPAT & Owner EPS (6% refranchising cap)."
  },
  {
    "op": "update-text",
    "element": "textbox_1795014495932265000_377",
    "text": "Exact formula 0g / 3% max terminal P/E: 15.45× operating  |  11.72× BS financials"
  }
]
```

---

## 5. Verification Method

1. **Verify patch applies cleanly (dry-run):**
   ```bash
   git apply --check .agents/teamwork/slides_explorer_iter2_3/build_batch_iter2_3.patch
   ```
2. **Verify live v7.19 figures cited in Slide 13 notes:**
   ```bash
   python3 -c 'from screener import gates as G; from screener.dashboard import collect_screener_data; d=collect_screener_data(); m={c["id"]:c for c in d["companies"]}; print("HNR1.DE:", round(m["HNR1.DE"]["roic_exp"]*100,1), round(m["HNR1.DE"]["term_mult"],2)); print("MUV2.DE:", round(m["MUV2.DE"]["roic_exp"]*100,1), round(m["MUV2.DE"]["term_mult"],2)); print("Ceilings:", round(G.terminal_multiple(0.50,0.085,0.03),2), round(G.terminal_multiple(0.50,0.1025,0.03),2))'
   ```
   Expected output: `HNR1.DE: 19.0 10.97`, `MUV2.DE: 18.2 10.88`, `Ceilings: 15.45 11.72`.
3. **Post-apply verification (by implementer):** Run `python3 output/deck/build_batch.py` (`validate_batch()` must pass), confirm `gslides readonly get-notes` on Slides 9, 11, 13 and `gslides readonly list-slides --json == pres_read['slides']`, and inspect re-rendered `output/verify/slide_11.png` and `slide_13.png`.
- **Invalidation condition:** Any update to `data/{us,eu,ca}/financials.csv` or `output/deck/build_batch.py` invalidates line numbers / figures in this handoff.
