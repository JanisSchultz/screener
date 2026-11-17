# Data & 121 Incomplete Moat Franchises Survey (v7.18)

**Core Summary**: Across `data/us/`, `data/eu/`, and `data/ca/` (1,175 companies total), exactly **989** reach Gate 3, **504** fail Gate 3, and **485** advance past Gate 3 (483 `3b = "Y"` + `EL` and `APD` on Calamity pass). Of those 485 moat franchises, **364** are already complete across Gates 4–6 (`225` Prime Grade + `13` Calamity pass + `126` Gate-6 rejects), and **121** are incomplete (**108** Gate-4 rejects at `CAP = 5Y/10Y` across 57 US, 51 EU, 0 CA + **13** non-calamity Gate-5 rejects at `5 = 0` across 9 US, 4 EU, 0 CA). Crucially, only **2** of the 121 rows contain the exact string `"Downstream gates bypassed per waterfall."`, while **4** additional rows contain variants (`"Downstream Gates 5-6 bypassed per waterfall."`, `"Downstream gates bypassed per strict waterfall."`, `"Downstream Gate 6 bypassed per waterfall."`) and **115** have no waterfall-bypass sentence at all.

---

## 1. Universe & Funnel Verification (`data/us/`, `data/eu/`, `data/ca/`)

Verified by executing `screener/gates.py` (`phase_results`, `g6_checks`, `cap_audit`) and `screener/bulk_scorer.py --audit` against all rows in `inputs.csv`, `financials.csv`, `prescreen.csv`, and `markets.csv`:

| Funnel Stage / Metric | US | EU | CA | Total | Matches Spec Target? |
|---|---:|---:|---:|---:|---|
| **Total Universe (`inputs.csv` rows)** | 515 | 602 | 58 | **1,175** | Yes (exact) |
| **Gate 1 Fail (`1 == "N"`)** | 14 | 14 | 2 | **30** | Yes |
| **Gate 2 Fail (`1 == "Y", 2 == "N"`)** | 56 | 93 | 7 | **156** | Yes |
| **Gate 3 Reaching (`1 == "Y", 2 == "Y"`)** | 445 | 495 | 49 | **989** | Yes (`TARGET_GATE_3_COUNTS`) |
| **Gate 3 Rejects** | 198 | 278 | 28 | **504** | Yes (`4_*`, `4`, `4n`, `5`, `6` blank) |
| **Gate 3 Advancing (`3a != "None"` and (`3b == "Y"` or `calamity == "Y"`))** | 247 | 217 | 21 | **485** | Yes (`483` `3b="Y"` + `US:EL` + `US:APD`) |
| **Gate 4 Pass (`CAP >= 15`)** | 190 | 166 | 21 | **377** | Yes |
| **Gate 4 Rejects (`CAP = 5Y / 10Y`) — Incomplete Group A** | **57** | **51** | **0** | **108** | Yes (`5Y`: 20 US + 29 EU = 49; `10Y`: 37 US + 22 EU = 59) |
| **Gate 5 Rejects (`5 = 0`, non-calamity) — Incomplete Group B** | **9** | **4** | **0** | **13** | Yes (5 additional `5=0` rows are Calamity pass w/ `6` filled) |
| **Total Incomplete Moat Franchises (`5` or `6` blank)** | **66** | **55** | **0** | **121** | Yes (`108 + 13 = 121`) |
| **Completed Moat Franchises (`5` and `6` non-blank)** | 181 | 162 | 21 | **364** | Yes (`485 - 121 = 364`) |
| **Gate 6 Rejects (non-calamity)** | 61 | 55 | 10 | **126** | Yes |
| **Quality Pass (`result == "Quality pass"`)** | 110 | 104 | 11 | **225** | Yes (all 225 have `g6_flags < 3`) |
| **Prime Grade (`Quality pass` & `g6_flags < 3`)** | 110 | 104 | 11 | **225** | Yes |
| **Calamity Pass (`result == "Calamity pass"`)** | 10 | 3 | 0 | **13** | Yes (`10` US + `3` EU) |
| **Prime Grade Calamity (`Calamity pass` & `g6_flags < 3`)** | 8 | 3 | 0 | **11** | Yes (`US:EL` and `US:RTX` have `g6_flags = 3`) |
| **`To review` rows** | 0 | 0 | 0 | **0** | Yes |

### Calamity Pass Breakdown (13 Total / 11 `< 3` G6 Flags)
- **US (10)**: `GOOGL` (0 flags, `3b=Y,4=20,5=1,6=N`), `EL` (**3 flags**, `3b=N,4=15,5=0,6=N`), `NDAQ` (1 flag, `3b=Y,4=25,5=1,6=N`), `HONA` (1 flag, `3b=Y,4=20,5=1,6=N`), `NOC` (1 flag, `3b=Y,4=20,5=1,6=N`), `RTX` (**3 flags**, `3b=Y,4=20,5=1,6=N`), `EFX` (2 flags, `3b=Y,4=20,5=1,6=N`), `SNPS` (1 flag, `3b=Y,4=25,5=1,6=N`), `TXN` (0 flags, `3b=Y,4=20,5=2,6=N`), `APD` (2 flags, `3b=N,4=25,5=0,6=N`).
- **EU (3)**: `DGE.GB` (1 flag, `3b=Y,4=15,5=0,6=Y`), `NESN.CH` (2 flags, `3b=Y,4=15,5=0,6=N`), `RTO.GB` (2 flags, `3b=Y,4=15,5=0,6=N`).
- **Note**: All 5 Calamity rows with `5 = 0` (`US:EL`, `US:APD`, `EU:DGE.GB`, `EU:NESN.CH`, `EU:RTO.GB`) already have Gate 6 scored (`N`/`Y`/`N`/`N`), so none are in the 121 incomplete set. Zero rows in the 121 have `calamity = "Y"`.

---

## 2. All 121 Incomplete Moat Franchises Grouped Strictly by GICS Sector & Sub-Industry (US + EU Combined)

Sub-industries are matched across US and EU combined by normalizing away the `" (mapped)"` suffix used on EU (and 15 NDX-only US) rows (`sub_industry.replace(" (mapped)", "").strip()`). All 121 rows have `calamity = ""` (blank), `6 = ""` (blank), and `5` either blank (108 Gate-4 rejects) or `0` (13 Gate-5 rejects).

### Sector Summary Table (US + EU Combined)

