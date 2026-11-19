# Specification Miner Handoff — Quality & Moat Screener (v7.19) Google Slides Deck

## 1. Observation

### 1.1 Authoritative Sources Read & Verified
1. **`.agents/teamwork/ORIGINAL_REQUEST.md`** (lines 1–93): Defines R1 (Direct Google Slides Creation via `gslides` for connected account `schultz.janis@gmail.com`, outputs inside repo `output/`), R2 (complete v7.19 coverage across Executive Summary/Universe/5 Philosophies, Pre-Screen Layer, Part I 6 Gates + Attrition + Two-Step CAP Engine, Part II Explicit Mauboussin-Fade DCF + 3-Price Anchor + Bellman 5Y IRR + Reverse-DCF, Part III Cohorts + 6 Live Case Studies), R3 (programmatic + independent visual verification against an explicit rubric), and an initial 12-slide draft.
2. **`/Users/janis.schultz/.gemini/config/plugins/gslides/skills/gslides/SKILL.md`** (lines 1–428): Documents `gslides` CLI (`mutate create`, `mutate batch`, `mutate insert-image-from-file`, `readonly read --json`, `readonly export-thumbnail`, `readonly export`), single-batch placeholder IDs, `add-line` connectors, `set-notes`, and `updateTableColumnProperties`.
3. **`/Users/janis.schultz/.gemini/config/plugins/gslides/skills/gslides/references/styling.md`** (lines 1–580): Mandates `720 × 405 pt` canvas (16:9), minimum `30 pt` margins, `14–16 pt` left-aligned body text, `36–44 pt` bold titles (at least `2×` body size), max 5–6 bullets per slide, one core idea per slide, dark→light→dark sandwich pattern, explicit `--color` and `--font_family` on every text element, visual element on every slide, varied layouts across 10 templates, WCAG `>= 4.5:1` body contrast, zero red-green colorblind pitfalls, and **no accent lines under titles** (line 572).
4. **Repository Specs & Live Code Verification**:
   - `README.md` (lines 1–241), `QUALITATIVE_EVALUATION_SPEC.md` (lines 1–345), `QUANTITATIVE_EVALUATION_SPEC.md` (lines 1–234), `screener/gates.py` (lines 170–620).
   - Live Python check via `screener.dashboard.collect_screener_data(universe_keys())` confirmed 100% parity with `ORIGINAL_REQUEST.md`:
     - **Universe**: `1,175` total (`us` `515`, `eu` `602`, `ca` `58`).
     - **Attrition**: Start `1,175` → G1 `−30` (`1,145`) → G2 `−156` (`989`) → G3 `−506` (`483`) → G4 `−108` (`375`) → G5 `−16` (`359`) → G6 `−134` → **`225` Prime Grade (`19.1%`)**.
     - **Prime Grade Breakdown**: `110 US | 104 EU | 11 CA`; `220 Valued` (median excess IRR `-11.7pp` vs hurdle); Moats: `Toll booth & switching costs` (`124`), `Irreplaceable infrastructure & intangibles` (`71`), `Scale economies shared` (`17`), `R&D & innovation leadership` (`13`); CAP: `15Y` (`51`), `20Y` (`114`), `25Y` (`57`), `30Y` (`3`).
     - **Cohorts**: `Prime Grade` `225`, `Growth at ~0g` `25`, `Quality Grade` `443`.
     - **Live Case Studies (exact live output)**:
       - `MSFT`: `Quality pass`, G3 `(2,2,0,1)` Toll booth, G4 `(0,1,0,0,1)`, `CAP_init 30Y → CAP 25Y` (`-5Y`), `G5=1, G6=Y`, Price `$506.24`, Fair Value `$547.10` (`-7.5%`), 0g Terminal `$277.08`, Cur P/E `28.2×`, Fair P/E `30.5×`, `g₀ = 11.5%`, `RONIC₀ = 50.0%`, `g_market = 10.5%` (`g_gap = +1.0pp`), `CAP_imp = 22.0Y`, `5Y IRR = +10.3%`.
       - `COST`: `Quality pass`, G3 `(1,1,2,0)` Scale economies shared, G4 `(0,0,0,0,0)`, `CAP 30Y`, `G5=2, G6=Y`, Price `$1,110.08`, Fair Value `$600.33` (`+84.9%`), 0g Terminal `$320.87`, Cur P/E `53.5×`, Fair P/E `28.9×`, `g₀ = 10.0%`, `RONIC₀ = 43.1%`, `g_market = 16.5%`, `5Y IRR = -4.6%`.
       - `ASML.NL`: `Quality pass`, G3 `(2,2,0,2)` R&D & innovation leadership, G4 `(0,0,1,1,0)`, `CAP_init 30Y → CAP 25Y` (`-5Y`), `G5=2, G6=Y`, Price `€1,236.80`, Fair Value `€806.65` (`+53.3%`), 0g Terminal `€383.74`, Cur P/E `49.8×`, Fair P/E `32.5×`, `g₀ = 12.3%`, `RONIC₀ = 50.0%`, `g_market = 17.5%`, `5Y IRR = -0.7%`.
       - `SPGI`: `Quality pass`, G3 `(2,2,0,0)` Toll booth, G4 `(0,0,0,0,0)`, `CAP 30Y`, `G5=1, G6=Y`, Price `$452.35`, Fair Value `$362.36` (`+24.8%`), 0g Terminal `$264.91`, Cur P/E `25.4×`, Fair P/E `20.3×`, `g₀ = 7.0%`, `RONIC₀ = 24.4%`, `g_market = 9.9%`, `5Y IRR = +3.5%`.
       - `WM`: `Quality pass`, G3 `(1,2,0,0)` Irreplaceable infra, G4 `(0,0,0,0,0)`, `CAP 25Y`, `G5=1, G6=Y`, Price `$242.69`, Fair Value `$97.52` (`+148.9%`), 0g Terminal `$87.38`, Cur P/E `36.0×`, Fair P/E `14.4×`, `g₀ = 5.6%`, `RONIC₀ = 12.3%`, `g_market = 23.5%`, `5Y IRR = -10.5%`.
       - `CRM`: `Rejected – G4 Runway (<15Y)`, G3 `(2,0,0,0)` Toll booth, G4 `(1,1,1,0,2)` (`4_sub=2` AI Fatal Flaw), `CAP_init 20Y → CAP 5Y`, diagnostic `G5=0, G6=Y`, Price `$194.52`, Fair Value `$164.31`, Cur P/E `17.8×`, Fair P/E `15.1×`, `g₀ = 11.6%`, `g_market = 26.6%`, `5Y IRR = +4.7%`.
5. **Local Graphics Runtime Observation**:
   - Default `/usr/bin/python3` does **not** have `matplotlib`, `PIL`, `numpy`, `cairosvg`, or `plotly` installed, and `node`/`playwright` are absent. However, **`/usr/bin/swiftc` (macOS CoreGraphics)**, `/usr/bin/qlmanage`, `/usr/bin/sips`, and **native Google Slides vector shapes/lines/tables (`gslides mutate batch`)** are all available offline with zero dependencies.

---

## 2. Logic Chain

