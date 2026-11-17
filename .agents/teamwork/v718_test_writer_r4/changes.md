# Changes — v718_test_writer_r4

## Files Modified
1. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/tests/test_calamity_tier.py`
   - Updated `ApplyEvaluationWaterfallTests.test_gate4_failure_clears_calamity_and_downstream` to set `gate_3b_pricing_and_proof="Y"` (and `gate_6_cash_and_balance_sheet="N"` waived by `calamity_flag="Y"`), assert `qual["4"] == 10`, diagnostic `qual["5"] == 1` and `qual["6"] == "N"` preserved, `calamity`/`calamity_note` cleared, and `phase_results(qual, params({}))["result"] == C.RES_REJ[4]`.
   - Added `ApplyEvaluationWaterfallTests.test_gate5_failure_without_calamity_preserves_gate6` verifying `5 = 0` without calamity preserves diagnostic `6` (`"Y"` and `"N"`) while `phase_results` rejects at Gate 5 (`C.RES_REJ[5]`).

2. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/tests/test_bulk_scoring_e2e.py`
   - Updated `Tier1FeatureCoverageTests.test_t1_f7_04_gate4_cap_under_15_clears_gates_5_and_6` to assert Gate 4 `CAP < 15` preserves diagnostic `5` and `6`, clears `calamity`/`calamity_note`, rejects at Gate 4 (`C.RES_REJ[4]`), and confirmed Stage 1 (`3b="N"` without calamity) still scrubs `4_*`, `4`, `4n`, `5`, `6`.
   - Updated `Tier1FeatureCoverageTests.test_t1_f7_05_gate5_failure_clears_gate_6_without_calamity` to assert `5 = 0` without calamity preserves diagnostic `6` and rejects at Gate 5 (`C.RES_REJ[5]`).
   - Updated `HelperAndRegressionTests.test_all_989_gate3_companies_completed` so all 485 Gate-3-advancing companies (`not fails_g3`) require valid non-empty `5` in `{0, 1, 2}` and `6` in `{"Y", "N"}` (and `calamity != "Y"` when `CAP < 15`), while all 504 Gate-3 rejects (`fails_g3`) keep `4_*`, `4`, `4n`, `5`, `6` strictly blank `""`.

## Files Created
3. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/tests/test_v718_two_stage_waterfall.py`
   - `WaterfallEngineValidationTests` (7 tests): Stage 1 scrubbing, Stage 2 G4/G5 preservation across `apply_evaluation` and `bulk_scorer`, invalid `5`/`6` rejection & clearing, blank `5`/`6` warnings past Gate 3, `audit_gate_3_universe()` + CLI `--audit` + `REFERENCE_SNAPSHOT` checks.
   - `FunnelAndScorecardInvarianceTests` (3 tests): `1,175` total, `989` Gate 3, `485` advancing (`483` `3b="Y"` + `APD`, `EL`), `504` G3 rejects, `225` Prime Grade, `13` total / `11` `<3` G6-flag Calamity, `0` `To review`, `thr_cap=15`; complete G5/G6 scorecard across all 485 advancing rows without altering the 108 G4 rejects or 13 G5 rejects; note hygiene across all 121 newly completed rows (no `"Downstream gates bypassed..."` variants, matching `[Diagnostic G5=<0|1|2> | G6=<Y|N>: ...]`, `CRM` `CAP = 5Y` with no stale `CAP = 10`).
   - `DashboardV718UITests` (4 tests): `SCREENER_VERSION == "7.18"`, `"7.18"` in `CHANGELOG`, HTML/JS UI tokens & column invariants (`qpass`, `calamity`, `compactKeys`), JavaScriptCore (`osascript -l JavaScript`) runtime verification of `openDrawer` (including `0/2` falsy-zero guard) and `renderTable` across `COST`, `BA`, `CRM`, `EL`, `NUE`, and built artifact checks (`output/screener.html`, `output/index.html`, `docs/index.html`).
   - `SpecConsistencyV718Tests` (1 test): `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` `v7.18` & Two-Stage Waterfall checks.

4. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/TEST_READY_V718.md`
   - Published test readiness summary and M1/M2/R3 status breakdown.
