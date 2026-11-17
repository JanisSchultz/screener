# Handoff Report — v718_challenger_1

## Observation

1. **Test Suite & Audit**:
   - `python3 -m unittest discover -s tests` exited `0`: `Ran 319 tests in 24.061s` (`OK`).
   - `python3 screener/bulk_scorer.py --audit` exited `0`: `Gate 3 Populations: {'us': 445, 'eu': 495, 'ca': 49} | Total: 989 / 989`, `485 moat franchises: 0 missing/invalid`, `0` formula/moat/4n/waterfall/calamity violations, `Dual-Listed Mirror Parity: PASSED`.
2. **Dataset & Notes Invariants (`data/{us,eu,ca}/inputs.csv`)**:
   - Diffing `data/{us,eu,ca}/inputs.csv` against `HEAD` showed `121` modified rows and `0` changes (`[]`) to Gate 1–4 or calamity columns (`1, 2, 3_*, 3a, 3b, 3m, 4_*, 4, 4n, calamity, calamity_note`).
   - Across all `485` Gate-3-advancing companies (`g3_fail=504`, `g3_adv=485`), `0` rows contain `"Downstream gates bypassed per waterfall."`. Across the `121` newly completed rows (`108` G4 rejects + `13` non-calamity G5 rejects), `0` rows lack `[Diagnostic G5=...]` or mismatch their CSV `5`/`6` columns. `CRM` has `4=5`, `5=0`, `6=Y`, and `note` begins `"Fails Gate 4 (CAP = 5Y, REJECT)..."`.
3. **Engine Waterfall Edge Cases (`screener/apply_evaluation.py` & `screener/bulk_scorer.py`)**:
   - Stage 1 failures (`1="N"`, `2="N"`, `3a="None"`, unwaived `3b="N"`), Stage 2 `CAP < 15` + `calamity="Y"` (when `3b="Y"`), Stage 2 `5=0`, invalid `5`/`6` values (`-1, 3, True, False, "abc", 1.5, "1.5"`, `"Yes", "X", 1, 0, True, "y", "n", "N/A"`), and blank `5`/`6` warnings/audit failure (tested on a temporary copy of `data/`) all behaved per spec.
   - **Confirmed Bug**: In `screener/apply_evaluation.py:266-282` (`validate_and_waterfall`) and `screener/bulk_scorer.py:586-626` (`validate_company_evaluation`), submitting `1="Y", 2="Y", 3a="Toll booth & switching costs", 3b="N", calamity="Y", calamity_note="Temporary 3b dip", 4=10, 5=1, 6="Y"` cleared `calamity` and `calamity_note` on `CAP < 15` **without** re-applying the Stage 1 Gate 3b scrub. Running `ingest_evaluations` against a temporary copy of `data/` for `NVDA` returned `{'applied': 1, 'rejected': 0, 'errors': []}`, and immediately running `audit_gate_3_universe()` failed with `waterfall_violations: ["[NVDA] Failed Gate 3 but downstream keys ['4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6'] are not blank"]`.
   - Minor note: `apply_evaluation.py:226` checks `int(qual["4"])` without verifying integer equality for standalone floats like `15.5`, leaving `qual["4"] = 15.5` with 0 warnings.
4. **Built HTMLs & JavaScriptCore Runtime (`output/screener.html`, `output/index.html`, `docs/index.html`)**:
   - `cmp -s output/screener.html output/index.html && cmp -s output/screener.html docs/index.html` confirmed all three files are byte-identical (`5,879,842` bytes).
   - Embedded `screener-raw-data` JSON has `version: "7.18"`, `"7.18"` in `changelog`, `1175` total companies, `Prime Grade: 225`, `Calamity pass total: 13`, `passes_calamity_grade (<3 G6 flags): 11`, `Quality Grade: 443`, `Gate-3 advancing: 485` (`G4 rejects: 108, G5 rejects: 13`).
   - Executing the extracted controller JS from `output/screener.html` in `osascript -l JavaScript` with a DOM shim passed all checks across `openDrawer` (`COST`, `MSFT`, `EL`, `APD`, `DGE.GB`, `CRM`, `BA`, `NUE`), `renderTable` (compact vs. expanded across `qpass`, `calamity`, `moat_universe`, `all`), and `sortData` (`g5_mgmt`, `g6_cash`).

