# Handoff Report — `v718_eval_b09` (Batch 9: Consumer Staples, Materials & Energy, US+EU Combined)

## 1. Observation
Inspected read-only local repository files (`data/us/inputs.csv`, `data/eu/inputs.csv`, `data/ca/inputs.csv`, `data/us/financials.csv`, `data/eu/financials.csv`, `data/us/fundamentals_panel.csv`, `data/eu/fundamentals_panel.csv`, `data/us/prescreen.csv`, `data/eu/prescreen.csv`, `screener/gates.py`, and `QUALITATIVE_EVALUATION_SPEC.md`) for all 10 assigned companies and their completed US/EU/CA sub-industry peers:

- **No `g6_default = "N"`**: None of the 10 assigned companies belong to Banks or Regulated Utilities (`prescreen.csv` `g6_default` is blank for all 10).
- **No waterfall-bypass sentences**: None of the 10 `note` fields in `inputs.csv` contain `"Downstream gates bypassed per waterfall."` or variants.
- **Direct company observations**:
  1. `EU:ABI.BE` (Brewers, `4=15`, existing `5=0`): `roic_median=7.1%`, `fcf_conv=157.5%`, `p2p_ok=N` (FY25 Owner EPS `$4.02` < FY19 `$4.68`, `cagr_oe=-2.5%`), `g6_netdebt_yrs=8.63y`, `g6_intcov=3.70x` (`g6_checks` flags `netdebt`, `intcov`, `p2p`; `$61.4B` net debt, `$72.1B` LT debt).
  2. `EU:RBREW.DK` (Brewers, `4=5`): `roic_median=14.2%` (`roic_operating=42.7%`, `roiic=7.5%`), `fcf_conv=96.6%`, `p2p_ok=Y` (Owner EPS grew `DKK 14.71` [2016] -> `DKK 31.84` [2025]), diluted shares `53.29M -> 49.00M` (`-8%`), SBC `DKK 35M` (`0.2%` sales), `g6_netdebt_yrs=3.89y`, `g6_intcov=6.64x` (`0` G6 flags).
  3. `US:CLX` (Household Products, `4=10`): `roic_median=18.8%` (`roic_operating=54.8%`, `roiic=14.7%`), SBC `$48M`, `fcf_conv=123.0%` (FY25 `60.8%`, `$357M` Owner FCF < `$602M` dividends), `p2p_ok=N` (FY25 Owner EPS `$4.81` < FY24 `$6.50` < FY19 `$7.40`), FY25 net debt jumped from `$2,713M` to `$5,377M` (`total_debt=$5,520M`, `g6_netdebt_yrs=7.56y`), equity compressed to `$90M` (tangible equity `-$2,461M`), `g6_intcov=12.78x`.
  4. `US:KDP` (Soft Drinks, `4=10`): `roic_median=6.4%` (`$44.0B` goodwill+intangibles), `roic_operating=19.2%`, `roiic=26.8%`, `p2p_ok=Y` (`+8.84%` OE CAGR), `fcf_conv=90.9%`, `g6_netdebt_yrs=7.27y` (`$15.1B` net debt / `$13.0B` LT debt vs `$2.08B` NI), `g6_intcov=4.84x` (`ebit $3,653M / int $754M`), plus announced `€15.7B ($17.4B)` debt-funded JDE Peet's acquisition.
  5. `US:AVY` (Paper & Plastic Packaging, `4=10`): `roic_median=16.3%` (`roic_operating=35.8%`, `roiic=6.6%`), Owner EPS `$3.56` [2016] -> `$9.20` [2025] (`+18.48%` 5Y CAGR, `p2p_ok=Y`), shares reduced `90.10M -> 77.40M` (`-14%`), SBC `$27.9M`, `fcf_conv=97.0%`, `g6_intcov=8.15x`, but FY25 net debt rose to `$3,530.1M` (`total_debt=$3,732.9M`, `g6_netdebt_yrs=4.96y > 4.0y`), tangible equity `-$857.9M` (`equity=$2,242.1M` vs `$3.10B` goodwill+intangibles).
  6. `EU:CRDA.GB` (Specialty Chemicals, `4=5`): `roic_median=6.6%` (`roic_operating=15.7%`, `roiic=0.0%`), SBC `£5.0M`, `g6_netdebt_yrs=2.83y`, `g6_intcov=8.61x`, but `fcf_conv=67.4%` (<80% flag), Owner EPS declined 4 consecutive years `£2.29` [2021] -> `£1.22` [2023] -> `£1.13` [2024] -> `£0.45` [2025] (75% below 2016-2019 `£1.48-£1.85`), and FY25 dividends `£154.9M` exceeded Owner FCF `£150.6M`.
  7. `EU:DSFIR.NL` (Specialty Chemicals, `4=5`): `€18B` DSM-Firmenich merger left `€15.4B` FY25 goodwill+intangibles (`€18.7B` peak in 2023), `roic_median=2.3%` (`roic_operating=6.9%`, `roiic=0.0%`), `-€1,081M` FY25 net loss, discounted ANH carve-out, fragrance antitrust class-action settlements, `p2p_ok` blank in `financials.csv` (panel Owner EPS fell `€1.19` [2024] -> `-€4.01` [2025]), FY25 Owner FCF fell 45% YoY to `€487.3M` while payouts totaled `€1,899M` (`€718M` div + `€1,181M` buybacks), driving net debt `+48.5%` to `€3,881M` (`g6_netdebt_yrs=6.47y`, `g6_intcov=3.59x`).
  8. `EU:EMSN.CH` (Specialty Chemicals, `4=5`): Blocher family owner-operator, `ma_reinvest=0.0%` (`CHF 48.9M` goodwill), `roic_median=34.3%` (`roic_operating=35.9%`), `28.4%` FY25 EBIT margin, shares flat/declining `23.38M -> 23.16M`, net cash `CHF 570.6M` (`CHF 623.7M` cash vs `CHF 32.5M` total debt, `g6_netdebt_yrs=-1.13y`, `g6_intcov=282.55x`), `p2p_ok=Y` (`CHF 21.22` in FY25), headline `fcf_conv=78.9%` vs `ocf_ni_2y=1.10` and 5Y cumulative `(OCF-CapEx)/NI = 88.9%` (`93.5%`, `96.7%`, `108.7%` Owner FCF conversion in 2023-2025).
  9. `US:IFF` (Specialty Chemicals, `4=10`): `$7.1B` Frutarom + `$26.2B` DuPont N&B mega-mergers expanded shares `3.25x` (`79.1M -> 257.0M`), generated `>$6.0B` cumulative goodwill impairments (`$1.15B` in FY25), collapsed `roic_median` to `2.2%`, forced a `50%` dividend cut (`$826M -> $409M`), and left `p2p_ok=N` (FY25 Owner EPS `-$0.02`), `fcf_conv` blank in `financials.csv` (panel FY25 Owner FCF `$168M` < `$409M` dividend), `g6_netdebt_yrs=99.0` (`$6,061M` net debt on `-$374M` NI), and `g6_intcov=2.51x`.
  10. `US:TPL` (Oil & Gas E&P, `4=10`): Debt-free cash fortress (`lt_debt=$0.0M`, `cash=$144.8M`, `g6_netdebt_yrs=-0.81y`, `g6_intcov=99.0x`), `p2p_ok=Y` (FY25 all-time peak Owner EPS `$6.97`), `fcf_conv=96.6%` (`ocf_ni_2y=1.11`, FY25 Owner FCF `$468.2M` / `$481.4M` NI = `97.3%`), `roiic=27.0%`, `45.0%` FY25 GAAP ROIC, consistent share reduction (`71.43M -> 69.03M`), SBC `$15.1M` (`1.9%` sales), alongside inherited 1888 trust economics, post-2021 C-corp governance friction, and `$425M-$514M` water/mineral growth capex.

