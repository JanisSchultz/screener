# Dispatch — v718_eval_b09 (Batch 9: Consumer Staples, Materials & Energy, US+EU Combined)

## 2026-11-17T15:46:00Z
Assigned Role: `teamwork_worker` (Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 9)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Rubric Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Data & Peer Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b09`

## Strictly Read-Only on Repository Files
DO NOT modify `data/*/inputs.csv` or any repository source/doc files! Write outputs ONLY inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b09/`.

## Assigned Companies (10 total: 5 US + 5 EU; 1 Gate-5 reject)
- **Brewers (2)**: `EU:ABI.BE` (**Gate-5 reject: MUST preserve `5 = 0`; evaluate Gate 6 ONLY**), `EU:RBREW.DK`
- **Household Products (1)**: `US:CLX`
- **Soft Drinks & Non-alcoholic Beverages (1)**: `US:KDP`
- **Paper & Plastic Packaging Products & Materials (1)**: `US:AVY`
- **Specialty Chemicals (4)**: `EU:CRDA.GB`, `EU:DSFIR.NL`, `EU:EMSN.CH`, `US:IFF`
- **Oil & Gas Exploration & Production (1)**: `US:TPL`

## Evaluation Methodology
1. **Sub-Industry Peer Benchmarking (Anti-Drift Rule #1)**: Cross-check against completed US+EU peers (`CARL B.DK[1,Y]`, `HEIA.NL[1,Y]`, `HEIO.NL[1,Y]`, `CHD[1,Y]`, `CL[1,Y]`, `KO[1,Y]`, `PEP[1,Y]`, `MNST[2,Y]`, `CCEP[1,N]`, `SIKA.CH[2,Y]`, `GIVN.CH[1,Y]`, `SY1.DE[1,N]`, `ECL[1,Y]`, `SHW[2,Y]`).
2. **Gate 5 & Gate 6 Focus**:
   - Preserve `5 = 0` on `EU:ABI.BE` (`is_g5_reject: true`) and evaluate Gate 6 (`Y/N`) across Pillars 1–3 (`g6_netdebt_yrs`, `g6_intcov`, `fcf_conv`, M&A debt overhang).
   - Inspect `fundamentals_panel.csv` directly for `US:IFF` (blank `fcf_conv` in `financials.csv`, goodwill/write-downs, debt from DuPont N&B) and `EU:DSFIR.NL` (blank `p2p_ok`, DSM-Firmenich merger integration). Check `US:TPL` (royalty land trust economics, cash fortress, owner alignment/buybacks/litigation).

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Evaluate each company individually from its real local data. Do NOT fabricate numbers or use generic boilerplate rationales.

## Deliverable
Write `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b09/evaluations.json`, `progress.md`, and `handoff.md`. Report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
