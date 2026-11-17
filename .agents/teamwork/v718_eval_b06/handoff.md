# Handoff Report — `v718_eval_b06` (Batch 6: Information Technology — Semiconductors & Electronic Instruments, US+EU Combined)

## 1. Observation
Inspected read-only local data across `data/{us,eu}/inputs.csv`, `data/{us,eu}/financials.csv`, `data/{us,eu}/fundamentals_panel.csv`, `data/{us,eu}/prescreen.csv`, and `screener/gates.py` (`g6_checks`) for all 8 assigned companies and 16 completed US+EU sub-industry peers (`HEXA B.SE[1,N]`, `HLMA.GB[2,Y]`, `ADI[1,Y]`, `AVGO[1,Y]`, `TXN[2,N]`, `NVDA[2,N]`, `ARM[1,N]`, `ASML[2,Y]`, `ASML.NL[2,Y]`, `KLAC[2,Y]`, `LRCX[2,Y]`, `AMAT[1,Y]`, `ASM.NL[2,Y]`, `BESI.NL[2,N]`, `MYCR.SE[1,Y]`, `VACN.CH[1,Y]`):

1. **`EU:IFCN.CH` (INFICON, `Electronic Equipment & Instruments (mapped)`, CAP `10Y`)**:
   - `financials.csv`: `roic_median = 0.389`, `roic_operating = 0.398`, `roiic = 0.267`, `ma_reinvest = 0.0`, `p2p_ok = Y` (`cagr_oe_eps = 0.098`, peak `$4.62` FY24), `g6_netdebt_yrs = -0.66`, `g6_intcov = 69.54`, `fcf_conv = 0.776` (`ocf_ni_2y = 1.059`, `lt_debt_m = 0.0`, `cash_m = 131.9`).
   - `fundamentals_panel.csv`: 5Y SBC = `$8.1M` (`1.7%` of `$477.2M` NI), diluted shares `23.9M -> 24.4M` (10Y), GW+Intangibles = `$4.7M` vs `$426.1M` equity (`$421.5M` tangible equity). FY22 `fcf_conversion = 0.329` pulled 5Y cumulative ratio to `0.769`, whereas FY23–FY25 averaged `87.6%` (`0.926`, `0.861`, `0.841`).
2. **`US:KEYS` (Keysight Technologies, `Electronic Equipment & Instruments`, CAP `10Y`)**:
   - `financials.csv`: `roic_median = 0.256`, `roic_operating = 0.485`, `roiic = 0.041`, `ma_reinvest = 0.515`, `buyback_yield = 0.017`, `p2p_ok = Y` (`18.8%` 10Y OE EPS CAGR), `fcf_conv = 1.073`, `g6_netdebt_yrs = 0.06`, `g6_intcov = 9.92`, `lt_debt_m = 2534.0`, `cash_m = 1873.0`.
   - `fundamentals_panel.csv`: 5Y NI `$4,535M`, Owner FCF `$4,864M` (`107.3%`), SBC `$662M` (`14.6%` NI), buybacks `$3,044M` (shares `186M -> 173M` over 5Y). FY25 Total Debt `$2,971M`, Net Debt `$1,098M`, Equity `$5,877M`, GW+Intangibles `$4,720M` (`+$1,157M` tangible equity).
3. **`US:ROP` (Roper Technologies, `Electronic Equipment & Instruments`, CAP `20Y`, `5 = 0` preserved)**:
   - `inputs.csv`: `5 = "0"`, `note` ends with `"Downstream Gate 6 bypassed per waterfall."`.
   - `financials.csv`: `roic_median = 0.061`, `roiic = 0.085`, `ma_reinvest = 1.614`, `fcf_conv = 1.258`, `p2p_ok = Y` (`$21.61` FY25 peak), `g6_netdebt_yrs = 3.3`, `g6_intcov = 7.7`, `lt_debt_m = 8595.8`, `cash_m = 297.4`, `ni_ttm_m = 1536.3`, `owner_add_m = 793.5`.
   - `fundamentals_panel.csv`: FY25 Total Debt `$9,301.0M` (`$705.2M` ST debt > `$297.4M` cash), Net Debt `$9,003.6M` (`5.86x` FY25 GAAP NI; `LT Debt / NI = 5.60x`), `+$2,990M` net borrowings added in FY24–FY25 (`+$1,265M` FY24, `+$1,725M` FY25), GW+Intangibles `$31,105.4M` vs `$19,881.5M` equity (`-$11,223.9M` tangible equity).
