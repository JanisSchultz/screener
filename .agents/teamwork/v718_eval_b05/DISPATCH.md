# Dispatch — v718_eval_b05 (Batch 5: Information Technology — Software, IT Consulting & Internet)

## 2026-11-17T15:46:00Z
Assigned Role: `teamwork_worker` (Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 5)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Rubric Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Data & Peer Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05`

## Strictly Read-Only on Repository Files
DO NOT modify `data/*/inputs.csv` or any repository source/doc files! Write outputs ONLY inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05/`.

## Assigned Companies (10 total: 10 US + 0 EU; 2 Gate-5 rejects)
- **Application Software (5)**: `US:ADBE`, `US:CRM`, `US:INTU` (**Gate-5 reject: MUST preserve `5 = 0`**), `US:PLTR`, `US:TRMB`
- **Systems Software (2)**: `US:NOW`, `US:PANW` (**Gate-5 reject: MUST preserve `5 = 0`**)
- **IT Consulting & Other Services (2)**: `US:ACN`, `US:IT`
- **Internet Services & Infrastructure (1)**: `US:SHOP`

## Evaluation Methodology
1. **Sub-Industry Peer Benchmarking (Anti-Drift Rule #1)**: Cross-check against completed US+EU+CA Software peers (`CA:CSU.CA[2,Y]`, `EU:DSY.FR[1,Y]`, `EU:NEM.DE[1,Y]`, `EU:SAP.DE[1,Y]`, `EU:SGE.GB[1,Y]`, `US:ADSK[1,Y]`, `US:CDNS[2,Y]`, `US:FICO[1,N]`, `US:PTC[1,Y]`, `US:SNPS[1,N]`, `US:TYL[1,Y]`, `US:FTNT[2,Y]`, `US:MSFT[1,Y]`, `US:VRSN[2,Y]`).
2. **Gate 5 & Gate 6 Focus**:
   - Check SBC dilution, M&A capital allocation, non-GAAP vs GAAP gap, debt-funded buybacks / negative equity (like `FICO` / `MSCI` or `IT`!), and FCF conversion in `fundamentals_panel.csv` & `financials.csv`.
   - **Special attention to `US:CRM`**: `CRM` is a `REFERENCE_SNAPSHOT` company AND Worked Example 4 in `COMPANY_EVALUATION_SPEC.md`! Evaluate `CRM` rigorously against the 5 vectors (Benioff M&A empire history like Slack/Tableau/Informatica, SBC, activist pivot vs capital allocation) and 3 pillars (`p2p_ok`, `fcf_conv`, `g6_netdebt_yrs`, `g6_intcov`), and ensure its `diagnostic_rationale` is crystal clear. (Note: `CRM`'s `CAP = 10` prose fix in `note` will be applied during ingest).
   - Preserve `5 = 0` on `US:INTU` and `US:PANW` (`is_g5_reject: true`) and evaluate Gate 6 (`Y/N`) for both.

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Evaluate each company individually from its real local data. Do NOT fabricate numbers or use generic boilerplate rationales.

## Deliverable
Write `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05/evaluations.json`, `progress.md`, and `handoff.md`. Report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