### 2.1 Optimal Slide Count & Pacing Evaluation (12 vs. 16 Slides)
Fitting all of R2 onto the 12-slide draft in `ORIGINAL_REQUEST.md` breaks `styling.md` readability rules on **four** slides:
1. **Draft Slide 2** merges the `1,175`-stock 3-region universe, all 5 philosophical foundations, AND the 2-part Pre-Screen layer (`in_market`, `g6_default`), plus Stage 1/Stage 2 waterfall rules—far exceeding the 5–6 bullet cap on a `720×405pt` canvas. → **Split into Slide 2 (Universe & 5 Philosophies) + Slide 3 (Pre-Screen Layer & Two-Stage Waterfall).**
2. **Draft Slide 4** merges Gate 1, Gate 2 (+ `2r`), AND Gate 3's 4 moat archetypes (`124 / 71 / 17 / 13`) + `3b` ROIC/ROIIC/pricing hurdles. → **Split into Slide 5 (Gates 1 & 2) + Slide 6 (Gate 3: 4 Moat Archetypes & Proof of Moat).**
3. **Draft Slide 8** merges Step 2 (`RONIC₀` across 3 capital-base regimes + M&A harmonic blend) AND Step 3 (4-pillar statistical `g₀` with `S_t`, Theil–Sen, 3-driver triangulation, Empirical Bayes `τ₀=6%`, `tanh` cap, buyback clamp). → **Split into Slide 10 (Step 2: `RONIC₀` & M&A Blend) + Slide 11 (Step 3: 4-Pillar Statistical `g₀`).**
4. **Draft Slide 12** packs all 6 live case studies (`MSFT`, `COST`, `ASML.NL`, `SPGI`, `WM`, `CRM`)—with both Gate 3/4 CAP details and DCF valuation metrics—plus the concluding takeaway for the user's brother onto one slide. → **Split into Slide 15 (Live Case Studies: Valuation Map + 6-Ticker Scorecard) + Slide 16 (Closing: Brother's 4-Step Decision Playbook).**

**Result:** **16 slides** (within the 14–16 ultra-readable target). Every slide presents **one clear idea**, holds `<= 6` concise bullets at `>= 14 pt` body text, reserves generous `>= 30 pt` whitespace, pairs text with a purposeful visual element, and alternates strictly along a **Dark → Light → Dark** sandwich cadence.

---

## 3. Complete Visual Design System (`720 × 405 pt` Canvas)

### 3.1 Color Palette ("Midnight Executive & Ice Slate" — WCAG AA & Colorblind-Safe)
| Role | Hex | Usage | Contrast vs. Canvas |
| :--- | :--- | :--- | :--- |
| **Dark Background** | `#1E2761` | Title, hero chart, section transition & closing slides | — |
| **Dark Card Surface** | `#283582` | Elevated cards / callout panels on Dark slides | `1.28:1` surface lift |
| **Dark Card Header** | `#34439E` | Card title bands on Dark slides | `1.65:1` surface lift |
| **Light Background** | `#F5F7FA` | Content, framework, and analytical slides | — |
| **Light Card Surface** | `#FFFFFF` | Cards/tables on Light slides (outline `#D5DFED`, `1pt`) | Crisp elevation |
| **Light Tint Surface** | `#E8EEF7` | Secondary/comparison boxes on Light slides | Subtle contrast |
| **Primary Text (Dark)** | `#FFFFFF` | Titles & key callouts on `#1E2761` | **`13.5:1`** ✅ |
| **Body Text (Dark)** | `#CADCFC` | Bullets & labels on `#1E2761` | **`8.2:1`** ✅ |
| **Muted Caption (Dark)** | `#A8BCE8` | Footers, slide numbers, source tags on `#1E2761` | **`5.8:1`** ✅ |
| **Title Text (Light)** | `#1E2761` | Slide titles & card headers on `#F5F7FA` / `#FFFFFF` | **`12.6:1`** ✅ |
| **Body Text (Light)** | `#1F2937` | Body bullets & table cells on `#F5F7FA` / `#FFFFFF` | **`13.8:1`** ✅ |
| **Muted Caption (Light)** | `#4B5563` | Footers, slide numbers, captions on `#F5F7FA` | **`7.1:1`** ✅ |
| **Positive / Pass (Dark)** | `#2DD4BF` | Bright Teal for `PASS`, `Prime`, `IRR > r`, positive highlights | **`9.5:1`** ✅ |
| **Positive / Pass (Light)** | `#0F766E` | Deep Teal for text/badges (`#0D9488` for large bars/shapes) | **`5.1:1`** ✅ (`3.6:1` large) |
| **Highlight / Warn (Dark)** | `#FBBF24` | Warm Amber for `CAP`, `Growth at ~0g`, key thresholds | **`10.2:1`** ✅ |
| **Highlight / Warn (Light)** | `#B45309` | Deep Amber for text (`#D97706` for large callout borders/bars) | **`4.8:1`** ✅ |
| **Reject / Overvalued (Dark)** | `#FB923C` | Warm Coral-Orange for `REJECT` / `Fatal Flaw` / premium bars | **`7.9:1`** ✅ |
| **Reject / Overvalued (Light)** | `#C2410C` | Deep Burnt-Coral for `REJECT` / overvalued / negative IRR text | **`5.2:1`** ✅ |

**Colorblind Safety Rule:** Zero pure Red (`#FF0000`) + Green (`#00FF00`) pairings. Use **Teal (`#0F766E` / `#2DD4BF`) vs. Coral-Orange (`#C2410C` / `#FB923C`) vs. Amber (`#B45309` / `#FBBF24`)**, and **always reinforce with text/glyphs** (`[PASS]`, `[REJECT]`, `[⚠]`, `▲`, `▼`).

### 3.2 Typography Pairing (2 Fonts Max)
- **Header Font:** **`Montserrat`** (Bold) — Slide titles, section headers, big hero stats, card headers.
- **Body & Table Font:** **`Roboto`** (Regular / Bold for inline emphasis) — Body bullets, table cells, formulas, labels, footers.
- **Size Hierarchy (`>= 2×` Title-to-Body Rule):**
  - Hero Title (Slide 1): `38–42 pt` Bold | Big Stat Callouts: `48–72 pt` Bold
  - Content Slide Title: `28–32 pt` Bold (guarantees 1-line fit inside `width = 660 pt` and `>= 2.0×` over `14 pt` body!)
  - Card / Section Header: `16–18 pt` Bold
  - Body / Bullets / Table Body: **`14 pt` Regular** (minimum `14 pt` for all body prose; compact 6-row data tables `11.5–12.5 pt` only inside table cells where `14 pt` would wrap, or `12–13 pt` inside dense diagram badges; prose bullets strictly `>= 14 pt`)
  - Captions / Axis Labels / Footer: `10–11 pt` Regular (muted color)

### 3.3 Coordinate Grid & Visual Motif (`720 × 405 pt`)
- **Strict Safe Margin:** `x ∈ [30, 690]` (usable width `660 pt`), `y ∈ [30, 375]` (usable height `345 pt`). No text or content shape may extend outside `[30, 690] × [30, 375]` (only optional full-bleed background or `x=0, w=8` edge stripe is allowed as non-content decoration).
- **Consistent Zone Grid:**
  - **Kicker Pill / Section Tag:** `x=30, y=24` (or `y=30` to honor strict 30pt top margin: `y=30, h=18`, `10pt` bold uppercase pill e.g. `PART I · QUALITATIVE GATES`)
  - **Slide Title:** `x=30, y=50, w=660, h=38` (`28–30 pt` Montserrat Bold, **NO underline/accent line underneath!**)
  - **Main Content Area:** `x=30, y=96` to `y=352` (`height = 256 pt`) — `20 pt` horizontal gaps between columns (`320 + 20 + 320 = 660`, or 3 cards `206 + 21 + 206 + 21 + 206 = 660`, or 4 cards `153 + 16 + 153 + 16 + 153 + 16 + 153 = 660`).
  - **Footer / Page Motif:** `x=30, y=360, w=540, h=15` (framework source/takeaway, `10 pt` muted) + `x=590, y=360, w=100, h=15` (`02 / 16`, right-aligned, `10 pt` muted). Bottom edge at `375 pt` = exact `30 pt` margin from bottom!
