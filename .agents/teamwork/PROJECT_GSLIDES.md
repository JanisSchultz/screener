# Project: Quality & Moat Screener (v7.19) — Google Slides Presentation

## 1. Objective & Scope
Create a complete, visually polished Google Slides presentation via `gslides` (connected account: `schultz.janis@gmail.com`) explaining the **Quality & Moat Screener (v7.19)** investment framework clearly for the user's brother.

- **Workspace Root**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`
- **Local Output Directory**: `output/` (charts in `output/charts/`, batch/generator scripts in `output/deck/`, verification thumbnails in `output/verify/`, optional `.pptx` export in `output/Quality_Moat_Screener_v7.19.pptx`).
- **Source of Truth**: `.agents/teamwork/ORIGINAL_REQUEST.md`, verified against live repo data (`price_updated_at = 2026-11-17`, `screener/gates.py`, `screener/dashboard.py:collect_screener_data()`).

---

## 2. Verified Fact Corrections & Exact Reference Values
All figures in `ORIGINAL_REQUEST.md` match live `v7.19` repo data (`317/317` tests passing), with **one verified formula correction**:
- **Standalone Terminal P/E (`0g` / `3%` inflation floor) max for Balance-Sheet Financials**: **`11.72×`** (`(1 - 0.030/0.20) / (0.1025 - 0.030) = 0.85 / 0.0725`), NOT `10.89×`. Operating companies max is **`15.45×`** (`r = 8.50%`). Zero-spread floors (`RONIC = r`) are `11.76×` op / `9.76×` fin. (Note in speaker notes that `HNR1.DE` has `10.89×` at `14.3%` `RONIC₀`.)
- **Verified `Growth at ~0g` (`25`) Prime Grade Live Examples**: **`ZTS`** (`$83.48` vs `$146.23` FV & `$94.19` `0g` floor, `g₀ = 8.7%` vs `g_mkt = +1.6%`, `+22.4%` 5Y IRR), **`PGHN.CH`** (`CHF 644.40` vs `891.33` FV & `763.76` `0g` floor, `+16.5%` 5Y IRR), **`PGR`** (`$234.67` vs `$327.53` FV, `+18.3%` 5Y IRR).
- **Verified 6 Case Studies (`2026-11-17`)**:
  - `MSFT`: `Quality pass`, `25Y` CAP (`30Y - 5Y`: `4_riv=1, 4_sub=1`), `G5=1, G6=Y`, `$506.24` vs `$547.10` FV (`-7.5%`), `0g $277.08`, `28.2×` Cur vs `30.5×` Fair P/E, `g₀=11.5%`, `g_mkt=10.5%`, `RONIC₀=50.0%`, **`+10.3%` 5Y IRR**
  - `COST`: `Quality pass`, `30Y` CAP, `G5=2, G6=Y`, `$1,110.08` vs `$600.33` FV (`+84.9%`), `0g $320.87`, `53.5×` vs `28.9×`, `g₀=10.0%`, `g_mkt=16.5%`, `RONIC₀=43.1%`, **`-4.6%` 5Y IRR**
  - `ASML.NL`: `Quality pass`, `25Y` CAP (`30Y - 5Y`), `G5=2, G6=Y`, `€1,236.80` vs `€806.65` FV (`+53.3%`), `0g €383.74`, `49.8×` vs `32.5×`, `g₀=12.3%`, `g_mkt=17.5%`, `RONIC₀=50.0%`, **`-0.7%` 5Y IRR**
  - `SPGI`: `Quality pass`, `30Y` CAP, `G5=1, G6=Y`, `$452.35` vs `$362.36` FV (`+24.8%`), `0g $264.91`, `25.4×` vs `20.3×`, `g₀=7.0%`, `g_mkt=9.9%`, `RONIC₀=24.4%`, **`+3.5%` 5Y IRR**
  - `WM`: `Quality pass`, `25Y` CAP, `G5=1, G6=Y`, `$242.69` vs `$97.52` FV (`+148.9%`), `0g $87.38`, `36.0×` vs `14.4×`, `g₀=5.6%`, `g_mkt=23.5%`, `RONIC₀=12.3%`, **`-10.5%` 5Y IRR**
  - `CRM`: `Rejected – G4 Runway (<15Y)`, `5Y` CAP (`20Y` init, `4_sub=2` AI Fatal Flaw), diag `G5=0, G6=Y`, `$194.52` vs `$164.31` FV, `17.8×` vs `15.1×`, `g₀=11.6%`, `g_mkt=26.6%`, `+4.7%` IRR (blocked @ G4).

---

## 3. Deck Architecture (16 Slides, `720 × 405 pt` Canvas)
Detailed slide-by-slide specification lives in `.agents/teamwork/slides_spec_miner_deck/handoff.md` (§3–§6), refined with the verified facts in §2 above:

| Slide | Title | Mode | Layout & Primary Visual |
|---:|---|---|---|
| 1 | **Quality & Moat Screener (v7.19)** | Dark `#1E2761` | Full-bleed title + `#2DD4BF` divider + 3 hero stat pills (`1,175`, `6 Gates`, `0 Overrides`) |
| 2 | **Global Universe & 5 Philosophical Foundations** | Light `#F5F7FA` | Left 3 region cards (`EU 602`, `US 515`, `CA 58`) + Right 5 numbered giant pillars (`①–⑤`) |
| 3 | **Pre-Screen Layer & Two-Stage Waterfall** | Light `#F5F7FA` | Top 2 pre-screen cards (`in_market`, `g6_default`) + Bottom Stage 1 vs Stage 2 connector flow (`0` blank) |
| 4 | **Global Funnel Attrition (`1,175 → 225 Prime Grade`)** | Dark `#1E2761` | Custom PNG `output/charts/funnel_waterfall.png` + Right 2 stat callouts (`19.1%` pass, `43.1%` G3 cut) |
| 5 | **Stage 1 Filters: Gates 1 & 2** | Light `#F5F7FA` | Two-column Pass `✓` / Reject `✗` cards (`G1 Understandability -30`, `G2 Essential/Habits -156 + 2r`) |
| 6 | **Gate 3: 4 Moat Archetypes & Proof of Moat (`3a` + `3b`)** | Light `#F5F7FA` | 4 archetype cards (`124`, `71`, `17`, `13`) + Bottom `3b` ROIC/ROIIC/Pricing hurdle banner |
| 7 | **Gate 4: Two-Step Deterministic CAP Engine (`CAP ≥ 15Y`)** | Dark `#1E2761` | 2-step flow (`CAP_init` + 5 Forces × 5 Macrotrends & Clock Speed, haircut, Fatal-Flaw `≤10Y`) + Prime CAP dist (`51/114/57/3`) + 3 Anti-Drift Rules |
| 8 | **Stage 2: Stewardship & Solvency (Gates 5 & 6)** | Light `#F5F7FA` | Left 5 Superinvestor vectors (`G5 ≥ 1`, `-16`) + Right 3 Solvency/Cash pillar cards (`G6`, `< 3` flags, `-134`) |
| 9 | **Part II: Slump-Cannibal Doctrine & Sanitized Owner EPS** | Dark `#1E2761` | Owner EPS formula banner + 4 accounting guard cards + Age-Weighted Reversion (`50% → 0%` over 4y) |
| 10 | **Capital Base & M&A-Matched `RONIC₀` (`≤ 50%`)** | Light `#F5F7FA` | Compact 3-regime table (Tangible, 5Y ROE, GAAP IFRIC-12) + Harmonic M&A blend (`> 1.25×` trigger) |
| 11 | **4-Pillar Statistical Organic Growth (`g₀ ≤ 13%`)** | Light `#F5F7FA` | 4-step connected pipeline (`S_t` → Theil–Sen `Δt≥5y` → 3-Driver + `6%` guard → EB `τ₀=6%` + `tanh`) + Buyback clamp `[-3%, +3.5%]` |
| 12 | **Explicit N-Year Mauboussin-Fade DCF (`r = 8.50% / 10.25%`)** | Dark `#1E2761` | Left PNG `output/charts/mauboussin_fade_dcf.png` + Right 3 formula cards (`E₁=1.0`, linear fade, MM `RONIC=r ⇒ 1/r`) |
| 13 | **3-Price Anchor, Bellman 5Y IRR & Reverse-DCF** | Light `#F5F7FA` | 2×2 quadrant cards (3-Price Anchor `15.45×/11.72×`, Bellman 5Y IRR, Reverse-DCF `[-20%,+50%]`, Special Physics & Circuit Breakers) |
| 14 | **Part III: Actionable Decision Cohorts** | Dark `#1E2761` | 3 big-stat cohort cards (`225 Prime Grade`, `25 Growth at ~0g` e.g. `ZTS`/`PGHN.CH`/`PGR`, `443 Quality Grade`) |
| 15 | **Live Case Studies: Quality vs. Price & Fatal Flaws** | Light `#F5F7FA` | Left 6-row table (`MSFT`, `SPGI`, `ASML.NL`, `COST`, `WM`, `CRM`) + Right PNG `output/charts/case_study_irr_pe.png` |
| 16 | **Brother's 4-Step Decision Playbook** | Dark `#1E2761` | 4 numbered action cards (`① Screen`, `② Invert g`, `③ 3-Price Anchor`, `④ IRR > Hurdle`) + Munger closing quote |