| GICS Sector | Incomplete Total | Incomplete (US / EU) | Gate-4 Rejects (`5Y`/`10Y`) | Gate-5 Rejects (`5=0`) | Completed Peers in Sector (US / EU / CA) | `g6_default = N` Count |
|---|---:|---|---:|---:|---|---:|
| Communication Services | 2 | 2 US / 0 EU | 2 (1 / 1) | 0 | 5 (1 / 4 / 0) | 0 |
| Consumer Discretionary | 8 | 6 US / 2 EU | 8 (2 / 6) | 0 | 19 (10 / 7 / 2) | 0 |
| Consumer Staples | 4 | 2 US / 2 EU | 3 (1 / 2) | 1 (`ABI.BE`) | 29 (15 / 13 / 1) | 0 |
| Energy | 1 | 1 US / 0 EU | 1 (0 / 1) | 0 | 2 (0 / 2 / 0) | 0 |
| Financials | 38 | 10 US / 28 EU | 38 (20 / 18) | 0 | 78 (34 / 34 / 10) | 24 |
| Health Care | 8 | 5 US / 3 EU | 6 (3 / 3) | 2 (`DIM.FR`, `SRT3.DE`) | 34 (24 / 10 / 0) | 0 |
| Industrials | 24 | 12 US / 12 EU | 22 (8 / 14) | 2 (`BA`, `ADP.FR`) | 100 (43 / 54 / 3) | 0 |
| Information Technology | 18 | 16 US / 2 EU | 15 (6 / 9) | 3 (`INTU`, `PANW`, `ROP`) | 34 (22 / 11 / 1) | 0 |
| Materials | 5 | 2 US / 3 EU | 5 (3 / 2) | 0 | 14 (7 / 6 / 1) | 0 |
| Real Estate | 6 | 5 US / 1 EU | 4 (3 / 1) | 2 (`CSGP`, `CCI`) | 5 (2 / 3 / 0) | 0 |
| Utilities | 7 | 5 US / 2 EU | 4 (2 / 2) | 3 (`ES`, `SO`, `D`) | 44 (23 / 18 / 3) | 7 |
| **Total** | **121** | **66 US / 55 EU** | **108 (49 / 59)** | **13** | **364 (181 / 162 / 21)** | **31** |

---

### Complete Roster of All 121 Companies & Completed Same-Sub-Industry Peers

#### 1. Communication Services (2 Incomplete | 5 Completed Sector Peers)
- **Advertising** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:APP` — AppLovin (`4=5`, `5=blank`, `6=blank`, `g6_default=-`)
- **Movies & Entertainment** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:NFLX` — Netflix (`4=10`, `5=blank`, `6=blank`, `g6_default=-`)

#### 2. Consumer Discretionary (8 Incomplete | 19 Completed Sector Peers)
- **Apparel, Accessories & Luxury Goods** — *Incomplete: 3 | Completed Sub-Industry Peers: 3* (`EU:CFR.CH[1,Y]`, `EU:MC.FR[1,Y]`, `EU:RMS.FR[2,Y]`)
  - `EU:ADS.DE` — adidas (`4=5`, `5=blank`, `6=blank`)
  - `EU:MONC.IT` — Moncler (`4=10`, `5=blank`, `6=blank`)
  - `US:NKE` — Nike, Inc. (`4=10`, `5=blank`, `6=blank`)
- **Broadline Retail** — *Incomplete: 1 | Completed Sub-Industry Peers: 2* (`CA:DOL.CA[2,Y]`, `US:AMZN[1,N]`)
  - `US:EBAY` — eBay Inc. (`4=10`, `5=blank`, `6=blank`)
- **Consumer Electronics** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:GRMN` — Garmin (`4=10`, `5=blank`, `6=blank`)
- **Footwear** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:DECK` — Deckers Brands (`4=5`, `5=blank`, `6=blank`)
- **Restaurants** — *Incomplete: 2 | Completed Sub-Industry Peers: 5* (`CA:QSR.CA[1,N]`, `EU:CPG.GB[2,Y]`, `US:DPZ[1,N]`, `US:MCD[1,Y]`, `US:YUM[1,N]`)
  - `US:CMG` — Chipotle Mexican Grill (`4=10`, `5=blank`, `6=blank`)
  - `US:SBUX` — Starbucks (`4=10`, `5=blank`, `6=blank`)

#### 3. Consumer Staples (4 Incomplete | 29 Completed Sector Peers)
- **Brewers** — *Incomplete: 2 | Completed Sub-Industry Peers: 3* (`EU:CARL B.DK[1,Y]`, `EU:HEIA.NL[1,Y]`, `EU:HEIO.NL[1,Y]`)
  - `EU:ABI.BE` — AB InBev (`4=15`, **`5=0`**, `6=blank`) — *Gate-5 reject*
  - `EU:RBREW.DK` — Royal Unibrew (`4=5`, `5=blank`, `6=blank`)
- **Household Products** — *Incomplete: 1 | Completed Sub-Industry Peers: 2* (`US:CHD[1,Y]`, `US:CL[1,Y]`)
  - `US:CLX` — Clorox (`4=10`, `5=blank`, `6=blank`)
- **Soft Drinks & Non-alcoholic Beverages** — *Incomplete: 1 | Completed Sub-Industry Peers: 4* (`US:CCEP[1,N]`, `US:KO[1,Y]`, `US:MNST[2,Y]`, `US:PEP[1,Y]`)
  - `US:KDP` — Keurig Dr Pepper (`4=10`, `5=blank`, `6=blank`)

