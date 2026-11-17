# R3 Changes — Dashboard UI, Version Bump & Spec Docs

## 1. `screener/dashboard.py`
- **HTML Dossier (`#dossier-g56-row`, lines ~2172–2181)**: Added a 2-column grid row directly below `Moat Archetype` / `Moat Runway (CAP)` containing `Management & Allocation (G5)` (`#dossier-g5-mgmt`) and `Cash & Fortress B/S (G6)` (`#dossier-g6-cash`), hidden by default (`display: none`).
- **`ALL_COLS` & `COL_TIPS` (lines ~2654–2688)**: Added `g5_mgmt` (`G5 Mgmt`, `num: true`) and `g6_cash` (`G6 B/S`) with descriptive tooltips.
- **`renderTable` expanded columns (lines ~3151–3159)**: Added `ALL_COLS.g5_mgmt` and `ALL_COLS.g6_cash` to expanded table mode ONLY on `moat_universe` (Quality Grade) and `all` (Full Universe), leaving `compactKeys`, `qpass`, and `calamity` column lists untouched.
- **`renderTable` cell formatters (lines ~3278–3292)**: Added `g5_mgmt` renderer (`0/2` red badge, `1/2` slate badge, `2/2` green badge, `-` when null/undefined/empty; handles `0` without JS falsy bug) and `g6_cash` renderer (`Y` green badge, `N` red badge, `-` when null/undefined/empty).
- **`openDrawer` Waterfall Stepper (lines ~3640–3648)**: Appended concrete gate values to stepper sub-labels when scored (`st !== 'blank'` and `label !== 'WAIVED'`), preserving `WAIVED` label and amber styling on calamity waivers:
  - G4: `${label} · ${c.g4_cap}Y` (e.g., `PASS · 25Y`, `FAIL · 10Y`)
  - G5: `${label} · ${c.g5_mgmt}/2` (e.g., `PASS · 2/2`, `PASS · 1/2`, `FAIL · 0/2`, handling `0` safely)
  - G6: `${label} · ${c.g6_cash}` (e.g., `PASS · Y`, `FAIL · N`)
- **`openDrawer` 2-card G5/G6 row (lines ~3665–3701)**: Populated `#dossier-g5-mgmt` (`2/2 — Elite Compounder`, `1/2 — Standard Pass`, `0/2 — Red Flag`) and `#dossier-g6-cash` (`Y — Pass`, `N — Fail`) with status colors, showing `#dossier-g56-row` when either G5 or G6 is scored and hiding it when neither is scored (Gate 1–3 rejects).
- **`openDrawer` `#dossier-g6-answer` (line ~3807)**: Updated fallback to `c.g6_answer || c.g6_cash || 'blank'`.

## 2. `screener/config.py`
- **Line 328**: Bumped `SCREENER_VERSION` from `"7.17"` to `"7.18"`.
- **Lines 708–718**: Added `"7.18"` `CHANGELOG` entry right above `"7.17"` summarizing the Two-Stage Munger Waterfall, Gate 4 non-waivable Anchor Gate preservation, 121 diagnostic Gate 5/6 completions, and dashboard UI surfacing.

## 3. `QUALITATIVE_EVALUATION_SPEC.md`
- Updated all 8 cataloged locations to `v7.18` Two-Stage Waterfall:
  1. Title & Section 1 intro (`v7.16` -> `v7.18`).
  2. Section 1 Item 2 (`Two-Stage Sequential Waterfall Invariant`: Stage 1 early stop at Gates 1–3 vs Stage 2 full diagnostic scorecard across Gates 4–6; Gate 4 non-waivable Anchor clearing calamity while preserving diagnostic `5` and `6`).
  3. Section 3 intro & ASCII diagram showing Stage 1 vs Stage 2 flow.
  4. Gate 4 Waterfall Action (clears `calamity_flag`/`calamity_note` on `4 < 15`, continues to evaluate `5` and `6` diagnostically).
  5. Gate 5 Waterfall Action (continues to evaluate `6` diagnostically on unwaived `5 = 0`).
  6. Section 4.1 `note` rules distinguishing Stage 1 rejects vs Stage 2 rejects (omitting `"Downstream gates bypassed per waterfall."`, matching deterministic `4`, and appending `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`).
  7. Section 5 Schema table rows `5`, `6`, and `note`.
  8. Section 6 Ingestion description (`apply_evaluation.py` Two-Stage Waterfall validation & scrubbing).

## 4. `COMPANY_EVALUATION_SPEC.md`
- Updated all 9 cataloged locations to `v7.18` Two-Stage Waterfall:
  1. Title & Section 1 intro (`v7.16` -> `v7.18`).
  2. Section 1 Item 2 (`Two-Stage Sequential Waterfall Invariant`).
  3. Section 3 intro & ASCII diagram.
  4. Gate 4 Waterfall Action.
  5. Gate 5 Waterfall Action.
  6. Section 4.1 `note` rules for Stage 1 vs Stage 2 rejects (`CRM` illustrative `CAP = 5Y`).
  7. Section 6 Schema Rules & Field Mapping table rows `5`, `6`, and `note`.
  8. Section 7 Example 4 (`CRM` — Stage 2 Diagnostic Format, clearly marked pending M2 `CRM` verification).
  9. Section 8 Step 1 Item 2 (`Two-Stage Waterfall invariant`).

## 5. Regenerated Build Outputs
- `output/screener.html`, `output/index.html`, `docs/index.html` regenerated via `python3 build.py`.
