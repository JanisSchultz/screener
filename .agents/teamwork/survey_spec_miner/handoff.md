# Comprehensive Evaluation Framework Specification Mining Report (v7.16)

**Target File**: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_spec_miner/handoff.md`  
**Author**: Specification Miner (`survey_spec_miner`)  
**Date**: 2026-11-16  
**Authoritative Sources**:
- `QUALITATIVE_EVALUATION_SPEC.md` (v7.16)
- `COMPANY_EVALUATION_SPEC.md` (v7.16)
- `screener/config.py`
- `screener/gates.py`
- `screener/apply_evaluation.py`
- `tests/test_cap_engine.py`, `tests/test_calamity_tier.py`
- `data/us/inputs.csv`, `data/eu/inputs.csv`, `data/ca/inputs.csv`

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Gate 3 Moat Profiles | Moat Archetype Sub-Scores (`3_tb`, `3_ia`, `3_se`, `3_rd`) | Orthogonal 4-archetype moat scoring on `0/1/2` scale | Four integers $\in \{0, 1, 2\}$ | Sub-scores stored in CSV/JSON | Invalid values stripped; partial sub-scores yield `C.RES_REVIEW` | `config.py:51-57,123-142`, `gates.py:41-60` |
| 2 | Gate 3 Moat Profiles | Deterministic Step 1 Initial CAP (`CAP_init`) | Calculates Initial CAP (0Y to 30Y) based on $m_{\max}$ and $m_{\text{sum}}$ | `(s_tb, s_ia, s_se, s_rd)` tuple | Integer $\in \{0, 15, 20, 25, 30\}$ | $m_{\max}=0 \implies \text{CAP}_{\text{init}}=0\text{Y}$ (Gate 3 Reject) | `gates.py:41-60`, `test_cap_engine.py:30-46` |
| 3 | Gate 3 Moat Profiles | Primary Moat Archetype Derivation (`3a`) | Deterministically derives or validates primary moat label from top-scoring archetype | `3_*` scores + optional supplied `3a` | Canonical archetype string or `"None"` | Cleared/corrected to max archetype if supplied label invalid or sub-max | `apply_evaluation.py:198-210`, `gates.py:108-117` |
| 4 | Gate 3 Moat Profiles | Moat Label Alias Normalization | Normalizes historical/legacy moat labels to canonical 4-archetype strings | Legacy string (e.g. `"R&D super-thinkers"`) | Canonical string | Non-empty unmapped string preserved with warning | `config.py:70-75`, `gates.py:31-39` |
| 5 | Gate 3b Proof & Pricing | Gate 3b Empirical Return & Pricing Power | Requires structural moat, 5Y median GAAP ROIC $\ge 12\%$, ROIIC $\ge 12\%$, and pricing $\ge$ inflation | `3a`, `3b` (`"Y"`/`"N"`), financial history | Gate pass/fail status | Fails if `3a=="None"` or `3b=="N"`; waivable ONLY if calamity='Y' | `QUALITATIVE_EVALUATION_SPEC.md:127-143`, `gates.py:177-185` |
| 6 | Gate 3 Moat Profiles | Moat & Erosion Note (`3m`) | Mandatory qualitative synthesis of moat barriers, empirical proof, and erosion vectors | String text | Populated `3m` column | Downstream scrubbed if Gate 1 or 2 fails | `QUALITATIVE_EVALUATION_SPEC.md:140-142`, `config.py:155-156` |
| 7 | Gate 4 Competitive Forces | Porter's 5 Forces Sub-Scores (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`) | Evaluates 15–30Y secular trajectory across 5 forces on `0/1/2` scale via 5 Macrotrends & clock speed | Five integers $\in \{0, 1, 2\}$ | Sub-scores stored in CSV/JSON | Invalid values stripped; partial sub-scores yield `C.RES_REVIEW` | `config.py:59-66,158-182`, `gates.py:74-90` |
| 8 | Gate 4 Competitive Forces | Mauboussin Clock-Speed Presumption | Fast-clock-speed industries (tech, semi, pharma, hardware) carry presumptive `4_sub >= 1` | Sub-industry classification | Default `4_sub >= 1` unless physically unbypassable | Must be justified in `4n` if overridden to 0 | `QUALITATIVE_EVALUATION_SPEC.md:157-160`, `config.py:178-182` |
| 9 | Gate 4 Competitive Forces | Tiered Moderate Force Haircut $h(c_1)$ | Non-linear haircut preventing double-counting of correlated moderate frictions: $h(0)=0, h(1\text{–}2)=5, h(3\text{–}4)=10, h(5)=15$ | Count of force scores equal to 1 ($c_1$) | Integer haircut $\in \{0, 5, 10, 15\}$ | None | `gates.py:62-72`, `test_cap_engine.py:49-56` |
| 10 | Gate 4 Competitive Forces | Fatal-Flaw Cap ($c_2 \ge 1$) | Any single Force $= 2$ caps Final CAP at $\le 10\text{Y}$, causing immediate Gate 4 rejection | Count of force scores equal to 2 ($c_2$) | Final CAP $\in \{0, 5, 10\}$ | Triggered automatically; non-waivable | `gates.py:74-90`, `test_cap_engine.py:64-75` |
| 11 | Gate 4 Competitive Forces | Deterministic Step 2 Final CAP (`4`) | Computes final CAP deterministically: $\max(5, \text{CAP}_{\text{init}} - h(c_1))$ or fatal cap | $\text{CAP}_{\text{init}}$ and 5 force scores | Integer $\in \{0, 5, 10, 15, 20, 25, 30\}$ | Overwrites any manual override in payload | `apply_evaluation.py:212-222`, `gates.py:74-90` |
| 12 | Gate 4 Competitive Forces | Mandatory Runway & Forces Note (`4n`) | Explains competitive force adjustments whenever any Force $\ge 1$; records insulation when 0 | String text | Populated `4n` column | Mandatory when any force $\ge 1$; cleared if upstream gate fails | `QUALITATIVE_EVALUATION_SPEC.md:176`, `config.py:192-193` |
| 13 | Calamity Tier | Conditional Calamity Waiver (`calamity="Y"`) | Waives failure on Gates `3b`, `5`, and/or `6` for temporary fixable calamities | `calamity="Y"`, raw failing values | Funnel status `C.RES_CALAMITY` | Invalid if any Anchor Gate (1, 2, 3a, 4) fails, or if no eligible gate fails | `config.py:239-245`, `gates.py:192-223`, `apply_evaluation.py:293-300` |
| 14 | Calamity Tier | Structured Calamity Note (`calamity_note`) | 3-part note: (1) broken metric, (2) intact moat proof, (3) fix catalyst & kill-switch | String text | Populated `calamity_note` | Cleared with warning if `calamity != "Y"` or Anchor Gate fails | `QUALITATIVE_EVALUATION_SPEC.md:15,325-326`, `apply_evaluation.py:145-148` |
| 15 | Evaluation Ingestion | Ingestion & Waterfall Enforcement Engine | Ingests JSON evaluation payloads, enforces waterfall clearing, verifies mirror parity | JSON payload file / stdin | Updated `inputs.csv` rows | Strips invalid downstream data; logs precise warnings | `apply_evaluation.py:123-300` |
| 16 | Cross-Universe Mirroring | Dual-Listed Mirror Synchronization | Ensures dual-listed tickers (e.g. `ASML` / `ASML.NL`) share identical qualitative sub-scores | Cross-universe rows | Identical qualitative values | Test suite asserts exact field-by-field equality | `README.md:69`, `test_cap_engine.py:223-226` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Gate 3 Initial CAP | All moat scores zero `(0, 0, 0, 0)` | `compute_initial_cap_from_scores` returns `0`. `apply_evaluation.py` sets `3a = "None"`. Gate 3 immediately fails (`C.RES_REJ[3]`). Downstream fields scrubbed. |
| 2 | Gate 3 Initial CAP | Four moderate moats `(1, 1, 1, 1)` | `m_max = 1`, `m_sum = 4`. Returns `20Y` (capped at 20Y because no single elite score of 2 exists). |
| 3 | Gate 3 Initial CAP | Single elite moat with no supporting moats `(2, 0, 0, 0)` | `m_max = 2`, `m_sum = 2`. Returns `20Y`. |
| 4 | Gate 3 Initial CAP | Elite moat plus one moderate `(2, 1, 0, 0)` or `(0, 2, 1, 0)` | `m_max = 2`, `m_sum = 3`. Returns `25Y`. |
| 5 | Gate 3 Initial CAP | Dual elite moats `(2, 2, 0, 0)` | `m_max = 2`, `m_sum = 4`. Returns `30Y`. |
| 6 | Gate 3 Primary Moat Derivation | Tie at maximum score (e.g. `ASML`: tb=2, ia=2, rd=2) | If supplied `3a` is in `top_archs` (e.g. `"R&D & innovation leadership"`), it is preserved. If supplied `3a` is invalid or absent, defaults to first in canonical order (`"Toll booth & switching costs"`). |
| 7 | Gate 3 Primary Moat Derivation | Supplied `3a` has score lower than $m_{\max}$ | Evaluator supplies `3a = "Scale economies shared"` (score 0), but `3_tb = 2`. `apply_evaluation.py` overwrites `3a` to `"Toll booth & switching costs"` with an alignment warning. |
| 8 | Gate 4 Deterministic CAP | Evaluator provides manual override `gate_4_runway_cap: 30`, but formula computes `25` | `apply_evaluation.py` overwrites manual 30 with deterministic 25 and logs a warning. Manual overrides are strictly impossible. |
| 9 | Gate 4 Fatal-Flaw Cap | Single Force $= 2$ with $\text{CAP}_{\text{init}} = 30\text{Y}$, no moderate forces | $c_2 = 1, c_1 = 0$. $\text{rem} = 30 - 10 - 0 = 20 \ge 10 \implies \text{CAP}_{\text{final}} = 10\text{Y}$. (Immediate reject $< 15$). |
| 10 | Gate 4 Fatal-Flaw Cap | Single Force $= 2$ with $\text{CAP}_{\text{init}} = 20\text{Y}$, three moderate forces ($c_1 = 3$) | $c_2 = 1, c_1 = 3$. $h(3) = 10\text{Y}$. $\text{rem} = 20 - 10 - 10 = 0 \le 5 \implies \text{CAP}_{\text{final}} = 5\text{Y}$. |
| 11 | Gate 4 Fatal-Flaw Cap | Single Force $= 2$ on $\text{CAP}_{\text{init}} = 15\text{Y}$ | $c_2 = 1$. $\text{rem} = 15 - 10 - 0 = 5 < 10 \implies \text{CAP}_{\text{final}} = 5\text{Y}$. |
| 12 | Gate 4 Fatal-Flaw Cap | Two Forces $= 2$ ($c_2 = 2$) on any Initial CAP | Returns $\text{CAP}_{\text{final}} = 5\text{Y}$ regardless of $\text{CAP}_{\text{init}}$ or moderate forces. |
| 13 | Gate 4 Fatal-Flaw Cap | Three or more Forces $= 2$ ($c_2 \ge 3$) | Returns $\text{CAP}_{\text{final}} = 0\text{Y}$ immediately. |
| 14 | Gate 4 Non-Fatal Deductions Floor | $\text{CAP}_{\text{init}} = 15\text{Y}$, all five forces moderate ($c_1 = 5, c_2 = 0$) | Haircut $h(5) = 15\text{Y}$. $\text{CAP}_{\text{init}} - h = 15 - 15 = 0$. Floored at $\max(5, 0) = 5\text{Y}$. |
| 15 | Calamity Attempt on Anchor Gate | Evaluator sets `calamity = "Y"` on company with `1 = "N"`, `2 = "N"`, `3a = "None"`, or `4 < 15` | `clear_calamity()` is triggered immediately: `calamity` and `calamity_note` are scrubbed, verdict set to `Rejected – G[X]`, and downstream gates cleared. |
| 16 | Calamity Attempt with No Failed Gates | Evaluator sets `calamity = "Y"`, but company passes all gates cleanly (3b=Y, 5>=1, 6=Y) | Detected by `apply_evaluation.py:293-300`. Warning issued: *"Calamity flag 'Y' is set, but no eligible gate (3b, 5, or 6) failed."* |
| 17 | Calamity on Gate 3b | `3a != "None"`, `3b = "N"`, `calamity = "Y"`, Anchor Gates pass | Gate 3b is waived. Gates 4, 5, and 6 are NOT cleared; they are evaluated fully. Stock achieves `Calamity pass` verdict and enters Quantitative PAR valuation. |
| 18 | Incomplete Sub-scores | Evaluator populates 3 of 4 moat scores, or 4 of 5 force scores | `cap_audit()` marks `moat_partial` or `force_partial`. Result evaluates to `"To review (blank gate)"` (`C.RES_REVIEW`). Downstream gates cannot evaluate. |