#### 4. Energy (1 Incomplete | 2 Completed Sector Peers)
- **Oil & Gas Exploration & Production** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:TPL` — Texas Pacific Land Corporation (`4=10`, `5=blank`, `6=blank`)

#### 5. Financials (38 Incomplete | 78 Completed Sector Peers)
- **Diversified Banks** — *Incomplete: 14 | Completed Sub-Industry Peers: 18* (`CA:BMO.CA[1,N]`, `CA:BNS.CA[1,N]`, `CA:CM.CA[1,N]`, `CA:NA.CA[2,N]`, `CA:RY.CA[2,N]`, `CA:TD.CA[1,N]`, `EU:CABK.ES[1,N]`, `EU:DNB.NO[1,N]`, `EU:ISP.IT[2,N]`, `EU:KBC.BE[2,N]`, `EU:NDA FI.FI[2,N]`, `EU:SHB A.SE[2,N]`, `EU:UBSG.CH[1,N]`, `US:BAC[1,N]`, `US:JPM[2,N]`, `US:PNC[1,N]`, `US:USB[1,N]`, `US:WFC[1,N]`) — *All `g6_default=N`*
  - `EU:A5G.IE` — AIB Group (`4=10`), `EU:ABN.NL` — ABN AMRO (`4=5`), `EU:BCP.PT` — Millennium bcp (`4=5`), `EU:BG.AT` — BAWAG (`4=5`), `EU:BIRG.IE` — Bank of Ireland (`4=10`), `EU:BKT.ES` — Bankinter (`4=10`), `EU:DANSKE.DK` — Danske Bank (`4=5`), `EU:EBS.AT` — Erste Group (`4=10`), `EU:INGA.NL` — ING Groep (`4=10`), `EU:LLOY.GB` — Lloyds Banking Group (`4=10`), `EU:NWG.GB` — NatWest (`4=5`), `EU:SEB A.SE` — SEB (`4=10`), `EU:SWED A.SE` — Swedbank (`4=10`), `EU:UCG.IT` — UniCredit (`4=10`)
- **Regional Banks** — *Incomplete: 10 | Completed Sub-Industry Peers: 0* (benchmark against the 18 Diversified Banks peers) — *All `g6_default=N`*
  - `EU:ALSYDB.DK` — AL Sydbank (`4=5`), `EU:BCVN.CH` — Banque Cantonale Vaudoise (`4=5`), `EU:JYSK.DK` — Jyske Bank (`4=5`), `EU:RILBA.DK` — Ringkjøbing Landbobank (`4=10`), `EU:SB1NO.NO` — SpareBank 1 Sør-Norge (`4=5`), `EU:SBNOR.NO` — Sparebanken Norge (`4=5`), `EU:UNI.ES` — Unicaja Banco (`4=5`), `EU:VATN.CH` — Valiant (`4=5`), `US:MTB` — M&T Bank (`4=5`), `US:RF` — Regions Financial Corporation (`4=5`)
- **Financial Exchanges & Data** — *Incomplete: 1 | Completed Sub-Industry Peers: 11* (`CA:X.CA[1,Y]`, `EU:DB1.DE[1,Y]`, `EU:ENX.FR[2,Y]`, `EU:LSEG.GB[1,N]`, `US:CBOE[1,Y]`, `US:CME[1,Y]`, `US:ICE[1,Y]`, `US:MCO[2,Y]`, `US:MSCI[1,N]`, `US:NDAQ[1,N]`, `US:SPGI[1,Y]`)
  - `US:FDS` — FactSet (`4=10`, `5=blank`, `6=blank`)
- **Insurance Brokers** — *Incomplete: 1 | Completed Sub-Industry Peers: 5* (`US:AJG[1,N]`, `US:AON[1,Y]`, `US:BRO[1,Y]`, `US:ERIE[1,Y]`, `US:MRSH[1,Y]`)
  - `US:WTW` — Willis Towers Watson (`4=5`, `5=blank`, `6=blank`)
- **Investment Banking & Brokerage** — *Incomplete: 1 | Completed Sub-Industry Peers: 7* (`EU:AZA.SE[2,Y]`, `EU:FBK.IT[2,Y]`, `EU:SAVE.SE[1,Y]`, `US:IBKR[2,Y]`, `US:MS[1,N]`, `US:RJF[1,N]`, `US:SCHW[1,Y]`)
  - `EU:TCAP.GB` — TP ICAP (`4=5`, `5=blank`, `6=blank`)
- **Life & Health Insurance** — *Incomplete: 3 | Completed Sub-Industry Peers: 0*
  - `EU:SLHN.CH` — Swiss Life (`4=10`, `5=blank`, `6=blank`)
  - `EU:STB.NO` — Storebrand (`4=5`, `5=blank`, `6=blank`)
  - `US:GL` — Globe Life (`4=5`, `5=blank`, `6=blank`)
- **Multi-line Insurance** — *Incomplete: 4 | Completed Sub-Industry Peers: 2* (`EU:ALV.DE[2,N]`, `EU:ZURN.CH[1,Y]`)
  - `EU:HBAN.CH` — Helvetia Baloise (`4=10`, `5=blank`, `6=blank`)
  - `EU:TLX.DE` — Talanx (`4=10`, `5=blank`, `6=blank`)
  - `EU:UNI.IT` — Unipol (`4=10`, `5=blank`, `6=blank`)
  - `US:AIZ` — Assurant (`4=5`, `5=blank`, `6=blank`)
- **Property & Casualty Insurance** — *Incomplete: 3 | Completed Sub-Industry Peers: 9* (`CA:FFH.CA[2,Y]`, `CA:IFC.CA[2,Y]`, `EU:ADM.GB[2,Y]`, `EU:GJF.NO[2,Y]`, `EU:SAMPO.FI[2,Y]`, `EU:TRYG.DK[1,Y]`, `US:CB[1,Y]`, `US:PGR[2,Y]`, `US:WRB[2,Y]`)
  - `US:ACGL` — Arch Capital Group (`4=5`, `5=blank`, `6=blank`)
  - `US:HIG` — Hartford (The) (`4=10`, `5=blank`, `6=blank`)
  - `US:TRV` — Travelers Companies (The) (`4=10`, `5=blank`, `6=blank`)
- **Transaction & Payment Processing Services** — *Incomplete: 1 | Completed Sub-Industry Peers: 5* (`EU:ADYEN.NL[2,Y]`, `EU:WISE.GB[2,Y]`, `US:JKHY[1,Y]`, `US:MA[2,Y]`, `US:V[2,Y]`)
  - `US:CPAY` — Corpay (`4=10`, `5=blank`, `6=blank`)

#### 6. Health Care (8 Incomplete | 34 Completed Sector Peers)
- **Biotechnology** — *Incomplete: 3 | Completed Sub-Industry Peers: 1* (`US:VRTX[2,Y]`)
  - `EU:ARGX.BE` — argenx (`4=5`, `5=blank`, `6=blank`)
  - `US:ALNY` — Alnylam Pharmaceuticals (`4=10`, `5=blank`, `6=blank`)
  - `US:INCY` — Incyte (`4=5`, `5=blank`, `6=blank`)
- **Health Care Equipment** — *Incomplete: 1 | Completed Sub-Industry Peers: 13* (`EU:ALC.CH[1,Y]`, `EU:BIM.FR[2,Y]`, `EU:EL.FR[1,Y]`, `EU:SECT B.SE[2,Y]`, `EU:SHL.DE[1,Y]`, `US:ABT[1,Y]`, `US:BSX[1,Y]`, `US:EW[2,Y]`, `US:IDXX[2,Y]`, `US:ISRG[2,Y]`, `US:RMD[1,Y]`, `US:STE[1,Y]`, `US:SYK[2,Y]`)
  - `US:PODD` — Insulet Corporation (`4=10`, `5=blank`, `6=blank`)
- **Health Care Services** — *Incomplete: 2 | Completed Sub-Industry Peers: 0*
  - `US:DGX` — Quest Diagnostics (`4=5`, `5=blank`, `6=blank`)
  - `US:LH` — Labcorp (`4=5`, `5=blank`, `6=blank`)
- **Life Sciences Tools & Services** — *Incomplete: 2 | Completed Sub-Industry Peers: 7* (`EU:QIA.DE[1,Y]`, `US:A[1,Y]`, `US:DHR[1,Y]`, `US:MTD[2,Y]`, `US:TECH[1,N]`, `US:TMO[1,Y]`, `US:WAT[1,Y]`)
  - `EU:DIM.FR` — Sartorius Stedim Biotech (`4=25`, **`5=0`**, `6=blank`) — *Gate-5 reject*
  - `EU:SRT3.DE` — Sartorius (`4=25`, **`5=0`**, `6=blank`) — *Gate-5 reject (parent of DIM.FR)*

#### 7. Industrials (24 Incomplete | 100 Completed Sector Peers)
- **Aerospace & Defense** — *Incomplete: 1 | Completed Sub-Industry Peers: 23* (`EU:AIR.FR[1,N]`, `EU:AM.FR[2,N]`, `EU:BA..GB[1,N]`, `EU:BAB.GB[1,N]`, `EU:HAG.DE[1,N]`, `EU:HO.FR[1,N]`, `EU:KOG.NO[2,Y]`, `EU:LDO.IT[1,N]`, `EU:MRO.GB[1,N]`, `EU:MTX.DE[2,Y]`, `EU:RHM.DE[1,N]`, `EU:RR..GB[1,Y]`, `EU:SAAB B.SE[1,N]`, `EU:SAF.FR[1,Y]`, `US:GD[2,Y]`, `US:GE[2,Y]`, `US:HONA[1,N]`, `US:HWM[2,Y]`, `US:LHX[1,N]`, `US:LMT[1,N]`, `US:NOC[1,N]`, `US:RTX[1,N]`, `US:TDG[1,N]`)
  - `US:BA` — Boeing (`4=15`, **`5=0`**, `6=blank`) — *Gate-5 reject*
- **Airport Services** — *Incomplete: 1 | Completed Sub-Industry Peers: 2* (`EU:AENA.ES[1,Y]`, `EU:FHZN.CH[1,N]`)
  - `EU:ADP.FR` — Aéroports de Paris (`4=20`, **`5=0`**, `6=blank`) — *Gate-5 reject*
- **Building Products** — *Incomplete: 2 | Completed Sub-Industry Peers: 7* (`EU:ASSA B.SE[2,Y]`, `EU:BEAN.CH[2,Y]`, `EU:GEBN.CH[2,Y]`, `EU:KRX.IE[1,Y]`, `US:ALLE[1,Y]`, `US:JCI[1,N]`, `US:TT[1,Y]`)
  - `US:AOS` — A. O. Smith (`4=10`, `5=blank`, `6=blank`)
  - `US:LII` — Lennox International (`4=10`, `5=blank`, `6=blank`)
- **Cargo Ground Transportation** — *Incomplete: 1 | Completed Sub-Industry Peers: 1* (`US:ODFL[2,Y]`)
  - `US:FDXF` — FedEx Freight (`4=10`, `5=blank`, `6=blank`)
- **Construction & Engineering** — *Incomplete: 2 | Completed Sub-Industry Peers: 1* (`EU:DG.FR[1,Y]`)
  - `EU:FGR.FR` — Eiffage (`4=10`, `5=blank`, `6=blank`)
  - `EU:SCYR.ES` — Sacyr (`4=5`, `5=blank`, `6=blank`)
- **Electrical Components & Equipment** — *Incomplete: 2 | Completed Sub-Industry Peers: 8* (`EU:ABBN.CH[2,Y]`, `EU:LAGR B.SE[2,Y]`, `EU:LR.FR[2,Y]`, `EU:PRY.IT[1,Y]`, `EU:SU.FR[2,Y]`, `US:AME[1,Y]`, `US:EMR[1,N]`, `US:ETN[1,Y]`)
  - `US:ROK` — Rockwell Automation (`4=10`, `5=blank`, `6=blank`)
  - `US:VRT` — Vertiv (`4=5`, `5=blank`, `6=blank`)
- **Heavy Electrical Equipment** — *Incomplete: 1 | Completed Sub-Industry Peers: 1* (`US:GEV[1,N]`)
  - `EU:ENR.DE` — Siemens Energy (`4=5`, `5=blank`, `6=blank`)
- **Industrial Conglomerates** — *Incomplete: 2 | Completed Sub-Industry Peers: 2* (`EU:LIFCO B.SE[2,Y]`, `EU:SIE.DE[1,N]`)
  - `US:HON` — Honeywell Technologies (`4=10`, `5=blank`, `6=blank`)
  - `US:MMM` — 3M (`4=10`, `5=blank`, `6=blank`)
- **Industrial Machinery & Supplies & Components** — *Incomplete: 8 | Completed Sub-Industry Peers: 16* (`EU:ACLN.CH[2,Y]`, `EU:ATCO A.SE[2,Y]`, `EU:KBX.DE[1,Y]`, `EU:KNEBV.FI[2,Y]`, `EU:RAA.DE[2,Y]`, `EU:SAND.SE[1,Y]`, `EU:SCHP.CH[1,Y]`, `EU:SPX.GB[1,Y]`, `EU:WRT1V.FI[1,N]`, `US:GWW[2,Y]`, `US:HUBB[1,Y]`, `US:ITW[2,Y]`, `US:NDSN[1,Y]`, `US:OTIS[1,Y]`, `US:PH[2,Y]`, `US:SNA[2,Y]`)
  - `EU:ALFA.SE` — Alfa Laval (`4=10`), `EU:IMI.GB` — IMI (`4=10`), `EU:IP.IT` — Interpump (`4=10`), `EU:ROR.GB` — Rotork (`4=10`), `EU:SKF B.SE` — SKF (`4=5`), `EU:TREL B.SE` — Trelleborg (`4=10`), `US:FTV` — Fortive (`4=10`), `US:IEX` — IDEX Corporation (`4=10`)
- **Passenger Ground Transportation** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:UBER` — Uber (`4=5`, `5=blank`, `6=blank`)
- **Research & Consulting Services** — *Incomplete: 1 | Completed Sub-Industry Peers: 8* (`EU:BVI.FR[1,Y]`, `EU:EXPN.GB[1,Y]`, `EU:ITRK.GB[1,Y]`, `EU:REL.GB[2,Y]`, `EU:SGSN.CH[1,Y]`, `EU:WKL.NL[2,Y]`, `US:EFX[1,N]`, `US:VRSK[2,Y]`)
  - `US:TRI` — Thomson Reuters (`4=10`, `5=blank`, `6=blank`)
