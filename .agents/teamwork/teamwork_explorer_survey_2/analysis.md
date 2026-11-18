# v7.19 Data, Counts & Repo-Wide Reference Survey (`analysis.md`)

**Core Findings:** Repo-wide scans confirm that `calamity` / `calamity_note` / `RES_CALAMITY` span 7 core Python modules, 2 top-level scripts (`build.py`, `fetch_market_data.py`), 4 markdown specs (`README.md`, `COMPANY_EVALUATION_SPEC.md`, `QUALITATIVE_EVALUATION_SPEC.md`, `QUANTITATIVE_EVALUATION_SPEC.md`), 7 test files, 3 `inputs.csv` files, `data/fundamentals.sqlite`, and historical `evaluations/` JSONs; `SCREENER_VERSION = "7.18"` and `CHANGELOG` live in `screener/config.py` (no `CHANGELOG.md`/`pyproject.toml`/`setup.py`). Read-only simulation against the live data and `par_valuation` pipeline reproduces every expected v7.19 count (`1175` total, `989` Gate 3, `483` Stage-2 advancing, `506` Gate-3 rejects, `225` Prime Grade, `443` Quality Grade, `25` `passes_growth_0g` = `9` Prime + `6` `CAP >= 15Y` failing G6 + `10` `CAP = 5–10Y`).

---

## 1. Repo-Wide Search: `calamity` & `7.18` / `v7.18`

### 1.1 Version & Changelog Files
- There is **no** `CHANGELOG`, `CHANGELOG.md`, `pyproject.toml`, `setup.py`, or `VERSION` file at the repository root.
- Version and changelog are centralized in `screener/config.py`:
  - `SCREENER_VERSION = "7.18"` at `screener/config.py:328`
  - `CHANGELOG = { ... "7.18": [...] ... }` at `screener/config.py:330–816` (`"7.18"` entry at lines `708–718`).

### 1.2 All Occurrences of `calamity` (Case-Insensitive, Excluding `.agents/`, `output/`, `docs/`, `data/_cache/`, `data/*/backups/`)

