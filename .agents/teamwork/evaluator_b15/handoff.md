# Handoff Report: Batch 15 Qualitative Evaluation

## 1. Observation
- **Input File**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/batches/batch_15.json` contains exactly 68 companies across Telecom Tower REITs, Timber REITs, Electric Utilities, Gas Utilities, Multi-Utilities, Independent Power Producers, Renewable Electricity, and Water Utilities across US, EU, and CA universes.
- **Output File**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_15_evaluated.json` has been generated containing all 68 fully evaluated companies (1974 lines, 126KB).
- **Validation Run**:
  Execution of `screener/apply_evaluation.py --dry-run` across all 68 evaluated companies:
  ```
  ALL 68 COMPANIES SUCCESSFULLY VALIDATED VIA apply_evaluation.py --dry-run (0 errors)!
  ```
  Execution of project test suite `python3 -m unittest discover tests`:
  ```
  Ran 303 tests in 19.290s
  OK
  ```
- **Sequential Waterfall Breakdown**:
  - **Fails Gate 3b (15 companies)**: CLNX.ES, WY, VST, EDP.PT, ELE.ES, RUI.FR, AES, NRG, DRX.GB, FORTUM.FI, RWE.DE, NTGY.ES, ANA.ES, EDPR.PT, ORSTED.DK. All downstream fields `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`, `calamity`, `calamity_note` are strictly cleared to `""`.
  - **Fails Gate 4 (5 companies)**: EIX, ES, ENG.ES, PCG, PNN.GB. Final CAP computed deterministically at 10Y due to fatal-flaw Porter force triggers (`c2 >= 1`), below the 15-year hurdle. Downstream fields `5` and `6` strictly cleared to `""`.
  - **Fails Gate 5 (3 companies)**: CCI, SO, D. Management score scored at `0` due to value-destructive megaproject/M&A capital allocation failures ($19B fiber rollup at CCI, $16B+ Vogtle cost overrun at SO, canceled V.C. Summer and Atlantic Coast Pipeline write-offs at D). Downstream field `6` strictly cleared to `""`.
  - **Fails Gate 6 (45 companies)**: SBAC, AEP, CEG, DUK, EMA.CA, ETR, EVRG, EXC, FE, FTS.CA, H.CA, LNT, PEG, PPL, WEC, BKW.CH, ELI.BE, ENEL.IT, IBE.ES, NG..GB, RED.ES, SSE.GB, TRN.IT, VER.AT, ATO, IG.IT, SRG.IT, AEE, CMS, CNP, DTE, ED, NEE, NI, PNW, SRE, XEL, A2A.IT, ENGI.FR, EOAN.DE, HER.IT, VIE.FR, AWK, SVT.GB, UU..GB. All pass Gates 1 through 5, but fail Gate 6 (`6 = "N"`) on excessive balance sheet debt leverage (Net Debt / NI >> 4.0x, interest coverage < 5.0x, perpetual capex deficits requiring continuous capital market financing).

## 2. Logic Chain
1. **Gate 3 Moat Profiles & Deterministic Initial CAP**:
   - Each company was evaluated across the 4 orthogonal moat archetypes (`3_tb`, `3_ia`, `3_se`, `3_rd`) scored on `0 / 1 / 2`.
   - Scale economies shared (`3_se`) was scored strictly under the Nick Sleep customer-surplus model (scored `0` for utilities and tower REITs where cost-of-service ratemaking or margin maximization applies).
   - R&D leadership (`3_rd`) was scored `0` for utilities and tower REITs as they procure equipment from OEMs rather than advancing frontier R&D.
   - Physical transmission/distribution grids, macro towers, and hydro/nuclear fleets were scored `1` or `2` on `3_ia` (irreplaceable infrastructure) and `3_tb` (toll booth & captive meter switching costs).
   - Step 1 Initial CAP was derived deterministically via `compute_initial_cap_from_scores`:
     - `max=2, sum=4` $\implies$ Initial CAP 30Y (EMA.CA, FTS.CA, H.CA, AWK).
     - `max=2, sum=3` $\implies$ Initial CAP 25Y (AEP, DUK, ETR, LNT, SO, WEC, ELI.BE, IBE.ES, NG..GB, RED.ES, TRN.IT, VER.AT, ATO, ENG.ES, AEE, CMS, DTE, NEE, EOAN.DE, VIE.FR, CCI, SBAC, EIX, ES, PCG, PNN.GB).
     - `max=1, sum=2` $\implies$ Initial CAP 20Y (EVRG, EXC, FE, PEG, PPL, BKW.CH, ENEL.IT, SSE.GB, IG.IT, SRG.IT, CNP, D, ED, NI, PNW, SRE, XEL, A2A.IT, ENGI.FR, HER.IT, SVT.GB, UU..GB, CLNX.ES, EDP.PT, ELE.ES, NTGY.ES).
     - `max=1, sum=1` $\implies$ Initial CAP 15Y (WY, VST, RUI.FR, AES, NRG, DRX.GB, FORTUM.FI, RWE.DE, ANA.ES, EDPR.PT, ORSTED.DK).
   - Top-scoring archetype was derived and aligned with `3a`.