- **Security & Alarm Services** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `EU:VSURE.SE` — Verisure (`4=5`, `5=blank`, `6=blank`)
- **Trading Companies & Distributors** — *Incomplete: 1 | Completed Sub-Industry Peers: 8* (`EU:ADDT B.SE[2,Y]`, `EU:BEIJ B.SE[2,Y]`, `EU:BNZL.GB[1,Y]`, `EU:DPLM.GB[2,Y]`, `EU:HWDN.GB[2,Y]`, `EU:INDT.SE[2,Y]`, `US:FAST[2,Y]`, `US:FERG[1,Y]`)
  - `EU:RS1.GB` — RS Group (`4=5`, `5=blank`, `6=blank`)

#### 8. Information Technology (18 Incomplete | 34 Completed Sector Peers)
- **Application Software** — *Incomplete: 5 | Completed Sub-Industry Peers: 11* (`CA:CSU.CA[2,Y]`, `EU:DSY.FR[1,Y]`, `EU:NEM.DE[1,Y]`, `EU:SAP.DE[1,Y]`, `EU:SGE.GB[1,Y]`, `US:ADSK[1,Y]`, `US:CDNS[2,Y]`, `US:FICO[1,N]`, `US:PTC[1,Y]`, `US:SNPS[1,N]`, `US:TYL[1,Y]`)
  - `US:ADBE` — Adobe Inc. (`4=5`, `5=blank`, `6=blank`)
  - `US:CRM` — Salesforce (`4=5`, `5=blank`, `6=blank`) — *Reference company; stale `CAP = 10` text in `note`*
  - `US:INTU` — Intuit (`4=15`, **`5=0`**, `6=blank`) — *Gate-5 reject*
  - `US:PLTR` — Palantir Technologies (`4=10`, `5=blank`, `6=blank`)
  - `US:TRMB` — Trimble Inc. (`4=10`, `5=blank`, `6=blank`)
