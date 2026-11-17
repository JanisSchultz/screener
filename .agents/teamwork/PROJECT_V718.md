# Project: Quality & Moat Screener v7.18 — Two-Stage Munger Waterfall & Diagnostic Gate 5–6 Scorecard

## Architecture
- **Data Layer**: `data/{us,eu,ca}/inputs.csv` (1,175 total: 989 Gate 3, 504 Gate-3 rejects, 485 Gate-3 advancing = 364 complete + 121 incomplete [108 Gate-4 CAP<15Y rejects + 13 Gate-5 5=0 rejects]), `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`, `universe.json` (mirrors `ASML`/`ASML.NL`, `FER`/`FER.ES`).
- **Evaluation Engine (R1)**:
  - `screener/apply_evaluation.py`: Two-Stage Waterfall validation (`validate_and_waterfall`). Stage 1 (`1="N"`, `2="N"`, `3a="None"`, or unwaived `3b="N"`) scrubs downstream fields and clears calamity. Stage 2 (advancing past Gate 3) preserves diagnostic `5` and `6` even when `4 < 15` or `5 = 0`, keeps `clear_calamity(...)` when `4 < 15`, and validates `5 in {0, 1, 2}` and `6 in {"Y", "N"}` whenever supplied.
  - `screener/bulk_scorer.py`: `validate_company_evaluation` preserves `5` and `6` on `CAP < 15` and `6` on `5 = 0`, validates `5` (`0/1/2`) and `6` (`Y/N`), and warns if any Gate-3-advancing company leaves `5` or `6` blank. `audit_gate_3_universe` keeps Gate-3 failures blank on `G4–G6` and enforces non-empty valid `5` and `6` across all 485 Gate-3-advancing companies. `REFERENCE_SNAPSHOT["CRM"]` updated once `CRM`'s verified `5` and `6` scores are recorded.
- **Core Funnel Invariance (`screener/gates.py`)**: Unchanged. `thr_cap = 15`, `phase_results` short-circuits on non-waived Gate 4 / Gate 5 failure, keeping Prime Grade (225) and Prime Grade Calamity (13 total / 11 `< 3` G6 flags) invariant.
- **UI & Docs (R3)**: `screener/dashboard.py` (scored stepper sub-labels in `openDrawer`, 2-card G5/G6 row below Moat Archetype/CAP, `#dossier-g6-answer`, `g5_mgmt`/`g6_cash` in `ALL_COLS` and expanded `moat_universe`/`all` views with `compactKeys`, `qpass`, `calamity` unchanged), `screener/config.py` (`SCREENER_VERSION = "7.18"`, `CHANGELOG`), `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`.
- **Build & Test Layer (R4)**: `build.py` (`output/screener.html`, `output/index.html`, `docs/index.html`), `tests/test_calamity_tier.py`, `tests/test_bulk_scoring_e2e.py`, `tests/test_v718_two_stage_waterfall.py`.

