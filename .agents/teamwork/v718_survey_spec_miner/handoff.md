# Handoff Report — v718_survey_spec_miner

**Handoff Type**: Hard  
**Agent**: `v718_survey_spec_miner` (`teamwork_spec_miner`)  
**Parent Orchestrator**: `d510ad6d-e687-40ee-9300-d03ba5fff497`  
**Primary Deliverable**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`

---

## 1. Observation

Read-only inspection of the authoritative specification files and supporting code/data contracts revealed:

1. **Gate 5 (`0 / 1 / 2`) Rubric**:
   - `QUALITATIVE_EVALUATION_SPEC.md:185–202` and `COMPANY_EVALUATION_SPEC.md:171–188` define Gate 5 (`5` / `gate_5_management_score`) with threshold `thr_culture = 1`, evaluated across 5 vectors: `(a)` Integrity & Candor (Fisher/Buffett), `(b)` Rational Capital Allocation (Murphy/Thorndike, $\ge 12\%$ reinvestment, counter-cyclical buybacks, no empire M&A), `(c)` Customer Value-for-Money / Consumer Surplus (Bezos/Sleep), `(d)` Product-Led Execution, and `(e)` Anti-Bureaucracy & Planned Abandonment (Wallenberg/Drucker).
   - Scoring: `0` = REJECT (promotional ego, aggressive non-GAAP / repeated one-offs, value-destructive M&A rollups, predatory pricing, bureaucratic/SG&A bloat per `screener/config.py:201`, compensation decoupled from per-share compounding); `1` = Standard Pass (`MSFT`, `MSCI`); `2` = Elite Compounder (`V`).
   - Current Waterfall Action (`QUALITATIVE_EVALUATION_SPEC.md:202`, `COMPANY_EVALUATION_SPEC.md:188`): `"If 5 < 1 (i.e. 0), set result = \"Rejected – G5 Management\". Leave Gate 6 completely blank/null."`

2. **Gate 6 (`Y / N`) Rubric**:
   - `QUALITATIVE_EVALUATION_SPEC.md:206–232` and `COMPANY_EVALUATION_SPEC.md:192–218` define Gate 6 (`6` / `gate_6_cash_and_balance_sheet`) across Three Compounding Pillars:
     - **Pillar 1**: Peak-to-Peak Business Cycle EPS Compounding (`p2p_ok`; repeatable earnings power, not windfall spike).
     - **Pillar 2**: Real Free Cash Flow Conversion (Multi-Year Owner FCF $\ge 80\%$ of GAAP Net Income, `fcf_conv >= 0.80`; no capex sinkholes or working-capital black holes).
     - **Pillar 3**: Peace-of-Mind Balance Sheet (No "Kindness of Strangers"): Quantitative baseline Net Debt $\le 4.0$ years (`g6_netdebt_yrs <= 4.0`) and Interest Coverage $> 5.0\times$ (`g6_intcov > 5.0`, ideally $> 10\times$).
   - **Sector/Special Rules**:
     - Essential infrastructure & concessions (freight rails, landfills, regulated toll concessions): pass if interest coverage $> 5\times$.
     - Float institutions & holding companies (insurers/HoldCos): evaluated on Solvency II $> 200\%$, underwriting discipline, and look-through operating earnings (`screener/gates.py:359–366` sets `g6_checks` `netdebt`/`intcov`=`n/a` and `fcfconv`=`info` for Balance-Sheet Financials).
     - Commercial fractional-reserve banks: automatic `N` (`QUALITATIVE_EVALUATION_SPEC.md:226`, `COMPANY_EVALUATION_SPEC.md:212`); `Diversified Banks` and `Regional Banks` also carry `g6_default = "N"` (`data/us/prescreen.csv:50, 58`).
     - Regulated utilities: carry `g6_default = "N"` (`QUALITATIVE_EVALUATION_SPEC.md:35`, `COMPANY_EVALUATION_SPEC.md:35`, `data/us/prescreen.csv:134–138` for Electric, Gas, IPP, Multi-Utilities, Water Utilities).
     - Surplus cash / T-bills: count toward fortress strength, never against return hurdles.
     - Disqualifying Red Flags (auto `N`): debt-funded share buybacks at peak multiples creating negative tangible/book equity (`FICO`, `MSCI` Example 5 at `COMPANY_EVALUATION_SPEC.md:583–623`), serial debt/dilution M&A rollups, reliance on short-term CP / continuous capital-market access.
   - `QUANTITATIVE_EVALUATION_SPEC.md:203–205` and `screener/gates.py:347–368` confirm `g6_checks` (`g6_netdebt_yrs <= 4.0`, `g6_intcov > 5.0`, `fcf_conv >= 0.80`, `p2p_ok`) are informational review flags only; qualitative `6` decides.

3. **Anti-Drift Rules & Note/Rationale Formatting**:
   - `QUALITATIVE_EVALUATION_SPEC.md:177–180` and `COMPANY_EVALUATION_SPEC.md:163–166` specify:
     - **Rule #1 (Sub-Industry Peer Benchmarking)**: Cross-check scores against same-sub-industry peers on an identical yardstick (e.g., `SU.FR` vs `ETN`, `DHR` vs `TMO`, `CME` vs `ICE` / `DB1.DE`, `WM` vs `RSG` / `WCN.CA`); `ORIGINAL_REQUEST.md:18` extends this to G5/G6 evaluation across US and EU combined.
     - **Rule #2 (`4_sub / 4_riv = 1 vs 2` Boundary)**: Reserve `2` for UI seat workflows/research workstations (`CRM`, `ADBE`, `NOW`, `FDS`, `TRI`); score proprietary non-seat data/statutory engines (`REL.GB`, `WKL.NL`, `FICO`) at `1`.
     - **Rule #3 (Gate 4 vs Gate 5/6 Orthogonality)**: Reject PE M&A rollups (`ROP`) at Gate 5 (`5=0`) and debt-funded buyback negative equity (`FICO`, `MSCI`) at Gate 6 (`6="N"`), never via Gate 4 CAP.
   - Note/evidence formatting: Quality/Calamity Pass notes end with `[5-10Y g: ...]`; `4n` mandatory if any `4_* >= 1`; `calamity_note` requires 3 parts when `calamity="Y"`; per `ORIGINAL_REQUEST.md:20`, Stage-2 G4/G5 rejects strip `"Downstream gates bypassed per waterfall."` and append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`.

