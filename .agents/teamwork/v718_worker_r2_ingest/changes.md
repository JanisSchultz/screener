# Changes — v718_worker_r2_ingest

## Modified Files (Exclusive Ownership)

1. **`data/us/inputs.csv`** (66 rows updated) and **`data/eu/inputs.csv`** (55 rows updated)
   - Ingested all 121 evaluator Gate 5 & Gate 6 evaluations from `.agents/teamwork/v718_eval_b01/evaluations.json` through `v718_eval_b10/evaluations.json` (108 Gate-4 rejects at `CAP = 5Y / 10Y` across 57 US + 51 EU; 13 Gate-5 rejects at `5 = 0` across 9 US + 4 EU; `data/ca/inputs.csv` untouched).
   - Populated `"5"` (`0`/`1`/`2`) and `"6"` (`"Y"`/`"N"`), preserving `5 = "0"` on all 13 Gate-5 rejects (`US:BA`, `EU:ADP.FR`, `US:INTU`, `US:PANW`, `US:ROP`, `EU:DIM.FR`, `EU:SRT3.DE`, `EU:ABI.BE`, `US:CSGP`, `US:CCI`, `US:ES`, `US:SO`, `US:D`) and `6 = "N"` on all 31 `g6_default == "N"` rows (24 Banks + 7 Utilities).
   - Distribution across the 121 newly completed rows:
     - Gate 5 (`5`): `2` = 8 (2 US, 6 EU), `1` = 90 (48 US, 42 EU), `0` = 23 (16 US, 7 EU: 13 preserved G5 rejects + 10 G4 rejects scoring 0).
     - Gate 6 (`6`): `Y` = 46 (33 US, 13 EU), `N` = 75 (33 US, 42 EU).
   - Cleaned `"note"` on all 121 rows: stripped stale `"Downstream gates bypassed per (strict) waterfall."` / `"Downstream Gate 6 / Gates 5-6 bypassed per waterfall."` sentences, corrected `US:CRM`'s stale `CAP = 10` / `haircut to CAP 10` prose to `CAP = 5Y` / `haircut to CAP 5`, normalized inner `[...]` brackets to `(...)` inside `b07` rationales (`ALNY`, `INCY`, `PODD`) so `[Diagnostic G5=... | G6=...: ...]` stays unambiguous, and appended `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`.
   - Verified programmatically against `git show HEAD:data/{us,eu,ca}/inputs.csv`: only the 121 target rows changed, only columns `{5, 6, note}` changed, and all Gate 1–4 / metadata columns remained 100% character-for-character identical.

2. **`screener/bulk_scorer.py`** (line 208 only)
   - Updated `REFERENCE_SNAPSHOT["CRM"]` from `"5": "", "6": ""` to `"5": 0, "6": "Y"` matching `CRM`'s verified `v718_eval_b05` evaluation. Left all other 10 reference companies and all engine/audit code untouched.

3. **`COMPANY_EVALUATION_SPEC.md`** (lines 547, 575–577 only)
   - Updated Example 4 (`CRM`) replacing `<pending M2 verification>` placeholders with `CRM`'s verified `"gate_5_management_score": 0`, `"gate_6_cash_and_balance_sheet": "Y"`, and `[Diagnostic G5=0 | G6=Y: ...]` diagnostic note.

4. **`output/screener.html`**, **`output/index.html`**, **`docs/index.html`**
   - Regenerated exclusively via `python3 build.py` (`Total Companies: 1175`, `Prime Grade: 225`, `Prime Grade Calamity (Conditional): 11`, `Valued Prime Grade: 220`).
