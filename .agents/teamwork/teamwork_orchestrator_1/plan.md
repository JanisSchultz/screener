# v7.19 Implementation Plan — Retire `Calamity` Tier & Add `💎 Growth at ~0g` Tab

**Created:** 2026-11-18  
**Author:** Project Orchestrator (`teamwork_orchestrator_1`)  
**Sources:** Survey reports from `teamwork_explorer_survey_1`, `teamwork_explorer_survey_2`, `teamwork_spec_miner_survey_3`, and `ORIGINAL_REQUEST.md`.

---

## 1. Summary of Verified Baseline & Target v7.19 State

| Metric | v7.18 Baseline | Target v7.19 | Delta / Notes |
|---|---:|---:|---|
| Total Universe | 1,175 | **1,175** | `515` US, `602` EU, `58` CA |
| Gate 3 Cohort (`G1=Y & G2=Y`) | 989 | **989** | `445` US, `495` EU, `49` CA |
| Stage-2 Advancing (`3a != None & 3b = Y`) | 485 | **483** | `-2` (`APD`, `EL` have `3b=N`, scrubbed to G3 rejects) |
| Gate-3 Rejects | 504 | **506** | `+2` (`APD`, `EL`) — `483 + 506 = 989` |
| `Prime Grade` (`passes_prime_grade`) | 225 | **225** | `110` US, `104` EU, `11` CA |
| `Quality Grade` (`passes_quality_grade`) | 443 | **443** | `10` of 11 former `3b=Y` calamity tickers remain (`RTX` excluded by `g6_flags = 3`) |
| `Prime Grade Calamity` | 11 (13 raw) | **Retired (0)** | Completely removed across code, CSVs, SQLite, UI, specs, tests |
| `💎 Growth at ~0g` (`passes_growth_0g`) | — | **25** | `9` Prime Grade + `6` `CAP >= 15Y` failing `G6 = N` + `10` `CAP = 5–10Y` |

---

## 2. Step-by-Step Execution Plan

### Step 1: Core Engine & Schema Retirement of `Calamity`
1. **`screener/config.py`**:
   - Remove `CALAMITY_GATES`, `CALAMITY_FLAG_DEF`, `RES_CALAMITY`, `V_CALAMITY`, and `V_CALAMITY` entry from `LIST_CAPACITY`.
   - Update `FUNNEL_RESULTS = (RES_QPASS,)` and `Q_RESULTS` (remove `RES_CALAMITY`).
   - Bump `SCREENER_VERSION = "7.19"` (`L328`) and prepend `"7.19": [...]` to `CHANGELOG` documenting the retirement of the Calamity tier, Stage-1 scrubbing of `APD`/`EL` (`483` Stage-2 advancing / `506` G3 rejects / `989` G3), retention of `225` Prime Grade and `443` Quality Grade, and addition of the `💎 Growth at ~0g` (`25` companies) tab. *(Preserve existing `"6.25"`–`"7.18"` historical changelog entries as factual release history.)*
2. **`screener/data.py`**:
   - Update `TAIL_FIELDS = ["note", "evidence"]` (`L19`).
3. **`screener/gates.py`**:
   - Update `phase_results()` (`L192–222`) to remove `calamity = company.get("calamity") == "Y"` and all waiver branches; any `"fail"` gate (`1`, `2`, `3a`, `3b`, `4`, `5`, `6`) immediately routes to `C.RES_REJ[ph]`, and passing all gates returns `C.RES_QPASS`. Remove `"waived"` from the returned dict (or verify all internal/test callers are updated).
   - Simplify `funnel_ids(meta: dict) -> list[str]:` (`L241–244`) by removing `include_calamity` and returning only `C.RES_QPASS` IDs.
4. **`screener/apply_evaluation.py`**:
   - Remove `"calamity_flag"`, `"calamity"`, `"calamity_note"` from `QUAL_KEY_MAP` (`L62–64`).
   - Remove calamity normalization, `clear_calamity()`, `cal_active` checks on Gate `3b`, Gate 4 `< 15` calamity clearing, and calamity warnings/errors (`L137–156, 258, 267, 271–298, 312–319, 370–372`).
   - Stage 1 (`g1 == "N"`, `g2 == "N"`, or `g3a == "None"` or `g3b == "N"`) unconditionally scrubs `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]` to `""`. Stage 2 (`g4 < 15` or `g5 == 0`) continues preserving diagnostic `5` and `6`.
