# v7.18 Two-Stage Munger Waterfall — Engine, UI, Config & Test Survey (`analysis.md`)

**Core Finding:** The current v7.17 baseline is green (`--audit` passes with 0 discrepancies; `unittest` passes 303/303 tests; Prime Grade = 225, Prime Grade Calamity = 11/13, Gate-3 advancing = 485, Gate-3 rejects = 504). Implementing R1, R3, and R4 is surgical and preserves `phase_results`, `thr_cap = 15`, and Prime Grade / Calamity counts by construction, with two key edge cases to watch: (1) `test_gate4_failure_clears_calamity_and_downstream` in `tests/test_calamity_tier.py` passes `gate_3b_pricing_and_proof = "N"` alongside `gate_4_runway_cap = 10`, which would reject at Gate 3 (not Gate 4) once calamity is cleared unless updated to `3b = "Y"`; and (2) `tests/test_valuation_sandbox.py:205-206` asserts exact expanded column strings for `qpass` and `calamity`, so `g5_mgmt` and `g6_cash` must be added only to `moat_universe` and `all` expanded views (matching R3).

---

## 1. Baseline Verification Results

| Check | Command | Result | Key Metrics Observed |
|---|---|---|---|
| Bulk Scorer Audit | `python3 screener/bulk_scorer.py --audit` | Exit 0 (`PASSED`) | US: 445, EU: 495, CA: 49 (Total: 989/989); 989 scored / 0 unscored; 11 reference companies verified; 0 CAP discrepancies; 0 3a discrepancies; 0 missing 4n; 0 waterfall violations; 0 calamity violations; Mirror parity PASSED |
| Full Test Suite | `python3 -m unittest discover -s tests` | Exit 0 (`OK`) | Ran 303 tests in 19.006s |
| Live Universe Funnel | `collect_screener_data(["us", "eu", "ca"])` & `phase_results` | Verified | Total: 1175; Prime Grade (`passes_prime_grade`): 225; Prime Grade Calamity (`passes_calamity_grade`): 11 (13 total `calamity = "Y"`, 2 with `g6_flags >= 3`); Valued Prime Grade: 220; Gate-3 advancing (`1=Y, 2=Y, 3a!=None, 3b=Y or calamity=Y`): 485; Gate-3 rejects: 504; Gate-4 rejects (`CAP < 15`): 108 (US: 57, EU: 51, CA: 0); Gate-5 rejects (`5 = 0`, no calamity): 13 (US: 9, EU: 4, CA: 0); Blank G5 among 485: 108; Blank G6 among 485: 121 |

---

## 2. Detailed Codebase Survey by Requirement

### 2.1 R1 — `screener/apply_evaluation.py`

File: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/apply_evaluation.py`

- **`validate_and_waterfall(eval_data: dict)` (lines 123–306)**:
  - **Stage 1 early-stop scrubbing (KEEP)**:
    - Line 246 (`g1 == "N"`): scrubs `["2", "2r", *g3_all_keys, *g4_all_keys, "5", "6"]` and calls `clear_calamity("Gate 1 is 'N'")`.
    - Line 254 (`g2 == "N"`): scrubs `[*g3_all_keys, *g4_all_keys, "5", "6"]` and calls `clear_calamity("Gate 2 is 'N'")`.
    - Line 264 (`g3a == "None" or (g3b == "N" and not cal_active)`): scrubs `[*g4_all_keys, "5", "6"]` and calls `clear_calamity(reason)`.
  - **Stage 2 diagnostic preservation (MODIFY)**:
    - Lines 276–281 (`g4_num < 15`): Currently scrubs `["5", "6"]` with `"Waterfall: scrubbed '{k}' because Gate 4 (CAP={g4_num}) < 15"` and calls `clear_calamity(...)`. **Change:** Remove the `["5", "6"]` scrubbing loop; **keep** `clear_calamity(f"Gate 4 (CAP={g4_num}) < 15")`.
    - Lines 284–289 (`g5_num == 0 and not cal_active`): Currently scrubs `qual["6"] = ""` with `"Waterfall: scrubbed Gate 6 because Gate 5 is 0 without calamity override"`. **Change:** Remove Gate 6 scrubbing when `g5_num == 0 and not cal_active`.
  - **Missing `5` and `6` validation (ADD)**:
    - Currently `_parse_subscore` (lines 157–174) is only called for `MOAT_SCORE_CODES` and `FORCE_SCORE_CODES` (lines 184–185). Neither `"5"` nor `"6"` is validated for domain membership! If `5` is `"bad"`, line 285 raises `ValueError` caught silently at line 290; if `5` is `9` or `6` is `"maybe"`, invalid values pass through untouched.
    - **Change:** Whenever `"5"` is non-empty (and not scrubbed by Stage 1), validate via `_parse_subscore("5")` (validates `{0, 1, 2}`, rejects `bool`, normalizes to `int`, clears + warns on invalid). Whenever `"6"` is non-empty (and not scrubbed by Stage 1), validate `sanitize_val(qual.get("6"))` in `{"Y", "N"}` (normalize stripped string, clear + warn on invalid).
  - **Edge case (`3b="N"`, `calamity="Y"`, `4 < 15`)**:
    - If a payload supplies `3b="N"`, `calamity="Y"`, and `4=10`, line 264 lets it pass Gate 3 because `cal_active` is True, and then line 281 clears `calamity`. If `calamity` is cleared while `3b=="N"`, the resulting dict has `3b="N"` and `calamity=""` with non-blank G4–G6. Note this affects `tests/test_calamity_tier.py:126` (see Section 2.5).

### 2.2 R1 — `screener/bulk_scorer.py`

File: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/bulk_scorer.py`

