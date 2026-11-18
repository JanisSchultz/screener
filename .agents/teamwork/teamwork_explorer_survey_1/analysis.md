# v7.19 Codebase & Test Survey (`Calamity` Retirement + `💎 Growth at ~0g` Tab + Version Bump)

**Summary:** Every occurrence of `calamity` / `calamity_note` / `RES_CALAMITY` / calamity-waiver logic across `screener/`, `build.py`, `fetch_market_data.py`, `data/{us,eu,ca}/inputs.csv`, `tests/`, and specs has been mapped with exact file paths and line numbers, and the end-to-end R3 (`💎 Growth at ~0g`) data & JS/HTML flow is traced and verified (`25` matching companies: `9` Prime Grade, `6` `CAP >= 15Y` failing `G6 = N`, `10` `CAP = 5–10Y`).

---

## 1. Calamity Occurrences & Removal Map (R2)

### 1.1 Core Python Modules (`screener/`, `build.py`, `fetch_market_data.py`)

| File | Exact Lines | Symbols / Behavior | v7.19 Action |
|---|---|---|---|
| `screener/config.py` | L239–245 | `CALAMITY_GATES = ("3b", "5", "6")`, `CALAMITY_FLAG_DEF` | Remove both constants and comment. |
| `screener/config.py` | L313–317 | `RES_CALAMITY = "Calamity pass"`, `FUNNEL_RESULTS = (RES_QPASS, RES_CALAMITY)`, `Q_RESULTS` includes `RES_CALAMITY` | Remove `RES_CALAMITY`; set `FUNNEL_RESULTS = (RES_QPASS,)` (or remove if unused after updating `gates.py`); remove `RES_CALAMITY` from `Q_RESULTS`. |
| `screener/config.py` | L323–326 | `V_CALAMITY = "Calamity Watchlist"`, `LIST_CAPACITY = {V_VALUED: 350, V_CALAMITY: 100}` | Remove `V_CALAMITY` and its `LIST_CAPACITY` entry. |
| `screener/config.py` | L577–588, 712–713, 742, 745, 760, 763, 814 | Historical `CHANGELOG` entries (`6.25`, `7.18`, `7.15`, `7.14`, `7.9`, `7.8`, `7.1`) | Keep historical changelog entries or note retirement in `"7.19"` (note: R2 acceptance criterion asks for zero references across `screener/config.py` — check whether historical `CHANGELOG` prose should be preserved or reworded). |
| `screener/data.py` | L19 | `TAIL_FIELDS = ["calamity", "calamity_note", "note", "evidence"]` | Remove `"calamity"`, `"calamity_note"` -> `["note", "evidence"]`. |
| `screener/gates.py` | L192–222 | `phase_results(...)`: reads `calamity = company.get("calamity") == "Y"`, waives `3b` (`st[k] == "fail" and not calamity`) and `k in C.CALAMITY_GATES`, computes `waived` and `res = C.RES_CALAMITY if waived else C.RES_QPASS` | Remove calamity waiver logic; any `st[k] == "fail"` (including `3b`, `5`, `6`) immediately rejects at `C.RES_REJ[ph]`; `waived` becomes `[]` (or omitted) and final pass returns `C.RES_QPASS`. |
| `screener/gates.py` | L241–244 | `def funnel_ids(meta: dict, include_calamity: bool = True) -> list[str]:` | Simplify to `def funnel_ids(meta: dict) -> list[str]:` returning `[c["id"] for c in meta["companies"] if res[c["id"]]["result"] == C.RES_QPASS]`. |
| `screener/apply_evaluation.py` | L62–64 | `QUAL_KEY_MAP` entries `"calamity_flag"`, `"calamity"`, `"calamity_note"` | Remove from `QUAL_KEY_MAP`. |
| `screener/apply_evaluation.py` | L137–156, 258, 267, 271–298 | Calamity normalization, `clear_calamity()`, `cal_active` check on Gate `3b`, Gate 4 `CAP < 15` calamity clearing | Remove calamity normalization & `clear_calamity()`. Stage 1 checks `g1 == "N"`, `g2 == "N"`, or `g3a == "None" or g3b == "N"` (unconditionally scrubbing `4_*`, `4`, `4n`, `5`, `6`). Stage 2 checks `g4 < 15` / `g5 == 0` while preserving diagnostic `5` and `6`. |
| `screener/apply_evaluation.py` | L312–319, 370–372 | Warning when `calamity == "Y"` without eligible fail; error when `calamity == "Y"` lacks `calamity_note` | Remove both blocks. |
| `screener/bulk_scorer.py` | L15, 44, 52, 85 | Docstring, `CALAMITY_GATES` & `RES_CALAMITY` imports, `QUAL_COLUMNS` (`"calamity", "calamity_note"`) | Remove imports, `"calamity"`, `"calamity_note"` from `QUAL_COLUMNS`, and update docstring (also L783 `"20 qualitative fields"` -> 21 columns). |
| `screener/bulk_scorer.py` | L119, 129, 139, 149, 159, 169, 179, 189, 199, 209, 219 | `REFERENCE_SNAPSHOT` 11 entries each contain `"calamity": "", "calamity_note": ""` | Remove `"calamity"` and `"calamity_note"` keys from all 11 entries. |
| `screener/bulk_scorer.py` | L565, 576, 580, 585–592, 617–629, 651–675 | `validate_company_evaluation(...)`: `calamity_active`, `clear_keys` calamity scrubbing, `g3_failed = (g3a == "None") or (g3b == "N" and not calamity_active)`, calamity validation | Remove all calamity logic; `g3_failed = (g3a == "None") or (g3b == "N")` unconditionally scrubs `4_*`, `4`, `4n`, `5`, `6`. |
| `screener/bulk_scorer.py` | L977, 994, 1016, 1068–1116, 1203–1206, 1249 | `audit_gate_3_universe()`, `print_audit_report()`, `main()`: `calamity_violations` checks and `calamity_flag` exceptions in Stage 1/2 checks | Remove `calamity_violations` and calamity checks. Stage 1 checks `g3a == "None" or g3b == "N"`; Stage 2 checks `g3a in MOAT_TYPES and g3a != "None" and g3b == "Y"`. |
| `screener/fetch/sqlite_db.py` | L143, 202, 224 | `calamity TEXT,` in `CREATE TABLE companies`, `c.get("calamity")` in `comp_rows`, `INSERT OR REPLACE INTO companies VALUES ({','.join(['?'] * 28)})` | Remove `calamity TEXT` and `c.get("calamity")`; update `?` count from `28` to `27` and rebuild `data/fundamentals.sqlite`. |
| `screener/dashboard.py` | L113–116, 144–145, 151, 158–159, 251, 266 | Python data collection: `passes_calamity_grade`, `calamity_flag`, `calamity_note`, `waived_gates`, `waived_keys`, `calamity_list`, `summary["calamity_pass"]` | Remove all calamity fields and `summary["calamity_pass"]`; replace with `passes_growth_0g` and `summary["growth_0g"]`. |
| `screener/dashboard.py` | L1882–1883, 1899–1902, 1984, 2082–2093, 2210–2213 | HTML: KPI chip `Prime Grade Calamity`, tab button `calamity`, `#filter-gate` option `Calamity pass`, Framework tab Calamity section/tier description, `#dossier-calamity-box` | Replace KPI chip & tab with `Growth at ~0g` / `💎 Growth at ~0g`; remove `#filter-gate` `Calamity pass` option, `#dossier-calamity-box`, and Calamity text in Framework tab (document `💎 Growth at ~0g` instead). |
| `screener/dashboard.py` | L2645, 2656–2657, 2689–2693, 2772–2792, 2813, 2823, 2826, 2948, 2971, 3159–3171, 3208–3246, 3485–3530, 3616–3688, 3743–3750, 4723, 4737–4739 | JS: `TAB_DEFAULT_SORTS.calamity`, `waived_gates` col, `rejected_at` label (`'Failing / Waived Gate'`), `COL_TIPS`, `calamityTag()`, `passesCalamityGrade()`, `updateTabCounts()`, `getFilteredData()`, `renderTable()`, `renderCards()`, `openDrawer()` stepper `WAIVED` branch, `#dossier-calamity-box` binding, `exportCurrentView()` CSV columns | Remove all calamity/waived JS logic, rename `rejected_at` label to `'Failing Gate'`, remove CSV columns `'Calamity Flag', 'Waived Gates', 'Calamity Rationale'`, and wire `growth_0g` tab. |
| `build.py` | L38 | `print(f"  • Prime Grade Calamity (Conditional): {summary['calamity_pass']}")` | Replace with `Growth at ~0g` KPI line using `summary['growth_0g']`. |
| `fetch_market_data.py` | L4, L388 | Comment `# Quality-pass + Calamity-pass companies (default)` and `for qk in [*QUAL_CODES, "calamity", "calamity_note"]:` | Update comment to `Quality-pass companies` and loop over `QUAL_CODES` only. |

