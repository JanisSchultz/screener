# Challenger 1 Handoff Report: Adversarial CAP Math & Waterfall Verification

**Verdict**: `APPROVE`
**Milestone**: M5 (Final Acceptance — Adversarial Challenge & Integrity Verification)
**Agent**: Challenger 1 (Adversarial CAP Math & Waterfall Challenger)
**Working Directory**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/challenger_1/`

---

## 1. Observation

Direct empirical observations collected across `data/{us,eu,ca}/inputs.csv`, `screener/gates.py`, `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `tests/`, and `build.py`:

### 1.1 Universe Populations & Gate 3 Reach
- **Universe row counts**:
  - `data/us/inputs.csv`: 515 total rows
  - `data/eu/inputs.csv`: 602 total rows
  - `data/ca/inputs.csv`: 58 total rows
  - Total: 1,175 rows
- **Gate 3 candidate counts** (`1 == "Y"` and `2 == "Y"`):
  - US: 445 companies (target: 445)
  - EU: 495 companies (target: 495)
  - CA: 49 companies (target: 49)
  - Total Gate 3 Candidates: **989 companies** (100% matched to target)

### 1.2 Gate 3 Moat Profiles, Initial CAP & 3a Derivation
- All 989 Gate 3 companies have populated moat scores in `{0, 1, 2}` across all four archetypes (`3_tb`, `3_ia`, `3_se`, `3_rd`).
- Independent recalculation of Initial CAP $\text{CAP}_{\text{init}}$ directly from `(3_tb, 3_ia, 3_se, 3_rd)` against `screener/gates.py:compute_initial_cap_from_scores` produced **0 discrepancies** across all 989 companies.
- Independent derivation of primary moat `3a` confirmed **0 discrepancies** across all 989 companies:
  - If $m_{\max} = 0 \implies 3a = \text{"None"}$ (38 companies).
  - If $m_{\max} > 0 \implies 3a$ matches an archetype achieving $m_{\max}$ (951 companies).
  - All 989 companies use canonical labels from `C.MOAT_TYPES`; zero legacy un-normalized aliases.
- **Empirical Initial CAP Distribution across 989 companies**:
  - `0Y`: 38 companies
  - `15Y`: 380 companies
  - `20Y`: 230 companies
  - `25Y`: 273 companies
  - `30Y`: 68 companies
- **Empirical Primary Moat 3a Distribution across 989 companies**:
  - `Toll booth & switching costs`: 489 companies
  - `Irreplaceable infrastructure & intangibles`: 356 companies
  - `R&D & innovation leadership`: 70 companies
  - `None`: 38 companies
  - `Scale economies shared`: 36 companies

### 1.3 Gate 3 Sequential Waterfall Enforcement
- **Gate 3 Failing Partition**: Exactly **504 companies** fail Gate 3 (`3a == "None"` or `3b == "N"` without calamity):
  - US: 198 companies
  - EU: 278 companies
  - CA: 28 companies
  - **Downstream Clearing**: 100% of these 504 failing companies have Gate 4 (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`) and Gates 5–6 (`5`, `6`) cleared to empty string `""`.
  - **Anchor Gate Calamity Guard**: All 38 companies with $3a = \text{"None"}$ have `calamity` and `calamity_note` cleared to `""` (no invalid calamity waivers).
  - **Waterfall Leaks**: **0 leaks detected**.
- **Gate 3 Passing Partition**: Exactly **485 companies** pass Gate 3 (`3a != "None"` and `(3b == "Y" or calamity == "Y")`):
  - US: 247 companies
  - EU: 217 companies
  - CA: 21 companies
  - **Gate 4 Population**: 100% of these 485 passing companies have all five force scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`) and deterministic Final CAP `4` populated.

### 1.4 Gate 4 Competitive Forces, Moderate Haircuts & Final CAP Math
- All 485 Gate 3 passing companies have valid force scores in `{0, 1, 2}`.
- Independent clean-room calculation of tiered moderate haircut $h(c_1)$:
  - `0Y` ($c_1 = 0$): 20 companies
  - `5Y` ($c_1 \in \{1, 2\}$): 217 companies
  - `10Y` ($c_1 \in \{3, 4\}$): 240 companies
  - `15Y` ($c_1 = 5$): 8 companies
- Independent calculation of Fatal Flaw caps ($c_2 \ge 1 \implies \text{CAP} \le 10\text{Y}$):
  - Fatal Flaw active ($c_2 \ge 1$): 80 companies (16.5% of passing Gate 3)
  - No Fatal Flaw ($c_2 = 0$): 405 companies (83.5% of passing Gate 3)
- Deterministic Final CAP comparison:
  - Bit-for-bit comparison of column `4` against independent clean-room formula produced **0 discrepancies** and **0 manual overrides** across all 485 companies.
