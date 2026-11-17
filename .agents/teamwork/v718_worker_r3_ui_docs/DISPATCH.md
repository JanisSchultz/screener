# Dispatch — v718_worker_r3_ui_docs (R3: Dashboard UI, Version Bump & Spec Docs)

## 2026-11-17T15:42:00Z
Assigned Role: `teamwork_worker` (R3 Implementation)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Survey References:
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine/analysis.md`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_worker_r3_ui_docs`

## Exclusive File Ownership
Modify ONLY:
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/dashboard.py`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/config.py`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/QUALITATIVE_EVALUATION_SPEC.md`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/COMPANY_EVALUATION_SPEC.md`

DO NOT modify `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/gates.py`, `data/`, or `tests/`.

## Exact Requirements (R3)
1. **`screener/dashboard.py`**:
   - **6-Gate Waterfall Stepper (`openDrawer`)**: Display concrete gate values in stepper sub-labels when scored (and not `WAIVED`, preserving `WAIVED` styling on calamity waivers):
     - G4 (`g.key === '4'`): e.g. `PASS · 25Y` / `FAIL · 10Y` when `c.g4_cap` is non-null/non-empty
     - G5 (`g.key === '5'`): e.g. `PASS · 2/2`, `PASS · 1/2`, `FAIL · 0/2` when `c.g5_mgmt !== null && c.g5_mgmt !== undefined && c.g5_mgmt !== ''` (CRITICAL: `0` is falsy in JS! Never use `if (c.g5_mgmt)`!)
     - G6 (`g.key === '6'`): e.g. `PASS · Y` / `FAIL · N` when `c.g6_cash !== null && c.g6_cash !== undefined && c.g6_cash !== ''`
   - **2-Card Row below Moat Archetype / Moat Runway (CAP)** in Qualitative Investment Thesis & Moat Analysis card grid:
     - Show `Management & Allocation (G5)` (`2/2 — Elite Compounder`, `1/2 — Standard Pass`, `0/2 — Red Flag`) and `Cash & Fortress B/S (G6)` (`Y — Pass`, `N — Fail`) whenever scored (hide row when neither is scored, e.g., Gate 1–3 rejects).
     - Ensure `#dossier-g6-answer` is populated with `Y` or `N` when scored (fallback `c.g6_answer || c.g6_cash || 'blank'`).
   - **Expanded Table Columns**:
     - Add `g5_mgmt` (`G5 Mgmt`) and `g6_cash` (`G6 B/S`) to `ALL_COLS`, `COL_TIPS`, and cell renderers (handling `0` safely as `0/2`).
     - Include `ALL_COLS.g5_mgmt` and `ALL_COLS.g6_cash` in expanded table mode ONLY on Quality Grade (`moat_universe`) and Full Universe (`all`).
     - **CRITICAL**: Keep `compactKeys`, `qpass`, and `calamity` expanded column arrays completely untouched (`tests/test_valuation_sandbox.py:205-206` checks exact `qpass` and `calamity` column expressions!).
2. **`screener/config.py`**:
   - Bump `SCREENER_VERSION` from `"7.17"` to `"7.18"`.
   - Add `"7.18"` `CHANGELOG` entry at the top of `CHANGELOG`.
3. **`QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`**:
   - Update all waterfall rules, prose, and field nullable tables (cataloged in `spec_report.md` Section 4: 8 locations in `QUALITATIVE_EVALUATION_SPEC.md`, 9 locations in `COMPANY_EVALUATION_SPEC.md`) to reflect the v7.18 Two-Stage Waterfall (Stage 1 early stop at Gates 1–3; Stage 2 full diagnostic scorecard across Gates 4–6; non-waivable Anchor Gate 4 clears calamity; Stage-2 reject `note` omits `"Downstream gates bypassed per waterfall."` and appends `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`).
   - For `COMPANY_EVALUATION_SPEC.md` Example 4 (`CRM`, lines 539–579), update prose to reflect Stage 2 diagnostic scoring (note that exact verified `CRM` `5`/`6` values will be filled after M2 evaluates `CRM`, or mark `[Pending M2 CRM score]` clearly if not yet scored — wait: let's keep `CRM` Example 4 clearly marked or updated in final integration M4 once M2 finishes!).

## Integrity Warning (MANDATORY)
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification & Deliverables
Run `python3 -m unittest tests/test_valuation_sandbox.py tests/test_dashboard_filters.py` and `python3 build.py` (verifying `output/screener.html` renders cleanly and `Total Companies: 1175`, `Prime Grade: 225`, `Prime Grade Calamity (Conditional): 11` remain unchanged).
Write `progress.md`, `changes.md`, and `handoff.md` in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_worker_r3_ui_docs`, and notify `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
