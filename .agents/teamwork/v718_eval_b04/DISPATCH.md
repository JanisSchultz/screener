# Dispatch — v718_eval_b04 (Batch 4: Industrials — Infra, A&D, Transport & Services, US+EU Combined)

## 2026-11-17T15:46:00Z
Assigned Role: `teamwork_worker` (Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 4)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Rubric Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Data & Peer Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b04`

## Strictly Read-Only on Repository Files
DO NOT modify `data/*/inputs.csv` or any repository source/doc files! Write outputs ONLY inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b04/`.

## Assigned Companies (11 total: 6 US + 5 EU; 2 Gate-5 rejects)
- **Aerospace & Defense (1)**: `US:BA` (**Gate-5 reject: MUST preserve `5 = 0`; evaluate Gate 6 ONLY**)
- **Airport Services (1)**: `EU:ADP.FR` (**Gate-5 reject: MUST preserve `5 = 0`; evaluate Gate 6 ONLY**)
- **Building Products (2)**: `US:AOS`, `US:LII`
- **Cargo Ground Transportation (1)**: `US:FDXF`
- **Construction & Engineering (2)**: `EU:FGR.FR`, `EU:SCYR.ES`
- **Passenger Ground Transportation (1)**: `US:UBER`
- **Research & Consulting Services (1)**: `US:TRI`
- **Security & Alarm Services (1)**: `EU:VSURE.SE`
- **Trading Companies & Distributors (1)**: `EU:RS1.GB`

## Evaluation Methodology
1. **Sub-Industry Peer Benchmarking (Anti-Drift Rule #1)**: Cross-check against completed US+EU peers (`BA` vs 23 A&D peers, `ADP.FR` vs `AENA.ES[1,Y]`/`FHZN.CH[1,N]`, `AOS`/`LII` vs `TT[1,Y]`/`ALLE[1,Y]`/`GEBN.CH[2,Y]`, `FDXF` vs `ODFL[2,Y]`, `FGR.FR`/`SCYR.ES` vs `DG.FR[1,Y]`, `TRI` vs `REL.GB[2,Y]`/`WKL.NL[2,Y]`/`VRSK[2,Y]`, `RS1.GB` vs `FAST[2,Y]`/`DPLM.GB[2,Y]`/`BNZL.GB[1,Y]`).
2. **Essential Infrastructure & Concessions Rule**: Remember `QUALITATIVE_EVALUATION_SPEC.md:225` — contractually formula-indexed physical infrastructure / regulated toll & airport concessions (`ADP.FR`, `FGR.FR`, `SCYR.ES`) pass Gate 6 if interest coverage > 5x (or verify exact coverage, net debt, FCF conversion in `financials.csv`/`fundamentals_panel.csv`!).
3. **Preserve `5 = 0`**: For `US:BA` and `EU:ADP.FR`, keep `"5": 0` and `"is_g5_reject": true`.

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Evaluate each company individually from its real local data. Do NOT fabricate numbers or use generic boilerplate rationales.

## Deliverable
Write `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b04/evaluations.json`, `progress.md`, and `handoff.md`. Report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