- **Cohesive Visual Motif:** A slim `8 pt` left-edge vertical color accent bar (`x=0, y=0, w=8, h=405`, `#2DD4BF` on Dark slides, `#1E2761` on Light slides) + uppercase section kicker tag at `(30, 30)` + `01 / 16` page counter at `(590, 360)`.

---

## 4. Slide-by-Slide Blueprint (16 Slides)

### Slide 1 — Title & Core Premise
- **Background:** Dark (`#1E2761`) | **Layout:** #1 Title Slide (Full Bleed) + 3 Bottom Metric Pills
- **Purpose / Brother Takeaway:** Set the big-picture goal: filter ~1,200 global stocks down to ~225 elite compounders, then pay only a disciplined price.
- **Visual Element:** Clean full-bleed dark hero layout with `#2DD4BF` thin horizontal divider bar (`x=260, y=228, w=200, h=4`) and 3 rounded stat badges at bottom (`1,175 Global Stocks` → `225 Prime Grade` → `100% Deterministic DCF`).
- **Key Text:**
  - Kicker: `INVESTMENT FRAMEWORK WALKTHROUGH · v7.19`
  - Title (`38 pt` Bold `#FFFFFF`, centered): `Quality & Moat Screener`
  - Subtitle (`18 pt` `#CADCFC`, centered): `How to Find World-Class Compounders — and Never Overpay`
  - 3 Pill Callouts (`x=75, 275, 475`, `y=265`, `w=170, h=70`, bg `#283582`): `1,175` Global Universe | `6 Gates` Munger Elimination | `0` Analyst Overrides
- **Speaker Notes:** *"Here's the whole system in one sentence: first decide WHICH businesses are good enough to own for 20 years, and only THEN let strict accounting math tell you what price is fair."*

### Slide 2 — Global Universe & 5 Philosophical Foundations
- **Background:** Light (`#F5F7FA`) | **Layout:** #7 Split Left Region Bars + Right 5 Numbered Principles
- **Purpose / Brother Takeaway:** Show where the 1,175 stocks come from and the 5 investing giants behind the rules.
- **Visual Element:** Left side (`x=30..255`): 3 native horizontal stacked region cards showing `1,175` total (`EU: 602 STOXX 600 [51%]`, `US: 515 S&P 500 ∪ NDX-100 [44%]`, `CA: 58 S&P/TSX 60 [5%]`). Right side (`x=275..690`): 5 numbered principle rows (`①`–`⑤`) with Teal/Navy badges.
- **Key Content (<= 5 items):**
  - `① Munger Inversion:` Default stance is rejection; hunt fatal flaws sequentially.
  - `② Buffett Owner Earnings & Solvency:` Inflation-beating moats, cash earnings, no *"kindness of strangers"*.
  - `③ Sleep & Thorndike:` Scale economies shared with customers + rational per-share allocation.
  - `④ Mauboussin CAP & Fade:` Separate moat existence from 5–30Y runway duration & mean-reversion.
  - `⑤ Zero Analyst Overrides:` Qualitative Gates 1–6 (`screener/gates.py`) strictly separated from deterministic DCF.
- **Speaker Notes:** *"Most investors fall in love with a story and tweak DCF assumptions until the price looks cheap. This system bans overrides: judgment picks the business; pure math values it."*

### Slide 3 — Pre-Screen Layer & Two-Stage Waterfall Architecture
- **Background:** Light (`#F5F7FA`) | **Layout:** #5/#8 Top 2 Pre-Screen Cards + Bottom Two-Stage Waterfall Flow Diagram
- **Purpose / Brother Takeaway:** Explain the automatic geographic/sector rules before Gate 1, plus why early rejects stop while late rejects get scored for learning.
- **Visual Element:** Top (`y=98..198`): 2 side-by-side white cards (`in_market → Gate 2` and `g6_default → Gate 6`) with Coral warning tags. Bottom (`y=216..348`): Native flow diagram with `add-line` arrows showing **Stage 1 Early Stop (G1–G3)** vs. **Stage 2 Full Diagnostic Scorecard (G4–G6, 483 companies)** + `Blank Gate Rule = 0 unreviewed`.
- **Key Content:**
  - **`in_market` (→ Gate 2):** Western rule-of-law property rights (`US, CA, UK, CH, Nordics, W. Europe = Y`; `Greece, Poland = N` → auto-fail G2).
  - **`g6_default` (→ Gate 6):** Deposit Commercial Banks (`10–15×` leverage, duration mismatch) & Regulated Utilities (`6–8%` capped ROIC, perpetual capex dilution) default to `N` at G6.
  - **Blank Gate Rule:** Unreviewed (`blank`) gates never pass (`0` blank across all `1,175` companies).
  - **Stage 1 (G1–G3):** Fail stops immediately; G4–G6 left blank.
  - **Stage 2 (G4–G6):** All `483` G3-passers get full G4/G5/G6 scores even if rejected at G4 (`CAP < 15Y`) or G5 (`Score = 0`).
- **Speaker Notes:** *"Before a single financial ratio is checked, risky jurisdictions and structurally leveraged utilities/banks get flagged automatically. And once a firm proves it has a moat at Gate 3, we grade all remaining gates so nothing hides."*

### Slide 4 — Global Funnel Attrition Waterfall (`1,175 → 225 Prime Grade`)
- **Background:** Dark (`#1E2761`) | **Layout:** #4/#2 Hero Waterfall Chart + Key Insight Sidebar
- **Purpose / Brother Takeaway:** Make Charlie Munger's inversion visceral: 81% of the world's biggest companies fail before reaching Prime Grade.
- **Visual Element:** Left (`x=30..495, y=96..348`): **Custom high-DPI PNG Horizontal/Step Funnel Waterfall Chart** (`output/charts/funnel_waterfall.png` — or native proportional horizontal bars) plotting exact remaining counts and attrition deltas:
  - Start: `1,175` (100%)
  - Gate 1 (Simple): `−30 (−2.6%)` → `1,145`
  - Gate 2 (Essential/Habit): `−156 (−13.3%)` → `989`
  - Gate 3 (Moat & Pricing): `−506 (−43.1%)` → `483` [Amber highlight: biggest killer!]
  - Gate 4 (CAP ≥ 15Y): `−108 (−9.2%)` → `375`
  - Gate 5 (Management ≥ 1): `−16 (−1.4%)` → `359`
  - Gate 6 (Cash & Fortress B/S): `−134 (−11.4%)` → **`225 Prime Grade (19.1%)`** [Teal highlight]
  Right (`x=510..690, y=96..348`): 2 Dark Stat Callout cards (`19.1%` Survival Rate | `43.1%` Killed at Gate 3 alone).