## Code Layout
- `screener/apply_evaluation.py` — Two-Stage Waterfall cleaner & validator
- `screener/bulk_scorer.py` — Batch ingestion, validation, `REFERENCE_SNAPSHOT`, `--audit`
- `screener/gates.py` — Core gate funnel & `phase_results` (read-only / invariant)
- `screener/dashboard.py` — Dashboard HTML/JS generator
- `screener/config.py` — `SCREENER_VERSION = "7.18"` and `CHANGELOG`
- `data/us/inputs.csv`, `data/eu/inputs.csv` — 121 incomplete moat franchises (66 US, 55 EU; 0 CA)
- `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md` — Normative specs
- `tests/test_calamity_tier.py`, `tests/test_bulk_scoring_e2e.py`, `tests/test_v718_two_stage_waterfall.py` — Unit & E2E tests
- `build.py` → `output/screener.html`, `output/index.html`, `docs/index.html`

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | Two-Stage Waterfall in `apply_evaluation.py` | Keep Stage 1 G1–G3 scrubbing; remove G5/G6 scrubbing on `CAP < 15` and G6 scrubbing on `5=0`; keep `clear_calamity` on `CAP < 15`; validate `5 in {0,1,2}` & `6 in {"Y","N"}` | M1 | R1, engine survey |
| 2 | Validation & Audit in `bulk_scorer.py` | Update `validate_company_evaluation` (preserve G5/G6, validate `5`/`6`, warn blank G5/G6 past G3); update `audit_gate_3_universe` (485 non-empty valid G5/G6, 504 G3-rejects blank G4–G6) | M1 | R1, engine survey |
| 3 | 121-Company G5/G6 Qualitative Evaluation | Score `5` (`0/1/2`) on 108 G4-rejects (preserving `5=0` on 13 G5-rejects) and `6` (`Y/N`) on all 121 across US+EU combined strictly by GICS Sector/Sub-Industry vs 364 completed peers; strip waterfall-bypass sentences, fix `CRM` `CAP = 5Y` note, append `[Diagnostic G5=... \| G6=...: ...]` | M2 | R2, data survey, spec miner |
| 4 | `CRM` Snapshot & Worked Example Sync | Update `REFERENCE_SNAPSHOT["CRM"]` in `bulk_scorer.py` and Example 4 (`CRM`) in `COMPANY_EVALUATION_SPEC.md` with verified `5` & `6` scores | M4 | R1, R2, R3 |
| 5 | Dashboard `openDrawer` Stepper & 2-Card G5/G6 Row | Scored stepper sub-labels (`PASS · 25Y`, `FAIL · 10Y`, `PASS · 2/2`, `FAIL · 0/2`, `PASS · Y`, `FAIL · N`, preserve `WAIVED`, safe `0` check); 2-card G5/G6 row below Moat Archetype/CAP + `#dossier-g6-answer` | M3 | R3, engine survey |
| 6 | Dashboard Expanded Columns (`g5_mgmt`, `g6_cash`) | Add `g5_mgmt` (`G5 Mgmt`) & `g6_cash` (`G6 B/S`) to `ALL_COLS`, `COL_TIPS`, and expanded `moat_universe`/`all` tables while preserving `compactKeys`, `qpass`, `calamity` | M3 | R3, engine survey |
| 7 | Version Bump & Changelog (`7.18`) | Bump `SCREENER_VERSION = "7.18"` and add `"7.18"` `CHANGELOG` entry in `screener/config.py` | M3 | R3 |
| 8 | Specification Updates (Two-Stage Waterfall) | Update all 8 locations in `QUALITATIVE_EVALUATION_SPEC.md` and 8+1 (`CRM`) locations in `COMPANY_EVALUATION_SPEC.md` | M3 (prose/tables), M4 (`CRM` Ex.4) | R3, spec miner |
| 9 | Test Suite Alignment & E2E Coverage | Update `tests/test_calamity_tier.py`, `tests/test_bulk_scoring_e2e.py` (`test_t1_f7_04`, `test_t1_f7_05`, `test_all_989_gate3_companies_completed`), and add v7.18 Two-Stage Waterfall & dashboard tests | E2E Track | R4, engine survey |
| 10 | Final Build, Audit, Adversarial Hardening & Invariance | Run `bulk_scorer.py --audit` (0 errors), `build.py` (225 Prime Grade, 11/13 Calamity), `unittest` (100% pass), Tier 5 adversarial & forensic audit | M4 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Engine Waterfall & Audit Core (R1) | Update `screener/apply_evaluation.py` and `screener/bulk_scorer.py` (excl. final `CRM` snapshot values); verify via unit checks | none | PLANNED |
| M3 | Dashboard UI, Version Bump & Spec Docs (R3) | Update `screener/dashboard.py`, `screener/config.py`, `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md` (excl. final `CRM` Ex.4 values) | none | PLANNED |
| E2E | Test Alignment & Opaque-Box E2E Track (R4) | Update `tests/test_calamity_tier.py`, `tests/test_bulk_scoring_e2e.py`, add `tests/test_v718_two_stage_waterfall.py`, publish `.agents/teamwork/TEST_READY_V718.md` | none (authoring) | PLANNED |
| M2 | 121-Company Sector-Combined G5/G6 Evaluation (R2) | Evaluate all 121 incomplete companies across 10 US+EU GICS Sector/Sub-Industry batches; ingest into `data/{us,eu}/inputs.csv`; preserve G1–G4 & 13 `5=0`; clean `note` + append `[Diagnostic ...]` | M1 | PLANNED |
| M4 | Final Integration, Build, Audit & Tier 5 Acceptance | Update `REFERENCE_SNAPSHOT["CRM"]` & `CRM` Ex.4; run `--audit`, `build.py`, full `unittest`; run Tier 5 adversarial verification & forensic audit | M1, M2, M3, E2E | PLANNED |

## Interface Contracts
### `screener/apply_evaluation.py` ↔ `screener/bulk_scorer.py` ↔ `data/*/inputs.csv`
- Stage 1 failure (`1="N"`, `2="N"`, `3a="None"`, or `3b="N"` without `calamity="Y"`): scrub downstream fields (`4_*`, `4`, `4n`, `5`, `6` for Gate 3 fail) and clear `calamity` / `calamity_note`.
- Stage 2 (`1="Y"`, `2="Y"`, `3a!="None"`, and `3b="Y"` or `calamity="Y"`):
  - `4 < 15`: non-waivable Anchor Gate clears `calamity` / `calamity_note` (`""`), **preserves** `5` (`0/1/2`) and `6` (`Y/N`).
  - `5 == 0` without `calamity="Y"`: **preserves** `6` (`Y/N`).
  - Both `5` (valid `0/1/2`) and `6` (valid `"Y"`/`"N"`) are mandatory for all 485 Gate-3-advancing rows in `audit_gate_3_universe`.
- `note` convention for the 121 Stage-2 incomplete rows: strip `Downstream (?:gates?|Gates? (?:5-6|6)) bypassed per (?:strict )?waterfall\.`, fix `CRM`'s `CAP = 10` prose to `CAP = 5Y`, append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`. Keep Gate 1–4 columns (`1`, `2`, `3_*`, `3a`, `3b`, `3m`, `4_*`, `4`, `4n`) 100% untouched.

### Dashboard JS ↔ Data Payload (`screener/dashboard.py`)
- `company_record` already provides `g4_cap`, `g5_mgmt` (`int` `0/1/2` or `None`), `g6_cash` (`"Y"`/`"N"` or `None`), `g6_answer` (`"Y"`/`"N"` or `None`).
- JS checks `v !== null && v !== undefined && v !== ''` (never truthiness on `0`).
- `ALL_COLS.g5_mgmt` and `ALL_COLS.g6_cash` are added ONLY to `moat_universe` and `all` expanded column arrays (`compactKeys`, `qpass`, and `calamity` remain untouched).
