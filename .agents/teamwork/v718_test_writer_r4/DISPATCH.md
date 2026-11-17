# Dispatch — v718_test_writer_r4 (R4: Test Suite Alignment & Opaque-Box v7.18 E2E Tests)

## 2026-11-17T15:42:00Z
Assigned Role: `teamwork_test_writer` (R4 Test Alignment & Opaque-Box E2E Suite)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Survey Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_test_writer_r4`

## Exclusive File Ownership
Modify/Create ONLY:
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/tests/test_calamity_tier.py`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/tests/test_bulk_scoring_e2e.py`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/tests/test_v718_two_stage_waterfall.py` (new opaque-box E2E test suite)
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/TEST_READY_V718.md`

DO NOT modify `screener/`, `data/`, `build.py`, or `*.md` spec files at project root.

## Exact Requirements (R4 + Opaque-Box E2E)
1. **`tests/test_calamity_tier.py`**:
   - Update `test_gate4_failure_clears_calamity_and_downstream`:
     - Verify `calamity` and `calamity_note` are cleared on Gate 4 `CAP < 15`, while diagnostic `5` and `6` are preserved!
     - CRITICAL: The existing test fixture sets `gate_3b_pricing_and_proof = "N"` alongside `gate_4_runway_cap = 10`; update `gate_3b_pricing_and_proof = "Y"` (and `gate_6_cash_and_balance_sheet = "N"` waived by `calamity_flag = "Y"`) so that after Gate 4 clears calamity, `phase_results(qual, params({}))` genuinely rejects at Gate 4 (`C.RES_REJ[4]`).
   - Add a Gate 5 = `0` without-calamity test verifying diagnostic `6` is preserved while `phase_results` rejects at Gate 5 (`C.RES_REJ[5]`).
2. **`tests/test_bulk_scoring_e2e.py`**:
   - Update `test_t1_f7_04_gate4_cap_under_15_clears_gates_5_and_6` (keep test name or update docstring/assertions cleanly so `t1_f7_04` verifies Gate 4 `< 15` preserves `5` and `6` while clearing calamity, and Stage 1 G1–G3 still scrubs downstream).
   - Update `test_t1_f7_05_gate5_failure_clears_gate_6_without_calamity` (verify `5 = 0` without calamity preserves `6`).
   - Update `test_all_989_gate3_companies_completed` so all 485 Gate-3-advancing companies (`not fails_g3`) have valid non-empty `5` in `{0, 1, 2}` and `6` in `{"Y", "N"}`, while all 504 Gate-3 rejects (`fails_g3`) keep `4_*`, `4`, `4n`, `5`, `6` strictly blank `""`.
3. **`tests/test_v718_two_stage_waterfall.py`** (New Opaque-Box E2E Tests derived from `ORIGINAL_REQUEST.md`):
   - Funnel & Prime Grade invariance: `1,175` total, `989` Gate 3, `485` Gate-3 advancing (`483` `3b="Y"` + `EL` + `APD`), `504` Gate-3 rejects, `225` Prime Grade, `13` total / `11` `<3` G6-flag Prime Grade Calamity, `0` `To review`, `thr_cap = 15`.
   - Note hygiene across all 121 newly completed rows: zero occurrences of `"Downstream gates bypassed per waterfall."` or variants (`Gates 5-6`, `strict waterfall`, `Gate 6`), `[Diagnostic G5=<0|1|2> | G6=<Y|N>: ...]` present, `CRM` note reflects `CAP = 5Y` (no stale `CAP = 10`).
   - Validation tests for `5` (`0/1/2`) and `6` (`Y/N`) invalid inputs and blank warnings past Gate 3.
   - Dashboard v7.18 UI checks (`SCREENER_VERSION == "7.18"`, `"7.18"` in `CHANGELOG`, `openDrawer` scored sub-labels including `0/2` handling, 2-card `#dossier-g5-mgmt` / `#dossier-g6-cash` / `#dossier-g6-answer`, `g5_mgmt` / `g6_cash` in `ALL_COLS` and expanded `moat_universe`/`all` views while `compactKeys` / `qpass` / `calamity` unchanged).
   - Spec consistency checks for `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` (`v7.18` & Two-Stage Waterfall).
4. Publish `.agents/teamwork/TEST_READY_V718.md`.

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Tests must genuinely exercise the real implementation and real datasets without mocking away failures or hardcoding pass conditions.

## Verification & Deliverables
Run `python3 -m unittest discover -s tests` (note clearly in `handoff.md` and `TEST_READY_V718.md` which tests already pass vs which tests await M1/M2/M3 completion).
Write `progress.md`, `changes.md`, and `handoff.md` in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_test_writer_r4`, and notify `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
