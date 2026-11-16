# Engine, Build Process, and Test Suite Investigation Report

**Working Directory**: `.agents/teamwork/survey_explorer_engine/`  
**Date**: 2026-11-16  
**Author**: Engine and Test Explorer  
**Mission**: Investigate `screener/apply_evaluation.py`, `build.py`, and `tests/` in preparation for Phase 2 bulk re-scoring across all 989 Gate 3 companies.

---

## 1. Observation

### 1.1 `screener/apply_evaluation.py` Execution and CLI Arguments
Direct inspection of `screener/apply_evaluation.py` (lines 8–12, 404–435):
- **Command-line arguments**:
  - `--input`, `-i`: Path to JSON evaluation file, or `"-"` to read JSON from `sys.stdin`. (Required)
  - `--universe`, `-u`: Target universe (`"us"`, `"eu"`, `"ca"`). Optional; if omitted, `find_company_universe(company_id)` iterates through `data/*/inputs.csv` to auto-detect the company's universe (lines 104–111).
  - `--dry-run`: Preview input diffs without writing modifications to disk (lines 389–391, 408).
  - `--rebuild`: Automatically runs `build.py` after applying changes (lines 409, 428–434).
- **Execution behavior**:
  - Ingests qualitative inputs; per line 303–304, any `quantitative_overrides` block in the JSON is rejected/ignored with a warning per v7.6 specification ("the valuation uses statement data only").
  - Identifies row by `id` or `ticker` in `data/<universe>/inputs.csv`.
  - Normalizes keys via `QUAL_KEY_MAP` (lines 42–86), maps legacy 3a aliases via `LEGACY_MOAT_ALIASES` (lines 177–181).
  - Enforces mandatory validation checks:
    - If `calamity == "Y"`, `calamity_note` is strictly required (lines 351–353: `calamity_flag='Y' requires a non-empty calamity_note`).
    - If any of the five Gate 4 Porter force scores is non-zero (1 or 2), a non-empty `4n` Runway & Forces note is strictly required (lines 355–364).

### 1.2 Sequential Munger Reject Waterfall & Field Clearing
In `screener/apply_evaluation.py:validate_and_waterfall` (lines 234–301):
The 6 qualitative gates are checked in strict sequential order:
- **Gate 1 (`1`) Check (Never Waivable)**:
  - If `qual["1"] == "N"`:
    - Clears: `"2"`, `"2r"`, all Gate 3 keys (`"3_tb"`, `"3_ia"`, `"3_se"`, `"3_rd"`, `"3a"`, `"3b"`, `"3m"`), all Gate 4 keys (`"4_ent"`, `"4_riv"`, `"4_buy"`, `"4_sup"`, `"4_sub"`, `"4"`, `"4n"`), `"5"`, and `"6"`.
    - Clears calamity flag and note via `clear_calamity("Gate 1 is 'N'")`.
- **Gate 2 (`2`) Check (Never Waivable)**:
  - If `qual["1"] == "Y"` and `qual["2"] == "N"`:
    - Clears: all Gate 3 keys, all Gate 4 keys, `"5"`, and `"6"`.
    - Clears calamity: `clear_calamity("Gate 2 is 'N'")`.
  - If `qual["2"] == "Y"`: clears `"2r"` (Gate 2 reason is only retained on rejection).
- **Gate 3 (`3a`, `3b`) Check**:
  - Condition: `g3a == "None"` OR (`g3b == "N"` and not `calamity == "Y"`).
  - `g3a == "None"` is **never waivable** (even if calamity is requested).
  - If failed:
    - Clears: all Gate 4 keys (`"4_ent"`, `"4_riv"`, `"4_buy"`, `"4_sup"`, `"4_sub"`, `"4"`, `"4n"`), `"5"`, and `"6"`.
    - Clears calamity: `clear_calamity(reason)`.
