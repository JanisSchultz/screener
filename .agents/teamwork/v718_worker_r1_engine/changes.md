# Changes — v718_worker_r1_engine (R1)

## Modified Files
1. `screener/apply_evaluation.py`
   - Updated `validate_and_waterfall` (lines 234–302):
     - Kept Stage 1 downstream scrubbing when Gate 1 = `"N"`, Gate 2 = `"N"`, or unwaived Gate 3 fails (`3a == "None"` or `3b == "N"` without `calamity == "Y"`).
     - Removed downstream scrubbing of `"5"` and `"6"` when Gate 4 `CAP < 15` and of `"6"` when Gate 5 = `0` without calamity.
     - Preserved `clear_calamity(...)` when Gate 4 `CAP < 15` (non-waivable Anchor Gate).
     - Added Stage 2 validation (whenever not scrubbed by Stage 1): validates `"5"` via `_parse_subscore("5")` (rejects `bool`, fractional floats, out-of-range/non-int values; normalizes valid `{0, 1, 2}` to `int`; clears + warns on invalid) and validates `"6"` (`sanitize_val` in `{"Y", "N"}`, normalizes stripped string, clears + warns on invalid).

2. `screener/bulk_scorer.py`
   - Updated module docstring (lines 1–20) from `v7.16` to `v7.18` Two-Stage Munger Waterfall.
   - Updated `validate_company_evaluation`:
     - Hardened `_parse_score` (lines 512–526) to treat whitespace-only strings as empty and reject fractional floats (e.g. `1.5`) via `iv == float(raw)`.
     - Removed `clear_keys(["5", "6"], ...)` on `g4_val < 15` and `clear_keys(["6"], ...)` on `g5_str == "0" and not calamity_active`, while keeping `clear_keys(["calamity", "calamity_note"], ...)` on `g4_val < 15` (lines 617–627).
     - Added Stage 2 validation of `"5"` (`0/1/2`, normalizing valid values to `int` and recording errors on invalid) and `"6"` (`Y/N`, normalizing stripped string and recording errors on invalid) (lines 629–645).
     - Added blank Stage 2 warnings whenever any company advancing past Gate 3 (`g1 == "Y"`, `g2 == "Y"`, `g3a not in ("", "None")`, and `g3b == "Y"` or `calamity_now`) leaves `"5"` or `"6"` blank (lines 647–659).
   - Updated `audit_gate_3_universe`, `print_audit_report`, and `main`:
     - Kept Stage 1 Gate-3 failure check requiring blank `*FORCE_SCORE_CODES, "4", "4n", "5", "6"`.
     - Removed the old `waterfall_violations` check that flagged `g4_num < 15` with non-blank `"5"`/`"6"`.
     - Added `stage2_advancing_count` and `stage2_discrepancies` auditing all Gate-3-advancing moat franchises (`485`) for valid non-empty `"5"` in `{"0", "1", "2"}` and `"6"` in `{"Y", "N"}` (1 entry per company with missing/invalid Stage 2 scores).
     - Updated `print_audit_report` banner to `v7.18` and added Stage 1 / Stage 2 reporting lines.
     - Updated `main()` so `--audit` exits non-zero (`sys.exit(1)`) when Stage 2 missing/invalid G5/G6, Stage 1 waterfall violations, formula/alignment/4n/calamity violations, or mirror parity failures exist.
   - Left `REFERENCE_SNAPSHOT["CRM"]` unchanged (`"5": ""`, `"6": ""`) until M2 scores `CRM`.
