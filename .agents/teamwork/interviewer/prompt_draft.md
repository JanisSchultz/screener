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