- **Speaker Notes:** *"Look at the choke point: Gate 3 wipes out 506 companies—43% of the entire starting universe—because most big companies lack a real moat or pricing power above inflation."*

### Slide 5 — Stage 1 Filters: Gates 1 & 2 (Understandability & Essential Habits)
- **Background:** Light (`#F5F7FA`) | **Layout:** #5 Two-Column Comparison Cards (`PASS ✓` vs `REJECT ✗`)
- **Purpose / Brother Takeaway:** Plain-English intuition for the first two filters: "Do I understand it?" and "Will people still buy this in a recession without regulators shutting it down?"
- **Visual Element:** Two symmetrical vertical cards (`x=30..350` Gate 1, `x=370..690` Gate 2), each split into a Teal-accented **Pass Standard** upper half and a Coral-accented **Reject Standard** lower half with explicit `✓` / `✗` badges.
- **Key Content:**
  - **Gate 1 — Simple to Understand (`Y/N`, −30):**
    - `✓` Established multi-cycle history, transparent verifiable statements (incl. clean banks/insurers/holdcos).
    - `✗` Pre-profit/unproven models, opaque risks (prop trading, crypto treasuries, binary biotech).
  - **Gate 2 — Essential Western Need & Habits (`Y/N + 2r`, −156):**
    - `✓` Functional necessities + Buffett/Munger *"likely to spend"* daily rituals & Lindy luxury (`in_market = Y`).
    - `✗` Deferrable cyclicals (cruises, airlines, homebuilders), commodity explorers, pariah regimes, predatory/addictive models (tobacco, CFD betting); requires `2r` reason.
- **Speaker Notes:** *"Gate 2 isn't just bread and water—it includes everyday habits like coffee or Hershey's chocolate, plus Lindy luxury like Hermès. What fails is big-ticket items people postpone in a downturn, or businesses society tries to tax out of existence."*

### Slide 6 — Gate 3: The 4 Moat Archetypes & Empirical Proof (`3a` + `3b`)
- **Background:** Light (`#F5F7FA`) | **Layout:** #3 4-Column Archetype Cards + Bottom Empirical Hurdle Banner
- **Purpose / Brother Takeaway:** Explain the 4 exact ways a company protects profits—and why Gate 3b demands hard financial proof, not marketing claims.
- **Visual Element:** Top (`y=98..258`): 4 clean vertical cards (`w=153pt` each) showing Prime Grade counts & proportions:
  1. `Toll Booth & Switching` (`124 Prime | 55%` — e.g. `MSFT`, `SPGI`)
  2. `Irreplaceable Infra & Intangibles` (`71 Prime | 32%` — e.g. `WM`, `RMS.FR`)
  3. `Scale Economies Shared` (`17 Prime | 8%` — strictly Nick Sleep: `COST`, `PGR`)
  4. `R&D & Innovation Leadership` (`13 Prime | 6%` — e.g. `ASML.NL`)
  Bottom (`y=272..348`): Full-width `3b` Proof-of-Moat bar (`5Y Median GAAP ROIC ≥ 12%` OR `Tangible ≥ 15%` + `Incremental ROIIC ≥ 12%` + `Pricing Power ≥ Inflation`; scored `0/1/2` on `3_tb, 3_ia, 3_se, 3_rd`).
- **Speaker Notes:** *"Be careful with 'Scale Economies Shared': Walmart or Costco pass savings back to shoppers to grow the flywheel. Standard network-scale businesses go under Irreplaceable Infrastructure instead."*

