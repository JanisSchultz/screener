# Dispatch Assignment
- Agent ID: `teamwork_challenger_iter1_1`
- Role: Empirical Engine, Data & Waterfall Adversarial Challenger
- Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/teamwork_challenger_iter1_1`
- Original Request: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
- Parent Conversation ID: `c307c0cf-44ac-4f26-a3e8-55de8491f05c`
## 2026-11-18T10:01:49Z
Sender: c307c0cf-44ac-4f26-a3e8-55de8491f05c
Objective: Empirically and adversarially stress-test the v7.19 engine, waterfall scrubbing, mirror parity, SQLite schema, and passes_growth_0g cohort calculations. Do NOT modify project source files or output/ files.
Checks:
1. Synthetic Legacy Calamity Rejection Stress Tests (apply_evaluation.validate_and_waterfall, bulk_scorer.validate_company_evaluation, gates.phase_results)
2. Independent Live Dataset & passes_growth_0g Recomputation (1,175 companies, counts, near-boundary probes, us:APD/us:EL, 11 former calamity rows)
3. Mirror & SQLite Verification (ASML/ASML.NL, FER/FER.ES, fundamentals.sqlite)
4. python3 screener/bulk_scorer.py --audit
