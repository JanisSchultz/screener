# Dispatch — v718_eval_b01 (Batch 1: Financials — Diversified & Regional Banks, US+EU Combined)

## 2026-11-17T15:46:00Z
Assigned Role: `teamwork_worker` (Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 1)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Rubric Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Data & Peer Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b01`

## Strictly Read-Only on Repository Files
DO NOT modify `data/*/inputs.csv` or any repository source/doc files! Write outputs ONLY inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b01/`.

## Assigned Companies (24 total: 2 US + 22 EU; 0 Gate-5 rejects)
- **Diversified Banks (14 EU)**:
  `EU:A5G.IE`, `EU:ABN.NL`, `EU:BCP.PT`, `EU:BG.AT`, `EU:BIRG.IE`, `EU:BKT.ES`, `EU:DANSKE.DK`, `EU:EBS.AT`, `EU:INGA.NL`, `EU:LLOY.GB`, `EU:NWG.GB`, `EU:SEB A.SE`, `EU:SWED A.SE`, `EU:UCG.IT`
- **Regional Banks (2 US + 8 EU)**:
  `EU:ALSYDB.DK`, `EU:BCVN.CH`, `EU:JYSK.DK`, `EU:RILBA.DK`, `EU:SB1NO.NO`, `EU:SBNOR.NO`, `EU:UNI.ES`, `EU:VATN.CH`, `US:MTB`, `US:RF`

## Evaluation Methodology
1. **Sub-Industry Peer Benchmarking (Anti-Drift Rule #1)**: First inspect the 18 completed Diversified Banks peers across US, EU, and CA (`CA:BMO.CA[1,N]`, `CA:BNS.CA[1,N]`, `CA:CM.CA[1,N]`, `CA:NA.CA[2,N]`, `CA:RY.CA[2,N]`, `CA:TD.CA[1,N]`, `EU:CABK.ES[1,N]`, `EU:DNB.NO[1,N]`, `EU:ISP.IT[2,N]`, `EU:KBC.BE[2,N]`, `EU:NDA FI.FI[2,N]`, `EU:SHB A.SE[2,N]`, `EU:UBSG.CH[1,N]`, `US:BAC[1,N]`, `US:JPM[2,N]`, `US:PNC[1,N]`, `US:USB[1,N]`, `US:WFC[1,N]`) in `inputs.csv`, `financials.csv`, and `prescreen.csv` so you score US and EU banks on the exact same Gate 5 (`0/1/2`) yardstick!
2. **Gate 6 (`6 = "N"`)**: All 24 are commercial fractional-reserve banks with `prescreen.csv` `g6_default = "N"` (`"Commercial fractional-reserve banks fail"` per `QUALITATIVE_EVALUATION_SPEC.md:226`). Score `6 = "N"` explicitly for all 24, citing bank leverage/deposit-duration risk and each bank's specific financial profile.
3. **Gate 5 (`0 / 1 / 2`)**: Evaluate each bank individually against the 5-vector rubric (Integrity & Candor, Rational Capital Allocation / buybacks / M&A discipline, Customer Value, Execution, Anti-Bureaucracy) using ONLY local `inputs.csv` (`note`, `evidence`), `financials.csv`, `fundamentals_panel.csv` (especially for `EU:ALSYDB.DK` and `EU:SBNOR.NO` which carry `share count changed since FY` `fin_note`), and `prescreen.csv`. Watch for regulatory/AML scandals, serial empire M&A, or governance flags (`0`) vs steady stewardship (`1`) vs exceptional long-term Nordic/owner-like compounding & cost discipline (`2`, e.g., calibrated against `SHB A.SE`, `NDA FI.FI`, `KBC.BE`, `ISP.IT`, `JPM`).

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Evaluate each company individually from its real local data. Do NOT fabricate numbers or use generic boilerplate rationales.

## Deliverable
Write `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b01/evaluations.json` (array of 24 dicts: `universe`, `id`, `ticker`, `sub_industry`, `is_g5_reject: false`, `5`, `6`, `diagnostic_rationale`, `peer_calibration_notes`), `progress.md`, and `handoff.md`. Report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
