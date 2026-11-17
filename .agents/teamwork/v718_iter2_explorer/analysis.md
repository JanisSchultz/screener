# Analysis — Iteration 2 Engine Cascade Fix & Hygiene (`v718_iter2_explorer`)

## Core Findings
1. **Confirmed Stage 1 / Stage 2 Cascade Bug**: Both `screener/apply_evaluation.py` (`validate_and_waterfall`, lines 265–283) and `screener/bulk_scorer.py` (`validate_company_evaluation`, lines 586–626) evaluate Stage 1 (`3b == "N" and not calamity`) before Stage 2 (`CAP < 15` clearing `calamity`). When `3b="N"` + `calamity="Y"` + `CAP < 15`, clearing `calamity` leaves `3b="N"` unwaived without running the Stage 1 Gate 3b downstream scrub (`*FORCE_SCORE_CODES, "4", "4n", "5", "6"`), breaking the `ingest_evaluations` → `audit_gate_3_universe` invariant (`waterfall_violations`).
2. **Confirmed Standalone Gate 4 Float/Bool Bug**: `screener/apply_evaluation.py:224-232` uses `int(qual["4"]) in CAP_VALUES`, which silently accepts non-integer floats like `15.5` (`int(15.5) == 15`) and `False` (`int(False) == 0 in CAP_VALUES`).
3. **Confirmed Stray OneDrive Conflict Files**: `git status -s` shows two untracked conflict copies in `output/`: `"output/screener.html 2.html"` and `"output/screener.html 3.html"` (each `535949` bytes, vs `5879842` bytes for `output/screener.html`). No other `* [0-9].*` conflict files exist in the repo outside `.agents/` and `.git/`.

---

## Detailed Findings & Proposed Changes

### 1. Stage 1/Stage 2 Cascade (`3b="N"` + `calamity="Y"` + `CAP < 15`)

#### `screener/apply_evaluation.py` (`validate_and_waterfall`)
- **Location**: Lines 274–283
- **Observed behavior**:
  - Line 266 checks `if g3a == "None" or (g3b == "N" and not cal_active):` — skipped when `cal_active` is `True` and `g3a != "None"`.
  - Line 274 enters `elif g3a in MOAT_TYPES and g3a != "None" and (g3b == "Y" or (g3b == "N" and cal_active)):`.
  - Lines 279–280: when `g4_num < 15`, `clear_calamity(f"Gate 4 (CAP={g4_num}) < 15")` clears `qual["calamity"] = ""` and `qual["calamity_note"] = ""`.
  - `stage1_scrubbed` stays `False`, and `*g4_all_keys, "5", "6"` are never scrubbed, so lines 284–295 continue validating/preserving `"5"` and `"6"` alongside `3b == "N"` and `calamity == ""`.
- **Proposed fix** (`screener/apply_evaluation.py:279-280`):
  ```python
                            if g4_num < 15:
                                clear_calamity(f"Gate 4 (CAP={g4_num}) < 15")
                                if g3b == "N":
                                    for k in [*g4_all_keys, "5", "6"]:
                                        if sanitize_val(qual.get(k)) != "":
                                            warnings.append(
                                                f"Waterfall: scrubbed '{k}' because Gate 3b failed without calamity override (calamity cleared by Gate 4 CAP < 15)"
                                            )
                                        qual[k] = ""
                                    stage1_scrubbed = True
  ```
- **Why safe**:
  - When `g3b == "Y"` and `CAP < 15`, `g3b == "N"` is `False`: `calamity` is cleared and diagnostic `4_*`, `4`, `4n`, `5`, `6` remain preserved (preserving R1 and `test_stage2_gate4_under_15_preserves_g5_g6_and_clears_calamity`).
  - When `g3b == "N"` and `calamity == "Y"` and `CAP < 15`, clearing `calamity` makes `3b == "N"` unwaived, so Stage 1 Gate 3b scrub runs on `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]`, `stage1_scrubbed = True` skips lines 284–295, and `phase_results` returns `C.RES_REJ[3]`.

#### `screener/bulk_scorer.py` (`validate_company_evaluation`)
- **Location**: Lines 617–626
- **Observed behavior**:
  - Line 586 checks `g3_failed = (g3a == "None") or (g3b == "N" and not calamity_active)` — `False` when `g3b == "N"` and `calamity_active == True`.
  - Lines 622–623: when `g4_val < 15 and calamity_active`, `clear_keys(["calamity", "calamity_note"], ...)` clears calamity, then execution falls through to lines 627–669, preserving `4_*`, `4`, `4n`, `5`, `6`.
  - Subsequent `audit_gate_3_universe()` (lines 1064–1068) sees `g3b == "N"` and `not calamity_flag`, flagging all non-blank `(*FORCE_SCORE_CODES, "4", "4n", "5", "6")` as `waterfall_violations`.
- **Proposed fix** (`screener/bulk_scorer.py:622-624`):
  ```python
            if g4_val < 15 and calamity_active:
                clear_keys(["calamity", "calamity_note"], f"Gate 4 CAP ({g4_val}Y) < 15 (non-waivable anchor)")
                if g3b == "N":
                    clear_keys(
                        [*FORCE_SCORE_CODES, "4", "4n", "5", "6"],
                        "Gate 3b is 'N' without calamity override (calamity cleared by Gate 4 CAP < 15)",
                    )
                    return qual, warnings, errors
  ```