- **Empirical Final CAP Distribution across 485 Gate 3 passing companies**:
  - `5Y`: 75 companies
  - `10Y`: 42 companies
  - `15Y`: 219 companies
  - `20Y`: 136 companies
  - `25Y`: 5 companies
  - `30Y`: 8 companies
- **Mandatory `4n` Runway & Forces Note**:
  - 467 companies have at least one force $\ge 1$; all 467 (100%) have a non-empty `4n` note.
  - 18 companies have all five forces $= 0$; all 18 also provide explicit explanatory notes justifying total force insulation.
  - Missing mandatory `4n` notes: **0**.

### 1.5 Gate 4 Sequential Waterfall Enforcement & Funnel Outcomes
- **Gate 4 Failing Partition (`CAP < 15`)**: Exactly **117 companies** (US: 63, EU: 54, CA: 0):
  - 100% of these 117 companies have Gates 5 and 6 cleared to empty string `""`.
  - 100% have `calamity` and `calamity_note` cleared to `""` (Gate 4 is an anchor gate).
  - Waterfall violations: **0**.
- **Gate 4 Passing Partition (`CAP >= 15`)**: Exactly **368 companies** (US: 184, EU: 163, CA: 21):
  - Gate 5 is populated in `{0, 1, 2}` for all 368 companies.
  - 10 companies fail Gate 5 (`5 == 0`, unwaived): Gate 6 is cleared to empty string `""`.
  - 358 companies reach Gate 6: Gate 6 is populated in `{"Y", "N"}` for all 358 companies.
  - Companies left in "To review (blank gate)": **0**.
- **Final Funnel Counts**:
  - Quality Pass (`result == "Quality pass"`): **223 companies** (US: 109, EU: 103, CA: 11).
  - Calamity Pass (`result == "Calamity pass"`): **13 companies** (US: 10, EU: 3, CA: 0).
  - Prime Grade Calamity in Cockpit (`passes_calamity_grade`, $g_6\text{-flags} < 3$): **11 companies** (US: 9, EU: 2, CA: 0).

