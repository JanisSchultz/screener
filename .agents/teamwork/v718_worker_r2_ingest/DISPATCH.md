# Dispatch — v718_worker_r2_ingest (R2 Ingestion, Note Cleanup, CRM Snapshot/Spec Sync, Audit & Build)

## 2026-11-17T15:54:00Z
Assigned Role: `teamwork_worker` (R2 Ingestion & Final Integration)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_worker_r2_ingest`

## Exclusive File Ownership
Modify ONLY:
- `data/us/inputs.csv`
- `data/eu/inputs.csv`
- `screener/bulk_scorer.py` (`REFERENCE_SNAPSHOT["CRM"]` ONLY — update `"5"` and `"6"` to match `CRM`'s verified M2 evaluation; leave all other 10 reference companies untouched!)
- `COMPANY_EVALUATION_SPEC.md` (Example 4 `CRM` ONLY — replace `<pending M2 verification>` placeholders with `CRM`'s verified `"5"`, `"6"`, and `[Diagnostic G5=... | G6=...: ...]` note!)
- `output/screener.html`, `output/index.html`, `docs/index.html` (exclusively via running `python3 build.py`)

DO NOT modify `data/ca/inputs.csv`, `screener/apply_evaluation.py`, `screener/gates.py`, `screener/dashboard.py`, `screener/config.py`, `QUALITATIVE_EVALUATION_SPEC.md`, or `tests/`.

## Exact Tasks
1. **Load & Validate All 10 Evaluator Payloads**:
   - Read `.agents/teamwork/v718_eval_b01/evaluations.json` through `v718_eval_b10/evaluations.json` (handle both top-level JSON `list` and `dict["evaluations"]`).
   - Verify total count == **121** unique `(universe, id)` entries (**66** US + **55** EU + **0** CA), matching every one of the 108 Gate-4 rejects + 13 Gate-5 rejects.
   - Verify all 13 Gate-5 rejects (`US:BA`, `EU:ADP.FR`, `US:INTU`, `US:PANW`, `US:ROP`, `EU:DIM.FR`, `EU:SRT3.DE`, `EU:ABI.BE`, `US:CSGP`, `US:CCI`, `US:ES`, `US:SO`, `US:D`) preserve `5 == 0` (`is_g5_reject == True`).
   - Verify all 31 `g6_default == "N"` companies (24 Banks + 7 Utilities) have `6 == "N"`.
2. **Ingest via Two-Stage Waterfall Engine (`validate_and_waterfall` / `validate_company_evaluation`) & Update `data/{us,eu}/inputs.csv`**:
   - For each of the 121 rows:
     - Validate `(5, 6)` through `validate_and_waterfall` / `validate_company_evaluation` (confirm 0 warnings/errors and Gate 1–4 columns `1, 2, 2r, 3_tb, 3_ia, 3_se, 3_rd, 3a, 3b, 3m, 4_ent, 4_riv, 4_buy, 4_sup, 4_sub, 4, 4n, calamity, calamity_note, evidence` remain **100% character-for-character identical** to pre-ingest!).
     - Set column `"5"` (`str(item["5"])`) and column `"6"` (`item["6"]`).
     - Update `"note"` on ALL 121 rows:
       - If `"updated_note"` is already provided in the item, verify it preserves the original core note (except `CRM`'s `CAP = 10` fix), has zero waterfall-bypass sentences, and ends with `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`.
       - Otherwise, start from the existing `inputs.csv` `"note"`, strip any sentence matching `re.sub(r'\s*Downstream\s+(?:gates?|Gates?\s+(?:5-6|6))\s+bypassed\s+per\s+(?:strict\s+)?waterfall\.', '', note, flags=re.IGNORECASE).strip()`, for `US:CRM` specifically fix stale `CAP = 10` / `haircut to CAP 10` prose to `CAP = 5Y` / `haircut to CAP 5`, and append ` [Diagnostic G5=<0|1|2> | G6=<Y|N>: <diagnostic_rationale>]` (ensure single clean space before `[Diagnostic ...]` and no double periods/whitespace).
     - Double-check zero rows outside the 121 are modified in `data/{us,eu,ca}/inputs.csv`.
3. **Sync `CRM` in `REFERENCE_SNAPSHOT` and `COMPANY_EVALUATION_SPEC.md` Example 4**:
   - Update `REFERENCE_SNAPSHOT["CRM"]` in `screener/bulk_scorer.py` with `CRM`'s verified `"5"` and `"6"` values (`0` / `Y` from `v718_eval_b05`, or exact verified payload values).
   - Update `COMPANY_EVALUATION_SPEC.md` Example 4 (`CRM`) replacing any pending M2 placeholders with `CRM`'s verified `"5"`, `"6"`, and `[Diagnostic G5=... | G6=...: ...]` note.
4. **Run Full Verification Suite**:
   - `python3 screener/bulk_scorer.py --audit` -> MUST exit `0` (`0` discrepancies, `0` Stage 1 violations, `0` Stage 2 missing/invalid across 485 moat franchises, `11 Reference Companies Verified: PASSED`, `Dual-Listed Mirror Parity: PASSED`).
   - `python3 build.py` -> MUST exit `0` (`Total Companies: 1175`, `Prime Grade: 225`, `Prime Grade Calamity (Conditional): 11`).
   - `python3 -m unittest discover -s tests` -> MUST exit `0` (`319/319 OK`).

## Integrity Warning (MANDATORY)
DO NOT CHEAT. Do NOT alter Gate 1–4 scores or fabricate any field. Verify every row diff programmatically.

## Deliverables
Write `progress.md`, `changes.md`, and `handoff.md` in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_worker_r2_ingest`, and report completion to `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
