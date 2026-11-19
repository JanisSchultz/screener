Build a Google Slides presentation directly using the installed `gslides` skill (`/Users/janis.schultz/.gemini/config/plugins/gslides/skills/gslides/SKILL.md`) to explain how the complete Quality & Moat Screener (v7.19) investment framework works for the user's brother.

Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Integrity mode: development

## Requirements

### R1. Direct Google Slides Creation (`gslides`)
- Create a complete Google Slides presentation directly via the installed `gslides` skill (connected Google account: `schultz.janis@gmail.com`).
- The presentation's goal is to walk the user's brother clearly through how the complete Quality & Moat Screener (v7.19) investment framework works. Slide count, pacing (whether following the 12-slide blueprint below or splitting dense topics for readability), visual approach (native Google Slides layouts/shapes/tables and/or custom generated charts/diagrams), and speaker notes are open to the team's judgment.
- Optionally export a local `.pptx` copy if appropriate; keep any local working or exported files inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener` (e.g., `output/`).

### R2. Complete & Accurate Framework Coverage
- Present all sections of the Quality & Moat Screener (v7.19) specification below accurately, with the option to cross-check details against the `Screener` repository in the working directory where helpful:
  - Executive Summary, 1,175-company global universe, and 5 philosophical foundations.
  - Pre-Screen layer (`in_market` rule-of-law filter and `g6_default` structural sector defaults).
  - Part I Qualitative Screening: Two-stage waterfall, 6 Munger Reject Gates, live global funnel attrition (`1,175 → 225 Prime Grade`), 4 moat archetypes, Two-Step Deterministic CAP Engine (Porter's 5 Forces × 5 Macrotrends & Clock Speed, moderate haircut, fatal-flaw cap, 3 anti-drift rules), Gate 5 Superinvestor vectors, and Gate 6 solvency & cash-conversion pillars.
  - Part II Quantitative Valuation: Slump-Cannibal Compounder doctrine (zero analyst overrides), Sanitized Owner EPS & Age-Weighted Active EPS, Capital Base & M&A-matched `RONIC₀`, 4-Pillar Statistical Organic Growth (`g₀`), Explicit N-Year Mauboussin-Fade DCF, 3-Price Anchor, Bellman 5Y IRR, Reverse-DCF (`g_market`), and special physics / circuit breakers.
  - Part III Actionable Decision Cohorts (`Prime Grade` 225, `Growth at ~0g` 25, `Quality Grade` 443) and Live Case Studies (`MSFT`, `COST`, `ASML.NL`, `SPGI`, `WM`, `CRM`).

### R3. Structural & Visual Verification
- Verify the finished Google Slides deck both programmatically via `gslides` read-only inspection (slide inventory, element/text completeness) and visually via an independent reviewer inspecting rendered/exported slide views against an explicit visual and factual rubric.

## Reference Material: Quality & Moat Screener (v7.19) Specification

### 1. Executive Summary & Core Philosophy
- **Universe:** **1,175 large- and mid-cap public companies** across three developed universes: **United States (`us`)** 515 (Nasdaq-100 ∪ S&P 500), **Europe (`eu`)** 602 (STOXX Europe 600), **Canada (`ca`)** 58 (S&P/TSX 60).
- **Philosophical Foundations:**
  1. **Charlie Munger's Inversion Principle:** *"Tell me where I am going to die, so I never go there."* Sequential elimination rather than composite factor scoring; default stance is rejection.
  2. **Warren Buffett's Owner Earnings & Solvency Standard:** Economic moats with inflation-beating pricing power, cash-backed Owner Earnings, and a "peace-of-mind" balance sheet free from the *"kindness of strangers."*
  3. **Nick Sleep's Scale Economies Shared & Will Thorndike's *Outsiders*:** Customer-surplus flywheels and rational per-share capital allocation.
  4. **Michael Mauboussin's Competitive Advantage Period (CAP) & Base-Rate Fade:** Separates moat existence from moat duration, fading excess growth and incremental returns over a deterministically scored 5-to-30-year runway.
  5. **Strict Separation of Quality and Valuation (Zero Analyst Overrides):** Qualitative judgment decides which businesses qualify (Gates 1–6 in `screener/gates.py`); intrinsic value is computed 100% deterministically from audited financial statements with zero manual analyst overrides.

### 2. Pre-Screen Layer
1. **Rule-of-Law Market Filter (`in_market` → feeds Gate 2):** Western democracies with strong property rights (US, CA, UK, CH, Nordics, Western Europe = `Y`; Greece, Poland = `N`). `in_market = N` automatically fails Gate 2.
2. **Sub-Industry Structural Defaults (`g6_default` → feeds Gate 6):** Deposit-Taking Commercial Banks (10–15× leverage, credit/duration mismatch) and Regulated Utilities (6–8% capped ROIC, perpetual capex dilution) default to `N` at Gate 6.

### 3. Part I: Qualitative Screening — The 6 Munger Reject Gates (Two-Stage Waterfall)
- **Blank Gate Rule:** Unreviewed (`blank`) gates never pass (currently 0 across all 1,175 companies — 100% evaluated).
- **Stage 1 — Early Stop (Gates 1–3):** Failure at Gate 1, 2, or 3 stops immediately and leaves Gates 4–6 blank.
- **Stage 2 — Full Diagnostic Scorecard (Gates 4–6):** Every company passing Gate 3 (**483 structural moat franchises**) receives full scores across Gates 4, 5, and 6 even if rejected at Gate 4 (`CAP < 15Y`) or Gate 5 (`Score = 0`).
- **Live Global Funnel Attrition (v7.19):**
  - Starting Universe: **1,175** (US 515 | EU 602 | CA 58)
  - Gate 1 (Simple to Understand): −30 (−2.6%) → **1,145** remain
  - Gate 2 (Essential Western Need & Entrenched Habits): −156 (−13.3%) → **989** remain
  - Gate 3 (Moat Profile `3a ≠ None` & Pricing ≥ Inflation `3b = Y`): −506 (−43.1%) → **483** remain
  - Gate 4 (Predictable Runway `CAP ≥ 15Y`): −108 (−9.2%) → **375** remain
  - Gate 5 (Honest, Able Management & Allocation `Score ≥ 1`): −16 (−1.4%) → **359** remain
  - Gate 6 (Cash Conversion, Peak-to-Peak EPS & Fortress B/S): −134 (−11.4%) → **225 Prime Grade (19.1%)**
- **Gate Details:**
  - **Gate 1 (`Y/N`):** Circle of competence & external verifiability. Rejects unproven/pre-profit models and opaque balance sheets (proprietary trading, crypto treasuries, binary biotech).
  - **Gate 2 (`Y/N` + `2r`):** Munger/Buffett *"likely to spend"* standard (functional necessities + entrenched daily habits & Lindy luxury) with low societal/legislative ruin risk. Rejects big-ticket deferrable cyclicals (cruises, airlines, homebuilders), commodity explorers, pariah regimes, and predatory/addictive models (tobacco, CFD betting).
  - **Gate 3 (`3_tb`, `3_ia`, `3_se`, `3_rd` scored `0/1/2` + `3a` + `3b`):** 4 Moat Archetypes: `Toll booth & switching costs` (124 Prime), `Irreplaceable infrastructure & intangibles` (71 Prime), `Scale economies shared` — strictly Nick Sleep model (17 Prime), `R&D & innovation leadership` (13 Prime). `3b = Y`: 5Y Median GAAP ROIC ≥ 12% (or Tangible ROIC ≥ 15%) AND Incremental ROIIC ≥ 12%, plus real pricing power ≥ inflation.
  - **Gate 4 (Two-Step Deterministic CAP Engine, `CAP ≥ 15Y`):** Step 1 Initial CAP from Gate 3 Moat scores (`m_max`, `m_sum`): `0Y` (`m_max=0`), `15Y` (`1,1`), `20Y` (`1,≥2` or `2,2`), `25Y` (`2,3`), `30Y` (`2,≥4`). Step 2 Porter's 5 Forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub` scored `0/1/2`) evaluated across the **5 Macrotrends** (AI/Automation, Demographics/Labor, Geopolitics/Reshoring, Energy/Resources, Inflation/Cost of Capital) & **Mauboussin Clock Speed** (presumptive `4_sub ≥ 1` for fast-clock-speed tech/pharma unless unbypassable). Tiered Moderate Haircut `h(c1)`: `0→0Y`, `1–2→−5Y`, `3–4→−10Y`, `5→−15Y`. Fatal-Flaw Cap (`any Force = 2`): caps `CAP_final ≤ 10Y` (automatic Reject). Prime Grade CAP distribution: 51 at 15Y, 114 at 20Y, 57 at 25Y, 3 at 30Y. Includes 3 Anti-Drift Rules: Peer Benchmarking, UI Seat Layer (`2`) vs Proprietary Data/Statutory Engine (`1`), and Gate Orthogonality (no gate-bleed from G5/G6 into G4).
  - **Gate 5 (`0/1/2`, pass ≥ 1):** 5 Superinvestor Vectors — Integrity & Candor (Fisher/Buffett), Rational Capital Allocation (Murphy/Thorndike), Customer Surplus (Bezos/Sleep), Product-Led Execution, Anti-Bureaucracy & Planned Abandonment (Wallenberg/Drucker).
  - **Gate 6 (`Y/N` + `< 3` numeric flags for top tiers):** 3 Pillars — (1) Peak-to-Peak Cycle Owner EPS Compounding, (2) Multi-year Owner FCF ÷ GAAP NI ≥ 80%, (3) Peace-of-Mind Fortress Balance Sheet (3Y median Net Debt ÷ Owner Earnings ≤ 4.0y, EBIT ÷ Interest > 5.0×; contextual standards for inflation-indexed infrastructure & Solvency II > 200% insurers).

