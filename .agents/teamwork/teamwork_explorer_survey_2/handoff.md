# Handoff Report — `teamwork_explorer_survey_2` (Hard Handoff)

**Summary:** Completed the read-only data, counts, and repo-wide reference survey for v7.19. Verified all `calamity` and `7.18` references, schemas (`inputs.csv`, `universe.json`, `fundamentals.sqlite`), the 13 active calamity rows, 56 prose mentions in `inputs.csv`, mirror parity, and simulated the exact v7.19 counts (`989` Gate 3 = `483` Stage-2 advancing + `506` Gate-3 rejects; `225` Prime Grade; `443` Quality Grade; `25` `Growth at ~0g` = `9` Prime + `6` `CAP >= 15Y` failing G6 + `10` `CAP = 5–10Y`).

Full supporting tables and line-by-line inventories are in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/teamwork_explorer_survey_2/analysis.md`.

---

## 1. Observation

1. **Repo-wide `calamity` occurrences** (Python scan excluding `.agents/`, `output/`, `docs/`, `data/_cache/`, `data/*/backups/`):
   - Core modules: `screener/config.py` (22 lines), `screener/data.py` (L19), `screener/gates.py` (9 lines), `screener/apply_evaluation.py` (33 lines), `screener/bulk_scorer.py` (51 lines), `screener/fetch/sqlite_db.py` (L143, L202), `screener/dashboard.py` (61 lines).
   - Top-level scripts: `build.py:38` (`summary['calamity_pass']`), `fetch_market_data.py:4, 388` (`apply_mirrors` copies `"calamity", "calamity_note"`).
   - Specs: `COMPANY_EVALUATION_SPEC.md` (14 lines), `QUALITATIVE_EVALUATION_SPEC.md` (11 lines), `QUANTITATIVE_EVALUATION_SPEC.md:15`, `README.md` (7 lines: L17, L63, L133–136, L307).
   - Tests: `tests/test_calamity_tier.py` (40 lines), `tests/test_bulk_scoring_e2e.py` (91 lines), `tests/test_v718_two_stage_waterfall.py` (45 lines), `tests/test_dashboard_filters.py` (7 lines), `tests/test_valuation_sandbox.py` (4 lines), `tests/test_v71_remediation.py` (3 lines), `tests/test_v72_remediation.py:136`, `tests/test_v76_g6_overrides.py:93`, `tests/test_v77_alignment.py:64`.
   - Legacy `screener/v2..v4_2/` and `screener/migrations/`: `0` matches.
   - `evaluations/`: 1,218 files match (1,175 `*_qual.json` have `"calamity_flag": null`, 0 non-null; 43 non-`_qual.json` incl. 13 `*_quant.json` and `batches/`/`completed/`).
2. **Repo-wide `7.18` / `v7.18` and version files**:
   - No `CHANGELOG`, `CHANGELOG.md`, `pyproject.toml`, `setup.py`, or `VERSION` file exists at repo root. `SCREENER_VERSION = "7.18"` is at `screener/config.py:328` and `CHANGELOG` dict at `screener/config.py:330–816` (`"7.18"` at L708–718).
   - `7.18` appears in `screener/bulk_scorer.py:1, 1160`, `COMPANY_EVALUATION_SPEC.md:1, 8, 547`, `QUALITATIVE_EVALUATION_SPEC.md:1, 8`, `tests/test_bulk_scoring_e2e.py:1317`, and `tests/test_v718_two_stage_waterfall.py` (13 lines). (`README.md:1` and `QUANTITATIVE_EVALUATION_SPEC.md:1, 8` say `v7.7`; `tests/test_v76_g6_overrides.py:25` and `data/us/inputs.csv` L7, 157, 337, 374 match numeric `7.18` dollar values.)
3. **Data & SQLite schemas**:
   - `data/us/inputs.csv`: 515 rows, 31 cols (incl. `calamity`, `calamity_note`).
   - `data/eu/inputs.csv`: 602 rows, 31 cols (incl. `calamity`, `calamity_note`).
   - `data/ca/inputs.csv`: 58 rows, 30 cols (incl. `calamity`, `calamity_note`).
   - `data/fundamentals.sqlite`: `companies` table (1,175 rows) has `calamity TEXT` (col 27 of 28) and `result = 'Calamity pass'` on 13 rows (`screener/fetch/sqlite_db.py:143, 202, 224`).
   - `data/us/universe.json:87–90` defines `"mirror": {"ASML": "eu:ASML.NL", "FER": "eu:FER.ES"}`; `eu`/`ca` `universe.json` have no mirrors. Neither mirror pair is a calamity ticker.
4. **Calamity rows & prose in `inputs.csv`**:
   - Exactly **13** rows have `calamity == 'Y'` and non-empty `calamity_note` (0 other rows have either column populated):
     - **11** with `3b = Y`: `eu:DGE.GB`, `eu:NESN.CH`, `eu:RTO.GB`, `us:GOOGL`, `us:NDAQ`, `us:HONA`, `us:NOC`, `us:RTX`, `us:EFX`, `us:SNPS`, `us:TXN`. Retaining G4–6 scores yields `10` with `passes_quality_grade = True`; **`us:RTX` fails `passes_quality_grade` because `g6_flags = 3`** (`netdebt: flag`, `intcov: flag`, `p2p: flag`, failing `< 3` at `screener/dashboard.py:107`).
     - **2** with `3b = N`: `us:APD` (`4=25, 5=0, 6=N`, `g6_flags=2`) and `us:EL` (`4=15, 5=0, 6=N`, `g6_flags=3`). Per `screener/apply_evaluation.py:273–278` and `screener/bulk_scorer.py:586–589`, unwaived `3b = N` triggers Stage-1 scrubbing of `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]`.
   - **56 rows** (`51` US, `5` EU, `0` CA) contain the word `"calamity"` in `note` and/or `evidence` (12 of the 13 `calamity='Y'` rows — all except `NOC` — plus 44 non-calamity rows explaining Calamity Tier ineligibility). Zero mentions in `3m`, `4n`, `2r`.
5. **Baseline & simulated v7.19 counts**:
   - Baseline `python3 screener/bulk_scorer.py --audit`: PASSED (485 Stage-2 advancing, 989 Gate 3, 13 calamity rules OK).
   - Baseline `python3 -m unittest discover -s tests`: Ran 321 tests in 53.875s — **1 pre-existing failure**: `test_dashboard_runtime_js_openDrawer_and_renderTable_via_jsc` (`tests/test_v718_two_stage_waterfall.py:650`) expected `'PASS · 2/2'` while `screener/dashboard.py:3665–3667` outputs `'ELITE'` for `g5_mgmt == 2`.
   - Simulated v7.19 counts: `1,175` total; `989` Gate 3 (`445` US, `495` EU, `49` CA); `483` Stage-2 advancing (`245` US, `217` EU, `21` CA); `506` Gate-3 rejects (`200` US, `278` EU, `28` CA); `225` Prime Grade; `443` Quality Grade; `25` `passes_growth_0g` (`9` Prime Grade, `6` `CAP >= 15Y` failing G6, `10` `CAP = 5–10Y`).

---

## 2. Logic Chain

1. Removing `calamity` and `calamity_note` from `screener/data.py:19`, `screener/config.py`, `screener/gates.py`, `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/fetch/sqlite_db.py`, `screener/dashboard.py`, `fetch_market_data.py`, `build.py`, and `data/{us,eu,ca}/inputs.csv` eliminates `RES_CALAMITY` (`Calamity pass`) end-to-end.
2. When `APD` and `EL` (`3b = N`) undergo Stage-1 waterfall scrubbing (`4_ent..4_sub, 4, 4n, 5, 6` -> blank), Stage-2 advancing drops by 2 (`485 -> 483`) and Gate-3 rejects increase by 2 (`504 -> 506`), preserving `483 + 506 = 989`.
3. Retaining G4–6 on the 11 `3b = Y` tickers moves `DGE.GB`, `NESN.CH`, `RTO.GB` to `Rejected – G5 Management` and `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN` to `Rejected – G6 Cash & Fortress Balance Sheet`, leaving `Prime Grade` at `225` and `Quality Grade` at `443` (where 10 enter `Quality Grade` and `RTX` is excluded by `g6_flags == 3`).
4. Evaluating `passes_growth_0g` (`passes_quality_grade` AND `val_status == 'Valued'` AND `g_market_flag in ('ok', 'saturated_low')` AND `g_market < 0.05` AND `g_org_exp >= 0.05`) over the simulated v7.19 dataset yields exact 25 rows (`9` Prime Grade, `6` `CAP >= 15Y` failing G6, `10` `CAP = 5–10Y`), all with `g_market_flag == 'ok'`.

---

## 3. Caveats

- **56 `note`/`evidence` prose mentions in `data/{us,eu}/inputs.csv`**: Beyond the `calamity` and `calamity_note` columns, 12 active calamity `note` fields state `"Calamity pass..."` and 44 rejected/other `note`/`evidence` fields state `"Ineligible for Calamity Tier..."` / `"not a temporary fixable calamity"`. The plan must explicitly decide whether to rewrite all 56 prose mentions (to satisfy a strict zero-grep check on `data/{us,eu,ca}/inputs.csv`) or only the 12 active `Calamity pass` headers.
- **`build.py:38`, `fetch_market_data.py:4, 388`, `QUANTITATIVE_EVALUATION_SPEC.md:15`, and `tests/test_v71/v72/v76/v77` mocks**: These files were not listed explicitly in R2's file list (`fetch_market_data.py`, `build.py`, `QUANTITATIVE_EVALUATION_SPEC.md`, older test files), yet they reference `calamity`, `calamity_note`, or `summary['calamity_pass']` and **will break or fail a zero-reference check** unless updated.
- **`data/fundamentals.sqlite`**: Currently contains `calamity TEXT` and 13 `'Calamity pass'` rows; regenerating it via `build_sqlite_db()` after updating `sqlite_db.py` (adjusting placeholder count `28 -> 27`) keeps the DB aligned.
- **Pre-existing test failure**: `tests/test_v718_two_stage_waterfall.py:650` (`PASS · 2/2` vs `ELITE`) already fails in v7.18 baseline (`320/321` pass).
- **`evaluations/` archive**: 1,218 historical evaluation JSONs exist on disk; not runtime-loaded by `screener/`.

---

## 4. Conclusion

The codebase and dataset are clean and deterministic for the v7.19 transition:
1. All target v7.19 counts (`1175` universe, `989` Gate 3, `483` Stage-2 advancing, `506` Gate-3 rejects, `225` Prime Grade, `443` Quality Grade, `25` `Growth at ~0g`) are independently verified against the live pipeline.
2. Implementation plan must include `build.py:38`, `fetch_market_data.py:388`, `QUANTITATIVE_EVALUATION_SPEC.md:15`, `screener/fetch/sqlite_db.py` (including placeholder count `28 -> 27` and DB rebuild), all 7 test files with `calamity`/`calamity_pass` mocks, `tests/test_v718_two_stage_waterfall.py` fixes, and explicit handling of the 56 `note`/`evidence` calamity prose mentions in `data/{us,eu}/inputs.csv`.

---

## 5. Verification Method

All observations and counts are independently reproducible read-only from `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`:
1. Baseline audit & tests:
   - `python3 screener/bulk_scorer.py --audit`
   - `python3 -m unittest discover -s tests` (expect 320 pass, 1 pre-existing fail at `test_v718_two_stage_waterfall.py:650`)
2. Inspect `data/{us,eu,ca}/inputs.csv` headers/rows, `data/*/universe.json`, and `data/fundamentals.sqlite` `companies` table.
3. Run a read-only Python script using `screener.dashboard.collect_screener_data()` and `screener.gates.phase_results` / `par_valuation` (clearing `calamity`/`calamity_note` and scrubbing `4_*..6` on `APD`, `EL`) to reproduce `483`/`506`/`225`/`443`/`25` (`9`/`6`/`10`).
4. **Invalidation conditions**: Any edits to `data/{us,eu,ca}/inputs.csv`, `financials.csv`, or `screener/gates.py` before planning completes would invalidate the exact snapshot counts.
