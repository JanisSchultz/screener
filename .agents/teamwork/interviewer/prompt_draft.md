Implement the Two-Stage Munger Waterfall and diagnostic Gate 5–6 scorecard (v7.18) in the Quality & Moat Screener so every company advancing past Gate 3 (485 companies across US, EU, and CA: 483 clean `3b = "Y"` passers plus `EL` and `APD` on Calamity pass) receives a complete 6-gate scorecard (`G4`, `G5`, and `G6`), even when rejected at Gate 4 (`CAP < 15Y`) or Gate 5 (`5 = 0`), with zero impact on `thr_cap = 15`, `phase_results`, or Prime Grade (225) and Prime Grade Calamity (13 total / 11 < 3 G6 flags) counts.

Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Integrity mode: development

## Requirements

### R1. Waterfall Validation, Ingestion & Audit Engine
- In `screener/apply_evaluation.py` (`validate_and_waterfall`), keep strict downstream scrubbing when Gate 1 = `"N"`, Gate 2 = `"N"`, or unwaived Gate 3 fails (`3a = "None"` or `3b = "N"` without `calamity = "Y"`). Remove downstream scrubbing of `5` and `6` when Gate 4 `CAP < 15` and of `6` when Gate 5 = `0` without calamity, keep `clear_calamity(...)` when Gate 4 `CAP < 15` (non-waivable Anchor Gate), and validate `5` in `{0, 1, 2}` and `6` in `{"Y", "N"}` whenever supplied.
- In `screener/bulk_scorer.py`, update `validate_company_evaluation` to preserve `5` and `6` on `CAP < 15` and `6` on `5 = 0`, validate `5` (`0/1/2`) and `6` (`Y/N`), and warn if any company advancing past Gate 3 leaves `5` or `6` blank. Update `audit_gate_3_universe` so Gate-3 failures still require blank `G4–G6`, while all 485 Gate-3-advancing companies are audited for non-empty, valid `5` and `6` (zero blank G5/G6 allowed across moat franchises). Update `REFERENCE_SNAPSHOT` for `CRM` once its verified `5` and `6` scores are recorded (keeping the other 10 reference companies, `NUE` blank `G4–G6`, and mirrors `ASML`/`ASML.NL` and `FER`/`FER.ES` consistent).