5. **`screener/bulk_scorer.py`**:
   - Remove `CALAMITY_GATES` and `RES_CALAMITY` imports (`L44, 52`), remove `"calamity"`, `"calamity_note"` from `QUAL_COLUMNS` (`L85`) and all 11 `REFERENCE_SNAPSHOT` entries (`L119–219`).
   - Remove `calamity_active` / `calamity_violations` and calamity exceptions from `validate_company_evaluation()` (`L565–675`), `audit_gate_3_universe()` (`L977–1116`), `print_audit_report()` (`L1203–1206`), and `main()` (`L1249`).
   - Update module docstring (`L1, 15, 783`) and audit header (`L1160`) to `v7.19`.
6. **`screener/fetch/sqlite_db.py`**:
   - Remove `calamity TEXT,` from `CREATE TABLE companies` (`L143`), remove `c.get("calamity")` from `comp_rows` (`L202`), and update `INSERT OR REPLACE INTO companies VALUES (...)` placeholders from `28` to `27` (`L224`).
7. **`fetch_market_data.py` & `build.py`**:
   - `fetch_market_data.py`: update comment (`L4`) and change `apply_mirrors()` (`L388`) to `for qk in QUAL_CODES:` (removing `"calamity", "calamity_note"`).
   - `build.py`: update `L38` to print `Growth at ~0g`: `print(f"  • Growth at ~0g: {summary['growth_0g']}")`.

### Step 2: Data Transition (`data/{us,eu,ca}/inputs.csv` & `data/fundamentals.sqlite`)
1. **Drop `calamity` and `calamity_note` columns** from `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv` (column counts: US `31 -> 29`, EU `31 -> 29`, CA `30 -> 28`).
2. **Stage-1 Waterfall Scrubbing on `us:APD` and `us:EL` (`3b = N`)**:
   - Clear `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6` to `""`.
   - Retain `3_tb..3m` and `evidence`, and strip the `"Calamity pass..."` header from `note` so both reflect standard Gate-3 `3b=N` rejection.
3. **Retain Gate 4–6 Scores & Notes on the `11` `3b = Y` Former Calamity Companies**:
   - `DGE.GB`, `NESN.CH`, `RTO.GB` (`5 = 0` -> `Rejected – G5 Management`): keep Gate 4–6 scores and `4n`, strip `"Calamity pass..."` wording from `note`, and ensure `note` carries `[Diagnostic G5=0 | G6=Y: ...]` (`DGE.GB`) / `[Diagnostic G5=0 | G6=N: ...]` (`NESN.CH`, `RTO.GB`) per the Stage-2 diagnostic note convention.
   - `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN` (`5 >= 1, 6 = N` -> `Rejected – G6 Cash & Fortress Balance Sheet`): keep Gate 4–6 scores and `4n`, strip `"Calamity pass..."` / `"Qualifies for Calamity Tier..."` wording from `note`.
4. **Scrub Obsolete Calamity Prose in Remaining `44` `inputs.csv` Rows**:
   - Rewrite/strip `"Ineligible for Calamity Tier..."` / `"Not eligible for Calamity Pass..."` / `"not a temporary fixable calamity"` phrases in `note` and `evidence` across the 44 non-calamity rows while preserving all underlying moat and financial rationale, achieving **zero** `calamit*` matches in `data/{us,eu,ca}/inputs.csv`.
5. **Regenerate `data/fundamentals.sqlite`**:
   - Run `build_sqlite_db()` from `screener/fetch/sqlite_db.py` so `companies` schema has 27 columns and 0 `'Calamity pass'` `result` rows.