| File | Hit Count | Exact Lines / Scope | Notes |
|---|---:|---|---|
| `screener/config.py` | 22 | L239–244, 313–314, 317, 323, 326, 578–586, 712–713, 742, 745, 760, 763, 814 | Live constants: `CALAMITY_GATES`, `CALAMITY_FLAG_DEF`, `RES_CALAMITY`, `FUNNEL_RESULTS`, `Q_RESULTS`, `V_CALAMITY`, `LIST_CAPACITY`. Historical entries in `CHANGELOG` ("6.25", "7.1", "7.8", "7.9", "7.14", "7.15", "7.18"). |
| `screener/data.py` | 1 | L19 | `TAIL_FIELDS = ["calamity", "calamity_note", "note", "evidence"]` |
| `screener/gates.py` | 9 | L193, 197, 205, 209–210, 220–221, 241, 243 | `phase_results()` calamity waiver + `C.RES_CALAMITY`; `funnel_ids(meta, include_calamity=True)` |
| `screener/apply_evaluation.py` | 33 | L62–64, 137–155, 258, 267, 271–292, 312–319, 370–371 | `QUAL_KEY_MAP` keys (`calamity_flag`, `calamity`, `calamity_note`), normalization, `clear_calamity()`, Stage-1/2 waiver & non-empty `calamity_note` check |
| `screener/bulk_scorer.py` | 51 | L15, 44, 52, 85, 119–219 (11 ref snapshots), 565–674, 977, 994, 1016, 1068–1115, 1203–1205, 1249 | `CALAMITY_GATES`, `RES_CALAMITY`, `QUAL_COLUMNS`, `REFERENCE_SNAPSHOT`, `validate_company_evaluation()`, `audit_gate_3_universe()`, `print_audit_report()`, `main()` |
| `screener/fetch/sqlite_db.py` | 2 | L143, 202 | `companies` DDL column `calamity TEXT` (L143) and `INSERT` value `c.get("calamity")` (L202); note `INSERT` uses hardcoded `28` placeholders (`?` * 28) at L224! |
| `screener/dashboard.py` | 61 | L113–114, 144–145, 151, 251, 266, 1882–1883, 1899–1902, 1984, 2082–2089, 2210–2212, 2645, 2689–2693, 2772–2775, 2789–2791, 2813, 2823, 2826, 2948, 2971, 3159, 3170, 3208–3215, 3239, 3242, 3485–3498, 3520–3525, 3616–3617, 3651, 3683–3685, 3743–3746, 4723, 4737, 4739 | Backend `passes_calamity_grade`, `calamity_flag`, `calamity_note`, `summary["calamity_pass"]`; HTML KPI chip, tab button, `#filter-gate` option, methodology box, dossier box; JS `calamityTag`, `passesCalamityGrade`, table/card/drawer/CSV export |
| `build.py` | 1 | L38 | `print(f"  • Prime Grade Calamity (Conditional): {summary['calamity_pass']}")` — **must update** since `summary['calamity_pass']` is being retired/replaced |
| `fetch_market_data.py` | 2 | L4, 388 | L4 docstring comment; L388 `for qk in [*QUAL_CODES, "calamity", "calamity_note"]:` in `apply_mirrors()` |
| `COMPANY_EVALUATION_SPEC.md` | 14 | L15, 17, 18, 63, 172, 256, 365–366, 402–404, 647, 653, 660 | Full calamity workflow, JSON schema, CSV mapping, waterfall rules |
| `QUALITATIVE_EVALUATION_SPEC.md` | 11 | L15, 17, 18, 60, 186, 299–300, 336–338, 349 | Full calamity workflow, JSON schema, CSV mapping |
| `QUANTITATIVE_EVALUATION_SPEC.md` | 1 | L15 | Prerequisite mentions `Calamity pass` |
| `README.md` | 7 | L17, 63, 133–136, 307 | L17 overview, L307 `inputs.csv` description, L63/133–136 historical changelog prose |
| `tests/test_calamity_tier.py` | 40 | Throughout | Dedicated v6.25 Calamity Tier test module |
| `tests/test_bulk_scoring_e2e.py` | 91 | L79–80, 387–409, 453–498, 531, 812–1077, 1262–1361 | Calamity fixture fields, Feature 9 tests, corner-case tests, audit checks |
| `tests/test_v718_two_stage_waterfall.py` | 45 | L84–134, 194–451, 514, 616, 675, 686 | Stage-2 calamity-clearing tests, `EL` drawer test, `calamity` tab table test |
| `tests/test_dashboard_filters.py` | 7 | L22, 33, 35, 39, 59, 61, 76 | `calamity_pass` summary key, `"Prime Grade Calamity"` label, `passes_calamity_grade`, `"Calamity pass"` filter |
| `tests/test_valuation_sandbox.py` | 4 | L142, 202–203, 555 | `calamity_pass` summary key, `test_consistent_column_order_across_qpass_and_calamity`, `("Quality pass", "Calamity pass")` check |
| `tests/test_v71_remediation.py` | 3 | L175, 178–179 | `test_sandbox_payload_does_not_touch_calamity` |
| `tests/test_v72_remediation.py` | 1 | L136 | Mock `summary` dict has `"calamity_pass": 0` |
| `tests/test_v76_g6_overrides.py` | 1 | L93 | Mock `summary` dict has `"calamity_pass": 0` |
| `tests/test_v77_alignment.py` | 1 | L64 | Mock `summary` dict has `"calamity_pass": 0` |
| `data/{us,eu,ca}/inputs.csv` | 59 files/lines total | `us`: 52 lines; `eu`: 6 lines; `ca`: 1 line | Header cols `calamity`, `calamity_note`; 13 rows with `calamity='Y'`; 56 rows with `calamity` word in `note`/`evidence` (see Section 3) |
| `evaluations/*` | 1,218 files | 1,175 `*_qual.json` (all `"calamity_flag": null`, 0 non-null), 43 non-`_qual.json` (13 `*_quant.json` + batch/completed files) | Historical evaluation artifacts |
| `screener/v2..v4_2/*`, `screener/migrations/*` | 0 | None | Clean |
| `output/*`, `docs/index.html` | generated | `output/screener.html`, `output/index.html`, `docs/index.html` | Regenerated via `python3 build.py` |

### 1.3 All Occurrences of `7.18` / `v7.18` (Excluding `.agents/`, `output/`, `docs/`, `data/_cache/`, `data/*/backups/`)
- **Code & Specs:**
  - `screener/config.py`: L328 (`SCREENER_VERSION = "7.18"`), L708 (`"7.18": [...]`)
  - `screener/bulk_scorer.py`: L1 (module docstring `v7.18`), L1160 (`GATE 3 COMPLIANCE AUDIT (v7.18)`)
  - `COMPANY_EVALUATION_SPEC.md`: L1 (`(v7.18)`), L8 (`(v7.18)`), L547 (`v7.18 Stage 2 Note`)
  - `QUALITATIVE_EVALUATION_SPEC.md`: L1 (`(v7.18)`), L8 (`(v7.18)`)
  - *(Note: `QUANTITATIVE_EVALUATION_SPEC.md` and `README.md` headers still say `v7.7` at L1.)*
