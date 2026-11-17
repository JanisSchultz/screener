# Changes — `v718_iter2_worker`

## Modified Files
1. **`screener/apply_evaluation.py`** (`validate_and_waterfall`):
   - **Lines 223–239**: Replaced naive `int(qual["4"]) in CAP_VALUES` check with explicit `isinstance(raw_4, bool)` rejection, `int(raw_4) == float(raw_4) and g4_chk in CAP_VALUES` validation, `OverflowError` handling, and `int` normalization (`qual["4"] = g4_chk`). Rejects `15.5`, `"15.5"`, `True`, `False`, `17`, etc., clearing `qual["4"] = ""` with a warning while normalizing `"15"` / `15.0` / `15` to `15`.
   - **Lines 274–291**: In the Stage 2 `g4_num < 15` branch after `clear_calamity(...)`, added `if g3b == "N":` to scrub `[*g4_all_keys, "5", "6"]` with explicit warnings and set `stage1_scrubbed = True` so Gate 5/6 validation is skipped for the now-unwaived Gate 3 failure. Rows with `g3b == "Y"` continue to preserve diagnostic `4_*`, `4`, `4n`, `5`, `6`.

2. **`screener/bulk_scorer.py`** (`validate_company_evaluation`):
   - **Lines 622–629**: When `g4_val < 15 and calamity_active` clears `["calamity", "calamity_note"]`, added `if g3b == "N":` to call `clear_keys([*FORCE_SCORE_CODES, "4", "4n", "5", "6"], ...)` and return early `return qual, warnings, errors`, preventing orphaned Stage 2 fields and avoiding spurious blank-G5/G6 warnings. Rows with `g3b == "Y"` continue to preserve `4_*`, `4`, `4n`, `5`, `6`.

3. **`tests/test_v718_two_stage_waterfall.py`** (`WaterfallEngineValidationTests`):
   - **Lines 24–33**: Imported `screener.bulk_scorer as bulk_scorer` and `ingest_evaluations`.
   - **Lines 204–302**:
     - Added `test_gate3b_calamity_cleared_by_gate4_under_15_cascades_stage1_scrub` verifying both force-computed (`CAP=10`) and standalone (`CAP=10`) payloads with `3b="N"` + `calamity="Y"` clear calamity and scrub `(*FORCE_SCORE_CODES, "4", "4n", "5", "6")` in `validate_and_waterfall` and `validate_company_evaluation`, return `C.RES_REJ[3]` from `phase_results`, and produce `0` `waterfall_violations`, `0` `calamity_violations`, and `0` `stage2_discrepancies` through an isolated temp `ingest_evaluations` -> `audit_gate_3_universe` run.
     - Added `test_standalone_gate4_rejects_bool_and_non_integer_float` verifying `(15.5, 10.2, True, False, "15.5", 17)` are cleared with warnings and `(15, 15.0, "15", 0, "0")` normalize cleanly to `int`.

## Cleanup & Rebuild
- Removed untracked OneDrive sync conflict files `"output/screener.html 2.html"` and `"output/screener.html 3.html"`.
- Re-ran `python3 build.py` cleanly (`1175` total, `225` Prime Grade, `11` Prime Grade Calamity; no stray conflict copies created).
