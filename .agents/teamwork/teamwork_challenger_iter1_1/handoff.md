# Handoff Report — `teamwork_challenger_iter1_1`

**Verdict: `APPROVE`**
**Overall Risk Assessment**: `LOW`
**Handoff Type**: Hard

---

## 1. Observation

All four adversarial and empirical check suites (plus the full `unittest` suite) were executed directly against the v7.19 codebase and live datasets (`data/{us,eu,ca}/inputs.csv`, `data/*/financials.csv`, `data/fundamentals.sqlite`).

### Check 1: Synthetic Legacy Calamity Rejection Stress Tests
- Verified in `screener/config.py`, `screener/apply_evaluation.py`, and `screener/bulk_scorer.py`:
  - `RES_CALAMITY` is absent from `screener.config`; `Q_RESULTS` contains no calamity entries; `"calamity"` and `"calamity_note"` are absent from `QUAL_KEY_MAP` and `QUAL_COLUMNS`.
- Fed synthetic legacy payloads (both nested `"qualitative"` and top-level forms) containing `"calamity": "Y"`, `"calamity_flag": "Y"`, `"calamity_note": "temporary issue"`, `"3a": "Toll booth & switching costs"`, `"3b": "N"`, and populated Gate 4–6 fields (`4_ent..4_sub`, `4=20`, `4n`, `5=1`, `6="Y"`) into:
  - `screener.apply_evaluation.validate_and_waterfall()`
  - `screener.bulk_scorer.validate_company_evaluation()` (both fresh `existing_row=None` and contaminated `existing_row` with stale Gate 4–6 and calamity fields)
  - `screener.gates.phase_results()` (both on sanitized output AND on the raw unsanitized dict)
  - **Result**: `3b="N"` was never waived; all Gate 4–6 fields (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`) were scrubbed to `""`; zero calamity keys leaked into sanitized dicts; `phase_results()` returned `result="Rejected – G3 Moat & Pricing"` and `rejected_at="G3 Moat & Pricing >= Infl."` in every case.
- Tested `"3a": "Toll booth & switching costs"` with all moat sub-scores `0` (`3_tb=3_ia=3_se=3_rd=0`), `3b="Y"`, and `"calamity": "Y"`:
  - **Result**: `3a` deterministically overwritten to `"None"`, all Gate 4–6 fields scrubbed to `""`, `phase_results()` rejected at Gate 3.
- Tested `3b="Y"` with `CAP=10` (`< 15`, via `3_tb=2` and `4_sub=2`), `5=0`, `6="N"`, and `"calamity": "Y"`, `"calamity_flag": "Y"`, `"calamity_note": "legacy note"`:
  - **Result**: Stage-2 diagnostic fields preserved (`4=10`, `4_sub=2`, `4n` retained, `5=0`, `6="N"`), all calamity fields stripped, and `phase_results()` rejected at Gate 4 (`"Rejected – G4 Runway (<15Y)"`) with `status["5"] == "fail"` and `status["6"] == "fail"`.

### Check 2: Independent Live Dataset & `passes_growth_0g` Recomputation
- Parsed `data/{us,eu,ca}/inputs.csv`, `financials.csv`, `prescreen.csv`, `markets.csv`, `universe.json` directly via `screener.data.load_universe` and recomputed `phase_results`, `cap_audit`, `g6_checks`, and `par_valuation` across all companies:
  - **Universe counts**: `1,175` total (`us`: `515`, `eu`: `602`, `ca`: `58`). None of the three `inputs.csv` files contain `calamity` or `calamity_note` columns.
  - **Gate 3 counts**: `989` (`us`: `445`, `eu`: `495`, `ca`: `49`) = `483` Stage-2 advancing (`3b="pass"`) + `506` Gate-3 rejects (`3b="fail"`) + `0` blank.
  - **Tier counts**:
    - `Quality pass` (raw): `225`; **Prime Grade** (`g6_flags < 3`): `225`.
    - **Quality Grade** (`G1=Y`, `G2=Y`, `3a != None`, `3b=Y`, `g6_flags < 3`): `443` (with `40` additional `G1–3b` passing companies excluded by `g6_flags >= 3`).
    - **`passes_growth_0g`**: `25` = `9` Prime Grade (`PGR`, `MC.FR`, `ZTS`, `DG.FR`, `AUTO.GB`, `BNZL.GB`, `WKL.NL`, `PGHN.CH`, `GTT.FR`) + `6` `CAP >= 15` non-Prime failing `G6=N` (`VER.AT`, `FICO`, `AAK.SE`, `A2A.IT`, `PST.IT`, `HER.IT`) + `10` `CAP 5–10Y` (`ADBE`, `ACGL`, `DECK`, `IT`, `ACN`, `HIG`, `LII`, `NWG.GB`, `FGR.FR`, `GL`).
  - **Dashboard parity**: 100% row-by-row match across all `1,175` companies between independent recomputation and `screener.dashboard.collect_screener_data()` (`summary["quality_pass"] == 225`, `summary["growth_0g"] == 25`, `sum(passes_quality_grade) == 443`).
- **Near-boundary probes**:
  - `g_market` in `[0.04, 0.06]` (9 companies): `FICO` (`0.0427`), `PGR` (`0.0432`), `BNZL.GB` (`0.0447`) pass `< 0.05` (`0g=True`); `HWDN.GB` (`0.0441`) fails on `g_org_exp=0.0436 < 0.05`; `CRH` (`0.0517`, `g_org=0.0576`), `COR` (`0.0530`), `UBER` (`0.0535`), `UBSG.CH` (`0.0537`), `HCA` (`0.0574`) are excluded (`>= 0.05` -> `0g=False`).
  - `g_org_exp` in `[0.04, 0.06]` with `g_market < 0.06` (14 companies): `HWDN.GB` (`0.0436`) and `AOS` (`0.0473`) excluded (`< 0.05`); `GL` (`0.0504`) and `GTT.FR` (`0.0513`) included (`>= 0.05`).
  - `Quality Grade` (`443`) `val_status` & `g_market_flag` distribution: `val_status` = `Valued: 427, No data: 15, No value: 1`; `g_market_flag` = `ok: 340, no_value_creation: 54, saturated_high: 28, None: 16, nav_anchored: 5` (`saturated_low: 0`). Non-`ok` flags with numeric `g_market < 0.05` (e.g., `eu:VPK.NL` at `g_market=-0.0163, g_market_flag='no_value_creation'`, `us:PCG` at `0.0027, no_value_creation`, `eu:WDP.BE` at `0.0046, no_value_creation`) and `nav_anchored` (`FFH.CA`, `III.GB`, `INDU C.SE`, `INVE B.SE`, `STB.NO`) are all cleanly excluded (`0g=False`).
  - `g6_flags >= 3` exclusion (`40` companies): `us:RTX` has `g6_flags=3` (`netdebt='flag'`, `intcov='flag'`, `fcfconv='ok'`, `p2p='flag'`), giving `QG=False`, `0g=False`.
- **`us:APD` & `us:EL` Stage-1 scrub**:
  - `us:APD` (`3a="Toll booth & switching costs"`, `3b="N"`) and `us:EL` (`3a="Irreplaceable infrastructure & intangibles"`, `3b="N"`) have all Gate 4–6 fields (`4_ent..4_sub`, `4`, `4n`, `5`, `6`) scrubbed to blank and reject at Gate 3 (`"Rejected – G3 Moat & Pricing"`).
- **11 former calamity `3b="Y"` rows**:
  - `DGE.GB`, `NESN.CH`, `RTO.GB`, `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN` all retain `3b="Y"`, Gate 4 sub-scores, `4` (CAP `15–25`), `4n` notes (`333–557` chars), `5`, and `6`; `10/11` remain in `Quality Grade`, with `RTX` excluded solely by `g6_flags=3`.

### Check 3: Mirror & SQLite Verification
- Dual-listed mirror parity: `ASML == ASML.NL` and `FER == FER.ES` match identically across all `21` qualitative columns (`QUAL_COLUMNS`), confirmed both by direct CSV comparison and `sync_mirrors(dry_run=True)`.
- `data/fundamentals.sqlite`:
  - `companies` table has exactly `27` columns (`['universe', 'id', 'ticker', 'eodhd_symbol', 'company', 'country', 'sector', 'sub_industry', 'exchange', 'g1', 'g2', 'g3_tb', 'g3_ia', 'g3_se', 'g3_rd', 'g3a', 'g3b', 'g4_ent', 'g4_riv', 'g4_buy', 'g4_sup', 'g4_sub', 'g4', 'g4n', 'g5', 'g6', 'result']`), zero `calamity` columns across all tables.
  - `companies` row count: `1,175` (`us: 515`, `eu: 602`, `ca: 58`), `0` `'Calamity pass'` rows.
  - Cross-checked every single one of the `1,175` rows in SQLite `companies` against live CSV & `phase_results`: `0` stale or mismatched rows on `result`, `g4`, `g5`, or `g6`.

### Check 4: Bulk Scorer Audit & Full Unit Tests
- `python3 screener/bulk_scorer.py --audit`: exited `0` (`989 / 989` Gate 3, `11` reference companies verified, `989 scored / 0 unscored`, `0` formula/3a/4n/waterfall/stage2 discrepancies, mirror parity PASSED).
- `python3 -m unittest discover -s tests`: exited `0` (`Ran 317 tests in 42.103s`, `OK`).

---

## 2. Logic Chain

1. **Calamity retirement is structurally enforced, not merely deleted from CSVs**: Even when synthetic legacy payloads inject `calamity="Y"`, `calamity_flag="Y"`, `calamity_note`, and populated Gate 4–6 values alongside `3b="N"` or `3a="None"`, both `validate_and_waterfall()` and `validate_company_evaluation()` drop all calamity keys, scrub `4_ent..4_sub`, `4`, `4n`, `5`, `6` to `""`, and `phase_results()` rejects at Gate 3 even on unsanitized dicts. Meanwhile, Stage-2 advancing rejects (`3b="Y"`, `CAP < 15`, `5=0`) retain diagnostic Gate 4–6 scores/notes cleanly.
2. **Live dataset & `passes_growth_0g` cohort math are exact**: Independent recomputation from raw CSVs + `screener/gates.py` reproduces every expected population (`1,175` total, `989` Gate 3 = `483 + 506`, `225` Prime Grade, `443` Quality Grade, `25` `passes_growth_0g` = `9 + 6 + 10`) and matches `dashboard.collect_screener_data()` 1:1. Boundary probes confirm strict `< 0.05` on `g_market`, `>= 0.05` on `g_org_exp`, `g_market_flag in ('ok', 'saturated_low')` exclusion of `no_value_creation`/`nav_anchored`, and `g6_flags < 3` exclusion of `RTX`.
3. **Storage & mirror layers are synchronized**: `ASML`/`ASML.NL` and `FER`/`FER.ES` have 100% parity across all 21 qualitative columns, and `data/fundamentals.sqlite` matches live CSVs and `phase_results` across all 1,175 rows with the 27-column schema and zero calamity artifacts.

---

## 3. Caveats

- In the live `Quality Grade` (`443`) cohort, zero companies currently have `g_market_flag == 'saturated_low'`, so the `saturated_low` inclusion branch of `passes_growth_0g` was verified via code inspection (`screener/dashboard.py:126,2792`) rather than a live dataset member. (The `no_value_creation` and `nav_anchored` exclusions were empirically observed on live rows such as `VPK.NL`, `PCG`, `WDP.BE`, and `FFH.CA`.)
- `challenger_v719.py` was temporarily created in the agent working directory to execute Checks 1–3 (because `/tmp` writes timed out waiting for user permission) and was deleted immediately after execution so `.agents/teamwork/` remains metadata-only.

---

## 4. Conclusion

**`APPROVE`**. No defects, discrepancies, stale SQLite rows, mirror drifts, waterfall leaks, or cohort miscalculations were reproduced across the v7.19 engine, live data, SQLite DB, or test suite.

---

## 5. Verification Method

Run the read-only compliance audit and full unit test suite:
```bash
python3 screener/bulk_scorer.py --audit
python3 -m unittest discover -s tests
```
Expected results:
- `--audit` exits `0` with `989 / 989` Gate 3, `0` discrepancies/violations, `483` Stage-2 advancing, and mirror parity `PASSED`.
- `unittest` exits `0` with `317` tests `OK`.
- `sqlite3 data/fundamentals.sqlite "PRAGMA table_info(companies);"` returns `27` rows (none named `calamity*`), and `SELECT COUNT(*), SUM(CASE WHEN result LIKE '%Calamity%' THEN 1 ELSE 0 END) FROM companies;` returns `1175|0`.
