# Challenge Report — v718_challenger_2 (Universe Data, Funnel Invariance, Mirror Parity & 121-Row Audit)

**Verdict: `APPROVE`**
**Overall risk assessment: LOW**

All five empirical verification dimensions in `DISPATCH.md` were independently tested against `git show HEAD:data/{us,eu,ca}/inputs.csv`, the working tree CSVs (`inputs.csv`, `prescreen.csv`, `financials.csv`, `fundamentals_panel.csv`), `screener/gates.py`, `screener/dashboard.py`, `screener/bulk_scorer.py`, and `COMPANY_EVALUATION_SPEC.md`. Zero discrepancies, zero waterfall violations, and zero Gate 1–4 or unintended row mutations were found.

---

## Challenge Summary & Stress Test Results

| Verification Axis | Hypothesis Challenged | Empirical Result | Status |
|---|---|---|---|
| **1. Gate 1–4 & Non-Target Row Immutability** | Did any Gate 1–4 score, Stage 1 reject (`690`), completed franchise (`364`), or Gate-5 reject `5="0"` mutate? | Exact `121` rows changed (`66` US: `57` G4 + `9` G5; `55` EU: `51` G4 + `4` G5; `0` CA). Only `['5', '6', 'note']` changed on those `121` rows. `0` changes across all `364` completed and `690` Stage-1 rows (`30` G1 + `156` G2 + `504` G3). `0` changes to `5` on the `13` Gate-5 rejects. `git diff -U0` shows exact `66/66` US, `55/55` EU, `0/0` CA line replacements. | **PASS** |
| **2. Funnel & Prime Grade Invariance** | Did populating `5` & `6` on the `121` Stage-2 rejects alter any `phase_results`, `thr_cap`, or Prime Grade / Calamity count? | `0` `phase_results` differences (`result`, `rejected_at`, `review_at`, `waived`) between `HEAD` and working tree across all `1,175` companies. `thr_cap = 15`, `989` Gate 3 (`445` US, `495` EU, `49` CA), `485` Gate-3 advancing (`483` `3b="Y"` + `EL`, `APD`), `504` Gate-3 rejects, `108` G4 rejects, `13` G5 rejects, `126` G6 rejects, `225` Prime Grade, `13` total / `11` `<3` G6-flag Prime Grade Calamity, `0` `To review`. | **PASS** |
| **3. Note Hygiene & `CRM` Sync** | Did any row retain `"Downstream gates bypassed..."`, misalign `[Diagnostic G5=...|G6=...]`, truncate prior notes, or leave `CRM` at `CAP=10`? | `0` occurrences of `bypassed` / `downstream gates` across all `485` advancing rows. `121/121` have valid `[Diagnostic G5=<0\|1\|2> \| G6=<Y\|N>: <rationale>]` matching columns `5` and `6` 100%. Prefix diff vs `HEAD` note (minus bypass sentence) found only `4` intentional cleanups (`NFLX`, `SBUX`, `ROP` plural/singular `"Downstream Gate(s)... bypassed"` variants, and `CRM` `CAP = 10` -> `CAP = 5Y`). `CRM` matches `REFERENCE_SNAPSHOT["CRM"]` and `COMPANY_EVALUATION_SPEC.md` Example 4 (`4=5`, `5=0`, `6=Y`). | **PASS** |
| **4. Quantitative Cross-Check & Rubric Audit** | Do `g6_default="N"`, negative equity, `G5=2`, `G5=0`, `G6="Y"` exceptions, or cited numbers violate rubric or contradict `financials.csv` / `fundamentals_panel.csv`? | `31/31` `g6_default="N"` rows scored `6="N"`. `4/4` negative-equity rows (`SBUX`, `FDXF`, `IRM`, `CCI`) scored `6="N"`. All `12` `G6="Y"` rows with a sub-threshold single summary metric in `financials.csv` (`APP`, `NFLX`, `NKE`, `GRMN`, `INCY`, `PODD`, `TRI`, `HBAN.CH`, `FGR.FR`, `IP.IT`, `IFCN.CH`, `EMSN.CH`) explicitly reconcile against `fundamentals_panel.csv` / rubric exceptions. Stratified 30-company quantitative check + all `8` `G5=2` + all `10` new `G5=0` verified accurate. | **PASS** |
| **5. Mirror Parity & `--audit`** | Do dual-listed mirrors diverge or does `bulk_scorer.py --audit` fail? | `ASML` vs `ASML.NL` and `FER` vs `FER.ES` have `0` diffs across all `23` `QUAL_COLUMNS`. `python3 screener/bulk_scorer.py --audit` exited `0` (`0` discrepancies, `0` Stage-1 violations, `0` Stage-2 missing/invalid, mirror parity `PASSED`). | **PASS** |