## 2. Logic Chain
1. **Cross-Atlantic Peer Calibration (Anti-Drift Rule #1 & #3)**:
   - **Brewers**: `CARL B.DK[1,Y]`, `HEIA.NL[1,Y]`, `HEIO.NL[1,Y]` establish `5=1` for competent multi-brand brewing stewardship and `6=Y` when `p2p_ok=Y` and `g6_intcov > 5.0x`. `EU:ABI.BE` preserves `5=0` and scores `6=N` (fails `p2p_ok=N`, `8.63y`, `3.70x`). `EU:RBREW.DK` scores `5=1, 6=Y` (stronger balance sheet at `3.89y` and `6.64x` intcov, `p2p_ok=Y`, `96.6%` FCF conversion, `14.2%` ROIC).
   - **Household Products & Soft Drinks**: Completed peers `CHD[1,Y]`, `CL[1,Y]`, `KO[1,Y]`, `PEP[1,Y]`, `MNST[2,Y]`, `CCEP[1,N]` distinguish operational competence (`5=1`) from leverage ceiling failures (`6=N`, e.g., `CCEP` at `4.87y`). Both `US:CLX` (`5=1, 6=N` — `7.56y` Net Debt/OE, `$90M` equity, `p2p_ok=N`) and `US:KDP` (`5=1, 6=N` — `7.27y` Net Debt/OE, `4.84x` intcov, `€15.7B` JDE Peet's deal) follow this exact boundary.
   - **Packaging & Specialty Chemicals**: `CA:CCL.B.CA[2,Y]` and `EU:FPE3.DE[2,Y]` benchmark family/owner-operator `5=2` compounders, whereas `EU:SY1.DE[1,N]` (`4.63y` Net Debt/OE) and `EU:KRZ.IE[1,N]` (sub-10% ROIC + failed P2P compounding despite low debt) benchmark `6=N`. Accordingly, `US:AVY` scores `5=1, 6=N` (`4.96y` Net Debt/OE, `-$858M` tangible equity), `EU:CRDA.GB` scores `5=1, 6=N` (4-year EPS collapse to `£0.45`, `67.4%` FCF conversion, `6.6%` ROIC), `EU:EMSN.CH` scores `5=2, 6=Y` (Blocher family owner-operator, `34.3%` ROIC, `CHF 571M` net cash, `88.9%` 5Y cumulative `(OCF-CapEx)/NI` matching `KO`/`BEI.DE`), while `US:IFF` (`5=0, 6=N`) and `EU:DSFIR.NL` (`5=0, 6=N`) fail both gates due to value-destructive mega-M&A, impairments/losses, dividend cut (`IFF`), antitrust settlements + pro-cyclical `€1.9B` payout (`DSFIR.NL`), and `<4x` interest coverage.
   - **Energy**: `US:TPL` scores `5=1, 6=Y` (0 G6 flags, debt-free cash fortress, `96.6%` Owner FCF conversion, FY25 peak OE EPS `$6.97`; `5=1` rather than `2` because returns stem from inherited land-grant royalty rights plus post-2021 C-corp governance friction and expanding water/mineral capex).

## 3. Caveats
- All evaluations are strictly grounded in local repository datasets (`inputs.csv`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`) as of `2026-11-15`; no external web sources were queried.
- `EU:EMSN.CH` shows `fcf_conv = 78.9%` in `financials.csv` (1.1pp below 80%), which triggers `g6_checks["fcfconv"] = "flag"`, but inspection of `fundamentals_panel.csv` confirms `88.9%` 5Y cumulative `(OCF - CapEx) / NI`, `ocf_ni_2y = 1.10`, and `93.5%–108.7%` Owner FCF conversion across FY23–FY25 (calibrated identically to `US:KO` at `78.2%` and `EU:BEI.DE` at `67.2%`).
- `US:KDP` is borderline between `5=0` and `5=1` due to the announced `€15.7B` JDE Peet's acquisition; scored `5=1` (consistent with `US:CCEP[1,N]` and `EU:SY1.DE[1,N]`) because historical operations delivered `+8.8%` OE CAGR, `26.8%` ROIIC, and zero dividend cuts/impairments prior to deal close, while failing `6=N` decisively on leverage (`7.27y`, `4.84x` intcov).

## 4. Conclusion
Completed independent read-only Gate 5 & Gate 6 evaluations for all 10 Batch 9 companies in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b09/evaluations.json`:
- `EU:ABI.BE`: `5=0` *(preserved)*, `6=N`
- `EU:RBREW.DK`: `5=1`, `6=Y`
- `US:CLX`: `5=1`, `6=N`
- `US:KDP`: `5=1`, `6=N`
- `US:AVY`: `5=1`, `6=N`
- `EU:CRDA.GB`: `5=1`, `6=N`
- `EU:DSFIR.NL`: `5=0`, `6=N`
- `EU:EMSN.CH`: `5=2`, `6=Y`
- `US:IFF`: `5=0`, `6=N`
- `US:TPL`: `5=1`, `6=Y`

Zero repository files were modified.

## 5. Verification Method
Run from repo root `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener`:
1. Confirm zero repo modifications to `data/*/inputs.csv`:
   `git status --short data/` (expect empty output).
2. Validate `evaluations.json` integrity, schema, `EU:ABI.BE` preservation (`5=0`), and `[Diagnostic G5=...|G6=...]` tags:
   Inspect `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b09/evaluations.json` (10 entries matching `data/us/inputs.csv` and `data/eu/inputs.csv` metadata, `5 in {0,1,2}`, `6 in {"Y","N"}`).
3. Invalidation conditions: Any change to `data/{us,eu}/inputs.csv` or `financials.csv` for these 10 tickers or any change to Gate 5/6 rubric thresholds (`thr_culture=1`, `g6_netdebt_yrs<=4.0`, `g6_intcov>5.0`, `fcf_conv>=0.80`) would require re-evaluating affected rows.