### Step 3: Dashboard & `💎 Growth at ~0g` Tab (`screener/dashboard.py`)
1. **Python Data Collection (`collect_screener_data`)**:
   - Remove `passes_calamity_grade`, `calamity_flag`, `calamity_note`, `waived_gates`, `waived_keys`, `calamity_list`, and `summary["calamity_pass"]`.
   - Compute `passes_growth_0g`:
     ```python
     passes_growth_0g = bool(
         passes_quality_grade
         and val.get("status") == C.V_VALUED
         and val.get("g_market_flag") in (G_FLAG_OK, G_FLAG_SAT_LO)
         and val.get("g_market") is not None
         and val.get("g_market") < 0.05
         and val.get("g_org_exp") is not None
         and val.get("g_org_exp") >= 0.05
     )
     ```
   - Store `"passes_growth_0g": passes_growth_0g` on each record and `"growth_0g": sum(1 for c in all_companies if c["passes_growth_0g"])` in `summary`.
2. **HTML Structure (`build_dashboard_html`)**:
   - Use `data['summary'].get('growth_0g', 0)` for the top-bar KPI chip `#kpi-growth-0g` (`Growth at ~0g`, replacing `#kpi-calamity` `Prime Grade Calamity`).
   - Tab bar order (slot #1 default active `qpass`):
     1. `data-tab="qpass"` (`active`): `🛡️ Prime Grade` (mobile `🛡️ Prime`)
     2. `data-tab="growth_0g"`: `💎 Growth at ~0g` (mobile `💎 ~0g Growth`, pill `id="count-growth-0g"`)
     3. `data-tab="moat_universe"`: `🏰 Quality Grade` (mobile `🏰 Quality`)
     4. `data-tab="all"`: `🔍 Full Universe` (mobile `🔍 All`)
     5. `data-tab="methodology"`: `📖 Framework` (mobile `📖 Framework`)
   - `#filter-gate`: remove `<option value="Calamity pass">Calamity Pass</option>`.
   - `📖 Framework` tab HTML: delete `Prime Grade Calamity` card/bullet; document `💎 Growth at ~0g` and its predicate in `Dashboard Views & Quality Tiers`.
   - Drawer HTML: remove `#dossier-calamity-box`.
3. **Client-Side JS**:
   - `TAB_DEFAULT_SORTS`: replace `calamity` with `growth_0g: { col: 'g_org_exp', asc: false }` (`Model g ↓`).
   - `ALL_COLS` & `COL_TIPS`: remove `waived_gates`; rename `rejected_at.label` to `'Failing Gate'`.
   - Remove `calamityTag()`, `passesCalamityGrade()`, `WAIVED` stepper branch in `openDrawer()`, and `#dossier-calamity-box` logic.
   - Add `passesGrowth0g(c)` matching the Python predicate (`c.passes_growth_0g` when defined, with full field fallback).
   - Update `updateTabCounts()` to count `growth0g` and update `#kpi-growth-0g` and `#count-growth-0g`.
   - Enable `#filter-gate` on `growth_0g`: update `setTab()` (`showGateFilter`), `getFilteredData()` (tab predicate + gate filter), and `hasActiveFilters()` (`showExt` includes `currentTab === 'growth_0g'` so Reset button activates).
   - Update `renderTable()` for `growth_0g`: surface `g5_mgmt` (`G5 Mgmt`), `g6_cash` (`G6 B/S`), `result` (`Gate Status`), and `rejected_at` (`Failing Gate`) alongside core valuation columns in both compact and expanded views.
   - Update `renderCards()` and `exportCurrentView()` CSV export to remove calamity/waived logic and support `growth_0g`.

### Step 4: Specification & Documentation Updates
1. **`QUALITATIVE_EVALUATION_SPEC.md`**: Update `v7.18 -> v7.19` (`L1, 8`); remove all calamity/waiver/`unwaived`/`Non-Waivable Anchor`/`calamity_flag`/`calamity_note` rules, JSON fields, and table rows (`L15–18, 49, 60, 63, 67, 147, 186, 207, 299–300, 327–338, 349`) while preserving Stage 1 / Stage 2 waterfall rules.
2. **`COMPANY_EVALUATION_SPEC.md`**: Update `v7.18 -> v7.19` (`L1, 8`); remove all calamity/waiver/`unwaived`/`calamity_flag`/`calamity_note` references (`L15–18, 52, 63, 66, 70, 144, 172, 193, 256, 365–366, 393–404, 647, 653`); update `L660` tab list to `🛡️ Prime Grade`, `💎 Growth at ~0g`, `🏰 Quality Grade`, `🔍 Full Universe`, `📖 Framework` and document `💎 Growth at ~0g`; update `L547` Stage 2 note cleanly if needed.
3. **`QUANTITATIVE_EVALUATION_SPEC.md`**: Remove `Calamity pass` / `pre-calamity peaks` references on `L15`.
4. **`README.md`**: Update `L1` / `L17` / `L20–23` / `L299` / `L307` to retire `Calamity pass` & `Calamity Watchlist`, remove `calamity flag/note` from `inputs.csv` layout, and document `v7.19` + `💎 Growth at ~0g`.

### Step 5: Test Suite Updates & Additions
1. **Replace `tests/test_calamity_tier.py` with `tests/test_growth_0g_tier.py`** (remove `test_calamity_tier.py` so zero calamity test files remain):
   - Assert baseline Prime Grade counts (`us: 110, eu: 104, ca: 11`, total `225`) and `Quality Grade` = `443`.
   - Assert zero `calamity` / `calamity_note` columns in `inputs.csv` and `RES_CALAMITY` removed from `config.py`.
   - Assert `APD` & `EL` are Stage-1 scrubbed Gate-3 rejects; `11` `3b=Y` former calamity rows retain G4–G6 (`10` in Quality Grade, `RTX` excluded).
   - Assert `passes_growth_0g` selects exact `25` companies (`9` Prime, `6` `CAP >= 15Y` failing `G6 = N`, `10` `CAP = 5–10Y`), and test boundary conditions (`g_market = 0.05` excluded, `g_org_exp = 0.05` included, `saturated_low` allowed, `val_status != 'Valued'` excluded).
2. **`tests/test_dashboard_filters.py`**: Update mock `summary` (`"growth_0g": 0`), assert `"Growth at ~0g"`, `"💎 Growth at ~0g"`, `"💎 ~0g Growth"`, tab order, default sort `g_org_exp` desc, `#filter-gate` enabled on `growth_0g`, and `passes_growth_0g` filtering.
3. **`tests/test_v718_two_stage_waterfall.py`**: Update for v7.19 (`483` Stage-2 advancing, `506` G3 rejects, `16` `G5=0` rejects, `124` Stage-2 diagnostic rows, remove `calamity_violations`, `SCREENER_VERSION == "7.19"`, spec/HTML `v7.19` checks, JSC `inspectTable('growth_0g', ...)` + `#filter-gate`, `inspectDrawer('EL')` asserting `BLANK` on G4–G6 + `inspectDrawer('GOOGL')` asserting Stage-2 G6 FAIL without `WAIVED`, and fix `L650` `'PASS · 2/2'` -> `'ELITE'` to match `dashboard.py:3666`).
4. **`tests/test_bulk_scoring_e2e.py`**: Remove `"calamity"`/`"calamity_note"` fixtures, replace calamity Feature 9/T2/T3 checks with unconditional Stage-1 `3b=N` scrubbing and `funnel_ids` checks, update `485 -> 483` and `504 -> 506`.
5. **`tests/test_valuation_sandbox.py`**, **`tests/test_v71_remediation.py`**, **`tests/test_v72_remediation.py`**, **`tests/test_v76_g6_overrides.py`**, **`tests/test_v77_alignment.py`**: Remove all `calamity_pass` / `waived_gates` / `Calamity pass` references; update mock `summary` dicts to `"growth_0g": 0`; update column-order test to compare `qpass` and `growth_0g`.

### Step 6: End-to-End Verification, Audit, Build & Gate
1. Run `python3 screener/bulk_scorer.py --audit` -> must exit 0 with `483` Stage-2 advancing, `989` Gate-3 total, `0` violations.
2. Run `python3 -m unittest discover -s tests` -> must pass **100%** (0 failures, 0 errors).
3. Run `python3 build.py` -> must complete cleanly and regenerate `output/screener.html`, `output/index.html`, and `docs/index.html`.
4. Run independent review (`2` `teamwork_reviewer`), adversarial/empirical verification (`2` `teamwork_challenger`, including JS runtime via `jsc` and zero-calamity grep verification), and forensic integrity audit (`1` `teamwork_auditor`) before reporting completion.
