# Quality & Moat Screener (v6.27 — 6 Munger Quality Gates & Equity Bond Below PAR)

Interactive standalone HTML cockpit for global quality screening (US: Nasdaq-100 ∪ S&P 500, EU: STOXX Europe 600, CA: S&P/TSX 60).
Source data and framework live as plain files; `build.py` compiles them instantly into `output/screener.html` (and `output/index.html`).

```
Pre-Screen (markets → Gate 2, sub-industry → Gate 6 default) → 6 Munger Reject Gates (Qualitative) → Quantitative (Equity Bond Below PAR) → Shortlists

Every qualitative step is a REJECT gate; Qualitative → "Review Stage / Action" and "Rejected at" show live flow:
Gate 1: Simple to Understand (verifiable, established model)
Gate 2: Essential Western Need & Entrenched Everyday Habits ('Likely To' Standard)
Gate 3: Strong Moat & Pricing Power >= Inflation (3a archetype + 3b pricing >= inflation & Proof of Moat ROIC/ROIIC >= 12%)
Gate 4: Low Disruption Risk & Predictable Runway (CAP >= 15 yrs via Mauboussin Base Rates & 5-Macrotrend Haircuts)
Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation (5 vectors >= 1)
Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Peace-of-Mind Balance Sheet (3 pillars: Peak-to-Peak, FCF >= 80% NI, Debt <= 4y & Interest Cover > 5x)

-> "Quality pass" and conditional "Calamity pass" (temporary fixable calamities on Gates 3b, 5, or 6 only, while Gates 1, 2, 3a, and 4 pass) enter the Quantitative sheet (Equity Bond Below PAR: 4-5Y Peak Owner EPS, PAR Multiple, 5Y Expected IRR, Market-Implied CAP, Market-Implied g), separated into clean Shortlists vs. the Calamity Watchlist.
A blank gate input never passes: the company stops as "To review (blank gate)".

v6.27: By-the-Book PAR Valuation Refinements (Pillar 2 Cap, CAP Growth Slope & Multiplicative Reinvestment Efficiency):
- Pillar 2 Historical Midpoint Cap (par_hist_cap = 35.0): Capped t_hist = min(35.0, 0.5 * (mult_low_5y + mult_high_5y)) symmetric with par_roic_cap = 35.0, preventing 2021 ZIRP bubble peaks and depressed-denominator years from inflating PAR above fundamental value (CFR.CH, SAF.FR, LUND B.SE) or driving g_market negative.
- Gate 4 CAP-Linked Growth Multiple Slope (M_cap): Linked Pillar 1 growth slope directly to Gate 4 CAP (240.0 for CAP >= 30y, 200.0 for CAP >= 20y, 170.0 for CAP >= 15y) so moat duration differentiates all funnel companies even when bottom-up g_implied is populated.
- Multiplicative Reinvestment Efficiency (eta_reinv): Scaled Pillar 1 growth credit by free-cash-flow payout capacity (1 - g_exp / ROIC) relative to the 35% ROIC capital-light standard (clamped to [0.25, 1.00]), preserving full credit for 35%+ ROIC compounders while penalizing capital-heavy growers (ALC.CH, EQT.SE, LUND B.SE) and maintaining exact closed-form g_market inversion.

v6.26: Gate 4 CAP-Linked Growth Engine & Expected Growth Renaming (g_exp):
- Gate 4 CAP-Linked Growth Persistence (λ): Grounded forward growth persistence in Gate 4 Runway CAP:
  (1) CAP >= 30 Years (Fortress Moats & Secular Monopolies: SPGI, MCO, MSFT, V): λ = 0.25 (slower autoregressive fade, higher weighting of historical compounding track record).
  (2) CAP >= 20 Years (Standard Quality Compounders: OTIS, ZTS, CPRT): λ = 0.15 (matches Mauboussin's 75-year market-wide autoregressive baseline).
  (3) CAP >= 15 Years (Shorter Runway / Higher Transition Risk): λ = 0.10 (faster fade towards the 7.0% base rate).
  (4) Fallback / Unpopulated: λ = 0.15.
- Expected Growth (g_exp) & Symmetrical Growth Margin: Renamed 'Forward Implied g' (g_imp) to 'Expected Growth' (g_exp) across UI, specs, and dashboard to eliminate terminology collision with Market-Implied Growth (g_market). Growth Margin of Safety is clearly defined as (g_exp - g_market), paired symmetrically with Moat Runway Margin (Our CAP - Market-Implied CAP).

v6.25: Conditional Calamity Pass Tier (Buffett Temporary Fixable Calamities on Gates 3b, 5 & 6):
- Added `calamity` ('Y'/blank) and `calamity_note` fields across `inputs.csv`, `screener/gates.py`, `screener/apply_evaluation.py`, and the HTML cockpit (`screener/dashboard.py`).
- Preserves raw failed gate scores (`3b="N"`, `5=0`, or `6="N"`) while allowing great franchises facing temporary, fixable issues to enter Quantitative PAR valuation under the separate `Calamity pass` tier when Anchor Gates 1, 2, 3a (not None), and 4 (CAP >= 15Y) all pass and remaining downstream gates are evaluated.
- Surfaced in the HTML cockpit via amber badges, dedicated `⚠️ Calamity Watchlist` tab, off-by-default Shortlist toggle, and dossier kill-switch callout.

v6.24: Quality Funnel Integrity Audit & Legacy Waterfall Swap Remediation:
- Quality Funnel Integrity Audit: Removed 5 companies that breached the updated v6.23 methodology from the Quality Pass funnel:
  (1) MSCI (Financial Engineering: -$820M book equity, Net debt 4.7y > 4.0y ceiling -> Rejected at Gate 6)
  (2) SNPS (Mega-M&A Ansys debt: Net debt 7.9y, IntCov 2.0x, FCF conv 63.6% -> Rejected at Gate 6)
  (3) NOW (Macrotrend #1 AI Disruption: Seat-based ITSM SaaS capped at CAP=10 -> Rejected at Gate 4)
  (4) AJG (Serial debt-funded M&A: Net debt 7.2y, IntCov 3.9x -> Rejected at Gate 6)
  (5) MDLZ (Sub-hurdle 10.8% ROIC < 12.0% hurdle & price-elastic volumes -> Rejected at Gate 3b)
- Full Legacy Waterfall Swap Remediation: Restored historical moat archetypes, pricing power, and CAP ratings for all 574 companies across US (240), EU (313), and CA (21) stranded in 'To review (blank gate)' following the v6.21 Gate 3/4 swap via `screener/migrations/remediate_v6_21_swap.py`.
- 100% Complete Funnel Resolution: 'To review (blank gate)' reduced to exactly 0 across all global universes (US: 0, EU: 0, CA: 0).
- Funnel: US 107, EU 103, CA 12 (Global Quality Funnel: 222 world-class compounders).

v6.23: Operating ROIC Normalization (Uncorrupted Operating Capital & M&A Goodwill Neutralization):
- Switched 3-Pillar Fundamental PAR Multiple and Market-Implied Growth to Uncorrupted Operating ROIC:
  Replaced accounting-distorted GAAP ROIC (NOPAT ÷ Total Invested Capital including goodwill) with true uncorrupted Operating ROIC (NOPAT ÷ Tangible Invested Capital = Equity + Debt - Cash - Goodwill - Intangibles).
- M&A Goodwill Neutralization: Eliminates the severe valuation penalty on capital-light toll booths that completed strategic mega-mergers (e.g. S&P Global's 2022 IHS Markit acquisition added $52.8B in accounting goodwill/intangibles, deflating GAAP ROIC to 11.8% and collapsing its PAR multiple to 19.9x; Operating ROIC normalizes SPGI to 35.0% and a proper 27.6x PAR multiple, moving it from +31.2% Above PAR to -5.4% Below PAR at 11.6% 5Y expected IRR).
- Negative Tangible Capital Standard: Asset-free compounders operating on negative net tangible capital (deferred subscription revenues, upfront payments, negative working capital) earn structurally unbounded returns on tangible capital, automatically aligning with par_roic_cap = 35.0%. True asset-heavy businesses (WM, UNP, CAT) retain their low physical-capital multiples.
- Full Transparency & Overrides: Added 'Operating ROIC 5Y (Tangible)' and 'My ROIC (override)' to the Quantitative sheet alongside GAAP ROIC, giving investors full visibility into both ongoing operating engine quality and retrospective total capital allocation.
- Funnel: US 112, EU 103, CA 12 (Global Quality Funnel: 227 world-class compounders).

v6.22: Mauboussin Growth Engine (Base-Rate Regression & Market-Implied Growth) + Streamlined Gate 6 Triad:
- Mauboussin Base-Rate Growth Regression: Grounded forward implied growth (g_imp) in Michael Mauboussin & Dan Callahan's 75-year empirical growth research ('Competitive Advantage Period: The Neglected Value Driver', Counterpoint Global, April 2026):
  (1) Enforced par_g_cap = 12.0% as the empirical ceiling for through-the-cycle large-cap EPS growth (reflecting empirical data that even top-quintile >44% historical growers regress to a 13.3% median within 3 years).
  (2) Replaced raw historical CAGR extrapolation with Mauboussin's autoregressive fade formula:
      Expected g = min(par_g_cap, max(0.02, 0.15 * (max(0, Hist_g) - par_g_base) + par_g_base))
      anchoring forward growth to the 7.0% mature large-cap base rate (par_g_base = 7.0%, regression slope = 0.15).
- Market-Implied Growth (g_market) & Growth Margin of Safety: Inverted the 3-Pillar Fundamental PAR formula on the Quantitative and Shortlists sheets:
  g_market = (3 * cur_mult - 5Y_midpoint_mult - min(ROIC * 100, par_roic_cap)) / 200
  alongside the Growth Margin of Safety (g_imp - g_market), paired symmetrically with Market-Implied CAP and Moat Runway Margin. Instantly reveals whether a stock's current multiple is pricing in heroic (>25%) growth or depressed (<0%) growth.
- Streamlined Gate 6 Triad: Purged redundant hurdle rate checks (already verified at Gate 3b Proof of Moat) into a focused 3-Pillar Triad:
  (1) Peak-to-Peak Compounding across cycles, (2) Real Cash Conversion (FCF >= 80% GAAP NI), (3) Self-Funding Fortress Balance Sheet (Net Debt <= 4y Owner Earnings, Interest Coverage > 5x).
- Funnel: US 112, EU 103, CA 12 (Global Quality Funnel: 227 world-class compounders).

v6.21: Gate 3 & Gate 4 Architectural Swap + Look-Through Holding Company Standard:
- Logical Sequencing of Quality Gates: Swapped Gate 3 (Moat Duration / Runway) and Gate 4 (Moat Existence & Pricing Power) to reflect foundational value investing logic: first verify that a structural economic moat actually exists and produces excess returns on capital (Gate 3: Moat Archetype 3a + Pricing Power & Proof of Moat 3b with 5Y median ROIC >= 12% and incremental ROIIC >= 12%), and only then evaluate how long that moat can endure against disruption (Gate 4: Runway / CAP >= 15 yrs).
- Look-Through Holding Company Standard: Holding companies (e.g. LUND B Lundbergsföretagen, INDU C Industrivärden) are evaluated on the economic reality of their portfolio look-through moats, pricing power, and balance-sheet durability rather than top-level accounting artifacts. Both unblocked into the Quality Pass funnel (LUND B: Holmen forestlands/hydro, prime CBD real estate, Sandvik; INDU C: Sandvik tooling and Volvo commercial trucks).
- Clean Gate 4 Filtering: Downstream challenged consumer compounders (NKE, SBUX, CMG, CLX, ADS, MONC) pass Gate 3 on proven brand intangibles/scale economies and high historical ROIC, and are cleanly filtered at Gate 4 on limited 10-year CAP runway due to brand heat / fashion cycles / store saturation.
- Funnel: US 112, EU 103, CA 12 (Global Quality Funnel: 227 world-class compounders).

v6.20: Gate 4 Base-Rate & Haircut Engine (Mauboussin & Callahan 1970–2024 Persistence) & Market-Implied CAP:
- Two-Step Longevity Architecture:
  (1) Outside View (Industry Base-Rate Persistence Anchor): Grounded in Michael Mauboussin and Dan Callahan's 54-year empirical study (1970–2024, Morgan Stanley Counterpoint Global):
      - Tier 1 (p=0.90, f=0.10): Consumer Staples, Food/Beverage, Household & Personal Care -> Baseline CAP 20–30 Years.
      - Tier 2 (p=0.81–0.87, f=0.13–0.19): Medical Devices, Mission-Critical Tech Hardware, Restaurants/Services -> Baseline CAP 15–20 Years.
      - Tier 3 (p=0.75–0.79, f=0.21–0.25): Software & IT Services, Pharma/Biotech, Semis, Capital Goods, Rails -> Baseline CAP 10–15 Years.
      - Tier 4 (p=0.70–0.71, f=0.29–0.30): Upstream Energy, Telecom, Regulated Utilities -> Baseline CAP 5–10 Years (natural REJECT).
  (2) Inside View (5-Macrotrend Deductive Haircut Filter): Deductively reduces the baseline by -5 to -10 years for structural headwinds across:
      [1] Automation & Cognitive Tech (AI disruption of seat SaaS/consulting), [2] Demographic Aging & Labor Scarcity,
      [3] Geopolitical Realignment & Supply Chain Reshoring, [4] Energy Transition & Resource Limits, [5] Structural Inflation & Cost of Capital.
- Incremental ROIC (ROIIC >= 12%): Codified into the Proof-of-Moat test, ensuring capital compounding is not profitless growth.
- Market-Implied CAP & Moat Margin: Added to Quantitative and Shortlists sheets, calculating exact years of excess return priced into the market quote relative to fundamental CAP.

v6.19: Gate 2 Evolution — Essential Needs & Entrenched Everyday Habits ('Likely To' Standard):
- Expanded Gate 2 beyond bare biological survival ('water and bread') to Charlie Munger & Warren Buffett's enduring consumer habit principle ('likely to' spend): admitting resilient, high-frequency daily rituals, cultural staples, low-cost household entertainment, and Lindy-luxury compounders (e.g. PEP, MDLZ, HSY, MNST, SBUX, CMG, DPZ, YUM, QSR, NFLX, NKE, ITX, RMS, MC, CFR, BEI, HEIA, DGE, LISP, LOTB).
- Maintained strict rejection on discretionary big-ticket/deferrable cyclicals (cruises, airlines, homebuilders), speculative commodity miners (gold), non-Western/pariah revenue concentrations, and predatory/addictive harm (tobacco, CFD trading).
- Rescued high-quality consumer compounders to be rigorously tested by downstream Gates 3–6 (moat, pricing power, macro resilience, and real cash conversion). Funnel expanded to 225 world-class global compounders (US 112, EU 101, CA 12).

v6.18: 3-Pillar Fundamental PAR Multiple & Cycle High Guardrail:
- Replaced the rigid market-multiple approach with Charlie Munger & Warren Buffett's 3-Pillar Fundamental PAR Multiple:
  PAR Multiple = min(mult_high_5y, (2 * (g_imp * 100) + 5Y Cycle Midpoint Multiple + min(ROIC * 100, par_roic_cap)) / 3).
- 5Y Cycle High Guardrail: Codifies the core value investing rule that through-the-cycle fair value can never exceed the highest multiple the market was willing to pay at the peak of the 5-year cycle. Protects balance-sheet financials and reinsurers (MUV2.DE capped at 11.4x, moving to Above PAR; III.GB clamped to 7.9x; BAM.CA to 11.3x) from being inflated into fantasy multiples while leaving pure operating compounders (OTIS, ZTS, MSFT, CPRT) completely untouched.
- Secular Growth Factor (Benjamin Graham / Peter Lynch): Directly integrates 2 * (g_imp * 100) into the multiple (+16 to +24 turns for 8%-12% compounders).
- Operating ROIC Normalization (Neutralizing Buyback Distortions): Set par_roic_cap = 35.0 as the empirical proxy for true uncorrupted operating ROIC (NOPAT / Operating Invested Capital: OTIS 32.7%, AZO 35.7%, AAPL 35.2%, MCK 30.1%), neutralizing negative-equity denominator collapses without penalizing true operating quality.
- Anti-Bubble Deflation: Deflated bubble multiples from the ZIRP era (SNPS PAR deflated from 54.9x to 34.0x; WM PAR deflated from 34.3x to 20.8x, properly warning against paying peak multiples for asset-heavy 12% ROIC).
- Normalized Berkshire Hathaway (BRK.B) Class A vs. Class B share basis in data/us/financials.csv (peak operating EPS ~31.29, cycle multiples 16-22x).

v6.17: Batch 2 Gate 3 evaluation: Alphabet (GOOGL) upgraded to CAP 20 (Quality Pass) under the 5-Macrotrend Secular Resilience standard (full-stack AI integration, Android/Chrome, YouTube, Cloud, $80B+ net cash); Below PAR shortlist at 15.0% 5Y IRR.

v6.16: Batch 1 Gate 6 consistency audit: rescored RSG & WCN.CA (landfills), AJG & BRO (P&C brokers), DHR & TMO (life sciences tools), AZA.SE, FBK.IT & SAVE.SE (digital wealth platforms), and MCD (franchise royalty).

v6.15: Gate 3 secular resilience evolution: replaced the single-factor 'Strict AI Rule' with the 5-Macrotrend Secular Resilience Test (Automation & Cognitive Tech, Demographics & Labor Scarcity, Geopolitical Realignment, Energy Transition & Resource Limits, Structural Inflation & Cost of Capital).

v6.14: Gate 6 qualitative re-framing: Peace of Mind vs. Kindness of Strangers across 4 compounding pillars (Peak-to-Peak compounding, real cash conversion, hurdle ROIC >= 12%, peace-of-mind balance sheet); OTIS, MSCI, SNPS, WM, and FFH.CA rescued into the Quality Pass funnel.

v6.13: Gate 6 surplus-cash rule for cash/T-bills (BRK.B rescued); float-funded holding companies judged on look-through book value / operating earnings.

v6.12: live fetch for the new funnel names; 'My Peak EPS' also caps Owner EPS for the cycle multiples (funnel: US 91, EU 87, CA 9).

v6.11: computed PAR inputs & consistency fixes
- Peak Owner EPS, cycle low/high multiples, peak-to-peak g and "New peak vs prior cycle" are computed by
  screener/fetch/par.py (one-off non-cash earnings spikes left out); your overrides go in "My Peak EPS" / "My growth g"
  with a note (it also caps each year's Owner EPS for the cycle multiples). `fetch_market_data.py --offline` recomputes from data/_cache; diff report output/par_recompute_report.csv.
- Median ROIC = 5-year median from code (no placeholder values). Dual listings mirror the primary line (universe.json "mirror").
- Gate 2 uses only your markets; the sub-industry defaults (regulated utilities, deposit banks) now feed Gate 6.
- Gate 6 rule check on Quantitative flags net debt > 4y, interest cover < 5x and no new peak; flagged passes re-scored with notes.
- Gate 3 AI-disruption rule written into the definition and applied to all data / information sellers.

v6.9: Intelligent Waterfall Architecture & Sequential Funnel Cleanup
- Visual Waterfall: Downstream gate cells automatically gray out once an earlier gate fails, eliminating visual clutter.
- Dedicated 'Review Stage / Action' column: Filter by 'Stage 6: G6 Candidate' or 'Quality Pass (Funnel)' for instant focus.
- Purged 4,392 phantom downstream entries in inputs.csv across US, EU, and CA while preserving 100% funnel consistency.

v6.8: Gate 6 Evolution (Peak-to-Peak Cycle Compounding & Fortress Balance Sheet)
- Explicitly codified the Peak-to-Peak Business Cycle EPS Test as an analytical prerequisite for the PAR Valuation model:
  companies must achieve a new high in Owner EPS at the peak of each succeeding business cycle, with clear indications
  of reaching new earnings highs in future cycles (intra-cycle dips remain normal provided peak-to-peak growth continues).
- Replaced ambiguous "anti-fragile" terminology with explicit Fortress & Self-Funding Balance Sheet standards:
  net debt repayable from normal owner earnings in <= 4 years (or net cash), interest coverage > 5–10x through the cycle,
  contractual inflation indexation for physical infrastructure (>5x coverage), Solvency II > 200% for float institutions,
  and a strict ban on financial engineering (debt-funded buybacks at peak multiples creating negative equity) and serial debt rollups.

v5.4: formalised Gate 3.4 'The Management & Culture Gate (The Rower)' into a five-vector elimination rubric
(3.4a Integrity & Candor [Fisher/Buffett], 3.4b Capital Rationality & Incentives [Murphy/Thorndike], 3.4c Consumer
Surplus & Value Asymmetry [Bezos/Sleep], 3.4d Product-Led Vision & Execution [BAG], 3.4e Anti-Bureaucracy & Planned
Abandonment [Wallenberg/Drucker]). A disqualifying behavioral red flag on any vector results in a score of 0 (REJECT).
Pricing Power & Rower Vulnerability Audit: purged 8 false positives (ADBE, GDDY, CAH, ABBV, GPC, ROP, FICO, INTU)
failing Gate 2.3 (stalled pricing/churn), Gate 3.4 (predatory dark patterns, rent extraction, panic/roll-up M&A), or
Gate 3.3 (Proof of Moat on GAAP ROIC); US Funnel refined from 124 to 116 (global funnel from 229 to 221).
Principal Protection Multiple Limit (Capital-Light Compounders): Operating companies with Tangible ROIC >= 35% and
FCF conversion >= a_fcfconv (90%) evaluate the multiple limit on Tangible ROIC (capped at 35x), preventing asset-light
market infrastructure and software monopolies (e.g. Deutsche Börse, Euronext, Cboe) from being artificially capped at
~15x by historical M&A goodwill; their buy-below price is now governed directly by the Chris Hohn 10-year DCF exit buffer.

v5.3: comprehensive Business Quality evaluation audit across all 1,175 companies (CA, EU, US) for cross-regional
sub-industry consistency, look-through holding discipline, and alignment with reported ROIC/FCF reality (funnel
refined from 255 to 229: US 124, EU 92, CA 13); cycle-normalised E_norm populated for <7-yr history cyclicals.

v5.2: comprehensive Growth Assumption audit across all funnel companies (91 explicit g_est overrides); 5-yr and
3-yr fallback growth bounded by sales CAGR + 4% (Operating) and book value CAGR + 2% (Bank / Insurer).

v5.1: negative invested capital (float / buybacks) handled in ROIC; SEC XBRL tag & accounting identity fallbacks
(EBIT = Pretax + Interest, implied diluted shares NI ÷ EPS for $1 test); 3-yr growth fallback capped at sales/BV
3-yr CAGR + 5% (post-trough rebound guard); Equity Bond requires Y_c > 0; Trigger 3 requires Audit & Protection pass.

v5.0: superinvestor quality filter ('Chris Hohn bar' — ~250 investable companies globally).
- Gate 0.2: Regulated utilities (Electric, Gas, Multi, Water) and deposit-taking commercial/regional/custody
  banks set to sole_owner = N on Pre-Screen (capped ROIC, perpetual dilution, leveraged credit/duration risk).
- Gate 2.1 / 2.3: Heavy industrial equipment and vehicles require >65% captive aftermarket to avoid Long-Cycle
  Trap (Repeat Frequency = 0); pipeline and commodity transport operators fail Gate 2.3 Pricing Power.
- Gate 3.3: Proof of Moat rule — operating companies with reported track records failing both tangible
  ROIC >= 15% and GAAP ROIC >= 12% are capped at CAP <= 5 (REJECT).
- Developed market pass count tightened from 353 down to 255 companies across US (131), EU (106), and CA (18).

v4.4: superinvestor cross-check fixes (regulated infrastructure in all sectors, reverse 2x2 check, businesses
earning mainly outside your markets fail Gate 2) and a new Canada universe (data/ca, Claude pre-scored — verify).

v4.3: the 2x2 matrix rejects only when Essentiality or Repeat Frequency is 0 (a 1 is not 'Low'); all zeros
re-checked; regulated utilities count as having Pricing Power.

v4.2: gates cut from 13 to 8 and inputs from 27 to 14 fields after a redundancy check (no verdict changed except
the market filter and one Must-Carry case); ROIC test uses tangible ROIC ≥ 15% and GAAP ROIC ≥ 10%; owner FCF uses
maintenance capex (MIN(capex, depreciation)); intermediate columns are grouped — click + to expand.

v4.1 additions:
- Business-model type (Inputs 0.0: Operating / Bank / Insurer / Holding) selects the Phase 4 tests
  (ROIC vs ROTE / ROE / NAV growth; FCF conversion vs combined ratio; debt cover vs CET1 / solvency / LTV;
  NAV discount for holding companies).
- Normalised earnings: Y_c = MIN(latest, normalised) for earnings and FCF (median margins × sales; cycle-average
  earnings for 2.1c Cyclical names; median ROE × equity for banks / insurers), with Peak margin / Below-normal /
  Short cycle flags.
- Guard rails: an entry needs your own review date (Inputs → "Reviewed by me"); Holdings warns on position size,
  cash floor and overdue reviews, and shows SELL candidate only with 2+ triggers or Trigger 1; Methodology logs
  every parameter change with date and reason.
```

