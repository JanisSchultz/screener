# Forensic Audit Report — Quality & Moat Screener v7.18

**Work Product**: v7.18 Two-Stage Munger Waterfall & Diagnostic Gate 5–6 Scorecard (`screener/`, `tests/`, `data/`, `v718_eval_b01`..`b10`, `output/`, `docs/`, `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`)
**Profile**: General Project (`Integrity mode: development` + explicit `ORIGINAL_REQUEST.md` R1–R4 & Acceptance Criteria)
**Audit Date**: 2026-11-17T16:06:00Z
**Verdict**: **CLEAN**

---

## Phase Results

- **Check 1 — No Hardcoding / Facade / Circumvention in Engine & Tests**: **PASS**
  - `screener/apply_evaluation.py` (`validate_and_waterfall`): Stage 1 early-stop scrubbing on `1="N"`, `2="N"`, `3a="None"`, and unwaived `3b="N"` strictly clears downstream gates `2..6` and calamity flags. Stage 2 preserves diagnostic `5` (`0/1/2`) and `6` (`Y/N`) on `4 < 15` (while calling `clear_calamity`) and on `5 = 0` without calamity, and validates `5` and `6` domains whenever supplied. No hardcoded ticker overrides or bypasses.
  - `screener/bulk_scorer.py` (`validate_company_evaluation`, `audit_gate_3_universe`, `REFERENCE_SNAPSHOT`): Preserves diagnostic `5` and `6` on `CAP < 15` and `5 = 0`, validates `5 in {0,1,2}` and `6 in {"Y","N"}`, warns when any Gate-3-advancing company leaves `5` or `6` blank, and audits all 485 Stage-2 moat franchises for valid non-empty `5` and `6` while enforcing blank `4_*, 4, 4n, 5, 6` on all 504 Stage-1 Gate-3 rejects. `REFERENCE_SNAPSHOT["CRM"]` updated to `"5": 0, "6": "Y"` with all other 10 reference companies and mirrors (`ASML`/`ASML.NL`, `FER`/`FER.ES`) intact.
  - `screener/dashboard.py` & `screener/config.py`: `SCREENER_VERSION = "7.18"` with `"7.18"` `CHANGELOG` entry. `openDrawer` renders concrete `PASS/FAIL · <val>` stepper sub-labels (`4`, `5`, `6`) while preserving `WAIVED` on calamity waivers; `#dossier-g56-row` displays `Management & Allocation (G5)` and `Cash & Fortress B/S (G6)`; `#dossier-g6-answer` falls back to `c.g6_answer || c.g6_cash || 'blank'`; `g5_mgmt` and `g6_cash` added to `ALL_COLS` for expanded table mode on `moat_universe` and `all` with `compactKeys`, `qpass`, and `calamity` columns unchanged.
  - `tests/`: `test_calamity_tier.py`, `test_bulk_scoring_e2e.py`, and `test_v718_two_stage_waterfall.py` exercise real engine modules, real CSVs, and compiled HTML/JS via JavaScriptCore (`osascript`) with zero mocked core assertions.

- **Check 2 — Authentic Bottom-Up Qualitative Evaluation of the 121 Companies**: **PASS**
  - Inspected `v718_eval_b01`..`b10` (`evaluations.json`): 121 unique `(universe, id)` entries across 10 batches (`b01`: 24 [22 EU, 2 US], `b02`: 14 [6 EU, 8 US], `b03`: 13 [7 EU, 6 US], `b04`: 11 [5 EU, 6 US], `b05`: 10 [10 US], `b06`: 8 [2 EU, 6 US], `b07`: 8 [3 EU, 5 US], `b08`: 10 [2 EU, 8 US], `b09`: 10 [5 EU, 5 US], `b10`: 13 [3 EU, 10 US]).
  - Zero sub-industries split across multiple batches (`Sub-industries split across >1 batch: {}`); every multi-region sector/sub-industry evaluated US and EU combined side-by-side (`b05` covers IT Software/IT Services where all 10 incomplete rows were US).
  - `121 / 121` unique diagnostic rationales (length 171–1,656 characters), zero boilerplate duplication, 100% parity between `evaluations.json` and `data/{us,eu}/inputs.csv`.
  - All 121 rows carry `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]` matching columns `5` and `6`; zero stale `"Downstream gates bypassed per waterfall."` strings remain; `CRM` note reflects `CAP = 5Y` (zero `CAP = 10` remnants); 13/13 Gate-5 rejects preserved `5 = "0"`; 31/31 `g6_default = "N"` rows scored `6 = "N"`; 0 calamity flags on the 121 rows.
  - Cross-verified 32 sampled companies across all 10 batches (`CRM`, `BA`, `ADP.FR`, `INTU`, `PANW`, `ROP`, `DIM.FR`, `SRT3.DE`, `ABI.BE`, `CSGP`, `CCI`, `ES`, `SO`, `D`, `DANSKE.DK`, `PCG`, `PNN.GB`, `IFF`, `DSFIR.NL`, `ADBE`, `PLTR`, `TRMB`, `MMM`, `SBUX`, `MONC.IT`, `FGR.FR`, `INCY`, `PODD`, `ACGL`, `SLHN.CH`, `NOD.NO`, `ENR.DE`) against `financials.csv`, `fundamentals_panel.csv`, and `prescreen.csv` — all cited metrics (ROIC, FCF conversion, net debt/OE years, interest coverage, SBC, goodwill/intangibles, Owner EPS) match empirical statement data.

