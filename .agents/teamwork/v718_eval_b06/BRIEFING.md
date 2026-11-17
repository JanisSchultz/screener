# BRIEFING — 2026-11-17T15:52:00Z

## Mission
Read-only qualitative Gate 5 (`0/1/2`) and Gate 6 (`Y/N`) evaluation of Batch 6 (8 companies in Information Technology — Semiconductors & Electronic Instruments, US+EU combined), preserving `5=0` on `US:ROP` (`is_g5_reject: true`) and calibrating against the 16 completed US+EU peers.

## 🔒 My Identity
- Archetype: `teamwork_worker` (Read-Only Qualitative Gate 5 & Gate 6 Evaluator — Batch 6)
- Roles: implementer, qa, specialist (read-only evaluation output in own folder)
- Working directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06`
- Original parent: `d510ad6d-e687-40ee-9300-d03ba5fff497`
- Milestone: v7.18 Two-Stage Waterfall Qualitative Evaluation (Batch 6)

## 🔒 Key Constraints
- Strictly read-only on all repository files (`data/*/inputs.csv`, source, docs). Write outputs ONLY inside `.agents/teamwork/v718_eval_b06/`.
- DO NOT CHEAT: evaluate each of the 8 companies individually from local repository files (`inputs.csv`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`), calibrated against completed US+EU peers.
- Preserve `5 = 0` on `US:ROP` (`is_g5_reject: true`); evaluate Gate 6 ONLY for `US:ROP` (while also checking if `US:ROP`'s `note` has `"Downstream Gate 6 bypassed per waterfall."` to document cleanly).
- Evaluate both Gate 5 (`0/1/2`) and Gate 6 (`Y/N`) for the remaining 7: `EU:IFCN.CH`, `US:KEYS`, `US:TDY`, `EU:NOD.NO`, `US:MPWR`, `US:NXPI`, `US:Q`.
- Inspect `fundamentals_panel.csv` and `note`/`evidence` directly for `US:Q` (blank `p2p_ok` and `ma_reinvest` in `financials.csv`).
- Output files: `evaluations.json`, `progress.md`, `handoff.md` in working directory; report to `d510ad6d-e687-40ee-9300-d03ba5fff497`.

## Current Parent
- Conversation ID: `d510ad6d-e687-40ee-9300-d03ba5fff497`
- Updated: 2026-11-17T15:52:00Z

## Task Summary
- **What to build**: `evaluations.json` containing 8 structured Gate 5 & Gate 6 evaluation dicts (`universe`, `id`, `ticker`, `sub_industry`, `is_g5_reject`, `5`, `6`, `diagnostic_rationale`, `peer_calibration_notes`).
- **Success criteria**: Rigorous, evidence-backed G5/G6 evaluation calibrated against the 16 completed US+EU sub-industry peers (`HEXA B.SE`, `HLMA.GB`, `ADI`, `AVGO`, `TXN`, `NVDA`, `ARM`, `ASML`, `ASML.NL`, `KLAC`, `LRCX`, `AMAT`, `ASM.NL`, `BESI.NL`, `MYCR.SE`, `VACN.CH`), accurate handling of `US:ROP` (`5=0`) and `US:Q`.
- **Interface contracts**: `QUALITATIVE_EVALUATION_SPEC.md`, `DISPATCH.md`, `v718_survey_spec_miner/spec_report.md`, `v718_survey_explorer_data/analysis.md`.
- **Code layout**: Read-only data in `data/us/`, `data/eu/`; outputs in `.agents/teamwork/v718_eval_b06/`.

## Key Decisions Made
- Completed full read-only audit of `inputs.csv`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`, and `screener/gates.py:g6_checks` across all 8 assigned companies and 16 completed US+EU sub-industry peers.
- Scored: `EU:IFCN.CH` `[1, Y]`, `US:KEYS` `[1, Y]`, `US:ROP` `[0 (preserved), N]`, `US:TDY` `[1, Y]`, `EU:NOD.NO` `[1, N]`, `US:MPWR` `[1, N]`, `US:NXPI` `[1, N]`, `US:Q` `[1, N]`.
- Verified `evaluations.json` schema, key alignment, and zero repository file edits.

## Artifact Index
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/DISPATCH.md` — Assignment
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/BRIEFING.md` — Working memory
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/progress.md` — Heartbeat log
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/evaluations.json` — 8 Gate 5 & Gate 6 evaluations
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/handoff.md` — 5-component handoff report