## Layout

```
screener/config.py        framework: fields (gates, scores, rubrics), gate chain, all parameters, change log
screener/gates.py         Python implementation of the 6 Munger gates and PAR maths (funnel selection, valuation)
screener/apply_evaluation.py validate & apply an evaluator agent's JSON evaluation to data/
QUALITATIVE_EVALUATION_SPEC.md standalone qualitative evaluation spec (6 Munger Reject Gates)
QUANTITATIVE_EVALUATION_SPEC.md standalone quantitative valuation spec (Equity Bond Below PAR v6.23)
COMPANY_EVALUATION_SPEC.md unified full-lifecycle evaluation framework spec
screener/v2/, v3/, v4_1/, v4_2/   archived earlier frameworks (not imported)
screener/data.py          file schema and CSV/JSON loading/saving
screener/fetch/           SEC EDGAR + Yahoo Finance sources, audit metrics, settings (SEC contact address)
data/<universe>/
  universe.json           titles, universe text, extra columns, breakdowns, benchmark symbols,
                          optional "parameters" overriding config defaults for this universe
  inputs.csv              Phase 1–3 inputs per company (Y/N gates, 0/1/2 scores, CAP years, calamity flag/note, notes, evidence)
  prescreen.csv           Gate 6 default by sub-industry (N or blank; your inputs)
  markets.csv             your markets by listing country (Y/N; feeds Gate 2)
  v4_prescore.csv         Claude's pre-scores for the fields new in v4 (merged by migrate_v4.py)
  v4_1_rescore.csv        Claude's v4.1 re-scores (id, code, value, note; merged by migrate_v4_1.py)
  v4_1_fin_estimates.csv  Claude's estimates of CET1 / solvency / combined ratio / NAV / LTV (verify!)
  financials.csv          Quantitative inputs (fetched + computed; peak_eps_est, g_est, g_implied, fin_note preserved)
  technicals.csv          weekly price / 30-wk MA / RS inputs (fetched)
  benchmarks.csv          market + sector benchmark trend (fetched)
  holdings.csv            your positions (Phase 5)
  backups/                v2 / v3 / v4.0 / v4.1 historical backups
data/_cache/              downloaded SEC / Yahoo responses (reused for 7 days; --offline uses them at any age)
build.py                  compile standalone interactive HTML cockpit -> output/screener.html
fetch_market_data.py      refresh Quantitative data (screener/fetch/par.py computes the PAR inputs)
screener/dashboard.py     generates the standalone HTML/JS cockpit application
screener/apply_evaluation.py ingests agent evaluations into inputs.csv / financials.csv
screener/migrations/      one-time historical migrations (already run)
```

