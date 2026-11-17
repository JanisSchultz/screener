# Dispatch — v718_sub_orch_e2e_tests (E2E Testing & R4 Test Suite Alignment Track)

## 2026-11-17T15:40:00Z
Assigned Role: Sub-orchestrator (`teamwork_orchestrator`) for **E2E Testing Track & R4 Test Alignment**
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read and pass path to all subagents): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Project Plan: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT_V718.md`
Survey Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_sub_orch_e2e_tests`

## Exclusive Write Ownership
You own ONLY:
- `tests/test_calamity_tier.py`
- `tests/test_bulk_scoring_e2e.py`
- `tests/test_v718_two_stage_waterfall.py` (new opaque-box v7.18 E2E test suite)
- `.agents/teamwork/TEST_READY_V718.md`

DO NOT modify `screener/`, `data/`, `build.py`, or `*.md` spec files at project root.

## Scope (R4 + Opaque-Box E2E Test Suite)
1. **`tests/test_calamity_tier.py`**:
   - Update `test_gate4_failure_clears_calamity_and_downstream` (around line 126): remember the Survey finding that the existing fixture passes `gate_3b_pricing_and_proof = "N"` alongside `gate_4_runway_cap = 10`! Update `gate_3b_pricing_and_proof` to `"Y"` (with `gate_6_cash_and_balance_sheet = "N"` waived by `calamity_flag = "Y"`) so that after Gate 4 clears calamity, `phase_results` genuinely rejects at Gate 4 (`C.RES_REJ[4]`), while diagnostic `qual["5"]` and `qual["6"]` are preserved.
   - Add coverage for Gate 5 = `0` without calamity preserving diagnostic `qual["6"]` while `phase_results` rejects at Gate 5 (`C.RES_REJ[5]`).
2. **`tests/test_bulk_scoring_e2e.py`**:
   - Update `test_t1_f7_04_gate4_cap_under_15_clears_gates_5_and_6` (or rename/keep name per R4: `test_t1_f7_04`, verify `qual["5"] == 1`, `qual["6"] == "Y"` preserved on `CAP < 15`, and Stage 1 G1–G3 still scrubbed).
   - Update `test_t1_f7_05_gate5_failure_clears_gate_6_without_calamity` (`test_t1_f7_05`, verify `qual["5"] == 0` without calamity preserves `qual["6"] == "Y"`).
   - Update `test_all_989_gate3_companies_completed` so all 485 Gate-3-advancing companies (`not fails_g3`) have valid non-empty `5` in `{0, 1, 2}` and `6` in `{"Y", "N"}`, while all 504 Gate-3 rejects (`fails_g3`) keep `4_*`, `4`, `4n`, `5`, `6` strictly blank `""`.
3. **`tests/test_v718_two_stage_waterfall.py` (New Opaque-Box E2E Tests)**:
   - Derive comprehensive opaque-box tests from `ORIGINAL_REQUEST.md` covering:
     - Funnel invariance: `1,175` total, `989` Gate 3, `485` Gate-3 advancing (`483` `3b="Y"` + `EL`, `APD`), `504` Gate-3 rejects, `225` Prime Grade, `13` total / `11` `<3` G6-flag Prime Grade Calamity, `0` `To review`, `thr_cap = 15`.
     - Note hygiene on all 121 completed Stage-2 rows (no `"Downstream gates bypassed per waterfall."` or variants; presence of `[Diagnostic G5=<0|1|2> | G6=<Y|N>: ...]`; `CRM` note does not claim `CAP = 10`).
     - Validation errors/warnings on invalid `5` / `6` in `validate_and_waterfall` and `validate_company_evaluation`.
     - Dashboard UI v7.18 assertions (`SCREENER_VERSION == "7.18"`, `"7.18"` in `CHANGELOG`, `openDrawer` scored sub-labels including `0/2` handling, `#dossier-g5-mgmt` / `#dossier-g6-cash` / `#dossier-g6-answer`, `g5_mgmt` / `g6_cash` in `ALL_COLS` and expanded `moat_universe`/`all`, while `compactKeys` / `qpass` / `calamity` unchanged).
     - Spec doc consistency checks (`QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`).
4. Publish `.agents/teamwork/TEST_READY_V718.md`.

## Execution & Gate Requirements
Use `teamwork_test_writer` / `teamwork_explorer` / `teamwork_reviewer` / `teamwork_challenger` / `teamwork_auditor` to write and review the test suite against `ORIGINAL_REQUEST.md`. Note that while M1/M2/M3 are still in progress, some E2E tests checking live `data/` or `dashboard.py` won't pass until M4 runs the integrated suite — verify test syntax, test discovery (`unittest`), and mocked/unit tests pass cleanly, and explicitly document in `TEST_READY_V718.md` which tests depend on M1/M2/M3 completion.
Write `BRIEFING.md`, `progress.md`, `GATE_STATUS.md`, and `handoff.md` in your working directory, and report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
