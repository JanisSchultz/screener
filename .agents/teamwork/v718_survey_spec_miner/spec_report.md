# v7.18 Specification Report: Gate 5/6 Rubrics, Anti-Drift Rules & Two-Stage Munger Waterfall Spec Catalog

**Authoritative Sources Inspected (Read-Only)**:
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/QUALITATIVE_EVALUATION_SPEC.md` (343 lines)
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/COMPANY_EVALUATION_SPEC.md` (653 lines)
- `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md` (48 lines)
- Cross-verified against code/data contracts: `screener/config.py`, `screener/gates.py`, `screener/apply_evaluation.py`, `QUANTITATIVE_EVALUATION_SPEC.md`, `data/us/prescreen.csv`

---

## 1. Gate 5 Rubric: Honest, Able, Customer-Focused Management & Capital Allocation (`0 / 1 / 2`)

- **Sources**: `QUALITATIVE_EVALUATION_SPEC.md:185–202`, `COMPANY_EVALUATION_SPEC.md:171–188`, `screener/config.py:195–204, 274`
- **CSV Field / JSON Key**: `5` / `gate_5_management_score`
- **Allowed Values**: `0`, `1`, `2` (`SCORE_VALUES = (0, 1, 2)`)
- **Pass Threshold**: `thr_culture = 1`. Any score `< 1` (i.e. `0`) is a **REJECT** (waivable only via `calamity = "Y"` when all Anchor Gates `1="Y"`, `2="Y"`, `3a!="None"`, and `4>=15` pass; non-waivable if `4 < 15`, where under v7.18 `5` is scored diagnostically).

### 1.1 Five-Vector Elimination Rubric
Management is evaluated across five superinvestor vectors:
1. **(a) Integrity & Candor (Phil Fisher / Warren Buffett)**: Radical transparency in shareholder communications; candid admission of operating errors; conservative accounting without promotional non-GAAP adjustments; transparent stock-based compensation (SBC).
2. **(b) Rational Capital Allocation (Tom Murphy / Will Thorndike — *"The Outsiders"*)**: Ruthless focus on per-share intrinsic value growth; disciplined reinvestment hurdle rates ($\ge 12\%$); counter-cyclical share repurchases executed only below intrinsic value; avoidance of dilutive, empire-building mega-M&A.
3. **(c) Customer Value-for-Money / Consumer Surplus (Jeff Bezos / Nick Sleep)**: Obsessive focus on delivering superior value to customers; refusal to employ predatory price gouging or dark patterns that build customer resentment.
4. **(d) Product-Led Execution**: Deep technical and operational domain expertise; product and engineering excellence rather than financial engineering.
5. **(e) Anti-Bureaucracy & Planned Abandonment (Marcus Wallenberg / Peter Drucker)**: Lean corporate headquarters; radical decentralization; disciplined pruning of sub-hurdle divisions.

### 1.2 Scoring Levels & Criteria
| Score | Classification | Exact Spec Criteria & Red Flags |
|---|---|---|
| **`0`** | **REJECT — Red Flag Triggered** | Promotional executive ego; aggressive non-GAAP accounting or repeated "one-off" adjustments; value-destructive M&A rollups; predatory customer pricing / price gouging that erodes customer trust; bureaucratic / SG&A bloat (`config.py:201`); or management compensation decoupled from per-share compounding. |
| **`1`** | **Standard Pass** | Honest, capable / able stewardship; sensible capital allocation across all 5 vectors; good alignment with shareholders; clean accounting without red flags. |
| **`2`** | **Elite Compounder** | True owner-operator or exceptional "Outsider" CEO; multi-decade track record of exceptional per-share value creation; radical candor; substantial insider skin in the game; product obsession (`config.py:203`); high consumer surplus. |

