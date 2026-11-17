# Dispatch — v718_eval_b06 (Batch 6: Information Technology — Semiconductors & Electronic Instruments, US+EU Combined)

## 2026-11-17T15:46:00Z
Assigned Role: `teamwork_worker` (Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 6)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Rubric Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`
Data & Peer Reference: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06`

## Strictly Read-Only on Repository Files
DO NOT modify `data/*/inputs.csv` or any repository source/doc files! Write outputs ONLY inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/`.

## Assigned Companies (8 total: 6 US + 2 EU; 1 Gate-5 reject)
- **Electronic Equipment & Instruments (4)**: `EU:IFCN.CH`, `US:KEYS`, `US:ROP` (**Gate-5 reject: MUST preserve `5 = 0`; evaluate Gate 6 ONLY**), `US:TDY`
- **Semiconductors (3)**: `EU:NOD.NO`, `US:MPWR`, `US:NXPI`
- **Semiconductor Materials & Equipment (1)**: `US:Q`

## Evaluation Methodology
1. **Sub-Industry Peer Benchmarking (Anti-Drift Rule #1)**: Cross-check against completed US+EU peers (`HEXA B.SE[1,N]`, `HLMA.GB[2,Y]`, `ADI[1,Y]`, `AVGO[1,Y]`, `TXN[2,N]`, `NVDA[2,N]`, `ARM[1,N]`, `ASML[2,Y]`, `ASML.NL[2,Y]`, `KLAC[2,Y]`, `LRCX[2,Y]`, `AMAT[1,Y]`, `ASM.NL[2,Y]`).
2. **Gate 5 & Gate 6 Focus**:
   - Preserve `5 = 0` on `US:ROP` (`is_g5_reject: true`) and evaluate Gate 6 (`Y/N`) rigorously across Pillars 1–3 (`g6_netdebt_yrs`, `g6_intcov`, `fcf_conv`, M&A debt load in `financials.csv` / `fundamentals_panel.csv` / `evidence`).
   - Score Gate 5 (`0/1/2`) and Gate 6 (`Y/N`) for the remaining 7 (`IFCN.CH`, `KEYS`, `TDY`, `NOD.NO`, `MPWR`, `NXPI`, `Q`). Note `US:Q` (Qnity Electronics) has blank `p2p_ok` and `ma_reinvest` in `financials.csv` — inspect `fundamentals_panel.csv` and `note`/`evidence` directly!

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Evaluate each company individually from its real local data. Do NOT fabricate numbers or use generic boilerplate rationales.

## Deliverable
Write `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/evaluations.json`, `progress.md`, and `handoff.md`. Report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
