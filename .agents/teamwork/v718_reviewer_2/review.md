# Independent R2 Qualitative Data, Peer Calibration & Note Hygiene Review (v7.18)

## Review Summary

**Verdict**: **APPROVE**

**Overall Risk Assessment**: **LOW**

All 121 incomplete moat franchises (108 Gate-4 rejects at `CAP = 5Y / 10Y` across 57 US, 51 EU, 0 CA + 13 non-calamity Gate-5 rejects at `5 = 0` across 9 US, 4 EU, 0 CA) were evaluated in 10 GICS Sector/Sub-Industry batches combining US and EU peers, faithfully ingested into `data/{us,eu}/inputs.csv`, and verified against `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`, `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, and `ORIGINAL_REQUEST.md`. All Gate 1–4 fields (`1..4n`), all 364 pre-completed moat franchises, all 504 Gate-3 rejects, and all 13 Gate-5 `5 = 0` rejects remain intact, funnel counts are 100% invariant (`225` Prime Grade, `13` Calamity pass / `11` `< 3` G6 flags), `python3 screener/bulk_scorer.py --audit` exits `0` with zero discrepancies, and `python3 -m unittest discover -s tests` passes `319/319` tests.

---

## Findings

No Critical or Major findings. Two Minor non-blocking observations are documented below for watchlist awareness and repo cleanliness.

### [Minor] Finding 1 — Borderline Gate 5/6 Watchlist Monitoring (`US:IT`, `US:NOW`)

- **What**: Two newly scored `6 = "Y"` / `5 = 1` companies sit close to Gate 5 / Gate 6 rubric boundaries:
  - `US:IT` (Gartner, `4=10, 5=1, 6=Y`): FY25 `$1,991.1M` share repurchases (partially debt-assisted, total debt `$2.90B -> $3.62B`) thinned GAAP book equity from `$1,359.2M` to `+$319.9M` and pushed tangible equity to `-$2,757.2M` while Contract Value slowed to `~1%`. It legitimately passes Gate 6 today (`+319.9M` positive book equity, `1.17y` 3Y median net debt / `1.86x` FY25 Owner FCF, `9.15x` interest coverage, `117.0%` 5Y Owner FCF conversion, `p2p_ok=Y`), unlike `US:FICO` (`-$3.87B` book equity, `4.48y`) or `US:MSCI` (`-$2.65B` book equity, `>4.5x`), and the rationale explicitly flags the negative tangible equity for monitoring.
  - `US:NOW` (ServiceNow, `4=10, 5=1, 6=Y`): 5-year cumulative SBC (`$7.98B`) equals `144%` of 5-year GAAP NI (`$5.55B`), comparable to `US:PANW` (`149%`, preserved `5=0`). However, `NOW` is distinguished from `PANW` (`$28B` CyberArk/Chronosphere M&A crushing FY26 GAAP ROIC to `3.5%`) and `PLTR` (`228%` 5Y SBC/NI, `+27.9%` 4Y dilution, Class F voting disenfranchisement) by declining SBC/Rev (`19.2%` FY21 -> `14.7%` FY25), `$1.84B` FY25 buybacks capping 4Y share dilution at `+2.6%`, `18.1%` 5Y GAAP ROIC (`18.3%` ROIIC), and `+$8.27B` tangible equity — calibrated consistently with `US:ADSK` (`5=1, 6=Y`, `76%` 5Y SBC/NI).
- **Where**: `data/us/inputs.csv` (`US:IT`, `US:NOW`).
- **Why**: Worth monitoring on future statement refreshes if `IT` continues debt-funded buybacks into negative book equity or `NOW` SBC fails to compress relative to GAAP NI.
- **Suggestion**: Accept as-is for v7.18; no score change warranted.

### [Minor] Finding 2 — Untracked OneDrive Conflict Copies in `output/`

- **What**: `git status --short` reports two untracked files: `output/screener.html 2.html` and `output/screener.html 3.html`.
- **Where**: `output/` (outside R2 qualitative data scope).
- **Why**: Likely OneDrive sync conflict artifacts rather than R2 ingestion outputs.
- **Suggestion**: Orchestrator can remove those two untracked conflict files before final commit/PR if desired.

---

## Verified Claims

| Claim / Requirement | Verification Method | Result |
|---|---|---|
| **Batching & No US/EU Split**: 10 evaluator batches (`v718_eval_b01`..`b10`) cover all 121 companies without splitting US vs. EU or splitting any GICS sub-industry | Python cross-check across all 10 `evaluations.json` files vs `data/{us,eu}/inputs.csv` | **PASS** — 121 unique `(universe, id)` entries, 0 duplicates, 0 sub-industries split across batches; `b05` (10 US IT software/consulting) explicitly benchmarked against EU/CA peers (`SAP.DE`, `DSY.FR`, `NEM.DE`, `SGE.GB`, `CSU.CA`) |
| **Exact Diff & Gate 1–4 Immutability**: Only the 121 incomplete rows changed, only `{5, 6, note}` columns changed | Programmatic cell-by-cell comparison against `git show HEAD:data/{us,eu,ca}/inputs.csv` | **PASS** — Exactly 121 rows changed (`66` US, `55` EU, `0` CA); exact 1:1 match with pre-change incomplete set; only `{5, 6, note}` modified; all Gate 1–4, `calamity`, `evidence`, and metadata columns 100% unchanged |
| **Batch JSON Parity**: Ingested `5` and `6` values in `inputs.csv` match `v718_eval_b01`..`b10/evaluations.json` 100% | Programmatic comparison of every batch JSON item vs `data/{us,eu}/inputs.csv` | **PASS** — 0 mismatches across 121 entries |
| **13 Gate-5 Rejects Preserved**: All 13 pre-existing `5 = 0` rejects (`BA`, `ADP.FR`, `INTU`, `PANW`, `ROP`, `DIM.FR`, `SRT3.DE`, `ABI.BE`, `CSGP`, `CCI`, `ES`, `SO`, `D`) preserve `5 = "0"` | Diff check against `git show HEAD` | **PASS** — 13/13 preserved at `5 = "0"` |
| **31 `g6_default = "N"` Rows**: All 24 banks (`Diversified`/`Regional Banks`) and 7 utilities (`Electric`/`Gas`/`Multi`/`Water Utilities`) carry explicit `6 = "N"` | Normalized `(sector, sub_industry)` lookup against `data/{us,eu}/prescreen.csv` | **PASS** — 31/31 carry `6 = "N"` |
| **485 Advancing & 504 G3-Reject Invariants**: All 485 Gate-3-advancing companies have valid `5 in {0,1,2}` and `6 in {Y,N}`; all 504 G3 rejects keep `4_*..6` blank | Full scan of `data/{us,eu,ca}/inputs.csv` | **PASS** — 485/485 valid, 504/504 blank |
| **Note Hygiene & `CRM` Fix**: Zero `"Downstream gates bypassed..."` variants in 121 (and all 485 advancing) rows; `[Diagnostic G5=<0\|1\|2> \| G6=<Y\|N>: <rationale>]` on all 121 rows matching `5`/`6`; `CRM` `note` fixed to `CAP = 5Y` (no `CAP = 10`) | Regex audit across all 121 & 485 `note` fields + direct inspection of `US:CRM` | **PASS** — 0 bypass variants, 121/121 valid diagnostic tags matching CSV `5`/`6`, 0 inner brackets, `CRM` `CAP = 5Y` verified |
| **Audit Script**: `python3 screener/bulk_scorer.py --audit` | Direct execution | **PASS** — Exit `0`, `989/989` Gate 3 scored, `0` CAP/3a/4n/Stage-1/Stage-2/Calamity discrepancies, `11 Reference Companies Verified: PASSED`, `Dual-Listed Mirror Parity: PASSED` |
| **Test Suite**: `python3 -m unittest discover -s tests` | Direct execution | **PASS** — Exit `0`, `Ran 319 tests in 27.180s`, `OK` |
| **Funnel Invariance**: Prime Grade (`225`) and Prime Grade Calamity (`13` total / `11` `< 3` flags) unchanged | Direct read-only evaluation via `screener.data.load_universe`, `screener.gates.results`, `screener.gates.g6_checks` | **PASS** — `total=1175`, `qpass=225`, `prime=225`, `calamity=13`, `prime_cal=11`, `g4_rej=108`, `g5_rej=13`, `g6_rej=126`, `g123_rej=690`, `to_review=0` |

---

## Adversarial Stress-Test & Special Rules Audit

Every potential Gate 5/6 rubric failure mode and cross-Atlantic calibration edge case was tested directly against `financials.csv` and `fundamentals_panel.csv`:

1. **Commercial Fractional-Reserve Banks (`b01`: 24 banks vs 18 completed peers)**:
   - All 24 banks (`14` EU Diversified, `8` EU Regional, `2` US Regional) carry `6 = "N"` (`g6_default = "N"`).
   - Gate 5 `5 = 2` (`4/24`: `EU:BG.AT` 16.7% ROE / ~33% CIR / -20% 8Y shares, `EU:BKT.ES` 17.0% ROE / ~37% CIR / 0% dilution, `EU:SEB A.SE` 13.9% ROE / ~36% CIR / clean AML, `EU:RILBA.DK` 20.5% ROE / ~30% CIR / -18.2% shares) aligns cleanly with the `7/18` completed `5 = 2` peers (`JPM`, `RY.CA`, `NA.CA`, `ISP.IT`, `KBC.BE`, `NDA FI.FI`, `SHB A.SE`).
   - `EU:DANSKE.DK` (`5 = 0`) properly penalized for the €200B Estonia AML scandal and $2.0B DOJ/SEC/Danish criminal settlement; `EU:SWED A.SE` (`5 = 1`) properly calibrated alongside `CA:TD.CA` (`5 = 1`); `US:MTB` and `US:RF` (`5 = 1`) match US regional/super-regional peers (`PNC`, `USB`, `BAC`).

2. **Insurers, Exchanges, Brokers & Payments (`b02`: 14 companies)**:
   - **Solvency II > 200% & Look-Through**: `US:ACGL` (`5=2, 6=Y`, sub-85% CR, 31.7x intcov, -1.53y ND), `US:HIG` (`5=1, 6=Y`), `US:TRV` (`5=1, 6=Y`), `US:GL` (`5=1, 6=Y`), `US:AIZ` (`5=1, 6=Y`), `EU:TLX.DE` (`5=1, 6=Y`), `EU:UNI.IT` (`5=1, 6=Y`, 230% SII), and `EU:HBAN.CH` (`5=1, 6=Y`, ~270% SST; `fin_note` 1.85x share count jump and `p2p=N`/`4.13x` intcov explained by Dec 2025 Helvetia-Baloise merger) pass Gate 6; `EU:SLHN.CH` (32x asset/eq, 10.49y ND, 4.06x intcov, 40.7% FCF) and `EU:STB.NO` (~30x asset/eq, 9.66y ND, -4.22x intcov, 8.1% FCF, lacking SII >200% proof) fail Gate 6 (`6 = "N"`).
   - **Fee/Data & Brokers/Payments**: `US:FDS` (`5=1, 6=Y`, 1.69y ND, 12.8x intcov, +$2.0B equity) passes, whereas `US:WTW` (`74.2%` FCF conv, TRANZACT non-cash mark), `EU:TCAP.GB` (`3.84x` intcov `< 5.0x`, `p2p` below 2009 peak), and `US:CPAY` (`4.58y` ND `> 4.0y`, `4.75x` intcov `< 5.0x`, `-$6.92B` tangible equity) fail Gate 6 (`6 = "N"`).

3. **Essential Infrastructure vs. Leveraged Industrial/Service Entities (`b03` & `b04`)**:
   - `EU:FGR.FR` (`4=10, 5=1, 6=Y`): `g6_netdebt_yrs = 7.56y` legitimately passes under the **Essential Infrastructure & Concessions Rule** (`g6_intcov = 5.77x > 5.0x`, `fcf_conv = 210.4%`, `p2p_ok = Y`, ring-fenced APRR/AREA debt), contrasting sharply with `EU:ADP.FR` (`4=20, 5=0, 6=N`), which fails the `> 5.0x` interest coverage floor (`g6_intcov = 2.92x`, FY25 `1.99x`, `20.6y` net debt).
   - `US:MMM` (`5=0, 6=N`): Properly flags `fin_note` non-cash litigation/Solventum marks distorting 5Y `fcf_conv` (129%) while actual FY24–25 cash conversion collapsed (`8.4%` / `36.0%`), `4.17x` intcov, `-$1.72B` tangible equity, and `$20B+` PFAS/earplug liabilities.
   - `EU:ENR.DE` (`5=1, 6=N`): Properly rejects on `-0.98%` median ROIC, `€7.3B` FY20–23 cumulative losses, and `€15B` German federal guarantee rescue (`"kindness of strangers"`) despite `954%` advance-payment FCF distortion.

4. **Apparent `fcf_conv < 0.80` Passing Cases (`6 = "Y"`) Verified Against `fundamentals_panel.csv`**:
   - `US:TRI` (`0.131`): Artifact of FY21 non-cash LSEG disposal spike (`ni=5689`, `own_fcf=-5027`); FY22–25 Owner FCF conversion averaged `90–137%`, `nd=0.75y`, `ic=10.87x`.
   - `US:PODD` (`0.645`): Reflects FY21 Omnipod 5 launch buildout (`-9.52x`); FY23–25 Owner FCF conversion = `82.7%` (`168.4%` FY25), `nd=1.05y`, `ic=6.08x`.
   - `US:NFLX` (`0.658`): Reflects FY21–22 content buildout; FY23–25 Owner FCF conversion = `89.0%` (`82.8%` FY25, `121.8%` FY23), `nd=0.69y`, `ic=14.49x` (negative tangible equity is capitalized content library, `gw=0`, book equity `+$26.6B`).
   - `US:GRMN` (`0.748`): Reflects FY21–22 inventory/capex build; `80.2%` 10Y Owner FCF conversion, `-$1.53y` net cash, `99x` intcov.
   - `EU:IFCN.CH` (`0.776`): Reflects single FY22 inventory/capex spike (`0.329`); FY23–25 averaged `87.6%`, net cash `-0.66y`, `69.5x` intcov.
   - `US:NKE` (`0.772`): `85.8%` 10Y Owner FCF conversion (`92.3%` 5Y GAAP FCF/NI), `-0.36y` net debt, `24.2x` intcov.
   - `EU:EMSN.CH` (`0.789`): `88.9%` 5Y `(OCF-CapEx)/NI` and `108.7%` FY25 Owner FCF conversion, `-1.13y` net cash, `282.6x` intcov.
   - `EU:IP.IT` (`0.796`): `81.0%` 9Y cumulative and `103%` FY24–25 Owner FCF conversion, `1.46y` ND, `10.1x` intcov.
   - `US:INCY` (`0.798`): `82.8%` 10Y Owner FCF conversion (`85.9%` FY25), `-6.05y` net cash, `256.9x` intcov.

5. **Post-Spin / Non-Cash / Negative-Equity Traps Caught (`6 = "N"`)**:
   - `US:Q` (`4=10, 5=1, 6=N`): Evaluator caught that `financials.csv` `g6_netdebt_yrs = -0.12y` was a pre-spin carve-out artifact; actual FY25 post-Nov-2025-spin balance sheet has `$4,065M` net debt (`5.87x` FY25 NI), `-$1,538M` tangible equity, and ~`4.1–4.6x` run-rate interest coverage.
   - `US:SBUX` (`4=10, 5=1, 6=N`): Automatic red flag for leveraged buybacks creating `-$7.67B` stockholders' deficit (`-$9.09B` tangible equity).
   - `US:MPWR` (`4=5, 5=1, 6=N`): Properly rejected at Gate 6 despite `-2.0y` net cash because 5Y (`50.4%`), 10Y (`55.8%`), and ex-FY24 4Y (`71.0%`) Owner FCF conversion fall below `80%` due to chronic SBC deduction (`25–37%` of NI) and working-capital absorption.
   - `US:ROP` (`4=20, 5=0, 6=N`): Serial debt-funded PE software rollup (`$31.1B` GW+intangibles, `-$11.2B` tangible equity, `5.86x` Net Debt/NI, `6.1%` GAAP ROIC).
   - `EU:DIM.FR` & `EU:SRT3.DE` (`4=25, 5=0, 6=N`): Both fail Gate 6 on Polyplus M&A leverage (`11.11y` / `23.20y` ND/OE, `3.60x` / `3.29x` intcov, 2024 emergency equity raises, EPS below peak).
   - `US:WELL` / `US:IRM` / `US:DLR` / `EU:UTG.GB` / `US:CCI` / `US:CSGP` (`b10`): All 6 REITs/RE Services fail Gate 6 cleanly on payout/FCF/leverage/negative equity (`IRM`, `CCI`) or cash burn (`CSGP`).
   - All 7 Utilities (`EIX`, `ES`, `SO`, `ENG.ES`, `D`, `PCG`, `PNN.GB`): `6 = "N"` (`g6_default = "N"`), with `PCG` (Ch.11 bankruptcy, `+325%` dilution) and `PNN.GB` (Brixham contamination, criminal fines, `+65%` emergency rights issue) also scoring `5 = 0`.

6. **Cross-Atlantic Consistency in Luxury, Staples & Materials (`b08`, `b09`)**:
   - `EU:MONC.IT` (`5=2, 6=Y`) aligns cleanly with completed peer `EU:RMS.FR` (`5=2, 6=Y`) vs `EU:MC.FR` / `EU:CFR.CH` (`5=1, 6=Y`).
   - `EU:EMSN.CH` (`5=2, 6=Y`) aligns with `EU:SIKA.CH` / `EU:FPE3.DE` (`5=2, 6=Y`), while M&A-impaired `EU:DSFIR.NL` and `US:IFF` (`5=0, 6=N`) are treated identically across the Atlantic.
   - `US:TPL` (`5=1, 6=Y`) properly tempered at `5=1` (inherited trust + C-corp governance friction) while passing all 3 Gate 6 pillars (`-0.81y` ND, `96.6%` FCF conv, `99x` intcov).

---

## Coverage Gaps

- **Re-running `python3 build.py`** — risk level: **low** — recommendation: **accept risk** (reviewer is strictly read-only on repository files; `v718_worker_r2_ingest` already ran `build.py` after final CSV/spec updates, and direct execution of `screener.gates.results` + `screener.bulk_scorer --audit` + `unittest` confirms exact funnel counts and HTML dashboard tests).

## Unverified Items

- None within R2 qualitative data, peer calibration, and note hygiene scope.
