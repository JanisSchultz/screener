# Handoff Report — `v718_survey_explorer_data`

**Handoff Type**: Hard
**Deliverable**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md`

---

## 1. Observation

1. **Existing audit baseline**: Running `python3 screener/bulk_scorer.py --audit` exited 0 with `Gate 3 Populations: {'us': 445, 'eu': 495, 'ca': 49} | Total: 989 / 989`, `989 scored / 0 unscored`, `0` formula discrepancies, `0` 3a alignment discrepancies, `0` missing 4n notes, `0` waterfall violations, `0` calamity violations, and `Dual-Listed Mirror Parity: PASSED`.
2. **Universe & Funnel Counts** (verified by running `screener.data.load_universe` + `screener.gates.phase_results` + `screener.gates.g6_checks` across `data/{us,eu,ca}/`):
   - Total rows: `515` US + `602` EU + `58` CA = `1,175`.
   - Gate 1 fail (`1 == "N"`): `14` US + `14` EU + `2` CA = `30`.
   - Gate 2 fail (`1 == "Y", 2 == "N"`): `56` US + `93` EU + `7` CA = `156`.
   - Gate 3 reaching (`1 == "Y", 2 == "Y"`): `445` US + `495` EU + `49` CA = `989`.
   - Gate 3 rejects: `198` US + `278` EU + `28` CA = `504`.
   - Gate 3 advancing: `247` US + `217` EU + `21` CA = `485` (`483` with `3b == "Y"`, plus `US:EL` and `US:APD` with `3b == "N", calamity == "Y"`).
   - Gate 4 pass (`CAP >= 15`): `190` US + `166` EU + `21` CA = `377`.
   - Gate 4 rejects (`CAP = 5Y / 10Y`): `57` US (`20` at `5Y`, `37` at `10Y`) + `51` EU (`29` at `5Y`, `22` at `10Y`) + `0` CA = `108`.
   - Gate 5 rejects (`5 == 0`, non-calamity): `9` US + `4` EU + `0` CA = `13` (`EU:ABI.BE`, `EU:DIM.FR`, `EU:SRT3.DE`, `EU:ADP.FR`, `US:BA`, `US:INTU`, `US:PANW`, `US:ROP`, `US:CCI`, `US:CSGP`, `US:D`, `US:ES`, `US:SO`). Five additional `5 == 0` rows (`US:EL`, `US:APD`, `EU:DGE.GB`, `EU:NESN.CH`, `EU:RTO.GB`) are Calamity passes and already have `6` populated.
   - Incomplete moat franchises (`5` or `6` blank among the 485): `108 + 13 = 121` (`66` US, `55` EU, `0` CA). Zero rows in the `121` have `calamity == "Y"`.
   - Completed moat franchises (`5` and `6` non-blank among the 485): `364` (`181` US + `162` EU + `21` CA = `225` Quality pass + `13` Calamity pass + `126` Gate-6 rejects).
   - Prime Grade (`Quality pass` and `g6_flags < 3`): `110` US + `104` EU + `11` CA = `225` (`0` Quality pass rows have `g6_flags >= 3`).
   - Prime Grade Calamity: `13` total (`10` US + `3` EU + `0` CA), `11` with `g6_flags < 3` (`8` US + `3` EU; `US:EL` and `US:RTX` each have `3` G6 flags).
3. **GICS Sector / Sub-Industry distribution (US + EU combined, normalizing `" (mapped)"`)**:
   - Communication Services: `2` (`APP`, `NFLX`); Consumer Discretionary: `8`; Consumer Staples: `4`; Energy: `1` (`TPL`); Financials: `38` (`14` Diversified Banks + `10` Regional Banks + `14` Insurance/Exchanges/Brokers/Payments); Health Care: `8`; Industrials: `24`; Information Technology: `18`; Materials: `5`; Real Estate: `6`; Utilities: `7`. Full per-company roster and same-sub-industry peer counts are in `analysis.md` Section 2.
4. **`CRM` inspection (`data/us/inputs.csv`)**:
   - Deterministic `4 = 5` (`3_tb=2`, `4_ent=1, 4_riv=1, 4_buy=1, 4_sup=0, 4_sub=2`), `4n` correctly states `Final CAP = 5Y`, `5` and `6` are blank, and `screener/bulk_scorer.py:201-210` (`REFERENCE_SNAPSHOT["CRM"]`) currently asserts `"5": "", "6": ""`.
   - `CRM`'s `note` begins `"Fails Gate 4 (CAP = 10, REJECT). Enterprise software baseline (10-15 years) haircut to CAP 10 under Macrotrend #1..."` and ends `"Downstream gates bypassed per strict waterfall."`
5. **Dual-listed mirrors (`data/us/universe.json:87-90`)**:
   - Only `ASML` (`eu:ASML.NL`) and `FER` (`eu:FER.ES`) are configured as mirrors. `ASML`/`ASML.NL` are complete (`Quality pass`); `FER`/`FER.ES` fail Gate 3 (`3b="N"`). Zero mirrors appear in the 121 incomplete set.
6. **`prescreen.csv` `g6_default = "N"`**:
   - Applies to `31` of the 121 incomplete companies (`14` Diversified Banks, `10` Regional Banks, `7` Utilities — including 3 Gate-5 rejects `US:D`, `US:ES`, `US:SO` whose `6` column in `inputs.csv` is currently blank).
7. **Schemas & Coverage**:
   - All 121 have rows in `financials.csv` (45 cols), multi-year rows in `fundamentals_panel.csv` (69 cols), and non-empty `note` + `evidence` in `inputs.csv`. Nine of the 121 (`US:EBAY`, `US:WTW`, `US:MMM`, `US:ES`, `EU:HBAN.CH`, `EU:ALSYDB.DK`, `EU:SBNOR.NO`, `EU:ENG.ES`, `EU:PNN.GB`) carry `BLOCKING_AUTO_NOTES` in `financials.csv:fin_note`.
8. **`"Downstream gates bypassed per waterfall."` occurrences**:
   - Across the 121 incomplete rows, exact `"Downstream gates bypassed per waterfall."` appears in **2** rows (`US:APP`, `US:NOW`), while **4** additional rows have variants: `"Downstream Gates 5-6 bypassed per waterfall."` (`US:NFLX`, `US:SBUX`), `"Downstream gates bypassed per strict waterfall."` (`US:CRM`), and `"Downstream Gate 6 bypassed per waterfall."` (`US:ROP`). The remaining **115** of the 121 have no waterfall-bypass sentence. `0` of the 364 completed rows have any waterfall-bypass sentence. `40` Gate 1–3 reject rows have waterfall-bypass/nullification sentences (must remain untouched).

---

## 2. Logic Chain

1. Funnel invariance (`225` Prime Grade, `13 / 11` Prime Grade Calamity, `485` Gate-3 advancing, `504` Gate-3 rejects) holds identically because `108` incomplete rows fail Anchor Gate 4 (`CAP < 15`) and `13` fail Gate 5 (`5 = 0`, non-calamity), leaving `0` rows in `To review`.
2. Combining US and EU by normalized `sub_industry` (`sub.replace(" (mapped)", "").strip()`) aligns cross-Atlantic peers (e.g., `ADS.DE` + `MONC.IT` + `NKE` against `CFR.CH`/`MC.FR`/`RMS.FR`; `ALFA.SE`/`IMI.GB`/`IP.IT`/`ROR.GB`/`SKF B.SE`/`TREL B.SE` + `FTV`/`IEX` against 16 US+EU peers), enabling an 11-batch (or 10-batch if Banks are combined) GICS Sector/Sub-Industry evaluation dispatch without splitting US vs. EU.
3. Because `CRM`'s `note` contains both stale `CAP = 10` prose and the `"strict"` variant (`"Downstream gates bypassed per strict waterfall."`), and `NFLX`, `SBUX`, and `ROP` use numbered variants (`"Gates 5-6"`, `"Gate 6"`), R2 cleanup must match all 4 regex variants on the 121 rows (and must NOT run globally across `inputs.csv`, where 40 Gate 1–3 rejects legitimately retain those sentences).
4. Because `screener/gates.py:171` falls back to `g6_default` when `inputs.csv` column `6` is blank, `US:D`, `US:ES`, and `US:SO` currently evaluate to Gate 6 fail without an explicit `"N"` in `inputs.csv`; R2 must populate explicit `6 = "N"` on all 31 bank/utility incomplete rows (including `D`, `ES`, `SO`) so `audit_gate_3_universe` passes zero-blank checks.

---

## 3. Caveats

- No repository files were modified (read-only survey).
- `EU:DIM.FR` (Sartorius Stedim Biotech) and `EU:SRT3.DE` (Sartorius) are related parent/subsidiary listed entities in the 121 (`5=0`, `Life Sciences Tools & Services`), though not configured as mirrors in `universe.json`; keeping them in the same Health Care evaluator batch ensures consistent Gate 6 scoring.
- `US:SHOP` and `US:TRI` are Canadian-headquartered companies listed in `data/us/inputs.csv` per `data/ca/universe.json:20`.
- For the 9 incomplete companies with `BLOCKING_AUTO_NOTES` in `financials.csv:fin_note`, `financials.csv` summary multiples/per-share figures may reflect non-cash marks or M&A share-count changes; evaluators should inspect `fundamentals_panel.csv` and `note`/`evidence` directly.

---

## 4. Conclusion

The dataset is clean, 100% consistent with `ORIGINAL_REQUEST.md` targets (`1,175` total, `989` Gate 3, `504` Gate-3 rejects, `485` Gate-3 advancing = `364` complete + `121` incomplete [`108` Gate-4 + `13` Gate-5], `225` Prime Grade, `13` / `11` Prime Grade Calamity), and ready for R1 engine updates and R2 evaluation across the proposed 10–11 US+EU sector-aligned batches detailed in `analysis.md`.

---

## 5. Verification Method

Independently verify all claims via read-only execution:
1. Run `python3 screener/bulk_scorer.py --audit` (verifies `989` Gate-3 counts, reference snapshot, deterministic CAP, waterfall, mirror parity).
2. Inspect `analysis.md` at `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data/analysis.md` alongside `data/{us,eu,ca}/{inputs.csv,financials.csv,fundamentals_panel.csv,prescreen.csv,universe.json}`.
3. Run the inline verification logic using `screener.data.load_universe` and `screener.gates.phase_results` / `g6_checks` to confirm `121` incomplete (`66` US + `55` EU + `0` CA), `6` waterfall-sentence matches in the `121`, and `31` `g6_default="N"` rows in the `121`.
