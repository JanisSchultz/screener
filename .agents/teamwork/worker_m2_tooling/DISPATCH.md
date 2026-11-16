## 2026-11-16T10:45:28Z
You are the Scoring Tooling Worker for Milestone M2.
Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/worker_m2_tooling/
Workspace directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Original request path: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md
PROJECT.md path: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT.md
Parent conversation ID: 52860145-8fc7-4969-8b2b-b7788e50408a

Survey Reference Artifacts:
- /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_spec_miner/handoff.md
- /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_explorer_data/handoff.md
- /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_explorer_engine/handoff.md

EXCLUSIVE FILE WRITE OWNERSHIP:
You own exclusively:
- `screener/bulk_scorer.py` (or new helper script in `screener/`)
- Temporary evaluation files/directories if needed
You MUST NOT edit `tests/test_bulk_scoring_e2e.py`, `TEST_READY.md`, `tests/test_calamity_tier.py`, or modify `inputs.csv` directly yet (inputs.csv application is in M3).

TASK:
1. Build a robust bulk scoring automation engine/script in `screener/bulk_scorer.py`.
2. The script must:
   - Identify all 989 Gate 3 companies across `data/{us,eu,ca}/inputs.csv` (`1 == 'Y'` and `2 == 'Y'`).
   - Strictly preserve the 11 Phase 1 reference companies with their existing verified scores and notes (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`).
   - Implement the qualitative evaluation framework and deterministic CAP engine adhering to `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`:
     - Score Gate 3 Moat Profiles: `3_tb`, `3_ia`, `3_se`, `3_rd` on 0/1/2 based on business model archetype, switching costs, infrastructure/intangibles/brands, Nick Sleep scale economies shared, R&D leadership.
     - Score Gate 4 Competitive Forces: `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub` on 0/1/2 evaluated against the 5 Macrotrends and clock speed (presumptive `4_sub >= 1` for fast clock-speed tech/semi/pharma/hardware).
     - Deterministically calculate Step 1 Initial CAP and primary moat archetype `3a` using `screener/gates.py:compute_initial_cap_from_scores`.
     - Deterministically calculate Step 2 Final CAP (`4`) using `screener/gates.py:compute_final_cap_from_scores` with zero manual overrides.
     - Generate compliant `4n` Runway & Forces notes whenever any force >= 1 (stating Initial CAP, haircut, force codes, and rationale).
     - Apply evaluations via `screener/apply_evaluation.py` (or replicate `validate_and_waterfall` logic) so that the sequential Munger reject waterfall is strictly enforced (clearing downstream fields on gate rejections).
     - Synchronize dual-listed mirror tickers (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`) so scores, notes, and evidence match identically across universes.
3. Test the script with `--dry-run` and verify that generated scores, notes, and waterfall behaviors are 100% compliant with specifications.
4. Keep `progress.md` updated in your working directory. Deliver `handoff.md` with verification details and notify the orchestrator via `send_message`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## 2026-11-16T10:50:24Z
[CRITICAL ARCHITECTURAL DIRECTIVE FOR M2 WORKER]
No Heuristic / Regex / Sector-Rule Scoring in `bulk_scorer.py`:
1. Per `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`, the 4 Gate 3 Moat scores (`3_tb`, `3_ia`, `3_se`, `3_rd`), the 5 Gate 4 Competitive Force scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`), and the `4n` Runway & Forces notes are **qualitative investment evaluations**, NOT mechanical keyword/regex/sub-industry heuristics.
2. Do **NOT** have `screener/bulk_scorer.py` invent scores or templated `4n` strings via Python regexes or sector lookup tables. Instead, `bulk_scorer.py` (M2) should be a **batch context-exporter, deterministic CAP/waterfall batch-ingester, validator, and mirror-sync tool**, while **M3 dispatches parallel AI evaluator subagents in batches** to genuinely evaluate each company individually (using its business model, existing `3m`/`note`/`evidence`, financials in `data/*/financials.csv`, and competitive/macrotrend context) and write authentic, company-specific scores and `4n` notes.
3. Waterfall rule: The ~504 companies that fail Gate 3 (`3a == "None"` or `3b == "N"` without `calamity == "Y"`) must have Gate 4 (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`) and Gates 5–6 left blank (`""`). Only companies passing Gate 3 receive Gate 4 scores and `4n`. Ensure `bulk_scorer.py` ingestion and validation enforce this waterfall.
4. Note also: if a company that previously failed Gate 4 (`CAP < 15`, leaving Gates `5` and `6` blank) shifts to `CAP >= 15` under honest re-scoring, Gates `5` and `6` must also be ingested/scored so no company is left in `"To review (blank gate)"`.

## 2026-11-16T10:50:53Z
**Context**: Architectural Directive for Milestone M2 (`screener/bulk_scorer.py`).

**Content**: 
CRITICAL DIRECTIVE FROM SENTINEL / USER GUIDANCE:
1. **No Heuristic / Regex / Sector-Rule Scoring in `bulk_scorer.py`**:
   - Per `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`, Gate 3 Moat scores (`3_tb`, `3_ia`, `3_se`, `3_rd`), Gate 4 Force scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`), and `4n` notes are **qualitative investment evaluations**, NOT mechanical keyword/regex/sub-industry heuristics.
   - Do **NOT** have `screener/bulk_scorer.py` invent scores or templated `4n` strings via Python regexes or sector lookup tables.
   - Instead, `bulk_scorer.py` must serve as a **batch context-exporter, deterministic CAP/waterfall batch-ingester, validator, and mirror-sync tool**:
     - (a) Exports batch evaluation context payloads (company metadata, existing `3m`/`note`/`evidence`, financials from `data/*/financials.csv`, sector/sub-industry) so evaluator agents in M3 can evaluate them.
     - (b) Ingests evaluation JSON payloads (or batches of evaluated companies), validates scores/notes, applies deterministic CAP and primary moat formulas, applies the sequential Munger reject waterfall (clearing downstream fields on gate rejections per `screener/apply_evaluation.py`), and synchronizes dual-listed mirrors (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`).
     - (c) Preserves the 11 reference companies strictly.
     - (d) Validates that if a company previously failing Gate 4 shifts to CAP >= 15, Gates 5 and 6 are populated.

**Action**: Implement `screener/bulk_scorer.py` strictly according to this tooling/pipeline specification (exporter, ingester, validator, mirror-sync) and do NOT hardcode scoring heuristics.


