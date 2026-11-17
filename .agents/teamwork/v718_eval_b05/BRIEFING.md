# BRIEFING — 2026-11-17T15:52:30Z

## Mission
Read-only qualitative Gate 5 & Gate 6 evaluation for Batch 5 (10 US companies in Information Technology — Software, IT Consulting & Internet), strictly calibrated against completed US+EU+CA Software peers, preserving `5=0` on `US:INTU` and `US:PANW` and paying special attention to `US:CRM`.

## 🔒 My Identity
- Archetype: `teamwork_worker` (implementer/qa/specialist)
- Roles: Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 5 (`v718_eval_b05`)
- Working directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05`
- Original parent: `d510ad6d-e687-40ee-9300-d03ba5fff497`
- Milestone: M2 (121-Company Sector-Combined G5/G6 Evaluation)

## 🔒 Key Constraints
- Strictly Read-Only on ALL repository files (`data/*/inputs.csv`, source, docs). Write ONLY inside `.agents/teamwork/v718_eval_b05/`.
- Evaluate all 10 assigned companies individually from local repository files (`inputs.csv`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`).
- Preserve `5 = 0` (`is_g5_reject: true`) on `US:INTU` and `US:PANW`, and evaluate Gate 6 (`Y`/`N`) for both.
- Pay special attention to `US:CRM` (`REFERENCE_SNAPSHOT` & Example 4 in `COMPANY_EVALUATION_SPEC.md`).
- Calibrate against completed US+EU+CA Software peers (`CA:CSU.CA[2,Y]`, `EU:DSY.FR[1,Y]`, `EU:NEM.DE[1,Y]`, `EU:SAP.DE[1,Y]`, `EU:SGE.GB[1,Y]`, `US:ADSK[1,Y]`, `US:CDNS[2,Y]`, `US:FICO[1,N]`, `US:PTC[1,Y]`, `US:SNPS[1,N]`, `US:TYL[1,Y]`, `US:FTNT[2,Y]`, `US:MSFT[1,Y]`, `US:VRSN[2,Y]`).
- DO NOT CHEAT: no fabricated numbers, no generic boilerplate rationales.

## Current Parent
- Conversation ID: `d510ad6d-e687-40ee-9300-d03ba5fff497`
- Updated: 2026-11-17T15:52:30Z

## Task Summary
- **What to produce**: `evaluations.json` (10 dicts), `progress.md`, `handoff.md` in `.agents/teamwork/v718_eval_b05/`.
- **Success criteria**: Completed and validated 10/10 evaluations with zero repository mutations.
- **Interface contracts**: `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `v718_survey_spec_miner/spec_report.md`.

## Key Decisions Made
- Confirmed `evaluations.json` dict schema: `universe`, `id`, `ticker`, `sub_industry`, `is_g5_reject`, `5`, `6`, `diagnostic_rationale`, `peer_calibration_notes`.
- Scored `US:CRM` (`REFERENCE_SNAPSHOT` & Example 4) at **`5 = 0`, `6 = "Y"`**: `$64.8B` goodwill/intangibles (`110%` of equity) compressing GAAP ROIC `< 12%` for 13 consecutive years (`7.5%` 5Y median), `$15.5B` 5Y SBC (`79.9%` of 5Y GAAP NI), and activist-coerced margin pivot followed by FY25 Informatica M&A fail Gate 5, while `166.6%` 5Y Owner FCF conversion (`$10.89B` FY25 Owner FCF), `p2p_ok = Y`, `-0.56y` 3Y median net debt (`< 1x` FY25 Owner FCF), and `27.5x` interest coverage pass Gate 6.
- Preserved `5 = 0` on `US:INTU` (`6 = "Y"`) and `US:PANW` (`6 = "Y"`).
- Scored `US:ADBE` (`0, Y`), `US:PLTR` (`0, Y`), `US:TRMB` (`0, N`), `US:NOW` (`1, Y`), `US:ACN` (`1, Y`), `US:IT` (`1, Y`), `US:SHOP` (`1, Y`).

## Artifact Index
- `.agents/teamwork/v718_eval_b05/DISPATCH.md` — Batch 5 assignment
- `.agents/teamwork/v718_eval_b05/BRIEFING.md` — Working memory
- `.agents/teamwork/v718_eval_b05/progress.md` — Liveness heartbeat
- `.agents/teamwork/v718_eval_b05/evaluations.json` — Verified 10-company Gate 5 & Gate 6 evaluations
- `.agents/teamwork/v718_eval_b05/handoff.md` — Final 5-component handoff report