- **Electronic Equipment & Instruments** — *Incomplete: 4 | Completed Sub-Industry Peers: 2* (`EU:HEXA B.SE[1,N]`, `EU:HLMA.GB[2,Y]`)
  - `EU:IFCN.CH` — INFICON (`4=10`, `5=blank`, `6=blank`)
  - `US:KEYS` — Keysight Technologies (`4=10`, `5=blank`, `6=blank`)
  - `US:ROP` — Roper Technologies (`4=20`, **`5=0`**, `6=blank`) — *Gate-5 reject*
  - `US:TDY` — Teledyne Technologies (`4=10`, `5=blank`, `6=blank`)
- **IT Consulting & Other Services** — *Incomplete: 2 | Completed Sub-Industry Peers: 0*
  - `US:ACN` — Accenture (`4=5`, `5=blank`, `6=blank`)
  - `US:IT` — Gartner (`4=10`, `5=blank`, `6=blank`)
- **Internet Services & Infrastructure** — *Incomplete: 1 | Completed Sub-Industry Peers: 1* (`US:VRSN[2,Y]`)
  - `US:SHOP` — Shopify (`4=5`, `5=blank`, `6=blank`)
- **Semiconductor Materials & Equipment** — *Incomplete: 1 | Completed Sub-Industry Peers: 9* (`EU:ASM.NL[2,Y]`, `EU:ASML.NL[2,Y]`, `EU:BESI.NL[2,N]`, `EU:MYCR.SE[1,Y]`, `EU:VACN.CH[1,Y]`, `US:AMAT[1,Y]`, `US:ASML[2,Y]`, `US:KLAC[2,Y]`, `US:LRCX[2,Y]`)
  - `US:Q` — Qnity Electronics (`4=10`, `5=blank`, `6=blank`)
- **Semiconductors** — *Incomplete: 3 | Completed Sub-Industry Peers: 5* (`US:ADI[1,Y]`, `US:ARM[1,N]`, `US:AVGO[1,Y]`, `US:NVDA[2,N]`, `US:TXN[2,N]`)
  - `EU:NOD.NO` — Nordic Semiconductor (`4=5`, `5=blank`, `6=blank`)
  - `US:MPWR` — Monolithic Power Systems (`4=5`, `5=blank`, `6=blank`)
  - `US:NXPI` — NXP Semiconductors (`4=10`, `5=blank`, `6=blank`)
- **Systems Software** — *Incomplete: 2 | Completed Sub-Industry Peers: 2* (`US:FTNT[2,Y]`, `US:MSFT[1,Y]`)
  - `US:NOW` — ServiceNow (`4=10`, `5=blank`, `6=blank`)
  - `US:PANW` — Palo Alto Networks (`4=15`, **`5=0`**, `6=blank`) — *Gate-5 reject*