### 1.3 Gate 5 Benchmarks & Worked Examples in Specs
- **`5 = 0` Benchmark (Anti-Drift Rule #3, `QUALITATIVE_EVALUATION_SPEC.md:180`, `COMPANY_EVALUATION_SPEC.md:166`)**: Value-dilutive PE M&A rollups (e.g., `ROP`) and predatory price gouging must be rejected at **Gate 5 (`5 = 0`)** rather than by artificially compressing Gate 4 CAP.
- **`5 = 1` Worked Examples**:
  - `MSFT` (`QUALITATIVE_EVALUATION_SPEC.md:290`, `COMPANY_EVALUATION_SPEC.md:356`): `gate_5_management_score: 1`
  - `MSCI` (`COMPANY_EVALUATION_SPEC.md:611`): `gate_5_management_score: 1` (fails Gate 6, passes Gate 5).
- **`5 = 2` Worked Example**:
  - `V` (`COMPANY_EVALUATION_SPEC.md:435`): `gate_5_management_score: 2`.

---

## 2. Gate 6 Rubric: Real Cash Conversion, Peak-to-Peak Compounding & Peace-of-Mind Balance Sheet (`Y / N`)

- **Sources**: `QUALITATIVE_EVALUATION_SPEC.md:35, 206–232`, `COMPANY_EVALUATION_SPEC.md:35, 40, 43, 192–218, 583–623`, `screener/config.py:206–222, 278–284`, `screener/gates.py:171, 347–368`, `QUANTITATIVE_EVALUATION_SPEC.md:203–205, 232`, `data/us/prescreen.csv:50, 58, 134–138`
- **CSV Field / JSON Key**: `6` / `gate_6_cash_and_balance_sheet`
- **Allowed Values**: `"Y"`, `"N"`
- **Core Principle**: Charlie Munger's qualitative triad and Warren Buffett's solvency standard: peak-to-peak earnings power, genuine cash generation, and freedom from the *"kindness of strangers"*.

### 2.1 The Three Compounding Pillars
1. **Pillar 1 — Peak-to-Peak Business Cycle EPS Compounding (`p2p_ok`)**:
   - Demonstrated track record and structural visibility of reaching a **new high in Owner EPS at the peak of each succeeding business cycle**.
   - Normal intra-cycle dips during general economic recessions are fully acceptable, provided peak-to-peak secular growth remains intact.
   - The prior peak must represent repeatable earnings power, not an unrepeatable windfall spike or secular ceiling (`config.py:218`).
2. **Pillar 2 — Real Free Cash Flow Conversion (`fcf_conv >= 0.80`)**:
   - Reported accounting profits convert cleanly into free cash flow: **Multi-Year Owner FCF $\ge$ 80% of GAAP Net Income** (`fcf_conv >= 0.80`, `a_fcfconv = 0.80`).
   - Business is free from maintenance capex sinkholes / capex treadmills, heavy capitalization of intangible costs, or working-capital black holes.
3. **Pillar 3 — Peace-of-Mind Balance Sheet (No "Kindness of Strangers")**:
   - Capital structure is built to comfortably endure a multi-year economic depression or complete credit market freeze without permanently impairing common equity (no bankruptcy, forced liquidation, or massive equity dilution).
   - Leverage strictly amplifies an already superior, cash-generative engine rather than masking or funding a mediocre one.
   - **Quantitative Baseline (`g6_checks` indicators)**:
     - **Net Debt Repayable $\le$ 4.0 years** (`g6_netdebt_yrs <= 4.0`): Spec text states `lt_debt_m / ni_ttm_m <= 4.0` or net cash; `QUANTITATIVE_EVALUATION_SPEC.md:204` & `metrics.py` compute 3-year median $(\text{LT} + \text{ST Debt} - \text{Cash \& ST Investments}) \div (\text{NI} + \text{Owner Add-Back}) \le 4.0\text{y}$.
     - **Interest Coverage $> 5.0\times$** (`g6_intcov > 5.0`): $\text{EBIT} / \text{Interest} > 5.0\times$ through the cycle (3-year median in `g6_checks`; ideally $> 10.0\times$ green threshold `a_intcov`).
     - *Note from `QUANTITATIVE_EVALUATION_SPEC.md:203` & `gates.py:348`*: `g6_checks` are informational/review flags (`✓ / ⚠ / –`); qualitative Gate 6 decides.

### 2.2 Sector, Capital-Structure & Special-Case Rules
| Category | Exact Rule in Specs & Pre-Screen |
|---|---|
| **Essential Infrastructure & Concessions** | Contractually formula-indexed physical infrastructure (freight rails, permitted landfills, regulated toll concessions) with non-displaceable cash flows **pass** provided interest coverage remains **$> 5\times$** (`QUALITATIVE_EVALUATION_SPEC.md:225`, `COMPANY_EVALUATION_SPEC.md:211`). |
| **Float Institutions & Holding Companies (Insurers / Reinsurers / HoldCos)** | Evaluated on **Solvency II ratios ($> 200\%$)**, conservative underwriting discipline, and **look-through operating earnings** across cycles rather than GAAP accounting noise or mark-to-market swings (`QUALITATIVE_EVALUATION_SPEC.md:226`, `COMPANY_EVALUATION_SPEC.md:212`, `config.py:213–214`). In `g6_checks` (`gates.py:359–366`), Balance-Sheet Financials have `netdebt = "n/a"`, `intcov = "n/a"`, and `fcfconv = "info"`. |
| **Commercial Fractional-Reserve Banks** | **Automatic `N`** — *"Commercial fractional-reserve banks fail."* (`QUALITATIVE_EVALUATION_SPEC.md:226`, `COMPANY_EVALUATION_SPEC.md:212`). Pre-screen sub-industries `Diversified Banks` and `Regional Banks` also carry `g6_default = "N"` (`prescreen.csv:50, 58`: *"leverage 10-15x, credit & deposit duration risk"*). |
| **Regulated Utilities (`g6_default = "N"`)** | Pre-screen sub-industry default is `g6_default = "N"` (`QUALITATIVE_EVALUATION_SPEC.md:35`, `COMPANY_EVALUATION_SPEC.md:35`, `config.py:216`). In `prescreen.csv:134–138`, `Electric Utilities`, `Gas Utilities`, `Independent Power Producers & Energy Traders`, `Multi-Utilities`, and `Water Utilities` have `g6_default = "N"` (*"capped 6-8% regulated ROIC, perpetual capex dilution"*). Note: under v7.18 diagnostic scoring, all Gate-3-advancing rows require an explicit non-blank `6` (`"Y"` or `"N"`). |
| **Surplus Cash Rule** | Cash and short-term sovereign T-bills held as dry powder count *toward* balance sheet fortress strength, never against return hurdles (`QUALITATIVE_EVALUATION_SPEC.md:227`, `COMPANY_EVALUATION_SPEC.md:213`). |

### 2.3 Disqualifying Red Flags (Automatic `N`)
`QUALITATIVE_EVALUATION_SPEC.md:228–231`, `COMPANY_EVALUATION_SPEC.md:214–217`:
1. **Debt-Funded Share Buybacks / Negative Equity**: Financial engineering via debt-funded share buybacks at peak cycle multiples resulting in negative tangible equity / negative stockholders' equity (e.g., `FICO` in Anti-Drift Rule #3; `MSCI` Example 5 at `COMPANY_EVALUATION_SPEC.md:583–623`: `$4.5B+` LT debt funding buybacks at 40–50x earnings, negative book equity `-$800M / -$820M`, Net Debt `> 4.5x` Owner Earnings).
2. **Serial Debt/Dilution Rollups**: Serial M&A rollups relying on continuous debt issuance or high-multiple equity dilution.
3. **Capital-Markets Dependence**: Reliance on short-term commercial paper or continuous access to capital markets to fund ongoing operations (`"kindness of strangers"`).

---

## 3. Anti-Drift Calibration Rules & Note/Rationale Formatting Standards

### 3.1 Three Anti-Drift Calibration Rules
Located in `QUALITATIVE_EVALUATION_SPEC.md:177–180` and `COMPANY_EVALUATION_SPEC.md:163–166`:
1. **Anti-Drift Rule #1 — Sub-Industry Peer Benchmarking**: Always cross-check `CAP_init` and Force scores against same-sub-industry peers so global oligopoly twins (e.g., `SU.FR` vs `ETN`, `DHR` vs `TMO`, `CME` vs `ICE` / `DB1.DE`, `WM` vs `RSG` / `WCN.CA`) are evaluated on an identical yardstick. *(Under `ORIGINAL_REQUEST.md` R2, this extends to Gate 5 & Gate 6: dispatch evaluator agents strictly by GICS Sector / Sub-Industry across US and EU combined, never splitting US vs. EU, and cross-check against already-scored same-sub-industry peers in the 364 completed moat franchises).*
2. **Anti-Drift Rule #2 — `4_sub / 4_riv = 1 vs. 2` Boundary (UI Seat Layer vs. Proprietary Data/Statutory Engine)**: Reserve `2` (Terminal Threat $\implies \text{CAP} \le 10\text{Y}$) for seat-licensed application/UI workflows or discretionary research workstations (`CRM`, `ADBE`, `NOW`, `FDS`, `TRI`). Score proprietary non-seat risk/compliance datasets & statutory calculation standards (`REL.GB`, `WKL.NL`, `FICO`) at `1` (Moderate Pressure).
3. **Anti-Drift Rule #3 — Gate 4 vs. Gate 5/6 Orthogonality (No Gate-Bleed)**: Gate 4 measures *business-model and moat longevity only*. Value-dilutive PE M&A rollups (`ROP`), predatory price gouging, or debt-funded buybacks creating negative equity (`FICO`, `MSCI`) must be rejected at **Gate 5 (`5 = 0`)** and/or **Gate 6 (`6 = "N"`)**, never by artificially compressing Gate 4 CAP.

### 3.2 Note, Rationale & Evidence Formatting Requirements
- **`note` (`QUALITATIVE_EVALUATION_SPEC.md:238–248, 331`; `COMPANY_EVALUATION_SPEC.md:226–236, 397`)**:
  - **Quality Pass & Calamity Pass**: Summarize core economic engine, primary moat barrier, 5-macrotrend resilience, and balance sheet verdict. Must end with the mandatory bracketed 5–10Y forward growth formula:
    `[5-10Y g: volume % + price % + mix/reinvestment % - margin drags % + buybacks %]`
  - **Rejected Companies (existing spec)**: State the exact failing gate, the specific operational or financial failure mechanism, and why the company fails the Munger bar. *(Note: `COMPANY_EVALUATION_SPEC.md:481, 525` include `"Downstream gates bypassed per waterfall."` for Gate 2 `CCL` and Gate 3 `NUE` rejects — valid ONLY for Stage 1 Gates 1–3 rejects).*
  - **v7.18 Stage-2 Diagnostic Tag (`ORIGINAL_REQUEST.md` R2 & Acceptance Criteria)**: For Gate 4 and Gate 5 rejects advancing past Gate 3, strip any stale `"Downstream gates bypassed per waterfall."` sentence, ensure CAP references match deterministic `4` (e.g., fix `CRM`'s stale `CAP = 10` note text to `CAP = 5Y`), and append:
    `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`
- **`evidence` (`QUALITATIVE_EVALUATION_SPEC.md:250–255`; `COMPANY_EVALUATION_SPEC.md:238–243`)**: Multi-cycle financial track record (historical ROIC, operating margin trends, cash conversion), segment revenue/profit breakdowns, customer lock-in & empirical pricing power proof, historical M&A record, capital allocation behavior, and debt repayment history.
- **`2r` (`gate_2_reason`)**: Concise failure reason populated ONLY when `2 == "N"`, else null/blank.
- **`3m` (`gate_3m_moat_note`)**: Required text summarizing (1) scored moat archetypes/barriers, (2) empirical proof of moat (ROIC, gross margin stability), and (3) primary erosion vectors.
- **`4n` (`gate_4n_runway_note`)**: Mandatory concise text whenever any `4_* >= 1` (recommended briefly even when all `4_* == 0`), explaining specific competitive force & macrotrend/clock-speed adjustments.
- **`calamity_note`**: Mandatory three-part structured note when `calamity == "Y"` (broken metric, intact moat proof, fix catalyst + kill-switch); else null/blank.

---

## 4. Exhaustive Catalog of Spec Sections, Rules & Tables Needing v7.18 Two-Stage Waterfall Updates (R3)

Under the **v7.18 Two-Stage Munger Waterfall**:
- **Stage 1 (Early Stop at Gates 1–3)**: Unchanged. Failure at Gate 1 (`1 = "N"`), Gate 2 (`2 = "N"`), or unwaived Gate 3 (`3a = "None"` or unwaived `3b = "N"`) halts evaluation immediately and leaves all downstream fields blank/null (`4_*`, `4`, `4n`, `5`, `6` blank when Gate 3 fails).
- **Stage 2 (Full Diagnostic Scorecard across Gates 4–6)**: Any company advancing past Gate 3 (passing `1="Y"`, `2="Y"`, `3a!="None"`, and either `3b="Y"` or `calamity="Y"` waiving `3b="N"`) MUST receive a complete 6-gate scorecard (`4_*`, `4`, `4n`, `5`, and `6` populated), **even when rejected at Gate 4 (`CAP < 15`) or Gate 5 (`5 = 0` without calamity)**.
  - Gate 4 (`CAP < 15`) remains a **non-waivable Anchor Gate**: it clears `calamity` / `calamity_note` (`calamity = ""`) and still rejects at Gate 4 in `phase_results`, while preserving diagnostic `5` and `6`.
  - Gate 5 (`5 = 0` without calamity) still rejects at Gate 5 in `phase_results`, while preserving diagnostic `6`.

### 4.1 `QUALITATIVE_EVALUATION_SPEC.md` — Every Location Requiring Update

| # | Exact Heading / Location | Lines | Current Text / Rule (Old 1-Stage Waterfall) | Required Update for v7.18 Two-Stage Waterfall |
|---|---|---|---|---|
| 1 | `# Qualitative Evaluation Framework Specification (v7.16)` & `## 1. Overview & Evaluator Mandate` intro | `1`, `8` | Title and intro reference `(v7.16)`. | Bump version reference to `(v7.18)`. |
| 2 | `## 1. Overview & Evaluator Mandate` → `### The Evaluator Agent's Core Mindset` → Item 2 | `15` | `"Strict Sequential Waterfall Invariant (with Conditional Calamity Tier on Gates 3b, 5 & 6 Only): Evaluation proceeds strictly in order (Gate 1 -> Gate 6). Normally, at the first gate a company fails, it is immediately rejected and downstream fields are left blank/null."` | Split into **Two-Stage Waterfall**: Stage 1 (Gates 1–3) stops early and leaves downstream fields blank/null on failure; Stage 2 (Gates 4–6) evaluates all remaining gates (`4_*`, `4`, `4n`, `5`, `6`) diagnostically for every company advancing past Gate 3, even on Gate 4 (`CAP < 15`, non-waivable Anchor Gate clearing calamity) or Gate 5 (`5 = 0`) rejection. Keep Calamity Tier rules on `{3b, 5, 6}` when Anchor Gates `1, 2, 3a, 4 >= 15` pass. |
| 3 | `## 3. The 6 Sequential Munger Reject Gates (Rubric & Scoring)` intro & ASCII flow | `44–68` | `"Evaluation must execute strictly in sequence. The first failed gate triggers an immediate reject verdict."` + single linear 6-gate diagram. | Clarify that rejection verdict still follows the first unwaived failed gate, while Gates 4–6 form Stage 2 where `5` and `6` are always scored diagnostically for all Gate-3-advancing companies. |
| 4 | `### Gate 4: Low Disruption Risk & Predictable Runway (15+ Years)` → `Waterfall Action` | `181` | `"If 4 < 15, set result = \"Rejected – G4 Runway (<15Y)\" (keeping 4_*, 4, and 4n populated for auditability) and leave Gates 5–6 completely blank/null."` | Update to: set `result = "Rejected – G4 Runway (<15Y)"`, clear `calamity` / `calamity_note` (non-waivable Anchor Gate), and **continue to evaluate Gate 5 (`5`) and Gate 6 (`6`) diagnostically** (do NOT leave blank/null). |
| 5 | `### Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation` → `Waterfall Action` | `202` | `"If 5 < 1 (i.e. 0), set result = \"Rejected – G5 Management\". Leave Gate 6 completely blank/null."` | Update to: if unwaived `5 < 1` (i.e. `0`), set `result = "Rejected – G5 Management"`, and **continue to evaluate Gate 6 (`6`) diagnostically** (do NOT leave blank/null). |
| 6 | `## 4. Qualitative Synthesis: Notes & Evidence Standards` → `### 4.1 The note Field` → `For Rejected Companies` | `245–248` | Shows Gate 4 reject example (`CRM` note with `CAP = 10`) without `[Diagnostic G5=... | G6=...: ...]`, and does not distinguish Stage 1 vs Stage 2 reject note conventions. | Document that Stage 1 (G1–G3) rejects may state downstream bypass, whereas Stage 2 (G4/G5) rejects must omit `"Downstream gates bypassed per waterfall."` and append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]` (and fix `CRM` `CAP = 5` if `CRM` is used as example). |
| 7 | `## 5. Output Contract: Qualitative JSON Result Schema` → `### Field Mapping & Waterfall Invariant Rules` (rows `5`, `6`, `note`) | `327–328`, `331` | Row `5` (`gate_5_management_score`): `"Null if Gate 1, 2, unwaived 3, or 4 fails"`. Row `6` (`gate_6_cash_and_balance_sheet`): `"Null if Gate 1, 2, unwaived 3, 4, or unwaived 5 fails"`. Row `note`: `"Mandatory summary text (include [5-10Y g: ...] for both Quality pass and Calamity pass)"`. | Update Row `5` nullable rule to: **Null if Gate 1, 2, or unwaived 3 fails; mandatory (`0/1/2`) for all companies advancing past Gate 3 (including Gate 4 rejects)**. Update Row `6` nullable rule to: **Null if Gate 1, 2, or unwaived 3 fails; mandatory (`Y/N`) for all companies advancing past Gate 3 (including Gate 4 and Gate 5 rejects)**. Update Row `note` to mention `[Diagnostic G5=... | G6=...: ...]` for Stage-2 G4/G5 rejects. |
| 8 | `## 6. Ingestion via screener/apply_evaluation.py` | `342` | `"The script validates the waterfall, strips illegal downstream values if any gate failed, updates inputs.csv, and reports the diff."` | Clarify Two-Stage Waterfall scrubbing: strips downstream fields only on Stage 1 failures (`1="N"`, `2="N"`, `3a="None"`, or unwaived `3b="N"`); preserves diagnostic `5` and `6` on Stage 2 (`4 < 15` and `5 = 0`) while still clearing `calamity` if `4 < 15`. |

---

### 4.2 `COMPANY_EVALUATION_SPEC.md` — Every Location Requiring Update

| # | Exact Heading / Location | Lines | Current Text / Rule (Old 1-Stage Waterfall) | Required Update for v7.18 Two-Stage Waterfall |
|---|---|---|---|---|
| 1 | `# Per-Company Evaluation Framework Specification (v7.16)` & `## 1. Overview & Evaluator Mandate` intro | `1`, `8` | Title and intro reference `(v7.16)`. | Bump version reference to `(v7.18)`. |
| 2 | `## 1. Overview & Evaluator Mandate` → `### The Evaluator Agent's Core Mindset` → Item 2 | `15` | `"Sequential Waterfall Invariant ... Normally, at the first gate a company fails, it is immediately rejected and downstream fields are left blank/null."` | Update to **Two-Stage Sequential Waterfall Invariant**: Stage 1 (Gates 1–3) halts and leaves downstream fields blank/null; Stage 2 (Gates 4–6) scores all remaining gates (`4_*`, `4`, `4n`, `5`, `6`) diagnostically for every company advancing past Gate 3 (even when `4 < 15` or `5 = 0`), while `calamity` remains restricted to `{3b, 5, 6}` when Anchor Gates `1, 2, 3a, 4 >= 15` pass. |
| 3 | `## 3. The 6 Sequential Munger Reject Gates (Qualitative Rubric)` intro & ASCII flow | `47–71` | `"Evaluation must execute strictly in sequence. The first failed gate triggers an immediate reject verdict."` | Clarify Stage 1 early stop (Gates 1–3) vs Stage 2 full diagnostic scorecard (Gates 4–6) while first unwaived failure still determines the rejection verdict. |
| 4 | `### Gate 4: Low Disruption Risk & Predictable Runway (15+ Years)` → `Waterfall Action` | `167` | `"If 4 < 15, set result = \"Rejected – G4 Runway (<15Y)\". Leave Gates 5–6 completely blank/null."` | Update to: set `result = "Rejected – G4 Runway (<15Y)"`, clear `calamity` / `calamity_note` if set (non-waivable Anchor Gate), and **continue to evaluate Gate 5 (`5`) and Gate 6 (`6`) diagnostically**. |
| 5 | `### Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation` → `Waterfall Action` | `188` | `"If 5 < 1 (i.e. 0), set result = \"Rejected – G5 Management\". Leave Gate 6 completely blank/null."` | Update to: if unwaived `5 < 1` (i.e. `0`), set `result = "Rejected – G5 Management"`, and **continue to evaluate Gate 6 (`6`) diagnostically**. |
| 6 | `## 4. Qualitative Synthesis: Notes & Evidence Standards` → `### 4.1 The note Field` → `For Rejected Companies` | `233–236` | Gate 4 reject example (`CRM` with `CAP = 10`) lacks `[Diagnostic G5=... | G6=...: ...]` and does not distinguish Stage 1 vs Stage 2 notes. | Add requirement for Stage 2 (Gate 4 / Gate 5) rejects: omit `"Downstream gates bypassed per waterfall."`, state exact CAP/Gate-5 failure, and append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`. |
| 7 | `## 6. Output Contract: Standardized JSON Result Format` → `### Schema Rules & Field Mapping Table` (rows `5`, `6`, `note`) | `393–394`, `397` | Row `5` (`gate_5_management_score`): `"Null if Gate 1, 2, unwaived 3, or 4 fails"`. Row `6` (`gate_6_cash_and_balance_sheet`): `"Null if Gate 1, 2, unwaived 3, 4, or unwaived 5 fails"`. Row `note`: `"Mandatory summary text"`. | Update Row `5` to **Null if Gate 1, 2, or unwaived 3 fails; mandatory (`0/1/2`) for all Gate-3-advancing companies (including Gate 4 rejects)**. Update Row `6` to **Null if Gate 1, 2, or unwaived 3 fails; mandatory (`Y/N`) for all Gate-3-advancing companies (including Gate 4 and Gate 5 rejects)**. Update Row `note` to specify `[Diagnostic G5=... | G6=...: ...]` for Stage-2 G4/G5 rejects. |
| 8 | `## 7. Concrete Worked Examples` → `### Example 4: Gate 4 Rejection (Seat-Based SaaS CRM)` | `539–579` (specifically `567–569`) | `"gate_5_management_score": null`, `"gate_6_cash_and_balance_sheet": null`, `"note"` lacks `[Diagnostic G5=... | G6=...: ...]`. | Update `CRM` Example 4 with its verified `gate_5_management_score` (`0/1/2`), `gate_6_cash_and_balance_sheet` (`Y/N`), and `[Diagnostic G5=... | G6=...: ...]` note suffix so the worked example conforms to v7.18 (note: Examples 2 `CCL` at `451–491` and 3 `NUE` at `495–535` remain valid Stage 1 early-stop examples with `null` G4–G6 and `"Downstream gates bypassed per waterfall."`). |
| 9 | `## 8. Handoff & Update Protocol for the Coordinator Agent` → `### Step 1: Validate Payload & Invariants` | `637–641` | Item 2: `"The waterfall invariant is respected (e.g. if Gate 2 failed, Gates 3–6 must be null)."` | Clarify Two-Stage Waterfall invariant: Stage 1 failures (`1="N"`, `2="N"`, or unwaived Gate 3 failure) require downstream fields to be null; Stage 2 (past Gate 3) requires `4_*`, `4`, `4n`, `5`, and `6` to be populated even on Gate 4 (`4 < 15`) or Gate 5 (`5 = 0`) failure. |

---

## 5. Specification Miner Summary Tables

## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Gate 5 Rubric | Management & Capital Allocation (`5`) | Evaluates leadership across 5 vectors: (a) Integrity & Candor (Fisher/Buffett), (b) Rational Capital Allocation (Murphy/Thorndike, >=12% reinvestment, counter-cyclical buybacks, no empire M&A), (c) Customer Value-for-Money / Consumer Surplus (Bezos/Sleep), (d) Product-Led Execution, (e) Anti-Bureaucracy & Planned Abandonment (Wallenberg/Drucker). | Qualitative leadership record, SBC, non-GAAP vs GAAP, M&A history, pricing practices, SG&A, insider ownership | `5` in `{0, 1, 2}` (`0`=Red Flag REJECT, `1`=Standard Pass, `2`=Elite Compounder) | `5 < thr_culture (1)` -> `Rejected – G5 Management` unless `calamity="Y"` waives; invalid values cleared by `apply_evaluation.py` | `QUALITATIVE_EVALUATION_SPEC.md:185-202`, `COMPANY_EVALUATION_SPEC.md:171-188`, `screener/config.py:195-204` |
| 2 | Gate 6 Rubric | Three Compounding Pillars (`6`) | Evaluates: Pillar 1 Peak-to-Peak Owner EPS compounding (`p2p_ok`), Pillar 2 Real FCF Conversion (Multi-year Owner FCF >= 80% GAAP NI, `fcf_conv >= 0.80`), Pillar 3 Peace-of-Mind Balance Sheet (survive multi-year depression / credit freeze without "kindness of strangers"). | Multi-year Owner EPS, FCF/NI, Net Debt/Owner Earnings (`g6_netdebt_yrs <= 4.0y`), EBIT/Interest (`g6_intcov > 5.0x`), Solvency II, sub-industry `g6_default` | `6` in `{"Y", "N"}` | `6 == "N"` -> `Rejected – G6 Cash & Fortress Balance Sheet` unless `calamity="Y"` waives | `QUALITATIVE_EVALUATION_SPEC.md:206-232`, `COMPANY_EVALUATION_SPEC.md:192-218`, `QUANTITATIVE_EVALUATION_SPEC.md:203-205` |
| 3 | Gate 6 Special Rules | Industry & Capital Structure Rules | (1) Essential Infrastructure/Concessions (freight rails, landfills, toll concessions) pass if `g6_intcov > 5x`; (2) Insurers/HoldCos evaluated on Solvency II > 200%, underwriting, look-through earnings (`g6_checks` sets `netdebt`/`intcov`=`n/a`); (3) Commercial fractional-reserve banks = automatic `N` (`g6_default="N"`); (4) Regulated utilities = `g6_default="N"`; (5) Surplus cash/T-bills count toward fortress; (6) Disqualifying Red Flags (auto `N`): debt-funded peak buybacks causing negative tangible/book equity (`FICO`, `MSCI`), serial debt/dilution rollups, short-term CP/capital-market reliance. | `sub_industry`, `g6_default`, Solvency II, interest coverage, tangible/book equity, buyback/debt history | `6 = "Y"` or `"N"` | Automatic `"N"` on commercial banks, debt-funded buyback negative equity, serial debt rollups, CP dependence | `QUALITATIVE_EVALUATION_SPEC.md:35, 225-231`, `COMPANY_EVALUATION_SPEC.md:35, 211-217, 583-623`, `data/us/prescreen.csv:50,58,134-138`, `screener/gates.py:347-368` |
| 4 | Anti-Drift Rules | Calibration & No Gate-Bleed (#1–#3) | #1 Sub-Industry Peer Benchmarking (score cross-Atlantic/global peers on identical yardstick); #2 `4_sub`/`4_riv` 1 vs 2 boundary (UI seat workflows `2` vs proprietary non-seat data/statutory engines `1`); #3 Gate 4 vs Gate 5/6 Orthogonality (reject PE rollups `ROP` at G5 `5=0` and debt buybacks `FICO`/`MSCI` at G6 `6="N"`, never via Gate 4 CAP). | Sector, sub-industry, peer scores, business model type | Calibrated `3_*`, `4_*`, `5`, `6` scores | Cross-gate bleed or US/EU split drift prohibited | `QUALITATIVE_EVALUATION_SPEC.md:177-180`, `COMPANY_EVALUATION_SPEC.md:163-166`, `ORIGINAL_REQUEST.md:18` |
| 5 | Synthesis Formats | `note`, `evidence`, `4n`, `calamity_note` | `note`: Quality/Calamity Pass requires `[5-10Y g: ...]`; v7.18 Stage-2 G4/G5 rejects strip `"Downstream gates bypassed per waterfall."` and append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`. `calamity_note` requires 3 parts (broken metric, moat proof, catalyst+kill-switch). `4n` mandatory when any `4_* >= 1`. | Qualitative verdict, gate scores, financial evidence | Formatted strings in CSV/JSON | `apply_evaluation.py` errors if `calamity="Y"` lacks `calamity_note` or any `4_* >= 1` lacks `4n` | `QUALITATIVE_EVALUATION_SPEC.md:176, 236-256, 330-332`, `COMPANY_EVALUATION_SPEC.md:222-244`, `ORIGINAL_REQUEST.md:20` |
| 6 | Waterfall Spec Audit | v7.18 Two-Stage Waterfall Spec Gaps | Both `QUALITATIVE_EVALUATION_SPEC.md` and `COMPANY_EVALUATION_SPEC.md` currently carry `v7.16`, enforce 1-stage blanking of `5`/`6` on Gate 4 `<15` and `6` on Gate 5 `=0`, and show `null` G5/G6 in `CRM` Example 4. | `QUALITATIVE_EVALUATION_SPEC.md` (8 locations), `COMPANY_EVALUATION_SPEC.md` (9 locations) | Updated spec prose, waterfall actions, nullable tables, Example 4 (`CRM`) | Old 1-stage spec contradicts R1–R4 Two-Stage Waterfall behavior | Line-by-line inspection of both spec files |

## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Gate 4 CAP < 15 + Calamity Flag | `1="Y"`, `2="Y"`, `3a!="None"`, `4 < 15`, `calamity="Y"`, `5=1`, `6="Y"` | Gate 4 is a non-waivable Anchor Gate: `calamity` and `calamity_note` MUST be cleared (`""`), `phase_results` rejects at Gate 4 (`Rejected – G4 Runway (<15Y)`), while under v7.18 diagnostic `5` and `6` are preserved (spec currently says leave 5–6 blank/null -> must update). |
| 2 | Gate 5 = 0 without Calamity | `1="Y"`, `2="Y"`, `3a!="None"`, `3b="Y"`, `4 >= 15`, `5=0`, `calamity=""`, `6="N"` | `phase_results` rejects at Gate 5 (`Rejected – G5 Management`); under v7.18 diagnostic `6` is preserved rather than scrubbed (spec currently says leave Gate 6 blank/null -> must update). |
| 3 | Gate 6 Regulated Utilities & Banks with `g6_default = "N"` | Blank `6` vs explicit `6 = "N"` for `Utilities` or `Diversified/Regional Banks` | In `gates.py:171`, blank `6` falls back to `g6_default` (`"N"`), which still evaluates Gate 6 as `"fail"`. However, R1 `audit_gate_3_universe` in v7.18 requires explicit non-empty `5` and `6` for all 485 Gate-3-advancing companies (zero blank G5/G6 allowed). |
| 4 | Gate 6 Quantitative Flags (`g6_checks`) vs Qualitative `6` | Infrastructure/concessions or HoldCos failing `g6_netdebt_yrs <= 4.0` or `fcf_conv >= 0.80` | `g6_checks` only renders dashboard review flags (`✓ / ⚠ / –`) and never rejects or feeds DCF (`QUANTITATIVE_EVALUATION_SPEC.md:203`, `gates.py:348`). Qualitative Gate 6 (`6 = "Y"` or `"N"`) is authoritative (e.g., rails/landfills/concessions pass with `>5x` interest cover; insurers evaluated on Solvency II > 200%). |
| 5 | Stage 1 Failures (Gates 1–3) | `1="N"`, `2="N"`, `3a="None"`, or unwaived `3b="N"` | Unchanged in v7.18: early stop remains strictly enforced (`4_*`, `4`, `4n`, `5`, `6` remain blank/null; Examples 2 `CCL` and 3 `NUE` stay valid). |
| 6 | Stale `CRM` CAP in Spec & Note | `CRM` in `COMPANY_EVALUATION_SPEC.md:565–569` & `inputs.csv` | `COMPANY_EVALUATION_SPEC.md` Example 4 already computes `gate_4_runway_cap: 5`, but shows `gate_5_management_score: null` and `gate_6_cash_and_balance_sheet: null` (needs v7.18 diagnostic G5/G6 + note update). |
