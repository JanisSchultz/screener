# Handoff Report — v718_eval_b05 (Batch 5: Information Technology — Software, IT Consulting & Internet)

**Handoff Type**: Hard (Task Complete)  
**Agent**: `v718_eval_b05` (`teamwork_worker`, Read-Only Qualitative Gate 5 & Gate 6 Evaluator)  
**Parent**: `d510ad6d-e687-40ee-9300-d03ba5fff497`  
**Timestamp**: `2026-11-17T15:52:30Z`

---

## 1. Observation

1. **Completed Software Peer Benchmarks (`data/{us,eu,ca}/{inputs.csv,financials.csv,fundamentals_panel.csv}`)**:
   - `CA:CSU.CA`: `G4=20, G5=2, G6=Y`, `fcf_conv=3.091`, `nd_yrs=1.38`, `roic_med=12.6%`, `0.0%` SBC/Rev.
   - `EU:DSY.FR`: `G4=20, G5=1, G6=Y`, `fcf_conv=1.121`, `nd_yrs=-1.08`, `intcov=20.9`, `roic_med=14.1%`, `2.8%` FY25 SBC/Rev.
   - `EU:NEM.DE`: `G4=20, G5=1, G6=Y`, `fcf_conv=1.450`, `nd_yrs=0.38`, `intcov=15.83`, `roic_med=29.6%`.
   - `EU:SAP.DE`: `G4=20, G5=1, G6=Y`, `fcf_conv=0.616`, `nd_yrs=-0.67`, `intcov=8.56`, `roic_med=9.1%`, `4.6%` FY25 SBC/Rev.
   - `EU:SGE.GB`: `G4=15, G5=1, G6=Y`, `fcf_conv=1.060`, `nd_yrs=1.82`, `intcov=9.82`, `roic_med=18.0%`, `2.0%` FY25 SBC/Rev.
   - `US:ADSK`: `G4=15, G5=1, G6=Y`, `fcf_conv=1.174`, `nd_yrs=0.11`, `intcov=99.0`, `roic_med=44.2%`, `10.9%` FY25 SBC/Rev (resolved SEC accounting probe with zero restatements).
   - `US:CDNS`: `G4=25, G5=2, G6=Y`, `fcf_conv=0.937`, `nd_yrs=-0.44`, `intcov=17.77`, `roic_med=35.5%`, `8.6%` FY25 SBC/Rev.
   - `US:FICO`: `G4=20, G5=1, G6=N`, `fcf_conv=0.955`, `nd_yrs=4.48`, `intcov=6.92`, `eq=-$3,873.2M` (debt-funded buybacks at 50-70x).
   - `US:PTC`: `G4=15, G5=1, G6=Y`, `fcf_conv=0.882`, `nd_yrs=1.51`, `intcov=12.76`, `roic_med=10.7%`, `9.2%` FY26 SBC/Rev.
   - `US:SNPS`: `G4=25, G5=1, G6=N` (`calamity=Y`), `fcf_conv=0.638`, `lt_debt=$13,462M`, `12.7%` FY25 SBC/Rev.
   - `US:TYL`: `G4=20, G5=1, G6=Y`, `fcf_conv=1.476`, `nd_yrs=-0.44`, `intcov=50.5`, `roic_med=7.0%`, `6.5%` FY25 SBC/Rev (debt paid down to zero post-NIC).
   - `US:FTNT`: `G4=15, G5=2, G6=Y`, `fcf_conv=1.325`, `nd_yrs=-1.40`, `intcov=90.17`, `roic_med=106.8%`, `4.1%` FY25 SBC/Rev, ~16% founder equity.
   - `US:MSFT`: `G4=25, G5=1, G6=Y`, `fcf_conv=0.936`, `nd_yrs=-0.27`, `intcov=50.88`, `roic_med=46.3%`, `3.7%` FY25 SBC/Rev.
   - `US:VRSN`: `G4=25, G5=2, G6=Y`, `fcf_conv=1.032`, `nd_yrs=1.45`, `intcov=14.05`, `eq=-$2,154.2M` (organic FCF buybacks), `4.2%` FY25 SBC/Rev.
   - Additional calibration anchors inspected: `US:ROP` (`G4=20, G5=0`, `$31.1B` GW+Int, `6.1%` 5Y GAAP ROIC), `US:MSCI` (`G4=25, G5=1, G6=N`, `eq=-$2,654.5M`), `EU:HEXA B.SE` (`G4=15, G5=1, G6=N`, serial M&A goodwill bloat, `8.2%` ROIC).

