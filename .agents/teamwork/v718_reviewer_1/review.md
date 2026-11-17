# Independent Review & Adversarial Challenge Report — v7.18

## Review Summary

**Verdict**: APPROVE

All v7.18 requirements across R1 (`screener/apply_evaluation.py`, `screener/bulk_scorer.py`), R3 (`screener/dashboard.py`, `screener/config.py`, `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`), R4 (`tests/test_calamity_tier.py`, `tests/test_bulk_scoring_e2e.py`, `tests/test_v718_two_stage_waterfall.py`), and all build/audit/test acceptance criteria have been independently verified and pass cleanly with zero integrity violations.

---

## Verified Claims

| Claim / Requirement | Verification Method | Result |
|---|---|---|
| R1 Stage 1 scrubbing (`1="N"`, `2="N"`, `3a="None"`, unwaived `3b="N"`) remains strict | Inspected `screener/apply_evaluation.py:246-273` and `screener/bulk_scorer.py:574-592`; executed `unittest` | PASS |
| R1 Stage 2 preserves `5` and `6` on `CAP < 15` and `6` on `5 = 0` without calamity, clears `calamity` on `CAP < 15`, rejects `bool`/non-int/out-of-range `5` and invalid `6`, warns on blank `5`/`6` past G3 | Inspected `screener/apply_evaluation.py:157-175,274-295` and `screener/bulk_scorer.py:512-526,617-656`; verified via `tests/test_calamity_tier.py` and `tests/test_v718_two_stage_waterfall.py` | PASS |
| R1 `audit_gate_3_universe` enforces blank `G4-G6` on 504 G3 failures, valid non-empty `5`/`6` on 485 G3 passers, exits non-zero on audit failures, and `REFERENCE_SNAPSHOT["CRM"]` matches `data/us/inputs.csv` | Inspected `screener/bulk_scorer.py:201-210,1059-1085,1235-1248`; ran `python3 screener/bulk_scorer.py --audit` (exit 0) and CSV inspection | PASS |
| R2/Funnel invariance (`1175` total, `989` G3, `485` advancing [`483` `3b="Y"` + `EL`, `APD`], `504` G3 rejects, `121` modified rows in `us`/`eu`, `0` in `ca`, G1–G4 & `calamity` & prior `5=0` 100% unchanged vs `HEAD`) | Python diff script comparing `git show HEAD:data/{us,eu,ca}/inputs.csv` against current CSVs + `collect_screener_data` check | PASS |
| R3 `screener/dashboard.py` stepper sub-labels (`PASS · 30Y`, `FAIL · 5Y`, `PASS · 2/2`, `FAIL · 0/2`, `PASS · Y`, `FAIL · N`, preserving `WAIVED`, safe `0` check), `#dossier-g56-row` 2-card row, `#dossier-g6-answer` population, `g5_mgmt`/`g6_cash` in `ALL_COLS` and expanded `moat_universe`/`all` only (`compactKeys`, `qpass`, `calamity` unchanged) | Inspected `screener/dashboard.py:2172-2181,2654-2655,2690-2691,3133-3160,3278-3292,3640-3648,3676-3712,3807`; verified live JavaScriptCore execution in `tests/test_v718_two_stage_waterfall.py` | PASS |
| R3 `SCREENER_VERSION = "7.18"` and `"7.18"` `CHANGELOG` entry | Inspected `screener/config.py:332,708-718` | PASS |
| R3 Two-Stage Waterfall docs & `CRM` Example 4 | Inspected `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` (including `CRM` Example 4 at lines 546-587) | PASS |
| Build & Output Parity (`output/screener.html`, `output/index.html`, `docs/index.html`, Prime Grade `225`, Prime Grade Calamity `11` / `13` total `calamity="Y"`) | Ran `python3 build.py` (exit 0, 3.04s) and `shasum -a 256` (identical `aa8e764c...` across all 3 HTML outputs) | PASS |
| Full Test Suite (`tests/`) | Ran `python3 -m unittest discover -s tests` (`Ran 319 tests in 23.131s`, `OK`) | PASS |

---

## Findings

### [Minor] Finding 1: Secondary Stage 1 Scrub Gap When `3b="N"`, `calamity="Y"`, and `CAP < 15` Co-Occur in an Input Payload