## Logic Chain

1. Every committed dataset invariant, build output (`output/*.html`, `docs/index.html`), dashboard JS runtime behavior (`openDrawer`, `renderTable`, `sortData`), and existing test suite (319 tests) passes empirically.
2. However, the Two-Stage Waterfall contract in `ORIGINAL_REQUEST.md` R1 requires strict downstream scrubbing whenever unwaived Gate 3 fails (`3b = "N"` without `calamity = "Y"`), and `audit_gate_3_universe()` enforces that invariant (`bulk_scorer.py:1064-1068`).
3. Because `CAP < 15` is a non-waivable Anchor Gate that clears `calamity = "Y"`, a company submitted with `3b = "N"` + `calamity = "Y"` + `CAP < 15` ends up with `3b = "N"` and `calamity = ""` — making Gate 3b unwaived — yet `validate_and_waterfall` and `validate_company_evaluation` never re-run the Stage 1 Gate 3b scrub after clearing `calamity`.
4. Empirical execution proves `ingest_evaluations` accepts this payload with `errors=[]` and writes a state that fails `audit_gate_3_universe()` with `waterfall_violations`. Therefore, the engine R1 state-machine implementation has a reproducible bug, yielding **Verdict: REJECT** until fixed.

## Caveats

- Only temporary test scripts (executed via stdin heredoc or `/tmp/test_jsc_v718.js`, subsequently removed) were run; no repository files were modified.
- Live headless browser CSS layout rendering was not tested; JS runtime behavior was verified in JavaScriptCore (`osascript -l JavaScript`) with a DOM mock covering all HTML element IDs.

## Conclusion

**Verdict: REJECT** (details in `.agents/teamwork/v718_challenger_1/challenge_report.md`).

- **Blocking item**: Fix the `3b="N"` + `calamity="Y"` + `CAP < 15` cascade in `screener/apply_evaluation.py` (`validate_and_waterfall`) and `screener/bulk_scorer.py` (`validate_company_evaluation`) so that if `clear_calamity` clears `calamity` on `CAP < 15` when `g3b == "N"`, the Stage 1 Gate 3b scrub (`*FORCE_SCORE_CODES, "4", "4n", "5", "6"`) is applied, and add a regression unit test.
- **Everything else verified clean**: Data (`989` Gate-3, `485` Stage 2, `121` completed rows, Gate 1–4 immutability), `--audit`, `319` unit/E2E tests, `output/*.html` & `docs/index.html` (`v7.18`), and JavaScriptCore `openDrawer`/`renderTable`/`sortData` runtime all pass.

## Verification Method

1. Run unit/E2E suite and audit:
   - `python3 -m unittest discover -s tests`
   - `python3 screener/bulk_scorer.py --audit`
2. Reproduce the `3b="N"` + `calamity="Y"` + `CAP < 15` bug (post-fix, assert `4`..`6` are `""` and `audit_gate_3_universe()["waterfall_violations"] == []`):
   - Call `validate_and_waterfall` and `validate_company_evaluation` with `{"id": "X", "qualitative": {"1": "Y", "2": "Y", "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs", "3b": "N", "4_sub": 2, "4": 10, "4n": "Fatal", "5": 1, "6": "Y", "calamity": "Y", "calamity_note": "temp"}}`.
3. Verify HTML parity and JS runtime:
   - `cmp -s output/screener.html output/index.html && cmp -s output/screener.html docs/index.html`
   - Execute `openDrawer` and `renderTable` in `osascript -l JavaScript` against `output/screener.html`.
