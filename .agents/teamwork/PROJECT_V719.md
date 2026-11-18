# Project: Quality & Moat Screener — v7.19 (`Calamity` Retirement & `💎 Growth at ~0g`)

## Architecture
- **Data Layer**: `data/{us,eu,ca}/inputs.csv` (`1,175` companies, `989` Gate 3), `data/*/universe.json` (`ASML` <-> `eu:ASML.NL`, `FER` <-> `eu:FER.ES`), `data/fundamentals.sqlite` (`27`-column `companies` table).
- **Evaluation & Gate Engine**: `screener/config.py` (`SCREENER_VERSION = "7.19"`, `CHANGELOG`), `screener/data.py` (`TAIL_FIELDS = ["note", "evidence"]`), `screener/gates.py` (`phase_results`, `funnel_ids`, `par_valuation`), `screener/apply_evaluation.py` (unconditional Stage-1 G1–G3 scrubbing, Stage-2 G4–G6 diagnostic preservation), `screener/bulk_scorer.py` (`--audit` and batch ingestion).
- **Dashboard & Build**: `screener/dashboard.py` (`passes_growth_0g`, 5-tab bar: `🛡️ Prime Grade` → `💎 Growth at ~0g` → `🏰 Quality Grade` → `🔍 Full Universe` → `📖 Framework`), `build.py` (`output/screener.html`, `output/index.html`, `docs/index.html`), `fetch_market_data.py`.
- **Specs & Tests**: `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `QUANTITATIVE_EVALUATION_SPEC.md`, `README.md`, `tests/`.

## Code Layout
- `screener/config.py`: Canonical version, constants, `CHANGELOG`
- `screener/data.py`: CSV column schema (`TAIL_FIELDS`)
- `screener/gates.py`: Gate evaluation (`phase_results`, `funnel_ids`) and valuation engine
- `screener/apply_evaluation.py`: Stage-1/Stage-2 waterfall cleaner & validator
- `screener/bulk_scorer.py`: Batch validator & `--audit` CLI
- `screener/fetch/sqlite_db.py`: SQLite DB builder (`companies` 27 cols)
- `screener/dashboard.py`: `collect_screener_data()` & `build_dashboard_html()`
- `build.py`: Static HTML build script
- `fetch_market_data.py`: Market data fetcher & mirror sync
- `data/{us,eu,ca}/inputs.csv`: Qualitative inputs (`calamity` & `calamity_note` removed)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Implementation Plan | Concrete plan (`plan.md`) produced before edits | M0 | R1 |
| 2 | Core Calamity Retirement | Remove `calamity`, `calamity_note`, `RES_CALAMITY`, waiver logic across `screener/`, `build.py`, `fetch_market_data.py`, `sqlite_db.py` | M1 | R2 |
| 3 | Data Transition & Waterfall Scrubbing | Drop `calamity`/`calamity_note` from `inputs.csv`, scrub `APD`/`EL` (`483` Stage-2 / `506` G3 rejects), retain G4–G6 on 11 `3b=Y` rows (`10` in Quality Grade), clean 56 prose mentions, rebuild `fundamentals.sqlite` | M1 | R2 |
| 4 | `💎 Growth at ~0g` Tab & KPI | `passes_growth_0g` (`25` companies: `9`/`6`/`10`), slot #2 tab, KPI chip, `g_org_exp` desc sort, `#filter-gate`, `G5`/`G6`/`Gate Status`/`Failing Gate` cols | M1 | R3 |
| 5 | Spec, Version & Test Alignment | Bump to `v7.19`, update `CHANGELOG`, specs (`QUALITATIVE`, `COMPANY`, `QUANTITATIVE`, `README`), and full `tests/` suite | M1 | R2, R4 |
| 6 | Audit, Full Test Suite & Build | `bulk_scorer.py --audit` pass, `unittest` 100% pass, `build.py` regenerating HTML outputs | M1 | R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | Survey & Implementation Plan | 3-agent repo survey + concrete `plan.md` | none | DONE |
| M1 | v7.19 End-to-End Implementation & Verification | Execute `plan.md` via Iteration Loop (Worker → 2 Reviewers → 2 Challengers → Forensic Auditor → Gate) | M0 | DONE (Gate PASS: `483`/`506`/`989`, `225` Prime, `443` Quality Grade, `25` Growth at ~0g, `317/317` tests, `--audit` & `build.py` clean) |