---

## Detailed Findings by Dimension

### 1. Zero Gate 1–4 Mutation & Exact 121-Row Scope
- Universe row counts: `us = 515`, `eu = 602`, `ca = 58`, total `= 1,175`.
- `HEAD` classification: `30` G1 rejects + `156` G2 rejects + `504` G3 rejects (`690` Stage 1 rejects) + `108` G4 rejects (`57` US, `51` EU, `0` CA) + `13` G5 rejects (`9` US, `4` EU, `0` CA) + `364` completed = `1,175`.
- Working tree diff vs `HEAD`:
  - `data/us/inputs.csv`: `66` changed rows (`66` `-` / `66` `+` lines in `git diff -U0`).
  - `data/eu/inputs.csv`: `55` changed rows (`55` `-` / `55` `+` lines in `git diff -U0`).
  - `data/ca/inputs.csv`: `0` changed rows (`0` `-` / `0` `+` lines).
  - Union of changed columns across all `121` changed rows: `['5', '6', 'note']` only.
  - Changed rows in `690` Stage-1 rejects: `0`. Changed rows in `364` completed franchises: `0`.
  - All `13` pre-existing Gate-5 rejects preserved `5 == "0"`.

### 2. Funnel & Prime Grade Invariance
- Independent `phase_results` comparison (`HEAD` vs working tree) across all `1,175` companies returned `0` differences in `(result, rejected_at, review_at, waived)`.
- `thr_cap = 15` across all three universes.
- `gate_results_all` exact counts:
  - `Rejected – G1 Understandability`: `30`
  - `Rejected – G2 Essential Need`: `156`
  - `Rejected – G3 Moat & Pricing`: `504`
  - `Rejected – G4 Runway (<15Y)`: `108`
  - `Rejected – G5 Management`: `13`
  - `Rejected – G6 Cash & Fortress Balance Sheet`: `126`
  - `Quality pass` (Prime Grade): `225`
  - `Calamity pass` (total): `13` (`EL` and `APD` waived on `3b, 5, 6`; `DGE.GB`, `NESN.CH`, `RTO.GB`, `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN` waived on `5`/`6`).
- `collect_screener_data(universe_keys())["summary"]`: `total_companies = 1175`, `quality_pass = 225`, `calamity_pass = 11` (`<3` G6-flag Prime Grade Calamity), `valued = 220`. `To review = 0`.

### 3. Note Hygiene & `CRM` Sync
- Regex check across all `485` Gate-3-advancing rows found `0` remaining occurrences of `bypassed` or `downstream gates`.
- All `121` newly completed rows end with `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`, with `100%` agreement between bracketed tags and columns `5` / `6`.
- Score distribution across the `121` rows: `G5`: `0` (`23`), `1` (`90`), `2` (`8`); `G6`: `N` (`75`), `Y` (`46`).
- `CRM` in `data/us/inputs.csv` (`4=5`, `5=0`, `6=Y`, `note` starting `Fails Gate 4 (CAP = 5Y, REJECT)...`) matches `REFERENCE_SNAPSHOT["CRM"]` in `screener/bulk_scorer.py` (`201–210`) and Example 4 in `COMPANY_EVALUATION_SPEC.md` (`546–587`).