- **Gate 4 (`4`) Check (Never Waivable)**:
  - Condition: `qual["4"] < 15` (where `qual["4"]` is CAP in years).
  - If failed (`CAP < 15`):
    - Clears: `"5"` and `"6"`.
    - Clears calamity: `clear_calamity("Gate 4 (CAP={g4_num}) < 15")`.
- **Gate 5 (`5`) Check**:
  - Condition: `int(qual["5"]) == 0` and not `calamity == "Y"`.
  - If failed without active calamity:
    - Clears: `"6"`.
- **Gate 6 (`6`) Check**:
  - `qual["6"] == "N"` fails Gate 6, but is waivable if `calamity == "Y"`.
- **Calamity Sanity Guard** (lines 293–301):
  - If `calamity == "Y"`, verifies that at least one waivable gate failed (`3b == "N"` or `5 == 0` or `6 == "N"`). If not, issues warning: `"Calamity flag 'Y' is set, but no eligible gate (3b, 5, or 6) failed."`

### 1.3 Deterministic CAP (`4`) and Primary Moat (`3a`) Calculations
Defined in `screener/gates.py` and applied in `screener/apply_evaluation.py`:
- **Gate 3 Moat Archetype Subscores**:
  - Four subscores: `3_tb` (Toll booth & switching costs), `3_ia` (Irreplaceable infrastructure & intangibles), `3_se` (Scale economies shared), `3_rd` (R&D & innovation leadership). Each must be integer `0`, `1`, or `2`.
  - **Deterministic Initial CAP** (`screener/gates.py:compute_initial_cap_from_scores`, lines 41–59):
    Let $m_{\max} = \max(\text{scores})$ and $m_{\text{sum}} = \sum(\text{scores})$:
    - $m_{\max} == 0 \implies 0\text{Y}$ (No moat $\implies$ fails Gate 3, Gate 3a becomes `"None"`).
    - $m_{\max} == 1, m_{\text{sum}} == 1 \implies 15\text{Y}$.
    - $m_{\max} == 1, m_{\text{sum}} \ge 2 \implies 20\text{Y}$ (capped at 20Y without an elite score of 2).
    - $m_{\max} == 2, m_{\text{sum}} == 2 \implies 20\text{Y}$.
    - $m_{\max} == 2, m_{\text{sum}} == 3 \implies 25\text{Y}$.
    - $m_{\max} == 2, m_{\text{sum}} \ge 4 \implies 30\text{Y}$.
  - **Deterministic Gate 3a Primary Moat** (`screener/apply_evaluation.py`, lines 200–210):
    - If $m_{\max} == 0 \implies$ `3a` is set to `"None"`.
    - If $m_{\max} > 0$: candidate archetypes are those matching $m_{\max}$. If existing/supplied `3a` is among candidate archetypes, it is kept; otherwise, defaults deterministically to the first archetype in canonical order (`MOAT_SCORE_SPEC`).
- **Gate 4 Porter Force Subscores & Final CAP**:
  - Five force subscores: `4_ent` (Entrants), `4_riv` (Rivalry), `4_buy` (Buyers), `4_sup` (Suppliers), `4_sub` (Substitution). Each must be `0`, `1`, or `2`.
  - Count of moderate forces ($c_1$, forces scored 1) and count of high/fatal forces ($c_2$, forces scored 2).
  - **Moderate haircut** $h(c_1)$ (`screener/gates.py:moderate_force_haircut`, lines 62–71):
    - $c_1 = 0 \implies 0\text{Y}$
    - $c_1 \in \{1, 2\} \implies 5\text{Y}$
    - $c_1 \in \{3, 4\} \implies 10\text{Y}$
    - $c_1 = 5 \implies 15\text{Y}$
  - **Final CAP Formula** (`screener/gates.py:compute_final_cap_from_scores`, lines 74–90):
    - If $\text{CAP}_{\text{init}} \le 0$ or $c_2 \ge 3 \implies 0\text{Y}$ (fatal flaw).
    - If $c_2 == 2 \implies 5\text{Y}$ (fatal flaw).
    - If $c_2 == 1$: let $\text{rem} = \text{CAP}_{\text{init}} - 10 - h(c_1)$. Final CAP is $10\text{Y}$ if $\text{rem} \ge 10$, else $5\text{Y}$ (fatal flaw).
    - If $c_2 == 0 \implies \max(5, \text{CAP}_{\text{init}} - h(c_1))$.
  - In `screener/apply_evaluation.py` (lines 212–221): if all 4 moat scores and 5 force scores are present and $\text{CAP}_{\text{init}} > 0$, formula-derived Final CAP overwrites any manually supplied CAP.