### 1.6 Reference Companies & Dual-Listed Mirror Synchrony
- All 11 Phase 1 reference companies (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`) match `REFERENCE_SNAPSHOT` character-for-character across all gate fields, notes, and evidence.
- Dual-listed mirror pairs (`ASML` <-> `ASML.NL` and `FER` <-> `FER.ES`) exhibit exact 100% character-for-character parity across all 20 qualitative fields, notes, and evidence: **0 differences**.

### 1.7 Combinatorial State-Space Exploration & Mutation Testing
- Exhaustive testing of all $3^4 = 81$ moat score combinations against the Initial CAP formula produced **0 anomalies**.
- Exhaustive testing of all $5 \times 3^5 = 1,215$ (Initial CAP $\times$ Force scores) state-space paths against `compute_final_cap_from_scores` produced **0 anomalies** (all outputs $\in \{0, 5, 10, 15, 20, 25, 30\}$; fatal-flaw caps strictly bounded $\le 10\text{Y}$).
- In-memory mutation sensitivity tests verified that:
  - Attempted manual CAP overrides are overridden by the deterministic formula.
  - Downstream gates on Gate 3 failures are scrubbed.
  - Gates 5–6 on Gate 4 failures are scrubbed.
  - Calamity waivers on anchor gates (Gates 1, 2, 3a, 4) are rejected and scrubbed.

### 1.8 Full Test Suite & Build Execution
- `python3 -m unittest discover tests`: Ran 303 tests in 19.917s, **OK** (100% pass).
- `python3 -m unittest tests/test_bulk_scoring_e2e.py`: Ran 134 tests in 9.043s, **OK** (100% pass).
- `python3 screener/bulk_scorer.py --audit`: **ALL CHECKS PASSED** (0 discrepancies, 0 violations).
- `python3 build.py`: Generated `output/screener.html`, `output/index.html`, and `docs/index.html` in 3.00s with exit code 0.

---

## 2. Logic Chain

1. **Gate 3 Population Grounding**:
   - Observation 1.1 establishes that exactly 989 companies meet the Gate 3 entry criteria (`1 == "Y"` and `2 == "Y"`). This satisfies requirement R1 and `PROJECT.md` line 4.
2. **Moat Derivation & Initial CAP Soundness**:
   - Observation 1.2 demonstrates that every company has 4 valid moat sub-scores, that `compute_initial_cap_from_scores` matches the specification across all 81 potential combinations, and that primary moat `3a` strictly follows the maximum sub-score. Because zero discrepancies were observed between independent clean-room recalculation and the stored values, the Initial CAP calculation is 100% mathematically sound.
3. **Munger Sequential Waterfall Invariant on Gate 3**:
   - Observation 1.3 shows that the 989 candidate companies partition into 504 failing and 485 passing companies. For all 504 failing companies, Gate 4 and Gates 5–6 are 100% blank (`""`), confirming that no downstream evaluations leaked past Gate 3 rejection. Furthermore, 38 companies with no moat ($3a = \text{"None"}$) were barred from calamity waivers.
4. **Deterministic Gate 4 CAP & Force Scoring**:
   - Observation 1.4 confirms that for all 485 companies advancing to Gate 4, force scores are populated and Final CAP `4` matches the deterministic two-step formula ($c_1$ moderate haircuts and $c_2$ fatal flaw caps) bit-for-bit without manual overrides. The mandatory `4n` requirement is 100% fulfilled (467/467 companies with force $\ge 1$ possess non-empty notes).
5. **Gate 4 Waterfall & Downstream Completeness**:
   - Observation 1.5 proves that for all 117 companies with Final CAP $< 15$, Gates 5–6 are cleared to `""` with zero exceptions. For all 368 companies with Final CAP $\ge 15$, Gate 5 is populated and downstream evaluation proceeds without leaving any company in `"To review (blank gate)"`.
6. **Integrity, Parity, and Regressions**:
   - Observations 1.6–1.8 prove that reference companies remain untampered, mirror pairs have bit-for-bit parity, all 303 unit tests pass, and HTML cockpit generation runs cleanly with exit code 0.

---

## 3. Caveats

- **Qualitative Prose Authenticity**: Challenger 1's mandate focuses exclusively on mathematical recalculation, deterministic formulas, and waterfall invariant verification. The forensic evaluation of qualitative note prose (ensuring evaluations were produced by genuine AI analysis rather than mechanical script generators) is within the scope of the Forensic Auditor and Challenger 2.
- **Financial Statement Data**: Quantitative statement inputs in `data/*/financials.csv` were treated as verified source-of-truth groundings per the v7.6 architecture.

---

## 4. Conclusion

The CAP mathematics and sequential Munger waterfall invariants across all 989 Gate 3 companies in `data/{us,eu,ca}/inputs.csv` are **100% mathematically correct, deterministic, and leak-free**. 
- 0 CAP formula discrepancies.
- 0 manual CAP overrides.
- 0 waterfall leaks across 504 Gate 3 failures and 117 Gate 4 failures.
- 0 missing `4n` notes.
- 0 mirror discrepancies across dual-listed tickers.
- 100% pass across full unit test suite (303 tests) and Phase 2 E2E suite (134 tests).
- 100% clean build of interactive cockpit HTML outputs.

**Explicit Verdict**: `APPROVE`

---

## 5. Verification Method

To independently verify these conclusions, execute the following commands from the project root:

1. **Run Full Test Suite**:
   ```bash
   python3 -m unittest discover tests
   ```
   *Expected outcome*: 303 tests ran, exit code 0, OK.

2. **Run E2E Phase 2 Test Suite**:
   ```bash
   python3 -m unittest tests/test_bulk_scoring_e2e.py
   ```
   *Expected outcome*: 134 tests ran, exit code 0, OK.

3. **Run Comprehensive Compliance Audit**:
   ```bash
   python3 screener/bulk_scorer.py --audit
   ```
   *Expected outcome*: All 8 audit sections report `PASSED` / `0 discrepancies` / `0 violations`.

4. **Run Cockpit HTML Build**:
   ```bash
   python3 build.py
   ```
   *Expected outcome*: Cockpit compiles in ~3s with exit code 0 (`Prime Grade: 223`, `Prime Grade Calamity: 11`).

5. **Run Clean-Room Mathematical Recalculation**:
   ```bash
   python3 -c "
   import csv
   from pathlib import Path
   from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

   for u in ['us', 'eu', 'ca']:
       with open(f'data/{u}/inputs.csv', newline='', encoding='utf-8') as f:
           rows = list(csv.DictReader(f))
       for r in rows:
           if r.get('1') == 'Y' and r.get('2') == 'Y':
               m = [int(r[c]) for c in ('3_tb', '3_ia', '3_se', '3_rd')]
               icap = compute_initial_cap_from_scores(m)
               if r.get('3a') != 'None' and (r.get('3b') == 'Y' or r.get('calamity') == 'Y'):
                   f = [int(r[c]) for c in ('4_ent', '4_riv', '4_buy', '4_sup', '4_sub')]
                   fcap, _, _ = compute_final_cap_from_scores(icap, f)
                   assert int(r['4']) == fcap, f'CAP mismatch on {r[\"id\"]}'
   print('Clean-room check: 100% verified!')
   "
   ```
   *Expected outcome*: `Clean-room check: 100% verified!`