#### 9. Materials (5 Incomplete | 14 Completed Sector Peers)
- **Paper & Plastic Packaging Products & Materials** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:AVY` — Avery Dennison (`4=10`, `5=blank`, `6=blank`)
- **Specialty Chemicals** — *Incomplete: 4 | Completed Sub-Industry Peers: 7* (`EU:FPE3.DE[2,Y]`, `EU:GIVN.CH[1,Y]`, `EU:NSIS B.DK[1,Y]`, `EU:SIKA.CH[2,Y]`, `EU:SY1.DE[1,N]`, `US:ECL[1,Y]`, `US:SHW[2,Y]`)
  - `EU:CRDA.GB` — Croda (`4=5`, `5=blank`, `6=blank`)
  - `EU:DSFIR.NL` — dsm-firmenich (`4=5`, `5=blank`, `6=blank`)
  - `EU:EMSN.CH` — EMS-Chemie (`4=5`, `5=blank`, `6=blank`)
  - `US:IFF` — International Flavors & Fragrances (`4=10`, `5=blank`, `6=blank`)

#### 10. Real Estate (6 Incomplete | 5 Completed Sector Peers)
- **Data Center REITs** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:DLR` — Digital Realty (`4=5`, `5=blank`, `6=blank`)
- **Health Care REITs** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:WELL` — Welltower (`4=10`, `5=blank`, `6=blank`)
- **Other Specialized REITs** — *Incomplete: 2 | Completed Sub-Industry Peers: 0*
  - `EU:UTG.GB` — Unite (`4=5`, `5=blank`, `6=blank`)
  - `US:IRM` — Iron Mountain (`4=5`, `5=blank`, `6=blank`)
- **Real Estate Services** — *Incomplete: 1 | Completed Sub-Industry Peers: 0*
  - `US:CSGP` — CoStar Group (`4=25`, **`5=0`**, `6=blank`) — *Gate-5 reject*
- **Telecom Tower REITs** — *Incomplete: 1 | Completed Sub-Industry Peers: 2* (`US:AMT[1,N]`, `US:SBAC[1,N]`)
  - `US:CCI` — Crown Castle (`4=20`, **`5=0`**, `6=blank`) — *Gate-5 reject*

#### 11. Utilities (7 Incomplete | 44 Completed Sector Peers)
- **Electric Utilities** — *Incomplete: 3 | Completed Sub-Industry Peers: 23* (`CA:EMA.CA[1,N]`, `CA:FTS.CA[2,N]`, `CA:H.CA[2,N]`, `EU:BKW.CH[1,N]`, `EU:ELI.BE[1,N]`, `EU:ENEL.IT[1,N]`, `EU:IBE.ES[2,N]`, `EU:NG..GB[1,N]`, `EU:RED.ES[1,N]`, `EU:SSE.GB[1,N]`, `EU:TRN.IT[1,N]`, `EU:VER.AT[1,N]`, `US:AEP[1,N]`, `US:CEG[1,N]`, `US:DUK[1,N]`, `US:ETR[1,N]`, `US:EVRG[1,N]`, `US:EXC[1,N]`, `US:FE[1,N]`, `US:LNT[1,N]`, `US:PEG[1,N]`, `US:PPL[1,N]`, `US:WEC[2,N]`) — *All `g6_default=N`*
  - `US:EIX` — Edison International (`4=10`, `5=blank`, `6=blank`)
  - `US:ES` — Eversource Energy (`4=15`, **`5=0`**, `6=blank`) — *Gate-5 reject*
  - `US:SO` — Southern Company (`4=20`, **`5=0`**, `6=blank`) — *Gate-5 reject*
- **Gas Utilities** — *Incomplete: 1 | Completed Sub-Industry Peers: 3* (`EU:IG.IT[1,N]`, `EU:SRG.IT[1,N]`, `US:ATO[2,N]`) — *`g6_default=N`*
  - `EU:ENG.ES` — Enagás (`4=5`, `5=blank`, `6=blank`)
- **Multi-Utilities** — *Incomplete: 2 | Completed Sub-Industry Peers: 15* (`EU:A2A.IT[1,N]`, `EU:ENGI.FR[1,N]`, `EU:EOAN.DE[1,N]`, `EU:HER.IT[2,N]`, `EU:VIE.FR[1,N]`, `US:AEE[1,N]`, `US:CMS[1,N]`, `US:CNP[1,N]`, `US:DTE[1,N]`, `US:ED[1,N]`, `US:NEE[1,N]`, `US:NI[1,N]`, `US:PNW[1,N]`, `US:SRE[1,N]`, `US:XEL[1,N]`) — *All `g6_default=N`*
  - `US:D` — Dominion Energy (`4=20`, **`5=0`**, `6=blank`) — *Gate-5 reject*
  - `US:PCG` — PG&E Corporation (`4=10`, `5=blank`, `6=blank`)
- **Water Utilities** — *Incomplete: 1 | Completed Sub-Industry Peers: 3* (`EU:SVT.GB[2,N]`, `EU:UU..GB[1,N]`, `US:AWK[1,N]`) — *`g6_default=N`*
  - `EU:PNN.GB` — Pennon (`4=5`, `5=blank`, `6=blank`)

---

## 3. Recommended R2 Evaluator Batching Plan (US + EU Combined by GICS Sector / Sub-Industry)

To satisfy Anti-Drift Rule #1 (Sub-Industry Peer Benchmarking across US and EU combined) while keeping each evaluator agent's workload balanced (~8–14 companies each, or 24 for Banks where Gate 6 is automatic `N`), **10 sector-aligned batches** cover all 121 companies without ever splitting US vs. EU or splitting any GICS Sub-Industry:

| Batch | GICS Sector / Industry Cluster | Count | US / EU | Sub-Industries Included (with Peer Count) | Notes for Evaluator |
|---|---|---:|---|---|---|
| **B1** | Financials — Diversified Banks | 14 | 0 US / 14 EU | Diversified Banks (14; 18 US+EU+CA peers) | All `g6_default = N` (automatic `6 = N`); score Gate 5 (`0/1/2`) vs 18 bank peers |
| **B2** | Financials — Regional Banks | 10 | 2 US / 8 EU | Regional Banks (10; benchmarked vs 18 Diversified Banks peers) | All `g6_default = N` (automatic `6 = N`); note `ALSYDB.DK` & `SBNOR.NO` have M&A share-count `fin_note` |
| **B3** | Financials — Insurance, Exchanges, Brokers & Payments | 14 | 8 US / 6 EU | Life & Health Ins. (3; 0), Multi-line Ins. (4; 2), P&C Ins. (3; 9), Ins. Brokers (1; 5), Fin. Exchanges (1; 11), IB & Brokerage (1; 7), Payments (1; 5) | Check Solvency II > 200% for insurers; `HBAN.CH` share-count M&A `fin_note`; `WTW` non-cash mark `fin_note` |
| **B4** | Industrials — Machinery, Electrical & Conglomerates | 13 | 6 US / 7 EU | Ind. Machinery (8; 16), Electrical Comp. (2; 8), Heavy Electrical (1; 1), Ind. Conglomerates (2; 2) | Strong US+EU twin coverage (`ATCO A.SE`/`PH`/`ITW`, `SU.FR`/`ETN`/`ROK`); `MMM` non-cash mark `fin_note` |
| **B5** | Industrials — Infra, A&D, Transport & Services | 11 | 6 US / 5 EU | A&D (1 `5=0`; 23), Airport Svcs (1 `5=0`; 2), Building Prod. (2; 7), Cargo Ground (1; 1), Constr. & Eng. (2; 1), Passenger Ground (1; 0), Research & Consult. (1; 8), Security (1; 0), Trading Cos. (1; 8) | Preserve `5=0` on `US:BA` and `EU:ADP.FR`; score Gate 6 only for those two |
| **B6** | Information Technology — Software, IT Consulting & Internet | 10 | 10 US / 0 EU | Application SW (5; 11 incl. `SAP.DE`, `DSY.FR`, `CSU.CA`), Systems SW (2; 2), IT Consulting (2; 0), Internet Svcs (1; 1) | **Fix `CRM` stale `CAP = 10` note**; preserve `5=0` on `US:INTU`, `US:PANW`; strip `CRM` & `NOW` waterfall sentences |
| **B7** | Information Technology — Semiconductors & Electronic Instruments | 8 | 6 US / 2 EU | Electronic Equip. & Instr. (4; 2), Semiconductors (3; 5), Semi Equip. (1; 9) | Preserve `5=0` on `US:ROP`; strip `ROP` waterfall sentence |
| **B8** | Health Care | 8 | 5 US / 3 EU | Biotechnology (3; 1), Health Care Equip. (1; 13), Health Care Svcs (2; 0), Life Sciences Tools (2 `5=0`; 7) | Preserve `5=0` on `EU:DIM.FR` & `EU:SRT3.DE` (parent/sub pair) |
| **B9** | Consumer Discretionary & Communication Services | 10 | 8 US / 2 EU | Apparel/Luxury (3; 3), Broadline Retail (1; 2), Consumer Elec. (1; 0), Footwear (1; 0), Restaurants (2; 5), Advertising (1; 0), Movies & Ent. (1; 0) | Strip waterfall sentences on `US:APP`, `US:NFLX`, `US:SBUX`; `EBAY` non-cash mark `fin_note` |
| **B10** | Consumer Staples, Materials & Energy | 10 | 5 US / 5 EU | Brewers (2; 3), Household Prod. (1; 2), Soft Drinks (1; 4), Specialty Chem. (4; 7), Paper/Plastic Pkg (1; 0), Oil & Gas E&P (1; 0) | Preserve `5=0` on `EU:ABI.BE` |
| **B11** | Real Estate & Utilities | 13 | 10 US / 3 EU | Data Center REIT (1; 0), Health Care REIT (1; 0), Other Spec. REIT (2; 0), Real Estate Svcs (1 `5=0`; 0), Telecom Tower REIT (1 `5=0`; 2), Electric Util. (3; 23), Gas Util. (1; 3), Multi-Util. (2; 15), Water Util. (1; 3) | All 7 Utilities have `g6_default = N` (automatic `6 = N`); preserve `5=0` on `US:CSGP`, `US:CCI`, `US:D`, `US:ES`, `US:SO`; `ES`/`ENG.ES`/`PNN.GB` blocking `fin_note` |

*(B1 + B2 can optionally be combined into a single 24-company Banks batch since Gate 6 is automatic `N` across all 24.)*

---

## 4. `CRM` (Salesforce) Inspection

- **Location**: `data/us/inputs.csv` (id=`CRM`, ticker=`CRM`, sector=`Information Technology`, sub_industry=`Application Software`).
- **Mirror status**: **Not a mirror** (only `ASML`/`ASML.NL` and `FER`/`FER.ES` are mirrors in `data/us/universe.json`).
- **Current qualitative fields**:
  - `1="Y"`, `2="Y"`, `2r=""`
  - `3_tb=2`, `3_ia=0`, `3_se=0`, `3_rd=0`, `3a="Toll booth & switching costs"`, `3b="Y"`
  - `4_ent=1`, `4_riv=1`, `4_buy=1`, `4_sup=0`, `4_sub=2` → deterministic `4=5` (`Initial CAP 20Y`, Fatal-Flaw `4_sub=2` + `3x 1` forces with `h(3)=10Y` → `20 - 10 - 10 = 0 -> 5Y`).
  - `4n`: `"Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): agentic AI substitution threatens per-seat CRM licensing (4_sub=2) alongside enterprise Buyer seat scrutiny (4_buy=1), suite Rivalry (4_riv=1), and AI-native Entrants (4_ent=1)."` (Consistent with `4=5`).
  - `5=""`, `6=""`, `calamity=""`, `calamity_note=""`.
- **Stale `note` text**:
  > `"Fails Gate 4 (CAP = 10, REJECT). Enterprise software baseline (10-15 years) haircut to CAP 10 under Macrotrend #1 (Automation & Cognitive Tech): core monetization relies on seat-based licensing across Sales and Service Clouds, which faces secular deflation as autonomous AI agents compress corporate sales and customer support headcount. Agentforce consumption pricing remains unproven to offset seat cannibalization. Downstream gates bypassed per strict waterfall."`
  - **Two required fixes in R2**: (1) Update `CAP = 10` / `haircut to CAP 10` text to reflect deterministic `CAP = 5` / `5Y`, and (2) strip `"Downstream gates bypassed per strict waterfall."` (note the word `"strict"`!) and append `[Diagnostic G5=<0|1|2> | G6=<Y|N>: <rationale>]`.
  - **R1 note**: `REFERENCE_SNAPSHOT["CRM"]` in `screener/bulk_scorer.py:201-210` currently expects `"5": "", "6": ""` and must be updated after `CRM` is scored.

---

## 5. Dual-Listed Mirror Check

- **`data/us/universe.json:87-90`**: `"mirror": {"ASML": "eu:ASML.NL", "FER": "eu:FER.ES"}`. `data/eu/universe.json` and `data/ca/universe.json` have no `"mirror"` key.
- **Status in the 121 incomplete set**: **None (0)** of the mirror pairs are in the 121:
  - `US:ASML` / `EU:ASML.NL`: Both are complete (`3a="R&D & innovation leadership"`, `3b="Y"`, `4=25`, `5=2`, `6="Y"`, `Quality pass`).
  - `US:FER` / `EU:FER.ES`: Both fail Gate 3 (`3b="N"`, `4=""`, `5=""`, `6=""`, `Rejected – G3 Moat & Pricing`).
- **Related non-mirror pair in the 121**: `EU:SRT3.DE` (Sartorius) and `EU:DIM.FR` (Sartorius Stedim Biotech) are parent/subsidiary separate listed entities (NOT mirrors in `universe.json`), and both are Gate-5 rejects (`4=25`, `5=0`, `6=""`) in `Life Sciences Tools & Services`.

---

## 6. Exact Data Schemas & Coverage (`inputs.csv`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`)