*Note:* `screener/migrations/` and `screener/v2..v4_2/` have **zero** occurrences of `calamity`.

---

### 1.2 Universe Data (`data/{us,eu,ca}/inputs.csv`)

- **Schema columns:** All three `inputs.csv` files currently include `calamity,calamity_note` before `note,evidence` (verified at `data/us/inputs.csv:1`, `data/eu/inputs.csv:1`, `data/ca/inputs.csv:1`).
- **13 active `calamity = 'Y'` rows:**
  - **2 rows with `3b = N` (US: `APD`, `EL`)**:
    - `us:APD`: `3a="Toll booth & switching costs"`, `3b="N"`, currently `4=25, 5=0, 6=N` -> Stage-1 waterfall scrubbing clears `4_ent..4_sub, 4, 4n, 5, 6` so it becomes `Rejected – G3 Moat & Pricing`.
    - `us:EL`: `3a="Irreplaceable infrastructure & intangibles"`, `3b="N"`, currently `4=15, 5=0, 6=N` -> Stage-1 waterfall scrubbing clears `4_ent..4_sub, 4, 4n, 5, 6` so it becomes `Rejected – G3 Moat & Pricing`.
    - Funnel effect: Stage-2 advancing `485 -> 483`; Gate-3 rejects `504 -> 506` (`483 + 506 = 989`).
  - **11 rows with `3b = Y`** (retain Gate 4–6 scores & notes):
    - **3 becoming `Rejected – G5 Management` (`5 = 0`, all EU):** `DGE.GB` (`CAP=15, G5=0, G6=Y, g6_flags=1`), `NESN.CH` (`CAP=15, G5=0, G6=N, g6_flags=2`), `RTO.GB` (`CAP=15, G5=0, G6=N, g6_flags=2`).
    - **8 becoming `Rejected – G6 Cash & Fortress Balance Sheet` (`5 >= 1, 6 = N`, all US):** `GOOGL` (`g6_flags=0`), `NDAQ` (`g6_flags=1`), `HONA` (`g6_flags=1`), `NOC` (`g6_flags=1`), `RTX` (`g6_flags=3`), `EFX` (`g6_flags=2`), `SNPS` (`g6_flags=1`), `TXN` (`g6_flags=0`).
    - **Quality Grade retention:** `10` of the `11` have `g6_flags < 3` and remain in `🏰 Quality Grade` (`RTX` has `g6_flags = 3`, so `passes_quality_grade = False`).
    - **`Prime Grade`:** Unchanged at `225` (`us: 110, eu: 104, ca: 11`).
