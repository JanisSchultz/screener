# Dispatch — v718_survey_explorer_engine

## 2026-11-17T15:33:30Z
Assigned Role: `teamwork_explorer` (Engine, UI, Config & Test Survey)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine`

Task:
Read `ORIGINAL_REQUEST.md` first, then inspect (read-only) all codebase files relevant to R1, R3, and R4:
1. `screener/apply_evaluation.py` (especially `validate_and_waterfall`, `clear_calamity`, downstream scrubbing)
2. `screener/bulk_scorer.py` (`validate_company_evaluation`, `audit_gate_3_universe`, `REFERENCE_SNAPSHOT`, `--audit` flow, context export/ingest helpers)
3. `screener/gates.py` (`phase_results`, `thr_cap`, `calamity` handling — verify how Gate 5/6 presence on CAP<15Y or 5=0 affects or does not affect `phase_results`, Prime Grade, and Prime Grade Calamity counts)
4. `screener/dashboard.py` (`openDrawer`, 6-Gate Waterfall Stepper, Qualitative Investment Thesis & Moat Analysis card grid, `#dossier-g6-answer`, `ALL_COLS`, Compact Cols, Quality Grade and Full Universe tables, Prime Grade counts)
5. `screener/config.py` (`SCREENER_VERSION`, `CHANGELOG`)
6. `build.py` (build outputs, how dashboard & docs are generated, whether `PROJECT.md` or `TEST_READY.md` exist at root)
7. `tests/test_calamity_tier.py`, `tests/test_bulk_scoring_e2e.py`, and all other files in `tests/` (exact test names, assertions that currently expect blank G5/G6 on CAP<15 or G6 on 5=0, dashboard tests, baseline counts)
8. Run `python3 screener/bulk_scorer.py --audit` and `python3 -m unittest discover -s tests` (read-only verification of current baseline) if safe/fast, and report exact baseline status.

Deliverables:
Write `analysis.md` and `handoff.md` in your working directory (`/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_engine`), then notify parent `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
