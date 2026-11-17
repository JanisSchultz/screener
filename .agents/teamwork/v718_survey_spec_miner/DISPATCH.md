# Dispatch — v718_survey_spec_miner

## 2026-11-17T15:33:30Z
Assigned Role: `teamwork_spec_miner` (Gate 5/6 Rubrics & Waterfall Spec Extraction)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner`

Task:
Read `ORIGINAL_REQUEST.md` first, then thoroughly read `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` (read-only):
1. Extract the complete, exact Gate 5 (`0 / 1 / 2`) rubric, criteria, red flags, and examples/benchmarks.
2. Extract the complete, exact Gate 6 (`Y / N`) rubric across Pillars 1–3 (`p2p_ok`, `fcf_conv >= 80%`, `g6_netdebt_yrs <= 4.0y`, `g6_intcov > 5.0x`, Solvency II > 200% for insurers, automatic `N` for commercial fractional-reserve banks, regulated utilities with `g6_default = "N"`, debt-funded buyback negative equity, etc.).
3. Extract Anti-Drift Rules (especially Anti-Drift Rule #1 Sub-Industry Peer Benchmarking) and note/rationale formatting requirements.
4. Catalog every section, waterfall rule, and field nullable table in BOTH `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` that currently enforces the old 1-stage Gate 4/5 downstream blanking and needs updating in R3 for the Two-Stage Munger Waterfall (Stage 1 early stop at Gates 1–3; Stage 2 full diagnostic scorecard across Gates 4–6), citing exact file paths, headings, and line numbers.

Deliverables:
Write `spec_report.md` and `handoff.md` in your working directory (`/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner`), then notify parent `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
