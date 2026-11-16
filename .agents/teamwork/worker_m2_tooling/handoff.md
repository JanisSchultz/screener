# Milestone M2 Tooling Completion Report: Bulk Scoring Engine (`screener/bulk_scorer.py`)

**Worker**: `worker_m2_tooling`  
**Milestone**: M2  
**Date**: 2026-11-16  
**Artifact Created**: `screener/bulk_scorer.py`  
**Test Suite**: `.agents/teamwork/worker_m2_tooling/test_bulk_scorer.py`  

---

## 1. Observation

1. **Exact Gate 3 Universe Population**:
   - Querying `data/{us,eu,ca}/inputs.csv` for companies with `1 == 'Y'` and `2 == 'Y'` yields exactly **989 companies**:
     - **US**: 445 companies (out of 515)
     - **EU**: 495 companies (out of 602)
     - **CA**: 49 companies (out of 58)
     - Total: $445 + 495 + 49 = 989$.
   - Among these 989 companies, exactly **11 reference companies** have complete qualitative sub-scores (`3_tb`, `3_ia`, `3_se`, `3_rd`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`), while **978 companies** are unscored legacy rows awaiting M3 evaluation.

2. **11 Phase 1 Reference Companies**:
   - Verified that `SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, and `NUE` retain their exact verified scores:
     - `SPGI`: `3_tb=2, 3_ia=2, 3_se=0, 3_rd=0, 3a="Toll booth & switching costs", 3b="Y", 4=30, 5=1, 6="Y"`
     - `COST`: `3_tb=1, 3_ia=1, 3_se=2, 3_rd=0, 3a="Scale economies shared", 3b="Y", 4=30, 5=2, 6="Y"`
     - `ASML` / `ASML.NL`: `3_tb=2, 3_ia=2, 3_se=0, 3_rd=2, 3a="R&D & innovation leadership", 3b="Y", 4_buy=1, 4_sup=1, 4=25, 5=2, 6="Y"`
     - `MSFT`: `3_tb=2, 3_ia=2, 3_se=0, 3_rd=1, 3a="Toll booth & switching costs", 3b="Y", 4_riv=1, 4_sub=1, 4=25, 5=1, 6="Y"`
     - `WM`: `3_tb=1, 3_ia=2, 3_se=0, 3_rd=0, 3a="Irreplaceable infrastructure & intangibles", 3b="Y", 4=25, 5=1, 6="Y"`
     - `RMS.FR`: `3_tb=1, 3_ia=2, 3_se=0, 3_rd=0, 3a="Irreplaceable infrastructure & intangibles", 3b="Y", 4=25, 5=2, 6="Y"`
     - `CNR.CA`: `3_tb=1, 3_ia=2, 3_se=0, 3_rd=0, 3a="Irreplaceable infrastructure & intangibles", 3b="Y", 4_sup=1, 4=20, 5=1, 6="Y"`
     - `HSY`: `3_tb=0, 3_ia=2, 3_se=0, 3_rd=0, 3a="Irreplaceable infrastructure & intangibles", 3b="Y", 4_buy=1, 4_sup=1, 4=15, 5=1, 6="Y"`
     - `CRM`: `3_tb=2, 3_ia=0, 3_se=0, 3_rd=0, 3a="Toll booth & switching costs", 3b="Y", 4_ent=1, 4_riv=1, 4_buy=1, 4_sub=2, 4=5, 5="", 6=""`
     - `NUE`: `3_tb=0, 3_ia=0, 3_se=0, 3_rd=0, 3a="None", 3b="N", 4_*="", 4="", 4n="", 5="", 6=""`
   - Every reference company has 0 discrepancies against formula rules and 100% verified status.

3. **Critical Architectural Directive**:
   - Sentinel / parent message (`2026-11-16T10:50:53Z`): Qualitative scores must NOT be fabricated via mechanical keyword/regex or sector tables. `bulk_scorer.py` serves as the robust **batch context-exporter, deterministic CAP/waterfall batch-ingester, validator, and mirror synchronizer** for M3 parallel evaluator agents.

4. **Engine Implementation in `screener/bulk_scorer.py`**:
   - `get_gate_3_companies()`: filters Gate 3 candidates and enriches with financial statement history and clock-speed indicators.
   - `REFERENCE_SNAPSHOT` & `verify_reference_companies()`: hardcoded immutable reference baseline and active guard preventing accidental mutation.
   - `is_fast_clock_speed()`: identifies fast clock-speed sub-industries where presumptive `4_sub >= 1` applies under Mauboussin outside-view rules.
   - `export_batch_context()`: generates structured JSON dossiers (identity, current qualitative values, 5-10Y financials, sales CAGRs) in batches of 20-25 for M3 evaluators.
   - `validate_company_evaluation()`: enforces deterministic Initial CAP (`compute_initial_cap_from_scores`), derived primary moat (`3a`), deterministic Final CAP (`compute_final_cap_from_scores`), mandatory `4n` notes when forces $\ge 1$, Munger waterfall clearing (downstream cleared on Gate 3 or Gate 4 fail), and calamity validation.
   - `ingest_evaluations()`: ingests evaluation payloads from files or directories, supports `--dry-run` and `--apply` atomic writes.
   - `sync_mirrors()`: enforces 100% field parity across dual-listed pairs (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`).
   - `audit_gate_3_universe()`: validates count targets, reference companies, formula parity, note presence, waterfall integrity, and mirror parity.

5. **Test Results**:
   - Unit test suite `.agents/teamwork/worker_m2_tooling/test_bulk_scorer.py`: 8 tests, 100% passing in 0.206s.
   - Full test suite `python3 -m unittest discover tests`: 303 tests, 100% passing in 14.75s.

---

## 2. Logic Chain

1. **Adherence to Core Specifications**:
   - Under `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`, evaluation proceeds through sequential Munger reject gates.
   - Step 1 Moat Profile (`3_tb`, `3_ia`, `3_se`, `3_rd`) produces deterministic Initial CAP (0Y, 15Y, 20Y, 25Y, 30Y) and derives primary moat label `3a`. If all moat scores are zero, `3a = "None"`, Initial CAP = 0Y, and Gate 3 fails immediately, clearing all downstream fields.
   - Step 2 Competitive Forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`) produces deterministic Final CAP (`4`): moderate haircut $h(c_1)$ and Fatal-Flaw Cap ($c_2 \ge 1 \implies \le 10\text{Y}$). Manual overrides are strictly impossible.
   - When Final CAP $< 15$, the company fails Gate 4 and downstream Gates 5–6 are cleared. When Final CAP $\ge 15$, Gates 5 and 6 must be populated to prevent the company from being trapped in `"To review (blank gate)"`.

2. **Decoupled Architecture for Quality**:
   - By creating `export_batch_context()` and `ingest_evaluations()`, `bulk_scorer.py` enables Milestone M3 to dispatch parallel domain evaluators across sector cohorts without using brittle regex heuristics.
   - The engine validates every payload before write, ensuring that invalid scores, missing `4n` notes, or broken waterfall invariants are caught immediately.

3. **Mirror Parity Mechanics**:
   - `data/us/universe.json["mirror"]` designates `eu:ASML.NL` as the source for `us:ASML` and `eu:FER.ES` as the source for `us:FER`.
   - `sync_mirrors()` compares all 20 qualitative columns (`3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`, `3b`, `3m`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`, `calamity`, `calamity_note`, `note`, `evidence`) and synchronizes US mirror listings from EU primary listings, satisfying Acceptance Criteria R2.

---

## 3. Caveats

1. **Inputs.csv Preservation**:
   - Per explicit instructions, no changes were committed to `data/{us,eu,ca}/inputs.csv` during M2 (`--apply` was tested only in mock/temp contexts; universe files remain unmodified).
2. **Mirror Parity Pre-M3 State**:
   - Currently in `data/us/inputs.csv`, `ASML` and `FER` exhibit slight textual differences in narrative `note` and `evidence` relative to `ASML.NL` and `FER.ES`. Running `bulk_scorer.py --sync-mirrors --apply` in M3 will bring both pairs into 100% character-for-character equality.
3. **Calamity Tier Guard**:
   - Calamity flag `Y` is strictly guarded by Anchor Gates 1, 2, 3a, 4. If any company shifts in M3 such that an Anchor Gate fails, the waterfall engine automatically strips the calamity flag and note.

---

## 4. Conclusion

1. **Tooling Readiness**: `screener/bulk_scorer.py` is fully implemented, verified, and operational.
2. **Integrity Verified**: Zero hardcoded outputs or heuristic shortcuts. Clean batch context exporter and deterministic ingester/validator implemented.
3. **Reference Baseline Protected**: 11 reference companies are guarded against modification.
4. **All Tests Passing**: 303/303 repository tests and 8/8 new unit tests pass cleanly. Milestone M2 is complete and ready for Milestone M3.

---

## 5. Verification Method

To independently verify the tooling and audit functionality:

1. **Run Bulk Scorer Compliance Audit**:
   ```bash
   python3 screener/bulk_scorer.py --audit
   ```
   *Expected Output*: Displays Gate 3 count (989 / 989: US 445, EU 495, CA 49), verified status for 11 reference companies, and 0 formula discrepancies.

2. **Verify Tooling Unit Tests**:
   ```bash
   python3 .agents/teamwork/worker_m2_tooling/test_bulk_scorer.py
   ```
   *Expected Output*: `Ran 8 tests in ~0.2s. OK`

3. **Verify Dry-Run Batch Export**:
   ```bash
   python3 screener/bulk_scorer.py --export-batch --out-dir /tmp/test_batches --batch-size 25
   ```
   *Expected Output*: Exports 40 JSON batch dossiers for the 978 unscored companies.

4. **Verify Full Test Suite**:
   ```bash
   python3 -m unittest discover tests
   ```
   *Expected Output*: `Ran 303 tests. OK`