- **Why safe**:
  - Early `return qual, warnings, errors` also avoids spurious blank-`5`/`6` warnings or re-parsing `5`/`6` at lines 628–669, matching the early return at line 592 for Stage 1 Gate 3 failure.
  - Also works when `existing_row` had pre-existing `4_*`/`4`/`4n`/`5`/`6` values and an update triggers `CAP < 15` on a `3b="N"` + `calamity="Y"` row.

---

### 2. Standalone Gate 4 Float / Bool Check (`screener/apply_evaluation.py:224-232`)

- **Location**: `screener/apply_evaluation.py:224-232`
- **Observed behavior**:
  ```python
        if sanitize_val(qual.get("4")) != "":
            try:
                g4_chk = int(qual["4"])
                if g4_chk not in CAP_VALUES:
                    warnings.append(f"Invalid Gate 4 CAP '{qual['4']}' (allowed: {CAP_VALUES}); cleared.")
                    qual["4"] = ""
            except (ValueError, TypeError):
                ...
  ```
  - `qual["4"] = 15.5` yields `int(15.5) == 15 in CAP_VALUES`, keeping `qual["4"] = 15.5`.
  - `qual["4"] = False` yields `int(False) == 0 in CAP_VALUES` (`CAP_VALUES = [0, 5, 10, 15, 20, 25, 30]`), keeping `qual["4"] = False`.
- **Proposed fix** (`screener/apply_evaluation.py:224-233`):
  ```python
        if sanitize_val(qual.get("4")) != "":
            raw_4 = qual["4"]
            if isinstance(raw_4, bool):
                warnings.append(f"Invalid Gate 4 CAP '{raw_4}' (allowed: {CAP_VALUES}); cleared.")
                qual["4"] = ""
            else:
                try:
                    g4_chk = int(raw_4)
                    if g4_chk == float(raw_4) and g4_chk in CAP_VALUES:
                        qual["4"] = g4_chk
                    else:
                        warnings.append(f"Invalid Gate 4 CAP '{raw_4}' (allowed: {CAP_VALUES}); cleared.")
                        qual["4"] = ""
                except (ValueError, TypeError, OverflowError):
                    warnings.append(f"Invalid Gate 4 CAP '{raw_4}' (allowed: {CAP_VALUES}); cleared.")
                    qual["4"] = ""
  ```
- **Why safe**: Normalizes valid `"15"` / `15.0` / `15` to `int(15)` (every test in `tests/` asserts `int` on `qual["4"]`) while rejecting `bool`, `15.5`, `"15.5"`, `17`, etc.

---

### 3. Regression Test Placement (`tests/test_v718_two_stage_waterfall.py`)

- **Target class**: `WaterfallEngineValidationTests` (lines 71–235), right after `test_stage2_gate4_under_15_preserves_g5_g6_and_clears_calamity` (or right before `test_bulk_scorer_audit_and_reference_snapshot_clean` at line 202).
- **Recommended regression tests**:
  1. `test_gate3b_calamity_cleared_by_gate4_under_15_cascades_stage1_scrub`:
     - Tests both `validate_and_waterfall` and `validate_company_evaluation` on `3b="N"` + `calamity="Y"` + `CAP < 15` (via force scores producing `CAP=10`, and also standalone `CAP=10` without force scores), asserting `calamity == ""`, `calamity_note == ""`, all of `*C.FORCE_SCORE_CODES, "4", "4n", "5", "6"` are `""`, `errs == []`, and `phase_results(qual, self.p)["result"] == C.RES_REJ[3]`.
     - Also runs an isolated `ingest_evaluations` → `audit_gate_3_universe()` check against a temporary copy of `data/` (patching `bulk_scorer.DATA_DIR` in a `try/finally` block) for `NVDA` with `3b="N"`, `calamity="Y"`, `4_sub=2`, `5=1`, `6="Y"`, verifying `applied == 1`, `errors == []`, and `audit["waterfall_violations"] == []` / `audit["calamity_violations"] == []`.
  2. `test_standalone_gate4_rejects_bool_and_non_integer_float`:
     - Tests `validate_and_waterfall({"qualitative": {"gate_4_runway_cap": bad_4}})` for `bad_4 in (15.5, 10.2, True, False, "15.5", 17)`, asserting `qual.get("4", "") == ""` and an invalid Gate 4 CAP warning is emitted; also verifies `15.0` and `"15"` normalize cleanly to `15`.

---

### 4. Stray OneDrive Conflict Files (`git status -s`)

- `git status -s` reported:
  - `?? "output/screener.html 2.html"`
  - `?? "output/screener.html 3.html"`
- `ls -la output/screener.html*`:
  - `output/screener.html` — `5879842` bytes (`Nov 17 17:05`)
  - `output/screener.html 2.html` — `535949` bytes (`Nov 17 17:03`)
  - `output/screener.html 3.html` — `535949` bytes (`Nov 17 17:05`)
- `find . -maxdepth 3 -name "* [0-9].*" -not -path "./.agents/*" -not -path "./.git/*"` returned only those two files.
- **Action**: Remove both untracked conflict files (`rm "output/screener.html 2.html" "output/screener.html 3.html"`).
