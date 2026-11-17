# Handoff Report — v718_eval_b01 (Batch 1: Diversified & Regional Banks, US+EU Combined)

**Handoff Type**: Hard  
**Working Directory**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b01`  
**Deliverable**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b01/evaluations.json`  

---

## 1. Observation

1. **Authoritative Spec & Pre-Screen Baseline**:
   - `QUALITATIVE_EVALUATION_SPEC.md:190-237` defines Gate 5 (`5` in `{0, 1, 2}` across Integrity & Candor, Rational Capital Allocation, Customer Value, Product-Led Execution, and Anti-Bureaucracy) and Gate 6 (`6` in `{"Y", "N"}`, explicitly stating at line 231: *"Commercial fractional-reserve banks fail"*).
   - `data/us/prescreen.csv`, `data/eu/prescreen.csv`, and `data/ca/prescreen.csv` all set `g6_default = "N"` (`"Gate 6 default N (v6.11, moved from Gate 2): leverage 10-15x, credit & deposit duration risk"`) for both `Diversified Banks` / `Diversified Banks (mapped)` and `Regional Banks` / `Regional Banks (mapped)`.

2. **18 Completed Bank Peer Calibration Set (`us`, `eu`, `ca`)**:
   - Directly inspected all 18 completed Diversified Banks peers in `inputs.csv` and `financials.csv`:
     - **`5 = 2` (7 peers)**: `CA:NA.CA` (14.9% ROE med, 11.0% OE CAGR), `CA:RY.CA` (14.9% ROE med), `EU:ISP.IT` (12.4% ROE med, 15-18% ROTE, Eurizon/Fideuram), `EU:KBC.BE` (13.7% ROE med, ~45% CIR), `EU:NDA FI.FI` (14.9% ROE med, ~45% CIR, -16.3% 8Y shares), `EU:SHB A.SE` (11.6% ROE med, decentralized Wallander Church model since 1970, <0.05% loan loss ratio), `US:JPM` (15.7% ROE med, 17-22% ROTCE, -18.1% 8Y shares).
     - **`5 = 1` (11 peers)**: `CA:BMO.CA` (9.6% ROE), `CA:BNS.CA` (9.2% ROE), `CA:CM.CA` (12.6% ROE), `CA:TD.CA` (14.4% ROE med; Oct 2024 $3.09B criminal AML settlement & OCC/Fed asset cap), `EU:CABK.ES` (15.6% ROE med), `EU:DNB.NO` (14.5% ROE med, -8.4% shares), `EU:UBSG.CH` (12.4% ROE med), `US:BAC` (9.6% ROE med, -24.5% shares), `US:PNC` (10.6% ROE med, -14.9% shares), `US:USB` (10.4% ROE med), `US:WFC` (10.2% ROE med, -31.6% shares, Scharf turnaround).
     - **`5 = 0` (0 of 18 peers)**; **`6 = "N"` (18 of 18 peers)**.

3. **Assigned 24 Banks (`14` EU Diversified + `8` EU Regional + `2` US Regional)**:
   - All 24 rows in `data/eu/inputs.csv` and `data/us/inputs.csv` have `4` in `{5, 10}`, `5 = ""`, `6 = ""`, `calamity = ""`, `is_g5_reject = false`, and zero `"Downstream gates bypassed..."` waterfall sentences in `note`.
   - Quantitative data inspected across `financials.csv` and `fundamentals_panel.csv` (FY2018–FY2025):
     - **Outlier Compounders**: `EU:RILBA.DK` (20.5% ROE med, ~30% CIR, 18.9% OE CAGR, -18.2% 8Y shares, 7.5x TA/Eq), `EU:BG.AT` (16.7% ROE med / ~26% RoTCE, ~33% CIR, 15.5% OE CAGR, -20.0% 8Y shares), `EU:BKT.ES` (17.0% ROE med, ~37% CIR, lowest Spanish NPLs, 0% dilution), `EU:SEB A.SE` (13.9% ROE med, ~36% CIR, 11.4% OE CAGR, -8.5% 8Y shares, Wallenberg anchor, clean AML record).
     - **AML / Governance / Integration Cases**: `EU:DANSKE.DK` (€200B Estonia AML scandal, $2.0B DOJ/SEC/Danish criminal settlement Dec 2022, -DKK 4.58B FY22 net loss / -3.2% ROE, 3.3% OE CAGR, heavy AML compliance overhead); `EU:SWED A.SE` (SEK 4B Swedish FSA fine, CEO/board ouster, ongoing US DOJ/SEC reviews, zero buybacks, but 14.7% ROE med & no net loss years); `EU:ALSYDB.DK` (`fin_note` 1.62x share count change post-FY25 3-way merger, FY25 ROE distorted to 5.0% vs 14.4% med); `EU:SBNOR.NO` (`fin_note` 1.58x share count change post-May 2025 merger; `roe_median = 6.6%` reflects `ni_c` ~40.5% ECC share vs 100% total equity, whereas total-bank `ni/eq` was 12.7–17.8% FY21–FY24 and 12.1% FY25).
     - **Validation**: `evaluations.json` passed a programmatic assertion check confirming 24 unique `(universe, id)` entries matching `inputs.csv` (`ticker`, `sub_industry`), `5` in `{0, 1, 2}`, `6 == "N"`, `is_g5_reject == False`, and non-empty `diagnostic_rationale` and `peer_calibration_notes`. `git status` confirms zero modifications to any `data/` or repository files by this worker.

---

## 2. Logic Chain