4. **`US:TDY` (Teledyne Technologies, `Electronic Equipment & Instruments`, CAP `10Y`)**:
   - `financials.csv`: `roic_median = 0.074`, `roic_operating = 0.223`, `roiic = 0.057`, `ma_reinvest = 0.292`, `fcf_conv = 1.003`, `p2p_ok = Y` (`14.1%` OE EPS CAGR to `$22.75` FY25 peak), `g6_netdebt_yrs = 1.98`, `g6_intcov = 17.08`.
   - `fundamentals_panel.csv`: 5Y SBC `$175.0M` (`4.6%` NI), Total Debt paid down from `$4,127.7M` (FY21) to `$2,642.1M` (FY25, `-$1,575M` net debt repayments FY22–25), FY25 Net Debt `$2,289.7M` (`2.56x` NI), EBIT/Interest `19.3x`, Tangible Equity `-$273.8M` (`$10,513.9M` equity vs `$10,787.7M` GW+Intangibles).
5. **`EU:NOD.NO` (Nordic Semiconductor, `Semiconductors (mapped)`, CAP `5Y`)**:
   - `financials.csv`: `roic_median = 0.043`, `roiic = 0.0`, `fcf_conv = 0.566`, `p2p_ok = Y`, `g6_netdebt_yrs = -12.6`, `g6_intcov = 2.04`.
   - `fundamentals_panel.csv`: NI collapsed from `$122.3M` (FY22) to `-$38.5M` loss (`-$45.8M` EBIT) in FY24 and `$16.4M` NI (`$23.2M` EBIT) in FY25. 5Y Owner FCF `$101.3M` vs `$179.0M` NI (`56.6%`), 5Y SBC `$49.5M` (`27.7%` NI; FY25 SBC `$16.6M` = `101%` of FY25 NI), FY25 cash `$304.8M` vs debt `$149.2M`.
6. **`US:MPWR` (Monolithic Power Systems, `Semiconductors`, CAP `5Y`)**:
   - `financials.csv`: `roic_median = 0.433`, `roiic = 0.224`, `ma_reinvest = 0.012`, `buyback_yield = -0.0068`, `fcf_conv = 0.504`, `p2p_ok = Y` (`29.4%` OE EPS CAGR), `g6_netdebt_yrs = -2.0`, `g6_intcov = 99.0`, `fin_note = "[auto] non-cash earnings spike left out of peak: FY2024"`.
   - `fundamentals_panel.csv`: 5Y SBC `$867.3M` (`24.7%` of 5Y NI; FY25 `$227.5M` = `36.9%` of `$615.9M` NI), 10Y diluted shares `42.4M -> 49.2M` (`+16.0%`). Even excluding FY24 non-cash NI spike (`$1,786.7M` NI vs `$539.4M` EBIT), 4Y (FY21–23, FY25) Owner FCF/NI = `$1,222.9M / $1,723.0M = 0.710` (10Y = `0.558`).
7. **`US:NXPI` (NXP Semiconductors, `Semiconductors`, CAP `10Y`)**:
   - `financials.csv`: `roic_median = 0.168`, `roic_operating = 0.472`, `roiic = 0.456`, `ma_reinvest = 0.051`, `fcf_conv = 0.802`, `p2p_ok = N` (`cagr_oe_eps = -0.0215`), `g6_netdebt_yrs = 3.12`, `g6_intcov = 8.36`.
   - `fundamentals_panel.csv`: Owner EPS fell `$10.75` (FY23) -> `$9.73` (FY24) -> `$8.96` (FY25). Total debt expanded `$7,609M` (FY20) -> `$12,222M` (FY25, `+$1,368M` net borrowings in FY25) while 5Y buybacks (`$8,766M`) + dividends (`$4,446M`) = `$13,212M` exceeded `$9,607M` Owner FCF. FY25 Net Debt `$8,955M` = `4.43x` NI (`LT Debt / NI = 5.43x`), GW+Intangibles `$11,846M` vs Equity `$10,056M` (`-$1,790M` tangible equity).