2. **Assigned Batch 5 Companies (`data/us/{inputs.csv,financials.csv,fundamentals_panel.csv,prescreen.csv}`)**:
   - All 10 have `g6_default = ""`. `g6_checks` returns `{'netdebt': 'ok', 'intcov': 'ok', 'fcfconv': 'ok', 'p2p': 'ok'}` for 9 companies and flags `fcfconv: 'flag'` on `US:TRMB` (`0.502`).
   - **`US:ADBE`** (`Application Software`, `4=5`): `evidence` documents March 2026 `$150M` FTC/DOJ settlement for deceptive subscription dark patterns and hidden early termination fees (`$75M` penalty + `$75M` relief), aborted `$20B` Figma deal (`$1B` cash breakup fee), and `$20.8B` FY24–25 buybacks; 5Y SBC is `8.2%` rev (`28.9%` NI), shares `-13.1%`. `fcf_conv=1.118`, `p2p_ok=Y` (`$18.63` FY25 OE), `nd_yrs=-0.36`, `intcov=41.1`, `eq=+$11,623M`.
   - **`US:CRM`** (`Application Software`, `4=5`, Reference Company & Example 4): `GW+Int=$64,756M` (`110%` of `$59,142M` equity; `TangEq=-$5,614M`) after Slack/Tableau/MuleSoft and FY25 expansion (`+$9.0B` GW+Int, `+$5.8B` debt); `roic_gaap` stayed `<12%` in all 13 years FY13–FY25 (`roic_med=0.0752`, though `roiic=0.2134` post-activist margin lift to `21.5%` EBIT). 5Y SBC `$15,537M` (`79.9%` of 5Y NI; FY25 `$3,509M` = `47.1%` NI); 5Y shares `-3.9%`. `fcf_conv=1.666` (`$10,893M` FY25 Owner FCF), `p2p_ok=Y` (`$10.91` FY25 OE), `nd_yrs=-0.56` (FY25 yr-end `NetDebt=$9,849M` < `1x` Owner FCF), `intcov=27.52`.
   - **`US:INTU`** (`Application Software`, `4=15, 5=0` preserved): `$141M` 50-state TurboTax dark patterns settlement, `$12B` Mailchimp deal (`GW+Int=$18,623M`), `$2,056M` FY26 SBC (`45.0%` NI). `fcf_conv=1.186` (`$6,561M` FY26 Owner FCF), `p2p_ok=Y` (`$19.08` FY26 OE), `nd_yrs=0.33`, `intcov=19.93`, `eq=+$18,992M`.
   - **`US:PLTR`** (`Application Software`, `4=10`): `evidence` cites permanent ~50% Class F variable-voting control disenfranchising outside public shareholders regardless of insider share sales; 5Y SBC `$3,194.6M` (`24.5%` rev / `227.7%` 5Y NI; FY25 `15.3%` rev / `42.1%` NI), diluted shares `+27.9%` (`2,011.8M -> 2,573.5M`). `fcf_conv=0.908` (`$1,424.3M` FY25 Owner FCF), `p2p_ok=Y`, `cash=$7,177.0M` vs `debt=$229.3M` (`nd_yrs=-10.38`, `intcov=99.0`, `eq=+$7,387.3M`, zero goodwill).
   - **`US:TRMB`** (`Application Software`, `4=10`): `$2.1B` debt-funded Transporeon deal (`>3.5x` leverage) led to `$562M` goodwill impairment; `GW+Int=$6,164M` > `eq=$5,836.2M`; 10 straight years of `<10%` GAAP ROIC (`roic_med=0.0755`, `roiic=0.0438`, `ma_reinvest=1.062`); `$863.4M` FY25 buybacks vs `$39.8M` Owner FCF. `fcf_conv=0.502` (`ocf_ni_2y=0.476`), `cur_oe=$1.77` (`-28%` vs FY21 peak `$2.47`), `nd_yrs=2.69`, `intcov=5.08`.
   - **`US:NOW`** (`Systems Software`, `4=10`): `20.9%` FY25 revenue growth (`$13,278M`), `98%+` renewal, `roic_med=0.1807`, `roiic=0.1834`, `13.7%` FY25 EBIT margin, `TangEq=+$8,265M`; SBC/Rev fell from `19.2%` (FY21) to `14.7%` (FY25, `111.8%` NI) with `$1,840M` FY25 buybacks keeping 4Y share growth to `+2.6%`. `fcf_conv=1.372` (`$2,751M` FY25 Owner FCF), `p2p_ok=Y` (`$1.67` OE), `nd_yrs=-2.68` (`$6,284M` cash vs `$2,403M` debt), `intcov=59.3`.
   - **`US:PANW`** (`Systems Software`, `4=15, 5=0` preserved): `$25B` CyberArk + `$3B` Chronosphere M&A pushed `GW+Int` to `$29,027M` and dropped FY26 GAAP ROIC to `3.5%` (`roiic=0.0314`), `$1,774M` FY26 SBC (`15.5%` rev / `577.9%` NI), shares `+12.9%`. Equity-funded M&A left `$3,071M` cash vs `$2,500M` total debt (`nd_yrs=-1.94`, `intcov=99.0`, `eq=+$27,492M`), `fcf_conv=2.118` (`$2,339M` FY26 Owner FCF, growing annually), `p2p_ok=Y`.
   - **`US:ACN`** (`IT Consulting & Other Services`, `4=5`): `2.8%` FY26 SBC/Rev (`25.1%` NI), `-5.2%` 4Y shares (`638.8M -> 605.3M`), `roic_med=0.3435`, `roiic=0.1438`, `15.4%` FY26 EBIT margin. `fcf_conv=1.058` (`$9,520M` FY26 Owner FCF), `p2p_ok=Y` (`$16.44` FY26 OE), `nd_yrs=-0.51` (`$12,838M` cash vs `$13,397M` total debt), `intcov=44.74`, `eq=+$31,567M`.
   - **`US:IT`** (`IT Consulting & Other Services`, `4=10`): `2.4%` FY25 SBC/Rev (`21.4%` NI), `-14.0%` 4Y shares (`83.8M -> 72.1M`), `roic_med=0.4334`, `ma_reinvest=0.0`; `$1,991.1M` FY25 buyback added `+$718M` debt (`$2.90B -> $3.62B`) as Contract Value slowed `8% -> 1%`, cutting equity `$1,359M -> $319.9M` (`TangEq=-$2,757M`). `fcf_conv=1.170` (`$1,019M` FY25 Owner FCF), `p2p_ok=Y`, `nd_yrs=1.17` (FY25 yr-end `NetDebt=$1,895.6M` = `1.86x` Owner FCF), `intcov=9.15`.
   - **`US:SHOP`** (`Internet Services & Infrastructure (mapped)`, `4=5`): Divested Deliverr logistics in 2023 (Planned Abandonment), lifting FY25 EBIT margin to `12.7%`, GAAP ROIC to `16.1%` (`roiic=0.1583`), `+30.1%` rev growth, SBC halved from `9.8%` (FY22) to `3.9%` (FY25, `36.5%` NI; `+3.8%` 4Y shares). `fcf_conv=0.858` (`126.6%` in FY25 `$1,558M` Owner FCF), `p2p_ok=Y` (`$0.95` FY25 OE), `nd_yrs=-4.51` (`$5,767M` cash vs `$188M` debt), `intcov=99.0`, `eq=+$13,473M`.

