# Handoff Report — Batch 03 Qualitative Evaluation

## 1. Observation
- **Input Dossier**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/batches/batch_03.json` containing 65 companies across Consumer Staples (Packaged Foods, Personal Care, Soft Drinks) and Energy (Uranium, Integrated Oil & Gas, Oilfield Services, Cryogenic LNG Engineering, E&P, Refining, Storage & Midstream Pipelines).
- **Initial State**: All 65 companies had unscored Gate 3 moat sub-scores (`3_tb`, `3_ia`, `3_se`, `3_rd`) and Gate 4 force sub-scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`).
- **Target File**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_03_evaluated.json`.
- **Validation Execution**:
  - `python3 screener/bulk_scorer.py --ingest evaluations/completed/batch_03_evaluated.json --dry-run`
    - Result: `Total evaluated: 65, Applied successfully: 65, Rejected: 0, Errors: 0, Warnings: 0`.
  - Python strict audit on Initial CAP, derived `3a`, Gate 3b/calamity rules, Porter forces, Final CAP, and sequential waterfall clearing passed with 0 defects.

## 2. Logic Chain
1. **Moat Sub-Scores & Deterministic Initial CAP**:
   - For all 65 companies, scored `3_tb`, `3_ia`, `3_se`, `3_rd` on `0 / 1 / 2` based on empirical business models:
     - Toll booth & switching costs (`3_tb`): embedded contracts/royalties/switching barriers (e.g. `GTT.FR` scored 2; `AAK.SE`, `KRZ.IE`, `NESN.CH`, `KDP`, `KO`, `BKR`, `HAL`, `SBMO.NL`, `SPM.IT`, `SUBC.NO`, `VK.FR` scored 1).
     - Irreplaceable infrastructure & intangibles (`3_ia`): Lindy brands, global distribution density, unreplicable surface land rights (e.g. `LISP.CH`, `LOTB.BE`, `NESN.CH`, `EL`, `PG`, `BEI.DE`, `OR.FR`, `ULVR.GB`, `KO`, `MNST`, `PEP`, `CCEP`, `TPL` scored 2; `AAK.SE`, `ABF.GB`, `BN.FR`, `CWK.GB`, `KRZ.IE`, `ORK.NO`, `KVUE`, `GALD.CH`, `HLN.GB`, `PUIG.ES`, `KDP`, energy producers/refiners/pipelines scored 1).
     - Scale economies shared (`3_se`): Strictly Nick Sleep model (all 0 in this cohort as none operate the Costco/Sleep consumer surplus reinvestment model).
     - R&D leadership (`3_rd`): Standard staples/energy (all 0).
   - Initial CAP was derived deterministically via `compute_initial_cap_from_scores`:
     - 0Y when all scores are 0 (e.g. `TSN`, `AKRBP.NO`, `VAR.NO`).
     - 15Y when sum = 1 and max = 1 (single moderate moat).
     - 20Y when sum >= 2 and max = 1 (e.g. `AAK.SE`, `KRZ.IE`, `KDP`).
     - 20Y when max = 2 and sum = 2 (e.g. `LISP.CH`, `LOTB.BE`, `EL`, `PG`, `BEI.DE`, `OR.FR`, `ULVR.GB`, `MNST`, `PEP`, `CCEP`, `GTT.FR`, `TPL`).
     - 25Y when max = 2 and sum = 3 (e.g. `NESN.CH`, `KO`).
   - Derived `3a` aligned to the top-scoring moat archetype or "None" when all scores are 0.

2. **Sequential Waterfall Clearing on Failed Gate 3**:
   - 48 companies failed Gate 3 (`3a == "None"` or unwaived `3b == "N"`):
     - Unwaived commodity producers and price-takers across cyclical protein (`TSN`), sugar (`ABF.GB`), industrial cocoa (`BARN.CH`), dairy (`BN.FR`), fresh meat (`CWK.GB`), OTC drugs/retail goods (`ORK.NO`, `KVUE`, `GALD.CH`, `HLN.GB`, `PUIG.ES`), uranium (`CCO.CA`), oil sands and E&P (`CVE.CA`, `CVX`, `IMO.CA`, `SU.CA`, `XOM`, `BP..GB`, `ENI.IT`, `EQNR.NO`, `GALP.PT`, `OMV.AT`, `REP.ES`, `SHELL.GB`, `TTE.FR`, `CNQ.CA`, `OXY`, `TOU.CA`, `AKRBP.NO`, `VAR.NO`), cyclical oilfield services (`BKR`, `HAL`, `SLB`, `SBMO.NL`, `SPM.IT`, `SUBC.NO`, `TEN.IT`, `VK.FR`), refining (`MPC`, `PSX`, `VLO`, `NESTE.FI`), and regulated pipeline transmission utilities (`ENB.CA`, `KMI`, `OKE`, `PPL.CA`, `TRGP`, `TRP.CA`, `WMB`).
     - For all 48, downstream fields were cleared: `4_ent = ""`, `4_riv = ""`, `4_buy = ""`, `4_sup = ""`, `4_sub = ""`, `4 = ""`, `4n = ""`, `5 = ""`, `6 = ""`, `calamity = ""`, `calamity_note = ""`.

3. **Porter's Five Forces & Final CAP for Gate 3 Passing Companies**:
   - 17 companies passed Gate 3:
     - **Fatal-Flaw Rejections (Final CAP = 10Y < 15, REJECT)**:
       - `KDP`: Initial CAP 20Y. Severe single-serve coffee pod substitution (`4_sub=2`) triggered Fatal-Flaw Cap to 10Y. Gates 5 and 6 cleared.
       - `TPL`: Initial CAP 20Y. Macrotrend [4] Energy Transition and finite Permian Tier-1 drilling inventory depletion (`4_sub=2`) triggered Fatal-Flaw Cap to 10Y. Gates 5 and 6 cleared.
     - **Gate 4 Passing (Final CAP >= 15Y)**:
       - `AAK.SE`: Initial CAP 20Y - 5Y haircut (`4_buy=1`, `4_sup=1`) = 15Y. Gate 5 = 2, Gate 6 = N (FCF conversion 36.5% fails 80% hurdle).
       - `KRZ.IE`: Initial CAP 20Y - 5Y haircut (`4_buy=1`, `4_sup=1`) = 15Y. Gate 5 = 1, Gate 6 = N (goodwill from serial M&A dilutes GAAP ROIC to 9.5% and FCF conversion 77.4%).
       - `CCEP`: Initial CAP 20Y - 5Y haircut (`4_buy=1`, `4_sup=1`) = 15Y. Gate 5 = 1, Gate 6 = N (Net debt 4.87x Net Income exceeds 4.0x ceiling).
       - `NESN.CH`: Initial CAP 25Y - 10Y haircut (`4_riv=1`, `4_buy=1`, `4_sup=1`) = 15Y. Calamity Pass (Gate 5=0, Gate 6=N waived under complete 3-part note).
       - `EL`: Initial CAP 20Y - 0Y haircut (all forces 0) = 20Y. Calamity Pass (Gate 3b=N, Gate 5=0, Gate 6=N waived under complete 3-part note).
       - `ULVR.GB`: Initial CAP 20Y - 5Y haircut (`4_riv=1`, `4_buy=1`) = 15Y. Gate 5 = 1, Gate 6 = Y. Quality Pass.
       - `PEP`: Initial CAP 20Y - 5Y haircut (`4_riv=1`, `4_buy=1`) = 15Y. Gate 5 = 1, Gate 6 = Y. Quality Pass.
       - `LOTB.BE`: Initial CAP 20Y - 5Y haircut (`4_buy=1`) = 15Y. Gate 5 = 2, Gate 6 = Y. Quality Pass.
       - `GTT.FR`: Initial CAP 20Y - 5Y haircut (`4_buy=1`, `4_sub=1`) = 15Y. Gate 5 = 1, Gate 6 = Y. Quality Pass.
       - `KO`: Initial CAP 25Y - 5Y haircut (`4_buy=1`) = 20Y. Gate 5 = 1, Gate 6 = Y. Quality Pass.
       - `LISP.CH`: Initial CAP 20Y - 0Y haircut (all forces 0) = 20Y. Gate 5 = 2, Gate 6 = Y. Quality Pass.
       - `PG`: Initial CAP 20Y - 0Y haircut (all forces 0) = 20Y. Gate 5 = 2, Gate 6 = Y. Quality Pass.
       - `BEI.DE`: Initial CAP 20Y - 0Y haircut (all forces 0) = 20Y. Gate 5 = 1, Gate 6 = Y. Quality Pass.
       - `OR.FR`: Initial CAP 20Y - 0Y haircut (all forces 0) = 20Y. Gate 5 = 2, Gate 6 = Y. Quality Pass.
       - `MNST`: Initial CAP 20Y - 0Y haircut (all forces 0) = 20Y. Gate 5 = 2, Gate 6 = Y. Quality Pass.

## 3. Caveats
- Fast clock-speed presumption: None of the companies in Batch 03 operate in fast clock-speed tech/semi/pharma/hardware sub-industries (`is_fast_clock_speed: false`). However, potential substitution threats were rigorously evaluated across single-serve coffee (`KDP`), long-term LNG containment technologies (`GTT.FR`), and Permian hydrocarbon extraction longevity (`TPL`).
- Balance sheet / cash conversion hurdles: Strict compliance with Gate 6 standards was maintained. Companies with strong brands but high leverage or poor cash conversion (`AAK.SE`, `KRZ.IE`, `CCEP`) were rejected honestly at Gate 6 without waiving rules.

## 4. Conclusion
Batch 03 qualitative evaluation is complete, verified, and adheres 100% to `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`.
Summary of results:
- Total companies evaluated: 65
- Gate 3 Rejects: 48
- Gate 4 Rejects: 2 (`KDP`, `TPL` with CAP = 10Y)
- Gate 6 Rejects: 3 (`AAK.SE`, `KRZ.IE`, `CCEP`)
- Calamity Passes: 2 (`NESN.CH`, `EL`)
- Quality Passes: 10 (`LISP.CH`, `LOTB.BE`, `PG`, `BEI.DE`, `OR.FR`, `ULVR.GB`, `KO`, `MNST`, `PEP`, `GTT.FR`)

## 5. Verification Method
- Independent command to verify dry-run ingestion:
  ```bash
  python3 screener/bulk_scorer.py --ingest evaluations/completed/batch_03_evaluated.json --dry-run
  ```
  Expected output: `Total evaluated: 65, Applied successfully: 65, Rejected: 0, Errors: 0, Warnings: 0`.
- Output file path:
  `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_03_evaluated.json`