## Typical workflows

Refresh market data for the funnel (Quality-pass companies), then rebuild:

```bash
python3 fetch_market_data.py us eu ca
python3 build.py
```

Recompute PAR inputs from the cache only (no network; technicals untouched):

```bash
python3 fetch_market_data.py us eu ca --offline --all
python3 build.py
```

Build and open the interactive screener dashboard in your browser (fully responsive on desktop, tablet, and mobile with auto-detected Card View and sticky-ticker Table View):

```bash
python3 build.py
open output/screener.html
```

Weekly technicals only (fast):

```bash
python3 fetch_market_data.py us eu --prices-only
```

Evaluate a company via an independent agent and ingest the result:

```bash
# Qualitative evaluation (using QUALITATIVE_EVALUATION_SPEC.md -> inputs.csv)
python3 screener/apply_evaluation.py --input qual_result.json

# Quantitative valuation (using QUANTITATIVE_EVALUATION_SPEC.md -> financials.csv)
python3 screener/apply_evaluation.py --input quant_result.json

# Full evaluation (using COMPANY_EVALUATION_SPEC.md -> both)
python3 screener/apply_evaluation.py --input full_result.json
```

Add a `CHANGELOG` entry in `screener/config.py` when you change the framework.

## GitHub Pages Deployment