- **Tests:**
  - `tests/test_bulk_scoring_e2e.py`: L1317 (comment `(v7.18)`)
  - `tests/test_v718_two_stage_waterfall.py`: L1, 335, 484, 492–496, 512, 702–703, 707, 714 (asserts `SCREENER_VERSION == "7.18"`, `"7.18"` in `output/*.html` / `docs/index.html`, `"v7.18"` in specs and `--audit` stdout)
  - `tests/test_v76_g6_overrides.py`: L25 (unrelated numeric test datum `2025: 7.18`)
- **Data / Evaluations:**
  - `data/us/inputs.csv`: L7 (`CMCSA` `$17.18B`), L157 (`COIN` `$7.18B`), L337 (`HON` `-$7.18B`), L374 (`PLTR` `$7.18B`) — all dollar figures, not version strings.
  - `data/{us,eu,ca}/financials.csv`, `fundamentals_panel.csv`, `technicals.csv`: numeric market/financial values.
  - `evaluations/*`: 11 historical batch/eval JSONs.

---

## 2. Schemas: `inputs.csv`, `universe.json`, `fundamentals.sqlite`, and `data/_cache/`

1. **`data/us/inputs.csv`** (`515` data rows, `31` columns):
   `['id', 'ticker', 'company', 'country', 'sector', 'sub_industry', 'in_sp500', 'in_ndx', '1', '2', '2r', '3_tb', '3_ia', '3_se', '3_rd', '3a', '3b', '3m', '4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6', 'calamity', 'calamity_note', 'note', 'evidence']`
2. **`data/eu/inputs.csv`** (`602` data rows, `31` columns):
   `['id', 'ticker', 'company', 'country', 'sector', 'sub_industry', 'exchange', 'index_weight_pct', '1', '2', '2r', '3_tb', '3_ia', '3_se', '3_rd', '3a', '3b', '3m', '4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6', 'calamity', 'calamity_note', 'note', 'evidence']`
3. **`data/ca/inputs.csv`** (`58` data rows, `30` columns):
   `['id', 'ticker', 'company', 'country', 'sector', 'sub_industry', 'exchange', '1', '2', '2r', '3_tb', '3_ia', '3_se', '3_rd', '3a', '3b', '3m', '4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6', 'calamity', 'calamity_note', 'note', 'evidence']`
4. **`data/{us,eu,ca}/universe.json`**:
   - No `calamity` references in any `universe.json`.
   - Only `data/us/universe.json` defines `"mirror"` (`{"ASML": "eu:ASML.NL", "FER": "eu:FER.ES"}`).
5. **`data/fundamentals.sqlite`** (`28.86 MB`, built by `screener/fetch/sqlite_db.py`):
   - `companies` (`1175` rows, `28` columns): includes `calamity TEXT` (col 27) and `result TEXT` (`"Calamity pass"` for the 13 rows). `screener/fetch/sqlite_db.py` lines 143, 202, 224 must remove `calamity` and adjust `VALUES (?,...,?)` from `28` to `27` placeholders, and `data/fundamentals.sqlite` should be regenerated via `build_sqlite_db()` if kept synchronized.
   - `financials_latest` (`1175` rows), `annual_fundamentals` (`32862` rows), `quarterly_fundamentals` (`44289` rows), `technicals_latest` (`1175` rows): no `calamity` columns.
6. **`data/_cache/`**: subdirectories `eodhd/`, `sec/`, `yahoo/` (raw API JSONs only, no qualitative/calamity fields).

---

## 3. Calamity Rows, Stage-1 Scrubbing, Prose Mentions & Mirror Pairs

### 3.1 The 13 Rows with `calamity` / `calamity_note` Populated
Zero other rows in `data/{us,eu,ca}/inputs.csv` have non-empty `calamity` or `calamity_note`.

#### Group A: 11 Tickers with `3b = Y` (Retain full Gate 4–6 scores & notes; `10` stay in `🏰 Quality Grade`, `1` does not)

