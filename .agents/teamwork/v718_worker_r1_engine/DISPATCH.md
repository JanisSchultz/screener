# Dispatch — v718_worker_r1_engine (R1: Waterfall Validation, Ingestion & Audit Engine)

## 2026-11-17T15:42:00Z
Assigned Role: `teamwork_worker` (R1 Implementation)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Survey Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_worker_r1_engine`

## Exclusive File Ownership
Modify ONLY:
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/apply_evaluation.py`
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/screener/bulk_scorer.py`

DO NOT modify `data/`, `tests/`, `screener/dashboard.py`, `screener/config.py`, `screener/gates.py`, or any `*.md` spec files.

## Exact Requirements (R1)
1. **`screener/apply_evaluation.py` (`validate_and_waterfall`)**:
   - Keep strict downstream scrubbing when Gate 1 = `"N"`, Gate 2 = `"N"`, or unwaived Gate 3 fails (`3a = "None"` or `3b = "N"` without `calamity = "Y"`).
   - Remove downstream scrubbing of `"5"` and `"6"` when Gate 4 `CAP < 15`, and remove downstream scrubbing of `"6"` when Gate 5 = `0` without calamity.
   - Keep `clear_calamity(...)` when Gate 4 `CAP < 15` (non-waivable Anchor Gate).
   - Validate `"5"` in `{0, 1, 2}` (reject `bool`, normalize integer/string to `int`, clear + warn on invalid) and `"6"` in `{"Y", "N"}` (normalize stripped string, clear + warn on invalid) whenever supplied (and not scrubbed by Stage 1).
2. **`screener/bulk_scorer.py`**:
   - Update `validate_company_evaluation`:
     - Preserve `"5"` and `"6"` on `CAP < 15` and `"6"` on `5 = 0` (remove `clear_keys(["5", "6"], ...)` at `g4_val < 15` and `clear_keys(["6"], ...)` at `g5_str == "0" and not calamity_active`). Keep clearing `["calamity", "calamity_note"]` on `g4_val < 15`.
     - Validate `"5"` (`0/1/2`) and `"6"` (`Y/N`) when supplied (reject invalid values with actionable errors).
     - Warn if any company advancing past Gate 3 (`g1 == "Y"`, `g2 == "Y"`, `g3a != "None"`, and `g3b == "Y"` or `calamity_active`) leaves `"5"` or `"6"` blank (not just when `g4_val >= 15`).
   - Update `audit_gate_3_universe` (and `print_audit_report`):
     - Keep Stage 1 Gate-3 failures (`g3a == "None"` or `(g3b == "N" and not calamity_flag)`) requiring blank `*FORCE_SCORE_CODES, "4", "4n", "5", "6"`.
     - Remove the old `waterfall_violations` check that flagged `g4_num < 15` with non-blank `5`/`6`.
     - Audit all Gate-3-advancing companies (485 companies) for non-empty, valid `"5"` in `{"0", "1", "2"}` and `"6"` in `{"Y", "N"}` (zero blank/invalid G5/G6 allowed across moat franchises). Record any missing/invalid Stage 2 scores clearly in the audit dictionary & report, and update the audit banner from `v7.16` to `v7.18`. Ensure `--audit` exits non-zero if Stage 2 missing/invalid G5/G6 or waterfall violations are found (or check how `main()` handles exit codes).
   - Leave `REFERENCE_SNAPSHOT["CRM"]` unchanged for now (`""` for `"5"` and `"6"` until M2 scores `CRM`), keeping all 11 reference companies intact.

## Integrity Warning (MANDATORY)
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification & Deliverables
Run targeted Python verification commands (e.g. testing `validate_and_waterfall` and `validate_company_evaluation` on Gate 1–5 scenarios, and running `python3 screener/bulk_scorer.py --audit` to confirm it flags exactly the 121 currently blank Stage 2 rows with 0 Stage 1 violations).
Write `progress.md`, `changes.md`, and `handoff.md` in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_worker_r1_engine`, and notify `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