4. **Sections Requiring Update for v7.18 Two-Stage Munger Waterfall**:
   - `QUALITATIVE_EVALUATION_SPEC.md` has **8 locations** enforcing `v7.16` or old 1-stage G4/G5 blanking: lines `1 & 8` (version), `15` (Waterfall Invariant), `44–68` (Gate flow intro), `181` (Gate 4 Waterfall Action), `202` (Gate 5 Waterfall Action), `245–248` (`note` rejected format), `327–328 & 331` (Field Mapping nullable table rows `5`, `6`, `note`), and `342` (`apply_evaluation.py` scrubbing description).
   - `COMPANY_EVALUATION_SPEC.md` has **9 locations**: lines `1 & 8` (version), `15` (Waterfall Invariant), `47–71` (Gate flow intro), `167` (Gate 4 Waterfall Action), `188` (Gate 5 Waterfall Action), `233–236` (`note` rejected format), `393–394 & 397` (Schema Rules nullable table rows `5`, `6`, `note`), `539–579` (Example 4 `CRM` currently has `gate_5_management_score: null`, `gate_6_cash_and_balance_sheet: null`), and `637–641` (Step 1 Validate Payload & Invariants).

---

## 2. Logic Chain

1. By reading both `QUALITATIVE_EVALUATION_SPEC.md` (lines 1–343) and `COMPANY_EVALUATION_SPEC.md` (lines 1–653) in full and cross-checking against `ORIGINAL_REQUEST.md` and `screener/{config,gates,apply_evaluation}.py`, we established the exact normative Gate 5 and Gate 6 rubrics and verified how quantitative indicators (`g6_checks`, `g6_default`) interact with qualitative `5` and `6`.
2. Comparing the current spec text (labeled `v7.16`) against `ORIGINAL_REQUEST.md` R1–R3 shows that Stage 1 early stopping (Gates 1–3, lines `83, 101, 142` in `QUALITATIVE_EVALUATION_SPEC.md` and `86, 104, 139` in `COMPANY_EVALUATION_SPEC.md`, plus `CCL` Example 2 and `NUE` Example 3) remains valid, whereas every rule requiring Gates 5–6 to be null when `4 < 15` or Gate 6 to be null when `5 = 0` must be updated to Stage 2 diagnostic scoring.
3. Grep verification for `v7.16`, `downstream`, and `blank/null` across both markdown specs confirmed no hidden occurrences remain outside the 8 cataloged locations in `QUALITATIVE_EVALUATION_SPEC.md` and 9 cataloged locations in `COMPANY_EVALUATION_SPEC.md`.

---

## 3. Caveats

- Read-only survey only: no repository files were modified, and `data/*/inputs.csv` rows were not audited (per scope, another survey agent or R1/R2 agents handle CSV/code inspection).
- Exact verified `5` and `6` values for `CRM` in `COMPANY_EVALUATION_SPEC.md` Example 4 cannot be filled until R2 evaluates `CRM` and records its verified diagnostic scores.

---

## 4. Conclusion

The complete Gate 5 (`0/1/2`) and Gate 6 (`Y/N`) rubrics, Anti-Drift Rules (#1–#3), note/rationale formatting rules, and the exhaustive line-by-line catalog of **8 locations** in `QUALITATIVE_EVALUATION_SPEC.md` and **9 locations** in `COMPANY_EVALUATION_SPEC.md` requiring R3 Two-Stage Waterfall updates are documented in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_spec_miner/spec_report.md`. Ready for downstream R1/R2/R3 agents.

---

## 5. Verification Method

Independently verify by inspecting the cited line ranges in both spec files and running grep checks:
- View `QUALITATIVE_EVALUATION_SPEC.md` lines `1–18, 44–68, 177–256, 327–343`
- View `COMPANY_EVALUATION_SPEC.md` lines `1–18, 47–71, 163–244, 393–398, 539–642`
- Confirm no missed occurrences via:
  - `grep -nE "v7\.16|blank/null|downstream" QUALITATIVE_EVALUATION_SPEC.md COMPANY_EVALUATION_SPEC.md`
- **Invalidation Condition**: If `QUALITATIVE_EVALUATION_SPEC.md` or `COMPANY_EVALUATION_SPEC.md` are edited after `2026-11-17T15:35:00Z`, cited line numbers shift accordingly.