- **Important Data Detail — Prose mentions in `note` / `evidence`:**
  - `56` rows across `data/us/inputs.csv` and `data/eu/inputs.csv` contain `calamit*` in `note` and/or `evidence`:
    - `12` of the `13` former calamity rows (`GOOGL, EL, NDAQ, HONA, RTX, EFX, SNPS, TXN, APD, DGE.GB, NESN.CH, RTO.GB` — all except `NOC`) explicitly say `"Calamity pass..."` / `"Qualifies for Calamity Tier..."` / `"Calamity pass tier..."` in `note`.
    - `44` other rows (`APP, OMC, SPCX, FOXA, CHTR, CMCSA, T, VZ, TTWO, META, DIS, LYV, NFLX, SKYD, NWSA, TMUS, LULU, F, TSLA, APTV, AZO, AMZN, LVS, GPC, LEN, NVR, ABNB, CCL, RCL, DPZ, XOM, MDT, ILMN, NSC, ANET, AMD, INTC, ARM, CRWD, IFF, VTR, UDR, CPR.IT, FLS.DK`) contain `"Ineligible for Calamity Tier..."` / `"Not eligible for Calamity Pass..."` / `"temporary fixable calamity"` in `note` or `evidence`.
  - Also, `DGE.GB`, `NESN.CH`, and `RTO.GB` do **not** currently carry `[Diagnostic G5=0 | G6=<Y|N>: ...]` in `note` (relevant to `test_note_hygiene_across_all_121_newly_completed_rows` in `tests/test_v718_two_stage_waterfall.py`, where `G5=0` rejects rises from `13` to `16` and `121` becomes `124`).

