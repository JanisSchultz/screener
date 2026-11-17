# BRIEFING — 2026-11-17T15:33:00Z

## Mission
Implement the Two-Stage Munger Waterfall and diagnostic Gate 5–6 scorecard (v7.18) across engine, 121 incomplete moat franchises (split by GICS Sector/Sub-Industry across US+EU combined), dashboard UI, docs, and tests with zero funnel/Prime Grade count drift.

## 🔒 My Identity
- Archetype: teamwork_orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Level: Project Orchestrator (top-level for this v7.18 dispatch)
- Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/orchestrator
- Original parent: Sentinel
- Original parent conversation ID: 6cadad39-7b37-468d-bf2a-25a7a53af068

## 🔒 My Workflow
- **Pattern**: Project Pattern (Survey → Assess → Decompose & Delegate / Iteration Loop → E2E + Final Acceptance)
- **Scope document**: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT_V718.md
1. **Decompose**: Survey codebase, data (121 companies by GICS Sector/Sub-Industry), and specs; then decompose into module-aligned milestones + E2E testing verification.
2. **Dispatch & Execute**: Delegate milestones to sub-orchestrators (or direct iteration loops if small) with Explorer → Worker → Reviewer → Challenger → Auditor gates.
3. **On failure**: Retry → Replace → Skip (never skip Auditor) → Redistribute → Redesign.
4. **Succession**: Self-succeed at 16 spawns (when all non-sub-orch subagents complete).
- **Work items**:
  1. Survey (2 Explorers + 1 Spec Miner) [done]
  2. Architecture & Milestone Decomposition (PROJECT_V718.md) [done]
  3. Wave 1 Parallel Execution: R1 (`v718_worker_r1_engine`), R3 (`v718_worker_r3_ui_docs`), R4 (`v718_test_writer_r4`) [done]
  4. Wave 2 Delegation: R2 (10 US+EU GICS Sector/Sub-Industry evaluators + 1 ingest worker) [done]
  5. Wave 3 Final Verification Gate: 2 Reviewers + 2 Challengers + 1 Forensic Auditor [in-progress]
- **Current phase**: 2B (Iteration Loop — Wave 3 Verification Gate)
- **Current focus**: 2 Reviewers, 2 Challengers, and 1 Forensic Auditor independently verifying all R1–R4 acceptance criteria.

## 🔒 Key Constraints
- DISPATCH-ONLY orchestrator: NEVER write source code or run build/test commands directly; never inspect codebase files directly.
- Pass `ORIGINAL_REQUEST.md` path verbatim in EVERY subagent dispatch.
- R2 strict batching constraint: split evaluation agents strictly by GICS Sector / Sub-Industry across US and EU combined (NEVER split US vs. EU into separate evaluator agents).
- Preserve all Gate 1–4 scores (`1`, `2`, `3_*`, `3a`, `3b`, `3m`, `4_*`, `4`, `4n`), `thr_cap = 15`, `phase_results`, and Prime Grade (225) / Calamity (13 total / 11 < 3 G6 flags) counts.
- Never reuse a subagent after it delivers handoff — always spawn fresh.
- Forensic Auditor is non-skippable and has a binary veto.

## Current Parent
- Conversation ID: 6cadad39-7b37-468d-bf2a-25a7a53af068
- Updated: 2026-11-17T16:03:00Z

