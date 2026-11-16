# BRIEFING — 2026-11-16T10:46:00Z

## Mission
Build a robust bulk scoring automation engine/script in `screener/bulk_scorer.py` adhering to qualitative evaluation specs, preserving reference tickers, computing initial and final CAP deterministically, enforcing Munger reject waterfalls, and synchronizing mirror tickers.

## 🔒 My Identity
- Archetype: scoring_tooling_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/worker_m2_tooling
- Original parent: 52860145-8fc7-4969-8b2b-b7788e50408a
- Milestone: M2

## 🔒 Key Constraints
- Exclusively own `screener/bulk_scorer.py` (or new helper script in `screener/`), temporary evaluation files/directories, and worker working directory.
- MUST NOT edit `tests/test_bulk_scoring_e2e.py`, `TEST_READY.md`, `tests/test_calamity_tier.py`, or modify `inputs.csv` directly.
- Identify all 989 Gate 3 companies across `data/{us,eu,ca}/inputs.csv` (`1 == 'Y'` and `2 == 'Y'`).
- Strictly preserve the 11 Phase 1 reference companies with existing verified scores and notes (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`).
- Adhere strictly to `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`.
- Deterministic CAP engine (`compute_initial_cap_from_scores`, `compute_final_cap_from_scores`) with zero manual overrides.
- Synchronize dual-listed mirror tickers (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`).
- Maintain genuine logic without cheating or facade implementations.

## Current Parent
- Conversation ID: 52860145-8fc7-4969-8b2b-b7788e50408a
- Updated: not yet

## Task Summary
- **What to build**: `screener/bulk_scorer.py`
- **Success criteria**: Genuine bulk scorer that identifies 989 Gate 3 companies, preserves 11 reference tickers, scores moats (Gate 3) and competitive forces (Gate 4) according to specs, computes deterministic CAPs, generates valid notes, enforces waterfall (or via apply_evaluation), syncs mirror tickers, and supports `--dry-run`.
- **Interface contracts**: `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `screener/apply_evaluation.py`, `screener/gates.py`
- **Code layout**: `screener/`

## Key Decisions Made
- Architecture follows Critical Architectural Directive (2026-11-16T10:50:53Z): `screener/bulk_scorer.py` is implemented as a robust batch context-exporter, deterministic CAP/waterfall batch-ingester, validator, and mirror-sync tool. It strictly rejects any mechanical keyword/regex/sector heuristics for qualitative scores.
- M3 will use this tool to export batches for genuine AI evaluator subagents, and ingest/validate evaluation payloads with strict Munger waterfall enforcement and mirror synchronization.
- Reference companies (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`) are strictly preserved and guarded against modification or regression.


## Artifact Index
- `.agents/teamwork/worker_m2_tooling/DISPATCH.md` — Initial assignment
- `.agents/teamwork/worker_m2_tooling/progress.md` — Liveness & task progress
- `.agents/teamwork/worker_m2_tooling/BRIEFING.md` — Agent briefing & situational awareness

## Change Tracker
- **Files modified**: `screener/bulk_scorer.py` (new tooling engine for M2/M3 batch evaluation pipeline)
- **Build status**: All 303 repo tests pass; all 8 bulk scorer unit tests pass
- **Pending issues**: None for M2. Ready for M3 execution.

## Quality Status
- **Build/test result**: Pass (303/303 unit tests pass; 8/8 bulk scorer tests pass)
- **Lint status**: Clean (py_compile validated)
- **Tests added/modified**: `.agents/teamwork/worker_m2_tooling/test_bulk_scorer.py` (8 behavioral test cases)

## Loaded Skills
- None

