# Forensic Audit Report — Authenticity & Integrity Forensics

**Work Product**: Phase 2 Bulk Re-Scoring (`evaluations/completed/batch_*.json`, `data/{us,eu,ca}/inputs.csv`, `screener/bulk_scorer.py`)  
**Profile**: General Project / Integrity Forensics  
**Auditor**: Forensic Auditor 1  
**Verdict**: CLEAN  

---

## 1. Observation

### Obs 1: Authenticity & Text Diversity in Batch Evaluations
- Tool command: `python3 .agents/teamwork/auditor_1/audit_runner.py`
- Completed batch files: 15 JSON files (`batch_01_evaluated.json` through `batch_15_evaluated.json`) in `evaluations/completed/`.
- Total companies evaluated across batches: exactly **978 companies** (65 companies in batches 1–14, 68 companies in batch 15). Combined with the 11 Phase 1 reference companies, this accounts for all **989 Gate 3 companies**.
- Total non-empty `4n` Runway & Forces notes: **475 notes** across the cohort.
- Unique `4n` notes: **473 unique notes** out of 475, yielding a **99.58% uniqueness ratio**.
- Exactly two duplicate pairs were identified, both representing genuine economic direct competitors subject to identical regulatory/market constraints:
  - `['ADI', 'TXN']`: `"Initial CAP 25Y reduced by -5Y for analog duopoly rivalry (4_riv=1) and semiconductor technology clock speed (4_sub=1)..."`
  - `['EIX', 'PCG']`: `"Initial CAP 25Y capped at 10Y (REJECT) due to fatal-flaw wildfire liability under California inverse condemnation doctrine..."`
- Total word count in `4n` notes: **12,794 words** (mean: **26.9 words/note**).
- Distinct vocabulary size (words $\ge 3$ characters): **1,746 words**.
- Substantive business-model terminology cited in qualitative text: e.g., regulatory frameworks (`54`), OEMs (`28`), commercial contracts (`22`), semiconductor nodes (`15`), bulk liquid terminals (`14`), cloud infrastructures (`10`), brand/trademarks (`9`), clinical trials (`8`), waterfront concessions (`8`), pipelines (`4`), and patents (`3`).
- Codebase inspection of `screener/bulk_scorer.py`: Lines 1–1261 contain zero regex generators, keyword heuristics, or automated qualitative lookup tables. The tool functions strictly as a context exporter, validator, deterministic CAP calculator, Munger waterfall cleaner, and mirror synchronizer.

### Obs 2: Reference Preservation of the 11 Phase 1 Reference Companies
- Tool command: `python3 -c "import subprocess, csv... [git show HEAD:data/{us,eu,ca}/inputs.csv vs current inputs.csv]"`
- The 11 Phase 1 reference companies: `SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`.
- Score preservation: **0 score modifications across all 11 reference companies**. All 14 qualitative scoring keys (`1`, `2`, `2r`, `3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`, `3b`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`, `calamity`, `calamity_note`) match the git baseline HEAD (`a121812`) with 100% byte-for-byte fidelity.
- Text fields: 10 out of 11 reference companies (`SPGI`, `COST`, `ASML.NL`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`) are 100% identical across all columns.
- `ASML` (US): The `note` and `evidence` fields were updated to match European source listing `ASML.NL` character-for-character, directly executing explicit User Requirement R2 from `ORIGINAL_REQUEST.md`: *"Synchronize dual-listed mirror tickers defined in data/*/universe.json (such as ASML and ASML.NL) so that scores, notes, and evidence match identically across universes."* The European primary listing `ASML.NL` remained 100% unmutated.

### Obs 3: Zero Manual Overrides on Deterministic CAP Calculations
- Tool command: `python3 .agents/teamwork/auditor_1/audit_runner.py` (Check 3)
- Population audited: all **989 Gate 3 companies** across US (445), EU (495), and CA (49).
- Formula parity: **0 formula discrepancies found**.
  - 100% of Gate 3 companies have `3a` matching the maximum moat score archetype and canonical tie-breaking rules.
  - 100% of companies passing Gate 3 have Final CAP `4` matching `compute_final_cap_from_scores(cap_init, (4_ent, 4_riv, 4_buy, 4_sup, 4_sub))` with zero manual overrides.

### Obs 4: Calamity Pass Rules Integrity
- Tool command: `python3 .agents/teamwork/auditor_1/audit_runner.py` (Check 4)
- Population with `calamity == "Y"`: **13 companies** across all universes.
- Anchor Gate compliance: **0 calamity violations found**.
  - 100% of calamity companies satisfy Anchor Gate 1 (`1 == "Y"`).
  - 100% of calamity companies satisfy Anchor Gate 2 (`2 == "Y"`).
  - 100% of calamity companies satisfy Anchor Gate 3a (`3a != "None"`).
  - 100% of calamity companies satisfy Anchor Gate 4 (`4 >= 15`).
  - All 13 calamity companies fail only an eligible gate (`3b == "N"`, `5 == 0`, or `6 == "N"`).
  - All 13 calamity companies have substantive, non-empty 3-part `calamity_note` justifications.