1. **`inputs.csv`**:
   - `us`: 515 rows × 31 cols (`base` 6 + `in_sp500, in_ndx` + `qual` 19 + `tail` 4)
   - `eu`: 602 rows × 31 cols (`base` 6 + `exchange, index_weight_pct` + `qual` 19 + `tail` 4)
   - `ca`: 58 rows × 30 cols (`base` 6 + `exchange` + `qual` 19 + `tail` 4)
   - Common qualitative + tail columns: `1, 2, 2r, 3_tb, 3_ia, 3_se, 3_rd, 3a, 3b, 3m, 4_ent, 4_riv, 4_buy, 4_sup, 4_sub, 4, 4n, 5, 6, calamity, calamity_note, note, evidence`.
   - **Coverage on the 121**: 121/121 have non-empty `note` and `evidence` dossiers.

2. **`financials.csv`** (515 US / 602 EU / 58 CA rows; **45 columns**, identical across all 3 universes):
   `id, fin_currency, as_of, source, price, quote_currency, market_cap_m, sales_ttm_m, ni_ttm_m, capex_ttm_m, da_ttm_m, dividends_ttm_m, lt_debt_m, cash_m, interest_m, ebit_ttm_m, roic_median, roic_operating, fcf_conv, peak_oe_year, peak_oe_eps, cur_oe_eps, cur_oe_year, mult_low_5y, mult_high_5y, cagr_oe_eps, p2p_ok, sales_1y, sales_cagr, sales_cagr_yrs, opcost_1y, opcost_cagr, cap_growth, ma_reinvest, buyback_yield, retention_rate, roiic, roe_median, ic_neg_years, equity_m, ocf_ni_2y, owner_add_m, g6_netdebt_yrs, g6_intcov, fin_note`
   - **Coverage on the 121**: 121/121 have a `financials.csv` row (`lt_debt_m`, `cash_m`, `equity_m`, `g6_netdebt_yrs`, `g6_intcov`, `roic_median`, `roic_operating` are 100% populated).
   - **Blank fields on subset of the 121**:
     - `fcf_conv` blank on 4: `US:ALNY`, `US:BA`, `US:IFF`, `EU:VSURE.SE`
     - `p2p_ok` blank on 6: `US:APP`, `US:FDXF`, `US:Q`, `EU:SBNOR.NO`, `EU:VSURE.SE`, `EU:DSFIR.NL`
     - `roe_median` blank on 1: `US:SBUX` (negative equity)
     - `ma_reinvest` blank on 7: `US:ALNY`, `US:FDXF`, `US:PLTR`, `US:Q`, `US:EIX`, `US:PCG`, `EU:ARGX.BE`
     - `retention_rate` blank on 1: `EU:VSURE.SE`
     - `roiic` blank on 32 (18 US, 14 EU — mostly banks/insurers or negative-ΔIC cases)
   - **`BLOCKING_AUTO_NOTES` in `fin_note` on the 121 (9 rows)**:
     - `earnings dominated by non-cash marks`: `US:EBAY`, `US:WTW`, `US:MMM`, `US:ES`, `EU:ENG.ES`
     - `share count changed since FY`: `EU:HBAN.CH`, `EU:ALSYDB.DK`, `EU:SBNOR.NO`, `EU:PNN.GB`
     *(Evaluators should inspect `fundamentals_panel.csv` and `note`/`evidence` dossiers for these 9.)*

