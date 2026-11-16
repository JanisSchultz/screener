# Project: Quality & Moat Screener — Phase 2 Bulk Re-Scoring

## Architecture
- **Data Layer**: `data/{us,eu,ca}/inputs.csv` (1,175 universe companies, 989 reaching Gate 3), `data/*/universe.json` (universe metadata, mirrors).
- **Evaluation Engine**: `screener/apply_evaluation.py` (Munger waterfall clearing, deterministic CAP and primary moat derivation, calamity validation).
- **Core Domain Logic**: `screener/gates.py` (`compute_initial_cap_from_scores`, `compute_final_cap_from_scores`, `phase_results`, `cap_audit`, `par_valuation`), `screener/config.py` (canonical archetypes, force definitions, calamity gates).
- **Output Compilation**: `build.py` and `screener/dashboard.py` (generates `output/screener.html`, `output/index.html`, and `docs/index.html`).
- **Test Infrastructure**: `tests/` (`test_calamity_tier.py`, `test_cap_engine.py`, `test_valuation_sandbox.py`, etc., plus new Phase 2 E2E test suite).

## Code Layout
- `data/us/inputs.csv`: US universe qualitative and quantitative inputs (445 Gate 3 companies)
- `data/eu/inputs.csv`: EU universe qualitative and quantitative inputs (495 Gate 3 companies)
- `data/ca/inputs.csv`: CA universe qualitative and quantitative inputs (49 Gate 3 companies)
- `data/us/universe.json`: Mirror mappings (`ASML` <-> `eu:ASML.NL`, `FER` <-> `eu:FER.ES`)
- `screener/apply_evaluation.py`: Deterministic evaluation ingestion and waterfall cleaner
- `screener/gates.py`: Deterministic CAP math and gate logic
- `tests/test_calamity_tier.py`: Universe baseline funnel count assertions
- `tests/test_cap_engine.py`: CAP engine assertions and reference company tests
- `tests/test_bulk_scoring_e2e.py`: Phase 2 E2E verification test harness
- `build.py`: Cockpit HTML build generator

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Gate 3 Moat Profiles Scoring | Orthogonal 4-archetype moat scoring (`3_tb`, `3_ia`, `3_se`, `3_rd`) on 0/1/2 scale for all 989 Gate 3 companies | M3 | R1, survey |
| 2 | Initial CAP & 3a Derivation | Deterministic Step 1 Initial CAP (0Y, 15Y, 20Y, 25Y, 30Y) and primary moat archetype `3a` derivation | M2, M3 | R1, survey |
| 3 | Gate 4 Competitive Forces Scoring | Porter's 5 forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`) on 0/1/2 scale evaluated against 5 Macrotrends & clock speed for companies passing Gate 3 (~485 companies) | M3 | R1, survey |
| 4 | Deterministic Final CAP Engine | Deterministic Step 2 Final CAP (`4`): moderate haircuts $h(c_1)$ and fatal-flaw caps ($c_2 \ge 1 \implies \le 10\text{Y}$) | M2, M3 | R1, survey |
| 5 | Mandatory 4n Runway & Forces Note | Qualitative justification note populated whenever any competitive force $\ge 1$ | M3 | R1, survey |
| 6 | Preservation of Reference Companies | Strict preservation of 11 Phase 1 reference companies (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`) | M2, M3 | R1, survey |
| 7 | Sequential Munger Waterfall Clearing | Automatic clearing of downstream fields on gate rejection (companies failing Gate 3 have Gate 4-6 left blank `""`; companies failing Gate 4 have Gates 5-6 blank) via `screener/apply_evaluation.py` | M2, M3 | R2, survey |
| 8 | Dual-Listed Mirror Synchronization | Identical qualitative gate scores, notes (`4n`, `note`), and `evidence` synchronized across mirror tickers (`ASML`/`ASML.NL` and `FER`/`FER.ES`) | M3 | R2, survey |
| 9 | Calamity Pass Rules Integrity | Calamity flag and 3-part `calamity_note` strictly guarded by Anchor Gates 1, 2, 3a, 4; eligible only for Gates 3b, 5, 6 | M3 | R2, survey |
| 10 | Test Suite Alignment & Baseline Counts | Update baseline universe count assertions in `tests/test_calamity_tier.py` to match verified counts and ensure 100% unit test pass | M4 | R3, survey |
| 11 | Cockpit Output Regeneration | Run `build.py` to compile `output/screener.html`, `output/index.html`, and `docs/index.html` with exit code 0 | M4 | R3, survey |
| 12 | Opaque-Box E2E Test Suite (Tiers 1-4) | Comprehensive independent test suite validating all acceptance criteria without depending on internal implementation details | M1, M5 | Project Pattern, R1-R3 |
| 13 | Adversarial Coverage Hardening (Tier 5) | White-box adversarial testing, edge cases, stress testing, and forensic integrity audit | M5 | Project Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | E2E Test Suite & Infrastructure | Implement opaque-box E2E test harness (`tests/test_bulk_scoring_e2e.py`) covering all acceptance criteria, publish `TEST_READY.md` | none | DONE |
| M2 | Bulk Scoring Engine & Automation Tooling | Implement verified batch scoring engine/tooling enforcing deterministic rules, reference preservation, and mirror synchronization | none | DONE |
| M3 | 989 Company Bulk Re-Scoring & Waterfall Application | Execute qualitative evaluation across all 989 Gate 3 companies (US: 445, EU: 495, CA: 49) and apply Munger waterfall clearing | M2 | DONE |
| M4 | Test Baseline Update & Cockpit Build | Update `tests/test_calamity_tier.py` baseline counts, run full unit test suite (100% pass), and compile `build.py` | M3 | DONE |
| M5 | Final Acceptance: E2E Tests & Adversarial Audit | Pass 100% of E2E test suite (Phase 1) and pass adversarial coverage hardening & forensic integrity audit (Phase 2) | M1, M4 | DONE |

## Interface Contracts
### Bulk Scoring Tooling (`screener/bulk_scorer.py`) ↔ Data Layer
- Role: Batch context-exporter, deterministic CAP/waterfall batch-ingester, validator, and mirror-sync tool (no heuristic regex/lookup tables).
- Context Exporter: Exports company metadata, existing qualitative notes (`3m`/`note`/`evidence`), financial statements (`data/*/financials.csv`), and sector/clock-speed context into evaluation batch payloads for M3 evaluator agents.
- Batch Ingestion: Ingests completed evaluations, calculates deterministic Step 1 Initial CAP & 3a, applies Step 2 Final CAP & haircuts/fatal flaw caps, validates mandatory `4n` when forces $\ge 1$, applies sequential Munger waterfall clearing via `apply_evaluation.py` logic, and synchronizes mirror tickers.
- Inputs: Evaluated JSON payloads adhering to qualitative specifications.
- Outputs: Updated `data/{us,eu,ca}/inputs.csv` adhering strictly to schema and waterfall invariants.
- Error Handling: Invalid subscores, missing `4n` when force $\ge 1$, or unpopulated Gates 5–6 when shifting from CAP $<15$ to $\ge 15$ are rejected with actionable errors before writing.

### Mirror Synchronization Contract
- Mirror pairs defined: `data/us/universe.json["mirror"]` (`ASML` <-> `eu:ASML.NL`, `FER` <-> `eu:FER.ES`)
- Synchronization fields: `3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`, `3b`, `3m`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`, `calamity`, `calamity_note`, `note`, `evidence`
- Parity: Exact 100% character-for-character equality required across both records
