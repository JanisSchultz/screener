# Handoff Report — Batch 04 Qualitative Evaluation

## 1. Observation
- Evaluated all 65 companies contained in input dossier `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/batches/batch_04.json`.
- The cohort comprises 1 Energy logistics company (`VPK.NL`), 29 Asset Management & Custody Banks (`AMP`, `ARES`, `BAM.CA`, `BEN`, `BLK`, `BNY`, `BX`, `IVZ`, `NTRS`, `STT`, `TROW`, `ABDN.GB`, `AMUN.FR`, `AZM.IT`, `BAER.CH`, `BGN.IT`, `BMED.IT`, `BPT.GB`, `CVC.NL`, `EMG.GB`, `EQT.SE`, `ICG.GB`, `MNG.GB`, `PGHN.CH`, `QLT.GB`, `STJ.GB`, `VONN.CH`, `VZN.CH`, `AXP`, `COF`, `CMBN.CH`), and 34 Diversified / Commercial Banks (`BAC`, `BMO.CA`, `BNS.CA`, `C`, `CM.CA`, `JPM`, `NA.CA`, `PNC`, `RY.CA`, `TD.CA`, `TFC`, `USB`, `WFC`, `A5G.IE`, `ABN.NL`, `ACA.FR`, `BAMI.IT`, `BCP.PT`, `BG.AT`, `BIRG.IE`, `BKT.ES`, `BMPS.IT`, `BNP.FR`, `BPE.IT`, `CABK.ES`, `CBK.DE`, `DANSKE.DK`, `DNB.NO`, `EBS.AT`, `INGA.NL`, `INVP.GB`, `ISP.IT`, `KBC.BE`).
- Target file created: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_04_evaluated.json` (size: ~170 KB).
- Executed validation suite via `validate_company_evaluation` and dry-run ingestion via `screener.bulk_scorer.ingest_evaluations(path, dry_run=True)`:
  ```
  All 65 company structural & waterfall invariant checks PASSED!
  Dry-run ingestion applied: 65, rejected: 0
  Diffs found on 65 companies (as expected for scoring unscored fields).
  Dry-run ingestion PASSED!
  ```
- Regression test suites executed:
  - `python3 -m unittest tests/test_cap_engine.py`: 15 tests, 0 failures (OK).
  - `python3 -m unittest tests/test_bulk_scoring_e2e.py`: 134 tests, 0 failures (OK).

## 2. Logic Chain
1. **Gate 3 Moat Profiling (Step 1 Initial CAP)**:
   - Scored `3_tb`, `3_ia`, `3_se`, `3_rd` on 0/1/2 reflecting specific business models:
     - Toll booth switching costs (`3_tb`=2) for locked alternative capital (BAM.CA, BX, CVC.NL, EQT.SE, PGHN.CH), custody operating system plumbing (BNY, STT, NTRS), closed-loop payments (AXP), and financial advisory platform integration (VZN.CH).
     - Scale economies shared (`3_se`=2) for BlackRock (`BLK`) via iShares sub-5 bps indexing liquidity compounding.
     - Irreplaceable infrastructure (`3_ia`=2) for deep-water port terminal concessions (`VPK.NL`), Canadian statutory banking oligopoly (`RY.CA`, `TD.CA`, `BMO.CA`, `CM.CA`, `NA.CA`), US money-center deposit networks (`JPM`, `BAC`, `WFC`), and European national deposit champions (`CABK.ES`, `DNB.NO`, `ISP.IT`, `KBC.BE`).
     - Derived `3a` aligns deterministically to the max-scoring archetype, or `"None"` when all four scores are 0 (`COF`, `BMPS.IT`).
     - Step 1 Initial CAP was computed deterministically via `compute_initial_cap_from_scores` adhering strictly to formulas (0Y for all 0; 15Y for sum=1; 20Y for sum>=2 or single 2; 25Y for 2+1; 30Y for 2+2 or 2+1+1).
2. **Gate 3 Waterfall Enforcement**:
   - 29 companies fail Gate 3 (`3b == "N"` or `3a == "None"`): active asset managers facing secular indexation and fee compression (`AMP`, `BEN`, `IVZ`, `TROW`, `ABDN.GB`, `AMUN.FR`, `AZM.IT`, `BGN.IT`, `BMED.IT`, `MNG.GB`, `QLT.GB`, `STJ.GB`, `VONN.CH`), commoditized or sub-hurdle lenders (`COF`, `CMBN.CH`, `C`, `TFC`, `ACA.FR`, `BAMI.IT`, `BMPS.IT`, `BNP.FR`, `BPE.IT`, `CBK.DE`, `INVP.GB`), or volatile lumpy managers (`ARES`, `BAER.CH`, `BPT.GB`, `EMG.GB`, `ICG.GB`).
   - For all 29 Gate 3 failures, downstream fields (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`) are cleared to empty strings `""` per specification.