---

## 2. R3 Trace: `💎 Growth at ~0g` Tab & Dashboard Architecture

### 2.1 Python Data Pipeline (`screener/dashboard.py:collect_screener_data`)
- `passes_g123a` (L96–101): `st_map["1"] == "pass" and st_map["2"] == "pass" and moat_arch_val not in (None, "", "None") and not audit["moat_partial"]`
- `g6_flags` (L102–103): `sum(1 for v_ in g6_checks(fin, sub_ind, p).values() if v_ == "flag")`
- `passes_quality_grade` (L104–108): `passes_g123a and st_map.get("3b") == "pass" and g6_flags < 3` -> `443` companies currently.
- `passes_prime_grade` (L109–112): `pres.get("result") == C.RES_QPASS and g6_flags < 3` -> `225` companies.
- `val_status` (L209): `val.get("status", C.V_NODATA)` (`C.V_VALUED = "Valued"`).
- `g_market` (L228), `g_market_flag` (L229): from `gates.py:solve_market_growth` (`G_FLAG_OK = "ok"`, `G_FLAG_SAT_LO = "saturated_low"`).
- `g_org_exp` (L224): organic Model g (`g0`).
- **New `passes_growth_0g` predicate:**
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
- **Verified live count (`25` companies, `0` boundary ties, `0` calamity overlaps):**
  - `9` Prime Grade: `us:PGR`, `eu:MC.FR`, `us:ZTS`, `eu:DG.FR`, `eu:AUTO.GB`, `eu:BNZL.GB`, `eu:WKL.NL`, `eu:PGHN.CH`, `eu:GTT.FR`
  - `6` `CAP >= 15Y` failing `G6 = N`: `eu:VER.AT`, `us:FICO`, `eu:AAK.SE`, `eu:A2A.IT`, `eu:PST.IT`, `eu:HER.IT`
  - `10` `CAP = 5–10Y` (`Rejected – G4 Runway (<15Y)`): `us:ADBE`, `us:ACGL`, `us:DECK`, `us:IT`, `us:ACN`, `us:HIG`, `us:LII`, `eu:NWG.GB`, `eu:FGR.FR`, `us:GL`