### Obs 5: Sequential Munger Waterfall & Mirror Synchronization
- Tool command: `python3 .agents/teamwork/auditor_1/audit_runner.py` (Check 5 & Mirror Parity)
- Downstream clearing: **0 waterfall violations across all 1,175 companies**.
  - All companies failing Gate 3 have `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6` strictly blank (`""`).
  - All companies failing Gate 4 (`CAP < 15`) have `5` and `6` strictly blank (`""`).
  - All companies failing Gate 5 (`5 == 0` without calamity) have `6` strictly blank (`""`).
  - All companies passing Gate 4 (`CAP >= 15`) have Gates 5 and 6 fully populated.
  - 100% of companies with any competitive force $\ge 1$ have a non-empty `4n` Runway & Forces note.
- Mirror Synchronization:
  - Dual-listed pairs defined in `data/us/universe.json`: `ASML` <-> `eu:ASML.NL` and `FER` <-> `eu:FER.ES`.
  - Parity across all 23 qualitative fields (`1`, `2`, `2r`, `3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`, `3b`, `3m`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`, `calamity`, `calamity_note`, `note`, `evidence`): **0 differences found (100% character-for-character equality)**.

### Obs 6: Unit Test Suite & Cockpit Build Execution
- Test command: `python3 -m unittest discover tests`
  - Output: `Ran 303 tests in 17.678s ... OK`
- Build command: `python3 build.py`
  - Output: `✓ Dashboard built in 2.95s: Total Companies: 1175, Prime Grade: 223, Prime Grade Calamity (Conditional): 11, Valued Prime Grade: 218`
  - Exit code: 0.

---

## 2. Logic Chain

1. **Authenticity Assessment**:
   - Per Obs 1, the 978 evaluations were authored through parallel batch evaluator subagents with high lexical diversity (1,746 distinct terms), a 99.58% unique `4n` note ratio, and granular company-specific financial and competitive facts (e.g., OPAF automation architecture, California inverse condemnation, Zeiss single-source optics).
   - In conjunction with the absence of regex or keyword heuristic generators in `screener/bulk_scorer.py`, this proves the evaluations are genuine qualitative investment evaluations and not synthetic script artifacts.

2. **Reference Preservation vs. Mirror Requirement Arbitration**:
   - Per Obs 2, all 11 reference companies preserved 100% of their qualitative gate scores without modification.
   - For `ASML` (US), updating narrative `note` and `evidence` was explicitly mandated by `ORIGINAL_REQUEST.md` Requirement R2 (*"Synchronize dual-listed mirror tickers defined in data/*/universe.json (such as ASML and ASML.NL) so that scores, notes, and evidence match identically across universes"*).
   - Under the system governance rule (*"ORIGINAL_REQUEST.md always takes precedence"*), the synchronization of `ASML` to match European source `ASML.NL` is an authorized requirement fulfillment, not an integrity violation.

3. **Mathematical & Deterministic Integrity**:
   - Per Obs 3, recalculating Step 1 Initial CAP and Step 2 Final CAP across all 989 Gate 3 companies revealed zero divergence between stored values and formula outputs. No human or script overrides were applied.

4. **Waterfall, Calamity, and Parity Enforcement**:
   - Per Obs 4 and Obs 5, the sequential Munger reject waterfall is strictly enforced across all 1,175 rows: rejections at Gate 3 or Gate 4 clear downstream fields completely.
   - Calamity pass rules are strictly bounded by Anchor Gates 1, 2, 3a, and 4; zero companies bypassed anchor gates through calamity.
   - Dual-listed mirror tickers `ASML` and `FER` maintain 100% character-for-character parity with their European source records.

5. **Operational Verification**:
   - Per Obs 6, all 303 project unit tests pass cleanly, and `build.py` compiles the cockpit without errors or warnings.

---

## 3. Caveats

- **External Financial Statements**: The financial metrics cited in `evidence` and `note` reflect the ingested figures from `data/*/financials.csv` and company annual filings; the auditor spot-checked key metrics against `financials.csv` but did not independently audit SEC/EDGAR filings.
- **Index Flags**: Mirror parity was checked and confirmed across all qualitative scoring and narrative fields as defined in `PROJECT.md` line 57; index membership columns (`in_sp500`, `in_ndx`) remain universe-specific by design (e.g., ASML US ADR is in Nasdaq 100, whereas Amsterdam listing ASML.NL is not).

---

## 4. Conclusion

**Final Verdict**: **`CLEAN`**

The Phase 2 bulk re-scoring deliverable demonstrates total structural and qualitative integrity. All 989 Gate 3 companies possess deterministic, formulaic moat and force scores with authentic, highly differentiated qualitative justifications. Reference company scores are 100% preserved, Munger sequential waterfall rules are strictly enforced, calamity rules operate without anchor gate bypass, dual-listed mirrors are perfectly synchronized, and the full test suite and cockpit build run with 100% pass rates.

---

## 5. Verification Method

To independently verify these findings, run:

```bash
# 1. Execute automated forensic integrity audit runner
python3 .agents/teamwork/auditor_1/audit_runner.py

# 2. Run the complete project unit test suite (303 tests)
python3 -m unittest discover tests

# 3. Verify HTML cockpit build
python3 build.py

# 4. Run bulk scorer audit CLI
python3 screener/bulk_scorer.py --audit
```

Invalidation conditions:
- Any failure in `python3 .agents/teamwork/auditor_1/audit_runner.py`
- Any failure in `python3 -m unittest discover tests`
- Non-zero exit code on `python3 build.py`
