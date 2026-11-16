# Handoff Report — Batch 11 Qualitative Evaluation

## 1. Observation
- Evaluated all 65 companies from `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/batches/batch_11.json`.
- Completed payload written to `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_11_evaluated.json`.
- Universe and sector distribution:
  - 65 companies spanning Industrials (Machinery, Marine, Airlines, Ground Transport, Rail, TIC/Consulting, Security, Trading/Distribution) and Information Technology (Application Software).
  - 22 companies fail Gate 3 (`3b == "N"`).
  - 43 companies pass Gate 3 (`3b == "Y"`).
  - 10 companies fail Gate 4 (`CAP < 15`: `SKF B.SE`, `TREL B.SE`, `UBER`, `TRI`, `VSURE.SE`, `RS1.GB`, `ADBE`, `FICO`, `PLTR`, `TRMB`).
  - 1 company fails Gate 5 (`5 == 0`: `INTU`).
  - 3 companies fail Gate 6 (`6 == "N"`: `WRT1V.FI`, `CSX`, `NSC`).
  - 2 companies pass under Calamity Tier (`EFX`, `SNPS`).
  - 27 companies achieve full `Quality pass`.
  - Zero companies left in `"To review (blank gate)"`.

## 2. Logic Chain
1. **Gate 3 Moat Profiles (`3_tb`, `3_ia`, `3_se`, `3_rd`) & Derived `3a`**:
   - Each company was scored 0, 1, or 2 across the four orthogonal archetypes based on its core economic engine, switching costs, physical/regulatory infrastructure, Nick Sleep scale economies shared, and engineering R&D leadership.
   - Primary moat archetype `3a` was derived deterministically from the top-scoring moat archetype (`"None"` if all 0).
   - Step 1 Initial CAP was computed deterministically: 0Y (all 0), 15Y (sum=1), 20Y (sum>=2 or single 2), 25Y (2+1), 30Y (2+2 or 2+1+1).
2. **Sequential Munger Waterfall Clearing**:
   - For all 22 companies failing Gate 3 (`3b == "N"` without calamity), downstream Porter forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`), Final CAP (`4`), Runway note (`4n`), and Gates 5 and 6 were cleared to `""`.
3. **Gate 4 Competitive Forces & Fast Clock-Speed Rule**:
   - For all 43 companies passing Gate 3, Porter's Five Forces were evaluated against the 5 Macrotrends (AI/Automation, Demographics/Labor, Geopolitical Reshoring, Energy Transition, Cost of Capital/Inflation).
   - Fast clock-speed sub-industries (all Application Software companies) adhered strictly to presumptive `4_sub >= 1`.
   - Final CAP was computed 100% deterministically from `CAP_init` and Porter force scores with zero manual overrides:
     - Fatal flaw cap (<=10Y, reject) triggered whenever any force was 2 (`SKF B.SE`, `UBER`, `TRI`, `VSURE.SE`, `RS1.GB`, `ADBE`, `FICO`, `PLTR`, `TRMB`).
     - Tiered moderate haircuts applied: $h(0)=0\text{Y}$, $h(1\text{–}2)=5\text{Y}$, $h(3\text{–}4)=10\text{Y}$, $h(5)=15\text{Y}$.
   - Mandatory `4n` Runway & Forces note was populated for every company with any force >= 1, explicitly citing Initial CAP, haircut deduction, force codes, and rationale.
4. **Gates 5 and 6 Enforcement**:
   - For companies with Final CAP < 15 (10 companies), Gates 5 and 6 were cleared to `""` per waterfall.
   - For companies with Final CAP >= 15 (33 companies), Gate 5 (1 or 2, except 0 for INTU) and Gate 6 ('Y' or 'N') were populated.
   - INTU received Gate 5 score of 0 (predatory pricing, dark patterns, dilutive M&A) and Gate 6 was cleared to `""` per waterfall.
5. **Calamity Tier Preservation**:
   - `EFX` (Equifax) and `SNPS` (Synopsys) were preserved as legitimate Calamity tier passes with raw `6 = "N"`, `calamity = "Y"`, and structured 3-part `calamity_note`. Anchor gates 1, 2, 3a, 4 pass with Final CAP >= 15.

## 3. Caveats
- `INTU` generates a single informational warning during dry-run ingestion (`Company passes Gate 4 (CAP=15Y >= 15) but Gate 6 is blank; required to avoid 'To review'`) because `bulk_scorer.py` evaluates Gate 6 presence prior to Gate 5 waterfall clearing; however, `phase_results` correctly evaluates INTU as `Rejected – G5 Management` with zero blank review status.
- No inputs.csv or code files were modified, respecting exclusive file write ownership.

## 4. Conclusion
- Batch 11 qualitative evaluation is 100% complete, fully compliant with specifications, deterministically validated, and ready for ingestion by the orchestrator.
- Output file: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_11_evaluated.json`.

## 5. Verification Method
To independently verify the evaluated batch payload:
```bash
# 1. Validate compliance audit across all 65 companies
python3 -c "
import json
from screener.gates import phase_results, params
with open('evaluations/completed/batch_11_evaluated.json') as f:
    data = json.load(f)
p = params({})
for c in data:
    r = phase_results(c['qualitative'], p)
    assert 'To review' not in r['result'], f\"{c['id']} in review!\"
print('Verified: 0 companies in review!')
"

# 2. Run bulk_scorer dry-run ingestion
python3 screener/bulk_scorer.py --ingest evaluations/completed/batch_11_evaluated.json --dry-run
```
Both commands exit cleanly with code 0.