---

## 2. Logic Chain

1. **Vector & Pillar Calibration Against Cross-Atlantic Peers**:
   - *Dark patterns / consumer exploitation (`5 = 0`)*: `US:INTU` established the `5 = 0` precedent for deceptive subscription dark patterns (`$141M` settlement). `US:ADBE`'s `$150M` March 2026 FTC/DOJ dark-pattern settlement (explicitly cited in `evidence` as violating customer value-for-money) plus `$1B` Figma breakup fee mirrors `INTU` -> `ADBE` scores `5 = 0`.
   - *Empire M&A, sub-hurdle ROIC & SBC (`5 = 0` vs `5 = 1`)*: `US:ROP`, `US:PANW`, and `US:INTU` establish `5 = 0` for mega-M&A goodwill bloat compressing GAAP ROIC below the `12%` reinvestment hurdle and/or heavy SBC/dilution. On `US:CRM` (Reference Company / Example 4), `$64.76B` GW+Int (`110%` of equity), 13 straight years of `<12%` GAAP ROIC (`7.5%` 5Y median), `$15.54B` 5Y SBC (`79.9%` of 5Y NI), and renewed FY25 M&A (`+$9.0B` GW+Int) despite activist intervention fail Gate 5 (`5 = 0`). `US:TRMB` (`$2.1B` Transporeon -> `$562M` impairment, 10 years `<10%` GAAP ROIC, `4.4%` ROIIC) and `US:PLTR` (~50% Class F voting disenfranchisement + `24.5%` 5Y SBC/Rev + `+27.9%` 4Y dilution) likewise score `5 = 0`. Conversely, `US:NOW` (organic `20.9%` growth, `18.1%` GAAP ROIC, declining SBC/Rev `19.2% -> 14.7%` with buybacks capping 4Y dilution at `+2.6%`), `US:ACN` (`2.8%` SBC/Rev, `34.3%` ROIC, `-5.2%` shares), `US:IT` (`2.4%` SBC/Rev, `43.3%` ROIC, `-14.0%` shares), and `US:SHOP` (Deliverr Planned Abandonment, `3.9%` SBC/Rev, `15.8%` ROIIC) pass Gate 5 at `5 = 1` (none reach `5 = 2` due to SBC/scale/pro-cyclical buyback/prior M&A blemishes compared to `CSU.CA`, `CDNS`, `FTNT`, `VRSN`).
   - *Gate 6 Three Pillars & Buyback Leverage (`Y` vs `N`)*: Nine of the 10 companies achieve `fcf_conv >= 0.85`, `p2p_ok = "Y"`, `g6_netdebt_yrs <= 1.17y` (7 are net cash), `g6_intcov >= 9.15x`, and positive book equity (`6 = "Y"`). Notably, `US:IT` retains `+$319.9M` positive book equity, `1.17y` median net debt (`1.86x` FY25 Owner FCF), and `9.15x` interest coverage, distinguishing it from negative-equity high-leverage rejects `US:FICO` (`-$3.87B` eq, `4.48y` ND/OE) and `US:MSCI` (`-$2.65B` eq, `$4.5B+` LT debt). On `US:PANW`, equity-funded CyberArk M&A is penalized at Gate 5 (`5 = 0`), while its net cash (`-1.94y`), `99x` coverage, and `211.8%` FCF conversion pass Gate 6 (`6 = "Y"`, Anti-Drift Rule #3). Only `US:TRMB` fails Gate 6 (`6 = "N"`) due to `50.2%` 5Y FCF conversion (`9.4%` in FY25), Owner EPS `-28%` below its FY21 peak, and borderline `5.08x` interest coverage.

---

## 3. Caveats

- All evaluations are strictly grounded in local repository datasets (`data/*/inputs.csv`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`) as of `2026-11-15`; no external web sources were consulted.
- `US:CRM`'s `note` currently still contains stale `"CAP = 10"` and `"Downstream gates bypassed per strict waterfall."` text in `data/us/inputs.csv`; per `DISPATCH.md` and read-only constraints, `data/us/inputs.csv` was NOT modified by this agent (prose fix + `REFERENCE_SNAPSHOT` / Example 4 sync occur during M2 ingest / M4).
- On `US:IT`, FY25 year-end `$1.99B` share repurchases pushed tangible equity to `-$2.76B` and thinned book equity to `+$319.9M`; while Gate 6 passes today (`1.17y` median ND/OE, `9.15x` coverage, `117%` FCF conversion), continued debt-funded buybacks into slowing Contract Value (`1%`) would risk crossing into `FICO`/`MSCI` territory in future cycles.

---

## 4. Conclusion

All 10 Batch 5 companies have been evaluated individually and written to `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05/evaluations.json` with zero modifications to any repository file:

| Ticker | Sub-Industry | `is_g5_reject` | Gate 5 (`5`) | Gate 6 (`6`) |
|---|---|---|---:|---:|
| `US:ADBE` | Application Software | `false` | `0` | `Y` |
| `US:CRM` *(Reference / Ex. 4)* | Application Software | `false` | `0` | `Y` |
| `US:INTU` *(G5 Reject)* | Application Software | `true` | `0` *(preserved)* | `Y` |
| `US:PLTR` | Application Software | `false` | `0` | `Y` |
| `US:TRMB` | Application Software | `false` | `0` | `N` |
| `US:NOW` | Systems Software | `false` | `1` | `Y` |
| `US:PANW` *(G5 Reject)* | Systems Software | `true` | `0` *(preserved)* | `Y` |
| `US:ACN` | IT Consulting & Other Services | `false` | `1` | `Y` |
| `US:IT` | IT Consulting & Other Services | `false` | `1` | `Y` |
| `US:SHOP` | Internet Services & Infrastructure (mapped) | `false` | `1` | `Y` |

---

## 5. Verification Method

1. **JSON & Schema Validation** (executed and passed):
   ```bash
   python3 - <<'PY'
   import csv, json
   with open(".agents/teamwork/v718_eval_b05/evaluations.json", encoding="utf-8") as f:
       evals = json.load(f)
   with open("data/us/inputs.csv", newline="", encoding="utf-8") as f:
       inputs = {r["id"]: r for r in csv.DictReader(f)}
   assert len(evals) == 10
   for e in evals:
       row = inputs[e["id"]]
       assert e["universe"] == "us" and e["ticker"] == row["ticker"] and e["sub_industry"] == row["sub_industry"]
       assert e["5"] in (0, 1, 2) and e["6"] in ("Y", "N")
       if e["id"] in ("INTU", "PANW"):
           assert e["is_g5_reject"] is True and e["5"] == 0
       else:
           assert e["is_g5_reject"] is False
   print("ALL ASSERTIONS PASSED")
   PY
   ```
2. **Read-Only Repository Check** (executed and passed):
   `git status --short data/` outputs nothing (zero data mutations).
3. **Files to Inspect**:
   - `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05/evaluations.json`
   - `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05/progress.md`
   - `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b05/handoff.md`
