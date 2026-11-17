# TEST_READY_V718 — v7.18 Two-Stage Munger Waterfall Test Suite

**Published by:** `v718_test_writer_r4` (`teamwork_test_writer`)
**Date (UTC):** 2026-11-17T16:45:00Z
**Command:** `python3 -m unittest discover -s tests`
**Current Suite Status:** **314 / 319 passing** (`5` failures — all 5 strictly await M2 bottom-up evaluation of the 121 incomplete moat franchises + `CRM` `REFERENCE_SNAPSHOT` update; R1 engine/audit, R3 UI/config/specs/build, and R4 test alignment all pass).

---

## 1. Test Files Created / Modified

| File | Change Type | Coverage |
|---|---|---|
| `tests/test_calamity_tier.py` | Modified | Updated `test_gate4_failure_clears_calamity_and_downstream` (`gate_3b_pricing_and_proof="Y"`, `calamity` cleared while `5` & `6` preserved, `phase_results` -> `C.RES_REJ[4]`); added `test_gate5_failure_without_calamity_preserves_gate6` (`C.RES_REJ[5]`). |
| `tests/test_bulk_scoring_e2e.py` | Modified | Updated `test_t1_f7_04_gate4_cap_under_15_clears_gates_5_and_6` (Gate 4 < 15 preserves `5` & `6` and clears calamity; Stage 1 G3b=`"N"` still scrubs), `test_t1_f7_05_gate5_failure_clears_gate_6_without_calamity` (preserves `6`), and `test_all_989_gate3_companies_completed` (485 advancing rows require valid non-empty `5`/`6`; 504 G3 rejects keep `4_*`, `4`, `4n`, `5`, `6` blank). |
| `tests/test_v718_two_stage_waterfall.py` | Created (15 tests) | Opaque-box v7.18 E2E suite covering R1 validation/audit, R2 funnel invariance & note hygiene, R3 dashboard UI + real JavaScriptCore DOM execution + `v7.18` config/build artifacts, and `QUALITATIVE_EVALUATION_SPEC.md` / `COMPANY_EVALUATION_SPEC.md` consistency. |

---

## 2. Current Verification Matrix (M1/R3 Complete vs. Awaiting M2)

### Passing Now (314 tests — M1 & R3 Verified)
- `tests/test_calamity_tier.py` (13/13 PASS)
- `tests/test_bulk_scoring_e2e.py` (133/134 PASS — including `test_t1_f7_04` and `test_t1_f7_05`)
- `tests/test_v718_two_stage_waterfall.py` (11/15 PASS):
  - `WaterfallEngineValidationTests`: `test_stage1_early_stop_scrubs_downstream_on_g1_g2_g3`, `test_stage2_gate4_under_15_preserves_g5_g6_and_clears_calamity`, `test_stage2_gate5_zero_without_calamity_preserves_g6`, `test_gate5_invalid_inputs_rejected_and_cleared`, `test_gate6_invalid_inputs_rejected_and_cleared`, `test_blank_g5_or_g6_past_gate3_triggers_warning_even_on_g4_or_g5_reject`
  - `FunnelAndScorecardInvarianceTests`: `test_funnel_and_prime_grade_invariance` (`1,175` total, `989` G3, `485` advancing [`483` `3b="Y"` + `APD`, `EL`], `504` G3 rejects, `225` Prime Grade, `13` total / `11` `<3` G6-flag Calamity, `0` `To review`, `thr_cap=15`)
  - `DashboardV718UITests`: `test_config_version_and_changelog_v718`, `test_dashboard_html_contains_v718_cards_and_table_columns`, `test_built_output_html_files_exist_and_match_v718`
  - `SpecConsistencyV718Tests`: `test_specs_document_v718_two_stage_waterfall`
- All other existing test modules (`test_cap_engine.py`, `test_dashboard_filters.py`, `test_quantitative_growth.py`, `test_valuation_sandbox.py`, `test_v71..v77*.py`): 100% PASS.

### Awaiting M2 Completion (5 tests — Expected Failures Until 121 Rows + `CRM` Snapshot Complete)
1. `test_all_989_gate3_companies_completed` (`tests/test_bulk_scoring_e2e.py`): fails on `APP advanced past Gate 3 but missing Gate 5` (121 incomplete moat franchises in `data/{us,eu}/inputs.csv`).
2. `test_bulk_scorer_audit_and_reference_snapshot_clean` (`tests/test_v718_two_stage_waterfall.py`): fails on `audit["stage2_discrepancies"]` (121 blank G5/G6 items) and awaits `CRM` `REFERENCE_SNAPSHOT` `5`/`6` update.
3. `test_all_485_advancing_have_complete_g5_g6_without_changing_rejections` (`tests/test_v718_two_stage_waterfall.py`): fails on `APP invalid/blank Gate 5: ''`.
4. `test_note_hygiene_across_all_121_newly_completed_rows` (`tests/test_v718_two_stage_waterfall.py`): fails on stale `"Downstream gates bypassed per waterfall."`, missing `[Diagnostic G5=<0|1|2> | G6=<Y|N>: ...]`, and `CRM` `CAP = 10` text.
5. `test_dashboard_runtime_js_openDrawer_and_renderTable_via_jsc` (`tests/test_v718_two_stage_waterfall.py`): fails on `AssertionError: 'blank' not found in ('Y', 'N')` for `BA` (`#dossier-g6-answer`), because `BA` Gate 6 is currently blank pending M2 (note: `BA`'s `FAIL · 0/2` / `Red Flag` JS rendering already passed!).

---

## 3. Sign-off Criterion for Final Gate
Once M2 completes (121 rows scored, notes cleaned, `CRM` `REFERENCE_SNAPSHOT` updated, and `python3 build.py` re-run), `python3 -m unittest discover -s tests` must report **319 / 319 OK** (`returncode == 0`).
