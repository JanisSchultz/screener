## 2026-11-16T11:00:10Z
You are the Bulk Evaluation Worker for Milestone M3.
Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/worker_m3_evaluator/
Workspace directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Original request path: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md
PROJECT.md path: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT.md
TEST_READY.md path: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/TEST_READY.md
Parent conversation ID: 52860145-8fc7-4969-8b2b-b7788e50408a

EXCLUSIVE FILE WRITE OWNERSHIP:
You own exclusively:
- `data/us/inputs.csv`
- `data/eu/inputs.csv`
- `data/ca/inputs.csv`
- `evaluations/` directory
You MUST NOT edit test files or screener engine code.

TASK & INSTRUCTIONS:
Execute Milestone M3 — Bulk Re-Scoring Across All 989 Gate 3 Companies and Waterfall Application:

1. **Evaluation Framework Adherence**:
   Adhere strictly to `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`.
   - Evaluate all 989 companies reaching Gate 3 (`1 == 'Y'` and `2 == 'Y'`) across `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv`.
   - For all 989 companies, evaluate Gate 3 Moat Profiles: score `3_tb`, `3_ia`, `3_se`, `3_rd` on 0/1/2 based on business model archetype, switching costs, infrastructure/intangibles/brands, Nick Sleep scale economies shared, R&D leadership.
   - Initial CAP and derived primary moat `3a` are computed deterministically via `screener/gates.py:compute_initial_cap_from_scores`.
   - Sequential Munger reject waterfall:
     - Companies that FAIL Gate 3 (`3a == 'None'` or `3b == 'N'` without `calamity == 'Y'`, ~504 companies) MUST have Gate 4 (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`) and Gates 5-6 left blank (`""`)!
     - Companies that PASS Gate 3 advance to Gate 4 and receive full Porter force scores: `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub` on 0/1/2 evaluated against the 5 Macrotrends & clock speed (presumptive `4_sub >= 1` for fast clock-speed tech/semi/pharma/hardware).
     - Step 2 Final CAP (`4`) is computed deterministically via `screener/gates.py:compute_final_cap_from_scores` with zero manual overrides.
     - Mandatory `4n` Runway & Forces note populated whenever any competitive force >= 1 (citing Initial CAP, haircut, force codes, and rationale).
     - If Final CAP >= 15, ensure Gate 5 and Gate 6 are populated so no company is left in `'To review (blank gate)'`.
   - Strictly PRESERVE the 11 Phase 1 reference companies with their existing verified scores and notes (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`).
   - SYNCHRONIZE dual-listed mirror tickers defined in `data/*/universe.json` (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`) so that all qualitative scores, notes (`4n`, `note`), and `evidence` match identically across universes.

2. **Execution Process**:
   - Utilize `screener/bulk_scorer.py`:
     - You can use `python3 screener/bulk_scorer.py --export-batch` to inspect dossiers.
     - You can generate evaluated batch JSON payloads or evaluate companies, and ingest them via `python3 screener/bulk_scorer.py --ingest <path> --apply` which automatically enforces the deterministic formulas, waterfall clearing, and validations.
     - Run `python3 screener/bulk_scorer.py --sync-mirrors --apply` to ensure 100% mirror parity.
     - Run `python3 screener/bulk_scorer.py --audit` to audit all 989 companies.
   - Run `python3 -m unittest tests/test_bulk_scoring_e2e.py` to verify that all E2E tests pass (with 0 formula discrepancies, 0 missing `4n` notes, 0 waterfall violations, and 0 mirror mismatches).

3. **Deliverables**:
   - Updated `data/us/inputs.csv`, `data/eu/inputs.csv`, `data/ca/inputs.csv`.
   - Run `python3 screener/bulk_scorer.py --audit` and document clean audit results.
   - Run `python3 -m unittest tests/test_bulk_scoring_e2e.py` and document 100% passing results.
   - Deliver `handoff.md` and notify the orchestrator via `send_message`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## 2026-11-16T11:04:21Z
[DIRECTIVE TO M3 WORKER]
Do NOT attempt to score all 978 companies within a single worker context or write a Python heuristic/regex/keyword script to generate evaluations. The orchestrator is restructuring M3 into parallel batch evaluator workers of ~50–65 companies each. Any batch evaluations must reflect authentic, individual AI qualitative evaluation. Stand by for partitioned batch assignments or sub-orchestrator delegation.

## 2026-11-16T11:04:53Z
**Context**: Scope Adjustment for `worker_m3_evaluator` per Sentinel Architectural Directive.

**Content**: 
CRITICAL DIRECTIVE FROM SENTINEL:
M3 is being partitioned across parallel batch evaluator subagents (~60–65 companies per batch) to ensure genuine, individual AI qualitative judgment rather than a monolithic script.
Your role is now focused as the **Batch Context Exporter & Ingestion Coordinator**:
1. Run `python3 screener/bulk_scorer.py --export-batch --out-dir evaluations/batches --batch-size 65`.
   This will export the 978 unscored companies into 15 clean batch files (`evaluations/batches/batch_01.json` through `batch_15.json`), with each company's metadata, existing qualitative notes (`3m`/`note`/`evidence`), 5-10Y financials, sales CAGRs, and clock speed flag.
2. Confirm the 15 batch files are exported and list their filenames and company counts.
3. Once exported, write `handoff.md` and report back to the orchestrator via `send_message`.
Do NOT attempt to score all 978 companies yourself; parallel evaluator agents will be dispatched to evaluate the individual batch dossiers.

**Action**: Execute step 1 to export the 15 batch dossiers, document in `handoff.md`, and notify the orchestrator.