### 4. Quantitative Fact Cross-Checks
- **Automated Pillar/Default Checks (all 121 rows)**:
  - All `31` rows with `prescreen.csv` `g6_default == "N"` (commercial banks and regulated utilities) have `6 == "N"`.
  - All `4` rows with `equity_m <= 0` (`SBUX`, `FDXF`, `IRM`, `CCI`) have `6 == "N"`.
  - All `8` `G5=2` rows (`GRMN`, `ACGL`, `MONC.IT`, `BG.AT`, `BKT.ES`, `SEB A.SE`, `RILBA.DK`, `EMSN.CH`) and all `10` newly scored `G5=0` rows (`MMM`, `ADBE`, `CRM`, `PLTR`, `TRMB`, `IFF`, `PCG`, `DANSKE.DK`, `DSFIR.NL`, `PNN.GB`) align with Gate 5 rubric rules.
- **Spot-Check against `financials.csv` & `fundamentals_panel.csv` (30-company stratified sample)**:
  - `CRM`: `gw+int=$64.76B` (`110%` of `$59.14B` equity, `-$5.61B` tangible), `166.6%` 5Y Owner FCF conversion, `27.5x` intcov, `-0.56y` net debt — verified.
  - `APP`: `fcf_conv=127.3%`, `nd_yrs=1.39y`, `intcov=6.02x`, tangible equity `$2,134.7M - $1,936.7M = $198.0M` — verified.
  - `NFLX`: `gw=0` (`intang=$32.78B` content library), `nd=$5.43B`, `intcov=14.49x`, FY23–25 3Y Owner FCF/NI `22,328.2 / 25,100.8 = 88.95%` (`89.0%`) — verified.
  - `EMSN.CH`: `roic_med=34.3%`, `nd=-570.6M`, `nd_yrs=-1.13y`, `intcov=282.55x`, 5Y `(OCF-CapEx)/NI = 2,194.2 / 2,467.8 = 88.91%` (`88.9%`) — verified.
  - `NKE`, `GRMN`, `FDS`, `WTW`, `ACGL`, `IP.IT`, `IFCN.CH`, `SKF B.SE`, `TREL B.SE`, `VSURE.SE`, `NOD.NO`, `CRDA.GB`, `DSFIR.NL`, `UTG.GB`, `ENG.ES`, `FGR.FR`, `HBAN.CH`, `INCY`, `PODD`, `TRI`: all cited `fcf_conv`, `g6_netdebt_yrs`, `g6_intcov`, `roic_median`, `equity_m`, `goodwill_m + intangibles_m`, and multi-year sums matched `financials.csv` and `fundamentals_panel.csv`.

### 5. Mirror Parity & `--audit`
- `ASML` (`us`) vs `ASML.NL` (`eu`): `0` differences across all `23` `QUAL_COLUMNS`.
- `FER` (`us`) vs `FER.ES` (`eu`): `0` differences across all `23` `QUAL_COLUMNS`.
- `python3 screener/bulk_scorer.py --audit`: exited `0` (`989 / 989` Gate 3, `11` Reference Companies `PASSED`, `0` CAP/3a/4n discrepancies, `0` Stage-1 violations, `0` Stage-2 missing/invalid across `485` moat franchises, `0` Calamity violations, Mirror Parity `PASSED`).

---

## Unchallenged Areas
- `screener/dashboard.py` JS/HTML rendering, `build.py` output artifacts (`output/*.html`, `docs/index.html`), and `tests/` suite execution — outside `v718_challenger_2` scope (covered by `v718_challenger_1` / test suite).
- Manual deep-reading of narrative prose on the remaining ~80 rows outside the 30-company stratified sample + 12 `G6="Y"` exception set + 8 `G5=2` + 10 new `G5=0` + 31 `g6_default="N"` rows (though all `121` rows passed programmatic `G5`/`G6` tag-column parity, note-prefix diff, and rubric boundary checks).
