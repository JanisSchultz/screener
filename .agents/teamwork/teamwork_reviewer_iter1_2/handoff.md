# Independent Review & Adversarial Challenge Report — `teamwork_reviewer_iter1_2`

**Verdict:** `APPROVE`  
**Overall Risk Assessment:** `LOW`  
**Timestamp:** 2026-11-18T10:01:00Z  
**Scope:** Dashboard UI/JS (`screener/dashboard.py`, `output/screener.html`, `output/index.html`, `docs/index.html`), Specs & Changelog (`screener/config.py`, `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `QUANTITATIVE_EVALUATION_SPEC.md`, `README.md`), Data Fidelity (`data/{us,eu,ca}/inputs.csv`), and Targeted Unit Tests (`tests/test_growth_0g_tier.py`, `tests/test_dashboard_filters.py`).

---

## 1. Observation

### A. `passes_growth_0g` & Dashboard UI/JS (`screener/dashboard.py`, `output/screener.html`, `output/index.html`, `docs/index.html`)
1. **Python & JS Predicate Parity**:
   - `screener/dashboard.py:123–131` computes `passes_growth_0g` as:
     `passes_quality_grade and val.get("status") == C.V_VALUED and val.get("g_market_flag") in (G_FLAG_OK, G_FLAG_SAT_LO) and val.get("g_market") is not None and val.get("g_market") < 0.05 and val.get("g_org_exp") is not None and val.get("g_org_exp") >= 0.05`.
   - `screener/dashboard.py:2788–2795` defines `passesGrowth0g(c)` returning `Boolean(c.passes_growth_0g)` when defined, with an identical field fallback (`passesQualityGrade(c) && c.val_status === 'Valued' && (c.g_market_flag === 'ok' || c.g_market_flag === 'saturated_low') && c.g_market !== null && c.g_market !== undefined && c.g_market < 0.05 && c.g_org_exp !== null && c.g_org_exp !== undefined && c.g_org_exp >= 0.05`).
   - Across all `1,175` companies in `output/screener.html`, deleting precomputed `passes_growth_0g` / `passes_quality_grade` / `passes_g123a` / `passes_prime_grade` and evaluating `passesGrowth0g(copy)` in JavaScriptCore (`jsc`) produced `0` mismatches against Python's `passes_growth_0g`.
2. **Exact Counts & Cohort Breakdown**:
   - `summary` in `output/screener.html` (`line 2338`) and `collect_screener_data(["us", "eu", "ca"])`: `total_companies: 1175`, `quality_pass: 225`, `growth_0g: 25`, `valued: 220`, `median_excess_irr: -0.11706094013878286` (`-11.7pp`).
   - The `25` `passes_growth_0g` companies break down exactly into:
     - `9` Prime Grade (`PGR`, `MC`, `ZTS`, `DG`, `AUTO`, `BNZL`, `WKL`, `PGHN`, `GTT`)
     - `6` `CAP >= 15Y` failing `G6 = N` (`VER`, `FICO`, `AAK`, `A2A`, `PST`, `HER`)
     - `10` `CAP = 5–10Y` (`ADBE`, `ACGL`, `DECK`, `IT`, `ACN`, `HIG`, `LII`, `NWG`, `FGR`, `GL`)
3. **Tab Order, KPI Chip, Default Sort, Columns & Controls**:
   - `screener/dashboard.py:1904–1929` and rendered `output/screener.html` order the 5 `.tab-btn` buttons identically:
     1. `data-tab="qpass"` (`active`): `🛡️ Prime Grade` (mobile `🛡️ Prime`)
     2. `data-tab="growth_0g"`: `💎 Growth at ~0g` (mobile `💎 ~0g Growth`, pill `count-growth-0g`)
     3. `data-tab="moat_universe"`: `🏰 Quality Grade` (mobile `🏰 Quality`)
     4. `data-tab="all"`: `🔍 Full Universe` (mobile `🔍 All`)
     5. `data-tab="methodology"`: `📖 Framework` (mobile `📖 Framework`)
   - Top-bar KPI chip (`screener/dashboard.py:1892–1895`) renders `Growth at ~0g` (`#kpi-growth-0g` = `25`) in place of `Prime Grade Calamity`.
   - `TAB_DEFAULT_SORTS.growth_0g` (`L2646`) is `{ col: 'g_org_exp', asc: false }` (`Model g ↓`).
   - `#filter-gate` is enabled on `growth_0g` in `setTab()` (`L2853`), `getFilteredData()` (`L2966`), and `hasActiveFilters()` (`L3101` `showExt`).
   - `renderTable()` surfaces `g5_mgmt` (`G5 Mgmt`), `g6_cash` (`G6 B/S`), `result` (`Gate Status`), and `rejected_at` (`Failing Gate`) in both compact (`L3157–3158`) and expanded (`L3168–3169`) modes alongside core valuation columns.
   - `renderCards()` (`L3460–3561`), `openDrawer()` (`L3564–3838`), `exportCurrentView()` (`L4678–4733`), and `📖 Framework` (`L2059–2100`) contain zero `calamit*` or `waiv*` references; `renderCards()` uses the gate-stage branch for `growth_0g`, and `📖 Framework` documents `💎 Growth at ~0g` (`L2095`).
   - `output/screener.html`, `output/index.html`, and `docs/index.html` are byte-identical (`sha256: dc4e23e4a479ba9ef312d316d8fe6ba8ea4482ae6b6825efbee7840479e286d1`).

### B. Specs, Version & Changelog (`screener/config.py`, Specs, `README.md`)
1. `screener/config.py`: `SCREENER_VERSION = "7.19"` (`L319`), `CHANGELOG["7.19"]` (`L699–708`) accurately records calamity retirement, `APD`/`EL` Stage-1 scrubbing (`483` Stage-2 + `506` G3 rejects = `989` G3), retention of `11` `3b=Y` former calamity tickers (`10` in Quality Grade, `RTX` excluded by 3 G6 flags, Prime Grade `225`), and addition of `Growth at ~0g` (`25`). Historical `"6.25"`, `"7.1"`, `"7.8"`, `"7.13"`, `"7.14"`, `"7.15"`, `"7.18"` changelog entries remain as release history.
2. Zero `calamit*` or `waiv*` matches in `screener/dashboard.py`, `QUALITATIVE_EVALUATION_SPEC.md` (`v7.19`), `COMPANY_EVALUATION_SPEC.md` (`v7.19`), and `QUANTITATIVE_EVALUATION_SPEC.md` (`v7.7`, updated `L15` to reference `💎 Growth at ~0g`).
3. `README.md` active sections (`L1` `v7.19`, `L17–L19` tiers, `L314` `inputs.csv` layout) contain zero calamity/waiver remnants; only release-note sections (`L22–L24` `v7.19`, `L70` `v7.1`, `L140–L143` `v6.25`) mention `calamity`/`waiver`.

### C. Data Fidelity (`data/{us,eu,ca}/inputs.csv`)
1. Column counts updated (`us: 31->29`, `eu: 31->29`, `ca: 30->28`), removing `calamity` and `calamity_note`. Zero `calamit*` matches across all `data/{us,eu,ca}/{inputs,financials}.csv`.
2. `git show HEAD:data/{us,eu,ca}/inputs.csv` diff against working tree shows `51` changed US rows, `5` changed EU rows, `0` changed CA rows:
   - `APD` & `EL` (`3b=N`): `4_ent..4_sub`, `4`, `4n`, `5`, `6` scrubbed to `""` and notes updated to standard Gate 3 rejections (`Rejected – G3 Moat & Pricing`).
   - `DGE.GB`, `NESN.CH`, `RTO.GB` (`5=0`): Gate 4–6 scores and `4n` retained; notes cleanly carry `[Diagnostic G5=0 | G6=Y: ...]` (`DGE.GB`) / `[Diagnostic G5=0 | G6=N: ...]` (`NESN.CH`, `RTO.GB`).
   - `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN` (`5>=1, 6=N`): Gate 4–6 scores and `4n` retained; notes updated cleanly (`NOC` already had zero calamity phrasing).
   - Remaining changed rows (`43` non-calamity prose cleanups across `note`/`evidence`): zero double-space/punctuation/truncation artifacts found; economic and financial rationale preserved verbatim aside from removing calamity-tier eligibility phrasing.
3. Three `waiv` hits in `data/us/inputs.csv` are non-tier prose: `EBAY 4n` (`seller-fee waivers`), `SPCX evidence` (`waiving investor class actions`), and `SPCX`/`RDDT` `note` (`Gate 1 is non-waivable` / `non-waivable Anchor Gate`).

### D. Targeted Unit Tests & JSC Runtime
- `python3 -m unittest -v tests/test_growth_0g_tier.py tests/test_dashboard_filters.py`: **12 tests in 5.350s — OK**.
- `jsc` execution of extracted `<script>` from `output/screener.html`: **JSC_ALL_CHECKS_PASSED** (exit code 0).

---

## 2. Logic Chain

1. Observation A.1–A.3 + JSC verification prove that Python (`collect_screener_data`) and JS (`passesGrowth0g`, `setTab`, `getFilteredData`, `hasActiveFilters`, `renderTable`, `renderCards`, `openDrawer`, `exportCurrentView`) implement identical predicates and UI behavior for `growth_0g`, surfacing exact counts (`25` = `9` Prime + `6` G6-fail + `10` CAP 5–10Y) with `#filter-gate` and Reset working end-to-end.
2. Observation B.1–B.3 confirms all active specs, `README.md` active sections, `screener/config.py`, and `output/*.html` / `docs/index.html` align on `v7.19` with zero calamity/waiver leakage outside historical changelog entries.
3. Observation C.1–C.3 confirms the `inputs.csv` data migration preserved all `3b=Y` Gate 4–6 evaluations, scrubbed `APD`/`EL` cleanly per Stage 1, formatted Stage-2 diagnostic notes (`[Diagnostic G5=0 | G6=...]`), and removed obsolete calamity prose without corrupting notes.
4. Observation D confirms both `unittest` (`12/12`) and live `jsc` execution pass cleanly with zero integrity violations or dummy workarounds.

---

## 3. Caveats

- Per dispatch instructions, `build.py` and `tests/test_bulk_scoring_e2e.py` (and the full 317-test suite) were **not** run by this agent to avoid overwriting `output/*.html` while `teamwork_reviewer_iter1_1` runs them.
- `jsc` verification used a lightweight DOM mock rather than a live Chromium browser, so CSS visual spacing/overflow on `💎 Growth at ~0g` was verified by code inspection rather than pixel rendering.
- Minor non-blocking observation: `SPCX` and `RDDT` `note` fields still contain the generic phrase `"non-waivable"` (`Gate 1 is non-waivable`, `non-waivable Anchor Gate`), which is standard Anchor-Gate terminology rather than Calamity-tier logic.

---

## 4. Conclusion

**Verdict: `APPROVE`** (0 Critical, 0 Major, 0 Minor findings).  
The Dashboard UI/JS, `passes_growth_0g` predicate and `💎 Growth at ~0g` tab, v7.19 specs/changelog, and `inputs.csv` prose/data migration satisfy all requirements in `ORIGINAL_REQUEST.md` and `plan.md` cleanly and accurately.

---

## 5. Verification Method

1. **Targeted Unit Tests (read-only)**:
   ```bash
   python3 -m unittest -v tests/test_growth_0g_tier.py tests/test_dashboard_filters.py
   ```
   Expected: `Ran 12 tests ... OK`.
2. **HTML Sync & Active Zero-Calamity Scan**:
   ```bash
   shasum -a 256 output/screener.html output/index.html docs/index.html
   ```
   Expected: all 3 hashes identical (`dc4e23e4a479ba9ef312d316d8fe6ba8ea4482ae6b6825efbee7840479e286d1`).
3. **JSC Runtime & Python/JS Parity Check**:
   Run `/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc` on `<script>` extracted from `output/screener.html` verifying `init()`, `passesGrowth0g` fallback parity across all 1,175 rows, `setTab('growth_0g')`, `#filter-gate` counts (`9`, `6`, `10`, `25`), `hasActiveFilters()`, `resetAllFilters()`, `renderTable()` headers (`G5 Mgmt`, `G6 B/S`, `Gate Status`, `Failing Gate`), `exportCurrentView()`, and `openDrawer()` on `us:GOOGL`, `eu:DGE.GB`, `us:EL`, `us:APD`.
4. **CSV Diff Audit**:
   Compare `git show HEAD:data/{us,eu,ca}/inputs.csv` vs working tree for column removal (`31->29` US/EU, `30->28` CA), `APD`/`EL` Stage-1 scrubbing, 11 `3b=Y` former calamity retention, and prose cleanup integrity.