- `summary` dict (L263–269): replace `"calamity_pass": len(calamity_list)` with `"growth_0g": sum(1 for c in all_companies if c["passes_growth_0g"])` (`25`).

### 2.2 Dashboard HTML / CSS / JS (`screener/dashboard.py`)
1. **Top-Bar KPI Chips** (L1872–1889):
   - Replace `#kpi-calamity` (`Prime Grade Calamity`, `amber`) with `#kpi-growth-0g` (`Growth at ~0g`, value `{data['summary']['growth_0g']}`).
   - In `updateTabCounts()` (L2810–2830): compute `const growth0g = base.filter(c => passesGrowth0g(c));`, update `setKpi('kpi-growth-0g', growth0g.length);` and `document.getElementById('count-growth-0g').textContent = growth0g.length;`.
2. **Tabs & Tab Order** (L1893–1918):
   1. `data-tab="qpass"` (`active` by default) — `🛡️ Prime Grade` / mobile `🛡️ Prime`
   2. `data-tab="growth_0g"` (replaces `calamity`) — `💎 Growth at ~0g` / mobile `💎 ~0g Growth`, pill `id="count-growth-0g"`
   3. `data-tab="moat_universe"` — `🏰 Quality Grade` / mobile `🏰 Quality`
   4. `data-tab="all"` — `🔍 Full Universe` / mobile `🔍 All`
   5. `data-tab="methodology"` — `📖 Framework` / mobile `📖 Framework`
3. **Default Landing Tab & Default Sort** (L2634, 2643–2648, 2752):
   - `currentTab = 'qpass'` and `init()` calls `setTab('qpass')`.
   - `TAB_DEFAULT_SORTS`: `qpass`, `growth_0g`, `moat_universe`, `all` all default to `{ col: 'g_org_exp', asc: false }` (`Model g ↓`).
4. **Filter Bar Visibility & Reset State** (L2854–2860, 2960–2983, 3098–3107):
   - `showGateFilter`: update to `(tab === 'all' || tab === 'moat_universe' || tab === 'growth_0g')`.
   - `getFilteredData()`:
     - Tab filter: `if (currentTab === 'growth_0g' && !passesGrowth0g(c)) return false;`
     - Gate filter condition: `(currentTab === 'all' || currentTab === 'moat_universe' || currentTab === 'growth_0g') && gate !== 'all'`.
   - **Important bug-prevention catch:** `hasActiveFilters()` at L3104 also checks `const showExt = (currentTab === 'all' || currentTab === 'moat_universe');` — must add `|| currentTab === 'growth_0g'` so the `✕ Reset` button activates when `#filter-gate` is non-`'all'` on `growth_0g`.
   - `#filter-gate` `<option value="Calamity pass">` (L1984) removed.
5. **Column Definitions (`renderTable`, L3142–3182)** & **`ALL_COLS` (L2651–2685)**:
   - Rename `ALL_COLS.rejected_at.label` from `'Failing / Waived Gate'` to `'Failing Gate'`; remove `ALL_COLS.waived_gates` and its `COL_TIPS` entry.
   - Surface `G5 Mgmt` (`g5_mgmt`), `G6 B/S` (`g6_cash`), `Gate Status` (`result`), and `Failing Gate` (`rejected_at`) alongside core valuation columns in `growth_0g`:
     - Compact mode: `[...compactKeys, 'g5_mgmt', 'g6_cash', 'result', 'rejected_at']` (or `[...compactKeys, 'result', 'rejected_at', 'g5_mgmt', 'g6_cash']`).
     - Expanded mode: `[...coreValuationCols, ALL_COLS.g5_mgmt, ALL_COLS.g6_cash, ALL_COLS.result, ALL_COLS.rejected_at, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.sector]` (mirrors `moat_universe` expanded columns).
   - JS `passesGrowth0g(c)` fallback (when `c.passes_growth_0g === undefined`):
     ```javascript
     function passesGrowth0g(c) {
       if (c.passes_growth_0g !== undefined) return Boolean(c.passes_growth_0g);
       return passesQualityGrade(c)
         && c.val_status === 'Valued'
         && (c.g_market_flag === 'ok' || c.g_market_flag === 'saturated_low')
         && c.g_market !== null && c.g_market !== undefined && c.g_market < 0.05
         && c.g_org_exp !== null && c.g_org_exp !== undefined && c.g_org_exp >= 0.05;
     }
     ```