### 1.4 Mirror Tickers Synchronization Mechanics
Direct observation of `screener/apply_evaluation.py` and `fetch_market_data.py`:
- **`screener/apply_evaluation.py` does NOT synchronize mirrors**:
  - `apply_evaluation.py` only updates the specific company row in `data/<universe>/inputs.csv` for the target company ID. It does not inspect `universe.json` or mirror mappings.
- **Mirror definitions**:
  - Defined in `data/us/universe.json` (lines 87–90):
    ```json
    "mirror": {
      "ASML": "eu:ASML.NL",
      "FER": "eu:FER.ES"
    }
    ```
- **Existing mirror sync tool**:
  - `fetch_market_data.py:apply_mirrors(keys, eod, state)` (lines 365–417) copies qualitative scores (`[*QUAL_CODES, "calamity", "calamity_note"]`) from primary listing (`eu:ASML.NL`, `eu:FER.ES`) to mirror listing (`us:ASML`, `us:FER`).
- **Current state in `inputs.csv`**:
  - `ASML` (US) vs `ASML.NL` (EU): All 17 qualitative gate score fields match 100%. However, their narrative `note` and `evidence` strings have slight divergences.
  - `FER` (US) vs `FER.ES` (EU): Both reach Gate 3 (`1 == "Y"`, `2 == "Y"`). Neither has been scored under the deterministic CAP engine yet (`3_tb..3_rd` and `4_ent..4_sub` are currently null).

### 1.5 Calamity Pass Rules
- Governed by `screener/config.py:CALAMITY_GATES = ("3b", "5", "6")` and `screener/gates.py:phase_results` (lines 192–223):
  - Calamity can ONLY waive Gate 3b, Gate 5, and/or Gate 6.
  - Anchor gates (Gate 1, Gate 2, Gate 3a $\neq$ "None", Gate 4 CAP $\ge$ 15) can NEVER be waived.
  - If calamity is active and anchor gates pass, `phase_results` returns `result = C.RES_CALAMITY` ("Calamity pass").
  - In the cockpit dashboard (`screener/dashboard.py:collect_screener_data`, lines 107–110), a company reaches **Prime Grade Calamity** only if:
    `result == C.RES_CALAMITY` AND `g6_flags < 3`.
    (Companies such as `EL` and `RTX` have `result == 'Calamity pass'` from qualitative gates but have 3 G6 quantitative flags, so they do not count in `Prime Grade Calamity` in the summary KPI).

---

### 1.6 `build.py` and Output Generation
Direct inspection of `build.py` (lines 1–46) and `screener/dashboard.py` (lines 4679–4698):
- **Command invocation**:
  `python3 build.py` (or `python3 build.py [universe...]`)
- **Inputs read**:
  - `data/<u_key>/universe.json`: metadata, benchmark tickers, parameter overrides, mirror mappings.
  - `data/<u_key>/inputs.csv`: 26 columns of qualitative gate scores, notes, evidence.
  - `data/<u_key>/financials.csv`: 36 quantitative statement metrics.
  - `data/<u_key>/sales_cagr.csv`: historical panel sales CAGRs.
  - `screener/config.py`: field definitions, canonical archetypes, parameter groups, changelog.
  - `screener/gates.py`: valuation math (`par_valuation`), gate evaluations (`results`, `cap_audit`), G6 health checks (`g6_checks`).
  - `screener/dashboard.py`: HTML template, inline CSS, embedded JavaScript sandbox runtime.