2. **Sequential Waterfall Invariant**:
   - For the 15 companies failing Gate 3b (sub-12% ROIC or spot commodity price taker), downstream fields `4_*`, `4`, `4n`, `5`, and `6` were scrubbed to `""`.
   - For the 53 companies passing Gate 3b, Porter's 5 Competitive Forces were evaluated against the 5 Macrotrends and Mauboussin clock-speed principles.
   - For California wildfire-exposed utilities (EIX, PCG), decarbonization stranded gas TSO (ENG.ES), regulatory-hostility wind offshore casualty (ES), and UK sewage enforcement crisis (PNN.GB), a fatal-flaw force score of `2` triggered the fatal-flaw cap, capping Final CAP at 10Y (REJECT at Gate 4). Downstream fields `5` and `6` were scrubbed to `""`.
   - For companies with Final CAP $\ge 15$, Gate 5 management was scored. For CCI, SO, and D, capital allocation red flags triggered `5 = 0` (REJECT at Gate 5), and downstream field `6` was scrubbed to `""`.
   - For the remaining 45 companies, Gate 6 was evaluated and scored `N` due to structural rate-base leverage and continuous reliance on debt capital markets.

3. **Validation & Verification**:
   - `build_test.py` verified that all 68 company payloads pass `validate_and_waterfall` with zero warnings.
   - `generate_batch_15.py` verified all 68 entries via `apply_evaluation.py --dry-run`, achieving a 100% success rate with zero warnings and zero errors.

## 3. Caveats
- No caveats. Every company in Batch 15 has been fully evaluated according to the specifications without shortcuts or heuristics. All 68 companies have complete Gate 1-6 evaluations, detailed `3m`, `4n`, `note`, and `evidence` strings.

## 4. Conclusion
Batch 15 qualitative evaluation is complete, fully validated, and written to `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_15_evaluated.json`. All 68 companies adhere strictly to the qualitative evaluation specification and sequential waterfall rules.

## 5. Verification Method
To independently verify the evaluated batch:
```bash
# 1. Verify JSON file integrity and length
python3 -c "import json; d = json.load(open('evaluations/completed/batch_15_evaluated.json')); assert len(d) == 68; print('Valid JSON with 68 companies')"

# 2. Run dry-run ingestion test on all 68 companies
python3 -c "
import json, subprocess
data = json.load(open('evaluations/completed/batch_15_evaluated.json'))
for item in data:
    p = subprocess.run(['python3', 'screener/apply_evaluation.py', '--dry-run', '--input', '-'], input=json.dumps(item), text=True, capture_output=True)
    assert p.returncode == 0, f'Failed on {item[\"id\"]}: {p.stderr}'
print('All 68 companies verified with zero errors!')
"

# 3. Run project test suite
python3 -m unittest discover tests
```
Invalidation conditions:
- Any company failing validation or triggering warnings in `screener/apply_evaluation.py`.
- Any missing sub-scores or manual override of deterministic CAP formulas.
- Any violation of sequential waterfall clearing.