- **`REFERENCE_SNAPSHOT` (lines 110–221)**:
  - Lines 201–210 (`CRM`): Currently `"5": "", "6": ""`. **Change:** Update `"5"` and `"6"` for `CRM` once verified scores are recorded in `data/us/inputs.csv`. Keep the other 10 reference companies (`SPGI`, `COST`, `ASML`, `ASML.NL`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `NUE`) untouched (`NUE` retains blank `G4–G6`).
- **`validate_company_evaluation(payload, existing_row=None)` (lines 461–653)**:
  - Lines 575–592: Stage 1 clearing for `g1 == "N"`, `g2 == "N"`, and `g3_failed = (g3a == "None") or (g3b == "N" and not calamity_active)` — **keep intact**.
  - Lines 618–639 (Gate 4 & Gate 5 checks):
    - Line 623: Currently `clear_keys(["5", "6"], ...)` when `g4_val < 15`. **Change:** Remove `"5"` and `"6"` clearing when `g4_val < 15`; keep clearing `["calamity", "calamity_note"]` if `calamity_active`.
    - Line 633–634: Currently `if g5_str == "0" and not calamity_active: clear_keys(["6"], ...)`. **Change:** Remove `"6"` clearing when `g5_str == "0" and not calamity_active`.
    - **Validation & Blank Warnings:** Validate `"5"` via `_parse_score("5")` (records error if invalid non-empty; normalizes valid to `int`) and validate `"6"` in `{"Y", "N"}` when non-empty (records error if invalid). Warn whenever any company advancing past Gate 3 (`g1 == "Y"`, `g2 == "Y"`, `g3a != "None"`, and `(g3b == "Y" or calamity_active)`) leaves `"5"` or `"6"` blank (not only when `g4_val >= 15`).
- **`audit_gate_3_universe` (lines 942–1091) & `print_audit_report` (lines 1125–1175)**:
  - Lines 1043–1047: Gate 3 failures (`g3a == "None" or (g3b == "N" and not calamity_flag)`) still require `*FORCE_SCORE_CODES, "4", "4n", "5", "6"` to be blank — **keep intact**.
  - Lines 1049–1058: Currently flags `waterfall_violations` if `g4_num < 15` and `("5", "6")` are non-blank. **Change:** Remove this violation check.
  - **New Stage 2 Diagnostic Audit Check:** For all companies advancing past Gate 3 (i.e. `not (g3a == "None" or (g3b == "N" and not calamity_flag))`, and `g1 == "Y" and g2 == "Y"`), verify `"5"` is non-empty and in `{"0", "1", "2"}`, and `"6"` is non-empty and in `{"Y", "N"}` (zero blank/invalid G5/G6 allowed across the 485 moat franchises). Record failures in a new audit field (e.g., `stage2_discrepancies` or `missing_stage2_scores`) or `waterfall_violations`, print it in `print_audit_report`, and update line 1128 banner `(v7.16)` -> `(v7.18)`. Also check `main()` exit code at line 1201 (consider exiting non-zero if `waterfall_violations` or `stage2_discrepancies` is non-empty, or verify existing behavior).