The dashboard builds directly into `docs/index.html` and `output/index.html`:
```bash
python3 build.py
```

### Hosting on GitHub Pages
This repository is configured for GitHub Pages with two deployment options:
1. **GitHub Actions (Automated CI/CD)**: Push to `main`, and `.github/workflows/deploy.yml` automatically builds and deploys to Pages. In your GitHub repo settings: **Settings** → **Pages** → Source: **GitHub Actions**.
2. **Deploy from Branch**: Alternatively, select **Settings** → **Pages** → Source: **Deploy from a branch** → Branch: `main`, Folder: `/docs`.

Change the framework: edit `FIELDS` / `GATES` / `PARAMETER_GROUPS` in `config.py` (new input columns
also need adding to `data/*/inputs.csv`), then rebuild.

## Data notes

- US fundamentals: SEC EDGAR companyfacts (~10 fiscal years), split-adjusted with Yahoo split history.
  EU and non-SEC filers: Yahoo Finance annual statements (~4 years): peak-to-peak g falls back to first-year-to-peak,
  cycle multiples cover ~44 months, and fin_note says "short history".
- PAR inputs use current FX for all months (affects only companies whose quote and reporting currency differ).
- Money in millions of the reporting currency; market cap is converted into it (handles GBp quotes).
- "Latest FY" figures are the latest annual report, not trailing-twelve-months.
- Fetched data can contain tagging gaps or errors — check outliers before acting on a verdict.
- SEC contact address for the User-Agent header: `screener/fetch/settings.py`.
- Requires Python ≥ 3.9; fetcher also requires `requests`, `yfinance`.