8. **`US:Q` (Qnity Electronics, `Semiconductor Materials & Equipment`, CAP `10Y`)**:
   - `financials.csv`: `p2p_ok = ""`, `ma_reinvest = ""`, `g6_netdebt_yrs = -0.12`, `g6_intcov = 15.6`, `fcf_conv = 1.273`, `roic_median = 0.062`, `roic_operating = 0.187`.
   - `fundamentals_panel.csv` (FY22–FY25 carve-out): Prior to Nov 2025 spin-off, net debt was `$83M` (FY23) and `$25M` (FY24), distorting 3Y median `g6_netdebt_yrs` to `-0.12`. At Nov 2025 separation, `net_borrowings_m = +$4,100M`, leaving FY25 Total Debt `$4,980M` (`$4,003M` LT), Cash `$915M`, Net Debt `$4,065M` (`5.87x` FY25 `$692M` NI; `LT Debt/NI = 5.78x`; `Net Debt / Owner Earnings = 5.22x`; `Net Debt / Owner FCF = 4.20x`), Equity `$7,095M` vs GW+Intangibles `$8,633M` (`-$1,538M` tangible equity), partial-year FY25 interest `$65M` (~2 months post-spin), and OE EPS `$4.51` (FY22) -> `$3.72` (FY25).

## 2. Logic Chain
- **Gate 5 (`0/1/2`)**:
  - `US:ROP` preserves mandatory `5 = 0` (`is_g5_reject: true`) per Anti-Drift Rule #3 (`6.1%` GAAP ROIC serial PE rollup).
  - None of the remaining 7 meets the `5 = 2` "Outsider" / low-dilution compounder bar (`HLMA.GB[2,Y]`, `NVDA[2,N]`, `TXN[2,N]`, `ASML[2,Y]`, `KLAC[2,Y]`, `LRCX[2,Y]`, `ASM.NL[2,Y]`): `IFCN.CH` has >30% China concentration/semicap exposure; `KEYS` has `4.1%` ROIIC from M&A goodwill; `TDY` has `7.4%` post-FLIR GAAP ROIC; `NOD.NO` had `4.3%` ROIC and `101%` FY25 SBC/NI; `MPWR` has `24.7%` 5Y SBC/NI (`36.9%` FY25) and `+16%` 10Y share dilution (matching `AVGO[1,Y]` at `30.5%` SBC/NI, `+16%` shares); `NXPI` supplemented buybacks/divs with debt and `17.1%` SBC/NI; `Q` is a Nov 2025 spin-off lacking standalone capital-allocation history. All 7 score **`5 = 1`** cleanly without red flags (`0`).
- **Gate 6 (`Y/N`)**:
  - **Pass (`6 = "Y"`)**:
    - `EU:IFCN.CH`: Net cash (`-0.66y`, `$0` LT debt, `69.5x` intcov), `p2p_ok = Y` (`9.8%` OE EPS CAGR), normalized Owner FCF conversion `87.6%` across FY23–25 (`ocf_ni_2y = 1.06x`), calibrated identically to completed `6 = "Y"` peers `EU:ABBN.CH` (`0.768`), `US:WAT` (`0.749`), and `EU:EPI A.SE` (`0.746`).
    - `US:KEYS`: Passes all 4 `g6_checks` (`0.06y`, `9.92x`, `1.073`, `Y`), `+$1.16B` tangible equity.
    - `US:TDY`: Passes all 4 `g6_checks` (`1.98y`, `17.08x`, `1.003`, `Y`), actively retired `-36%` of post-FLIR debt (`$4.13B -> $2.64B`), `2.56x` FY25 ND/NI, `19.3x` FY25 EBIT/interest (stronger than completed `DHR[1,Y]` and `TMO[1,Y]`).
  - **Fail (`6 = "N"`)**:
    - `US:ROP`: Serial debt-funded M&A rollup disqualifying red flag (`+$2.99B` net debt added FY24–25, `$9.30B` total debt vs `$297M` cash `< $705M` ST debt, `5.86x` FY25 ND/NI, `5.60x` LT debt/NI, `-$11.22B` tangible equity), mirroring same-sub-industry peer `EU:HEXA B.SE[1,N]`.
    - `EU:NOD.NO`: Fails Pillar 2 (`fcf_conv = 0.566 < 0.80`), Pillar 3 interest coverage (`2.04x < 5.0x`), and Pillar 1 (`-$38.5M` FY24 loss).
    - `US:MPWR`: Fails Pillar 2 (`5Y fcf_conv = 0.504 < 0.80`; `0.710` even ex-FY24 non-cash NI spike; `10Y = 0.558`) from chronic `25–37%` SBC/NI and working-capital absorption, mirroring net-cash rejects `US:NVDA[2,N]` and `US:ARM[1,N]`.
    - `US:NXPI`: Fails Pillar 1 (`p2p_ok = N`, `-2.15%` OE EPS CAGR) and Pillar 3 (`4.43x` FY25 ND/NI, `5.43x` LT debt/NI, `-$1.79B` tangible equity, `$7.6B -> $12.2B` debt funding payouts > FCF), contrasting with `US:ADI[1,Y]`.
    - `US:Q`: Fails Pillar 3 on actual post-spin FY25 balance sheet (`$4,065M` net debt = `5.87x` NI, `5.78x` LT debt/NI, `5.22x` ND/Owner Earnings, `-$1.54B` tangible equity, partial-year `$65M` interest masking ~4.1–4.6x run-rate coverage) and unproven standalone cycle growth (`$4.51 -> $3.72` OE EPS).