- **Helper Functions**:
  - `export_batch_context` (lines 659–745) and `ingest_evaluations` (lines 814–935): `ingest_evaluations` calls `validate_company_evaluation` and `sync_mirrors(dry_run=False)`. `sync_mirrors` (lines 752–807) syncs all `QUAL_COLUMNS` (including `5`, `6`, `note`) between `ASML` <-> `ASML.NL` and `FER` <-> `FER.ES`.

### 2.3 Funnel & Valuation Invariance — `screener/gates.py`

File: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/gates.py`

- **`gate_status` (lines 166–184)**: Evaluates `"1"`, `"2"`, `"3b"`, `"4"` (`cap_final >= p["thr_cap"]`, where `thr_cap = 15`), `"5"` (`v("5") >= p["thr_culture"]`, where `thr_culture = 1`), `"6"` (`v("6") or g6_default or None`).
- **`phase_results` (lines 192–222)**:
  - Iterates `C.GATES` sequentially: `("1", ...), ("2", ...), ("3b", ...), ("4", ...), ("5", ...), ("6", ...)`.
  - When `4 < 15`: `st["4"] == "fail"` (and `"4"` is NOT in `CALAMITY_GATES`), so `phase_results` returns `result = C.RES_REJ[4]` (`"Rejected – G4 Runway (<15Y)"`) and `rejected_at = "G4 Runway (15+ Yrs)"` immediately at line 216 — **before** inspecting `st["5"]` or `st["6"]`.
  - When `4 >= 15` and `5 == 0` (without `calamity == "Y"`): `phase_results` returns `result = C.RES_REJ[5]` (`"Rejected – G5 Management & Allocation"`) immediately at line 211 — **before** inspecting `st["6"]`.
  - Note: `failed` (line 201) lists all gates with `st[k] == "fail"` (consumed as `failed_gates` in `dashboard.py:151`, not displayed in table/cards; `rejected_at` is the first failing gate).
  - **Invariance Proof:** Populating `5` and `6` on the 108 Gate-4 rejects and `6` on the 13 Gate-5 rejects has **zero effect** on `thr_cap = 15`, `phase_results()["result"]`, `phase_results()["rejected_at"]`, `par_valuation` inputs, Prime Grade (`225`), Prime Grade Calamity (`11` with `< 3` G6 flags / `13` total `calamity = "Y"`), or Quality Grade counts. Note: `CRM` already has `g4_cap = 5` and `moat = "Toll booth & switching costs"`, so `par_valuation` for `CRM` is unchanged; `phase_results` for `CRM` stays `Rejected – G4 Runway (<15Y)`.

### 2.4 R3 — `screener/dashboard.py`, `screener/config.py`, `build.py`

1. **`screener/dashboard.py`**:
   - **Data payload (`collect_screener_data`, lines 112–241)**:
     - Already emits `"g5_mgmt": c.get("5")` (line 136), `"g6_cash": c.get("6")` (line 137), and `"g6_answer": c.get("6")` (line 198). No backend data-shape changes required!
     - Note on types from `screener/data.py` (`_parse`, lines 141–152): `"0"`, `"1"`, `"2"` in `inputs.csv` are parsed as `int` (`0`, `1`, `2`); blank `""` is parsed as `None`; `"Y"`/`"N"` are `str`. In JS, `c.g5_mgmt === 0` is falsy! Always check `c.g5_mgmt !== null && c.g5_mgmt !== undefined && c.g5_mgmt !== ''` rather than truthiness (`if (c.g5_mgmt)` would fail for `0`!).
   - **6-Gate Waterfall Stepper (`openDrawer`, lines 3574–3617)**:
     - Currently sets `label = st.toUpperCase()` (`PASS`, `FAIL`, `BLANK`) and `label = 'WAIVED'` for calamity-waived gates.
     - Update for G4, G5, G6 when scored (and not `WAIVED`, preserving `WAIVED` styling on calamity waivers):
       - G4 (`g.key === '4'`): if `c.g4_cap !== null && c.g4_cap !== undefined && c.g4_cap !== ''`, append `· ${c.g4_cap}Y` (e.g. `PASS · 25Y` / `FAIL · 10Y`).
       - G5 (`g.key === '5'`): if `c.g5_mgmt !== null && c.g5_mgmt !== undefined && c.g5_mgmt !== ''`, append `· ${c.g5_mgmt}/2` (e.g. `PASS · 2/2`, `PASS · 1/2`, `FAIL · 0/2`).
       - G6 (`g.key === '6'`): if `c.g6_cash !== null && c.g6_cash !== undefined && c.g6_cash !== ''`, append `· ${c.g6_cash}` (e.g. `PASS · Y`, `FAIL · N`).
       - Check CSS at lines 1687–1689 & 1725–1728 (`.step-result`): `font-size: 10px` (9px on mobile) — short strings like `PASS · 25Y` / `FAIL · 0/2` fit cleanly inside the 6-column stepper.
   - **2-Card Row below Moat Archetype / Moat Runway (CAP) (HTML lines 2161–2171, JS lines 3630–3634)**:
     - HTML: Immediately after the `<div class="grid-2" style="margin-bottom: 12px;">` holding `#dossier-moat-type` and `#dossier-cap`, add `<div class="grid-2" id="dossier-g56-row" style="margin-bottom: 12px; display: none;">` with:
       - Card 1: label `Management & Allocation (G5)` and value `#dossier-g5-mgmt`
       - Card 2: label `Cash & Fortress B/S (G6)` and value `#dossier-g6-cash`
     - JS (`openDrawer`):
       - Map `g5_mgmt`: `2` -> `'2/2 — Elite Compounder'`, `1` -> `'1/2 — Standard Pass'`, `0` -> `'0/2 — Red Flag'`, else `'-'`. (Color-code green / main / red or neutral).
       - Map `g6_cash`: `'Y'` -> `'Y — Pass'`, `'N'` -> `'N — Fail'`, else `'-'`.
       - Show `#dossier-g56-row` (`style.display = 'grid'` or `''`) whenever either G5 or G6 is scored (`hasG5 || hasG6`), and hide (`'none'`) when neither is scored (Gate 1–3 rejects).
     - `#dossier-g6-answer` (HTML line 2272, JS lines 3727–3728): Already sets `g6Ans.textContent = c.g6_answer || 'blank';` (or `c.g6_answer || c.g6_cash || 'blank'`), so once the 121 rows have `6` scored in `inputs.csv`, `#dossier-g6-answer` automatically displays `Y` or `N`.
   - **`ALL_COLS`, `COL_TIPS`, and `renderTable` (lines 2618–2684, 3101–3284)**:
     - Add to `ALL_COLS`:
       - `g5_mgmt: { key: 'g5_mgmt', label: 'G5 Mgmt', num: true }`
       - `g6_cash: { key: 'g6_cash', label: 'G6 B/S' }`
     - Add matching entries to `COL_TIPS`.
     - In `renderTable` expanded mode (`!compactColumns`, lines 3130–3144):
       - **CRITICAL CONSTRAINT from `tests/test_valuation_sandbox.py:205-206`**: Do NOT modify `qpass` (`cols = [...coreValuationCols, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.sector];`) or `calamity` (`cols = [...coreValuationCols, ALL_COLS.roic_used, ALL_COLS.waived_gates, ALL_COLS.g6_flags];`), and do NOT modify `compactColumns === true` (`compactKeys`).
       - Add `ALL_COLS.g5_mgmt, ALL_COLS.g6_cash` ONLY to `moat_universe` (line 3136) and `all` (lines 3138–3142) expanded column lists!
     - In `renderTable` cell formatter (lines 3165–3279):
       - Handle `col.key === 'g5_mgmt'`: format `0/2` (red badge), `1/2`, `2/2` (green badge), or `'-'` when `null`/`undefined`/`''` (avoiding JS falsy `0` pitfalls).
       - Handle `col.key === 'g6_cash'`: format `'Y'` (green badge), `'N'` (red badge), or `'-'` when `null`/`undefined`/`''`.
