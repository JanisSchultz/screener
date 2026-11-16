"""Build evaluated payload for Batch 01 (65 companies) strictly adhering to
QUALITATIVE_EVALUATION_SPEC.md and COMPANY_EVALUATION_SPEC.md.
"""
import json
from pathlib import Path
import sys

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
from screener.bulk_scorer import validate_company_evaluation, load_universe_inputs

batch_file = ROOT / "evaluations" / "batches" / "batch_01.json"
with open(batch_file, "r", encoding="utf-8") as f:
    batch_data = json.load(f)

companies = batch_data["companies"]
print(f"Loaded {len(companies)} companies from {batch_file}")

# Evaluation dictionary keyed by id
evaluated_specs = {
    # 1. APP (AppLovin, us, Comm Services / Advertising)
    "APP": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 15Y reduced by -5Y for ad-tech rivalry (4_riv=1) and mobile OS platform dependency (4_sup=1).",
        "5": "", "6": "",
    },
    # 2. OMC (Omnicom Group, us, Comm Services / Advertising) - FAILS G3
    "OMC": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 3. PUB.FR (Publicis, eu, Comm Services / Advertising) - FAILS G3b
    "PUB.FR": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 4. WPP.GB (WPP, eu, Comm Services / Advertising) - FAILS G3b
    "WPP.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 5. FOXA (Fox Corporation, us, Comm Services / Broadcasting) - FAILS G3b
    "FOXA": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 6. CHTR (Charter Communications, us, Comm Services / Cable & Satellite) - FAILS G3b
    "CHTR": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 7. CMCSA (Comcast, us, Comm Services / Cable & Satellite) - FAILS G3b
    "CMCSA": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 8. BCE.CA (BCE, ca, Comm Services / Telecom) - FAILS G3b
    "BCE.CA": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 9. T (AT&T, us, Comm Services / Telecom) - FAILS G3b
    "T": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 10. T.CA (TELUS, ca, Comm Services / Telecom) - FAILS G3b
    "T.CA": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 11. VZ (Verizon, us, Comm Services / Telecom) - FAILS G3b
    "VZ": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 12. BT.A.GB (BT, eu, Comm Services / Telecom) - FAILS G3b
    "BT.A.GB": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 13. DTE.DE (Deutsche Telekom, eu, Comm Services / Telecom) - FAILS G3b
    "DTE.DE": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 14. ELISA.FI (Elisa, eu, Comm Services / Telecom) - FAILS G3b
    "ELISA.FI": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 15. KPN.NL (KPN, eu, Comm Services / Telecom) - FAILS G3b
    "KPN.NL": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 16. ORA.FR (Orange, eu, Comm Services / Telecom) - FAILS G3b
    "ORA.FR": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 17. SCMN.CH (Swisscom, eu, Comm Services / Telecom) - FAILS G3b
    "SCMN.CH": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 18. SUNN.CH (Sunrise, eu, Comm Services / Telecom) - FAILS G3b
    "SUNN.CH": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 19. TEF.ES (Telefónica, eu, Comm Services / Telecom) - FAILS G3b
    "TEF.ES": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 20. TEL.NO (Telenor, eu, Comm Services / Telecom) - FAILS G3b
    "TEL.NO": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 21. TEL2 B.SE (Tele2, eu, Comm Services / Telecom) - FAILS G3b
    "TEL2 B.SE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 22. TELIA.SE (Telia, eu, Comm Services / Telecom) - FAILS G3b
    "TELIA.SE": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 23. TTWO (Take-Two Interactive, us, Comm Services / Games) - FAILS G3b
    "TTWO": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 24. GOOGL (Alphabet Inc., us, Comm Services / Interactive Media) - CALAMITY PASS
    "GOOGL": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 1,
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -15Y for open-source AI entrant risk (4_ent=1), hyperscaler AI capex arms race (4_riv=1), enterprise multi-homing (4_buy=1), energy/TSMC supplier bottlenecks (4_sup=1), and conversational AI search substitution & tech clock speed (4_sub=1).",
        "5": 1, "6": "N",
    },
    # 25. AUTO.GB (Auto Trader, eu, Comm Services / Interactive Media) - QUALITY PASS
    "AUTO.GB": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for dealer group buyer power (4_buy=1), alternative portal rivalry (4_riv=1), and digital automotive portal clock speed (4_sub=1).",
        "5": 1, "6": "Y",
    },
    # 26. G24.DE (Scout24, eu, Comm Services / Interactive Media) - QUALITY PASS
    "G24.DE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for portal rivalry with Kleinanzeigen/Immowelt (4_riv=1), estate agent buyer pushback (4_buy=1), and digital platform clock speed (4_sub=1).",
        "5": 1, "6": "Y",
    },
    # 27. RMV.GB (Rightmove, eu, Comm Services / Interactive Media) - QUALITY PASS
    "RMV.GB": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for CoStar-backed OnTheMarket rivalry (4_riv=1), estate agent buyer pushback (4_buy=1), and digital classified clock speed (4_sub=1).",
        "5": 1, "6": "Y",
    },
    # 28. VEND.NO (Vend Marketplaces, eu, Comm Services / Interactive Media) - FAILS G3b
    "VEND.NO": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 29. NFLX (Netflix, us, Comm Services / Entertainment) - FAILS G4 (FATAL FLAW)
    "NFLX": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 10Y, REJECT): Long-form video attention substitution from algorithmic short-form video and generative media (4_sub=2) alongside streaming tech giant rivalry (4_riv=1) and sports/talent content supplier inflation (4_sup=1).",
        "5": "", "6": "",
    },
    # 30. SKYD (Skydance, us, Comm Services / Entertainment) - FAILS G3b
    "SKYD": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 31. NWSA (News Corp, us, Comm Services / Publishing) - FAILS G3b
    "NWSA": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 32. INF.GB (Informa, eu, Comm Services / Publishing) - FAILS G6
    "INF.GB": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for event marketing budget cyclicality (4_buy=1), exhibition organizer rivalry (4_riv=1), and open-access/virtual substitution (4_sub=1).",
        "5": 1, "6": "N",
    },
    # 33. RCI.B.CA (Rogers Communications, ca, Comm Services / Telecom) - FAILS G3b
    "RCI.B.CA": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 34. TMUS (T-Mobile US, us, Comm Services / Telecom) - FAILS G3b
    "TMUS": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 35. FNTN.DE (freenet, eu, Comm Services / Telecom) - FAILS G3b
    "FNTN.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 36. VOD.GB (Vodafone, eu, Comm Services / Telecom) - FAILS G3b
    "VOD.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 37. ZEG.GB (Zegona, eu, Comm Services / Telecom) - FAILS G3b
    "ZEG.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 38. ROST (Ross Stores, us, Consumer Disc / Apparel Retail) - QUALITY PASS
    "ROST": {
        "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for off-price rivalry with TJX/Burlington (4_riv=1), closeout inventory supply access (4_sup=1), and digital discount apparel substitution (4_sub=1).",
        "5": 1, "6": "Y",
    },
    # 39. TJX (TJX Companies, us, Consumer Disc / Apparel Retail) - QUALITY PASS
    "TJX": {
        "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for off-price retail rivalry (4_riv=1) and e-commerce channel substitution (4_sub=1).",
        "5": 2, "6": "Y",
    },
    # 40. ITX.ES (Inditex, eu, Consumer Disc / Apparel Retail) - QUALITY PASS
    "ITX.ES": {
        "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for fast-fashion rivalry with Shein/H&M (4_riv=1), fashion trend buyer power (4_buy=1), and ultra-fast digital fashion substitution (4_sub=1).",
        "5": 2, "6": "Y",
    },
    # 41. NKE (Nike, Inc., us, Consumer Disc / Apparel & Luxury) - FAILS G4 (FATAL FLAW)
    "NKE": {
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 1,
        "4_ent": 0, "4_riv": 2, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 10Y, REJECT): Severe athletic footwear and apparel brand rivalry from On, Hoka, and niche performance entrants (4_riv=2) alongside wholesale buyer power (4_buy=1) and athleisure trend substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 42. ADS.DE (adidas, eu, Consumer Disc / Apparel & Luxury) - FAILS G4
    "ADS.DE": {
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for athletic apparel rivalry (4_riv=1), wholesale retailer buyer power (4_buy=1), and fashion-trend cycle substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 43. CFR.CH (Richemont, eu, Consumer Disc / Luxury) - QUALITY PASS
    "CFR.CH": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for luxury conglomerate jewelry competition from LVMH/Tiffany (4_riv=1).",
        "5": 1, "6": "Y",
    },
    # 44. MC.FR (LVMH, eu, Consumer Disc / Luxury) - QUALITY PASS
    "MC.FR": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for luxury conglomerate rivalry (4_riv=1) and consumer luxury spending cyclicality/substitution (4_sub=1).",
        "5": 1, "6": "Y",
    },
    # 45. MONC.IT (Moncler, eu, Consumer Disc / Luxury) - FAILS G4
    "MONC.IT": {
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for luxury outerwear rivalry (4_riv=1), discretionary fashion buyer power (4_buy=1), and outerwear seasonality/climate substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 46. F (Ford Motor Company, us, Consumer Disc / Autos) - FAILS G3
    "F": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 47. TSLA (Tesla, Inc., us, Consumer Disc / Autos) - FAILS G3b
    "TSLA": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 48. BMW.DE (BMW, eu, Consumer Disc / Autos) - FAILS G3b
    "BMW.DE": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 49. MBG.DE (Mercedes-Benz, eu, Consumer Disc / Autos) - FAILS G3b
    "MBG.DE": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 50. RACE.IT (Ferrari, eu, Consumer Disc / Luxury Autos) - FAILS G6
    "RACE.IT": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 1,
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4n": "Deliberate ultra-luxury vehicle scarcity model, multi-year order backlogs, and Formula 1 heritage insulate the franchise across all five competitive forces and macrotrends.",
        "5": 2, "6": "N",
    },
    # 51. RNO.FR (Renault, eu, Consumer Disc / Autos) - FAILS G3b
    "RNO.FR": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 52. STLAM.IT (Stellantis, eu, Consumer Disc / Autos) - FAILS G3b
    "STLAM.IT": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 53. VOW3.DE (Volkswagen, eu, Consumer Disc / Autos) - FAILS G3b
    "VOW3.DE": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 54. APTV (Aptiv, us, Consumer Disc / Auto Parts) - FAILS G3b
    "APTV": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 55. MG.CA (Magna International, ca, Consumer Disc / Auto Parts) - FAILS G3b
    "MG.CA": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 56. CON.DE (Continental, eu, Consumer Disc / Auto Parts) - FAILS G3b
    "CON.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 57. FR.FR (Valeo, eu, Consumer Disc / Auto Parts) - FAILS G3b
    "FR.FR": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 58. AZO (AutoZone, us, Consumer Disc / Auto Retail) - FAILS G6
    "AZO": {
        "3_tb": 0, "3_ia": 2, "3_se": 1, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for commercial DIFM rivalry (4_riv=1), aftermarket supplier leverage (4_sup=1), and secular EV powertrain transition (4_sub=1).",
        "5": 1, "6": "N",
    },
    # 59. ORLY (O'Reilly Automotive, us, Consumer Disc / Auto Retail) - QUALITY PASS
    "ORLY": {
        "3_tb": 0, "3_ia": 2, "3_se": 1, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for aftermarket parts rivalry (4_riv=1), supplier consolidation (4_sup=1), and long-term EV powertrain transition (4_sub=1).",
        "5": 1, "6": "Y",
    },
    # 60. AG1.DE (AUTO1 Group, eu, Consumer Disc / Auto Retail) - FAILS G3
    "AG1.DE": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 61. DIE.BE (D'Ieteren, eu, Consumer Disc / Auto Retail) - FAILS G6
    "DIE.BE": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for insurer buyer leverage (4_buy=1), independent glass repair rivalry (4_riv=1), and automotive smart glass/ADAS technology evolution (4_sub=1).",
        "5": 1, "6": "N",
    },
    # 62. AMZN (Amazon, us, Consumer Disc / Broadline Retail) - FAILS G6
    "AMZN": {
        "3_tb": 1, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -15Y for cross-border e-commerce entrants (4_ent=1), hyperscaler and retail rivalry (4_riv=1), buyer cost-optimization leverage (4_buy=1), energy/labor supplier constraints (4_sup=1), and agentic commerce substitution (4_sub=1).",
        "5": 1, "6": "N",
    },
    # 63. DOL.CA (Dollarama, ca, Consumer Disc / Broadline Retail) - QUALITY PASS
    "DOL.CA": {
        "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for Canadian mass-retail rivalry (4_riv=1) and e-commerce discount substitution (4_sub=1).",
        "5": 2, "6": "Y",
    },
    # 64. EBAY (eBay Inc., us, Consumer Disc / Broadline Retail) - FAILS G4
    "EBAY": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 15Y reduced by -5Y for specialized vertical marketplace rivalry (4_riv=1) and social commerce/AI visual shopping substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 65. GRMN (Garmin, us, Consumer Disc / Consumer Electronics) - FAILS G4
    "GRMN": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 1,
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for consumer tech smartwatch rivalry (4_riv=1), consumer upgrade-cycle buyer leverage (4_buy=1), and non-wrist wearable sensor substitution (4_sub=1).",
        "5": "", "6": "",
    },
}

