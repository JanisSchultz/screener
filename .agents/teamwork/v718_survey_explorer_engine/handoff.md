# Handoff Report — v7.18 Survey Explorer (Engine, UI, Config & Tests)

## 1. Observation

- **Baseline Commands Executed (2026-11-17):**
  - `python3 screener/bulk_scorer.py --audit` exited `0`:
    - `Gate 3 Populations: {'us': 445, 'eu': 495, 'ca': 49} | Total: 989 / 989`
    - `Scoring Status: 989 scored / 0 unscored`
    - `0` CAP discrepancies, `0` Gate 3a discrepancies, `0` missing 4n, `0` waterfall violations, `0` calamity violations, `11 Reference Companies Verified: PASSED`, `Dual-Listed Mirror Parity: PASSED`.
  - `python3 -m unittest discover -s tests` exited `0`: `Ran 303 tests in 19.006s` (`OK`).
  - Live dataset check via `collect_screener_data(["us", "eu", "ca"])` and `phase_results`:
    - `total_companies = 1175`, `quality_pass = 225`, `calamity_pass = 11` (13 total `calamity == "Y"`), `valued = 220`.
    - Gate-3 advancing (`1=Y, 2=Y, 3a!=None, 3b=Y or calamity=Y`): `485` (`483` clean `3b="Y"` + `EL` and `APD` on calamity pass). Gate-3 rejects: `504` (`485 + 504 = 989`).
    - Incomplete Stage 2 rows: `108` Gate-4 rejects (`US: 57, EU: 51, CA: 0`, all blank `5` and `6`) + `13` Gate-5 rejects (`US: 9, EU: 4, CA: 0`, all `5=0` and blank `6`) = `121`.
    - `CRM` currently has `4 = 5` and `note` containing `'Fails Gate 4 (CAP = 10, REJECT)... Downstream gates bypassed per strict waterfall.'`
- **Source Files Inspected:**
  - `screener/apply_evaluation.py:123-307`: `validate_and_waterfall` scrubs `5`/`6` at lines 276–281 (`g4_num < 15`) and scrubs `6` at lines 284–289 (`g5_num == 0 and not cal_active`); does NOT validate `5` in `{0, 1, 2}` or `6` in `{"Y", "N"}`.
  - `screener/bulk_scorer.py:110-221, 461-653, 942-1175`: `REFERENCE_SNAPSHOT["CRM"]` (lines 201–210) has `"5": "", "6": ""`; `validate_company_evaluation` clears `["5", "6"]` at line 623 (`g4_val < 15`) and `["6"]` at line 634 (`g5_str == "0" and not calamity_active`) and only warns on blank `5`/`6` when `g4_val >= 15`; `audit_gate_3_universe` flags `g4_num < 15` with non-blank `5`/`6` as `waterfall_violations` (lines 1049–1058) and does not check Stage 2 completeness.
  - `screener/gates.py:166-222`: `phase_results` iterates `C.GATES` (`1, 2, 3b, 4, 5, 6`) and returns immediately on the first non-waived failure (Gate 4 at line 216, Gate 5 at line 211).
  - `screener/dashboard.py:136-137, 198, 2161-2170, 2272, 2618-2684, 3106-3284, 3574-3730`: `g5_mgmt`, `g6_cash`, and `g6_answer` are already emitted in `company_record`; `#dossier-g6-answer` is already wired at line 3728 (`c.g6_answer || 'blank'`); `ALL_COLS` lacks `g5_mgmt` and `g6_cash`; `openDrawer` stepper prints `PASS`/`FAIL`/`WAIVED` without gate values; qualitative card grid has only Moat Archetype + Moat Runway (CAP).
  - `screener/config.py:328-330`: `SCREENER_VERSION = "7.17"`, `CHANGELOG` top key is `"7.0"` followed by `"7.17"`.
  - `build.py:1-46`: builds `output/screener.html`, `output/index.html`, and `docs/index.html`. Root has no `PROJECT.md` or `TEST_READY.md`.
  - `tests/test_calamity_tier.py:126-145`, `tests/test_bulk_scoring_e2e.py:386-399, 1273-1360`, `tests/test_valuation_sandbox.py:202-206`.

## 2. Logic Chain