2. **`screener/config.py`**:
   - Line 328: Bump `SCREENER_VERSION = "7.17"` -> `"7.18"`.
   - Line 330+: Add `"7.18"` entry at the top of `CHANGELOG`.
3. **`build.py`**:
   - Calls `collect_screener_data(keys)` and `build_dashboard(keys)`, generating `output/screener.html`, `output/index.html`, and `docs/index.html`. No code edits needed in `build.py`. Note: neither `PROJECT.md` nor `TEST_READY.md` exists at repository root.

### 2.5 R4 — `tests/` Alignment

| File & Test Method | Lines | Current Assertion / Behavior | Required v7.18 Update |
|---|---|---|---|
| `tests/test_calamity_tier.py`: `test_gate4_failure_clears_calamity_and_downstream` | 126–145 | Asserts `qual["5"] == ""` and `qual["6"] == ""` on `gate_4_runway_cap=10` | Update to assert `qual["5"] == 1`, `qual["6"] == "N"`, `qual["calamity"] == ""`, `qual["calamity_note"] == ""`. **IMPORTANT:** Currently payload sets `gate_3b_pricing_and_proof="N"`; if `calamity` is cleared by Gate 4 while `3b="N"`, `phase_results(qual, params({}))` would reject at Gate 3! Change `gate_3b_pricing_and_proof` to `"Y"` in that test (so calamity was waiving G6=`"N"`) so `phase_results(qual, params({}))` genuinely rejects at Gate 4 (`C.RES_REJ[4]`). Also add a `5=0` without-calamity test preserving `6`. |
| `tests/test_bulk_scoring_e2e.py`: `test_t1_f7_04_gate4_cap_under_15_clears_gates_5_and_6` | 386–392 | Asserts `qual["5"] == ""` and `qual["6"] == ""` | Update to assert `qual["4"] == 10`, `qual["5"] == 1`, `qual["6"] == "Y"` (diagnostic G5 & G6 preserved). |
| `tests/test_bulk_scoring_e2e.py`: `test_t1_f7_05_gate5_failure_clears_gate_6_without_calamity` | 394–399 | Asserts `qual["5"] == 0`, `qual["6"] == ""` | Update to assert `qual["5"] == 0`, `qual["6"] == "Y"` (diagnostic G6 preserved). |
| `tests/test_bulk_scoring_e2e.py`: `test_all_989_gate3_companies_completed` | 1273–1360 | Lines 1340–1348 assert G4 rejects have blank `5`/`6` and non-calamity G5=0 rejects have blank `6` | Update Rule 4 (lines 1340–1350): for ALL 485 companies advancing past Gate 3 (`not fails_g3`), assert `row["5"]` is non-empty and `int(row["5"]) in (0, 1, 2)`, and `row["6"]` is non-empty and in `("Y", "N")`; keep Rule 2 (`fails_g3` -> 504 companies) asserting `4_*`, `4`, `4n`, `5`, `6` are strictly `""`. |
| `tests/test_bulk_scoring_e2e.py`: all other tests (incl. `test_t2_f6_01`, `test_t2_f7_05`, `test_t2_f8_01..05`, `test_t3_11`, `test_t4_07`, `test_reference_companies_regression`) | various | Test `CRM` CAP=5/REJ[4], `NUE` REJ[3], mirror parity, calamity clearing on G4 | Remain valid without modification once `CRM` scores & mirrors stay aligned. |
| `tests/test_valuation_sandbox.py`: `test_consistent_column_order_across_qpass_and_calamity` | 202–206 | Exact string match on `qpass` and `calamity` expanded columns | Preserved if `g5_mgmt`/`g6_cash` are added only to `moat_universe` and `all` expanded views. Add new dashboard test(s) covering stepper sub-labels, `#dossier-g5-mgmt` / `#dossier-g6-cash` / `#dossier-g6-answer`, and `g5_mgmt` / `g6_cash` in `ALL_COLS` (e.g., in `test_dashboard_filters.py` or `test_calamity_tier.py`). |
| `tests/test_cap_engine.py`, `tests/test_dashboard_filters.py`, `tests/test_v71..v77*.py` | various | Upstream G2 scrubbing, Quality Grade filters, sandbox & G6 rule checks | No breaking assumptions found. |