- **Outputs generated**:
  - `output/screener.html`: Main standalone interactive HTML dashboard.
  - `output/index.html`: Identical copy written to `output/index.html` for local browsers and static file servers.
  - `docs/index.html`: Identical copy written to `docs/index.html` for GitHub Pages hosting.
- **Current execution run output**:
  ```
  Compiling Quality & Moat Screener HTML Cockpit for: ca, eu, us...

  ✓ Dashboard built in 3.38s:
    • File: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/output/screener.html
    • Secondary File: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/output/index.html
    • GitHub Pages File: docs/index.html
    • Total Companies: 1175
    • Prime Grade: 223
    • Prime Grade Calamity (Conditional): 11
    • Valued Prime Grade: 218 (Median IRR vs hurdle: -12.2pp)
  ```

---

### 1.7 Test Suite Execution and Baseline Assertions
Direct execution of `python3 -m unittest discover tests`:
- **Current status**:
  `Ran 169 tests in 8.916s. OK (100% passing)`.
- **Inventory of test files**:
  1. `test_calamity_tier.py`: 12 tests (calamity pass rules, waterfall scrubbing, universe baseline counts).
  2. `test_cap_engine.py`: 15 tests (deterministic CAP formulas, fatal-flaw caps, 11 pilot reference companies, ASML mirror parity, dashboard CAP audit export).
  3. `test_dashboard_filters.py`: 3 tests (Gate 1–6 prefix filter matching, Quality Grade / Prime Grade requirements).
  4. `test_quantitative_growth.py`: 36 tests (statistical growth estimators, EODHD SQLite cache, EODHD source checks for `funnel_ids(u)`).
  5. `test_v71_remediation.py`: 20 tests (concessions, fin_notes, net debt).
  6. `test_v72_remediation.py`: 17 tests (JS sandbox blocking auto notes, share splits).
  7. `test_v73_capital_base.py`: 4 tests (invested capital, tangible capital).
  8. `test_v74_data_quality.py`: 8 tests (M&A spend, consolidated ROE, fiscal year stubs).
  9. `test_v75_roe_capital.py`: 5 tests (ROE capital base).
  10. `test_v76_g6_overrides.py`: 12 tests (no analyst overrides, statement-only inputs).
  11. `test_v77_alignment.py`: 6 tests (parameter centralization, hurdle-aware dashboard).
  12. `test_valuation_sandbox.py`: 31 tests (JS sandbox parity via `jsc`, Bellman equation, Miller-Modigliani invariance, zero baseline discrepancies across all universe companies).

- **`tests/test_calamity_tier.py` Baseline Counts Assertion**:
  Lines 156–159:
  ```python
  def test_universe_baseline_counts_preserved(self):
      counts = {k: len(funnel_ids(load_universe(k), include_calamity=False)) for k in ("us", "eu", "ca")}
      self.assertEqual(counts, {"us": 109, "eu": 103, "ca": 11})
  ```
  - `funnel_ids(u, include_calamity=False)` filters for companies whose qualitative gate evaluation evaluates to `result == C.RES_QPASS` ("Quality pass").
  - Current baseline values:
    - US: 109
    - EU: 103
    - CA: 11
    - Total: 223 (matches `Prime Grade: 223` in `build.py`).

---

## 2. Logic Chain

### 2.1 From Problem Boundary to 989 Gate 3 Universe
1. **Observation**: A company reaches Gate 3 if and only if it passes Gate 1 (`1 == "Y"`) and Gate 2 (`2 == "Y"`).
2. **Observation**: Querying all three universes yields:
   - CA: 49 companies
   - EU: 495 companies
   - US: 445 companies
   - Total: $49 + 495 + 445 = 989$ companies reaching Gate 3.
