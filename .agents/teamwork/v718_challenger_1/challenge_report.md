# Challenge Report — v7.18 Engine & Dashboard Runtime (`v718_challenger_1`)

## Challenge Summary

**Verdict**: **REJECT** (Targeted Engine Bug in R1 Waterfall State Machine; Data, Built HTMLs, JS Runtime & 319 Unit Tests Pass)  
**Overall risk assessment**: **MEDIUM**

All current repository datasets (`data/{us,eu,ca}/inputs.csv`), `python3 screener/bulk_scorer.py --audit`, `python3 -m unittest discover -s tests` (319/319), `output/screener.html` / `output/index.html` / `docs/index.html` parity, and JavaScriptCore (`osascript -l JavaScript`) runtime checks of `openDrawer`, `renderTable`, and `sortData` **PASS**.

However, empirical adversarial testing uncovered a **confirmed Stage 1/Stage 2 Waterfall state-machine bug** in both `screener/apply_evaluation.py` (`validate_and_waterfall`) and `screener/bulk_scorer.py` (`validate_company_evaluation`): when a payload supplies `3b="N"` + `calamity="Y"` + `CAP < 15` (with diagnostic `5`/`6`), `CAP < 15` clears `calamity="Y"` (leaving `3b="N"` unwaived) **without** triggering the Stage 1 Gate 3b downstream scrub. `ingest_evaluations` accepts the payload with `errors=[]`, and `audit_gate_3_universe()` immediately fails with `waterfall_violations`.

---

## Challenges

### [Medium] Challenge 1 — `3b="N"` + `calamity="Y"` + `CAP < 15` Leaves Orphaned Downstream Fields (Breaks `ingest_evaluations` → `audit_gate_3_universe` Invariant)

- **Assumption challenged**: Checking Stage 1 (`3b == "N" and not calamity`) *before* Stage 2 (`CAP < 15` clearing `calamity`) was implicitly assumed to keep Stage 1 and Stage 2 decoupled.
- **Attack scenario**: An evaluation (or analyst update) submits `1="Y"`, `2="Y"`, `3a="Toll booth & switching costs"`, `3b="N"`, `calamity="Y"`, `calamity_note="Temporary 3b dip"`, and Gate 4 forces yielding `4=10` (`CAP < 15`), plus `5=1`, `6="Y"`.
  - In `screener/apply_evaluation.py:266-282` (`validate_and_waterfall`) and `screener/bulk_scorer.py:586-626` (`validate_company_evaluation`), `3b="N"` passes Stage 1 because `calamity` is `"Y"`.
  - Stage 2 then sees `4 < 15` and clears `calamity=""` and `calamity_note=""`.
  - Neither function re-evaluates Stage 1 after clearing `calamity`, so `4_*`, `4`, `4n`, `5`, `6` remain populated alongside `3b="N"` and `calamity=""`.
- **Empirical reproduction**:
  - Ran `bs.ingest_evaluations(...)` against a temporary copy of `data/` for `NVDA` with `3b="N"`, `calamity="Y"`, `4=10`, `5=1`, `6="Y"`.
  - `ingest_evaluations` returned `{'applied': 1, 'rejected': 0, 'errors': [], 'warnings': ["[NVDA] Waterfall: cleared 'calamity' because Gate 4 CAP (10Y) < 15 (non-waivable anchor).", "[NVDA] Waterfall: cleared 'calamity_note' because Gate 4 CAP (10Y) < 15 (non-waivable anchor)."]}`.
  - Subsequent `audit_gate_3_universe()` failed with: `waterfall_violations: ["[NVDA] Failed Gate 3 but downstream keys ['4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6'] are not blank"]`.
- **Blast radius**: Zero impact on the current 989 committed rows (`--audit` has 0 violations), but breaks the ingestion-to-audit invariant for any future payload where a calamity-waived `3b="N"` company also fails Gate 4 `CAP < 15`.
- **Mitigation**: After clearing `calamity` due to `CAP < 15` in both `validate_and_waterfall` (`apply_evaluation.py`) and `validate_company_evaluation` (`bulk_scorer.py`), if `g3b == "N"`, run the Stage 1 Gate 3b downstream scrub (`*FORCE_SCORE_CODES, "4", "4n", "5", "6"`).

### [Low] Challenge 2 — Non-Integer Float in Standalone Gate 4 (`apply_evaluation.py:226`)

- **Assumption challenged**: `int(qual["4"]) in CAP_VALUES` validates standalone `4` values.
- **Attack scenario**: Passing standalone `"4": 15.5` (without `4_ent..4_sub`) to `apply_evaluation.validate_and_waterfall` evaluates `int(15.5) == 15 in CAP_VALUES`, emitting 0 warnings and leaving `qual["4"] = 15.5` (which `sanitize_val` serializes as `"15.5"`).
- **Blast radius**: Low — `bulk_scorer.validate_company_evaluation` and `audit_gate_3_universe` reject non-integer `"15.5"`, and normal runs compute `4` deterministically from `4_ent..4_sub`.
- **Mitigation**: Check `not isinstance(qual["4"], bool)` and `int(qual["4"]) == float(qual["4"])` in `apply_evaluation.py:226`.