### Slide 7 — Gate 4: Two-Step Deterministic CAP Engine (`CAP ≥ 15Y`)
- **Background:** Dark (`#1E2761`) | **Layout:** #8 Process Flow Diagram + Right Distribution Mini-Chart
- **Purpose / Brother Takeaway:** Show how moat strength (`Step 1`) and 5-force disruption stress-testing (`Step 2`) combine with **zero manual overrides** to set the Competitive Advantage Period (`5–30Y`).
- **Visual Element:**
  - Left/Top (`x=30..445, y=98..275`): Native 2-step deterministic diagram with connectors:
    - **Step 1 (`CAP_init`):** `(m_max, m_sum)` → `0Y (0)`, `15Y (1,1)`, `20Y (1,≥2 or 2,2)`, `25Y (2,3)`, `30Y (2,≥4)`.
    - **Step 2 (Porter's 5 Forces `0/1/2`):** `4_ent, 4_riv, 4_buy, 4_sup, 4_sub` tested vs. **5 Macrotrends** (AI, Demographics, Geopolitics, Energy, Inflation) + **Mauboussin Clock Speed** (presumptive `4_sub ≥ 1` for fast tech/pharma unless unbypassable).
    - **Formula Box:** Haircut `h(c1)`: `0→0Y`, `1–2→−5Y`, `3–4→−10Y`, `5→−15Y`; **Fatal-Flaw Cap** (`any Force = 2` → `CAP_final ≤ 10Y`, Reject).
  - Right (`x=460..690, y=98..275`): Native vertical/horizontal bar chart of **Prime Grade CAP Distribution**: `15Y: 51`, `20Y: 114`, `25Y: 57`, `30Y: 3` (`225` total).
  - Bottom (`x=30..690, y=288..348`): **3 Anti-Drift Rules** strip: (1) Peer Benchmarking, (2) UI Seat Layer (`2`) vs Proprietary Data/Statutory Engine (`1`), (3) Gate Orthogonality (no G5/G6 bleed into G4).
- **Speaker Notes:** *"Gate 4 separates 'how strong is the castle today?' from 'how fast are the barbarians evolving?' Even a 20Y moat drops straight to 5–10Y and fails if AI substitution scores a 2."*

### Slide 8 — Stage 2 Stewardship & Solvency Gates (Gates 5 & 6)
- **Background:** Light (`#F5F7FA`) | **Layout:** #2 Split Left 5-Vector List + Right 3-Pillar Solvency Cards
- **Purpose / Brother Takeaway:** Explain why great moats still fail if management burns cash on ego-M&A (Gate 5) or loads up on debt (Gate 6).
- **Visual Element:** Left (`x=30..345`): **Gate 5 (`0/1/2`, pass ≥ 1, −16)** — 5 Superinvestor Vector rows with author attributions (`Fisher/Buffett`, `Murphy/Thorndike`, `Bezos/Sleep`, `Product-Led`, `Wallenberg/Drucker`). Right (`x=365..690`): **Gate 6 (`Y/N` + `< 3` flags, −134)** — 3 stacked pillar cards:
  1. `Peak-to-Peak Owner EPS:` New high every business cycle (`p2p_ok`).
  2. `Cash Conversion ≥ 80%:` Multi-year Owner FCF ÷ GAAP NI ≥ 80%.
  3. `Peace-of-Mind B/S:` 3Y median Net Debt ÷ OE `≤ 4.0y`, EBIT ÷ Interest `> 5.0×` (contextual: formula-indexed infra & Solvency II `> 200%` insurers).
- **Speaker Notes:** *"134 companies with real moats and 15+ year runways still fail Gate 6—mostly because of debt, poor cash conversion, or shrinking cycle peaks. Only 225 survive to Prime Grade."*

### Slide 9 — Part II: Slump-Cannibal Doctrine & Sanitized Owner EPS
- **Background:** Dark (`#1E2761`) | **Layout:** #7/#4 Top Formula Strip + 4 Accounting Guard Cards + Bottom Reversion Decay Visual
- **Purpose / Brother Takeaway:** Introduce Part II (100% deterministic math, zero analyst overrides) and explain why accounting Net Income lies—and how Owner EPS fixes it.
- **Visual Element:**
  - Top banner (`x=30..690, y=96..145`): Monospace/highlighted **Owner EPS Formula**:
    `Owner EPS = (NI + max(0, min(clean_DA, max(0, OCF − NI)) − CapEx − 0.20 × AvgLease)) / Shares`
  - Middle 4 cards (`y=158..258`, `w=153pt` each): (1) **Cash-Flow Backing** (`OCF − NI` ceiling), (2) **`1.5×` Impairment Cap** (`clean_da`), (3) **`20%` IFRS-16 Lease Deduction** (US-GAAP exempt), (4) **Spike & Pre-IPO Stripping**.
  - Bottom (`y=270..348`): **Slump-Cannibal & Age-Weighted Mid-Cycle Reversion** bar/step visual: look through 1Y `sales_1y` slumps; if `cur_eps < peak`, blend weight decays `w = 50% (age ≤ 1y) → 33% (2y) → 17% (3y) → 0% (≥ 4y)`.
- **Speaker Notes:** *"Why 'Slump-Cannibal'? Because great companies buy back shares during temporary 1-year revenue slumps. And we never trust a 4-year-old stale earnings peak—its weight fades to zero."*

### Slide 10 — Capital Base & M&A-Matched `RONIC₀` (`≤ 50%`)
- **Background:** Light (`#F5F7FA`) | **Layout:** #6 Compact 3-Regime Table + Bottom Harmonic Blend Card
- **Purpose / Brother Takeaway:** Show how the model measures return on *new* invested capital (`RONIC₀`) fairly across asset-light software, banks/insurers, and serial acquirers.
- **Visual Element:**
  - Top (`x=30..690, y=98..235`): Styled 3-row **Native Table** (`4 columns`: Regime | Eligible Industries | Capital Return Formula | Why It Matters):
    1. `Tangible Operating ROIC` | Operating & Fee Financials | `NOPAT ÷ max(IC − GW − Intang, 1/3 IC)` | Strips legacy M&A goodwill distortion (`1/3 IC` floor).
    2. `5Y Median ROE` | BS Financials & `IC ≤ 0` Clearing (`≥ 2/5y`) | `5Y Consolidated ROE` (`r_fin = 10.25%` BS / `8.5%` clearing) | Customer cash/deposits make `IC` meaningless.
    3. `GAAP ROIC` | IFRIC-12 Concessions | `NOPAT ÷ IC_GAAP` | Concession intangibles *are* the physical asset.
  - Bottom (`x=30..690, y=248..348`): **M&A-Matched Harmonic Blend** visual card (`RONIC₀ ≤ 50%`): When goodwill-heavy (`r_tang > 1.25 × r_GAAP`), cash-funded M&A (`ma_reinvest`) blends `r_tang` & `r_GAAP` harmonically via `w = clip(ma_reinvest × r_GAAP / g₀, 0, 1)`; stock-funded deals already stripped by `S_t`.
- **Speaker Notes:** *"If a company grows by buying competitors with cash every year, pretending its capital return is 60% tangible ROIC is cheating. The harmonic blend forces serial cash acquirers to carry their M&A price tag."*

### Slide 11 — 4-Pillar Statistical Organic Growth Engine (`g₀ ≤ 13%`)
- **Background:** Light (`#F5F7FA`) | **Layout:** #8 4-Step Connected Pipeline (`① → ② → ③ → ④`) + Buyback Separation Box
- **Purpose / Brother Takeaway:** Explain how the screener forecasts future organic growth statistically from 10 years of statements—without relying on Wall Street hype or COVID rebound flukes.
- **Visual Element:** Top (`y=102..262`): 4 connected rounded cards (`w=150pt`, `gap=20pt`, connected by Teal arrows `add-line`):
  - `① Dilution Index S_t`: Penalizes SBC & stock-M&A share growth in exact year (`10Y` window).
  - `② Cycle Theil–Sen`: Non-parametric slopes (`Δt ≥ 5y`), outputs median `P50` & conservative `P25`.
  - `③ 3-Driver Triangulation`: Balances `Revenue`, `NOPAT` & `Owner Earnings` (+ `6%` refranchising guard).
  - `④ EB Shrinkage & tanh`: Shrinks (`τ₀ = 6%`) toward `3.0%` inflation + smooth `tanh` cap at `13.0%`.
  Bottom (`y=278..348`): Wide slate card highlighting **Buyback Discipline**: `bb_eff` clamped to `[-3.0%, +3.5%]` and kept strictly *out* of firm-level DCF (`g₀` is pure organic growth).
- **Speaker Notes:** *"Notice two clever tricks: Theil–Sen ignores crazy 1-year COVID bounce outliers, and Empirical Bayes pulls noisy growth estimates gently back toward 3% global nominal growth."*

### Slide 12 — Explicit N-Year Mauboussin-Fade DCF (`r = 8.50% / 10.25%`)
- **Background:** Dark (`#1E2761`) | **Layout:** #2 Split Left Custom Fade Chart + Right Equations & Invariance Card
- **Purpose / Brother Takeaway:** Visually demystify the DCF: growth and returns don't stay sky-high forever—they fade smoothly over the company's Gate 4 CAP (`N` years).
- **Visual Element:** Left (`x=30..395, y=96..348`): **Custom High-DPI PNG Chart (`output/charts/mauboussin_fade_dcf.png`)** showing dual-line linear fade over `t = 1..25Y` (`g_t`: `11.5% → 3.0%`; `RONIC_t`: `50% → 20%`) with shaded Stage 1 FCF area (`E_t(1 − g_t/RONIC_t)`) and Stage 2 Terminal Perpetuity marker at `t = N`.
  Right (`x=415..690, y=96..348`): 3 crisp stacked Dark cards:
  - **Conservative Base:** `E₁ = 1.0 × Active EPS`; `r = 8.50%` (operating) / `10.25%` (BS financials).
  - **Stage 1 & Stage 2 Fade:** Linear fade over `N = CAP` years to `g_term ≤ 3.0%` & `RONIC_term = min(RONIC₀, 20%, r + 0.5(RONIC₀−r))` + McKinsey terminal value.
  - **Miller–Modigliani Invariance:** Exact math guarantee: if `RONIC = r`, `Fair P/E ≡ 1/r` regardless of growth `g₀` or `N`.
- **Speaker Notes:** *"When a business only earns its cost of capital (8.5%), growing faster creates zero extra value—Fair P/E stays locked at 1/8.5% = 11.76×. Only returns ABOVE the hurdle rate create value."*

### Slide 13 — 3-Price Anchor, Bellman 5Y IRR, Reverse-DCF & Circuit Breakers
- **Background:** Light (`#F5F7FA`) | **Layout:** #3 / #7 2×2 Structured Quadrant Cards
- **Purpose / Brother Takeaway:** Translate Fair P/E into everyday investing decisions: "What is the price today vs. fair value vs. zero-growth floor, and what annual return (`IRR`) does it imply?"
- **Visual Element:** 4 crisp white cards in a 2×2 grid (`w=320pt, h=122pt` each, `gap=20pt`):
  1. **3-Price Anchor:** `Current Price` vs. `DCF Fair Value` vs. `0g Terminal Floor` (3% inflation, max `15.45×` P/E operating / `10.89×` financials).
  2. **Bellman-Consistent 5Y IRR:** Exact `FCF₁..FCF₅` + Year-5 DCF continuation `V₅` → `IRR == r` (`8.50%`/`10.25%`) *if and only if* `Price == Fair Value`.
  3. **Reverse-DCF (`g_market`):** Scans `[-20%, +50%]` grid + bisection to find growth priced into today's quote, plus `Market-Implied CAP`.
  4. **Special Physics & Circuit Breakers:** `1.0× BVPS` MTM HoldCo anchor; `No value` (`Fair Value ≤ 0`); `No data` (`BLOCKING_AUTO_NOTES` e.g. stale/currency/share-glitch/non-cash marks).
- **Speaker Notes:** *"Instead of arguing what Microsoft SHOULD grow at, Reverse-DCF flips the question: 'At today's stock price, what growth is Wall Street already assuming?'"*

### Slide 14 — Part III: Actionable Decision Cohorts (`Prime`, `Growth at ~0g`, `Quality`)
- **Background:** Dark (`#1E2761`) | **Layout:** #4 + #3 Three Big-Stat Cohort Cards
- **Purpose / Brother Takeaway:** Show how the cockpit organizes surviving stocks into 3 practical shopping lists depending on whether you want pure fortress quality or contrarian bargains.
- **Visual Element:** 3 full-height Dark Elevated Cards (`x=30, 257, 484`, `w=206pt, h=250pt`), each topped by a `48 pt` Bold hero stat:
  1. **`225` · 🛡️ Prime Grade** (`#2DD4BF` Teal): Clears all 6 Munger gates (`< 3` G6 numeric flags). Global split: **`110 US | 104 EU | 11 CA`** (`220 Valued`).
  2. **`25` · 💎 Growth at ~0g** (`#FBBF24` Amber): `Quality Grade`, `Valued`, `Model g₀ ≥ 5.0%` yet `Mkt Implied g < 5.0%` (`9` Prime, `6` G6-fail, `10` CAP `5–10Y` e.g. `PGR`, `FICO`, `ADBE`).
  3. **`443` · 🏰 Quality Grade** (`#CADCFC` Ice): Structural moat cohort passing G1, G2, G3 (`< 3` G6 flags) — full watchlist for cycle pullbacks.
- **Speaker Notes:** *"Prime Grade is the 225-stock A-list. 'Growth at ~0g' is the bargain hunter's radar: proven moat companies growing ≥5% organically that Mr. Market is pricing as if growth were dead."*

### Slide 15 — Live Case Studies: Quality vs. Price & The AI Fatal Flaw
- **Background:** Light (`#F5F7FA`) | **Layout:** #6 + #2 Compact 6-Row Table (Left) + Custom Valuation Chart (Right)
- **Purpose / Brother Takeaway:** Prove with 6 household names that **a great company ≠ a cheap stock** (`COST`, `ASML.NL`, `WM`), while `CRM` shows Gate 4 catching AI seat-risk early, and `MSFT` hits the rare sweet spot.
- **Visual Element:**
  - Left (`x=30..415, y=96..348`): Crisp 6-row **Native Table** (`Ticker | CAP | Cur vs Fair P/E | g₀ vs g_mkt | 5Y IRR | Verdict`):
    - **`MSFT`** | `25Y` | `28.2× vs 30.5×` | `11.5% vs 10.5%` | **`+10.3%`** | **`Prime (Discount −7.5%)`**
    - **`SPGI`** | `30Y` | `25.4× vs 20.3×` | `7.0% vs 9.9%` | `+3.5%` | `Prime (+24.8% Prem)`
    - **`ASML.NL`** | `25Y` | `49.8× vs 32.5×` | `12.3% vs 17.5%` | `−0.7%` | `Prime (+53.3% Prem)`
    - **`COST`** | `30Y` | `53.5× vs 28.9×` | `10.0% vs 16.5%` | `−4.6%` | `Prime (+84.9% Prem)`
    - **`WM`** | `25Y` | `36.0× vs 14.4×` | `5.6% vs 23.5%` | `−10.5%` | `Prime (+148.9% Prem)`
    - **`CRM`** | **`5Y`** | `17.8× vs 15.1×` | `11.6% vs 26.6%` | `Reject` | **`Rejected @ G4 (4_sub=2)`**
  - Right (`x=430..690, y=96..348`): **Custom High-DPI PNG Chart (`output/charts/case_study_irr_pe.png`)** comparing **5Y Expected IRR vs. 8.5% Hurdle** (or **Current P/E vs. Fair P/E** dumbbells) across the 6 tickers so the contrast between `MSFT (+10.3%)` and `WM (−10.5%)` pops visually!
- **Speaker Notes:** *"Waste Management (WM) is an incredible landfill moat—25Y CAP—but at 36× earnings for a 12% ROIC business, the market is pricing in 23.5% growth, giving a −10.5% 5Y IRR. Meanwhile Salesforce looks cheap at 17.8× P/E until Gate 4 flags AI seat-compression as a fatal flaw."*

### Slide 16 — Closing: Brother's 4-Step Decision Playbook
- **Background:** Dark (`#1E2761`) | **Layout:** #8/#10 4-Step Playbook Cards + Closing Quote Banner
- **Purpose / Brother Takeaway:** Leave the user's brother with a memorable, actionable 4-step workflow for reading any company dossier in `output/screener.html`.
- **Visual Element:** Top (`y=98..258`): 4 horizontal numbered step cards (`① Screen First`, `② Check g_market vs g₀`, `③ Anchor to 3 Prices`, `④ Demand IRR > Hurdle`), followed by a centered Munger-inspired closing takeaway banner (`y=280..345`) with `#2DD4BF` thin top/bottom accent divider.
- **Key Content:**
  - `① Start in Prime Grade (225) or Growth at ~0g (25)` — never override a failed gate.
  - `② Invert Expectations:` Compare `Model g₀` vs. `Mkt Implied g` (`g_gap > 0` = tailwind).
  - `③ Demand Price Discipline:` Compare `Price` vs. `Fair Value` & `0g Terminal Floor`.
  - `④ Require Margin of Safety:` Only buy when `Bellman 5Y IRR > 8.50%` (`10.25%` financials).
- **Speaker Notes:** *"That's the entire v7.19 Screener. Don't hunt for hot tips—wait patiently inside the 225 Prime Grade or 25 Growth-at-0g names until Mr. Market hands you a double-digit 5-year IRR."*

---

## 5. Custom Chart Specifications (`output/charts/`)

Because `matplotlib` is absent from `/usr/bin/python3`, the builder should generate the **3 data-intensive charts** using a clean offline **`swift` CoreGraphics PNG script** (rendered at `2×` Retina resolution e.g. `1400×840 px` with anti-aliased fonts, exact hex palette, explicit data labels, and transparent or slide-matched backgrounds) and embed via `gslides mutate insert-image-from-file` — OR install `matplotlib` inside an isolated temporary venv if preferred. Every chart must reside in `output/charts/`:

1. **`output/charts/funnel_waterfall.png` (Slide 4 — `465 × 252 pt` slot → `1395 × 756 px` @ 3×):**
   - Horizontal funnel/attrition bar chart on `#1E2761` background: 7 rows (`Start 1,175`, `G1 Simple 1,145 (−30)`, `G2 Habits 989 (−156)`, `G3 Moat 483 (−506)`, `G4 CAP≥15Y 375 (−108)`, `G5 Mgmt 359 (−16)`, `G6 Cash/BS 225 (−134)`).
   - Remaining bar in `#5B7CFA` / `#CADCFC`; dropped delta segment in `#FB923C` (Coral-Orange); G3 highlighted in `#FBBF24` (Amber); final `225 Prime Grade (19.1%)` bar in `#2DD4BF` (Teal). Direct white data labels (`>= 11 pt` equivalent) on every bar.
2. **`output/charts/mauboussin_fade_dcf.png` (Slide 12 — `365 × 252 pt` slot → `1095 × 756 px` @ 3×):**
   - Dual-series explicit fade trajectory (`t = 1..25Y` illustrative `MSFT`-like `25Y` CAP) on `#283582` panel:
     - Series A (`#2DD4BF` Teal solid line): `g_t` fading linearly from `11.5%` at `t=1` to `3.0%` at `t=25`, then flat `3.0%` Stage 2 perpetuity (`t=25..30` dashed).
     - Series B (`#FBBF24` Amber solid line): `RONIC_t` fading linearly from `50.0%` at `t=1` to `20.0%` at `t=25`, with horizontal dashed hurdle line `r = 8.50%` (`#CADCFC`).
     - Vertical dashed line at `t = N = 25Y` separating `Stage 1: Explicit Fade` from `Stage 2: Terminal Perpetuity`. Clear legend, axis labels, zero overlapping text.
3. **`output/charts/case_study_irr_pe.png` (Slide 15 — `260 × 252 pt` slot → `780 × 756 px` @ 3×):**
   - Clean horizontal bar chart on `#FFFFFF` card background plotting **Bellman 5Y Expected IRR (%)** for the 5 Prime Grade tickers + `CRM` (annotated `[G4 Reject: 5Y CAP]`):
     - `MSFT`: **`+10.3%`** (`#0D9488` Teal, clears `8.50%` vertical dashed hurdle line!)
     - `SPGI`: `+3.5%` (`#64748B` Slate)
     - `ASML.NL`: `−0.7%` (`#C2410C` Coral)
     - `COST`: `−4.6%` (`#C2410C` Coral)
     - `WM`: `−10.5%` (`#C2410C` Coral)
     - `CRM`: `+4.7% (G4 Reject)` (`#D97706` Amber hatched/outlined + `[G4 FAIL]` tag)
   - Vertical dashed benchmark line at `r = 8.50%` labeled `8.50% Hurdle`. Direct value labels outside bar ends.

---

## 6. Explicit Visual & Factual Verification Rubric (For Reviewers & Challengers)

### 6.1 Section A — Programmatic Structural Completeness (`gslides` CLI Read-Only Audit)
Run:
- `gslides readonly info <PRES_ID> --json`
- `gslides readonly read <PRES_ID> --json`
- `gslides readonly list-slides <PRES_ID> --json`
- `gslides readonly get-notes <PRES_ID> <SLIDE_ID>` for every slide

| ID | Check | Pass Criteria |
| :--- | :--- | :--- |
| **S-1** | Slide Count & Order | Exactly **16 slides** matching Blueprint Slides 1–16 in sequential order. |
| **S-2** | Zero Default Placeholders | Default `i0` / `i1` elements from `mutate create` removed; zero `"Title"`, `"Subtitle"`, `"Click to add"`, or `TBD` strings anywhere in textboxes or tables. |
| **S-3** | Explicit Colors & Fonts | `100%` of textboxes and populated table cells specify explicit `foregroundColor` (no accidental default black on dark `#1E2761`) and explicit `fontFamily` (`Montserrat` or `Roboto` only). |
| **S-4** | Speaker Notes Completeness | `16 / 16` slides have non-empty, tailored plain-English speaker notes (`>= 15 words` each). |
| **S-5** | Local Asset Hygiene | All generated PNG charts & exported `.pptx`/`.pdf`/thumbnails reside inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/output/` (never inside `.agents/teamwork/`). |

### 6.2 Section B — Visual & Layout Hygiene (`export-thumbnail` Inspection on 16/16 Slides)
Inspect all 16 rendered PNG thumbnails (`gslides readonly export-thumbnail <PRES_ID> output/verify/slide_XX.png --slide <SLIDE_ID>`):

| ID | Check | Pass Criteria |
| :--- | :--- | :--- |
| **V-1** | Zero Overlapping Shapes/Text | No textbox, shape, connector, table, or embedded PNG collides with or obscures another element's text. |
| **V-2** | Zero Clipped / Overflowing Text | No text extends past its bounding box, wraps unexpectedly onto an adjacent element, or truncates at card/table edges. |
| **V-3** | Margin Discipline (`>= 30 pt`) | All textboxes, cards, tables, and charts satisfy `x >= 30`, `x + width <= 690`, `y >= 30`, `y + height <= 375` on the `720 × 405 pt` canvas. |
| **V-4** | Font Hierarchy & Legibility | Content slide titles `>= 28 pt` Bold (`>= 2.0×` body text); body bullets `>= 14 pt`; compact table cells `>= 11.5 pt`; captions `>= 10 pt`; **zero accent underlines directly beneath slide titles** (`styling.md` line 572). |
| **V-5** | Contrast & Colorblind Safety | Body text contrast `>= 4.5:1` (`>= 3.0:1` large/bold); zero red-green pairs; Teal/Coral/Amber distinctions reinforced with `✓`/`✗`/`⚠` or explicit text tags. |
| **V-6** | Sandwich Rhythm & Layout Variety | Dark→Light→Dark pattern (`S1 D, S2-3 L, S4 D, S5-6 L, S7 D, S8 L, S9 D, S10-11 L, S12 D, S13 L, S14 D, S15 L, S16 D`); at least 5 distinct layout structures; every slide has a purposeful visual element; max 5–6 bullets per card/list. |
| **V-7** | Chart & Table Quality | All 3 PNG charts in `output/charts/` render sharply without clipping, overlap, or stretch distortion; tables have styled header rows and `<= 6` data rows. |

### 6.3 Section C — 100% Factual Parity Checklist (Quality & Moat Screener v7.19)
Reviewer and Challenger must verify **every** bulleted fact appears accurately with **zero discrepancies**:
- [ ] **Universe & Philosophy:** `1,175` companies (`us` `515` Nasdaq-100 ∪ S&P 500, `eu` `602` STOXX Europe 600, `ca` `58` S&P/TSX 60); all 5 foundations (Munger Inversion, Buffett Owner Earnings/Solvency, Nick Sleep Scale Economies Shared & Thorndike *Outsiders*, Mauboussin CAP & Fade, Zero Analyst Overrides / Quality-Valuation Separation).
- [ ] **Pre-Screen Layer:** `in_market` feeds Gate 2 (`Y` Western rule-of-law; `N` e.g. Greece, Poland → auto-fail G2); `g6_default` feeds Gate 6 (Deposit-Taking Commercial Banks & Regulated Utilities default to `N`).
- [ ] **Waterfall & Attrition:** Blank Gate Rule (`0` blank across `1,175`); Stage 1 Early Stop (`G1–G3`); Stage 2 Full Diagnostic Scorecard (`G4–G6` scored for all `483` G3-passers); Exact attrition: `1,175 → 1,145 (−30, −2.6%) → 989 (−156, −13.3%) → 483 (−506, −43.1%) → 375 (−108, −9.2%) → 359 (−16, −1.4%) → 225 Prime Grade (−134, −11.4%, 19.1%)`.
- [ ] **Gates 1–3:** G1 (`Y/N` circle of competence/verifiability); G2 (`Y/N + 2r` *"likely to spend"* standard, functional needs + daily habits/Lindy luxury vs cyclicals/commodities/pariah/predatory); G3 (`3_tb, 3_ia, 3_se, 3_rd` scored `0/1/2` + `3a` + `3b`); 4 Archetypes (`Toll booth 124`, `Irreplaceable infra 71`, `Scale economies shared 17` strictly Nick Sleep, `R&D 13`); `3b` (`5Y Median GAAP ROIC ≥ 12%` or `Tangible ≥ 15%`, `ROIIC ≥ 12%`, `Pricing ≥ Inflation`).
- [ ] **Gate 4 CAP Engine:** Step 1 `CAP_init` (`0Y`, `15Y [1,1]`, `20Y [1,≥2 or 2,2]`, `25Y [2,3]`, `30Y [2,≥4]`); Step 2 Porter's 5 Forces (`4_ent, 4_riv, 4_buy, 4_sup, 4_sub`) × 5 Macrotrends & Clock Speed (`4_sub ≥ 1` presumptive fast tech/pharma unless unbypassable); Haircut `h(c1)` (`0→0Y, 1–2→−5Y, 3–4→−10Y, 5→−15Y`); Fatal-Flaw Cap (`any Force=2 → CAP ≤ 10Y`, Reject); Prime CAP dist (`51 @ 15Y, 114 @ 20Y, 57 @ 25Y, 3 @ 30Y`); 3 Anti-Drift Rules (Peer Benchmarking, UI Seat `2` vs Proprietary Data/Statutory `1`, Gate Orthogonality).
- [ ] **Gates 5–6:** G5 (`0/1/2`, pass `≥ 1`, 5 Superinvestor vectors); G6 (`Y/N` + `< 3` numeric flags; Peak-to-Peak Owner EPS, Multi-year Owner FCF ÷ GAAP NI `≥ 80%`, Net Debt ÷ OE `≤ 4.0y`, EBIT ÷ Interest `> 5.0×`, contextual infra & Solvency II `> 200%` insurers).
- [ ] **Part II Quant Steps 1–5:** Slump-Cannibal Doctrine (zero overrides); Owner EPS formula (`OCF − NI` ceiling, `1.5×` impairment cap, `20%` IFRS-16 lease deduction w/ US-GAAP exempt, spike/pre-IPO strip, Age-Weighted Reversion `50% → 0%` over 4y); `RONIC₀ ≤ 50%` (Tangible w/ `1/3 IC` floor, 5Y ROE for BS Fin & `IC ≤ 0` in `≥ 2/5y`, GAAP ROIC concessions, Harmonic M&A blend when `r_tang > 1.25 × r_GAAP`); 4-Pillar `g₀ ≤ 13%` (`S_t`, Theil–Sen `Δt ≥ 5y` `P25`/`P50`, 3-Driver Triangulation + `6%` refranchising guard, EB `τ₀=6% → 3.0%` + `tanh` `13.0%`, buybacks `[-3.0%, +3.5%]` outside DCF); Explicit N-Year DCF (`r = 8.50% / 10.25%`, `E₁ = 1.0`, linear fade `g_t → ≤ 3.0%` & `RONIC_t → min(RONIC₀, 20%, r + 0.5(RONIC₀−r))`, McKinsey terminal, MM `RONIC = r ⇒ 1/r`); 3-Price Anchor (0g floor max `15.45× / 10.89×`), Bellman 5Y IRR (`IRR == r iff Price == Fair Value`), Reverse-DCF (`g_market` on `[-20%, +50%]` + Market-Implied CAP), Special Physics (`1.0× BVPS`, `No value`, `No data`).
- [ ] **Part III Cohorts & Live Case Studies:** `Prime Grade 225` (`110 US, 104 EU, 11 CA`), `Growth at ~0g 25` (`Model g₀ ≥ 5.0%`, `Mkt Implied g < 5.0%`), `Quality Grade 443`; Exact 6 Case Studies: `MSFT` (`25Y CAP, 30.5× Fair vs 28.2× Cur, +10.3% IRR`), `COST` (`30Y, 28.9× vs 53.5×, −4.6% IRR`), `ASML.NL` (`25Y, 32.5× vs 49.8×, −0.7% IRR`), `SPGI` (`30Y, 20.3× vs 25.4×, +3.5% IRR`), `WM` (`25Y, 14.4× vs 36.0×, −10.5% IRR`), `CRM` (`AI Fatal Flaw 4_sub=2 → 5Y CAP, Reject @ G4`).

---

## 3. Caveats
1. **`term_mult` Financial Ceiling Nuance:** `ORIGINAL_REQUEST.md` specifies `max 15.45× P/E operating / 10.89× financials` for the 0g Terminal floor (`term_mult`). Verified in `screener/gates.py:456`: at `r = 8.50%`, `(1 - 0.03/0.20)/(0.085 - 0.03) = 15.45×` exactly; at `r = 10.25%` (`RONIC_term = 20%`), theoretical `(1 - 0.03/0.20)/(0.1025 - 0.03) = 11.72×`, while observed Prime Grade reinsurer `HNR1.DE` (`RONIC₀ = 14.3%`) is `10.89×`. The deck should present `15.45×` operating / `10.89×` financials per `ORIGINAL_REQUEST.md` to ensure 100% spec parity.
2. **Chart Tooling:** Because `matplotlib`/`PIL` are not pre-installed in `/usr/bin/python3`, chart generation should use `/usr/bin/swiftc` CoreGraphics PNG rendering (zero external dependencies) or an isolated venv if `pip` is used; Slide 4 can alternatively use crisp native Google Slides horizontal bar shapes if preferred, though PNG charts on Slides 4, 12, and 15 give superior data visualization polish.

---

## 4. Conclusion
A **16-slide architecture** following the **Midnight Executive (`#1E2761`) / Crisp Ice Slate (`#F5F7FA`)** design system with **Teal / Coral-Orange / Amber** colorblind-safe accents, **Montserrat + Roboto** typography, `>= 30 pt` margins on the `720 × 405 pt` canvas, 3 custom high-DPI PNG charts in `output/charts/`, and the 3-part Verification Rubric (Programmatic + Visual + 100% Factual Parity) resolves every density bottleneck of the 12-slide draft while guaranteeing complete, accurate, brother-friendly coverage of Quality & Moat Screener v7.19.

---

## 5. Verification Method
1. Confirm exact v7.19 live numbers & case studies via:
   `python3 -c "from screener.dashboard import collect_screener_data; from screener.data import universe_keys; d = collect_screener_data(universe_keys()); print(d['summary'])"`
2. Confirm `gslides` formatting rules in `/Users/janis.schultz/.gemini/config/plugins/gslides/skills/gslides/references/styling.md` (lines 101–195, 326–339, 564–580).
3. After deck implementation, execute Section 6.1–6.3 of this handoff (`gslides readonly info --json`, `gslides readonly read --json`, `gslides readonly export-thumbnail`, and factual checklist sign-off).
