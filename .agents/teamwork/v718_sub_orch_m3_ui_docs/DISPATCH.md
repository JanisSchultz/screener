# Dispatch — v718_sub_orch_m3_ui_docs (Milestone M3: R3 Dashboard UI, Version Bump & Spec Docs)

## 2026-11-17T15:40:00Z
Assigned Role: Sub-orchestrator (`teamwork_orchestrator`) for **Milestone M3 (R3)**
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read and pass path to all subagents): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Project Plan: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT_V718.md`
Survey References:
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine/analysis.md`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_sub_orch_m3_ui_docs`

## Exclusive Write Ownership
You own ONLY:
- `screener/dashboard.py`
- `screener/config.py`
- `QUALITATIVE_EVALUATION_SPEC.md`
- `COMPANY_EVALUATION_SPEC.md`

DO NOT modify `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/gates.py`, `data/`, or `tests/`. (Note: `build.py` regeneration of `output/` & `docs/index.html` and final `CRM` Example 4 values in `COMPANY_EVALUATION_SPEC.md` will happen in M4 after M2 scores `CRM`; you may verify `build.py` or dashboard rendering without breaking existing tests, or check `test_valuation_sandbox.py` and `test_dashboard_filters.py` directly!)

## Scope (R3)
1. **`screener/dashboard.py`**:
   - Update 6-Gate Waterfall Stepper (`openDrawer`) to display concrete gate values in stepper sub-labels when scored (e.g. `PASS · 25Y` / `FAIL · 10Y` on G4, `PASS · 2/2` / `PASS · 1/2` / `FAIL · 0/2` on G5, `PASS · Y` / `FAIL · N` on G6), preserving `WAIVED` styling on calamity waivers. CRITICAL: In JS, check `!== null && !== undefined && !== ''` (never truthiness) so `0` renders as `0/2`!
   - Add a 2-card row below Moat Archetype / Moat Runway (CAP) in the Qualitative Investment Thesis & Moat Analysis card grid showing:
     - `Management & Allocation (G5)` (`2/2 — Elite Compounder`, `1/2 — Standard Pass`, `0/2 — Red Flag`)
     - `Cash & Fortress B/S (G6)` (`Y — Pass`, `N — Fail`)
     whenever scored (and ensure `#dossier-g6-answer` is populated with `Y` or `N`).
   - Add `g5_mgmt` (`G5 Mgmt`) and `g6_cash` (`G6 B/S`) to `ALL_COLS` (and `COL_TIPS` and cell formatters) in expanded table mode on Quality Grade (`moat_universe`) and Full Universe (`all`) while keeping default Compact Cols (`compactKeys`) AND `qpass` / `calamity` expanded column arrays completely unchanged (verified by `tests/test_valuation_sandbox.py:205-206`).
2. **`screener/config.py`**:
   - Bump `SCREENER_VERSION` from `"7.17"` to `"7.18"` and add the `"7.18"` `CHANGELOG` entry.
3. **`QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`**:
   - Update all waterfall rules, prose, and field nullable tables (cataloged in `spec_report.md` Section 4: 8 locations in `QUALITATIVE_EVALUATION_SPEC.md`, 9 locations in `COMPANY_EVALUATION_SPEC.md`) to reflect the v7.18 Two-Stage Waterfall (Stage 1 early stop at Gates 1–3; Stage 2 full diagnostic scorecard across Gates 4–6; `calamity` cleared on Gate 4 `< 15Y`; Stage-2 reject note format without `"Downstream gates bypassed per waterfall."` + `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`). Leave `CRM` Example 4 placeholder or note that M4 fills exact verified `CRM` G5/G6 once M2 completes.

## Execution & Gate Requirements
Run the full Project Pattern Iteration Loop (Explorer(s) → Worker → Reviewer(s) → Challenger(s) → Forensic Auditor → `GATE_STATUS.md`). Verify `tests/test_valuation_sandbox.py`, `tests/test_dashboard_filters.py`, and dashboard HTML/JS generation cleanly.
Write `BRIEFING.md`, `progress.md`, `GATE_STATUS.md`, and `handoff.md` in your working directory, and report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
