# Handoff Report: Batch 05 Qualitative Evaluation

**Agent**: `evaluator_b05`  
**Milestone**: Batch 05 Qualitative Evaluation (65 Financials companies)  
**Timestamp**: 2026-11-16T11:22:30Z  
**Parent Conversation ID**: `52860145-8fc7-4969-8b2b-b7788e50408a`  

---

## 1. Observation

1. **Input Dossier & Scope**:
   - Dossier: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/batches/batch_05.json`
   - Company count: Exactly 65 companies across `eu` (37), `us` (22), and `ca` (6).
   - Sector: 100% Financials (Diversified Banks, Financial Exchanges & Data, Insurance Brokers, Investment Banking & Brokerage, Life & Health Insurance, Multi-Sector Holdings, Multi-line Insurance).

2. **Evaluation & Ingestion Verification**:
   - Output file generated: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_05_evaluated.json` (65 evaluated companies).
   - Validation via `screener.bulk_scorer.validate_company_evaluation`:
     `Total evaluated items: 65 | Validation warnings: 0 | Validation errors: 0`
   - Dry-run batch ingestion via `python3 screener/bulk_scorer.py --ingest evaluations/completed/batch_05_evaluated.json --dry-run`:
     ```
     Batch Ingestion Summary (DRY RUN):
       Total evaluated: 65
       Applied successfully: 65
       Rejected: 0
       Companies modified: 65
     ```
   - Regression test suite:
     `Ran 303 tests in 17.913s ... OK`

---

## 2. Logic Chain

1. **Gate 3 Moat Profiles & Initial CAP**:
   - Each company was scored across the four orthogonal archetypes: `3_tb` (Toll booth & switching costs), `3_ia` (Irreplaceable infrastructure & intangibles), `3_se` (Scale economies shared), and `3_rd` (R&D leadership) on `0 / 1 / 2`.
   - Initial CAP was computed deterministically from `m_max` and `m_sum`:
     - 0Y if all 0;
     - 15Y if sum=1;
     - 20Y if sum>=2 (max=1) or sum=2 (max=2);
     - 25Y if sum=3 (max=2);
     - 30Y if sum>=4 (max=2).
   - Primary moat `3a` was aligned to the highest-scoring archetype.