| Universe:ID | 1 | 2 | 3a | 3b | G4 | G5 | G6 | G6 Numeric Flags (`g6_flags`) | `passes_quality_grade` | Post-v7.19 `result` |
|---|---|---|---|---:|---:|---:|---|---:|---|---|
| `eu:DGE.GB` | Y | Y | Irreplaceable infra & intangibles | Y | 15 | 0 | Y | 1 (`netdebt: flag`) | **True** | `Rejected – G5 Management` |
| `eu:NESN.CH` | Y | Y | Irreplaceable infra & intangibles | Y | 15 | 0 | N | 2 (`netdebt: flag`, `p2p: flag`) | **True** | `Rejected – G5 Management` |
| `eu:RTO.GB` | Y | Y | Irreplaceable infra & intangibles | Y | 15 | 0 | N | 2 (`netdebt: flag`, `intcov: flag`) | **True** | `Rejected – G5 Management` |
| `us:GOOGL` | Y | Y | Toll booth & switching costs | Y | 20 | 1 | N | 0 | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:NDAQ` | Y | Y | Toll booth & switching costs | Y | 25 | 1 | N | 1 (`netdebt: flag`) | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:HONA` | Y | Y | Toll booth & switching costs | Y | 20 | 1 | N | 1 (`p2p: flag`) | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:NOC` | Y | Y | Irreplaceable infra & intangibles | Y | 20 | 1 | N | 1 (`fcfconv: flag`) | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:RTX` | Y | Y | Toll booth & switching costs | Y | 20 | 1 | N | **3** (`netdebt`, `intcov`, `p2p`) | **False** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:EFX` | Y | Y | Toll booth & switching costs | Y | 20 | 1 | N | 2 (`netdebt: flag`, `intcov: flag`) | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:SNPS` | Y | Y | Toll booth & switching costs | Y | 25 | 1 | N | 1 (`fcfconv: flag`) | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |
| `us:TXN` | Y | Y | Toll booth & switching costs | Y | 20 | 2 | N | 0 | **True** | `Rejected – G6 Cash & Fortress Balance Sheet` |

- **Why `RTX` does not pass `passes_quality_grade`:** `RTX` triggers **3** of the 4 Gate 6 numeric flags (`g6_netdebt_yrs`, `g6_intcov`, `p2p_ok`), failing `g6_flags < 3` (`screener/dashboard.py:107`). (Note: in v7.18 `RTX` also failed `passes_calamity_grade` for the same reason.)