1. **Gate 6 (`6 = "N"` across all 24)**: Because `QUALITATIVE_EVALUATION_SPEC.md:231` and `prescreen.csv` (`g6_default = "N"`) explicitly disqualify commercial fractional-reserve banks—and all 24 banks exhibit 7.3x–21.2x assets-to-equity leverage, deposit/covered-bond duration transformation, and central bank/deposit-insurance reliance (matching all 18 completed bank peers)—every bank is scored `6 = "N"` with bank-specific balance sheet leverage, LT debt/NI, and FCF conversion figures cited.
2. **Gate 5 (`5 = 2`, 4 banks)**: Calibrated strictly to the 7 completed `5 = 2` peers (`SHB A.SE`, `NDA FI.FI`, `KBC.BE`, `ISP.IT`, `JPM`, `RY.CA`, `NA.CA`), `EU:RILBA.DK`, `EU:BG.AT`, `EU:BKT.ES`, and `EU:SEB A.SE` combine top-decile cost efficiency (30%–37% CIR), sustained high ROE (13.9%–20.5% median), clean credit/compliance discipline, and strong per-share capital allocation.
3. **Gate 5 (`5 = 0`, 1 bank)**: `EU:DANSKE.DK` fails Gate 5 Vectors (a) and (e) due to the €200B Estonia criminal AML catastrophe ($2.0B criminal settlement, FY22 net loss, CEO/board turnover, brand/compliance fallout, 3.3% OE CAGR), which is explicitly flagged in its dossier as severe integrity fallout.
4. **Gate 5 (`5 = 1`, 19 banks)**: Remaining banks show honest/capable or turnaround stewardship without disqualifying red flags (`A5G.IE`, `ABN.NL`, `BCP.PT`, `BIRG.IE`, `EBS.AT`, `INGA.NL`, `LLOY.GB`, `NWG.GB`, `SWED A.SE`, `UCG.IT`, `ALSYDB.DK`, `BCVN.CH`, `JYSK.DK`, `SB1NO.NO`, `SBNOR.NO`, `UNI.ES`, `VATN.CH`, `MTB`, `RF`). In particular, `EU:SWED A.SE` (14.7% ROE, ongoing DOJ/SEC AML review, zero buybacks) is calibrated consistently with `CA:TD.CA[1,N]` (criminal AML fine + asset cap on an otherwise high-ROE franchise), while `EU:UCG.IT` (Orcel turnaround after 2008–2021 capital destruction) is calibrated consistently with `US:WFC[1,N]`.

---

## 3. Caveats

- **Read-Only Scope**: Per `DISPATCH.md`, `data/eu/inputs.csv` and `data/us/inputs.csv` were NOT modified; the coordinator/ingestion step must apply `evaluations.json` into `inputs.csv` (`5`, `6`, and `[Diagnostic G5=<0|1|2> | G6=N: <diagnostic_rationale>]` appended to `note`).
- **Borderline Calls Documented**:
  - `EU:SWED A.SE` (`5 = 1` vs `0`): Calibrated to `CA:TD.CA[1,N]` rather than `EU:DANSKE.DK[0]` because Swedbank avoided negative FY earnings and €200B-scale criminal guilty pleas, though its ongoing US DOJ/SEC review keeps it below `SEB A.SE[2]`.
  - `EU:SEB A.SE` and `EU:BG.AT` (`5 = 2` vs `1`): Scored `2` based on ~33–36% CIR, clean compliance/credit culture, and -8.5% / -20.0% 8Y share count shrinkage; `EU:BG.AT` has a shorter 8-year public post-IPO window (2018–2025) than multi-decade `RILBA.DK` or `SHB A.SE`.
  - `EU:ABN.NL`, `EU:UNI.ES`, `EU:VATN.CH` (`5 = 1` vs `0`): Low historical ROE (5.7%–8.6%) reflects structural rate/spread compression already captured by Gate 4 `CAP = 5Y` rather than management fraud/empire M&A (respecting Anti-Drift Rule #3 orthogonality).

---

## 4. Conclusion

All 24 Batch 1 banks (14 EU Diversified Banks, 8 EU Regional Banks, 2 US Regional Banks) have been individually evaluated from local repository data and calibrated on a unified cross-Atlantic yardstick against the 18 completed bank peers:
- **Gate 5**: `4` Elite (`2`: `EU:BG.AT`, `EU:BKT.ES`, `EU:RILBA.DK`, `EU:SEB A.SE`), `19` Standard Pass (`1`), `1` Reject (`0`: `EU:DANSKE.DK`).
- **Gate 6**: `24` Reject (`"N"`).
- **Output file**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_eval_b01/evaluations.json`.

---

## 5. Verification Method

Run the following read-only verification command to independently confirm all 24 entries in `evaluations.json` match `inputs.csv` metadata, rubric bounds, and expected counts, and that no `data/` files were altered:

```bash
python3 - << 'EOF'
import json, csv
d = json.load(open(".agents/teamwork/v718_eval_b01/evaluations.json"))
assert len(d) == 24
assert all(x["5"] in (0, 1, 2) and x["6"] == "N" and x["is_g5_reject"] is False for x in d)
print({k: sum(1 for x in d if x["5"] == k) for k in (0, 1, 2)})
EOF
git status --short data/
```

**Invalidation Conditions**: Any entry missing from the 24-bank dispatch list, any mismatch on `ticker`/`sub_industry` vs `inputs.csv`, any `6 != "N"`, or any modification to `data/` files by this worker.
