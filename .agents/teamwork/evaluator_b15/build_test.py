"""Builder script to evaluate Batch 15 companies with 100% precision and compliance.
"""
import json
import sys
from pathlib import Path

from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
from screener.apply_evaluation import validate_and_waterfall

# Load batch 15
with open("evaluations/batches/batch_15.json") as f:
    batch_data = json.load(f)

companies = batch_data["companies"]
print(f"Loaded {len(companies)} companies from batch_15.json")

# Define evaluation mappings for all 68 companies
# Map keyed by company id:
# tuple: (3_tb, 3_ia, 3_se, 3_rd, 3a, 3b, 4_ent, 4_riv, 4_buy, 4_sup, 4_sub, 4n_rationale, 5, 6)
# Note: if 3b == 'N', 4_* to 6 will be cleared per waterfall.
# If 4 < 15, 5 and 6 cleared per waterfall.
# If 5 == 0, 6 cleared per waterfall.

COMPANY_SCORES = {
    # 01. CCI: Crown Castle (Telecom Tower REITs) - Fails Gate 5 (Score = 0)
    "CCI": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for carrier buyer consolidation (4_buy=1), tower colocation rivalry (4_riv=1), and technological substitution from satellite/small-cell alternatives (4_sub=1).",
        "5": 0,
        "6": ""
    },
    # 02. SBAC: SBA Communications (Telecom Tower REITs) - Fails Gate 6 (N)
    "SBAC": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for carrier customer consolidation (4_buy=1), tower colocation rivalry (4_riv=1), and technological substitution from satellite/small-cell alternatives (4_sub=1).",
        "5": 1,
        "6": "N"
    },
    # 03. CLNX.ES: Cellnex (Telecom Tower REITs) - Fails Gate 3b (N)
    "CLNX.ES": {
        "moat": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 04. WY: Weyerhaeuser (Timber REITs) - Fails Gate 3b (N)
    "WY": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 05. AEP: American Electric Power (Electric Utilities) - Fails Gate 6 (N)
    "AEP": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for regulatory rate scrutiny across 11 state public utility commissions and customer bill pushback (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 06. CEG: Constellation Energy (Electric Utilities) - Fails Gate 6 (N)
    "CEG": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for wholesale power market rivalry (4_riv=1), FERC regulatory pushback on data-center colocation tariffs (4_buy=1), and nuclear fuel supply chain bottlenecks (4_sup=1).",
        "5": 1,
        "6": "N"
    },
    # 07. DUK: Duke Energy (Electric Utilities) - Fails Gate 6 (N)
    "DUK": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for state regulatory commission rate scrutiny and rate-case lag across multiple jurisdictions (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 08. EIX: Edison International (Electric Utilities) - Fails Gate 4 (CAP = 10)
    "EIX": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 2),
        "4n": "Initial CAP 25Y capped at 10Y (REJECT) due to fatal-flaw wildfire liability under California inverse condemnation strict liability (4_sub=2) and intense ratepayer affordability pressure (4_buy=1).",
        "5": "",
        "6": ""
    },
    # 09. EMA.CA: Emera (Electric Utilities) - Fails Gate 6 (N)
    "EMA.CA": {
        "moat": (2, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 0, 0, 0),
        "4n": "Initial CAP 30Y preserved. Structural insulation across all 5 forces (all 4_*=0): regulated electric and gas utilities with statutory franchise monopolies, formulaic rate-base returns, and captive customer bases.",
        "5": 1,
        "6": "N"
    },
    # 10. ES: Eversource Energy (Electric Utilities) - Fails Gate 4 (CAP = 10)
    "ES": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 2, 0, 1),
        "4n": "Initial CAP 25Y capped at 10Y (REJECT) due to fatal-flaw regulatory hostility and punitive rate disallowances post-offshore wind impairments (4_buy=2) and clean energy transition execution risks (4_sub=1).",
        "5": "",
        "6": ""
    },
    # 11. ETR: Entergy (Electric Utilities) - Fails Gate 6 (N)
    "ETR": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for state regulatory rate-case review and Gulf Coast hurricane restoration rider scrutiny (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 12. EVRG: Evergy (Electric Utilities) - Fails Gate 6 (N)
    "EVRG": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Kansas and Missouri regulatory commission rate-case scrutiny and allowed ROE friction (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 13. EXC: Exelon (Electric Utilities) - Fails Gate 6 (N)
    "EXC": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for regulatory rate scrutiny and rate-case rejection risks across Illinois ICC and Maryland PSC (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 14. FE: FirstEnergy (Electric Utilities) - Fails Gate 6 (N)
    "FE": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for ongoing regulatory oversight post-House Bill 6 settlement and PUCO rate-case friction (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 15. FTS.CA: Fortis (Electric Utilities) - Fails Gate 6 (N)
    "FTS.CA": {
        "moat": (2, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 0, 0, 0),
        "4n": "Initial CAP 30Y preserved. Structural insulation across all 5 forces (all 4_*=0): 99% regulated electric and gas transmission/distribution utilities across Canada and the US with predictable formulaic rate-base returns.",
        "5": 2,
        "6": "N"
    },
    # 16. H.CA: Hydro One (Electric Utilities) - Fails Gate 6 (N)
    "H.CA": {
        "moat": (2, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 0, 0, 0),
        "4n": "Initial CAP 30Y preserved. Structural insulation across all 5 forces (all 4_*=0): provincial monopoly owning ~98% of Ontario's high-voltage electricity transmission network with zero competitive threat and formulaic OEB multi-year ratemaking.",
        "5": 2,
        "6": "N"
    },
    # 17. LNT: Alliant Energy (Electric Utilities) - Fails Gate 6 (N)
    "LNT": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Iowa Utilities Board and Wisconsin PSC regulatory scrutiny on renewable energy rate-base riders (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 18. PEG: Public Service Enterprise Group (Electric Utilities) - Fails Gate 6 (N)
    "PEG": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for New Jersey Board of Public Utilities rate review scrutiny and nuclear ZEC subsidy oversight (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 19. PPL: PPL Corporation (Electric Utilities) - Fails Gate 6 (N)
    "PPL": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for regulatory rate scrutiny across Pennsylvania, Kentucky, and Rhode Island commissions (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 20. SO: Southern Company (Electric Utilities) - Fails Gate 5 (Score = 0)
    "SO": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for regulatory rate scrutiny across southeastern state utility commissions (4_buy=1).",
        "5": 0,
        "6": ""
    },
    # 21. VST: Vistra Corp. (Electric Utilities) - Fails Gate 3b (N)
    "VST": {
        "moat": (1, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 22. WEC: WEC Energy Group (Electric Utilities) - Fails Gate 6 (N)
    "WEC": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Wisconsin and Illinois utility commission rate-case scrutiny (4_buy=1).",
        "5": 2,
        "6": "N"
    },
    # 23. BKW.CH: BKW (Electric Utilities) - Fails Gate 6 (N)
    "BKW.CH": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Swiss federal ElCom grid tariff regulation and engineering services margin cyclicality (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 24. EDP.PT: EDP (Electric Utilities) - Fails Gate 3b (N)
    "EDP.PT": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 25. ELE.ES: Endesa (Electric Utilities) - Fails Gate 3b (N)
    "ELE.ES": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 26. ELI.BE: Elia (Electric Utilities) - Fails Gate 6 (N)
    "ELI.BE": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Belgian CREG and German BNetzA regulatory tariff reviews and massive offshore grid capex demands (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 27. ENEL.IT: Enel (Electric Utilities) - Fails Gate 6 (N)
    "ENEL.IT": {
        "moat": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for European regulatory tariff reviews, windfall taxes, and Latin American macroeconomic volatility (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 28. IBE.ES: Iberdrola (Electric Utilities) - Fails Gate 6 (N)
    "IBE.ES": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for multi-jurisdictional regulatory tariff reviews across Spain, UK Ofgem, and US utility commissions (4_buy=1).",
        "5": 2,
        "6": "N"
    },
    # 29. NG..GB: National Grid (Electric Utilities) - Fails Gate 6 (N)
    "NG..GB": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for UK Ofgem RIIO-T3 price control negotiations and New York/Massachusetts regulatory scrutiny (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 30. RED.ES: Redeia (Electric Utilities) - Fails Gate 6 (N)
    "RED.ES": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Spanish CNMC regulatory remuneration rate resets and governmental fee caps (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 31. SSE.GB: SSE (Electric Utilities) - Fails Gate 6 (N)
    "SSE.GB": {
        "moat": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for UK Ofgem RIIO-T2/T3 price control resets and wholesale renewable merchant exposure (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 32. TRN.IT: Terna (Electric Utilities) - Fails Gate 6 (N)
    "TRN.IT": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Italian ARERA regulatory remuneration resets and sovereign debt spread exposure (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 33. VER.AT: Verbund (Electric Utilities) - Fails Gate 6 (N)
    "VER.AT": {
        "moat": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for Central European wholesale power rivalry (4_riv=1), Austrian statutory windfall profit clawbacks (4_buy=1), and hydrology drought volatility (4_sup=1).",
        "5": 1,
        "6": "N"
    },
    # 34. ATO: Atmos Energy (Gas Utilities) - Fails Gate 6 (N)
    "ATO": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 1, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for state utility commission rate reviews (4_buy=1), pipeline steel/labor replacement inflation (4_sup=1), and long-term building electrification substitution (4_sub=1).",
        "5": 2,
        "6": "N"
    },
    # 35. ENG.ES: Enagás (Gas Utilities) - Fails Gate 4 (CAP = 10)
    "ENG.ES": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 2),
        "4n": "Initial CAP 25Y capped at 10Y (REJECT) due to fatal-flaw secular substitution threat from European decarbonization and heating electrification (4_sub=2) alongside CNMC tariff cuts (4_buy=1).",
        "5": "",
        "6": ""
    },
    # 36. IG.IT: Italgas (Gas Utilities) - Fails Gate 6 (N)
    "IG.IT": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 0, 0, 1),
        "4n": "Initial CAP 20Y reduced by -5Y for secular European gas decarbonization and building electrification substitution pressure (4_sub=1).",
        "5": 1,
        "6": "N"
    },
    # 37. RUI.FR: Rubis (Gas Utilities) - Fails Gate 3b (N)
    "RUI.FR": {
        "moat": (1, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 38. SRG.IT: Snam (Gas Utilities) - Fails Gate 6 (N)
    "SRG.IT": {
        "moat": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "forces": (0, 0, 0, 0, 1),
        "4n": "Initial CAP 20Y reduced by -5Y for secular European gas decarbonization and transition substitution risks (4_sub=1).",
        "5": 1,
        "6": "N"
    },
    # 39. AES: AES Corporation (Independent Power Producers) - Fails Gate 3b (N)
    "AES": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 40. NRG: NRG Energy (Independent Power Producers) - Fails Gate 3b (N)
    "NRG": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 41. DRX.GB: Drax (Independent Power Producers) - Fails Gate 3b (N)
    "DRX.GB": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 42. FORTUM.FI: Fortum (Independent Power Producers) - Fails Gate 3b (N)
    "FORTUM.FI": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 43. RWE.DE: RWE (Independent Power Producers) - Fails Gate 3b (N)
    "RWE.DE": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 44. AEE: Ameren (Multi-Utilities) - Fails Gate 6 (N)
    "AEE": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Missouri Public Service Commission and Illinois ICC rate-case scrutiny (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 45. CMS: CMS Energy (Multi-Utilities) - Fails Gate 6 (N)
    "CMS": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Michigan Public Service Commission rate-case reviews and storm outage scrutiny (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 46. CNP: CenterPoint Energy (Multi-Utilities) - Fails Gate 6 (N)
    "CNP": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Texas PUC intense storm hardening scrutiny and rate-case friction post-Hurricane Beryl (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 47. D: Dominion Energy (Multi-Utilities) - Fails Gate 5 (Score = 0)
    "D": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Virginia State Corporation Commission regulatory scrutiny over the multi-billion Coastal Virginia Offshore Wind rider (4_buy=1).",
        "5": 0,
        "6": ""
    },
    # 48. DTE: DTE Energy (Multi-Utilities) - Fails Gate 6 (N)
    "DTE": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Michigan Public Service Commission rate-case reviews and grid reliability scrutiny (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 49. ED: Consolidated Edison (Multi-Utilities) - Fails Gate 6 (N)
    "ED": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for New York Public Service Commission regulatory rate-case scrutiny and clean heat mandate costs (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 50. NEE: NextEra Energy (Multi-Utilities) - Fails Gate 6 (N)
    "NEE": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Florida PSC regulatory rate-case scrutiny and renewable transmission interconnection delays (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 51. NI: NiSource (Multi-Utilities) - Fails Gate 6 (N)
    "NI": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Indiana and Ohio regulatory commission rate-case scrutiny (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 52. PCG: PG&E Corporation (Multi-Utilities) - Fails Gate 4 (CAP = 10)
    "PCG": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 2),
        "4n": "Initial CAP 25Y capped at 10Y (REJECT) due to fatal-flaw wildfire liability under California inverse condemnation strict liability (4_sub=2) and intense ratepayer affordability pressure (4_buy=1).",
        "5": "",
        "6": ""
    },
    # 53. PNW: Pinnacle West Capital (Multi-Utilities) - Fails Gate 6 (N)
    "PNW": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for historically contentious Arizona Corporation Commission rate-case proceedings and allowed ROE disallowances (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 54. SRE: Sempra (Multi-Utilities) - Fails Gate 6 (N)
    "SRE": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for California CPUC and Texas regulatory scrutiny on utility transmission and distribution riders (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 55. XEL: Xcel Energy (Multi-Utilities) - Fails Gate 6 (N)
    "XEL": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Minnesota and Colorado regulatory rate-case scrutiny and wildfire mitigation cost recovery oversight (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 56. A2A.IT: A2A (Multi-Utilities) - Fails Gate 6 (N)
    "A2A.IT": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Italian ARERA regulatory tariff resets and municipal concession renewal competition (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 57. ENGI.FR: Engie (Multi-Utilities) - Fails Gate 6 (N)
    "ENGI.FR": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for French CRE regulatory tariff oversight, nuclear phaseout provisions in Belgium, and energy market intervention (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 58. EOAN.DE: E.ON (Multi-Utilities) - Fails Gate 6 (N)
    "EOAN.DE": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for German Federal Network Agency (BNetzA) equity return resets and regulatory lag on massive grid reinforcement capex (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 59. HER.IT: Hera (Multi-Utilities) - Fails Gate 6 (N)
    "HER.IT": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for Italian ARERA regulatory tariff reviews and municipal concession tender risks (4_buy=1).",
        "5": 2,
        "6": "N"
    },
    # 60. NTGY.ES: Naturgy (Multi-Utilities) - Fails Gate 3b (N)
    "NTGY.ES": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 61. VIE.FR: Veolia (Multi-Utilities) - Fails Gate 6 (N)
    "VIE.FR": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for municipal public authority procurement renegotiations and concession retendering friction (4_buy=1).",
        "5": 1,
        "6": "N"
    },
    # 62. ANA.ES: Acciona (Renewable Electricity) - Fails Gate 3b (N)
    "ANA.ES": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 63. EDPR.PT: EDP Renováveis (Renewable Electricity) - Fails Gate 3b (N)
    "EDPR.PT": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 64. ORSTED.DK: Ørsted (Renewable Electricity) - Fails Gate 3b (N)
    "ORSTED.DK": {
        "moat": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "forces": (0, 0, 0, 0, 0),
        "4n": "",
        "5": "",
        "6": ""
    },
    # 65. AWK: American Water Works (Water Utilities) - Fails Gate 6 (N)
    "AWK": {
        "moat": (2, 2, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 0, 0, 0),
        "4n": "Initial CAP 30Y preserved. Structural insulation across all 5 forces (all 4_*=0): regulated water and wastewater utility with statutory territorial monopolies, irreplaceable underground pipe networks, zero substitute for water, and formulaic rate-base returns.",
        "5": 1,
        "6": "N"
    },
    # 66. PNN.GB: Pennon (Water Utilities) - Fails Gate 4 (CAP = 10)
    "PNN.GB": {
        "moat": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 2, 0, 1),
        "4n": "Initial CAP 25Y capped at 10Y (REJECT) due to fatal-flaw Ofwat regulatory enforcement, sewage penalty escalation, and pollution liabilities (4_buy=2) and water network asset degradation (4_sub=1).",
        "5": "",
        "6": ""
    },
    # 67. SVT.GB: Severn Trent (Water Utilities) - Fails Gate 6 (N)
    "SVT.GB": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for UK Ofwat PR24 regulatory determinations and environmental performance penalty scrutiny (4_buy=1).",
        "5": 2,
        "6": "N"
    },
    # 68. UU..GB: United Utilities (Water Utilities) - Fails Gate 6 (N)
    "UU..GB": {
        "moat": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "forces": (0, 0, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for UK Ofwat PR24 regulatory price controls and environmental storm overflow reduction mandates (4_buy=1).",
        "5": 1,
        "6": "N"
    }
}

print(f"Total scored mappings: {len(COMPANY_SCORES)}")
assert len(COMPANY_SCORES) == 68, f"Expected 68 company scores, got {len(COMPANY_SCORES)}"

evaluated_list = []
all_warnings = []

for c in companies:
    cid = c["identity"]["id"]
    uni = c["identity"]["universe"]
    cq = c["current_qualitative"]
    spec = COMPANY_SCORES[cid]

    m_tb, m_ia, m_se, m_rd = spec["moat"]
    f_ent, f_riv, f_buy, f_sup, f_sub = spec["forces"]
    g3a = spec["3a"]
    g3b = spec["3b"]
    g4n = spec["4n"]
    g5 = spec["5"]
    g6 = spec["6"]

    # Compute Initial CAP
    cap_init = compute_initial_cap_from_scores((m_tb, m_ia, m_se, m_rd))

    # Compute Final CAP
    if g3b == "Y":
        cap_final, _, _ = compute_final_cap_from_scores(cap_init, (f_ent, f_riv, f_buy, f_sup, f_sub))
    else:
        cap_final = ""

    # Assemble qualitative dictionary
    qual = {
        "1": "Y",
        "2": "Y",
        "2r": "",
        "3_tb": m_tb,
        "3_ia": m_ia,
        "3_se": m_se,
        "3_rd": m_rd,
        "3a": g3a,
        "3b": g3b,
        "3m": cq.get("3m", ""),
        "4_ent": f_ent if g3b == "Y" else "",
        "4_riv": f_riv if g3b == "Y" else "",
        "4_buy": f_buy if g3b == "Y" else "",
        "4_sup": f_sup if g3b == "Y" else "",
        "4_sub": f_sub if g3b == "Y" else "",
        "4": cap_final if g3b == "Y" else "",
        "4n": g4n if g3b == "Y" else "",
        "5": g5 if (g3b == "Y" and isinstance(cap_final, int) and cap_final >= 15) else "",
        "6": g6 if (g3b == "Y" and isinstance(cap_final, int) and cap_final >= 15 and g5 != 0) else "",
        "calamity": "",
        "calamity_note": "",
        "note": cq.get("note", ""),
        "evidence": cq.get("evidence", "")
    }

    entry = {
        "id": cid,
        "universe": uni,
        "qualitative": qual
    }

    # Run validation and waterfall from screener
    val_qual, _, warnings = validate_and_waterfall(entry)
    if warnings:
        all_warnings.append((cid, warnings))

    # Update qual with strictly validated & waterfalled qual
    # and map back keys to match JSON format
    entry["qualitative"] = val_qual
    evaluated_list.append(entry)

print(f"Evaluated {len(evaluated_list)} companies.")
if all_warnings:
    print(f"Encountered {len(all_warnings)} warnings:")
    for cid, w in all_warnings:
        print(f"  {cid}: {w}")
else:
    print("ALL 68 COMPANIES PASSED VALIDATION WITH ZERO WARNINGS!")