---

## 1. Observation

### 1.1 Gate 3 Moat Profiles & Scoring Architecture

From `QUALITATIVE_EVALUATION_SPEC.md` (§3, lines 105–143), `COMPANY_EVALUATION_SPEC.md` (§3, lines 108–140), `screener/config.py` (lines 51–57, 122–156), and `screener/gates.py` (lines 41–60):

#### 1. The 4 Orthogonal Moat Archetypes
The framework defines exactly four orthogonal moat archetypes scored on integer scale **`0 / 1 / 2`**:
- **`0`**: Absent / Negligible moat.
- **`1`**: Supporting / Moderate moat (solid, defensible, but not dominant on a global scale).
- **`2`**: Primary / Elite moat (unassailable, sovereign-grade, or world-class compounder barrier).

The four canonical fields and specifications:
1. **`3_tb` — Toll Booth & Switching Costs**:
   - *Definition*: Strength of network effects, embedded software/data workflow lock-in, and contractual or operational customer switching barriers.
   - *Examples*: S&P Global (`SPGI`=2), Microsoft (`MSFT`=2), Visa (`V`=2), Salesforce (`CRM`=2).
2. **`3_ia` — Irreplaceable Infrastructure & Intangibles**:
   - *Definition*: Strength of physically or legally unreplicable infrastructure, distribution/hub density networks, concessions/permits, regulatory licenses, proprietary datasets, and Lindy brands.
   - *Examples*: Waste Management (`WM`=2), Hermès (`RMS.FR`=2), CN Rail (`CNR.CA`=2), Hershey (`HSY`=2), S&P Global (`SPGI`=2).