- **What**: When a synthetic evaluation payload supplies `gate_3b_pricing_and_proof="N"`, `calamity_flag="Y"`, AND `gate_4_runway_cap < 15`, both `validate_and_waterfall` (`screener/apply_evaluation.py:266-282`) and `validate_company_evaluation` (`screener/bulk_scorer.py:586-625`) pass the Stage 1 Gate 3 check (because `calamity == "Y"`), then clear `calamity`/`calamity_note` on `4 < 15`, leaving `3b="N"` unwaived alongside non-blank `4_*`, `4`, `4n`, `5`, and `6`.
- **Where**: `screener/apply_evaluation.py:266-282`, `screener/bulk_scorer.py:586-625`
- **Why**: Clearing `calamity` after Gate 3 evaluation retroactively makes `3b="N"` an unwaived Stage 1 Gate 3 failure, which `audit_gate_3_universe` flags as a `waterfall_violation` if persisted. Confirmed via direct invocation in Python (`calamity=""`, `3b="N"`, `4=10`, `5=1`, `6="Y"`).
- **Impact**: Low / non-blocking — 0 rows in `data/{us,eu,ca}/inputs.csv` have this combination (confirmed by `--audit`), and `audit_gate_3_universe` catches it if ever introduced.
- **Suggestion**: In a future cleanup, if `calamity` is cleared because `4 < 15` while `g3b == "N"`, re-run Stage 1 Gate 3 downstream scrubbing of `[*FORCE_SCORE_CODES, "4", "4n", "5", "6"]`.

### [Minor] Finding 2: CSV Export (`exportCurrentView`) Does Not Include `G5 Mgmt` / `G6 B/S` Columns

- **What**: `exportCurrentView()` in `screener/dashboard.py:4703-4745` exports a hardcoded header list ending at `FCF Conv` and does not include `G5 Mgmt` or `G6 B/S`.
- **Where**: `screener/dashboard.py:4703-4745`
- **Why**: R3 explicitly scoped `g5_mgmt` and `g6_cash` to `ALL_COLS` in expanded table mode on Quality Grade and Full Universe, so this is compliant with R3, though analysts exporting Full Universe CSVs won't see G5/G6 in the downloaded CSV.
- **Suggestion**: Optionally add `G5 Mgmt` and `G6 B/S` to `exportCurrentView()` in a future release if CSV parity with expanded table columns is desired.

---

## Adversarial Challenge Summary

**Overall risk assessment**: LOW

### Challenges Evaluated

1. **JS Falsy `0` Trap in `dashboard.py` (`g5_mgmt = 0`)**:
   - **Assumption challenged**: `0` in JS is falsy (`!c.g5_mgmt` would hide `0/2` Red Flag scores).
   - **Verification**: Inspected `screener/dashboard.py:3279,3643,3676` (`!== null && !== undefined && !== ''`) and `sortData` lines `2995-2997`. Confirmed `BA` (`5=0`) renders `FAIL · 0/2` in stepper, `0/2 — Red Flag` in `#dossier-g5-mgmt`, and `0/2` badge in expanded table via live JavaScriptCore execution. **ROBUST**.
2. **Python `bool` Subclass of `int` (`True == 1` in `{0, 1, 2}`)**:
   - **Assumption challenged**: In Python, `isinstance(True, int)` is `True` and `True in {0, 1, 2}` is `True`.
   - **Verification**: Inspected `_parse_subscore` (`screener/apply_evaluation.py:161`) and `_parse_score` (`screener/bulk_scorer.py:516`) — both explicitly guard `if isinstance(raw, bool):` before `int(raw)` and reject `1.5` via `iv == float(raw)`. Confirmed via `tests/test_v718_two_stage_waterfall.py:146-161`. **ROBUST**.
3. **Core Funnel & Prime Grade Invariance**:
   - **Assumption challenged**: Populating `5` and `6` on the 121 Stage-2 rejected rows might alter `phase_results`, `thr_cap = 15`, Prime Grade (`225`), or Prime Grade Calamity (`11` / `13` total `calamity="Y"`).
   - **Verification**: Verified `screener/gates.py` is completely unmodified, `phase_results` still rejects at Gate 4 (`4 < 15`) or Gate 5 (`5 = 0` without calamity), and `build.py` + `collect_screener_data` report `Total Companies: 1175`, `Prime Grade: 225`, `Prime Grade Calamity (Conditional): 11`, `calamity_flag == "Y"` = `13` (`EL` and `RTX` have `g6_flags == 3`). **ROBUST**.
4. **Dual-Listed Mirror Parity & Gate 1–4 Immutability**:
   - **Assumption challenged**: Batch ingestion into `data/{us,eu}/inputs.csv` could have drifted `ASML`/`ASML.NL`, `FER`/`FER.ES`, or mutated Gate 1–4 / prior `5=0` values.
   - **Verification**: `git show HEAD:data/{us,eu,ca}/inputs.csv` diff check proved `66` US rows and `55` EU rows (`121` total, `0` CA) changed only in `5`, `6`, `note` (and `evidence` if any), with 100% exact equality on all Gate 1–4 and calamity columns across all `1,175` rows and all prior `5=0` rows preserved. `--audit` confirmed `Dual-Listed Mirror Parity: PASSED`. **ROBUST**.

---

## Coverage Gaps

- None for R1, R3, R4, build, audit, and test suite. (R2 qualitative rationale content across all 121 companies was audited structurally and for G1–4/`5=0`/calamity invariance; company-by-company financial prose accuracy was outside this dispatch's R1/R3/R4 review scope and handled by the dedicated R2 evaluation/audit track.)

## Unverified Items

- None within assigned scope.
