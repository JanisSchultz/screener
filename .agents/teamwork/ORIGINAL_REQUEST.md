# Original User Request

## Approved Task Prompt — 2026-11-16 10:32:12 UTC

Execute Phase 2 bulk re-scoring for the Quality & Moat Screener across all 989 companies reaching Gate 3 in the US, European, and Canadian universes according to the qualitative evaluation framework and deterministic CAP engine.

Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Integrity mode: development

## Requirements

### R1. Bulk Re-Scoring Across All Gate 3 Companies
Evaluate and score Gate 3 Moat Profiles (`3_tb`, `3_ia`, `3_se`, `3_rd`, and derived primary moat `3a`) and Gate 4 Competitive Forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, deterministic final CAP `4`, and mandatory `4n` Runway & Forces note whenever any force >= 1) for all 989 companies reaching Gate 3 across `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv`, adhering strictly to `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`. The team may structure batching and execution order as appropriate.

### R2. Waterfall Integrity, Mirror Synchronization, and Calamity Handling
Enforce the sequential Munger reject waterfall using `screener/apply_evaluation.py` (clearing downstream gate fields on gate rejection unless qualifying under Calamity pass rules for Gates 3b, 5, or 6). Synchronize dual-listed mirror tickers defined in `data/*/universe.json` (such as `ASML` and `ASML.NL`) so that scores, notes, and evidence match identically across universes.

### R3. Output Regeneration and Test Suite Alignment
Run `python3 build.py` to regenerate the screener outputs (`output/screener.html`, `output/index.html`, and `docs/index.html`). Run the full test suite (`python3 -m unittest discover tests`), updating the baseline universe count assertions in `tests/test_calamity_tier.py` to match the newly verified counts when scoring shifts companies between quality/calamity pass and rejected states.

## Verification Resources
- `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`
- 11 Phase 1 reference scored companies in `data/{us,eu,ca}/inputs.csv` (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`)
- Evaluation application engine: `python3 screener/apply_evaluation.py`
- Test suite: `python3 -m unittest discover tests`
- Build script: `python3 build.py`

## Acceptance Criteria

### Scoring and Data Completeness
- [ ] All 989 companies reaching Gate 3 have deterministic Gate 3 moat scores (`3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`) and Gate 4 force scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`) populated in `data/{us,eu,ca}/inputs.csv`.
- [ ] A non-empty `4n` Runway & Forces note is present for every scored company where at least one competitive force is >= 1.
- [ ] Dual-listed mirror companies have identical gate scores, notes, and evidence across universes.
- [ ] No manual overrides are applied to deterministic CAP calculations.

### System and Regression Verification
- [ ] All unit tests pass cleanly via `python3 -m unittest discover tests` with updated baseline counts in `tests/test_calamity_tier.py` reflecting legitimate score movements.
- [ ] `python3 build.py` runs cleanly with exit code 0, successfully compiling updated HTML reports in `output/` and `docs/`.


## Follow-up — 2026-11-16 10:49:42 UTC

Important architectural & specification guidance for M1, M2, and M3 (please forward immediately to the active orchestrator, `test_writer_m1`, and `worker_m2`):

1. **No Heuristic / Regex / Sector-Rule Scoring in `bulk_scorer.py`**:
   - Per `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`, the 4 Gate 3 Moat scores (`3_tb`, `3_ia`, `3_se`, `3_rd`), the 5 Gate 4 Competitive Force scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`), and the `4n` Runway & Forces notes are **qualitative investment evaluations**, NOT mechanical keyword/regex/sub-industry heuristics.
   - Do **NOT** have `screener/bulk_scorer.py` invent scores or templated `4n` strings via Python regexes or sector lookup tables. Instead, `bulk_scorer.py` (M2) should be a **batch context-exporter, deterministic CAP/waterfall batch-ingester, validator, and mirror-sync tool**, while **M3 dispatches parallel AI evaluator subagents in batches** to genuinely evaluate each company individually (using its business model, existing `3m`/`note`/`evidence`, financials in `data/*/financials.csv`, and competitive/macrotrend context) and write authentic, company-specific scores and `4n` notes.
   - Note also: if a company that previously failed Gate 4 (`CAP < 15`, leaving Gates `5` and `6` blank) shifts to `CAP >= 15` under honest re-scoring, the evaluator agent must also score Gates `5` and `6` so no company is left in `"To review (blank gate)"`.

2. **Waterfall Rule on the 989 Gate 3 Companies (R1 + R2 Alignment for `test_bulk_scoring_e2e.py`)**:
   - All **989** companies reaching Gate 3 (`1 == "Y"` and `2 == "Y"`) must have Gate 3 moat scores (`3_tb`, `3_ia`, `3_se`, `3_rd`, and derived `3a`) populated.
   - Per R2 (`screener/apply_evaluation.py` Munger sequential waterfall, illustrated by Phase 1 reference company `NUE`), the ~504 companies that **fail Gate 3** (`3a == "None"` or `3b == "N"` without `calamity == "Y"`) **must have Gate 4 (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`) and Gates 5–6 left blank (`""`)**.
   - Only companies that **pass Gate 3** (`3a != "None"` and `(3b == "Y"` or `calamity == "Y")`, ~485 companies) advance to Gate 4 and receive `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, deterministic `4`, and `4n` (mandatory whenever any Force >= 1). Make sure `tests/test_bulk_scoring_e2e.py` asserts this exact waterfall rule!


## Follow-up — 2026-11-16 11:04:01 UTC

Orchestration & quality note for M3 (978 remaining companies):
Assigning all 978 companies to a single `worker_m3_evaluator` risks context exhaustion or pressuring that single worker into writing a Python heuristic/keyword generator script to produce the 978 evaluations.

Please ensure the Orchestrator partitions M3 across **parallel batch evaluator subagents** (e.g., via sub-orchestrators managing ~15–20 batch evaluator workers of ~50–65 companies each writing separate batch JSON files, followed by a single merge/ingest step into `data/{us,eu,ca}/inputs.csv`) so every company receives genuine, individual AI qualitative judgment rather than rule-based script generation, and have the forensic auditor explicitly check that batch JSONs were authored by AI company evaluation rather than a heuristic Python generator script.