3. **`3_se` — Scale Economies Shared**:
   - *Definition*: **Strictly the Nick Sleep model** — deliberately passing operational unit-cost efficiencies back to customers via lower prices or superior consumer surplus to compound volume and widen unit-cost advantage. Standard margin-maximizing businesses with physical scale score on `3_ia`, NOT `3_se`.
   - *Examples*: Costco (`COST`=2), Walmart, Progressive.
4. **`3_rd` — R&D & Innovation Leadership**:
   - *Definition*: Strength of proprietary engineering know-how, continuous R&D velocity, and active product/process frontier leadership.
   - *Examples*: ASML (`ASML`/`ASML.NL`=2), KLA, Intuitive Surgical.

*(Note on prompt terminology: The user dispatch prompt referred to these as "Tollbridge (`3_tb`), Intangible Assets (`3_ia`), Switching Costs (`3_se`), Reinvestment Runway (`3_rd`)". In the authoritative code and specs, `3_tb` combines Toll Booth & Switching Costs, `3_ia` covers Infrastructure & Intangibles, `3_se` is Scale Economies Shared, and `3_rd` is R&D & Innovation Leadership. Downstream agents must strictly use the canonical keys `3_tb`, `3_ia`, `3_se`, and `3_rd` and canonical definitions).*

#### 2. Step 1 Deterministic Initial CAP (`CAP_init`) Derivation
Let $m_{\max} = \max(s_{\text{tb}}, s_{\text{ia}}, s_{\text{se}}, s_{\text{rd}})$ and $m_{\text{sum}} = s_{\text{tb}} + s_{\text{ia}} + s_{\text{se}} + s_{\text{rd}}$:

$$\text{CAP}_{\text{init}} = \begin{cases} 
0\text{Y} & \text{if } m_{\max} = 0 \quad (\implies 3a = \text{"None"}, \text{fails Gate 3}) \\
15\text{Y} & \text{if } m_{\max} = 1 \text{ and } m_{\text{sum}} = 1 \\
20\text{Y} & \text{if } m_{\max} = 1 \text{ and } m_{\text{sum}} \ge 2 \quad (\text{capped at 20Y without an elite } 2) \\
20\text{Y} & \text{if } m_{\max} = 2 \text{ and } m_{\text{sum}} = 2 \quad (\text{single elite } 2, \text{no supporting moats}) \\
25\text{Y} & \text{if } m_{\max} = 2 \text{ and } m_{\text{sum}} = 3 \quad (\text{one elite } 2 + \text{one supporting } 1) \\
30\text{Y} & \text{if } m_{\max} = 2 \text{ and } m_{\text{sum}} \ge 4 \quad (\text{dual elite } 2\text{s, or one elite } 2 + \ge 2 \text{ supporting } 1\text{s})
\end{cases}$$

#### 3. Derived Primary Moat Archetype (`3a`) & Tie-Breaking Rules
From `screener/apply_evaluation.py` (lines 198–210) and `screener/gates.py` (lines 108–117):
- **Canonical Allowed Values**:
  1. `"Toll booth & switching costs"`
  2. `"Irreplaceable infrastructure & intangibles"`
  3. `"Scale economies shared"`
  4. `"R&D & innovation leadership"`
  5. `"None"`
- **Rule 1 (Zero Moat)**: If $m_{\max} = 0$, `3a` is strictly set to `"None"`. Any supplied value is overwritten.
- **Rule 2 (Single Maximum)**: If exactly one archetype achieves $m_{\max} > 0$, `3a` must match that archetype.
- **Rule 3 (Tie-Breaking Among Multiple Maximums)**:
  - If multiple archetypes share the maximum score (e.g. `ASML` has $s_{\text{tb}}=2, s_{\text{ia}}=2, s_{\text{rd}}=2$), and the evaluator explicitly supplied one of those tying archetypes (e.g. `"R&D & innovation leadership"`), **the evaluator's choice is respected and preserved**.
  - If the evaluator supplied an archetype whose score is $< m_{\max}$, or left `3a` blank, the tie-breaker deterministically selects the **first** archetype in canonical specification order:
    1. `"Toll booth & switching costs"` (`3_tb`)
    2. `"Irreplaceable infrastructure & intangibles"` (`3_ia`)
    3. `"Scale economies shared"` (`3_se`)
    4. `"R&D & innovation leadership"` (`3_rd`)

#### 4. Gate 3 Pass / Fail / Calamity Thresholds
- **Pass (`Y`)**: Requires a structural moat (`m_max >= 1`, `3a != "None"`) AND empirical proof of moat via historical capital efficiency (**5-Year Median GAAP ROIC $\ge 12\%$** AND **Incremental ROIIC $\ge 12\%$** across the cycle, or tangible ROIC $\ge 15\%$) AND demonstrated **Pricing Power $\ge$ Inflation** without customer churn. Recorded as `3b = "Y"`.
- **Fail (`N`)**:
  - If $m_{\max} = 0$: `3a = "None"` $\implies$ automatic, non-waivable Gate 3 REJECT (`result = "Rejected – G3 Moat & Pricing"`). Downstream Gates 4–6 are cleared.
  - If $m_{\max} \ge 1$ but ROIC $< 12\%$ or pricing power is absent: `3b = "N"`. Without a calamity override, this triggers an immediate Gate 3 REJECT.
- **Calamity Waiver**: If $m_{\max} \ge 1$ (`3a != "None"`) and Anchor Gates 1, 2, 3a, 4 pass, a failing `3b = "N"` can be waived under the Calamity tier (`calamity = "Y"` + `calamity_note`), allowing downstream evaluation.

---

### 1.2 Gate 4 Competitive Forces & Deterministic CAP Engine

From `QUALITATIVE_EVALUATION_SPEC.md` (§3, lines 146–178), `COMPANY_EVALUATION_SPEC.md` (§3, lines 143–165), `screener/config.py` (lines 59–66, 158–193), and `screener/gates.py` (lines 62–90):

#### 1. Porter's 5 Competitive Forces Evaluated via 5 Macrotrends
Each force is scored on **`0 / 1 / 2`** reflecting the secular 15–30 year trajectory ($\Delta$):
- **`0`**: Benign / Insulated / Secular Tailwind.
- **`1`**: Moderate / Manageable Secular Pressure.
- **`2`**: Severe / Terminal Structural Threat (**Fatal Flaw**).