### 4. Part II: Quantitative Valuation — Explicit Mauboussin-Fade DCF
- **Slump-Cannibal Compounder Doctrine:** Looks through temporary 1Y revenue slumps (`sales_1y`) using multi-cycle structural growth (`g₀`), with zero manual analyst overrides.
- **Step 1 — Sanitized Owner EPS & Age-Weighted Active EPS:** `Owner EPS = (NI + max(0, min(clean_DA, max(0, OCF - NI)) - CapEx - 0.20 * AvgLease)) / Shares`. Includes Cash-Flow Backing (`OCF - NI`), `1.5×` transient impairment cap, `20%` IFRS-16 lease deduction (US-GAAP exempt), windfall spike & pre-IPO stripping, and Age-Weighted Mid-Cycle Reversion (`w = 50%` for peak ≤ 1y old fading to `0%` at 4y).
- **Step 2 — Capital Base & M&A-Matched `RONIC₀` (`≤ 50%`):** Tangible Operating ROIC (`NOPAT ÷ max(IC - Goodwill - Intangibles, 1/3 IC)`) for operating/fee firms; 5Y ROE for Balance-Sheet Financials & customer-cash clearing models (`IC ≤ 0` in ≥ 2/5y); GAAP ROIC for IFRIC-12 concessions. Goodwill-heavy cash acquirers (`r_tang > 1.25 × r_GAAP`) blend `r_tang` and `r_GAAP` harmonically by cash-funded M&A growth share `w = clip(ma_reinvest × r_GAAP / g₀, 0, 1)`.
- **Step 3 — 4-Pillar Statistical Organic Growth (`g₀ ≤ 13%`):** (1) Dilution-Only Share Index `S_t`, (2) Cycle-Spanning Theil–Sen (`Δt ≥ 5y`, `P25`/`P50`), (3) 3-Driver Triangulation across Revenue, NOPAT & Owner Earnings (plus 6% refranchising guard), (4) Empirical Bayes shrinkage (`τ₀ = 6%`) toward `3.0%` + smooth `tanh` compression to `13.0%`. Buybacks clamped to `[-3.0%, +3.5%]` and kept out of firm-level DCF.
- **Step 4 — Explicit N-Year Mauboussin-Fade DCF (`r = 8.50%` operating / `10.25%` financials):** Conservative `E₁ = 1.0 × Active EPS`. Stage 1 (`t = 1..N`, `N = CAP`) fades `g_t` linearly `g₀ → min(g₀, 3.0%)` and `RONIC_t` linearly `RONIC₀ → min(RONIC₀, 20%, r + 0.5(RONIC₀ - r))`, with `FCF_t = E_t(1 - g_t/RONIC_t)`. Stage 2 McKinsey terminal value at `3.0%` inflation. Exact Miller–Modigliani zero-spread invariance (`RONIC = r ⇒ Fair P/E = 1/r`).
- **Step 5 — 3-Price Anchor, Bellman 5Y IRR & Reverse-DCF:**
  1. 3-Price Anchor: Current Share Price, DCF Fair Value, and Standalone Terminal Price (0g / 3% inflation floor, max `15.45×` P/E operating / `10.89×` financials).
  2. Bellman-Consistent 5Y Expected IRR across `FCF_1..FCF_5` + exact Year-5 DCF continuation value `V_5` (`IRR == r` iff `Price == Fair Value`).
  3. Reverse-DCF Market-Implied Growth (`g_market` on `[-20%, +50%]` grid + bisection) & Market-Implied CAP.
  4. Special Physics & Circuit Breakers: `1.0× BVPS` MTM HoldCo anchor, `No value` (`Fair Value ≤ 0`), and `No data` (`BLOCKING_AUTO_NOTES`).

