"""Batch 02 Qualitative Evaluation Builder.

Evaluates all 65 companies in Batch 02 according to QUALITATIVE_EVALUATION_SPEC.md,
COMPANY_EVALUATION_SPEC.md, and Munger sequential waterfall standards.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.gates import (
    compute_initial_cap_from_scores,
    compute_final_cap_from_scores,
)
from screener.bulk_scorer import validate_company_evaluation, ingest_evaluations, load_universe_inputs, UNIVERSES

def main():
    batch_file = ROOT / "evaluations" / "batches" / "batch_02.json"
    with batch_file.open(encoding="utf-8") as f:
        batch_data = json.load(f)

    companies = batch_data["companies"]
    assert len(companies) == 65, f"Expected 65 companies, got {len(companies)}"

    # Specific qualitative score overrides for Batch 02
    # Structure: cid -> dict of qualitative scores and 4n note
    eval_specs = {
        # 1. GPC: Distributors
        "GPC": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 2. DCC.GB: Distributors
        "DCC.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 3. INCH.GB: Distributors
        "INCH.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 4. PSON.GB: Education Services
        "PSON.GB": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "Toll booth & switching costs", "3b": "N",
        },
        # 5. DECK: Footwear
        "DECK": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 1, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -10Y for footwear brand entry barriers (4_ent=1); running and casual shoe rivalry with Nike and On (4_riv=1); Asian supply-chain tariff exposure (4_sup=1); and fashion cycle substitution risk (4_sub=1).",
        },
        # 6. HD: Home Improvement Retail
        "HD": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for big-box home-improvement rivalry with Lowe's (4_riv=1); Pro contractor wholesale buying power (4_buy=1); and building material tariff/commodity supply volatility (4_sup=1); unreplicable big-box real estate and heavy-freight logistics provide strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 7. LOW: Home Improvement Retail
        "LOW": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 8. KGF.GB: Home Improvement Retail
        "KGF.GB": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 9. TSCO: Other Specialty Retail
        "TSCO": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "Toll booth & switching costs", "3b": "N",
        },
        # 10. CMG: Restaurants
        "CMG": {
            "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 2, "4_sub": 0,
            "4n": "Fatal-Flaw Cap triggered (Final CAP = 10Y, REJECT): structural food-service wage inflation and labor shortages under Macrotrend #2 (4_sup=2) alongside fast-casual competitive rivalry (4_riv=1) and consumer price elasticity (4_buy=1).",
        },
        # 11. DPZ: Restaurants
        "DPZ": {
            "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 25Y reduced by -10Y for third-party delivery aggregator substitution (4_sub=1); fast-food promotional rivalry (4_riv=1); and consumer price elasticity (4_buy=1).",
            "5": 1, "6": "N",
        },
        # 12. MCD: Restaurants
        "MCD": {
            "3_tb": 1, "3_ia": 2, "3_se": 1, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 30Y reduced by -10Y for QSR value discounting rivalry (4_riv=1); low-income consumer price resistance (4_buy=1); and franchisee labor/food supply pressures (4_sup=1); unreplicable commercial real-estate footprint provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 13. QSR.CA: Restaurants
        "QSR.CA": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for fast-food promotional rivalry (4_riv=1); consumer budget consciousness (4_buy=1); and franchisee labor/ingredient cost pressure (4_sup=1).",
            "5": 1, "6": "N",
        },
        # 14. SBUX: Restaurants
        "SBUX": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 2, "4_sub": 0,
            "4n": "Fatal-Flaw Cap triggered (Final CAP = 10Y, REJECT): barista labor scarcity, unionization wage pressures, and green coffee cost inflation under Macrotrend #2/#5 (4_sup=2) alongside consumer price resistance to premium drinks (4_buy=1) and specialty coffee rivalry (4_riv=1).",
        },
        # 15. YUM: Restaurants
        "YUM": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for QSR promotional discounting rivalry (4_riv=1); consumer budget consciousness (4_buy=1); and franchisee labor cost inflation (4_sup=1).",
            "5": 1, "6": "N",
        },
        # 16. CPG.GB: Restaurants (mapped)
        "CPG.GB": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for institutional contract procurement rivalry (4_riv=1); client budget scrutiny (4_buy=1); and food/labor input cost inflation (4_sup=1); unmatched Foodbuy scale provides strong structural insulation.",
            "5": 2, "6": "Y",
        },
        # 17. SW.FR: Restaurants (mapped)
        "SW.FR": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 18. DASH: Specialized Consumer Services
        "DASH": {
            "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Toll booth & switching costs", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for food-delivery platform rivalry (4_riv=1); merchant fee resistance (4_buy=1); and gig-courier labor regulation (4_sup=1).",
            "5": 1, "6": "N",
        },
        # 19. DHER.DE: Specialized Consumer Services (mapped)
        "DHER.DE": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "Toll booth & switching costs", "3b": "N",
        },
        # 20. ML.FR: Tires & Rubber (mapped)
        "ML.FR": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 1,
            "3a": "R&D & innovation leadership", "3b": "N",
        },
        # 21. PIRC.IT: Tires & Rubber (mapped)
        "PIRC.IT": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 1,
            "3a": "R&D & innovation leadership", "3b": "N",
        },
        # 22. ADM: Agricultural Products & Services
        "ADM": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 23. BG: Agricultural Products & Services
        "BG": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 24. ABI.BE: Brewers (mapped)
        "ABI.BE": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -5Y for developed-market beer category rivalry (4_riv=1); and consumer substitution toward spirits and RTDs (4_sub=1); global brewing scale provides strong structural insulation.",
            "5": 0, "6": "",
        },
        # 25. CARL B.DK: Brewers (mapped)
        "CARL B.DK": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -5Y for European beer market rivalry (4_riv=1); and consumer alternative beverage substitution (4_sub=1); dominant regional brewing density provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 26. HEIA.NL: Brewers (mapped)
        "HEIA.NL": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -5Y for global brewing competitive rivalry (4_riv=1); and ready-to-drink beverage substitution (4_sub=1); global premium brand equity provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 27. HEIO.NL: Brewers (mapped)
        "HEIO.NL": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -5Y for global brewing competitive rivalry (4_riv=1); and ready-to-drink beverage substitution (4_sub=1); look-through global premium brand equity provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 28. RBREW.DK: Brewers (mapped)
        "RBREW.DK": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 15Y reduced by -5Y for mature Nordic brewing rivalry (4_riv=1); and grocery retailer buyer concentration (4_buy=1).",
        },
        # 29. DG: Consumer Staples Merchandise Retail
        "DG": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 30. DLTR: Consumer Staples Merchandise Retail
        "DLTR": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 31. WMT: Consumer Staples Merchandise Retail
        "WMT": {
            "3_tb": 1, "3_ia": 1, "3_se": 2, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
            "4n": "Initial CAP 30Y reduced by -10Y for omnichannel retail rivalry with Amazon (4_riv=1); distribution center labor wage inflation (4_sup=1); and hard discounter grocery substitution (4_sub=1); unassailable procurement scale provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 32. MKS.GB: Consumer Staples Merchandise Retail (mapped)
        "MKS.GB": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "None", "3b": "N",
        },
        # 33. BF.B: Distillers & Vintners
        "BF.B": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 20Y reduced by -5Y for premium spirits competitive rivalry and spirits inventory normalization (4_riv=1); aged maturation inventory provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 34. STZ: Distillers & Vintners
        "STZ": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 35. CPR.IT: Distillers & Vintners (mapped)
        "CPR.IT": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 36. DGE.GB: Distillers & Vintners (mapped) - Calamity Pass Candidate
        "DGE.GB": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -5Y for spirits promotional rivalry and post-COVID destocking (4_riv=1); and distributor bargaining power (4_buy=1); irreplaceable aged inventory provides strong structural insulation.",
            "5": 0, "6": "Y", "calamity": "Y",
        },
        # 37. RI.FR: Distillers & Vintners (mapped)
        "RI.FR": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 20Y reduced by -5Y for global spirits promotional rivalry (4_riv=1); aged maturation inventory and protected geographical indications provide strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 38. SYY: Food Distributors
        "SYY": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for foodservice distribution rivalry (4_riv=1); restaurant client margin pressure (4_buy=1); and truck driver wage inflation (4_sup=1).",
            "5": 1, "6": "N",
        },
        # 39. ATD.CA: Food Retail
        "ATD.CA": {
            "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 25Y reduced by -5Y for convenience retail competition (4_riv=1); and long-term EV transition fuel volume substitution (4_sub=1); superior procurement scale provides strong structural insulation.",
            "5": 2, "6": "Y",
        },
        # 40. CASY: Food Retail
        "CASY": {
            "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "Toll booth & switching costs", "3b": "Y",
            "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -5Y for long-term rural vehicle electrification and fuel volume substitution (4_sub=1); rural geographic monopoly provides formidable structural insulation.",
            "5": 2, "6": "Y",
        },
        # 41. KR: Food Retail
        "KR": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 42. L.CA: Food Retail
        "L.CA": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 43. MRU.CA: Food Retail
        "MRU.CA": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 44. WN.CA: Food Retail
        "WN.CA": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 45. AD.NL: Food Retail (mapped)
        "AD.NL": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 46. AXFO.SE: Food Retail (mapped)
        "AXFO.SE": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 47. CA.FR: Food Retail (mapped)
        "CA.FR": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 48. JMT.PT: Food Retail (mapped)
        "JMT.PT": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 49. KESKOB.FI: Food Retail (mapped)
        "KESKOB.FI": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 50. SBRY.GB: Food Retail (mapped)
        "SBRY.GB": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 51. TSCO.GB: Food Retail (mapped)
        "TSCO.GB": {
            "3_tb": 0, "3_ia": 0, "3_se": 1, "3_rd": 0,
            "3a": "Scale economies shared", "3b": "N",
        },
        # 52. CHD: Household Products
        "CHD": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -5Y for retail customer concentration and buyer bargaining power (4_buy=1); #1/#2 niche brand leadership provides strong structural insulation.",
            "5": 1, "6": "Y",
        },
        # 53. CL: Household Products
        "CL": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -5Y for global oral care and premium pet food competitive rivalry (4_riv=1); dominant worldwide market share (>41%) and professional endorsements provide unassailable structural insulation.",
            "5": 1, "6": "Y",
        },
        # 54. CLX: Household Products
        "CLX": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 15Y reduced by -5Y for mature household staples competitive rivalry (4_riv=1); and private-label chemical/commodity substitution across bleach and trash bags (4_sub=1).",
        },
        # 55. KMB: Household Products
        "KMB": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "None", "3b": "N",
        },
        # 56. ESSITY B.SE: Household Products (mapped)
        "ESSITY B.SE": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "None", "3b": "N",
        },
        # 57. HEN3.DE: Household Products (mapped)
        "HEN3.DE": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
            "3a": "None", "3b": "N",
        },
        # 58. RKT.GB: Household Products (mapped)
        "RKT.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 59. GIS: Packaged Foods & Meats
        "GIS": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 60. HRL: Packaged Foods & Meats
        "HRL": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 61. KHC: Packaged Foods & Meats
        "KHC": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 62. MDLZ: Packaged Foods & Meats
        "MDLZ": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 63. MKC: Packaged Foods & Meats
        "MKC": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -5Y for private-label basic spice competitive rivalry (4_riv=1); category captaincy and proprietary condiment formulations provide exceptional structural insulation.",
            "5": 1, "6": "Y",
        },
        # 64. SAP.CA: Packaged Foods & Meats
        "SAP.CA": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
        # 65. SJM: Packaged Foods & Meats
        "SJM": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
            "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        },
    }

    evaluated_companies = []

    for c in companies:
        cid = c["identity"]["id"]
        u = c["identity"]["universe"]
        curr_q = dict(c["current_qualitative"])

        if cid not in eval_specs:
            raise ValueError(f"Missing evaluation spec for company: {cid}")

        spec = eval_specs[cid]

        # Apply Gate 3 Moat scores
        m_tuple = (spec["3_tb"], spec["3_ia"], spec["3_se"], spec["3_rd"])
        cap_init = compute_initial_cap_from_scores(m_tuple)
        g3a = spec.get("3a")
        g3b = spec.get("3b")

        qual = {
            "1": curr_q.get("1", "Y"),
            "2": curr_q.get("2", "Y"),
            "2r": curr_q.get("2r", ""),
            "3_tb": spec["3_tb"],
            "3_ia": spec["3_ia"],
            "3_se": spec["3_se"],
            "3_rd": spec["3_rd"],
            "3a": g3a,
            "3b": g3b,
            "3m": curr_q.get("3m", ""),
            "4_ent": "",
            "4_riv": "",
            "4_buy": "",
            "4_sup": "",
            "4_sub": "",
            "4": "",
            "4n": "",
            "5": "",
            "6": "",
            "calamity": spec.get("calamity", curr_q.get("calamity", "")),
            "calamity_note": curr_q.get("calamity_note", ""),
            "note": curr_q.get("note", ""),
            "evidence": curr_q.get("evidence", ""),
        }

        # Check Gate 3 pass/fail
        calamity_active = qual["calamity"] == "Y"
        g3_passes = (g3a != "None") and (g3b == "Y" or (g3b == "N" and calamity_active))

        if not g3_passes:
            # Waterfall: clear G4-G6
            qual["4_ent"] = ""
            qual["4_riv"] = ""
            qual["4_buy"] = ""
            qual["4_sup"] = ""
            qual["4_sub"] = ""
            qual["4"] = ""
            qual["4n"] = ""
            qual["5"] = ""
            qual["6"] = ""
            if qual["calamity"] != "Y":
                qual["calamity"] = ""
                qual["calamity_note"] = ""
        else:
            # Company passes Gate 3: evaluate Gate 4 Porter forces
            f_tuple = (
                spec["4_ent"],
                spec["4_riv"],
                spec["4_buy"],
                spec["4_sup"],
                spec["4_sub"],
            )
            cap_final, mod_h, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)

            qual["4_ent"] = spec["4_ent"]
            qual["4_riv"] = spec["4_riv"]
            qual["4_buy"] = spec["4_buy"]
            qual["4_sup"] = spec["4_sup"]
            qual["4_sub"] = spec["4_sub"]
            qual["4"] = cap_final
            qual["4n"] = spec["4n"]

            if cap_final < 15:
                # Waterfall: clear G5-G6
                qual["5"] = ""
                qual["6"] = ""
                qual["calamity"] = ""
                qual["calamity_note"] = ""
            else:
                # Passes Gate 4: evaluate Gate 5 & Gate 6
                qual["5"] = spec["5"]
                qual["6"] = spec["6"]

                # If G5 is 0 and not calamity, clear Gate 6
                if str(qual["5"]) == "0" and not calamity_active:
                    qual["6"] = ""

        evaluated_companies.append({
            "id": cid,
            "universe": u,
            "qualitative": qual,
        })

    # Validate output path
    out_dir = ROOT / "evaluations" / "completed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "batch_02_evaluated.json"

    out_path.write_text(json.dumps(evaluated_companies, indent=2), encoding="utf-8")
    print(f"Successfully generated {out_path} with {len(evaluated_companies)} companies.")

if __name__ == "__main__":
    main()