2. **Sequential Waterfall Enforcement (Gate 3 Rejections)**:
   - 21 companies failed Gate 3 (`3b == "N"`) due to structural spread-dependence, cyclical commodity underwriting, interest rate sensitivity, or sub-hurdle multi-cycle returns (<12% ROIC/ROE):
     - Spanish bank: `SAB.ES`.
     - Life & Health Insurers: `AFL`, `GWO.CA`, `MET`, `MFC.CA`, `PFG`, `POW.CA`, `PRU`, `SLF.CA`, `AGN.NL`, `LGEN.GB`, `MANTA.FI`, `NN.NL`, `PRU.GB`, `SDLF.GB`.
     - Conglomerates / Cyclical HoldCos: `AKER.NO`, `EXO.NL`, `GBLB.BE`, `KBCA.BE`, `TUB.BE`.
     - Multi-line insurer: `AIG`.
   - Under the sequential Munger reject waterfall, all downstream fields (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`) were strictly set to `""`.

3. **Gate 4 Competitive Forces & Deterministic Final CAP**:
   - The remaining 44 companies passing Gate 3 (`3b == "Y"`) received full Porter 5 Forces scoring on `0 / 1 / 2` evaluated against the 5 Macrotrends (AI/Automation, Demographic Aging, Reshoring, Energy Transition, Cost of Capital):
     - 11 companies failed Gate 4 (Final CAP < 15Y) due to fatal flaw caps or moderate friction accumulation:
       - Banks with low persistence / domestic rivalry: `LLOY.GB` (10Y), `NWG.GB` (5Y), `SEB A.SE` (5Y), `SWED A.SE` (10Y), `UCG.IT` (10Y).
       - Financial data facing AI substitution: `FDS` (10Y, AI research agent terminal substitution).
       - Broker with severe talent lift-out rivalry: `WTW` (5Y).
       - Wholesale voice broker facing electronification: `TCAP.GB` (5Y, electronic execution substitution).
       - Life insurers with demographic / regulatory headwinds: `GL` (5Y, agent recruiting crisis), `SLHN.CH` (5Y, European demographic aging & BVG caps), `STB.NO` (5Y, Nordic demographic aging).
       - For these 11 companies, Gates 5 and 6 were cleared to `""` per waterfall.
     - 33 companies passed Gate 4 (Final CAP >= 15Y) and maintained full evaluation through Gates 5 and 6:
       - Financial exchanges / data passing quality: `CBOE` (15Y, G5=1, G6=Y), `CME` (20Y, G5=1, G6=Y), `ICE` (20Y, G5=1, G6=Y), `MCO` (30Y, G5=2, G6=Y), `X.CA` (20Y, G5=1, G6=Y), `DB1.DE` (20Y, G5=1, G6=Y), `ENX.FR` (15Y, G5=2, G6=Y).
       - Insurance brokers passing quality: `AON` (20Y, G5=1, G6=Y), `BRO` (15Y, G5=1, G6=Y), `ERIE` (15Y, G5=1, G6=Y), `MRSH` (20Y, G5=1, G6=Y).
       - Investment brokers passing quality: `IBKR` (20Y, G5=2, G6=Y), `SCHW` (20Y, G5=1, G6=Y), `AZA.SE` (15Y, G5=2, G6=Y), `FBK.IT` (15Y, G5=2, G6=Y), `SAVE.SE` (15Y, G5=1, G6=Y).
       - Multi-sector compounders passing quality: `BRK.B` (20Y, G5=2, G6=Y), `III.GB` (15Y, G5=2, G6=Y), `INDU C.SE` (15Y, G5=1, G6=Y), `INVE B.SE` (20Y, G5=2, G6=Y), `LATO B.SE` (15Y, G5=2, G6=Y), `LUND B.SE` (20Y, G5=2, G6=Y).
       - Companies failing Gate 6 on balance sheet leverage / fractional-reserve structure: `NDA FI.FI` (15Y, G5=2, G6=N), `SHB A.SE` (15Y, G5=2, G6=N), `UBSG.CH` (15Y, G5=1, G6=N), `PST.IT` (15Y, G5=1, G6=N), `MSCI` (20Y, G5=1, G6=N), `NDAQ` (15Y, G5=1, G6=N), `LSEG.GB` (15Y, G5=1, G6=N), `AJG` (15Y, G5=1, G6=N), `MS` (15Y, G5=1, G6=N), `RJF` (15Y, G5=1, G6=N), `ACKB.BE` (15Y, G5=2, G6=N).
   - Mandatory `4n` Runway & Forces notes were populated for all 44 companies, explicitly stating the Initial CAP, force codes, and haircut deduction / structural insulation.

---

## 3. Caveats

- **No Caveats**: All 65 companies have been evaluated individually adhering strictly to `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md`.
- No inputs.csv or code files were modified directly, respecting exclusive file ownership.

---

## 4. Conclusion

Batch 05 qualitative evaluation is **COMPLETE** and verified:
1. `evaluations/completed/batch_05_evaluated.json` is generated with 65 fully evaluated records.
2. 100% compliance with deterministic CAP formulas, moat alignment rules, mandatory `4n` notes, and sequential waterfall clearing.
3. Batch ingestion dry-run reports 65/65 applied, 0 errors, 0 warnings.
4. Full unittest suite passes 303/303 tests cleanly.

---

## 5. Verification Method

To independently verify this evaluation:

1. **Run Batch Verification Script**:
   ```bash
   python3 .agents/teamwork/evaluator_b05/generate_batch_05_eval.py
   ```
   *Expected*: `Total evaluated items: 65 | Validation warnings: 0 | Validation errors: 0`.

2. **Run Dry-Run Ingestion**:
   ```bash
   python3 screener/bulk_scorer.py --ingest evaluations/completed/batch_05_evaluated.json --dry-run
   ```
   *Expected*: `Total evaluated: 65, Applied successfully: 65, Rejected: 0`.

3. **Run Test Suite**:
   ```bash
   python3 -m unittest discover tests
   ```
   *Expected*: `Ran 303 tests ... OK`.
