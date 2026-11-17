# Iteration 2 Challenge Report — v7.18 Engine Cascade & Parity (`v718_iter2_challenger_1`)

## Challenge Summary

**Verdict**: **APPROVE**  
**Overall risk assessment**: **LOW**

Both defects identified in Iteration 1 (`v718_challenger_1/challenge_report.md`) are **confirmed fixed empirically** in `screener/apply_evaluation.py` (`validate_and_waterfall`) and `screener/bulk_scorer.py` (`validate_company_evaluation`). Re-running the exact `3b="N" + calamity="Y" + CAP < 15` attack scenario (both force-computed and standalone CAP, as well as partial updates on real calamity company `EL`, `apply_evaluation` end-to-end on `NVDA`, and isolated `ingest_evaluations` → `audit_gate_3_universe()`) cleanly clears `calamity`/`calamity_note`, scrubs all downstream keys (`4_ent..4_sub, 4, 4n, 5, 6`), emits zero errors, and yields `waterfall_violations == []`, `stage2_discrepancies == []`, and `calamity_violations == []`.

Standalone Gate 4 (`"4"`) validation rejects `15.5`, `"15.5"`, `False`, `True`, `"10.0"`, `inf`, `nan`, `-5`, `99`, and `"abc"` with warnings/cleared values, and normalizes `10.0`, `10`, `"10"` to `int` `10`. `python3 screener/bulk_scorer.py --audit` passes (`989/989`, `485` Stage 2 moat franchises, `0` violations/discrepancies), `python3 -m unittest discover -s tests` passes (`321/321 OK`), `output/` contains zero stray `output/screener.html [0-9].html` conflict copies, and `output/screener.html`, `output/index.html`, and `docs/index.html` are 100% byte-identical.

*(Operational note only: during `unittest`, `test_bulk_scoring_e2e.py` executes `build.py ca` followed by `build.py`, which caused the OneDrive sync daemon to create an untracked conflict artifact `docs/index.html 2.html` at `17:15:42` that did not exist prior to the test run. Because this challenger is strictly read-only on repository files, `docs/index.html 2.html` was left untouched for orchestrator cleanup.)*

---

## Challenges & Empirical Re-Tests

### [Resolved] Iteration 1 Challenge 1 — `3b="N" + calamity="Y" + CAP < 15` Cascade

- **Assumption re-tested**: Clearing `calamity`/`calamity_note` on Gate 4 `CAP < 15` (non-waivable anchor) must re-trigger the Stage 1 Gate 3b downstream scrub across both `apply_evaluation.validate_and_waterfall` and `bulk_scorer.validate_company_evaluation`, as well as end-to-end `ingest_evaluations` → `audit_gate_3_universe()`.
- **Empirical attacks executed**:
  1. `validate_and_waterfall` (`screener/apply_evaluation.py:281-297`) with `3b="N"`, `calamity="Y"`, `5=1`, `6="Y"`, both force-computed (`4_sub=2` → `CAP=10`) and standalone (`4=10`, `4=5`, `4=0`): cleared `calamity`, `calamity_note`, and scrubbed `4_ent..4_sub`, `4`, `4n`, `5`, `6` to `""`. Exact boundary `4=15` and `4=20` preserved `calamity="Y"`, `4`, `5`, `6`.
  2. `validate_company_evaluation` (`screener/bulk_scorer.py:617-632`) with the same payloads, plus invalid `5=99, 6="Maybe"`: returned `errors == []`, cleared `calamity`/`calamity_note`, and scrubbed `4_ent..4_sub, 4, 4n, 5, 6` cleanly without spurious blank-G5/G6 warnings or invalid-G5/G6 errors.
  3. Isolated temp-dir `ingest_evaluations` → `audit_gate_3_universe()` on `NVDA` (`3b="N"`, `calamity="Y"`, `4_sub=2` → `CAP=10`, `5=1`, `6="Y"`): `applied=1, rejected=0, errors=[]`, `waterfall_violations=[]`, `stage2_discrepancies=[]`, `calamity_violations=[]`, `stage2_advancing_count=484`.
  4. Isolated temp-dir partial update on real calamity row `EL` (`3b="N"`, `calamity="Y"` in `data/us/inputs.csv`) supplying only `4_sub=2` + `4n`: `existing_row` fallback + cascade cleared `calamity`/`calamity_note` and scrubbed `4_ent..4_sub, 4, 4n, 5, 6` in temp `inputs.csv` with `0` audit violations.
  5. Isolated temp-dir `apply_evaluation` on `NVDA` → `audit_gate_3_universe()`: returned `True`, `0` audit violations.