---

## Stress Test Results

| Area | Scenario | Expected | Actual | Result |
|---|---|---|---|---|
| Unit & E2E Suite | `python3 -m unittest discover -s tests` | All tests pass | `Ran 319 tests in 24.061s — OK` | **PASS** |
| Bulk Audit | `python3 screener/bulk_scorer.py --audit` | 0 discrepancies, 485 Stage 2, mirror parity | `989/989`, `485 moat franchises`, `0` violations, `PASSED` | **PASS** |
| Data Immutability | `git show HEAD:data/{us,eu,ca}/inputs.csv` diff on Gates 1–4 & calamity | 0 Gate 1–4/calamity changes; 121 rows updated | `121` rows changed, `0` changes in Gate 1–4/calamity cols | **PASS** |
| Notes & `CRM` | Check 485 Gate-3-advancing notes & `CRM` | 0 stale waterfall sentences; 121 `[Diagnostic G5=...]` tags; `CRM` `CAP = 5Y` | `0` stale sentences, `0` missing/mismatched tags, `CRM` `4=5, 5=0, 6=Y` and `CAP = 5Y` in `note` | **PASS** |
| Stage 1 Scrubbing | `1="N"`, `2="N"`, `3a="None"`, unwaived `3b="N"` with `5`/`6` supplied | Strictly scrub `4_*`, `4`, `4n`, `5`, `6` | Both `apply_evaluation` and `bulk_scorer` scrubbed cleanly | **PASS** |
| Stage 2 `CAP < 15` + Calamity | `3b="Y"`, `4=10`, `calamity="Y"`, `5=2`, `6="Y"` | Clear `calamity`/`calamity_note`; preserve `5`/`6`; `phase_results` rejects Gate 4 | Cleared `calamity`, preserved `5=2, 6='Y'`, `Rejected – G4 Runway (<15Y)` | **PASS** |
| **Stage 1/2 Interaction** | **`3b="N"` + `calamity="Y"` + `4=10`, `5=1`, `6="Y"`** | **Either scrub `4..6` after `calamity` cleared, or reject** | **`ingest_evaluations` applied (`errors=[]`); `audit_gate_3_universe` failed with `waterfall_violations`** | **FAIL (BUG)** |
| Stage 2 `5=0` | `5=0`, `6="N"`, no calamity | Preserve `6="N"`, `phase_results` rejects Gate 5 | Preserved `6="N"`, `Rejected – G5 Management` | **PASS** |
| Invalid `5` & `6` | `5` in `{-1, 3, True, False, "abc", 1.5, "1.5"}`; `6` in `{"Yes", "X", 1, 0, True, "y", "n", "N/A"}` | `apply_evaluation` clears + warns; `bulk_scorer` errors | All rejected/cleared as expected | **PASS** |
| Blank `5`/`6` on G3-advancing | Blank `5` or `6` on Gate-3 passer | `validate_company_evaluation` warns; `audit` fails | Warnings emitted; temp `DATA_DIR` audit caught `['[CRM] 5 is blank']` | **PASS** |
| Built HTML Parity & Version | `output/screener.html`, `output/index.html`, `docs/index.html` | Byte-identical, `version="7.18"`, `"7.18"` changelog, Prime=225, Cal=11/13 | Byte-identical (`cmp -s`), `version="7.18"`, `"7.18"` changelog present, Prime=`225`, Cal=`13` total / `11` `<3` flags | **PASS** |
| JSC `openDrawer` Runtime | `osascript -l JavaScript` on `COST`, `MSFT`, `EL`, `APD`, `DGE.GB`, `CRM`, `BA`, `NUE` | Exact stepper sub-labels, `WAIVED` preserved, `#dossier-g56-row`, `#dossier-g6-answer`, no `0` falsiness bug | All 8 companies asserted cleanly (`BA` `FAIL · 0/2` & `FAIL · N`; `CRM` `FAIL · 5Y`/`0/2`/`PASS · Y`; `EL`/`APD`/`DGE.GB` `WAIVED`; `NUE` hidden) | **PASS** |
| JSC `renderTable` & `sortData` | Compact vs expanded columns across `qpass`, `calamity`, `moat_universe`, `all`; sort by `g5_mgmt`, `g6_cash` | `G5 Mgmt`/`G6 B/S` only in expanded `moat_universe` & `all`; `0` sorts properly with nulls last | All 8 tab/density combinations and `g5_mgmt`/`g6_cash` sorts passed | **PASS** |

---

## Unchallenged Areas

- Browser-visual CSS layout/responsiveness (width/overflow of the 2-card `#dossier-g56-row` or horizontal scroll of expanded tables at 375px/1280px) was not rendered in a live headless browser (verified via HTML/DOM structure and JavaScriptCore controller execution).
- Individual qualitative investment judgment quality across the 121 company notes (covered by peer-cohort/spec verification; only structural completeness, G5/G6 tag parity, and Gate 1–4 immutability were verified here).