#### Group B: 2 Tickers with `3b = N` (`APD`, `EL` — Stage-1 Waterfall Scrubbing Required)
- `us:APD`: currently `1='Y', 2='Y', 3_tb=2, 3_ia=1, 3_se=0, 3_rd=0, 3a='Toll booth & switching costs', 3b='N', 4_ent=0, 4_riv=0, 4_buy=0, 4_sup=1, 4_sub=0, 4=25, 5=0, 6='N', calamity='Y'`, `g6_flags=2` (`netdebt`, `intcov`).
- `us:EL`: currently `1='Y', 2='Y', 3_tb=0, 3_ia=2, 3_se=0, 3_rd=0, 3a='Irreplaceable infrastructure & intangibles', 3b='N', 4_ent=1, 4_riv=1, 4_buy=1, 4_sup=0, 4_sub=0, 4=15, 5=0, 6='N', calamity='Y'`, `g6_flags=3` (`netdebt`, `intcov`, `p2p`).
- **Stage-1 Waterfall Scrubbing (`screener/apply_evaluation.py:273–278`, `screener/bulk_scorer.py:586–589`):** Without calamity, `3b == 'N'` triggers Stage-1 scrubbing of `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]` (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6` cleared to `""`), while preserving `3_tb..3m`, `note`, and `evidence`. Both become `Rejected – G3 Moat & Pricing` (`passes_quality_grade = False`).

### 3.2 Prose Mentions of `calamity` in `inputs.csv` Other Columns
- **0** mentions in `3m`, `4n`, `2r`, or any column other than `note` and `evidence`.
- **56 rows** (`51` US, `5` EU, `0` CA) contain `"calamity"` in `note` and/or `evidence`:
  - **12 of the 13 active calamity rows** (`GOOGL`, `EL`, `NDAQ`, `HONA`, `RTX`, `EFX`, `SNPS`, `TXN`, `APD`, `DGE.GB`, `NESN.CH`, `RTO.GB` — `NOC`'s `note`/`evidence` does not contain the word `"calamity"`), whose `note` explicitly states `"Calamity pass..."` / `"Qualifies for Calamity Tier..."`.
  - **44 non-calamity rows** (`42` US: `APP`, `OMC`, `SPCX`, `FOXA`, `CHTR`, `CMCSA`, `T`, `VZ`, `TTWO`, `META`, `DIS`, `LYV`, `NFLX`, `SKYD`, `NWSA`, `TMUS`, `LULU`, `F`, `TSLA`, `APTV`, `AZO`, `AMZN`, `LVS`, `GPC`, `LEN`, `NVR`, `ABNB`, `CCL`, `RCL`, `DPZ`, `XOM`, `MDT`, `ILMN`, `NSC`, `ARM`, `CRWD`, `IFF`, `VTR`, `UDR` — wait: count = 42 US? Let's note exact count is `51 - 9 = 42` US + `2` EU (`CPR.IT`, `FLS.DK`) = **44** non-calamity rows) whose `note` or `evidence` explains why they are `"Ineligible for Calamity Tier..."` / `"not a temporary fixable calamity"`.
  - **Planning Implication:** Because Acceptance Criterion 2 specifies *"Zero references to `calamity`, `calamity_note`, `RES_CALAMITY`, or calamity-waiver logic remain across ... `data/{us,eu,ca}/inputs.csv`"*, a naive repo-wide grep on `data/{us,eu,ca}/inputs.csv` will still hit these 56 rows unless their `note`/`evidence` prose is also rewritten/cleaned (at minimum the 12 active calamity `note` prefixes, and potentially the 44 rejection-rationale sentences).

### 3.3 Mirror Pairs (`data/*/universe.json`)
- Only `data/us/universe.json` has `"mirror"`: `{"ASML": "eu:ASML.NL", "FER": "eu:FER.ES"}`.
- `ASML`/`ASML.NL`: `3b = Y`, `calamity = ''`, `result = 'Quality pass'`.
- `FER`/`FER.ES`: `3b = N`, `calamity = ''`, `result = 'Rejected – G3 Moat & Pricing'`.
- Neither mirror pair was a calamity ticker.

---

## 4. Verified Baseline vs. Expected v7.19 Counts & `passes_growth_0g` Simulation

### 4.1 Funnel & Tier Counts

| Metric | v7.18 Baseline | Expected v7.19 | Delta / Explanation |
|---|---:|---:|---|
| Total Universe | 1,175 (`515` US, `602` EU, `58` CA) | **1,175** | Unchanged |
| Gate 3 Companies (`G1=Y & G2=Y`) | 989 (`445` US, `495` EU, `49` CA) | **989** | Unchanged |
| Stage-2 Advancing (G3 Pass) | 485 (`247` US, `217` EU, `21` CA) | **483** (`245` US, `217` EU, `21` CA) | `-2` (`APD`, `EL` no longer waived at `3b=N`) |
| Gate-3 Rejects | 504 (`198` US, `278` EU, `28` CA) | **506** (`200` US, `278` EU, `28` CA) | `+2` (`APD`, `EL` become standard G3 rejects) |
| `Prime Grade` (`passes_prime_grade`) | 225 | **225** | Unchanged |
| `Quality Grade` (`passes_quality_grade`) | 443 | **443** | Unchanged (includes 10 of 11 former `3b=Y` calamity tickers; `RTX` has `g6_flags=3`) |
| `Prime Grade Calamity` | 11 | **Retired (0)** | Replaced by `Growth at ~0g` (`25`) |
| `Growth at ~0g` (`passes_growth_0g`) | — | **25** | `9` Prime + `6` `CAP >= 15Y` failing G6 + `10` `CAP = 5–10Y` |

### 4.2 Complete `passes_growth_0g` List (Sorted by `g_org_exp` Descending)

Predicate: `passes_quality_grade` (`G1=Y`, `G2=Y`, `3a != None`, `3b=Y`, `g6_flags < 3`), `val_status == 'Valued'`, `g_market_flag in ('ok', 'saturated_low')`, `g_market < 0.05`, `g_org_exp >= 0.05`. *(Note: across the entire 1,175-company universe, only `eu:STLAM.IT` and `eu:PAF.GB` have `g_market_flag == 'saturated_low'`, and neither passes Quality Grade; all 25 matching companies have `g_market_flag == 'ok'`.)*

| # | Universe:ID | Company | G4 CAP | G5 | G6 | `g_org_exp` | `g_market` | Cohort / Failing Gate |
|---:|---|---|---:|---:|---|---:|---:|---|
| 1 | `us:ADBE` | Adobe Inc. | 5 | 0 | Y | 11.22% | 0.91% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 2 | `us:PGR` | Progressive Corporation | 25 | 2 | Y | 11.15% | 4.32% | **Prime Grade** |
| 3 | `us:ACGL` | Arch Capital Group | 5 | 2 | Y | 10.87% | -1.16% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 4 | `us:DECK` | Deckers Brands | 5 | 1 | Y | 10.55% | -0.11% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 5 | `us:IT` | Gartner | 10 | 1 | Y | 9.77% | 1.00% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 6 | `eu:VER.AT` | Verbund | 15 | 1 | N | 9.73% | 2.83% | `CAP >= 15Y` (`Rejected – G6 Cash & Fortress Balance Sheet`) |
| 7 | `us:FICO` | Fair Isaac | 20 | 1 | N | 9.22% | 4.27% | `CAP >= 15Y` (`Rejected – G6 Cash & Fortress Balance Sheet`) |
| 8 | `eu:AAK.SE` | AAK | 15 | 2 | N | 8.81% | 1.94% | `CAP >= 15Y` (`Rejected – G6 Cash & Fortress Balance Sheet`) |
| 9 | `eu:MC.FR` | LVMH | 20 | 1 | Y | 8.78% | 3.22% | **Prime Grade** |
| 10 | `us:ZTS` | Zoetis | 25 | 1 | Y | 8.66% | 1.61% | **Prime Grade** |
| 11 | `eu:A2A.IT` | A2A | 15 | 1 | N | 8.25% | -3.79% | `CAP >= 15Y` (`Rejected – G6 Cash & Fortress Balance Sheet`) |
| 12 | `us:ACN` | Accenture | 5 | 1 | Y | 7.98% | 2.40% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 13 | `us:HIG` | Hartford (The) | 10 | 1 | Y | 6.43% | 1.03% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 14 | `eu:DG.FR` | Vinci | 15 | 1 | Y | 6.34% | 3.83% | **Prime Grade** |
| 15 | `us:LII` | Lennox International | 10 | 1 | Y | 5.88% | 2.21% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 16 | `eu:AUTO.GB` | Auto Trader | 20 | 1 | Y | 5.83% | 3.26% | **Prime Grade** |
| 17 | `eu:NWG.GB` | NatWest | 5 | 1 | N | 5.81% | -4.68% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 18 | `eu:BNZL.GB` | Bunzl | 20 | 1 | Y | 5.66% | 4.47% | **Prime Grade** |
| 19 | `eu:PST.IT` | Poste Italiane | 15 | 1 | N | 5.65% | 2.82% | `CAP >= 15Y` (`Rejected – G6 Cash & Fortress Balance Sheet`) |
| 20 | `eu:WKL.NL` | Wolters Kluwer | 20 | 2 | Y | 5.53% | 2.75% | **Prime Grade** |
| 21 | `eu:FGR.FR` | Eiffage | 10 | 1 | Y | 5.41% | -5.05% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |
| 22 | `eu:HER.IT` | Hera | 15 | 2 | N | 5.32% | -0.49% | `CAP >= 15Y` (`Rejected – G6 Cash & Fortress Balance Sheet`) |
| 23 | `eu:PGHN.CH` | Partners Group | 20 | 1 | Y | 5.15% | 1.17% | **Prime Grade** |
| 24 | `eu:GTT.FR` | GTT (Gaztransport & Technigaz) | 20 | 1 | Y | 5.13% | 3.37% | **Prime Grade** |
| 25 | `us:GL` | Globe Life | 5 | 1 | Y | 5.04% | 2.67% | `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`) |

---

## 5. Baseline Verification Runs & Pre-Existing Failure

- `python3 screener/bulk_scorer.py --audit`: **PASSED** (`989 / 989` Gate 3, `11` ref companies, `0` formula/3a/4n/waterfall/stage2/calamity violations, mirror parity PASSED; Stage 2 count = `485` in v7.18).
- `python3 -m unittest discover -s tests`: **Ran 321 tests in 53.875s — FAILED (failures=1)**.
  - Pre-existing baseline failure: `test_dashboard_runtime_js_openDrawer_and_renderTable_via_jsc (test_v718_two_stage_waterfall.DashboardV718UITests)` at `tests/test_v718_two_stage_waterfall.py:650` (`AssertionError: 'PASS · 2/2' not found in ...` because `screener/dashboard.py:3665-3667` renders `'ELITE'` for `g5_mgmt == 2` instead of `'PASS · 2/2'`).