### [Resolved] Iteration 1 Challenge 2 — Standalone Gate 4 Float / Bool Inputs

- **Assumption re-tested**: `apply_evaluation.validate_and_waterfall` (`screener/apply_evaluation.py:224-239`) must reject `bool` (`True`/`False`) and non-integer floats (`15.5`, `"15.5"`, `"10.0"`, `inf`, `nan`) while normalizing valid integers/whole floats (`10`, `10.0`, `"10"`) to `int`.
- **Empirical results**: All invalid values (`15.5`, `"15.5"`, `False`, `True`, `"10.0"`, `float("inf")`, `float("nan")`, `-5`, `99`, `"abc"`) were cleared to `""` with explicit `Invalid Gate 4 CAP ... cleared.` warnings; `10.0`, `10`, `"10"` all normalized to `int` `10` with zero warnings. `bulk_scorer.validate_company_evaluation` also rejected `15.5`, `"15.5"`, `False`, `True`, `"abc"` with errors.

### [Low / Informational] Pre-Existing Whitespace Handling in `apply_evaluation.validate_and_waterfall`

- **Observation**: Passing unstripped `"3b": "N "` to `apply_evaluation.validate_and_waterfall` fails to match `g3b == "N"` at `screener/apply_evaluation.py:245,273,288` (unlike `bulk_scorer.py:564`, which applies `sanitize_val`).
- **Assessment**: Non-blocking pre-existing behavior (canonical payloads supply `"Y"`/`"N"`), noted for completeness; does not affect any Iteration 2 acceptance criteria.

---

## Stress Test Results

| Area | Scenario | Expected | Actual | Result |
|---|---|---|---|---|
| `3b="N" + calamity="Y" + CAP < 15` (Unit) | Force-computed (`CAP=10`) & standalone (`CAP=0,5,10`) in `validate_and_waterfall` & `validate_company_evaluation` | Clear `calamity`/`calamity_note`; scrub `4_*`, `4`, `4n`, `5`, `6`; `errors=[]` | All downstream keys `""`, `calamity=""`, `errors=[]`; `CAP=15,20` preserved | **PASS** |
| `3b="N" + calamity="Y" + CAP < 15` (E2E) | Isolated temp `ingest_evaluations` (`NVDA` full + `EL` partial) & `apply_evaluation` → `audit_gate_3_universe()` | `applied=1, errors=[]`, `waterfall_violations=[]`, `stage2_discrepancies=[]`, `calamity_violations=[]` | Exact match (`0` violations across all audit buckets) | **PASS** |
| `3b="Y" + calamity="Y" + CAP < 15` | `3b="Y"`, `calamity="Y"`, `4_sub=2` (`CAP=10`), `5=2`, `6="Y"` across `validate_and_waterfall`, `validate_company_evaluation`, isolated `ingest_evaluations` → `audit_gate_3_universe()` | Clear `calamity`/`calamity_note`; preserve `4_*`, `4=10`, `4n`, `5=2`, `6="Y"`; `RES_REJ[4]`; `0` audit violations | Exact match (`1` applied, `0` errors, `0` audit violations, `RES_REJ[4]`) | **PASS** |
| Standalone `"4"` Validation | `15.5`, `"15.5"`, `False`, `True`, `10.0`, `10`, `"10"`, `"10.0"`, `inf`, `nan`, `-5`, `99`, `"abc"` | Reject/clear non-int/bool/out-of-domain; normalize `10`/`10.0`/`"10"` to `int` `10` | All 13 cases matched expected outputs and types | **PASS** |
| Built HTML Parity & `output/` Hygiene | `git status -s` + `cmp -s output/screener.html output/index.html && cmp -s output/screener.html docs/index.html` | Zero `output/screener.html [0-9].html` conflict copies; byte-identical HTMLs | Zero conflict copies in `output/`; all 3 HTMLs byte-identical (`5,879,842` B). *(Note: OneDrive created untracked `docs/index.html 2.html` during `unittest` `build.py` run)* | **PASS** |
| Comprehensive Bulk Audit | `python3 screener/bulk_scorer.py --audit` | Exit 0, `989/989`, `485` Stage 2, `0` discrepancies/violations, mirror parity | Exit 0, `989/989`, `485 moat franchises`, `0` violations/discrepancies, `PASSED` | **PASS** |
| Full Test Suite | `python3 -m unittest discover -s tests` | All 321 tests pass | `Ran 321 tests in 44.447s — OK` | **PASS** |

---

## Unchallenged Areas

- Live headless browser CSS layout/responsiveness (covered at JS controller level via JavaScriptCore in `tests/test_v718_two_stage_waterfall.py`).
