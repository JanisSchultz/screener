# Handoff Report — Iteration 2 Engine Cascade Fix Investigation (`v718_iter2_explorer`)

## 1. Observation
1. **`screener/apply_evaluation.py` (`validate_and_waterfall`, lines 265–296)**:
   - Line 266 evaluates `if g3a == "None" or (g3b == "N" and not cal_active):` before Stage 2.
   - Line 274 enters `elif g3a in MOAT_TYPES and g3a != "None" and (g3b == "Y" or (g3b == "N" and cal_active)):`.
   - Lines 279–280 execute `if g4_num < 15: clear_calamity(f"Gate 4 (CAP={g4_num}) < 15")`, clearing `qual["calamity"] = ""` and `qual["calamity_note"] = ""`, without re-checking `g3b == "N"` or scrubbing `[*g4_all_keys, "5", "6"]` or setting `stage1_scrubbed = True`.
2. **`screener/bulk_scorer.py` (`validate_company_evaluation`, lines 586–626)**:
   - Line 586 evaluates `g3_failed = (g3a == "None") or (g3b == "N" and not calamity_active)` and returns early at line 592 only if `g3_failed` is `True`.
   - Lines 622–623 execute `if g4_val < 15 and calamity_active: clear_keys(["calamity", "calamity_note"], ...)`, without scrubbing `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]` or returning when `g3b == "N"`.
   - `audit_gate_3_universe` (`screener/bulk_scorer.py:1064-1068`) checks `if g3a == "None" or (g3b == "N" and not calamity_flag):` and appends `waterfall_violations` if any key in `(*FORCE_SCORE_CODES, "4", "4n", "5", "6")` is non-blank.
3. **`screener/apply_evaluation.py` (lines 224–232)**:
   - Uses `g4_chk = int(qual["4"])` and `if g4_chk not in CAP_VALUES:`. Because `CAP_VALUES = [0, 5, 10, 15, 20, 25, 30]` (`screener/config.py:68`), `15.5` yields `int(15.5) == 15 in CAP_VALUES` and `False` yields `int(False) == 0 in CAP_VALUES`.
4. **`tests/test_v718_two_stage_waterfall.py` (lines 71–235)**:
   - Contains `WaterfallEngineValidationTests` covering Stage 1 scrubbing, Stage 2 `CAP < 15` with `3b="Y"`, `5=0`, invalid `5`/`6`, blank `5`/`6` warnings, and `--audit`.
5. **`git status -s` and `output/`**:
   - `git status -s` lists two untracked conflict files: `?? "output/screener.html 2.html"` and `?? "output/screener.html 3.html"`.
   - `ls -la output/screener.html*` shows both are `535949` bytes (`Nov 17 17:03` and `17:05`), while `output/screener.html` is `5879842` bytes (`Nov 17 17:05`).
   - `find . -maxdepth 3 -name "* [0-9].*" -not -path "./.agents/*" -not -path "./.git/*"` returned only those two files.

## 2. Logic Chain
1. From Observations 1–2, when a payload supplies `1="Y"`, `2="Y"`, valid `3a != "None"`, `3b="N"`, `calamity="Y"`, `calamity_note="..."`, and `CAP < 15` (plus `5`/`6`), `calamity` is cleared at Gate 4 (`CAP < 15`), leaving `3b="N"` unwaived. Because Stage 1 is never re-evaluated after `calamity` is cleared, `4_*`, `4`, `4n`, `5`, `6` remain populated, violating `audit_gate_3_universe` (`waterfall_violations`) and `ORIGINAL_REQUEST.md` R1.
2. Re-running the Stage 1 Gate 3b scrub (`[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]`) immediately after `CAP < 15` clears `calamity` whenever `g3b == "N"` restores the Stage 1/Stage 2 invariant in both `validate_and_waterfall` and `validate_company_evaluation` without affecting `3b == "Y"` rows (`CAP < 15` with `3b == "Y"` still clears `calamity` and preserves `4_*`, `4`, `4n`, `5`, `6`).
3. From Observation 3, checking `not isinstance(raw_4, bool)` and `int(raw_4) == float(raw_4)` (and normalizing valid `raw_4` to `int`) eliminates silent acceptance of `15.5` and `False` while preserving existing test expectations that `qual["4"]` is an `int`.
4. From Observation 4, `WaterfallEngineValidationTests` in `tests/test_v718_two_stage_waterfall.py` is the natural home for both regression tests (including an isolated `ingest_evaluations` → `audit_gate_3_universe` test).
5. From Observation 5, `"output/screener.html 2.html"` and `"output/screener.html 3.html"` are stale OneDrive sync conflict copies that should be removed.

## 3. Caveats
- Read-only investigation: no files were modified and no tests were executed after proposing the patch.
- In `screener/bulk_scorer.py:613-615`, if an input has `3b="N"`, `calamity="Y"`, force score `>= 1` yielding `CAP < 15`, AND omits `"4n"`, an error for missing `"4n"` is appended before line 622 clears `4n`. That is acceptable (invalid input missing mandatory `4n`), and normal payloads include `4n`.

## 4. Conclusion
Ready for targeted Iteration 2 implementation (see exact code snippets in `.agents/teamwork/v718_iter2_explorer/analysis.md`):
1. Patch `screener/apply_evaluation.py:224-232` (reject `bool` and non-integer float on standalone `4`) and `279-280` (scrub `[*g4_all_keys, "5", "6"]` and set `stage1_scrubbed = True` when `CAP < 15` clears calamity and `g3b == "N"`).
2. Patch `screener/bulk_scorer.py:622-624` (scrub `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]` and return early when `CAP < 15` clears calamity and `g3b == "N"`).
3. Add regression tests for both fixes in `tests/test_v718_two_stage_waterfall.py` (`WaterfallEngineValidationTests`).
4. Delete `"output/screener.html 2.html"` and `"output/screener.html 3.html"`.

## 5. Verification Method
After applying the fixes:
1. Run `python3 -m unittest tests.test_v718_two_stage_waterfall -v` and `python3 -m unittest discover -s tests`.
2. Run `python3 screener/bulk_scorer.py --audit` (must exit 0 with 0 discrepancies / 0 waterfall violations).
3. Run `git status -s` to confirm `"output/screener.html 2.html"` and `"output/screener.html 3.html"` are gone (and rebuild if needed with `python3 build.py` without leaving OneDrive conflict files).
4. **Invalidation conditions**: Any failure in `test_calamity_tier.py`, `test_bulk_scoring_e2e.py`, or `test_v718_two_stage_waterfall.py`, or non-zero `waterfall_violations` after `ingest_evaluations` on a `3b="N"` + `calamity="Y"` + `CAP < 15` payload.