3. **`fundamentals_panel.csv`** (16,566 US / 14,572 EU / 1,724 CA rows; **69 columns**, identical across all 3 universes):
   `id, ticker, eodhd_symbol, fy, period_end, filing_date, fin_currency, revenue_m, cogs_m, gross_profit_m, rd_m, sga_m, opex_m, opcost_m, ebitda_m, da_m, ebit_m, interest_expense_m, interest_income_m, pretax_income_m, tax_m, eff_tax_rate, net_income_m, net_income_common_m, ocf_m, capex_m, fcf_reported_m, owner_fcf_m, sbc_m, dividends_paid_m, share_buybacks_m, net_borrowings_m, working_capital_change_m, cash_m, cash_and_st_inv_m, receivables_m, inventory_m, current_assets_m, ppe_net_m, goodwill_m, intangibles_m, total_assets_m, accounts_payable_m, current_deferred_rev_m, current_liab_m, st_debt_m, lt_debt_m, total_debt_m, net_debt_m, total_liab_m, equity_m, retained_earnings_m, net_working_capital_m, ic_gaap_m, ic_tangible_m, nopat_m, roic_gaap, roic_tangible, roe, rote, gross_margin, ebit_margin, net_margin, fcf_conversion, diluted_shares_m, eps_gaap, eps_street, owner_eps, ye_price_quote`
   - **Coverage on the 121**: 121/121 have multi-year panel rows.

4. **`prescreen.csv`** (137 US / 117 EU / 32 CA rows; **4 columns**: `sector, sub_industry, g6_default, note`):
   - `g6_default = "N"` applies to **31** of the 121 incomplete companies:
     - `Diversified Banks` (14 EU)
     - `Regional Banks` (2 US + 8 EU = 10)
     - `Electric Utilities` (3 US: `EIX`, `ES`, `SO`)
     - `Gas Utilities` (1 EU: `ENG.ES`)
     - `Multi-Utilities` (2 US: `D`, `PCG`)
     - `Water Utilities` (1 EU: `PNN.GB`)
   - Note: `US:D`, `US:ES`, `US:SO` currently pass `phase_results` G6 check only via `prescreen.csv` fallback (`6=""` in `inputs.csv`); under R1/R2 they must receive explicit `6="N"` in `inputs.csv`.

---

## 7. `"Downstream gates bypassed per waterfall."` Occurrences Across All `inputs.csv`

Exact occurrences vs. variants across the **121 incomplete rows**:
- **Only 6 of the 121 rows** contain a waterfall-bypass sentence in `note` (and **0** in `4n`, `3m`, or `evidence`):
  - `US:APP` (`G4=5`): `"Downstream gates bypassed per waterfall."` *(exact)*
  - `US:NOW` (`G4=10`): `"Downstream gates bypassed per waterfall."` *(exact)*
  - `US:NFLX` (`G4=10`): `"Downstream Gates 5-6 bypassed per waterfall."` *(variant)*
  - `US:SBUX` (`G4=10`): `"Downstream Gates 5-6 bypassed per waterfall."` *(variant)*
  - `US:CRM` (`G4=5`): `"Downstream gates bypassed per strict waterfall."` *(variant)*
  - `US:ROP` (`G4=20, G5=0`): `"Downstream Gate 6 bypassed per waterfall."` *(variant)*
- **115 of the 121 rows** have **no** waterfall-bypass sentence in `note` at all.
- **0 of the 364 completed rows** contain any waterfall-bypass sentence.
- **Outside the 121 (in Gate 1/2/3 rejects, which must stay untouched)**: **40** rows contain waterfall-bypass/nullification sentences (e.g., 3 Gate-1 rejects, 11 Gate-2 rejects, 26 Gate-3 rejects — exact `"Downstream gates bypassed per waterfall."` appears on 18 of those Gate-1/2/3 rejects).

**Actionable warning for R2**: Strip any sentence matching `Downstream (?:gates?|Gates? (?:5-6|6)) bypassed per (?:strict )?waterfall\.` (case-insensitive) on the **121** incomplete rows (those 6 rows specifically), **without** touching Gate 1–3 reject notes.