3. **Gate 4 Competitive Forces & Deterministic Final CAP**:
   - For the 36 companies passing Gate 3, scored all 5 Porter forces against macrotrends.
   - Evaluated moderate frictions: rivalry among incumbents (`4_riv`=1), institutional / depositor bargaining leverage (`4_buy`=1), and monetary easing / digital disintermediation substitution (`4_sub`=1).
   - Applied deterministic haircut formula: $c_1=3 \implies h(3)=10\text{Y}$.
   - 9 European banks with Initial CAP 15Y or 20Y received a -10Y haircut, resulting in Final CAP of 5Y (`A5G.IE`, `ABN.NL`, `BCP.PT`, `BG.AT`, `BIRG.IE`, `DANSKE.DK`, `EBS.AT`) or 10Y (`BKT.ES`, `INGA.NL`). Because Final CAP < 15, Gate 4 fails and downstream `5` and `6` were cleared to `""`.
   - 27 companies achieved Final CAP >= 15Y (15Y: 17 companies; 20Y: 10 companies).
   - Mandatory `4n` Runway & Forces notes were populated for all 36 passing companies citing Initial CAP, deductions, force codes, and insulating mechanisms.
4. **Gates 5 and 6 Ingestion Readiness**:
   - All 27 companies with Final CAP >= 15Y have populated Gate 5 (1 or 2) and Gate 6 ('Y' or 'N').
   - 8 companies achieve Quality Pass (`6="Y"`): `VPK.NL`, `BAM.CA`, `BLK`, `BX`, `CVC.NL`, `EQT.SE`, `PGHN.CH`, `VZN.CH`.
   - 19 depository institutions fail Gate 6 (`6="N"`): custody banks (`BNY`, `STT`, `NTRS`), closed-loop card network (`AXP`), and commercial fractional-reserve banks (`BAC`, `BMO.CA`, `BNS.CA`, `CM.CA`, `JPM`, `NA.CA`, `PNC`, `RY.CA`, `TD.CA`, `USB`, `WFC`, `CABK.ES`, `DNB.NO`, `ISP.IT`, `KBC.BE`).

## 3. Caveats
- No companies in Batch 04 exhibited temporary fixable calamities (`calamity == "Y"` was empty across all 65 companies).
- No companies in Batch 04 belong to fast clock-speed tech/semi/pharma/hardware sub-industries.
- Inputs.csv files and repository code were untouched, preserving strict exclusive file ownership.

## 4. Conclusion
Batch 04 qualitative evaluation is 100% complete, fully audited, and mathematically verified against all specifications. The output file `evaluations/completed/batch_04_evaluated.json` contains 65 evaluated company records ready for automated ingestion into `data/{us,eu,ca}/inputs.csv` without errors or warnings.

## 5. Verification Method
1. Verify the JSON output structure and schema:
   ```bash
   python3 -c "
   import json
   with open('evaluations/completed/batch_04_evaluated.json') as f:
       d = json.load(f)
   assert len(d) == 65
   print('Batch 04 JSON contains 65 valid records.')
   "
   ```
2. Run dry-run ingestion test:
   ```bash
   python3 -c "
   from pathlib import Path
   from screener.bulk_scorer import ingest_evaluations
   res = ingest_evaluations(Path('evaluations/completed/batch_04_evaluated.json'), dry_run=True)
   assert res['rejected'] == 0
   assert len(res['errors']) == 0
   print(f'Ingestion verified: {res[\"applied\"]} applied, 0 errors, 0 warnings.')
   "
   ```
3. Run project regression test suites:
   ```bash
   python3 -m unittest tests/test_cap_engine.py
   python3 -m unittest tests/test_bulk_scoring_e2e.py
   ```