### 5. Part III: Actionable Decision Cohorts & Live Examples
- **🛡️ Prime Grade (225):** Clears all 6 gates (`< 3` G6 flags) — 110 US, 104 EU, 11 CA.
- **💎 Growth at ~0g (25):** Quality Grade, Valued, `Model g₀ ≥ 5.0%`, `Mkt Implied g < 5.0%` — mispriced compounders trading near 0g floor.
- **🏰 Quality Grade (443):** Structural moat cohort passing G1, G2, G3 (`< 3` G6 flags).
- **Live Examples:** `MSFT` (25Y CAP, 30.5× Fair P/E vs 28.2× Cur P/E → 10.3% 5Y IRR), `COST` (30Y CAP, 28.9× Fair vs 53.5× Cur → −4.6% IRR), `ASML.NL` (25Y CAP, 32.5× Fair vs 49.8× Cur → −0.7% IRR), `SPGI` (30Y CAP, 20.3× Fair vs 25.4× Cur → 3.5% IRR), `WM` (25Y CAP, 14.4× Fair vs 36.0× Cur → −10.5% IRR), `CRM` (AI Fatal Flaw `4_sub=2` → 5Y CAP, Reject @ G4).

### 6. Recommended 12-Slide Blueprint
1. Title & Core Premise | 2. Design Philosophy (Inversion & Zero Overrides) | 3. Global Funnel Attrition Waterfall (1,175 → 225) | 4. Stage 1 Gates (G1–G3) | 5. Two-Step Deterministic CAP Engine (G3 → G4) | 6. Stage 2 Stewardship & Solvency Gates (G5–G6) | 7. Slump-Cannibal Doctrine & Sanitized Owner EPS | 8. Capital Returns (`RONIC₀`) & 4-Pillar Statistical Growth (`g₀`) | 9. Explicit N-Year Mauboussin-Fade DCF | 10. 3-Price Anchor, Bellman 5Y IRR & Reverse-DCF | 11. Decision Cockpit & Discovery Tiers (`Prime Grade`, `Growth at ~0g`, `Quality Grade`) | 12. Live Case Studies (`MSFT`, `COST`, `ASML.NL`, `WM`, `CRM`).

## Acceptance Criteria

### Presentation Delivery & Structural Completeness
- [ ] A Google Slides presentation explaining the Quality & Moat Screener (v7.19) investment framework is created via the `gslides` skill, and its presentation ID and edit URL are returned; any local working or exported files reside within `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`.
- [ ] Read-only structural inspection via `gslides` confirms every slide is populated with zero leftover placeholder text, blank content regions, or broken elements, and covers all core sections of the v7.19 specification (Philosophy & Universe, Pre-Screen Layer, Gates 1–6 & Funnel Attrition, Two-Step CAP Engine, Quantitative Mauboussin-Fade DCF, Decision Cohorts, and Live Examples).

### Factual Accuracy & Visual Quality
- [ ] All quantitative metrics, attrition counts, formulas, thresholds, cohort counts, and ticker case-study figures in the deck match the provided v7.19 specification (and/or verified repository data) with zero discrepancies.
- [ ] An independent reviewer inspecting rendered/exported slide views against an explicit visual rubric confirms zero overlapping shapes/text, zero clipped or overflowing text, legible font hierarchy, and clean, consistent visual layout across 100% of slides.
