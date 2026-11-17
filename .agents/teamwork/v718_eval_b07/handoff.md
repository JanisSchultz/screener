# Handoff Report — v718_eval_b07 (Batch 7: Health Care, US+EU Combined)

**Handoff Type**: Hard  
**Author**: `v718_eval_b07`  
**Parent Orchestrator**: `d510ad6d-e687-40ee-9300-d03ba5fff497`  
**Deliverable**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b07/evaluations.json`

---

## 1. Observation

1. **Authoritative Spec & Data Sources Read**:
   - `.agents/teamwork/ORIGINAL_REQUEST.md:16–20` (R2 requirements: preserve `5=0` on Gate-5 rejects, evaluate Gate 5 & Gate 6 across US+EU combined by GICS Sector/Sub-Industry against completed peers, do not alter Gate 1–4 scores).
   - `.agents/teamwork/v718_survey_spec_miner/spec_report.md:11–89` (Gate 5 5-vector rubric, Gate 6 Three Pillars + disqualifying flags, Anti-Drift Rules #1–#3).
   - `.agents/teamwork/v718_survey_explorer_data/analysis.md:124–136, 292–309` (Health Care roster of 8 incomplete companies and 34 completed Health Care peers).
   - Local repository CSVs inspected read-only: `data/{us,eu}/inputs.csv`, `data/{us,eu}/financials.csv`, `data/{us,eu}/fundamentals_panel.csv`, `data/{us,eu}/prescreen.csv`.

2. **Observed Local Metrics for the 8 Batch 7 Companies** (verbatim from `inputs.csv`, `financials.csv`, `fundamentals_panel.csv`):
   - **`EU:ARGX.BE`** (`Biotechnology (mapped)`, `4=5`, `5=""`, `6=""`):
     - `financials.csv`: `sales_ttm_m=4153.482`, `ni_ttm_m=1344.711`, `ebit_ttm_m=1031.079`, `interest_m=4.248`, `cash_m=4440.568`, `lt_debt_m=47.16`, `roic_median=-0.524`, `fcf_conv=-3.050`, `ocf_ni_2y=0.3672`, `p2p_ok=Y`, `g6_netdebt_yrs=-3.27`, `g6_intcov=-8.79`.
     - `fundamentals_panel.csv`: Continuous EBIT/NI losses FY11–FY23 (`EBIT -$425.0M` FY23, `-$21.7M` FY24 with `$833.0M` non-cash tax-aided NI), first operating profit in FY25 (`$1,031.1M` EBIT, `$1,344.7M` NI, `$882.4M` OCF, `$6.4M` CapEx, `$248.1M` SBC, `$619.3M` Owner FCF = `46.1%` of NI). 3Y (FY23–FY25) cumulative Owner FCF `-$416.5M` on `+$1,882.7M` NI; 5Y (FY21–FY25) Owner FCF `-$2,332.7M` on `+$764.8M` NI. Diluted shares grew `20.28M` (FY16) → `66.21M` (FY25).
   - **`US:ALNY`** (`Biotechnology (mapped)`, `4=10`, `5=""`, `6=""`):
     - `financials.csv`: `sales_ttm_m=3713.937`, `ni_ttm_m=313.747`, `ebit_ttm_m=501.578`, `interest_m=252.627`, `cash_m=2908.484`, `lt_debt_m=1007.784`, `roic_median=-1.0`, `fcf_conv=""`, `p2p_ok=Y`, `g6_netdebt_yrs=0.0`, `g6_intcov=-1.25`.
     - `fundamentals_panel.csv`: 23 consecutive GAAP loss years FY02–FY24 (`-$852.8M` FY21, `-$1,131.2M` FY22, `-$440.2M` FY23, `-$278.2M` FY24); 5Y (FY21–FY25) cumulative NI `-$2,388.6M`, OCF `-$563.0M`, SBC `$1,238.4M`, Owner FCF `-$2,037.4M`. First profitable year FY25: NI `$313.7M`, OCF `$524.1M`, CapEx `$58.7M`, SBC `$348.2M`, Owner FCF `$120.2M` (`38.3%` of NI). FY25 EBIT/interest = `501.578 / 252.627 = 1.99x`. Diluted shares `85.84M` (FY16) → `136.28M` (FY25).
   - **`US:INCY`** (`Biotechnology`, `4=5`, `5=""`, `6=""`):
     - `financials.csv`: `sales_ttm_m=5141.242`, `ni_ttm_m=1286.65`, `ebit_ttm_m=1342.79`, `interest_m=2.428`, `cash_m=3580.604`, `lt_debt_m=40.412`, `roic_median=0.342`, `roic_operating=0.431`, `fcf_conv=0.7981`, `ocf_ni_2y=1.3256`, `p2p_ok=Y` (`peak_oe_eps=6.4516` in FY25), `g6_netdebt_yrs=-6.05`, `g6_intcov=256.9`.
     - `fundamentals_panel.csv`: 10Y (FY16–FY25) Owner FCF/NI = `82.8%` (`$2,699.0M / $3,257.9M`), 8Y (FY18–FY25) = `81.5%`, 5Y (FY21–FY25) = `79.8%` (Reported FCF/NI `110.0%`), FY25 Owner FCF `$1,105.3M` / `$1,286.7M` NI = `85.9%` (`$58.9M` CapEx = `1.1%` of sales). Cash-funded `$2,004.8M` buyback in FY24 cut shares from `226.1M` (FY23) to `204.8M` (FY25).
   - **`US:PODD`** (`Health Care Equipment`, `4=10`, `5=""`, `6=""`):
     - `financials.csv`: `sales_ttm_m=2708.1`, `ni_ttm_m=247.1`, `ebit_ttm_m=473.8`, `interest_m=79.7`, `cash_m=716.1`, `lt_debt_m=930.8`, `roic_median=0.1577`, `fcf_conv=0.6449`, `ocf_ni_2y=1.5023`, `p2p_ok=Y`, `ma_reinvest=0.0495`, `g6_netdebt_yrs=1.05`, `g6_intcov=6.08`.
     - `fundamentals_panel.csv`: CapEx/revenue declined from `28.8%` (FY18), `23.2%` (FY19), `18.4%` (FY20), `11.2–12.1%` (FY21–22) to `4.5%` (FY23), `6.0%` (FY24), `7.1%` (FY25). Post-Omnipod-5 launch 3Y (FY23–FY25) sum Owner FCF `$721.0M` / sum NI `$871.7M` = `82.7%` (Reported FCF/NI = `86.4%`); FY25 Owner FCF `$416.2M` / `$247.1M` NI = `168.4%`. Total debt cut from `$1,422.0M` (FY24) to `$1,050.8M` (FY25; net borrowings `-$708.1M`).
   - **`US:DGX`** (`Health Care Services`, `4=5`, `5=""`, `6=""`):
     - `financials.csv`: `sales_ttm_m=11035.0`, `ni_ttm_m=988.0`, `ebit_ttm_m=1603.0`, `interest_m=277.0`, `cash_m=420.0`, `lt_debt_m=5167.0`, `roic_median=0.0989`, `fcf_conv=1.0414`, `p2p_ok=Y`, `g6_netdebt_yrs=5.30`, `g6_intcov=5.96`.
     - `fundamentals_panel.csv`: FY25 `total_debt_m=6919.0`, `net_debt_m=6499.0`, `goodwill_m=8945.0`, `intangibles_m=1636.0`, `equity_m=7170.0`. Diluted shares reduced `141.0M` (FY16) → `112.0M` (FY25). FY25 EBIT/interest = `5.79x`; LT Debt/TTM NI = `5.23x`; Total Net Debt/TTM NI = `6.58x`.
   - **`US:LH`** (`Health Care Services`, `4=5`, `5=""`, `6=""`):
     - `financials.csv`: `sales_ttm_m=13951.7`, `ni_ttm_m=876.5`, `ebit_ttm_m=1516.2`, `interest_m=224.1`, `cash_m=532.3`, `lt_debt_m=5084.6`, `roic_median=0.0796`, `fcf_conv=1.1638`, `p2p_ok=Y`, `g6_netdebt_yrs=5.35`, `g6_intcov=5.22`.
     - `fundamentals_panel.csv`: FY25 `total_debt_m=7204.0`, `net_debt_m=6671.7`, `goodwill_m=6789.5`, `intangibles_m=3596.0`, `equity_m=8619.8`. Diluted shares reduced `105.1M` (FY16) → `83.2M` (FY25); Fortrea CRO spun off mid-2023. FY23 EBIT/interest = `3.64x`, FY25 = `6.77x`; LT Debt/TTM NI = `5.80x`; Total Net Debt/TTM NI = `7.61x`.
   - **`EU:DIM.FR`** (`Life Sciences Tools & Services (mapped)`, `4=25`, `5=0`, `6=""`):
     - `financials.csv`: `sales_ttm_m=2967.5`, `ni_ttm_m=265.6`, `ebit_ttm_m=549.0`, `interest_m=152.7`, `cash_m=434.2`, `lt_debt_m=1867.4`, `roic_median=0.0792`, `fcf_conv=1.0911`, `p2p_ok=Y`, `g6_netdebt_yrs=11.11`, `g6_intcov=3.60`.
     - `fundamentals_panel.csv`: FY25 `total_debt_m=2599.3`, `net_debt_m=2173.2`, `equity_m=4090.5`. Owner EPS `€4.49` (FY21) → `€2.73` (FY25, `-39%`). Diluted shares `92.17M` (FY23) → `97.30M` (FY25) following €1.2B Feb 2024 emergency equity raise after €2.4B Polyplus debt-funded deal.
   - **`EU:SRT3.DE`** (`Life Sciences Tools & Services (mapped)`, `4=25`, `5=0`, `6=""`):
     - `financials.csv`: `sales_ttm_m=3538.1`, `ni_ttm_m=154.9`, `ebit_ttm_m=651.4`, `interest_m=198.0`, `cash_m=541.4`, `lt_debt_m=3184.3`, `roic_median=0.0659`, `fcf_conv=1.6543`, `p2p_ok=Y`, `g6_netdebt_yrs=23.20`, `g6_intcov=3.29`.
     - `fundamentals_panel.csv`: FY25 `total_debt_m=4454.3`, `net_debt_m=3912.9`, `equity_m=2706.8`, `goodwill_m=3469.8`, `intangibles_m=1828.2`. Owner EPS `€9.91` (FY22) / `€4.65` (FY21) → `€2.24` (FY25, `-77%`). €1B Q1 2024 emergency equity raise after >4.5x EBITDA leverage post-Polyplus deal.

3. **Validation Command Results**:
   - Python schema & invariant check on `.agents/teamwork/v718_eval_b07/evaluations.json`: `JSON validation PASSED: 8/8 companies valid.`
   - `git status --porcelain -- data/`: exited 0 with empty output (zero data modifications by this worker).

---

## 2. Logic Chain

1. **Biotechnology (`EU:ARGX.BE`, `US:ALNY`, `US:INCY`) vs. `US:VRTX[2,Y]`**:
   - All three demonstrate able R&D/commercial stewardship without Gate-5 red flags (no value-destructive bubble rollups or predatory governance), earning `5 = 1`; none matches `VRTX`'s multi-decade >35% ROIC and multi-product non-dilutive compounding (`5 = 2`).
   - On Gate 6, `US:INCY` passes all three pillars (`p2p_ok = Y` with record `$6.45` Owner EPS, `79.8%` 5Y / `82.8%` 10Y / `85.9%` FY25 Owner FCF conversion, `$3.54B` net cash, `256.9x` interest coverage) — calibrated directly against `VRTX[2,Y]` (`fcf_conv = 0.762`) and keeping Jakafi's 2027/28 patent cliff strictly in Gate 4 (Anti-Drift Rule #3).
   - Conversely, `EU:ARGX.BE` and `US:ALNY` both fail Gate 6 (`6 = "N"`) despite net cash: `ARGX.BE` has only 1 year of positive EBIT (FY25), `-52.4%` 5Y median ROIC, and `-305%` 5Y / `46.1%` FY25 Owner FCF conversion (`< 80%`); `ALNY` had 23 loss years through FY24 (`roic_median = -1.0`), `-$2.04B` 5Y Owner FCF, `38.3%` FY25 Owner FCF conversion (`$348M` SBC > `$314M` NI), and `1.99x` FY25 interest coverage (`g6_intcov = -1.25x`), directly matching `US:ARM[1,N]`, `US:DASH[1,N]`, and `US:GEV[1,N]`.
2. **Health Care Equipment (`US:PODD`) vs. 13 Completed Peers**:
   - `US:PODD` earns `5 = 1` (strong Omnipod 5 execution, `15.8%`→`20.3%` ROIC, `$708M` FY25 debt paydown, minimal M&A, though shorter profit track record than `ISRG`/`IDXX`/`EW`/`SYK`) and `6 = "Y"`: `p2p_ok = Y`, `g6_netdebt_yrs = 1.05y <= 4.0y`, `g6_intcov = 6.08x > 5.0x`, and post-launch 3Y (FY23–FY25) Owner FCF conversion of `82.7%` (`168.4%` in FY25 as CapEx fell to `4.5–7.1%` of sales), matching `ISRG[2,Y]` (`0.568` 5Y during plant build) and `BIM.FR[2,Y]` (`0.739` 5Y) rather than chronic-capex/levered `COO[1,N]` (`0.382` 5Y, `6.3y` net debt, `4.5%` ROIC).
3. **Health Care Services (`US:DGX`, `US:LH`) Duopoly Calibration**:
   - Both `DGX` and `LH` earn `5 = 1` (disciplined cost/portfolio execution including `LH`'s Fortrea spin-off and ~21% share count reduction since FY16, offset by goodwill-heavy hospital outreach M&A).
   - Both fail Gate 6 (`6 = "N"`) on Pillar 3: `g6_netdebt_yrs = 5.30y` (`DGX`) and `5.35y` (`LH`) exceed the `4.0y` ceiling (LT Debt/NI `5.23x`/`5.80x`, Total Net Debt/NI `6.58x`/`7.61x`), with thin `g6_intcov` (`5.96x`/`5.22x`) and sub-10% GAAP ROIC (`9.9%`/`8.0%`) from M&A goodwill — calibrated identically to `US:AJG[1,N]`, `EU:INF.GB[1,N]`, `EU:SY1.DE[1,N]`, and `US:COO[1,N]`.
4. **Life Sciences Tools & Services (`EU:DIM.FR`, `EU:SRT3.DE`)**:
   - Both preserve `5 = 0` (`is_g5_reject: true`) per mandate and both fail Gate 6 (`6 = "N"`) decisively on Pillar 3 (`g6_netdebt_yrs = 11.11y` / `23.20y`, `g6_intcov = 3.60x` / `3.29x < 5.0x`, emergency €1.2B / €1.0B equity raises violating "no kindness of strangers") and Pillar 1 (Owner EPS still 39% / 77% below peak with `7.9%` / `6.6%` 5Y GAAP ROIC).

---

## 3. Caveats

- `US:INCY` sits right at the 5-year `80%` Owner FCF boundary (`fcf_conv = 0.7981`, vs `0.828` 10-year and `0.859` FY2025, `ocf_ni_2y = 1.326`). Consistent with `VRTX[2,Y]` (`0.762`), `JNJ[1,Y]` (`0.773`), and `BIM.FR[2,Y]` (`0.739`), `6 = "Y"` is appropriate.
- `US:PODD` has 5Y `fcf_conv = 0.6449` due to pre-Omnipod-5 launch investment in FY21–FY22 (`inputs.csv` `evidence` predates Gate 6 evaluation and noted the 5Y figure); post-launch FY23–FY25 Owner FCF conversion is `82.7%` (`168.4%` FY25) with `1.05y` net debt and `6.08x` interest coverage, aligning with `ISRG[2,Y]` (`0.568`) and `BIM.FR[2,Y]` (`0.739`).
- Repository modifications observed in `git status` (`COMPANY_EVALUATION_SPEC.md`, `QUALITATIVE_EVALUATION_SPEC.md`, `screener/*`, `tests/*`, `output/*`, `docs/*`) belong to parallel R1/R3/R4 agents; `data/` is completely unmodified.

---

## 4. Conclusion

All 8 Batch 7 Health Care companies have been individually evaluated from local repository datasets, calibrated across US+EU sub-industry peers, and recorded in `.agents/teamwork/v718_eval_b07/evaluations.json`:
- `EU:ARGX.BE`: `5=1`, `6=N`
- `US:ALNY`: `5=1`, `6=N`
- `US:INCY`: `5=1`, `6=Y`
- `US:PODD`: `5=1`, `6=Y`
- `US:DGX`: `5=1`, `6=N`
- `US:LH`: `5=1`, `6=N`
- `EU:DIM.FR`: `5=0` (preserved), `6=N`
- `EU:SRT3.DE`: `5=0` (preserved), `6=N`

---

## 5. Verification Method

1. Inspect `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b07/evaluations.json`.
2. Run read-only validation:
   ```bash
   python3 -c '
   import json
   with open(".agents/teamwork/v718_eval_b07/evaluations.json") as f:
       d = json.load(f)
   assert len(d) == 8
   assert all(x["5"] in (0,1,2) and x["6"] in ("Y","N") for x in d)
   assert [x["5"] for x in d if x["is_g5_reject"]] == [0, 0]
   print("OK:", [(x["universe"], x["id"], x["5"], x["6"]) for x in d])
   '
   ```
3. Confirm `git status --porcelain -- data/` returns empty (read-only compliance).
4. **Invalidation conditions**: Any change to `data/{us,eu}/financials.csv` or `fundamentals_panel.csv` for these 8 IDs, or any downstream ingestion altering `5=0` on `EU:DIM.FR` / `EU:SRT3.DE`.
