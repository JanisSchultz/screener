# Dispatch — v718_iter2_worker (Iteration 2: Engine Cascade Fix, Regression Tests & Cleanup)

## 2026-11-17T16:11:30Z
Assigned Role: `teamwork_worker` (Iteration 2 Remediation Implementer)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Investigation Blueprint: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_iter2_explorer/handoff.md` and `analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_iter2_worker`

## Exclusive File Ownership
Modify ONLY:
- `screener/apply_evaluation.py`
- `screener/bulk_scorer.py`
- `tests/test_v718_two_stage_waterfall.py`
- Remove stale untracked OneDrive conflict copies `"output/screener.html 2.html"` and `"output/screener.html 3.html"` (if present), then run `python3 build.py` cleanly at the end if needed.

DO NOT modify `data/`, `screener/dashboard.py`, `screener/config.py`, `screener/gates.py`, `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `tests/test_calamity_tier.py`, or `tests/test_bulk_scoring_e2e.py`.

## Exact Fixes Required
1. **`screener/apply_evaluation.py` (`validate_and_waterfall`)**:
   - Standalone `"4"` validation (~lines 224–232): reject `bool` (`isinstance(raw_4, bool)`), verify `int(raw_4) == float(raw_4)`, and normalize valid values to `int` (clear + warn if invalid).
   - Stage 1 / Stage 2 cascade (~lines 279–280): when `g4_num < 15` calls `clear_calamity(...)`, immediately check `if g3b == "N":` -> scrub `[*g4_all_keys, "5", "6"]` with clear warnings AND set `stage1_scrubbed = True` (so subsequent Gate 5/6 validation skips scrubbed fields cleanly). Keep `g3b == "Y"` preserving `4_*`, `4`, `4n`, `5`, `6`!
2. **`screener/bulk_scorer.py` (`validate_company_evaluation`)**:
   - Stage 1 / Stage 2 cascade (~lines 622–624): when `g4_val < 15` clears `calamity` / `calamity_note` and `g3b == "N"`, scrub `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]` via `clear_keys` and return early `return qual, warnings, errors` (preventing orphaned downstream fields and preventing false blank-G5/G6 warnings on the now-Gate-3-failed row). Keep `g3b == "Y"` preserving `4_*`, `4`, `4n`, `5`, `6`!
3. **`tests/test_v718_two_stage_waterfall.py` (`WaterfallEngineValidationTests`)**:
   - Add regression test verifying `3b="N"` + `calamity="Y"` + `CAP < 15` clears calamity AND scrubs `4_*`, `4`, `4n`, `5`, `6` in both `validate_and_waterfall` and `validate_company_evaluation`, AND verify isolated temp `ingest_evaluations` -> `audit_gate_3_universe` produces `0` `waterfall_violations`.
   - Add regression test verifying standalone `"4"` rejects `15.5` and `False` in `validate_and_waterfall`.
4. **Cleanup & Verification**:
   - Run `python3 -m unittest discover -s tests` (must pass 100%, all tests `OK`).
   - Run `python3 screener/bulk_scorer.py --audit` (must exit `0`).
   - Run `python3 build.py` (must exit `0`, `1175` total, `225` Prime Grade, `11` Prime Grade Calamity), and remove any OneDrive duplicate conflict files (`output/screener.html [0-9].html`) if created during test runs so `git status -s` is completely clean of stray conflict copies! (Run `unittest` again if needed or ensure `test_*.py` runs leave `output/screener.html` intact and no `screener.html *.html` copies).

## Integrity Warning (MANDATORY)
DO NOT CHEAT. All fixes and regression tests must be genuine.

## Deliverables
Write `progress.md`, `changes.md`, and `handoff.md` in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_iter2_worker/`, and notify `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