The 5 Force Codes:
1. **`4_ent` — Threat of New Entrants**: Secular risk of falling entry barriers (AI software build costs falling, deregulation, subsidized entrants).
2. **`4_riv` — Competitive Rivalry**: Secular risk of intensifying price, promotional, or capex competition among incumbents (e.g. hyperscaler AI capex race).
3. **`4_buy` — Customer Bargaining Power**: Secular risk of rising buyer leverage (customer consolidation, AI seat compression, multi-homing).
4. **`4_sup` — Supplier Bargaining Power**: Secular risk of rising upstream input/labor leverage (single-source foundry/optics bottlenecks, skilled labor scarcity, geopolitical supply concentration).
5. **`4_sub` — Threat of Substitution & Clock Speed**: Secular paradigm substitution (agentic AI replacing seat SaaS, GLP-1s, energy transition).
   - **Mauboussin Outside-View Clock-Speed Rule**: Fast-clock-speed tech, semi, pharma/biotech, and hardware sub-industries carry a **presumptive `4_sub >= 1`** unless protected by an unbypassable physical or protocol standard (e.g. ASML's EUV physics).

**Mandatory 5-Macrotrend Lens**: Every force must be evaluated against:
`[1] Automation & Cognitive Tech (AI)`  
`[2] Demographic Aging & Labor Scarcity`  
`[3] Geopolitical Realignment & Supply Chain Reshoring`  
`[4] Energy Transition & Resource Limits`  
`[5] Structural Inflation & Cost of Capital`

#### 2. Deterministic Final CAP Formula & Table
Let:
- $c_2 = \sum_{i=1}^5 \mathbf{1}(f_i = 2)$ (count of Fatal Flaws)
- $c_1 = \sum_{i=1}^5 \mathbf{1}(f_i = 1)$ (count of Moderate Pressures)

**Tiered Moderate Haircut Function $h(c_1)$**:
$$h(c_1) = \begin{cases} 
0\text{Y} & \text{if } c_1 = 0 \\
5\text{Y} & \text{if } c_1 \in \{1, 2\} \\
10\text{Y} & \text{if } c_1 \in \{3, 4\} \\
15\text{Y} & \text{if } c_1 = 5 
\end{cases}$$
*(Tiered grouping prevents double-counting of correlated moderate industry frictions).*

**Final CAP Determination**:
1. **Fatal-Flaw Branch ($c_2 \ge 1$)**: Any single Force $= 2$ caps $\text{CAP}_{\text{final}} \le 10\text{Y}$, guaranteeing immediate Gate 4 rejection (`thr_cap = 15`):
   - If $c_2 \ge 3 \implies \mathbf{0\text{Y}}$
   - If $c_2 = 2 \implies \mathbf{5\text{Y}}$
   - If $c_2 = 1$:
     $$\text{rem} = \text{CAP}_{\text{init}} - 10 - h(c_1)$$
     $$\text{CAP}_{\text{final}} = \begin{cases} \mathbf{10\text{Y}} & \text{if } \text{rem} \ge 10 \\ \mathbf{5\text{Y}} & \text{if } \text{rem} < 10 \end{cases}$$
2. **No Fatal Flaw ($c_2 = 0$)**:
   $$\text{CAP}_{\text{final}} = \max\big(5,\; \text{CAP}_{\text{init}} - h(c_1)\big)$$

**Lookup Matrix of Final CAP ($\text{CAP}_{\text{final}}$) for $c_2 = 0$**:

| Initial CAP ($\text{CAP}_{\text{init}}$) | $c_1 = 0$ ($h=0\text{Y}$) | $c_1 \in \{1, 2\}$ ($h=5\text{Y}$) | $c_1 \in \{3, 4\}$ ($h=10\text{Y}$) | $c_1 = 5$ ($h=15\text{Y}$) |
|---|---|---|---|---|
| **30Y** | **30Y** (Pass) | **25Y** (Pass) | **20Y** (Pass) | **15Y** (Pass) |
| **25Y** | **25Y** (Pass) | **20Y** (Pass) | **15Y** (Pass) | 10Y (*Reject*) |
| **20Y** | **20Y** (Pass) | **15Y** (Pass) | 10Y (*Reject*) | 5Y (*Reject*) |
| **15Y** | **15Y** (Pass) | 10Y (*Reject*) | 5Y (*Reject*) | 5Y (*Reject*) |

#### 3. Rule for Mandatory Runway & Forces Note (`4n`)
- **Trigger**: Mandatory whenever **any competitive force $\ge 1$** ($\sum f_i > 0$). Highly recommended even when all forces are 0.
- **Content Requirements**:
  - When forces $\ge 1$: Must state the Initial CAP, the exact haircut deduction in years, cite the specific non-zero force codes (e.g. `4_buy=1`, `4_sup=1`), provide the concise operational/macrotrend rationale for each, and cite the structural mitigant/insulation.
    *Syntax Standard*: `"Initial CAP [X]Y reduced by -[Y]Y for [force rationale with codes, e.g. 4_buy=1, 4_sup=1]; [insulation factor]."`
  - When Fatal Flaw triggered: Must explicitly declare the fatal cap and why the business model faces structural impairment:
    *Syntax Standard*: `"Fatal-Flaw Cap triggered (Final CAP = [5/10]Y, REJECT): [fatal threat with code 4_*=2] alongside [moderate forces with codes]."`
  - When all forces are 0: Must provide a concise statement of structural insulation:
    *Syntax Standard*: `"[Core moat driver / regulatory barrier] insulates the franchise across all five competitive forces and macrotrends."`

---

### 1.3 Calamity Pass Rules (Gates 3b, 5, and 6)

From `QUALITATIVE_EVALUATION_SPEC.md` (§1, line 15; §5, lines 325–326), `COMPANY_EVALUATION_SPEC.md` (§1, line 15; §6, lines 391–392), `screener/config.py` (lines 239–245), and `screener/gates.py` (lines 192–223):

#### 1. The Anchor Gate Invariant (Never Waivable)
A company **cannot** qualify for a Calamity pass unless all four Anchor Gates pass cleanly:
1. **Gate 1**: `1 == "Y"` (Simple, transparent, verifiable business model).
2. **Gate 2**: `2 == "Y"` (Essential Western need / entrenched habit; `in_market == "Y"`).
3. **Gate 3a**: `3a != "None"` ($m_{\max} \ge 1$; structural moat verified).
4. **Gate 4**: `4 >= 15` ($\text{CAP}_{\text{final}} \ge 15\text{Y}$; predictable 15+ year runway without fatal disruption).

If ANY of these four anchor conditions fails, `clear_calamity()` is invoked immediately, `calamity` and `calamity_note` are scrubbed, the stock is rejected at that gate, and downstream gates are cleared.

#### 2. Eligible Failing Gates: Strictly `{3b, 5, 6}`
A company qualifies for Calamity pass if and only if its failure is strictly confined to:
- **Gate `3b` (`"N"`)**: Temporary capital return or pricing disruption (e.g. extreme cyclical raw material spike like cocoa at Hershey, temporary post-pandemic travel retail inventory glut at Estée Lauder) while gross margin and underlying brand pricing power remain intact.
- **Gate `5` (`0`)**: Historic capital allocation or executive stewardship red flag from a former CEO/regime (e.g. debt-funded peak share repurchases, dilutive empire M&A rollups) where new leadership has been installed to reverse the error.
- **Gate `6` (`"N"`)**: Temporary balance sheet or cash conversion impairment (e.g. temporary bridge debt from transformational M&A, multi-year CapEx buildout spike like Alphabet's 2026 AI infrastructure surge, or temporary FCF conversion $< 80\%$) where operating cash flows remain robust and debt is organic-deleveraging.

#### 3. Mandatory Structured Calamity Note Requirements
`calamity_note` is mandatory whenever `calamity == "Y"`. It must strictly contain three components:
1. **Broken Metric / Failing Gate**: Exact empirical quantification of the failing metric (e.g. ROIC dropped to 7.9%, Net Debt / NI reached 5.12x, interest coverage fell to 3.88x).
2. **Intact Moat Proof**: Empirical proof that the core moat barrier and unit economics are unharmed (e.g. gross margins expanded 230 bps, tangible ROIC $> 30\%$, customer retention $> 95\%$).
3. **Fix Catalyst & Explicit Kill-Switch**: A concrete, time-bound operational catalyst (e.g. new CEO, asset divestiture, CapEx tapering) AND an unambiguous quantitative kill-switch (e.g. *"permanently reject if Net Debt / EBITDA fails to fall below 3.0x by FY2028"*).

#### 4. Downstream Evaluation Behavior
Unlike ordinary gate rejections which clear all downstream fields, a company qualifying under Calamity pass **evaluates all remaining downstream gates** and enters the Quantitative PAR Valuation Funnel under the separate **`Calamity pass`** tier (`C.RES_CALAMITY`).

---

### 1.4 Analysis of the 11 Phase 1 Reference Companies

From `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv`:

#### Empirical Scorecard Table

| ID | Uni | Company Name | G1 | G2 | 3_tb | 3_ia | 3_se | 3_rd | Primary Moat (`3a`) | 3b | 4_ent | 4_riv | 4_buy | 4_sup | 4_sub | $\text{CAP}_{\text{init}}$ | Haircut | Fatal? | CAP (`4`) | G5 | G6 | Calamity | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **SPGI** | us | S&P Global | Y | Y | 2 | 2 | 0 | 0 | Toll booth & switching costs | Y | 0 | 0 | 0 | 0 | 0 | 30Y | 0Y | False | **30Y** | 1 | Y | None | Quality pass |
| **COST** | us | Costco | Y | Y | 1 | 1 | 2 | 0 | Scale economies shared | Y | 0 | 0 | 0 | 0 | 0 | 30Y | 0Y | False | **30Y** | 2 | Y | None | Quality pass |
| **ASML.NL** | eu | ASML | Y | Y | 2 | 2 | 0 | 2 | R&D & innovation leadership | Y | 0 | 0 | 1 | 1 | 0 | 30Y | 5Y | False | **25Y** | 2 | Y | None | Quality pass |
| **ASML** | us | ASML Holding | Y | Y | 2 | 2 | 0 | 2 | R&D & innovation leadership | Y | 0 | 0 | 1 | 1 | 0 | 30Y | 5Y | False | **25Y** | 2 | Y | None | Quality pass |
| **MSFT** | us | Microsoft | Y | Y | 2 | 2 | 0 | 1 | Toll booth & switching costs | Y | 0 | 1 | 0 | 0 | 1 | 30Y | 5Y | False | **25Y** | 1 | Y | None | Quality pass |
| **WM** | us | Waste Management | Y | Y | 1 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 0 | 0 | 0 | 25Y | 0Y | False | **25Y** | 1 | Y | None | Quality pass |
| **RMS.FR** | eu | Hermès | Y | Y | 1 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 0 | 0 | 0 | 25Y | 0Y | False | **25Y** | 2 | Y | None | Quality pass |
| **CNR.CA** | ca | Canadian National Railway | Y | Y | 1 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 0 | 1 | 0 | 25Y | 5Y | False | **20Y** | 1 | Y | None | Quality pass |
| **HSY** | us | Hershey Company | Y | Y | 0 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 1 | 1 | 0 | 20Y | 5Y | False | **15Y** | 1 | Y | None | Quality pass |
| **CRM** | us | Salesforce | Y | Y | 2 | 0 | 0 | 0 | Toll booth & switching costs | Y | 1 | 1 | 1 | 0 | 2 | 20Y | 10Y | **True** | **5Y** | *null* | *null* | None | Rejected – G4 Runway |
| **NUE** | us | Nucor | Y | Y | 0 | 0 | 0 | 0 | None | N | *null* | *null* | *null* | *null* | *null* | 0Y | *null* | False | *null* | *null* | *null* | None | Rejected – G3 Moat |

#### Moat Stacking & Force Combination Patterns
1. **Moat Archetype Coverage**: All 4 canonical archetypes are represented across the reference set:
   - *Toll booth & switching costs*: `SPGI` (2), `MSFT` (2), `CRM` (2).
   - *Irreplaceable infrastructure & intangibles*: `WM` (2), `RMS.FR` (2), `CNR.CA` (2), `HSY` (2), `SPGI` (2), `ASML` (2), `MSFT` (2).
   - *Scale economies shared*: `COST` (2).
   - *R&D & innovation leadership*: `ASML.NL` / `ASML` (2), `MSFT` (1).
   - *Commodity Price Taker (No Moat)*: `NUE` (all 0s).
2. **Moat Stacking Tiers**:
   - $\text{CAP}_{\text{init}} = 30\text{Y}$: `ASML` (triple elite $2+2+2=6$), `MSFT` ($2+2+1=5$), `SPGI` ($2+2=4$), `COST` ($1+1+2=4$).
   - $\text{CAP}_{\text{init}} = 25\text{Y}$: `WM`, `RMS.FR`, `CNR.CA` (all single elite $2$ + supporting $1$ = $3$).
   - $\text{CAP}_{\text{init}} = 20\text{Y}$: `HSY` ($0+2+0+0=2$), `CRM` ($2+0+0+0=2$).
   - $\text{CAP}_{\text{init}} = 0\text{Y}$: `NUE` ($0+0+0+0=0$).
3. **Competitive Force Patterns & Haircuts**:
   - **All 0s (Haircut 0Y)**: `SPGI`, `COST`, `WM`, `RMS.FR`. Completely insulated from all five macrotrends.
   - **Single Moderate Force ($c_1=1$, Haircut 5Y)**: `CNR.CA` (`4_sup=1` for union rail labor / interswitching regulation).
   - **Dual Moderate Forces ($c_1=2$, Haircut 5Y)**:
     - `ASML`: `4_buy=1` (foundry concentration TSMC/Samsung/Intel) + `4_sup=1` (Zeiss optics / export curbs).
     - `MSFT`: `4_riv=1` (hyperscaler capex race) + `4_sub=1` (fast AI technology clock speed).
     - `HSY`: `4_buy=1` (consolidated grocery buyer leverage) + `4_sup=1` (West African cocoa supply shocks).
   - **Fatal Flaw ($c_2=1$, Fatal Cap triggered)**: `CRM`: `4_sub=2` (agentic AI seat substitution) + three moderate forces (`4_ent=1`, `4_riv=1`, `4_buy=1`). Cap capped at 5Y, failing Gate 4.
4. **Mirror Ticker Parity (`ASML` vs `ASML.NL`)**:
   - `ASML` (US) and `ASML.NL` (EU) have **100% identical qualitative sub-scores**:
     - `3_tb=2`, `3_ia=2`, `3_se=0`, `3_rd=2`, `3a="R&D & innovation leadership"`, `3b="Y"`.
     - `4_ent=0`, `4_riv=0`, `4_buy=1`, `4_sup=1`, `4_sub=0`, `4=25`.
     - Identical `3m` and `4n` text.
     - `5=2`, `6="Y"`.

---

## 2. Logic Chain

1. **Step 1 Moat Profile to Initial CAP**:
   - The framework isolates competitive advantage generation into 4 orthogonal archetypes. By taking $m_{\max}$ and $m_{\text{sum}}$, the engine rewards depth (elite score of 2 required to exceed 20Y) and breadth (stacking supporting moats increases Initial CAP from 20Y to 25Y and 30Y).
   - When all moat scores are 0, $m_{\max} = 0$, leading to $\text{CAP}_{\text{init}} = 0\text{Y}$ and `3a = "None"`. Gate 3 fails immediately, and per the Munger reject waterfall, no company can compound capital without an initial moat.

2. **Step 2 Five Forces to Final CAP**:
   - Porter's Five Forces evaluate the secular longevity (decay rate) of the initial moat.
   - The tiered moderate haircut function $h(c_1)$ ($0\text{Y} \rightarrow 5\text{Y} \rightarrow 10\text{Y} \rightarrow 15\text{Y}$) recognizes that moderate competitive headwinds often correlate across forces (e.g. buyer concentration and supplier leverage in hardware). Tiering prevents excessive double-haircutting while ensuring that broad pressure reduces runway.
   - The Fatal-Flaw Cap ($c_2 \ge 1$) enforces Charlie Munger's "tell me where I am going to die" principle: a structural terminal threat (such as agentic AI replacing per-seat software licensing) cannot be diversified away by other benign forces. It immediately caps CAP $\le 10\text{Y}$, triggering rejection at Gate 4 (`thr_cap = 15`).

3. **Strict Determinism and Zero Override**:
   - `apply_evaluation.py` enforces lines 212–222: whenever sub-scores are complete, `qual["4"]` is unconditionally overwritten by `compute_final_cap_from_scores(cap_init_det, f_tuple)`. This guarantees that human or LLM evaluators cannot inflate the runway of favorite companies.

4. **Sequential Waterfall and Calamity Tier Boundary**:
   - In standard mode, failure at Gate $N$ immediately clears all downstream fields ($N+1 \dots 6$).
   - The Buffett Calamity exception exists strictly for fixable operational, managerial, or balance-sheet crises in companies whose structural economic moat is intact. Anchor Gates 1, 2, 3a, and 4 verify that the product is understandable, essential, structurally protected, and has at least a 15-year runway. Only then can temporary failures in 3b (ROIC dip), 5 (bad legacy CEO), or 6 (bridge debt) be waived to allow quantitative valuation.

---

## 3. Caveats

1. **Prompt Terminology vs. Canonical Specification**:
   - The task prompt used informal names: *"Tollbridge (`3_tb`), Intangible Assets (`3_ia`), Switching Costs (`3_se`), Reinvestment Runway (`3_rd`)"*. Downstream evaluator agents must strictly use the canonical names defined in `screener/config.py`:
     - `3_tb`: `"Toll booth & switching costs"`
     - `3_ia`: `"Irreplaceable infrastructure & intangibles"`
     - `3_se`: `"Scale economies shared"`
     - `3_rd`: `"R&D & innovation leadership"`
2. **Sub-score Completeness Requirement**:
   - If an agent provides partial sub-scores (e.g. 3 of 4 moat scores, or 4 of 5 force scores), `apply_evaluation.py` will not guess or default the missing scores. Instead, it logs a warning, and `phase_results()` stops the company as `"To review (blank gate)"`. Evaluators must supply all 4 moat scores and all 5 force scores for any company reaching Gate 3.
3. **Dual-Listed Mirror Synchronization**:
   - While `universe.json` currently has empty `mirrors: {}` objects, mirror parity (e.g. `ASML` in US and `ASML.NL` in EU) is hard-coded and asserted in `tests/test_cap_engine.py` (lines 223–226). Dual-listed companies must have identical qualitative scores and notes across universes.

---

## 4. Conclusion

1. **Gate 3 Scoring**:
   - 4 archetypes (`3_tb`, `3_ia`, `3_se`, `3_rd`) scored on `0 / 1 / 2`.
   - Initial CAP: 0Y (if all 0), 15Y (sum=1), 20Y (sum $\ge 2$ or single 2), 25Y ($2+1$), 30Y ($2+2$ or $2+1+1$).
   - Derived `3a`: Top-scoring archetype, preserving evaluator choice on ties, or defaulting to `MOAT_SCORE_SPEC` order. `"None"` if all 0.
   - Gate 3 Pass: `3a != "None"`, `3b == "Y"`, ROIC $\ge 12\%$, pricing $\ge$ inflation.
2. **Gate 4 Scoring**:
   - 5 forces (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`) scored on `0 / 1 / 2` via 5 Macrotrends & clock speed.
   - Final CAP: Deterministic formula $\max(5, \text{CAP}_{\text{init}} - h(c_1))$ if $c_2 = 0$; capped at $\le 10\text{Y}$ if $c_2 \ge 1$ (immediate reject).
   - Gate 4 Pass: Final CAP $\ge 15\text{Y}$.
   - Mandatory `4n`: Required whenever any force $\ge 1$, following standardized syntax with force codes and macrotrend drivers.
3. **Calamity Rules**:
   - Anchor Gates 1, 2, 3a, 4 must all pass. Only `{3b, 5, 6}` can be waived.
   - Requires structured 3-part `calamity_note`: broken metric, intact moat proof, and turnaround catalyst with explicit kill-switch.
   - Evaluates all downstream gates into the `Calamity pass` tier.
4. **Reference Baseline**:
   - All 11 reference companies (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`) exhibit pristine adherence to the deterministic formulas, note structures, and waterfall invariants.

---

## 5. Verification Method

To independently verify all findings and scoring rules documented in this report:

1. **Run Full Test Suite**:
   ```bash
   python3 -m unittest discover tests
   ```
   *Expected Result*: 169 tests pass with exit code 0.

2. **Verify Deterministic CAP Engine and Reference Companies**:
   ```bash
   python3 -m unittest tests/test_cap_engine.py
   ```
   *Expected Result*: Verifies Initial CAP steps (0, 15, 20, 25, 30), tiered moderate haircuts (0, 5, 10, 15), fatal-flaw caps ($\le 10\text{Y}$), tie-breaking logic for `3a`, and exact score match for all reference companies.

3. **Verify Calamity Tier Invariants & Waterfall Mechanics**:
   ```bash
   python3 -m unittest tests/test_calamity_tier.py
   ```
   *Expected Result*: Verifies that non-waivable anchor gates (1, 2, 3a, 4) reject even with `calamity="Y"`, and that Gates 3b, 5, and 6 qualify for `Calamity pass`.

4. **Verify Mirror Parity on Inputs**:
   ```bash
   python3 -c "
   import csv
   us = {r['id']: r for r in csv.DictReader(open('data/us/inputs.csv'))}
   eu = {r['id']: r for r in csv.DictReader(open('data/eu/inputs.csv'))}
   for k in ('3_tb', '3_ia', '3_se', '3_rd', '3a', '3b', '4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4', '4n', '5', '6'):
       assert us['ASML'][k] == eu['ASML.NL'][k], f'Mismatch on {k}: {us[\"ASML\"][k]} vs {eu[\"ASML.NL\"][k]}'
   print('ASML mirror parity verified successfully.')
   "
   ```
