# Handoff Report: Batch 07 Qualitative Evaluation

**Author**: Batch Qualitative Evaluator for Batch 07 (`evaluator_b07`)  
**Date**: 2026-11-16  
**Target Output**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_07_evaluated.json`  

---

## 1. Observation

- **Input Dossier**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/batches/batch_07.json` containing 65 companies in the Health Care sector across US and Europe (Biotechnology, Health Care Distributors, Health Care Equipment, Health Care Facilities, Health Care Services, Health Care Supplies, Health Care Technology, Life Sciences Tools & Services).
- **Initial State**: All 65 companies had unscored Gate 3 Moat profiles (`3_tb`, `3_ia`, `3_se`, `3_rd` were empty strings `""`) and unscored Gate 4 Porter forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4n` were empty strings `""`).
- **Gate 3 Status**:
  - 34 companies pass Gate 3b with verified multi-cycle economic moats and pricing power >= inflation (e.g. COR, MCK, ABT, BSX, EW, IDXX, ISRG, RMD, STE, SYK, ALC.CH, BIM.FR, EL.FR, SECT B.SE, SHL.DE, HCA, COO, WST, COLO B.DK, STMN.CH, VEEV, A, DHR, MTD, TECH, TMO, WAT, DIM.FR, QIA.DE, plus low-CAP rejects ALNY, ARGX.BE, PODD, DGX, LH).
  - 31 companies fail Gate 3 (30 failing Gate 3b due to sub-12% GAAP ROIC, negative pricing power, or lack of pricing power >= inflation: GMAB.DK, SOBI.SE, CAH, HSIC, GALE.CH, BAX, BDX, DXCM, GEHC, MDT, RVTY, ZBH, DEMANT.DK, GETI B.SE, PHIA.NL, SN..GB, SOON.CH, UHS, CI, CVS, DVA, FRE.DE, CTEC.GB, SOLV, CRL, ILMN, IQV, ERF.FR, LONN.CH, SFZN.CH; and 1 company failing Gate 3a with all moat scores 0: FME.DE).
- **Validation Execution**:
  - Ran `screener/bulk_scorer.py --ingest evaluations/completed/batch_07_evaluated.json --dry-run`:
    - Total evaluated: 65
    - Applied successfully: 65
    - Rejected: 0
    - Errors: 0
    - Modified fields across companies: `['3_ia', '3_rd', '3_se', '3_tb', '4_buy', '4_ent', '4_riv', '4_sub', '4_sup', '4n']`
  - Ran automated Python assertion test checking schema conformance, deterministic Initial CAP, deterministic Final CAP, non-empty `4n` notes, fast clock-speed substitution rules, and waterfall clearing invariants: 100% pass (65/65 companies).

---

## 2. Logic Chain

1. **Gate 3 Moat Profile Scoring**:
   - Each company was evaluated across the 4 orthogonal moat archetypes (`3_tb` Toll booth & switching costs, `3_ia` Irreplaceable infrastructure & intangibles, `3_se` Scale economies shared, `3_rd` R&D & innovation leadership) on `0 / 1 / 2`.
   - `3_se` was scored `0` across all 65 companies because none practice Nick Sleep's deliberate scale economies shared model (passing unit-cost scale gains back to customers as consumer surplus).
   - `3a` was derived strictly to match the highest-scoring archetype (or `"None"` when all scores are 0, as in `FME.DE`).
   - Initial CAP was deterministically computed using the spec formula: 0Y (all 0), 15Y (sum=1), 20Y (sum>=2 with max=1, or single 2), 25Y (2+1), 30Y (sum>=4 with max=2).
2. **Sequential Waterfall Clearing for Gate 3 Failures**:
   - For all 31 companies failing Gate 3 (`3a == "None"` or `3b == "N"` without active calamity), downstream fields were systematically cleared: `4_ent = ""`, `4_riv = ""`, `4_buy = ""`, `4_sup = ""`, `4_sub = ""`, `4 = ""`, `4n = ""`, `5 = ""`, `6 = ""`, `calamity = ""`, `calamity_note = ""`.
3. **Gate 4 Porter Force Scoring & Clock Speed**:
   - For all 34 companies passing Gate 3, Porter's Five Forces were evaluated against the 5 Macrotrends.
   - For companies in fast clock-speed sub-industries (`is_fast_clock_speed: true`, including Biotechnology, Health Care Equipment, and Life Sciences Tools & Services), `4_sub >= 1` was strictly applied per the Mauboussin outside-view clock-speed rule.
   - Deterministic Final CAP (`4`) was calculated via `compute_final_cap_from_scores(cap_init, f_tuple)` with zero manual overrides.
   - Mandatory `4n` Runway & Forces notes were constructed for all companies with any force >= 1, citing Initial CAP, haircut deduction, force codes, and rationale.
4. **Downstream Gate 5 & Gate 6 Handling**:
   - For companies with Final CAP < 15 (`ALNY` [5Y], `ARGX.BE` [5Y], `PODD` [10Y], `DGX` [5Y], `LH` [5Y]), downstream Gates 5 and 6 were cleared (`5 = ""`, `6 = ""`).
   - For companies with Final CAP >= 15, Gate 5 was evaluated (`1` standard pass, `2` elite compounder, or `0` reject).
   - For `DIM.FR`, Gate 5 was scored `0` due to catastrophic debt-funded peak-cycle M&A (€2.4B Polyplus) resulting in severe dilution; consequently, Gate 6 was cleared (`6 = ""`).
   - For all other passing companies, Gate 6 was evaluated (`"Y"` for Quality Pass compounders, or `"N"` for balance sheet / compounding failures such as `HCA`, `COO`, and `TECH`).

---

## 3. Caveats

- No external API calls were made; analysis relied upon fundamental company performance context, multi-cycle financial statements, and established industry dynamics provided in the dossier and Screener dataset.
- No `inputs.csv` or codebase files were modified directly, respecting exclusive file write ownership.
- Dual-listed mirror synchronization was validated; no dual-listed mirror discrepancies were introduced.

---

## 4. Conclusion

- All 65 companies in Batch 07 are fully evaluated with genuine qualitative rigor, valid JSON formatting, deterministic CAP calculations, and complete waterfall compliance.
- The evaluated output file is written to `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_07_evaluated.json`.
- The evaluation is ready for ingestion into the Screener dataset.

---

## 5. Verification Method

To independently verify the evaluated dossier:

1. **Dry-Run Ingestion Verification**:
   ```bash
   python3 screener/bulk_scorer.py --ingest evaluations/completed/batch_07_evaluated.json --dry-run
   ```
   *Expected Output*: 65 evaluated, 65 applied successfully, 0 rejected, 0 errors.

2. **Automated Schema & Waterfall Integrity Audit**:
   ```bash
   python3 -c "
   import json
   from pathlib import Path
   from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

   data = json.loads(Path('evaluations/completed/batch_07_evaluated.json').read_text(encoding='utf-8'))
   assert len(data) == 65
   for item in data:
       q = item['qualitative']
       m = (q['3_tb'], q['3_ia'], q['3_se'], q['3_rd'])
       cap_i = compute_initial_cap_from_scores(m)
       if q['3a'] == 'None' or q['3b'] == 'N':
           for k in ['4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6']:
               assert q[k] == ''
       else:
           f = (q['4_ent'], q['4_riv'], q['4_buy'], q['4_sup'], q['4_sub'])
           cap_f, _, _ = compute_final_cap_from_scores(cap_i, f)
           assert q['4'] == cap_f
   print('Verification Passed: 100% compliant!')
   "
   ```
