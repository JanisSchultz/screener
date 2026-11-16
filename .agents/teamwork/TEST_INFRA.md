# E2E Test Infra: Quality & Moat Screener Phase 2 Bulk Re-Scoring

## Test Philosophy
- Opaque-box, requirement-driven. Derived strictly from `ORIGINAL_REQUEST.md`, `QUALITATIVE_EVALUATION_SPEC.md`, and `COMPANY_EVALUATION_SPEC.md`.
- No dependency on internal module shortcuts.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## Feature Inventory & Test Mapping
| # | Feature | Source (Requirement) | Tier 1 (Feature Coverage) | Tier 2 (Boundary & Corner) | Tier 3 (Cross-Feature) | Tier 4 (Real-World) |
|---|---------|---------------------|:------------------------:|:--------------------------:|:----------------------:|:--------------------:|
| 1 | Gate 3 Moat Profiles Scoring (3_tb, 3_ia, 3_se, 3_rd) | R1, Specs §3 | 5 test cases | 5 test cases | ✓ | ✓ |
| 2 | Initial CAP & 3a Derivation | R1, Specs §3 | 5 test cases | 5 test cases | ✓ | ✓ |
| 3 | Gate 4 Competitive Forces Scoring (4_ent, 4_riv, 4_buy, 4_sup, 4_sub) | R1, Specs §3 | 5 test cases | 5 test cases | ✓ | ✓ |
| 4 | Deterministic Final CAP Engine (Haircuts & Fatal Flaw) | R1, Specs §3 | 5 test cases | 5 test cases | ✓ | ✓ |
| 5 | Mandatory 4n Runway & Forces Note | R1, Specs §3 | 5 test cases | 5 test cases | ✓ | ✓ |
| 6 | Preservation of 11 Reference Companies | Verification Resources | 5 test cases | 5 test cases | ✓ | ✓ |
| 7 | Sequential Munger Waterfall Clearing | R2, Specs §1 | 5 test cases | 5 test cases | ✓ | ✓ |
| 8 | Dual-Listed Mirror Synchronization (ASML, FER) | R2, Specs §1 | 5 test cases | 5 test cases | ✓ | ✓ |
| 9 | Calamity Pass Rules Integrity | R2, Specs §5 | 5 test cases | 5 test cases | ✓ | ✓ |
| 10 | Unit Test Suite & Baseline Universe Counts | R3, Acceptance Criteria | 5 test cases | 5 test cases | ✓ | ✓ |
| 11 | Cockpit Output Regeneration (build.py) | R3, Acceptance Criteria | 5 test cases | 5 test cases | ✓ | ✓ |

## Test Architecture
- Test Suite Runner: `python3 -m unittest tests/test_bulk_scoring_e2e.py`
- Test Assertions:
  - 100% of the 989 Gate 3 companies have deterministic Gate 3 moat scores (`3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`) and Gate 4 force scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`) populated.
  - Every company with any force $\ge 1$ has non-empty `4n`.
  - Zero manual CAP overrides (every CAP `4` matches `compute_final_cap_from_scores`).
  - Dual-listed mirror companies (`ASML`/`ASML.NL`, `FER`/`FER.ES`) match identically across scores, notes, and evidence.
  - Sequential Munger reject waterfall: downstream fields cleared on gate rejections unless Calamity pass.
  - Calamity pass companies satisfy anchor gates and have valid 3-part `calamity_note`.
  - Full unit test suite passes cleanly with updated baseline counts in `tests/test_calamity_tier.py`.
  - `build.py` runs cleanly with exit code 0 and regenerates `output/screener.html`, `output/index.html`, and `docs/index.html`.

## Coverage Thresholds
- Tier 1: $\ge 5$ test assertions per feature ($\ge 55$ test cases)
- Tier 2: $\ge 5$ boundary/corner cases per feature ($\ge 55$ test cases)
- Tier 3: Pairwise feature interactions across all universes ($\ge 11$ test cases)
- Tier 4: Real-world portfolio scenarios ($\ge 6$ test cases)
- Total Minimum: $\ge 127$ test assertions in the E2E verification suite.
