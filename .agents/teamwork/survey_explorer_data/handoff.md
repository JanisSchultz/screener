# Universe Data Explorer — Investigation & Universe Analysis Report

**Generated**: 2026-11-16  
**Investigator**: Universe Data Explorer (`survey_explorer_data`)  
**Target Path**: `.agents/teamwork/survey_explorer_data/handoff.md`  

---

## Executive Summary

- **Total Universe Population**: 1,175 companies across three universes: US (515), EU (602), and CA (58).
- **Exact Gate 3 Candidate Count**: Exactly **989 companies** reach Gate 3 (pass Gate 1 `1 == 'Y'` and Gate 2 `2 == 'Y'`). The exact per-universe counts are:
  - **US**: 445 companies (out of 515; 14 fail Gate 1, 56 fail Gate 2)
  - **EU**: 495 companies (out of 602; 14 fail Gate 1, 93 fail Gate 2)
  - **CA**: 49 companies (out of 58; 2 fail Gate 1, 7 fail Gate 2)
  - **Total Gate 3 Candidates**: $445 + 495 + 49 = \mathbf{989}$.
- **Scoring Status**: Exactly **11 reference companies** are fully scored under the new Step 1 / Step 2 framework (8 US, 2 EU, 1 CA). The remaining **978 companies** are unscored legacy rows with blank new moat/force fields (`3_tb`, `3_ia`, `3_se`, `3_rd`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4n`).
- **Dual-Listed Mirrors**: Exactly **2 dual-listed pairs** are defined in `data/us/universe.json`:
  1. `ASML` (US) $\leftrightarrow$ `eu:ASML.NL` (EU) [Phase 1 scored reference pair]
  2. `FER` (US) $\leftrightarrow$ `eu:FER.ES` (EU) [Legacy scored pair]
- **Industry & Sector Distribution**: The 989 Gate 3 companies span 11 GICS sectors. The top four sectors represent **61.8%** of the entire cohort: Industrials (214), Financials (188), Information Technology (109), and Health Care (100).

---

## 1. Observation

### 1.1 Input Dataset Schema, Headers, and Data Formats

We inspected `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv`.

#### Column Headers
All three datasets share the same **6 base metadata fields** and the same **23 qualitative & evaluation fields** (totaling 29 common fields). They differ only in market-specific extra columns:

| Universe | File Path | Total Rows | Total Cols | Extra Market Columns |
| :--- | :--- | :---: | :---: | :--- |
| **US** | `data/us/inputs.csv` | 515 | 31 | `in_sp500`, `in_ndx` |
| **EU** | `data/eu/inputs.csv` | 602 | 31 | `exchange`, `index_weight_pct` |
| **CA** | `data/ca/inputs.csv` | 58 | 30 | `exchange` |

#### Field Specification
1. **Base Metadata**: `id`, `ticker`, `company`, `country`, `sector`, `sub_industry`
2. **Extra Columns**:
   - US: `in_sp500` ('Y'/'N'), `in_ndx` ('Y'/'N')
   - EU: `exchange` (text), `index_weight_pct` (float string)
   - CA: `exchange` (text)
3. **Munger Gate 1 & 2**:
   - `1`: 'Y' or 'N' (simple to understand / transparent)
   - `2`: 'Y' or 'N' (essential Western need / habit; blank if failed Gate 1)
   - `2r`: Text reason populated only when Gate 2 is 'N'
4. **Gate 3 Moat Evaluation Fields**:
   - `3_tb`: Toll booth & switching costs score (0, 1, or 2; blank if unscored)
   - `3_ia`: Irreplaceable infrastructure & intangibles score (0, 1, or 2; blank if unscored)
   - `3_se`: Scale economies shared score (0, 1, or 2; blank if unscored)
   - `3_rd`: R&D & innovation leadership score (0, 1, or 2; blank if unscored)
   - `3a`: Primary Moat Archetype (`Toll booth & switching costs`, `Irreplaceable infrastructure & intangibles`, `Scale economies shared`, `R&D & innovation leadership`, or `None`)
   - `3b`: Pricing power $\ge$ inflation ('Y' or 'N')
   - `3m`: Qualitative moat barrier and erosion threat text note
5. **Gate 4 Competitive Forces & Runway CAP**:
   - `4_ent`: Threat of new entrants (0, 1, or 2)
   - `4_riv`: Competitive rivalry (0, 1, or 2)
   - `4_buy`: Customer bargaining power (0, 1, or 2)
   - `4_sup`: Supplier bargaining power (0, 1, or 2)
   - `4_sub`: Threat of substitution (0, 1, or 2)
   - `4`: Deterministic Competitive Advantage Period (CAP) in years (allowed: 0, 5, 10, 15, 20, 25, 30)
   - `4n`: Runway & Forces justification note (mandatory whenever any Porter force is $\ge 1$)
6. **Downstream Gates & Calamity**:
   - `5`: Honest, able, customer-focused management (0, 1, or 2)
   - `6`: Real cash conversion, compounding & balance sheet ('Y' or 'N')
   - `calamity`: 'Y' or blank (Buffett calamity waiver for temporary, fixable Gate 3b/5/6 failures)
   - `calamity_note`: Required note explaining broken metric, intact moat, and fix catalyst
   - `note`: Qualitative summary note (100% populated across all 1,175 rows)
   - `evidence`: Quantitative & financial evidence text (100% populated across all 1,175 rows)

---

### 1.2 Gate 1 & 2 Waterfall and Gate 3 Counts

In the sequential Munger reject waterfall (`screener/gates.py` and `screener/apply_evaluation.py`), a company reaches Gate 3 if and only if it passes Gate 1 (`1 == 'Y'`) and Gate 2 (`2 == 'Y'`).

Exact observed counts across all files:

| Universe | Total Companies | Gate 1 Rejections (`1 == 'N'`) | Gate 2 Rejections (`1 == 'Y', 2 == 'N'`) | Reach Gate 3 (`1 == 'Y', 2 == 'Y'`) |
| :--- | :---: | :---: | :---: | :---: |
| **US** | 515 | 14 | 56 | **445** |
| **EU** | 602 | 14 | 93 | **495** |
| **CA** | 58 | 2 | 7 | **49** |
| **Total** | **1,175** | **30** | **156** | **989** |

- **Verification**: $445 + 495 + 49 = 989$.
- Total rejected prior to Gate 3: $30 + 156 = 186$ companies.
- Every single company failing Gate 1 or Gate 2 has 100% empty downstream fields (`3_tb`, `3_ia`, `3_se`, `3_rd`, `3a`, `3b`, `3m`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, `4`, `4n`, `5`, `6`, `calamity`, `calamity_note`), confirming existing data strictly adheres to waterfall scrub rules.

---

### 1.3 Scored Reference Companies vs Unscored / Legacy Cohort

Among the 989 companies reaching Gate 3:

#### 1. Reference Scored Companies (11 Companies)
Exactly 11 companies were scored under the new Step 1 / Step 2 framework during Phase 1:

| Universe | ID | Ticker | Company Name | Sector | 3_tb | 3_ia | 3_se | 3_rd | 3a (Derived) | 3b | 4_ent | 4_riv | 4_buy | 4_sup | 4_sub | 4 (CAP) | 4n Populated |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **US** | `COST` | COST | Costco | Consumer Staples | 1 | 1 | 2 | 0 | Scale economies shared | Y | 0 | 0 | 0 | 0 | 0 | 30 | Yes |
| **US** | `HSY` | HSY | Hershey Company (The) | Consumer Staples | 0 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 1 | 1 | 0 | 15 | Yes |
| **US** | `SPGI` | SPGI | S&P Global | Financials | 2 | 2 | 0 | 0 | Toll booth & switching costs | Y | 0 | 0 | 0 | 0 | 0 | 30 | Yes |
| **US** | `WM` | WM | Waste Management | Industrials | 1 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 0 | 0 | 0 | 25 | Yes |
| **US** | `CRM` | CRM | Salesforce | Information Technology | 2 | 0 | 0 | 0 | Toll booth & switching costs | Y | 1 | 1 | 1 | 0 | 2 | 5 | Yes |
| **US** | `ASML` | ASML | ASML Holding | Information Technology | 2 | 2 | 0 | 2 | R&D & innovation leadership | Y | 0 | 0 | 1 | 1 | 0 | 25 | Yes |
| **US** | `MSFT` | MSFT | Microsoft | Information Technology | 2 | 2 | 0 | 1 | Toll booth & switching costs | Y | 0 | 1 | 0 | 0 | 1 | 25 | Yes |
| **US** | `NUE` | NUE | Nucor | Materials | 0 | 0 | 0 | 0 | None | N | — | — | — | — | — | — | No |
| **EU** | `RMS.FR` | RMS | Hermès | Consumer Discretionary | 1 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 0 | 0 | 0 | 25 | Yes |
| **EU** | `ASML.NL`| ASML | ASML | Information Technology | 2 | 2 | 0 | 2 | R&D & innovation leadership | Y | 0 | 0 | 1 | 1 | 0 | 25 | Yes |
| **CA** | `CNR.CA` | CNR | Canadian National Railway | Industrials | 1 | 2 | 0 | 0 | Irreplaceable infrastructure & intangibles | Y | 0 | 0 | 0 | 1 | 0 | 20 | Yes |

*Note on NUE*: Because all 4 moat archetype scores are 0, NUE receives `3a = 'None'` and fails Gate 3b (`3b = 'N'`). Under the Munger reject waterfall, failure at Gate 3b scrubs all downstream fields (`4_ent..4_sub`, `4`, `4n`, `5`, `6`).

#### 2. Unscored Legacy Cohort (978 Companies)
- **US**: 437 unscored companies ($445 - 8 = 437$)
- **EU**: 493 unscored companies ($495 - 2 = 493$)
- **CA**: 48 unscored companies ($49 - 1 = 48$)
- **Total Unscored**: $437 + 493 + 48 = \mathbf{978}$ companies.
- For all 978 companies, fields `3_tb`, `3_ia`, `3_se`, `3_rd`, `4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`, and `4n` are **completely blank** (`""`).
- They retain legacy qualitative ratings (`3a`, `3b`, `3m`, and legacy `4` where `3b == 'Y'`).

---

### 1.4 Dual-Listed Mirror Tickers

Inspection of `data/*/universe.json` reveals:
1. `data/us/universe.json` contains:
   ```json
   "mirror": {
     "ASML": "eu:ASML.NL",
     "FER": "eu:FER.ES"
   }
   ```
2. `data/eu/universe.json` and `data/ca/universe.json` do not declare a `mirror` block.
3. In `data/ca/universe.json`, Canadian dual-listed companies Shopify (`SHOP`) and Thomson Reuters (`TRI`) were intentionally omitted from the Canadian workbook because they are tracked in the US workbook (`data/us/inputs.csv`).
4. Cross-universe fuzzy matching and ticker analysis confirmed that **no other dual-listed mirrors exist** in the repository.

#### Mirror Ticker Synchronization State:
- **`ASML` $\leftrightarrow$ `ASML.NL`**:
  - `3_tb=2, 3_ia=2, 3_se=0, 3_rd=2, 3a="R&D & innovation leadership", 3b="Y"`
  - `4_ent=0, 4_riv=0, 4_buy=1, 4_sup=1, 4_sub=0, 4=25`
  - `4n` text note is identical.
  - Scores and gate statuses match 100%.
- **`FER` $\leftrightarrow$ `FER.ES`**:
  - Both currently have legacy scores: `3a = "Irreplaceable infrastructure & intangibles"`, `3b = "N"`, identical `3m` note, and blank downstream fields.
  - Both need Phase 2 evaluation and must be kept in exact synchronization.

#### Mapping & Synchronization Mechanism:
- In `fetch_market_data.py` (lines 365–416), `apply_mirrors()` iterates through `data/us/universe.json["mirror"]`, maps `target_ticker <- source_universe:source_id`, and synchronizes all qualitative gate scores (`[*QUAL_CODES, "calamity", "calamity_note"]`).
- In `screener/apply_evaluation.py`, evaluations are applied per target universe; therefore, whenever an evaluation payload is generated for `ASML.NL` or `FER.ES`, an identical payload must be applied to `ASML` or `FER` (or synchronized immediately after).

---

### 1.5 Industry & Sector Distribution Across 989 Gate 3 Companies

The 989 Gate 3 companies are distributed across **11 GICS sectors**:

| GICS Sector | Total Gate 3 | % of Gate 3 | US Count | EU Count | CA Count | Key Industry Clusters |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Industrials** | **214** | 21.6% | 80 | 128 | 6 | Industrial Machinery (39), Aerospace & Defense (30), Construction & Engineering (20), Electrical Equipment (14), Trading Companies (14) |
| **Financials** | **188** | 19.0% | 69 | 105 | 14 | Diversified Banks (42), Asset Management (28), Life & Health Insurance (17), P&C Insurance (15), Multi-line Insurance (14), Payment Processing (14) |
| **Information Technology** | **109** | 11.0% | 77 | 30 | 2 | Application Software (21), Semiconductors (20), Semiconductor Materials/Equipment (15), Tech Hardware (9), Systems Software (6) |
| **Health Care** | **100** | 10.1% | 59 | 41 | 0 | Health Care Equipment (26), Pharmaceuticals (22), Life Sciences Tools (16), Biotechnology (11), Health Care Services (9) |
| **Consumer Staples** | **71** | 7.2% | 31 | 35 | 5 | Packaged Foods & Meats (19), Food Retail (13), Personal Care (9), Household Products (7), Soft Drinks/Beverages (5), Brewers (5) |
| **Materials** | **65** | 6.6% | 23 | 38 | 4 | Specialty Chemicals (20), Paper/Plastic Packaging (8), Steel (7), Construction Materials (6), Fertilizers (5), Mining & Copper (7) |
| **Utilities** | **64** | 6.5% | 31 | 30 | 3 | Electric Utilities (29), Multi-Utilities (18), Gas Utilities (5), Independent Power/Energy Traders (5), Water Utilities (4), Renewables (3) |
| **Consumer Discretionary**| **50** | 5.1% | 22 | 25 | 3 | Automobile Manufacturers (8), Restaurants (8), Apparel & Luxury Goods (6), Automotive Parts & Retail (8), Broadline/Home Retail (9) |
| **Real Estate** | **50** | 5.1% | 26 | 24 | 0 | Real Estate Operating Companies (9), Industrial REITs (6), Health Care REITs (5), Residential REITs (6), Retail REITs (5), Office REITs (4) |
| **Energy** | **41** | 4.1% | 14 | 18 | 9 | Integrated Oil & Gas (13), Oil & Gas Equipment/Services (9), Midstream Storage/Transport (8), Oil & Gas E&P (6), Refining (4) |
| **Communication Services** | **37** | 3.7% | 13 | 21 | 3 | Integrated Telecom (15), Interactive Media (5), Wireless Telecom (5), Advertising (4), Cable/Satellite (2), Movies/Entertainment (2) |
| **Total** | **989** | **100.0%** | **445** | **495** | **49** | |

---

## 2. Logic Chain

1. **Gate 3 Definition & Scope Verification**:
   - *Premise*: Under the sequential Munger reject framework, evaluation terminates at the first failed gate. Rejection at Gate 1 or Gate 2 removes the company from further qualitative gate evaluations.
   - *Observation*: In `inputs.csv`, exactly 30 companies fail Gate 1 (`1 == 'N'`) and 156 companies pass Gate 1 but fail Gate 2 (`1 == 'Y', 2 == 'N'`).
   - *Deduction*: Out of 1,175 universe constituents, exactly $1,175 - 30 - 156 = 989$ companies have `1 == 'Y'` and `2 == 'Y'`. Therefore, the Gate 3 cohort size of **989** is mathematically exact and verified.

2. **Scoring State Partition**:
   - *Observation*: Examining `3_tb` across all 989 rows reveals 11 non-blank entries and 978 blank entries.
   - *Observation*: All 11 non-blank rows correspond verbatim to the 11 reference companies named in `ORIGINAL_REQUEST.md`.
   - *Deduction*: The total re-scoring workload for Phase 2 comprises **978 unscored companies** (plus verification of the 11 reference companies and synchronization of dual-listed mirrors).

3. **Mirror Pair Integrity**:
   - *Observation*: `data/us/universe.json` defines mirrors `ASML -> eu:ASML.NL` and `FER -> eu:FER.ES`. Both companies in each pair are Gate 3 candidates.
   - *Observation*: `ASML` / `ASML.NL` are already scored and identical. `FER` / `FER.ES` are currently legacy rows with `3b = 'N'`.
   - *Deduction*: During Phase 2 bulk re-scoring, evaluating `FER.ES` or `FER` must update both rows simultaneously to maintain mirror invariant `R2`.

4. **Logical Evaluation Batching**:
   - *Observation*: Porter forces (new entrants, rivalry, buyer power, supplier power, substitution) and moat dynamics (switching costs, concessions, R&D intensity) are intrinsic to industry structure rather than country geography.
   - *Observation*: European, US, and Canadian companies in the same sub-industry (e.g. `ASML` / `AMAT` / `LRCX` in semiconductor equipment; `BA` / `AIR` in commercial aircraft; `RMS.FR` / `CFR` / `MC` in luxury) share identical supplier chains, customer bases, and technological substitutes.
   - *Deduction*: Batching companies by **GICS Sector and Sub-Industry across universes** (rather than siloing by geography) provides the highest qualitative consistency and eliminates contradictory force evaluations among direct competitors.

---

## 3. Caveats

1. **`apply_evaluation.py` Single-Universe Application**:
   `screener/apply_evaluation.py` operates on a single company row in a single universe at a time. It does not automatically propagate changes from `eu:ASML.NL` to `us:ASML` or from `eu:FER.ES` to `us:FER`. Dual-listed mirrors must be updated by issuing evaluations for both IDs or running `fetch_market_data.py --mirror` logic.
2. **Sub-Industry `(mapped)` Labeling**:
   All 602 EU rows and 15 US Nasdaq-100 rows have `(mapped)` appended to their `sub_industry` field. Evaluation batching scripts and prompts should normalize this string when grouping.
3. **Calamity Flags (13 Companies)**:
   There are 13 companies with `calamity == 'Y'` in the dataset (10 US, 3 EU). Under the framework, Calamity waivers are valid only for Gates 3b, 5, or 6. If re-scoring causes Gate 3a to be 'None' or Gate 4 CAP to drop below 15, the waterfall automatically clears the calamity flag.
4. **Baseline Count Assertions in `tests/test_calamity_tier.py`**:
   The test asserts `{"us": 109, "eu": 103, "ca": 11}` for un-waived Quality Pass companies. As Phase 2 re-scoring progresses, some companies will transition into or out of the quality pass funnel, necessitating an update to these test baseline numbers as explicitly anticipated in `R3`.

---

## 4. Conclusion

1. **Universe Data Integrity**: The data foundation is verified, valid, and clean. All 1,175 rows strictly follow the schema.
2. **Cohort Size**: The exact count of Gate 3 candidates is **989** (US: 445, EU: 495, CA: 49).
3. **Workload Scope**: Exactly **11 reference franchises** are complete; **978 companies** require full Step 1 (Moat Profile) and Step 2 (Competitive Forces) scoring.
4. **Dual Mirrors**: Exactly 2 pairs (`ASML` $\leftrightarrow$ `ASML.NL` and `FER` $\leftrightarrow$ `FER.ES`).
5. **Recommended Batching Architecture**:
   To maximize qualitative evaluation quality and throughput, we recommend organizing the 978 unscored companies into **sector-based cohorts** of 15–25 companies:
   - **Batch Group 1 (Tech & Telecom)**: Information Technology (109) + Communication Services (37) = 146 companies (~7 batches)
   - **Batch Group 2 (Health Care)**: Equipment, Pharma, Biotech, Tools (100 companies, ~5 batches)
   - **Batch Group 3 (Consumer)**: Consumer Staples (71) + Consumer Discretionary (50) = 121 companies (~6 batches)
   - **Batch Group 4 (Infrastructure & Cyclicals)**: Utilities (64) + Real Estate (50) + Energy (41) + Materials (65) = 220 companies (~10 batches)
   - **Batch Group 5 (Industrials)**: Machinery, Aerospace, Transport, Construction (214 companies, ~10 batches)
   - **Batch Group 6 (Financials)**: Banks, Asset Managers, Insurance, Exchanges (188 companies, ~9 batches)

---

## 5. Verification Method

To independently verify the observations and conclusions in this report, execute the following commands in the workspace root:

### 1. Verify Gate 3 Counts (US=445, EU=495, CA=49, Total=989)
```bash
python3 -c "
import csv
from pathlib import Path
total = 0
for u in ['us', 'eu', 'ca']:
    with (Path('data') / u / 'inputs.csv').open() as f:
        rows = [r for r in csv.DictReader(f) if r.get('1') == 'Y' and r.get('2') == 'Y']
        print(f'{u.upper()}: {len(rows)}')
        total += len(rows)
print(f'TOTAL: {total}')
assert total == 989
"
```

### 2. Verify Scored Reference Companies (Count = 11) vs Unscored (Count = 978)
```bash
python3 -c "
import csv
from pathlib import Path
ref = {'SPGI', 'COST', 'ASML.NL', 'ASML', 'MSFT', 'WM', 'RMS.FR', 'CNR.CA', 'HSY', 'CRM', 'NUE'}
scored, unscored = 0, 0
for u in ['us', 'eu', 'ca']:
    with (Path('data') / u / 'inputs.csv').open() as f:
        for r in csv.DictReader(f):
            if r.get('1') == 'Y' and r.get('2') == 'Y':
                if r['id'] in ref:
                    assert all(r.get(k) != '' for k in ['3_tb', '3_ia', '3_se', '3_rd'])
                    scored += 1
                else:
                    assert all(r.get(k) == '' for k in ['3_tb', '3_ia', '3_se', '3_rd', '4_ent', '4_riv', '4_buy', '4_sup', '4_sub', '4n'])
                    unscored += 1
print(f'Scored reference: {scored}, Unscored legacy: {unscored}')
assert scored == 11 and unscored == 978
"
```

### 3. Verify Mirror Ticker Configuration
```bash
python3 -c "
import json
with open('data/us/universe.json') as f:
    u = json.load(f)
assert u.get('mirror') == {'ASML': 'eu:ASML.NL', 'FER': 'eu:FER.ES'}
print('Mirrors verified:', u['mirror'])
"
```

### 4. Run Test Suite and Build Cockpit
```bash
python3 -m unittest discover tests
python3 build.py
```
*(Expected: 169 unit tests passing cleanly; build finishes in ~3s generating `output/screener.html` and `docs/index.html` with 1,175 total companies, 223 Prime Grade, 11 Prime Grade Calamity).*