6. **Cards View (`renderCards`, L3485–3554)**:
   - Remove `|| currentTab === 'calamity'` from L3485; `growth_0g` falls into the `else` branch which already displays `result`, `rejected_at`, `g3a_moat_archetype`, and all valuation cards.

---

## 3. Version String & Spec Inventory (R4)

| Location | Lines / Details |
|---|---|
| `screener/config.py` | `SCREENER_VERSION = "7.18"` (L328) -> `"7.19"`, plus add `"7.19": [...]` to `CHANGELOG` (L330). |
| `screener/bulk_scorer.py` | Docstring `(v7.18)` (L1), `print_audit_report()` header `(v7.18)` (L1160) -> `v7.19`. |
| `QUALITATIVE_EVALUATION_SPEC.md` | Header `v7.18` (L1, L8) -> `v7.19`, plus calamity removal at L15, 17, 18, 60, 186, 299–300, 336–338, 349. |
| `COMPANY_EVALUATION_SPEC.md` | Header `v7.18` (L1, L8) -> `v7.19`, plus calamity removal at L15, 17, 18, 63, 172, 256, 365–366, 402–404, 547, 647, 653, 660. |
| `QUANTITATIVE_EVALUATION_SPEC.md` | L15 references `Calamity pass` / `pre-calamity peaks` — also update! |
| `README.md` | Calamity mentions at L17, 63, 133–136, 307 (`inputs.csv` schema list); update for v7.19 (`💎 Growth at ~0g`, retirement of Calamity). |
| Built HTML outputs | `output/screener.html`, `output/index.html`, `docs/index.html` (regenerated via `python3 build.py`). |

---

## 4. Test Suite Inventory & Required Updates

### 4.1 Test Files Containing `calamity` / `calamity_pass` / `7.18` / Tab Assertions

1. **`tests/test_calamity_tier.py`** (252 lines, 13 tests):
   - Entirely tests v6.25 Calamity Pass tier (`C.RES_CALAMITY`, `include_calamity`, `calamity` waterfall, `Prime Grade Calamity` HTML).
   - Must be retired/replaced (or rewritten to assert calamity absence + `passes_growth_0g` / baseline counts `{"us": 110, "eu": 104, "ca": 11}`).
2. **`tests/test_dashboard_filters.py`** (113 lines):
   - L22: mock `summary` uses `"calamity_pass": 0` -> update to `"growth_0g": 0`.
   - L33: asserts `"Prime Grade Calamity"` in HTML -> replace with `"Growth at ~0g"`, `"💎 Growth at ~0g"`, `"💎 ~0g Growth"`.
   - L39, 59–62, 76: asserts `passes_calamity_grade` and `gate == "Calamity pass"` -> remove/replace with `passes_growth_0g` tests (`25` total: `9` Prime, `6` `CAP>=15 & G6=N`, `10` `CAP<15`).
