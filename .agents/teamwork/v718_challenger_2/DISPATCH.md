# Dispatch — v718_challenger_2 (Empirical Challenger: Universe Data, Invariance, Mirror Parity & 121-Row Audit)

## 2026-11-17T16:02:00Z
Assigned Role: `teamwork_challenger` (Empirical Adversarial Verification — Universe Data, Funnel Invariance & Note Audit)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request (MUST read verbatim first): `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_challenger_2`

## Strictly Read-Only Scope
Do NOT modify repository files! Write and run independent Python verification scripts against `data/{us,eu,ca}/inputs.csv`, `git diff`, `screener/gates.py`, and `screener/bulk_scorer.py --audit` to empirically verify:
1. **Zero Gate 1–4 Mutation & Zero Unintended Row Edits (`git diff HEAD -- data/`)**:
   - Verify via `git show HEAD:data/{us,eu,ca}/inputs.csv` vs working tree that ONLY the exact 121 incomplete moat franchises (`66` US + `55` EU + `0` CA) changed, and ONLY columns `5`, `6`, `note` changed on those 121 rows (zero changes to `1, 2, 2r, 3_*, 3a, 3b, 3m, 4_*, 4, 4n, calamity, calamity_note, evidence`).
   - Verify all 13 Gate-5 rejects kept `5 == "0"`.
   - Verify all 364 already-completed moat franchises and all 690 Stage 1 rejects (30 G1 + 156 G2 + 504 G3) are 100% untouched byte-for-byte!
2. **Funnel & Prime Grade Invariance**:
   - Compute `phase_results` across all `1,175` companies: `989` Gate 3, `485` Gate-3 advancing (`483` `3b="Y"` + `EL`, `APD`), `504` Gate-3 rejects, `225` Prime Grade, `13` total / `11` `<3` G6-flag Prime Grade Calamity, `0` `To review`, `thr_cap = 15`.
3. **Note Hygiene & `CRM` Sync**:
   - Verify zero occurrences of `"Downstream gates bypassed..."` (any variant) across all 121 newly completed rows, valid `[Diagnostic G5=<0|1|2> | G6=<Y|N>: ...]` on all 121, `CRM` note reflects `CAP = 5Y` (no `CAP = 10`), and `REFERENCE_SNAPSHOT["CRM"]` + `COMPANY_EVALUATION_SPEC.md` Example 4 match `data/us/inputs.csv` `CRM`.
4. **Cross-Check Quantitative Claims in Diagnostic Rationales**:
   - Programmatically check `g6_default = "N"` consistency (all 31 bank/utility incomplete rows have `6 = "N"`), and spot-check cited numbers (`g6_netdebt_yrs`, `g6_intcov`, `fcf_conv`, `p2p_ok`) against `financials.csv` and `fundamentals_panel.csv` across a broad stratified sample of the 121 rows.
5. **Mirror Parity & `--audit`**:
   - Verify 100% character-for-character parity on `ASML`/`ASML.NL` and `FER`/`FER.ES`, and run `python3 screener/bulk_scorer.py --audit`.

## Deliverable
Write `challenge_report.md` and `handoff.md` in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_challenger_2/` with explicit **Verdict: `APPROVE` or `REJECT`**, and notify `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