3. **Logic**: Exactly 11 reference companies (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`) have complete Gate 3 moat scores and Gate 4 force scores (or moat complete with CAP 0 for `NUE`).
4. **Conclusion**: Exactly 978 companies ($989 - 11 = 978$) require new Gate 3/4 scoring in Phase 2 bulk re-scoring.

### 2.2 Impact of Scoring on the Reject Waterfall and Downstream Scrubbing
1. **Observation**: `validate_and_waterfall()` automatically clears all downstream gate fields when an anchor gate fails.
2. **Logic**:
   - If a company receives all 0s on moat scores ($m_{\max} = 0$), `3a` is deterministically forced to `"None"`.
   - Gate 3a `"None"` immediately triggers the waterfall rejection, clearing Gate 4 force scores, Gate 4 CAP, Gate 4n note, Gate 5, Gate 6, and any calamity flag/note.
   - If a company passes Gate 3a with a valid moat but receives Gate 4 Porter forces resulting in Final CAP $< 15$, Gate 4 fails.
   - Gate 4 CAP $< 15$ immediately triggers the waterfall rejection, clearing Gate 5, Gate 6, and any calamity flag/note.
3. **Conclusion**: When applying re-scored evaluations, agents/scripts must let `screener/apply_evaluation.py` enforce this downstream clearing so that rejected companies do not leave orphaned downstream scores in `inputs.csv`.

### 2.3 Synchronization of Dual-Listed Mirror Companies
1. **Observation**: `apply_evaluation.py` only touches the single universe of the submitted `id` and does not propagate to mirror tickers.
2. **Observation**: `data/us/universe.json` defines two mirrors: `ASML -> eu:ASML.NL` and `FER -> eu:FER.ES`.
3. **Observation**: `tests/test_cap_engine.py:224–225` verifies exact equality between `ASML` and `ASML.NL` across `(*MOAT_SCORE_CODES, "3a", "3b", *FORCE_SCORE_CODES, "4", "4n")`.
4. **Observation**: Requirement R2 and Acceptance Criteria specify: "Dual-listed mirror companies have identical gate scores, notes, and evidence across universes."
5. **Logic**: If an evaluation is applied to `ASML.NL` (EU) or `FER.ES` (EU), it will NOT automatically copy to `ASML` (US) or `FER` (US).
6. **Conclusion**: The Phase 2 pipeline must explicitly score or synchronize mirror pairs simultaneously, copying identical scores, `note`, and `evidence`.

### 2.4 Why and How `test_calamity_tier.py` Counts Will Shift
1. **Observation**: `test_universe_baseline_counts_preserved` tests `counts = {k: len(funnel_ids(load_universe(k), include_calamity=False)) for k in ("us", "eu", "ca")}` against `{"us": 109, "eu": 103, "ca": 11}`.
2. **Observation**: Out of the 989 companies reaching Gate 3, 978 are currently unscored at Gates 3 and 4, meaning many currently hold provisional or legacy values from earlier versions.
3. **Logic**:
   - When 978 companies are scored with deterministic moat and force rubrics, some companies previously classified as `Quality pass` may be rejected at Gate 3 ($3a = \text{"None"}$ or $3b = \text{"N"}$) or at Gate 4 ($\text{CAP} < 15$).
   - Conversely, companies previously held in review or rejected may now qualify for `Quality pass` or `Calamity pass`.
   - Consequently, `len(funnel_ids(u, include_calamity=False))` for `us`, `eu`, and `ca` will shift to new integer values.
4. **Conclusion**: Requirement R3 explicitly states: "updating the baseline universe count assertions in `tests/test_calamity_tier.py` to match the newly verified counts when scoring shifts companies between quality/calamity pass and rejected states." This assertion must be updated once the new bulk scores are finalized and validated.

---

## 3. Caveats

1. **No Source Modification in Survey Phase**: Per explorer constraints, no modifications to `inputs.csv`, `tests/test_calamity_tier.py`, or codebase files were made during this investigation.
2. **Quantitative Source Requirement in `funnel_ids`**: `tests/test_quantitative_growth.py` line 548 asserts that every company in `funnel_ids(u)` has an EODHD data source (`str(r.get("source")).startswith("EODHD")`). We verified that all US, CA, and EU companies reaching Gate 3 have valid EODHD sources (the only missing EODHD company is `DLG.IT`, which is rejected at Gate 2 and will never reach Gate 3).
3. **Difference between `funnel_ids(include_calamity=False)` and `Prime Grade Calamity`**:
   `funnel_ids(include_calamity=False)` counts purely qualitative `Quality pass` companies. Prime Grade Calamity in `build.py` further filters `Calamity pass` companies with `g6_flags < 3`. Both metrics will shift when bulk re-scoring is applied.
4. **Mirror Textual Sync**: While `tests/test_cap_engine.py` currently tests score parity for `ASML`/`ASML.NL`, `ORIGINAL_REQUEST.md` requires notes and evidence to also match identically across mirrors.

---

## 4. Conclusion

1. **Evaluation Engine Readiness**:
   `screener/apply_evaluation.py` is fully operational, thoroughly enforces the sequential Munger reject waterfall, calculates deterministic CAP (`4`) and primary moat archetype (`3a`), and validates non-empty `4n` and `calamity_note`.
2. **Batch Ingestion & Mirror Gap**:
   Because `apply_evaluation.py` operates on a single company row without automatic mirror cross-population, the Phase 2 execution pipeline must ensure:
   - Mirror pairs (`ASML` $\leftrightarrow$ `ASML.NL`, `FER` $\leftrightarrow$ `FER.ES`) receive identical payloads for all gate scores, `4n`, `note`, and `evidence`.
   - Bulk payloads can be fed cleanly either via stdin/file to `apply_evaluation.py` or through a batch script that calls `apply_evaluation.py` per company.
3. **Build Script & Outputs**:
   `build.py` runs cleanly in ~3.4s, reading `data/` inputs and generating byte-identical cockpit builds at `output/screener.html`, `output/index.html`, and `docs/index.html`.
4. **Test Suite Baseline & Update Strategy**:
   The test suite currently passes 100% (169/169 tests). The 11 Phase 1 reference companies in `test_cap_engine.py` are strictly protected and must retain their scores. Following Phase 2 re-scoring, `tests/test_calamity_tier.py:158` must be updated with the newly calculated counts for `us`, `eu`, and `ca`.

---

## 5. Verification Method

To independently verify all findings in this report, execute the following commands in the workspace root:

1. **Verify Baseline Test Suite Passes (169 tests)**:
   ```bash
   python3 -m unittest discover tests
   ```
   *Expected output*: `Ran 169 tests in ~8.9s. OK`

2. **Verify Cockpit Build Execution and Generated Files**:
   ```bash
   python3 build.py
   ```
   *Expected output*:
   - Exit code `0`
   - Files generated: `output/screener.html`, `output/index.html`, `docs/index.html`
   - Console summary matching: Total Companies: 1175, Prime Grade: 223, Prime Grade Calamity: 11.

3. **Verify Gate 3 Company Population (989 total)**:
   ```bash
   python3 -c "
   from screener.data import load_universe, universe_keys
   counts = {u: len([c for c in load_universe(u)['companies'] if c.get('1') == 'Y' and c.get('2') == 'Y']) for u in universe_keys()}
   print(counts, 'Total:', sum(counts.values()))
   "
   ```
   *Expected output*: `{'ca': 49, 'eu': 495, 'us': 445} Total: 989`

4. **Verify Mirror Definitions and `apply_evaluation.py` Waterfall Behavior**:
   ```bash
   python3 screener/apply_evaluation.py --input evaluations/HEIO.NL_qual.json --dry-run
   ```
   *Expected output*: Executes validation and prints waterfall diff without modifying files.