1. From `screener/gates.py:203-218`, `phase_results` short-circuits at `k == "4"` when `cap_final < 15` (`thr_cap = 15`) and at `k == "5"` when `5 == 0` without `calamity == "Y"`. Therefore, storing diagnostic `5` and `6` on the 108 Gate-4 rejects and `6` on the 13 Gate-5 rejects cannot alter `phase_results()["result"]`, `rejected_at`, `par_valuation`, Prime Grade (`225`), or Prime Grade Calamity (`11`/`13`) counts.
2. From `screener/apply_evaluation.py:246-291` and `screener/bulk_scorer.py:575-639, 1043-1058`, removing G5/G6 scrubbing on `CAP < 15` and G6 scrubbing on `5 = 0` (while keeping Stage 1 Gate 1–3 scrubbing and `clear_calamity` on `CAP < 15`) plus adding `5 in {0, 1, 2}` / `6 in {"Y", "N"}` validation and Stage 2 completeness checks satisfies R1 cleanly.
3. From `tests/test_calamity_tier.py:126-145`, the existing `test_gate4_failure_clears_calamity_and_downstream` sets `gate_3b_pricing_and_proof = "N"` and `calamity_flag = "Y"` alongside `gate_4_runway_cap = 10`. If `calamity` is cleared by Gate 4 while `3b` remains `"N"`, passing the resulting `qual` dict to `phase_results` would reject at Gate 3 rather than Gate 4; changing that test fixture to `gate_3b_pricing_and_proof = "Y"` (calamity waiving G6 = `"N"`) tests calamity-clearing on Gate 4 failure while ensuring `phase_results` rejects at Gate 4.
4. From `tests/test_valuation_sandbox.py:205-206`, `test_consistent_column_order_across_qpass_and_calamity` checks exact JS assignment lines for `qpass` and `calamity` expanded columns. Adding `ALL_COLS.g5_mgmt` and `ALL_COLS.g6_cash` only to `moat_universe` (Quality Grade) and `all` (Full Universe) expanded lists — leaving `compactKeys`, `qpass`, and `calamity` untouched — satisfies R3 without breaking existing sandbox tests.
5. From `screener/data.py:148-149`, integer `"0"` in CSV parses as Python `int` `0`, which is falsy in JS (`c.g5_mgmt`). Dashboard JS must explicitly check `!== null && !== undefined && !== ''` so `0` renders as `0/2` (`FAIL · 0/2` / `0/2 — Red Flag`), not blank/`-`.

## 3. Caveats

- Read-only survey only; no repository files were modified.
- Only R1, R3, and R4 (plus data counts and invariance checks) were in scope for this explorer; the 121 companies' statement/dossier qualitative scoring (R2) and spec markdown files (`QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`) were not audited in detail.
- In `screener/apply_evaluation.py` and `screener/bulk_scorer.py`, if a hypothetical payload manually supplies `3b="N"`, `calamity="Y"`, and `4 < 15`, Gate 4 clears `calamity` after Gate 3 already passed under `cal_active=True` (no real universe row has this combination; `EL` and `APD` have `CAP = 15` and `25`).

## 4. Conclusion

The codebase is clean and ready for v7.18 implementation:
1. **`screener/apply_evaluation.py` & `screener/bulk_scorer.py` (R1):** Remove Stage 2 G5/G6 scrubbing on `CAP < 15` and `5 = 0`; keep Stage 1 G1–G3 scrubbing and `clear_calamity` on `CAP < 15`; add strict domain validation for `5 in {0, 1, 2}` and `6 in {"Y", "N"}`; warn on blank G5/G6 for any Gate-3-advancing company; update `audit_gate_3_universe` to enforce zero blank/invalid G5/G6 across all 485 Gate-3-advancing companies while keeping Gate-3 rejects blank on `4_*..6`; update `REFERENCE_SNAPSHOT["CRM"]` once `CRM`'s `5`/`6` scores are finalized.
2. **`screener/dashboard.py`, `screener/config.py`, `build.py` (R3):** Add scored stepper sub-labels in `openDrawer` (preserving `WAIVED`), add the 2-card G5/G6 row below Moat Archetype / CAP, add `g5_mgmt` (`G5 Mgmt`) and `g6_cash` (`G6 B/S`) to `ALL_COLS` and `COL_TIPS` and include them in expanded `moat_universe` and `all` views only (handling `0` safely), bump `SCREENER_VERSION = "7.18"` and add `"7.18"` `CHANGELOG` in `config.py`, and run `python3 build.py`.
3. **`tests/` (R4):** Update `tests/test_calamity_tier.py` (`test_gate4_failure_clears_calamity_and_downstream` with `3b="Y"` so `phase_results` rejects at G4) and `tests/test_bulk_scoring_e2e.py` (`test_t1_f7_04`, `test_t1_f7_05`, `test_all_989_gate3_companies_completed`), plus add dashboard UI assertions for the new v7.18 elements.

Full line-by-line references are in `.agents/teamwork/v718_survey_explorer_engine/analysis.md`.

## 5. Verification Method

After v7.18 implementation is complete, independently verify with:
1. `python3 screener/bulk_scorer.py --audit` -> must exit `0` with `989 / 989` Gate 3 companies, `0` discrepancies, `0` Stage 1 waterfall violations, `0` missing/invalid Stage 2 G5/G6 across all 485 Gate-3-advancing companies, `11` reference companies verified (including `CRM`), and `Dual-Listed Mirror Parity: PASSED`.
2. `python3 build.py` -> must exit `0` reporting `Total Companies: 1175`, `Prime Grade: 225`, `Prime Grade Calamity (Conditional): 11`, and regenerate `output/screener.html`, `output/index.html`, and `docs/index.html`.
3. `python3 -m unittest discover -s tests` -> must exit `0` with 100% passing unit, parity, dashboard, and E2E tests.
4. **Invalidation conditions:** Any change to `Prime Grade` (225), `Prime Grade Calamity` (11 / 13 total), `Gate 3` total (989), or Gate 1–4 scores (`1..4n`) invalidates funnel invariance.