## Key Decisions Made
- Combined B1+B2 Banks into single 24-company US+EU batch (`v718_eval_b01`) since all 24 have `g6_default="N"`; total 10 US+EU combined sector batches covering all 121 companies.
- Wave 1 R1, R3, R4 all completed cleanly (`314/319` tests pass; 5 remaining await M2 + `CRM` snapshot).
- Wave 2 R2 evaluation + ingest + `CRM` sync (`5=0, 6="Y"`) + `build.py` + `--audit` + `unittest` all passed (`319/319` OK, `0` audit discrepancies).

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| v718_survey_explorer_engine | teamwork_explorer | Survey engine/UI/tests/baseline | completed | 9b6f22b4-2988-43a4-83ac-b54c0f85736a |
| v718_survey_explorer_data | teamwork_explorer | Survey data/121 companies/GICS | completed | 9a932438-3976-4993-8842-fdec5d99d17f |
| v718_survey_spec_miner | teamwork_spec_miner | Survey specs & Gate 5/6 rubrics | completed | 09af9fbd-dd0f-4fe3-bf08-8447a3ce888d |
| v718_worker_r1_engine | teamwork_worker | R1 apply_evaluation & bulk_scorer | completed | fa53d5cd-d3d7-4308-8279-f938e38a96c1 |
| v718_worker_r3_ui_docs | teamwork_worker | R3 dashboard, config 7.18 & specs | completed | 1de76415-6e4f-4bf9-ab07-07eedc73facc |
| v718_test_writer_r4 | teamwork_test_writer | R4 test alignment & v7.18 E2E suite | completed | 5e2271f2-c51f-443c-ae2f-525e93fb5800 |
| v718_eval_b01 | teamwork_worker | B01 Banks US+EU (24) | completed | 73babee6-8a8c-4f1c-ade5-2c5907d219f8 |
| v718_eval_b02 | teamwork_worker | B02 Non-Bank Financials US+EU (14) | completed | 3e9530a7-b6e9-46cd-88cf-51ea67e4ecd2 |
| v718_eval_b03 | teamwork_worker | B03 Ind Machinery/Elec/Cong US+EU (13) | completed | 69ec1336-b612-47b1-aa2e-e92151491538 |
| v718_eval_b04 | teamwork_worker | B04 Ind Infra/A&D/Transport US+EU (11) | completed | 7ef10351-9f66-4bc9-8638-6473348f0b5d |
| v718_eval_b05 | teamwork_worker | B05 IT Software/Consulting/Internet (10) | completed | cf1639a2-b8c1-43aa-b6a4-e4878a26b336 |
| v718_eval_b06 | teamwork_worker | B06 IT Semis/Instruments US+EU (8) | completed | 40b8f2cb-1ead-4123-b110-95080a807787 |
| v718_eval_b07 | teamwork_worker | B07 Health Care US+EU (8) | completed | 0f3b21a7-dada-40b6-a6c4-1eb1892d4658 |
| v718_eval_b08 | teamwork_worker | B08 ConsDisc & CommSvcs US+EU (10) | completed | be02d169-84da-4bab-9ec3-ea04d7a97582 |
| v718_eval_b09 | teamwork_worker | B09 Staples/Materials/Energy US+EU (10) | completed | e2a3d489-8176-42b1-9d1b-8744f24fb13d |
| v718_eval_b10 | teamwork_worker | B10 Real Estate & Utilities US+EU (13) | completed | 4d9437e8-367c-4228-a2a0-b6b869fda0b1 |
| v718_worker_r2_ingest | teamwork_worker | R2 ingest, CRM sync, audit, build & tests | completed | 3799e67d-6dff-4272-8b87-15970687ed55 |
| v718_reviewer_1 | teamwork_reviewer | Review R1/R3/R4/build/tests | completed | 45fe1f5f-e16a-4dda-b887-6aa4c42eb1e9 |
| v718_reviewer_2 | teamwork_reviewer | Review R2 121-company & peer calibration | completed | 4c0d1bd9-e9f3-4b43-a0f3-4ff61ec41ddc |
| v718_challenger_1 | teamwork_challenger | Challenge engine & dashboard runtime | completed | 707592cd-746d-4aab-8d47-f7138bb4c944 |
| v718_challenger_2 | teamwork_challenger | Challenge universe invariance & 121 audit | completed | 59dc2000-fdff-4924-b3c3-889d59a4a2e9 |
| v718_auditor_1 | teamwork_auditor | Forensic integrity audit (binary veto) | completed | 82d27462-fc9e-4402-947f-2c422f69ee49 |
| v718_iter2_explorer | teamwork_explorer | Iter 2 cascade fix & float check explorer | completed | 2b7e88ce-6c44-4b91-b265-4f92974bbaf4 |
| v718_iter2_worker | teamwork_worker | Iter 2 engine fix, regression tests & cleanup | completed | c6ff60b0-f441-4045-9592-688388a3e6b2 |
| v718_iter2_reviewer_1 | teamwork_reviewer | Iter 2 final code/build/tests reviewer | completed | cbd4044d-70bd-4f42-bb52-2f2eac5edc68 |
| v718_iter2_challenger_1 | teamwork_challenger | Iter 2 cascade/float challenger | completed | 958b2ba3-4e7a-4501-9aff-bf4da5963547 |
| v718_iter2_auditor_1 | teamwork_auditor | Iter 2 forensic integrity auditor | completed | 7837de1d-18e2-4b5a-a3f7-1289982bdb53 |

## Succession Status
- Succession required: no (direct Iteration Loop mode; max limit 128)
- Spawn count: 27 / 128
- Pending subagents: none
- Predecessor: none
- Successor: not applicable

## Active Timers
- Heartbeat cron: cancelled
- Safety timer: cancelled
- On succession: kill all timers before spawning successor
- On context truncation: handle timers as step 4 of the State Recovery section of your prompt says

## Artifact Index
- `.agents/teamwork/ORIGINAL_REQUEST.md` — Verbatim v7.18 user request
- `.agents/teamwork/orchestrator/DISPATCH.md` — Dispatch log
- `.agents/teamwork/orchestrator/progress.md` — Liveness & step checklist
