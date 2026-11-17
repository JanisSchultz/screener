# Dispatch — v718_sub_orch_m1_engine (Milestone M1: R1 Engine Waterfall & Audit Core)

## 2026-11-17T15:40:00Z
Assigned Role: Sub-orchestrator (`teamwork_orchestrator`) for **Milestone M1 (R1)**
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read and pass path to all subagents): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Project Plan: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT_V718.md`
Survey Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_sub_orch_m1_engine`

## Exclusive Write Ownership
You own ONLY:
- `screener/apply_evaluation.py`
- `screener/bulk_scorer.py`

DO NOT modify `data/`, `tests/`, `screener/dashboard.py`, `screener/config.py`, `screener/gates.py`, `QUALITATIVE_EVALUATION_SPEC.md`, or `COMPANY_EVALUATION_SPEC.md`.

## Scope (R1)
1. **`screener/apply_evaluation.py` (`validate_and_waterfall`)**:
   - Keep strict downstream scrubbing when Gate 1 = `"N"`, Gate 2 = `"N"`, or unwaived Gate 3 fails (`3a = "None"` or `3b = "N"` without `calamity = "Y"`).
   - Remove downstream scrubbing of `"5"` and `"6"` when Gate 4 `CAP < 15`, and remove scrubbing of `"6"` when Gate 5 = `0` without calamity.
   - Keep `clear_calamity(...)` when Gate 4 `CAP < 15` (non-waivable Anchor Gate).
   - Validate `"5"` in `{0, 1, 2}` (reject `bool`, normalize to `int`, clear + warn on invalid) and `"6"` in `{"Y", "N"}` (normalize stripped string, clear + warn on invalid) whenever supplied (and not scrubbed by Stage 1).
2. **`screener/bulk_scorer.py`**:
   - Update `validate_company_evaluation` to preserve `"5"` and `"6"` on `CAP < 15` and `"6"` on `5 = 0`, validate `"5"` (`0/1/2`) and `"6"` (`Y/N`) when supplied, and warn if any company advancing past Gate 3 (`1="Y"`, `2="Y"`, `3a!="None"`, and `3b="Y"` or `calamity="Y"`) leaves `"5"` or `"6"` blank.
   - Update `audit_gate_3_universe` (and `print_audit_report`) so Gate-3 failures still require blank `4_*`, `4`, `4n`, `5`, `6`, while all 485 Gate-3-advancing companies are audited for non-empty, valid `"5"` (`0/1/2`) and `"6"` (`Y/N`) (zero blank/invalid G5/G6 allowed across moat franchises).
   - Note: `REFERENCE_SNAPSHOT["CRM"]` will be updated in M4 once M2 scores `CRM`; keep all 11 reference entries structurally intact (`CRM` currently remains `""` for `"5"`/`"6"` until M2/M4).

## Execution & Gate Requirements
Run the full Project Pattern Iteration Loop (Explorer(s) → Worker → Reviewer(s) → Challenger(s) → Forensic Auditor → `GATE_STATUS.md`). Verify via targeted in-memory/subprocess tests of `validate_and_waterfall`, `validate_company_evaluation`, and `audit_gate_3_universe` (using synthetic payloads/temp fixtures — do NOT modify repo `tests/`). Note that live `bulk_scorer.py --audit` will temporarily report the 121 blank G5/G6 rows until M2 runs, which confirms the new audit check works!
Write `BRIEFING.md`, `progress.md`, `GATE_STATUS.md`, and `handoff.md` in your working directory, and report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