---

## 4. Verification Plan & Gate Criteria
Single Iteration Loop (2B):
1. **Worker (`slides_worker_iter1`)**:
   - Generate the 3 high-DPI PNG charts into `output/charts/` using `/usr/bin/swiftc` CoreGraphics (no external packages needed).
   - Verify/initialize `gslides` CLI and auth (`schultz.janis@gmail.com`).
   - Build complete `output/deck/batch.json` + execute `gslides mutate create` + `gslides mutate batch` + `gslides mutate insert-image-from-file` + positioning/sizing + speaker notes (`set-notes` on all 16 slides).
   - Export all 16 slide thumbnails (`output/verify/slide_01.png..slide_16.png`) and optional `.pptx` copy (`output/Quality_Moat_Screener_v7.19.pptx`), and run programmatic `gslides readonly info --json` / `read --json` checks.
2. **Reviewers (2 Independent `teamwork_reviewer`)**:
   - `slides_reviewer_iter1_1`: Independent **Visual & Layout Rubric Inspector** — views ALL 16 exported PNG thumbnails (`output/verify/slide_01.png..slide_16.png`) via `view_file` (image support!) and scores `V-1..V-7` strictly.
   - `slides_reviewer_iter1_2`: Independent **Factual & Structural Completeness Reviewer** — audits `gslides readonly read --json`, speaker notes, `S-1..S-5`, and 100% of Section C Factual Parity Checklist against `ORIGINAL_REQUEST.md` and `slides_explorer_repo/handoff.md`.
3. **Challengers (2 Empirical `teamwork_challenger`)**:
   - `slides_challenger_iter1_1`: Programmatic AST & Geometry Auditor — writes/runs a read-only Python verification script on `gslides readonly info <PRES_ID> --json` / `read --json` to empirically verify bounding boxes (`x >= 30, x+w <= 690, y >= 30, y+h <= 375`), zero pairwise text/element overlap, explicit font/color on 100% of elements, 16 slides, 16 speaker notes, zero placeholders.
   - `slides_challenger_iter1_2`: Empirical Quantitative Parity & Chart Verifier — checks every number in the live deck JSON + PNG charts (`output/charts/*.png`) directly against `screener.dashboard.collect_screener_data()` and `screener.gates`.
4. **Forensic Auditor (`teamwork_auditor`)**:
   - `slides_auditor_iter1_1`: Verifies authentic Google Slides presentation existence (`gslides readonly info`), authentic rendered thumbnails, zero fabricated outputs, clean workspace placement (`output/` only, nothing in `.agents/teamwork/`), and genuine visual/factual integrity.
5. **Gate**: Strict AND across Worker + 2 Reviewers (`APPROVE`) + 2 Challengers (`APPROVE`) + Forensic Auditor (`CLEAN`).