3. **`tests/test_v718_two_stage_waterfall.py`** (723 lines):
   - L84, 98–127, 134, 198, 204–285: tests calamity clearing on Gate 4 `< 15` / `3b=N` -> rewrite without `calamity_flag`/`calamity_note` (now `3b="N"` always Stage-1 scrubs regardless of downstream fields).
   - L311: `audit["calamity_violations"]` -> remove assertion.
   - L335: `self.assertIn("v7.18", proc.stdout)` -> update to `"v7.19"` (or `C.SCREENER_VERSION`).
   - L339–443: `485` advancing -> `483`, `504` G3 rejects -> `506`, `calamity_3b == ["APD", "EL"]` -> both are now G3 rejects (`3b="N"`), `calamity_all`/`calamity_pg`/`summary["calamity_pass"]` -> remove; `g5_rejects` increases from `13` (`eu: 4`) to `16` (`eu: 7`: adds `DGE.GB`, `NESN.CH`, `RTO.GB`).
   - L444–480: `newly_completed` (`CAP < 15 or 5 == "0"`) increases from `121` to `124` (`DGE.GB`, `NESN.CH`, `RTO.GB` join `5 == "0"` rejects, and currently lack `[Diagnostic G5=0 | G6=...]` in `note`).
   - L491–527, 616, 675–696, 702, 714: `7.18` version checks, `calamity` expanded columns assertion (`L520`), JSC `inspectTable('calamity', ...)`, `inspectDrawer('EL')` `WAIVED` check (EL becomes G3 reject -> `BLANK` on G4/G5/G6!), and spec `v7.18` checks.
   - **Pre-existing failure observed on baseline:** `test_dashboard_runtime_js_openDrawer_and_renderTable_via_jsc` currently FAILS at L650 (`AssertionError: 'PASS · 2/2' not found` because `dashboard.py:3666` renders `'ELITE'` instead of `'PASS · 2/2'`).
4. **`tests/test_bulk_scoring_e2e.py`** (1,384 lines):
   - L79–80: `make_test_company` has `"calamity": "", "calamity_note": ""`.
   - L387–405: Stage 2 Gate 4 `< 15` calamity clear test.
   - L453–499: Feature 9 (`test_t1_f9_01..05`) tests `C.RES_CALAMITY`, `calamity_note` required, `funnel_ids(..., include_calamity=...)`.
   - L531: checks `"calamity", "calamity_note"` in `inputs.csv`.
   - L812–840 (`test_t2_f7_02..05`), L848 (`ASML` mirror keys), L880–909 (`test_t2_f9_01..05`), L928–931 (`test_t2_f10_04_calamity_flagged_count` == 13), L969–973 (`test_t2_f11_04_dashboard_renders_calamity_badge`), L1034–1040 (`test_t3_07`), L1067–1078 (`test_t3_11`), L1262, L1266 (`ASML`/`FER` mirror keys).
   - L1317–1375: `test_all_989_gate3_companies_completed` asserts `g3_advancing == 485`, `g3_rejected == 504` (must become `483` and `506`), and checks `row.get("calamity")`.
5. **`tests/test_valuation_sandbox.py`** (678 lines):
   - L142: mock `summary` has `"calamity_pass": 0` -> `"growth_0g": 0`.
   - L202–207: `test_consistent_column_order_across_qpass_and_calamity` checks `ALL_COLS.waived_gates` line in `dashboard.py` -> update to test `qpass` and `growth_0g`.
   - L555: `if c.get("result") not in ("Quality pass", "Calamity pass"):` -> `if c.get("result") != "Quality pass":` (or `C.RES_QPASS`).
6. **`tests/test_v71_remediation.py`** (L175–179): `test_sandbox_payload_does_not_touch_calamity` -> remove or repurpose.
7. **`tests/test_v72_remediation.py`** (L136), **`tests/test_v76_g6_overrides.py`** (L93), **`tests/test_v77_alignment.py`** (L64): mock `summary` dicts pass `"calamity_pass": 0` -> update to `"growth_0g": 0` (and in `dashboard.py` HTML template, use `data['summary'].get('growth_0g', 0)` defensively or update all mocks).
8. **`tests/test_cap_engine.py`** & **`tests/test_quantitative_growth.py`**: No calamity references (`test_quantitative_growth.py:552-558` validates `data/fundamentals.sqlite`, which must remain valid after updating `sqlite_db.py`).
