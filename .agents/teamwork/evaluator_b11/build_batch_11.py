import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation, QUAL_COLUMNS
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
BATCH_PATH = ROOT / "evaluations" / "batches" / "batch_11.json"
OUTPUT_PATH = ROOT / "evaluations" / "completed" / "batch_11_evaluated.json"

# Load source batch 11
with open(BATCH_PATH, "r", encoding="utf-8") as f:
    batch_data = json.load(f)

companies = batch_data["companies"]
assert len(companies) == 65, f"Expected 65 companies, got {len(companies)}"

# Evaluation mappings for Batch 11:
# id -> {
#   "3_scores": (3_tb, 3_ia, 3_se, 3_rd),
#   "3a": primary moat label,
#   "3b": "Y" or "N",
#   "4_forces": (4_ent, 4_riv, 4_buy, 4_sup, 4_sub) or None if fails G3,
#   "4n": note or "",
#   "5": score or "",
#   "6": "Y" / "N" or "",
#   "calamity": "Y" or "",
#   "calamity_note": str or "",
# }
EVALS = {
    # 1. SFS Group
    "SFSN.CH": {
        "3_scores": (1, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 2. SKF
    "SKF B.SE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 2),
        "4n": "Initial CAP 20Y capped at 5Y fatal flaw for EV powertrain substitution eliminating 30-40% of automotive rotating bearings (4_sub=2), compounded by automotive OEM buyer power (4_buy=1) and bearing manufacturer rivalry (4_riv=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 3. Spirax Group
    "SPX.GB": {
        "3_scores": (2, 1, 0, 1),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for biopharma destocking and procurement consolidation (4_buy=1), competing single-use bioprocessing rivalry (4_riv=1), and industrial thermal electrification substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 4. Sulzer
    "SUN.CH": {
        "3_scores": (1, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 5. Tomra
    "TOM.NO": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 6. Trelleborg
    "TREL B.SE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 1),
        "4n": "Initial CAP 20Y reduced by -10Y for industrial seal rivalry (4_riv=1), OEM customer bargaining power (4_buy=1), specialty elastomer feedstock volatility (4_sup=1), and EV component substitution (4_sub=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 7. Valmet
    "VALMT.FI": {
        "3_scores": (1, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 8. Wärtsilä
    "WRT1V.FI": {
        "3_scores": (1, 1, 0, 1),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for marine engine and battery storage rivalry (4_riv=1) and cyclical shipyard buyer power (4_buy=1).",
        "5": 1,
        "6": "N",
        "calamity": "",
        "calamity_note": "",
    },
    # 9. A.P. Moller-Maersk
    "MAERSK B.DK": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 10. Southwest Airlines
    "LUV": {
        "3_scores": (0, 0, 1, 0),
        "3a": "Scale economies shared",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 11. easyJet
    "EZJ.GB": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 12. IAG
    "IAG.ES": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 13. Lufthansa
    "LHA.DE": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 14. Uber
    "UBER": {
        "3_scores": (1, 0, 1, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 2),
        "4n": "Initial CAP 20Y capped at 5Y fatal flaw for autonomous vehicle robotaxi substitution (4_sub=2) threatening human-driver gig network, alongside consumer multi-homing (4_buy=1), delivery rivalry (4_riv=1), and gig labor regulatory pressure (4_sup=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 15. Canadian Pacific Kansas City
    "CP.CA": {
        "3_scores": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 0, 1, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Class I railroad and intermodal rivalry (4_riv=1) and unionized rail labor bargaining power (4_sup=1); unreplicable tri-national right-of-way insulates against new entrants and substitution.",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 16. CSX Corporation
    "CSX": {
        "3_scores": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 0, 1, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for Eastern rail duopoly rivalry with Norfolk Southern (4_riv=1), union rail labor inflation (4_sup=1), and thermal coal volume phase-out substitution (4_sub=1).",
        "5": 1,
        "6": "N",
        "calamity": "",
        "calamity_note": "",
    },
    # 17. Norfolk Southern
    "NSC": {
        "3_scores": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 0, 1, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Eastern rail duopoly rivalry (4_riv=1) and unionized rail labor bargaining power (4_sup=1).",
        "5": 1,
        "6": "N",
        "calamity": "",
        "calamity_note": "",
    },
    # 18. Union Pacific Corporation
    "UNP": {
        "3_scores": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 0, 1, 0),
        "4n": "Initial CAP 25Y reduced by -5Y for Western rail duopoly rivalry with BNSF (4_riv=1) and unionized railroad labor bargaining power (4_sup=1); unreplicable 32,000-mile right-of-way insulates against new entrants and substitution.",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 19. Equifax
    "EFX": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for credit bureau triopoly rivalry (4_riv=1), mortgage lender buyer bargaining pushback (4_buy=1), and alternative credit scoring substitution (4_sub=1).",
        "5": 1,
        "6": "N",
        "calamity": "Y",
        "calamity_note": batch_data["companies"][18]["current_qualitative"]["calamity_note"],
    },
    # 20. Verisk Analytics
    "VRSK": {
        "3_scores": (2, 2, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for catastrophe modeling rivalry from Moody's RMS (4_riv=1), tier-one P&C insurer buyer power (4_buy=1), and internal carrier AI analytics substitution (4_sub=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 21. Bureau Veritas
    "BVI.FR": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for TIC oligopoly rivalry with SGS and Intertek (4_riv=1), multinational corporate buyer procurement power (4_buy=1), and qualified inspector wage inflation (4_sup=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 22. Experian
    "EXPN.GB": {
        "3_scores": (2, 2, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for credit bureau triopoly rivalry with Equifax and TransUnion (4_riv=1), banking customer buyer power (4_buy=1), and open-banking/alternative data substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 23. Intertek
    "ITRK.GB": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for TIC peer rivalry with Bureau Veritas and SGS (4_riv=1), corporate retail client buyer power (4_buy=1), and laboratory technician wage inflation (4_sup=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 24. RELX
    "REL.GB": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for legal/analytics rivalry with Thomson Reuters and Wolters Kluwer (4_riv=1), academic library and corporate buyer power (4_buy=1), and generative AI research assistant substitution (4_sub=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 25. SGS
    "SGSN.CH": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for TIC peer rivalry with Bureau Veritas and Intertek (4_riv=1), commodity client buyer power (4_buy=1), and qualified inspector wage inflation (4_sup=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 26. Sweco
    "SWEC B.SE": {
        "3_scores": (0, 0, 0, 0),
        "3a": "None",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 27. Thomson Reuters
    "TRI": {
        "3_scores": (2, 2, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (1, 1, 1, 0, 2),
        "4n": "Initial CAP 30Y capped at 10Y fatal flaw for generative AI legal drafting and research substitution (4_sub=2) compressing seat-based legal SaaS, alongside legal-AI startup entrant risk (4_ent=1), LexisNexis rivalry (4_riv=1), and law firm buyer consolidation (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 28. Wolters Kluwer
    "WKL.NL": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for tax/compliance software rivalry (4_riv=1), hospital and corporate buyer consolidation (4_buy=1), and clinical/tax AI assistance substitution (4_sub=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 29. Loomis
    "LOOMIS.SE": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 30. Securitas
    "SECU B.SE": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 31. Verisure
    "VSURE.SE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (1, 1, 1, 0, 2),
        "4n": "Initial CAP 20Y capped at 5Y fatal flaw for DIY smart home and unmonitored camera substitution (4_sub=2), compounded by DIY hardware entrant pressure (4_ent=1), residential security rivalry (4_riv=1), and consumer subscription fatigue (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 32. Fastenal
    "FAST": {
        "3_scores": (2, 2, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 30Y reduced by -10Y for MRO distribution rivalry with Grainger and MSC (4_riv=1), national manufacturing account buyer power (4_buy=1), and fastener import tariff/supply chain volatility (4_sup=1); embedded Onsite and vending footprint insulates against new entrants and substitution.",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 33. Ferguson Enterprises
    "FERG": {
        "3_scores": (1, 2, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for regional wholesale and big-box Pro rivalry (4_riv=1), large commercial contractor buyer power (4_buy=1), and major HVAC/plumbing OEM supplier concentration (4_sup=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 34. United Rentals
    "URI": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 35. Addtech
    "ADDT B.SE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for fragmented industrial niche rivalry (4_riv=1) and OEM buyer bargaining power (4_buy=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 36. Beijer Ref
    "BEIJ B.SE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for regional wholesale refrigeration rivalry (4_riv=1) and commercial supermarket contractor buyer power (4_buy=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 37. Brenntag
    "BNR.DE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 38. Bunzl
    "BNZL.GB": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for broadline distributor rivalry (4_riv=1) and large grocery/foodservice client buyer power (4_buy=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 39. Diploma
    "DPLM.GB": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 1, 0),
        "4n": "Initial CAP 25Y reduced by -10Y for specialized niche component rivalry (4_riv=1), industrial OEM buyer power (4_buy=1), and specialized aerospace/polymer supplier lead-time constraints (4_sup=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 40. Howden Joinery
    "HWDN.GB": {
        "3_scores": (1, 1, 1, 0),
        "3a": "Scale economies shared",
        "3b": "Y",
        "4_forces": (0, 1, 0, 1, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for UK kitchen retail and merchant rivalry (4_riv=1) and raw timber/cabinet material input volatility (4_sup=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 41. IMCD
    "IMCD.NL": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 42. Indutrade
    "INDT.SE": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 0),
        "4n": "Initial CAP 20Y reduced by -5Y for specialized engineering niche rivalry (4_riv=1) and European OEM buyer bargaining power (4_buy=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 43. RS Group
    "RS1.GB": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_forces": (1, 1, 1, 0, 2),
        "4n": "Initial CAP 20Y capped at 5Y fatal flaw for B2B e-commerce marketplace and direct OEM substitution (4_sub=2), compounded by digital marketplace entrant pressure (4_ent=1), electronic component distributor rivalry (4_riv=1), and transparent online buyer price discovery (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 44. Rexel
    "RXL.FR": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 45. tk accelis
    "TKCC.DE": {
        "3_scores": (0, 1, 0, 0),
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 46. Adobe Inc.
    "ADBE": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (1, 1, 1, 0, 2),
        "4n": "Initial CAP 25Y capped at 5Y fatal flaw for generative AI creative synthesis substitution (4_sub=2) automating human designer workflows, alongside generative tool entrant pressure (4_ent=1), design software rivalry from Canva/Figma (4_riv=1), and enterprise seat-count rationalization (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 47. Autodesk
    "ADSK": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for AEC software rivalry with Nemetschek and Bentley (4_riv=1), architecture firm buyer pushback on licensing (4_buy=1), and fast AEC software clock speed with generative BIM drafting substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 48. Cadence Design Systems
    "CDNS": {
        "3_scores": (2, 2, 0, 2),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for EDA duopoly rivalry with Synopsys (4_riv=1), semiconductor mega-customer buyer bargaining power (4_buy=1), and fast semiconductor tech clock speed with AI chip layout automation (4_sub=1); foundry PDK certifications provide unassailable insulation against new entrants.",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 49. Constellation Software
    "CSU.CA": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for private equity VMS acquisition rivalry (4_riv=1), niche enterprise buyer consolidation (4_buy=1), and fast tech clock speed with AI vertical workflow substitution (4_sub=1).",
        "5": 2,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 50. Datadog
    "DDOG": {
        "3_scores": (1, 0, 0, 1),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 51. Fair Isaac
    "FICO": {
        "3_scores": (2, 2, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 2),
        "4n": "Initial CAP 30Y capped at 10Y fatal flaw for FHFA-mandated VantageScore substitution breaking FICO's exclusive mortgage monopoly (4_sub=2), compounded by VantageScore consortium rivalry (4_riv=1) and mortgage lender pushback against price gouging (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 52. Intuit
    "INTU": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for accounting/tax software rivalry with Xero (4_riv=1), SMB customer price hike sensitivity (4_buy=1), and fast software clock speed with AI bookkeeping automation (4_sub=1).",
        "5": 0,
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 53. Oracle Corporation
    "ORCL": {
        "3_scores": (2, 1, 0, 1),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 54. Palantir Technologies
    "PLTR": {
        "3_scores": (2, 1, 0, 1),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (1, 1, 1, 0, 2),
        "4n": "Initial CAP 30Y capped at 10Y fatal flaw for open data lakehouse and modular AI agent architecture substitution (4_sub=2) displacing monolithic ontology lock-in, alongside AI platform entrant risk (4_ent=1), hyperscaler rivalry (4_riv=1), and enterprise buyer pushback against high contract minimums (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 55. PTC Inc.
    "PTC": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for discrete PLM/CAD rivalry with Siemens and Dassault (4_riv=1), industrial OEM buyer procurement power (4_buy=1), and fast software clock speed with generative CAD drafting substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 56. Synopsys
    "SNPS": {
        "3_scores": (2, 2, 0, 2),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for EDA duopoly rivalry with Cadence (4_riv=1), semiconductor mega-customer buyer bargaining power (4_buy=1), and fast semiconductor tech clock speed with AI chip design automation (4_sub=1); foundry PDK certifications provide unassailable insulation against new entrants.",
        "5": 1,
        "6": "N",
        "calamity": "Y",
        "calamity_note": batch_data["companies"][55]["current_qualitative"]["calamity_note"],
    },
    # 57. Trimble Inc.
    "TRMB": {
        "3_scores": (1, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (1, 1, 1, 0, 2),
        "4n": "Initial CAP 20Y capped at 5Y fatal flaw for captive equipment OEM telematics substitution (4_sub=2) bypassing aftermarket positioning, alongside positioning sensor entrant pressure (4_ent=1), Leica/Topcon rivalry (4_riv=1), and cyclical construction buyer leverage (4_buy=1).",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 58. Tyler Technologies
    "TYL": {
        "3_scores": (2, 1, 0, 1),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for public sector software rivalry with CentralSquare and Axon (4_riv=1), municipal government procurement buyer power (4_buy=1), and fast public-sector tech modernization clock speed (4_sub=1); state/county statutory lock-in provides unassailable insulation against new entrants.",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 59. Workday, Inc.
    "WDAY": {
        "3_scores": (2, 0, 0, 1),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 60. Dassault Systèmes
    "DSY.FR": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for industrial PLM rivalry with Siemens and PTC (4_riv=1), aerospace/auto OEM buyer procurement power (4_buy=1), and fast 3D engineering software clock speed with generative CAD substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 61. Nemetschek
    "NEM.DE": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for AEC software rivalry with Autodesk and Bentley (4_riv=1), construction contractor buyer pushback (4_buy=1), and fast AEC software clock speed with generative BIM drafting substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 62. Octave
    "OCTV SDB.SE": {
        "3_scores": (1, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
    # 63. SAP
    "SAP.DE": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for best-of-breed application rivalry from Salesforce and Oracle (4_riv=1), enterprise customer cloud migration pushback (4_buy=1), and fast software clock speed with enterprise AI agent substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 64. Sage
    "SGE.GB": {
        "3_scores": (2, 1, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for SMB accounting rivalry with Intuit and Xero (4_riv=1), SMB customer subscription price sensitivity (4_buy=1), and fast software clock speed with AI bookkeeping substitution (4_sub=1).",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
    },
    # 65. Temenos
    "TEMN.CH": {
        "3_scores": (2, 0, 0, 0),
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_forces": None,
        "4n": "",
        "5": "",
        "6": "",
        "calamity": "",
        "calamity_note": "",
    },
}

evaluated_list = []

for c in companies:
    cid = c["identity"]["id"]
    u = c["identity"]["universe"]
    cq = c["current_qualitative"]

    assert cid in EVALS, f"Missing evaluation mapping for {cid}"
    ev = EVALS[cid]

    m_scores = ev["3_scores"]
    init_cap = compute_initial_cap_from_scores(m_scores)
    g3b = ev["3b"]

    q_dict = {
        "1": "Y",
        "2": "Y",
        "2r": "",
        "3_tb": m_scores[0],
        "3_ia": m_scores[1],
        "3_se": m_scores[2],
        "3_rd": m_scores[3],
        "3a": ev["3a"],
        "3b": g3b,
        "3m": cq["3m"],
    }

    if ev["4_forces"] is not None:
        f_scores = ev["4_forces"]
        final_cap, h, ff = compute_final_cap_from_scores(init_cap, f_scores)
        q_dict["4_ent"] = f_scores[0]
        q_dict["4_riv"] = f_scores[1]
        q_dict["4_buy"] = f_scores[2]
        q_dict["4_sup"] = f_scores[3]
        q_dict["4_sub"] = f_scores[4]
        q_dict["4"] = final_cap
        q_dict["4n"] = ev["4n"]
        q_dict["5"] = ev["5"]
        q_dict["6"] = ev["6"]
    else:
        # Fails Gate 3: clear downstream fields
        q_dict["4_ent"] = ""
        q_dict["4_riv"] = ""
        q_dict["4_buy"] = ""
        q_dict["4_sup"] = ""
        q_dict["4_sub"] = ""
        q_dict["4"] = ""
        q_dict["4n"] = ""
        q_dict["5"] = ""
        q_dict["6"] = ""

    q_dict["calamity"] = ev["calamity"]
    q_dict["calamity_note"] = ev["calamity_note"]
    q_dict["note"] = cq["note"]
    q_dict["evidence"] = cq["evidence"]

    # Verify keys
    for col in QUAL_COLUMNS:
        assert col in q_dict, f"Missing column {col} in q_dict for {cid}"

    evaluated_item = {
        "id": cid,
        "universe": u,
        "qualitative": q_dict,
    }

    # Validate against bulk_scorer rules
    sanitized, warnings, errors = validate_company_evaluation(evaluated_item)
    if errors:
        print(f"ERROR in {cid}: {errors}")
        raise ValueError(f"Validation error for {cid}: {errors}")
    if warnings:
        print(f"Warning in {cid}: {warnings}")

    evaluated_list.append(evaluated_item)

print(f"Successfully evaluated all {len(evaluated_list)} companies with 0 errors!")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(evaluated_list, f, indent=2)

print(f"Wrote output to {OUTPUT_PATH}")