- **Check 3 — Data Immutability, Docs, Build & Test Execution**: **PASS**
  - `git diff HEAD` vs `data/{us,eu,ca}/inputs.csv`: strictly 121 rows modified (`us`: 66 = 57 G4 rejects + 9 G5 rejects; `eu`: 55 = 51 G4 rejects + 4 G5 rejects; `ca`: 0), strictly columns `{5, 6, note}` modified (`'5': 57, '6': 66, 'note': 66` in US; `'5': 51, '6': 55, 'note': 55` in EU), zero Gate 1–4 (`1..4n`) changes, zero non-target row changes.
  - `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` updated to v7.18 Two-Stage Waterfall consistently (`CRM` Example 4 matches verified `5=0`, `6="Y"`, `CAP=5Y`).
  - Independent command execution:
    - `python3 screener/bulk_scorer.py --audit`: exit code `0` (989/989 Gate-3 scored, 485/485 Stage-2 G5/G6 valid, 0 discrepancies/violations, 11/11 reference companies verified, dual-listed mirror parity PASSED).
    - `python3 build.py`: exit code `0` (`Total Companies: 1175`, `Prime Grade: 225`, `Prime Grade Calamity (Conditional): 11`, `Valued Prime Grade: 220 (Median IRR vs hurdle: -12.0pp)`); `output/screener.html`, `output/index.html`, and `docs/index.html` byte-for-byte identical.
    - `python3 -m unittest discover -s tests -v`: exit code `0` (`Ran 319 tests in 23.545s`, `OK`).

---

## Evidence

### 1. Data Diff Against `git HEAD`
```text
=== US ===
Changed rows: 66 | G4_rej: 57 | G5_rej: 9
Changed cols: {'5': 57, '6': 66, 'note': 66}
Non-target changed: []
=== EU ===
Changed rows: 55 | G4_rej: 51 | G5_rej: 4
Changed cols: {'5': 51, '6': 55, 'note': 55}
Non-target changed: []
=== CA ===
Changed rows: 0 | Non-target changed: []
```
Additional full-corpus invariant check:
```text
Checked 121 count: 121
g6_default=N violations: []
calamity=Y on 121: []
CAP text mismatches in 121 notes: []
```

### 2. Batching & Rationale Uniqueness (`v718_eval_b01`..`b10`)
```text
Batch files: 10
v718_eval_b01: n=24 univ={'eu': 22, 'us': 2} sectors={'Financials': 24}
v718_eval_b02: n=14 univ={'eu': 6, 'us': 8} sectors={'Financials': 14}
v718_eval_b03: n=13 univ={'eu': 7, 'us': 6} sectors={'Industrials': 13}
v718_eval_b04: n=11 univ={'us': 6, 'eu': 5} sectors={'Industrials': 11}
v718_eval_b05: n=10 univ={'us': 10} sectors={'Information Technology': 10}
v718_eval_b06: n=8 univ={'eu': 2, 'us': 6} sectors={'Information Technology': 8}
v718_eval_b07: n=8 univ={'eu': 3, 'us': 5} sectors={'Health Care': 8}
v718_eval_b08: n=10 univ={'eu': 2, 'us': 8} sectors={'Consumer Discretionary': 8, 'Communication Services': 2}
v718_eval_b09: n=10 univ={'eu': 5, 'us': 5} sectors={'Consumer Staples': 4, 'Materials': 5, 'Energy': 1}
v718_eval_b10: n=13 univ={'us': 10, 'eu': 3} sectors={'Real Estate': 6, 'Utilities': 7}
Total evaluated in b01..b10: 121
Sub-industries split across >1 batch: {}
Sectors across >1 batch: {'Financials': ['v718_eval_b01', 'v718_eval_b02'], 'Industrials': ['v718_eval_b03', 'v718_eval_b04'], 'Information Technology': ['v718_eval_b05', 'v718_eval_b06']}
Unique rationales: 121 / 121
Min rationale len: 171 Max: 1656
```

### 3. Independent Command Outputs
`python3 screener/bulk_scorer.py --audit` (exit `0`):
```text
======================================================================
QUALITY & MOAT SCREENER — GATE 3 COMPLIANCE AUDIT (v7.18)
======================================================================
Gate 3 Populations: {'us': 445, 'eu': 495, 'ca': 49} | Total: 989 / 989
[✓] Gate 3 Candidate Count Target: PASSED
[✓] 11 Reference Companies Verified: PASSED

Scoring Status: 989 scored / 0 unscored
[✓] Deterministic CAP Formulas: 0 discrepancies
[✓] Gate 3a Primary Moat Alignment: 0 discrepancies
[✓] Mandatory 4n Runway Notes: 0 missing
[✓] Sequential Munger Waterfall (Stage 1): 0 violations
[✓] Stage 2 Diagnostic G5/G6 (485 moat franchises): 0 missing/invalid
[✓] Calamity Pass Rules: 0 violations
[✓] Dual-Listed Mirror Parity: PASSED
======================================================================
```

`python3 build.py` (exit `0`):
```text
Compiling Quality & Moat Screener HTML Cockpit for: ca, eu, us...

✓ Dashboard built in 3.36s:
  • File: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/output/screener.html
  • Secondary File: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/output/index.html
  • GitHub Pages File: docs/index.html
  • Total Companies: 1175
  • Prime Grade: 225
  • Prime Grade Calamity (Conditional): 11
  • Valued Prime Grade: 220 (Median IRR vs hurdle: -12.0pp)
```

`python3 -m unittest discover -s tests -v` (exit `0`):
```text
Ran 319 tests in 23.545s

OK
```