# Verify coverage
missing = set(c["identity"]["id"] for c in companies) - set(evaluated_specs.keys())
assert not missing, f"Missing evaluations for: {missing}"
extra = set(evaluated_specs.keys()) - set(c["identity"]["id"] for c in companies)
assert not extra, f"Extra evaluations for: {extra}"

evaluated_companies = []

for c in companies:
    ident = c["identity"]
    cid = ident["id"]
    u = ident["universe"]
    cur = c["current_qualitative"]
    spec = evaluated_specs[cid]
    
    qual = dict(cur) # start with existing fields (1, 2, 2r, 3m, note, evidence, etc.)
    
    # Update Gate 3 moat scores
    for k in ("3_tb", "3_ia", "3_se", "3_rd"):
        qual[k] = spec[k]
        
    m_tuple = (spec["3_tb"], spec["3_ia"], spec["3_se"], spec["3_rd"])
    cap_init = compute_initial_cap_from_scores(m_tuple)
    
    # 3a derivation
    if max(m_tuple) == 0:
        qual["3a"] = "None"
    else:
        # Top archetype matching highest score
        # Preserve existing 3a if it is among the highest scorers
        top_archs = []
        if spec["3_tb"] == max(m_tuple): top_archs.append("Toll booth & switching costs")
        if spec["3_ia"] == max(m_tuple): top_archs.append("Irreplaceable infrastructure & intangibles")
        if spec["3_se"] == max(m_tuple): top_archs.append("Scale economies shared")
        if spec["3_rd"] == max(m_tuple): top_archs.append("R&D & innovation leadership")
        
        if qual.get("3a") in top_archs:
            pass # keep current
        else:
            qual["3a"] = top_archs[0]

    # Gate 3 waterfall
    g3_pass = (qual["3a"] != "None") and (qual["3b"] == "Y" or qual.get("calamity") == "Y")
    
    if not g3_pass:
        # Scrub Gate 4 and downstream
        for k in ("4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n", "5", "6"):
            qual[k] = ""
        qual["calamity"] = ""
        qual["calamity_note"] = ""
    else:
        # Pass Gate 3: populate Gate 4
        for k in ("4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4n"):
            qual[k] = spec[k]
            
        f_tuple = (spec["4_ent"], spec["4_riv"], spec["4_buy"], spec["4_sup"], spec["4_sub"])
        cap_final, mod_h, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)
        qual["4"] = cap_final
        
        # Gate 4 waterfall
        if cap_final < 15:
            qual["5"] = ""
            qual["6"] = ""
            qual["calamity"] = ""
            qual["calamity_note"] = ""
        else:
            qual["5"] = spec["5"]
            qual["6"] = spec["6"]
            # calamity preserved if GOOGL
            if cid == "GOOGL":
                qual["calamity"] = "Y"
                qual["calamity_note"] = cur["calamity_note"]
            else:
                qual["calamity"] = ""
                qual["calamity_note"] = ""

    evaluated_companies.append({
        "id": cid,
        "universe": u,
        "qualitative": qual,
    })

out_file = ROOT / "evaluations" / "completed" / "batch_01_evaluated.json"
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(evaluated_companies, f, indent=2)

print(f"Successfully wrote {len(evaluated_companies)} evaluated companies to {out_file}")