### R2. Bottom-Up Qualitative Evaluation of the 121 Incomplete Moat Franchises
- Evaluate all 121 incomplete moat franchises (108 Gate-4 rejects at `CAP = 5Y / 10Y` across 57 US, 51 EU, 0 CA + 13 Gate-5 rejects at `5 = 0` across 9 US, 4 EU, 0 CA) against the Gate 5 and Gate 6 rubrics in `QUALITATIVE_EVALUATION_SPEC.md` using only the existing local datasets and dossiers in the repository (`financials.csv`, `fundamentals_panel.csv`, `prescreen.csv` `g6_default`/`g6_checks`, and existing `note` dossiers).
- When batching and dispatching the 121 companies for bottom-up Gate 5 & Gate 6 evaluation, split evaluation agents strictly by GICS Sector / Sub-Industry across US and EU combined (never split US vs. EU into separate evaluator agents), preserving Sub-Industry Peer Benchmarking (Anti-Drift Rule #1 in `QUALITATIVE_EVALUATION_SPEC.md` / `COMPANY_EVALUATION_SPEC.md`) so cross-Atlantic sector peers are scored side-by-side on the same Gate 5 & Gate 6 yardstick and cross-checked against already-scored same-sub-industry peers in the 364 completed moat franchises.
- Score Gate 5 (`0 / 1 / 2`) for the 108 Gate-4 rejects while preserving existing `5 = 0` on the 13 Gate-5 rejects, and score Gate 6 (`Y / N`) for all 121 companies across Pillars 1–3 (`p2p_ok`, `fcf_conv >= 80%`, `g6_netdebt_yrs <= 4.0y`, `g6_intcov > 5.0x`, Solvency II > 200% for insurers, automatic `N` for commercial fractional-reserve banks, regulated utilities with `g6_default = "N"`, and debt-funded buyback negative equity).
- Strip stale `"Downstream gates bypassed per waterfall."` sentences from `note` on these 121 rows, fix `CRM`'s stale `CAP = 10` text in `note` to match its deterministic `CAP = 5Y`, and append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`. Keep all Gate 1–4 scores (`1`, `2`, `3_*`, `3a`, `3b`, `3m`, `4_*`, `4`, `4n`) untouched.

### R3. Dashboard UI, Version Bump & Documentation
- In `screener/dashboard.py`: update the 6-Gate Waterfall Stepper (`openDrawer`) to display concrete gate values in stepper sub-labels when scored (e.g. `PASS · 25Y` / `FAIL · 10Y` on G4, `PASS · 2/2` / `PASS · 1/2` / `FAIL · 0/2` on G5, `PASS · Y` / `FAIL · N` on G6, preserving `WAIVED` styling on calamity waivers); add a 2-card row below Moat Archetype / Moat Runway (CAP) in the Qualitative Investment Thesis & Moat Analysis card grid showing `Management & Allocation (G5)` (`2/2 — Elite Compounder`, `1/2 — Standard Pass`, `0/2 — Red Flag`) and `Cash & Fortress B/S (G6)` (`Y — Pass`, `N — Fail`) whenever scored (populating `#dossier-g6-answer` with `Y` or `N`); add `g5_mgmt` (`G5 Mgmt`) and `g6_cash` (`G6 B/S`) to `ALL_COLS` in expanded table mode on Quality Grade and Full Universe while keeping default Compact Cols unchanged.
- In `screener/config.py`, bump `SCREENER_VERSION` from `"7.17"` to `"7.18"` and add the `"7.18"` `CHANGELOG` entry.
- Update waterfall rules and field nullable tables in `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` to reflect the Two-Stage Waterfall (Stage 1 early stop at Gates 1–3; Stage 2 full diagnostic scorecard across Gates 4–6).

### R4. Test Suite Alignment
- Update Gate 4 / Gate 5 waterfall scrubbing assertions and add Two-Stage Waterfall coverage in `tests/test_calamity_tier.py` (`test_gate4_failure_clears_calamity_and_downstream` verifying calamity is cleared while diagnostic `5` and `6` are preserved and `phase_results` still rejects at Gate 4) and `tests/test_bulk_scoring_e2e.py` (`test_t1_f7_04`, `test_t1_f7_05`, and `test_all_989_gate3_companies_completed` asserting all 485 Gate-3-advancing companies have valid non-empty `5` and `6` while all 504 Gate-3 rejects keep `4_*`, `4`, `4n`, `5`, `6` blank).

## Verification Resources
- `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`
- Local statement context: `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv` (`g6_default`, `g6_checks`), and existing `note` dossiers
- Audit script: `python3 screener/bulk_scorer.py --audit`
- Build script: `python3 build.py`
- Test suite: `python3 -m unittest discover -s tests`

## Acceptance Criteria

### Engine, Audit & Funnel Invariance
- [ ] `python3 screener/bulk_scorer.py --audit` passes with 0 discrepancies, 0 waterfall violations, and 100% dual-listed mirror parity.
- [ ] All 485 Gate-3-advancing companies have valid `5` in `{0, 1, 2}` and `6` in `{"Y", "N"}` (with existing `5 = 0` preserved on the 13 Gate-5 rejects), all 504 Gate-3 rejects keep `4_*`, `4`, `4n`, `5`, `6` blank, and all Gate 1–4 scores (`1`, `2`, `3_*`, `3a`, `3b`, `3m`, `4_*`, `4`, `4n`) remain unchanged.
- [ ] Each of the 121 newly completed rows has `"Downstream gates bypassed per waterfall."` removed from `note`, appends `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`, and `CRM`'s `note` reflects `CAP = 5Y`.

### Build, Dashboard, Docs & Tests
- [ ] `python3 build.py` exits cleanly and regenerates `output/screener.html`, `output/index.html`, and `docs/index.html` with Prime Grade (225) and Prime Grade Calamity (11 / 13) counts unchanged, `SCREENER_VERSION = "7.18"` and `"7.18"` `CHANGELOG` entry in `screener/config.py`, and Two-Stage Waterfall updates in `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`.
- [ ] `screener/dashboard.py` includes the scored sub-labels in `openDrawer`, the 2-card G5/G6 row below Moat Archetype / Moat Runway (CAP) (and `#dossier-g6-answer` population), and `g5_mgmt` / `g6_cash` in `ALL_COLS` with Compact Cols unchanged.
- [ ] `python3 -m unittest discover -s tests` passes 100% across all unit, parity, dashboard, and E2E tests.