## 3. Caveats
- Read-only evaluation: `data/{us,eu}/inputs.csv` were NOT modified; ingestion of `5`, `6`, stripping `"Downstream Gate 6 bypassed per waterfall."` from `US:ROP`'s `note`, and appending `[Diagnostic G5=... | G6=...: ...]` remains for the M2 ingestion step.
- `US:Q` has only 4 years of carve-out financials (`FY22–FY25`) and partial-year FY25 interest (`$65M` on Nov 2025 `$4.1B` separation debt); run-rate interest coverage (~4.1–4.6x) is inferred from the post-spin debt balance.

## 4. Conclusion
Evaluated all 8 Batch 6 companies individually from local repository files with cross-Atlantic peer calibration across 16 completed peers:
- `EU:IFCN.CH`: `5 = 1`, `6 = "Y"` (`is_g5_reject: false`)
- `US:KEYS`: `5 = 1`, `6 = "Y"` (`is_g5_reject: false`)
- `US:ROP`: `5 = 0` *(preserved)*, `6 = "N"` (`is_g5_reject: true`)
- `US:TDY`: `5 = 1`, `6 = "Y"` (`is_g5_reject: false`)
- `EU:NOD.NO`: `5 = 1`, `6 = "N"` (`is_g5_reject: false`)
- `US:MPWR`: `5 = 1`, `6 = "N"` (`is_g5_reject: false`)
- `US:NXPI`: `5 = 1`, `6 = "N"` (`is_g5_reject: false`)
- `US:Q`: `5 = 1`, `6 = "N"` (`is_g5_reject: false`)

Deliverables written inside `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b06/`:
- `evaluations.json`
- `progress.md`
- `handoff.md`
- `BRIEFING.md`

## 5. Verification Method
Run the following read-only verification command from the repository root to verify `evaluations.json` schema, exact IDs/tickers/sub-industries against `data/{us,eu}/inputs.csv`, preservation of `5 = 0` on `US:ROP`, and zero modifications to `data/*/inputs.csv`:
```bash
python3 - <<'EOF'
import csv, json
with open(".agents/teamwork/v718_eval_b06/evaluations.json", encoding="utf-8") as f:
    evals = json.load(f)
assert len(evals) == 8
inputs = {u: {r["id"]: r for r in csv.DictReader(open(f"data/{u}/inputs.csv", newline="", encoding="utf-8"))} for u in ("us", "eu")}
for item in evals:
    inp = inputs[item["universe"]][item["id"]]
    assert item["ticker"] == inp["ticker"] and item["sub_industry"] == inp["sub_industry"]
    assert item["5"] in (0, 1, 2) and item["6"] in ("Y", "N")
    if inp["5"] == "0":
        assert item["is_g5_reject"] is True and item["5"] == 0
    else:
        assert item["is_g5_reject"] is False and inp["5"] == ""
print("Verified 8/8 Batch 6 evaluations.")
EOF
git status --short data/
```
Invalidation condition: any mismatch in count (`!= 8`), schema keys, `US:ROP` `5 != 0`, or any non-empty diff in `data/`.
