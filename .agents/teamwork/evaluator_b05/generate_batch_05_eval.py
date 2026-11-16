"""Generate evaluated JSON for batch 05 and validate against all screener rules."""
import json
from pathlib import Path
import sys

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

BATCH_FILE = ROOT / "evaluations" / "batches" / "batch_05.json"
OUT_FILE = ROOT / "evaluations" / "completed" / "batch_05_evaluated.json"

with open(BATCH_FILE, "r", encoding="utf-8") as f:
    batch_data = json.load(f)

companies = batch_data["companies"]
print(f"Loaded {len(companies)} companies from batch_05.json")

# Definitive qualitative evaluations for all 65 companies in Batch 05
# Each entry specifies:
# (3_tb, 3_ia, 3_se, 3_rd, 3a, 3b, 4_ent, 4_riv, 4_buy, 4_sup, 4_sub, 4n, 5, 6)
# Note: For companies failing Gate 3 (3b=='N'), Gate 4 and Gates 5-6 fields are empty strings.
evaluations_map = {
    # 01. LLOY.GB - Lloyds Banking Group
    "LLOY.GB": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for 4 moderate forces: digital fintech Entrants (4_ent=1), mortgage price Rivalry (4_riv=1), broker Buyer power (4_buy=1), and fintech Substitution (4_sub=1).",
        "5": "", "6": ""
    },
    # 02. NDA FI.FI - Nordea
    "NDA FI.FI": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: Nordic peer Rivalry (4_riv=1), digital Buyer price transparency (4_buy=1), and alternative credit Substitution (4_sub=1).",
        "5": 2, "6": "N"
    },
    # 03. NWG.GB - NatWest
    "NWG.GB": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 2, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe commoditized domestic mortgage price Rivalry (4_riv=2) alongside fintech Entrants (4_ent=1), Buyer comparison pressure (4_buy=1), and alternative credit Substitution (4_sub=1).",
        "5": "", "6": ""
    },
    # 04. SAB.ES - Sabadell
    "SAB.ES": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 05. SEB A.SE - SEB
    "SEB A.SE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe structural corporate lending Substitution from private credit and direct debt capital markets (4_sub=2) alongside multinational Buyer treasury power (4_buy=1), Nordic peer Rivalry (4_riv=1), and Entrants (4_ent=1).",
        "5": "", "6": ""
    },
    # 06. SHB A.SE - Handelsbanken
    "SHB A.SE": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: domestic mortgage price Rivalry (4_riv=1), digital Buyer price transparency (4_buy=1), and fintech Substitution (4_sub=1).",
        "5": 2, "6": "N"
    },
    # 07. SWED A.SE - Swedbank
    "SWED A.SE": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for 4 moderate forces: fintech Entrants (4_ent=1), mortgage price Rivalry (4_riv=1), Buyer comparison transparency (4_buy=1), and digital Substitution (4_sub=1).",
        "5": "", "6": ""
    },
    # 08. UBSG.CH - UBS
    "UBSG.CH": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: global wealth management Rivalry (4_riv=1), UHNW/family office Buyer fee scrutiny (4_buy=1), and advisor talent Supplier costs (4_sup=1).",
        "5": 1, "6": "N"
    },
    # 09. UCG.IT - UniCredit
    "UCG.IT": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for 4 moderate forces: digital Entrants (4_ent=1), European commercial banking Rivalry (4_riv=1), corporate Buyer sensitivity (4_buy=1), and fintech Substitution (4_sub=1).",
        "5": "", "6": ""
    },
    # 10. PST.IT - Poste Italiane
    "PST.IT": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: parcel/banking Rivalry (4_riv=1), regulated Buyer postal tariffs (4_buy=1), and digital communication Substitution (4_sub=1).",
        "5": 1, "6": "N"
    },
    # 11. CBOE - Cboe Global Markets
    "CBOE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: multi-listed options Rivalry (4_riv=1), market-maker Buyer fee pushback (4_buy=1), and S&P index royalty Supplier costs (4_sup=1).",
        "5": 1, "6": "Y"
    },
    # 12. CME - CME Group
    "CME": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: bank-backed FMX Entrants (4_ent=1), multi-asset derivatives Rivalry (4_riv=1), and institutional dealer Buyer fee leverage (4_buy=1).",
        "5": 1, "6": "Y"
    },
    # 13. FDS - FactSet
    "FDS": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 10Y, REJECT): severe structural Substitution from generative AI research agents replacing seat-based financial terminals (4_sub=2) alongside investment bank Buyer budget consolidation (4_buy=1).",
        "5": "", "6": ""
    },
    # 14. ICE - Intercontinental Exchange
    "ICE": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: derivatives peer Rivalry (4_riv=1), mortgage tech/dealer Buyer fee scrutiny (4_buy=1), and long-term energy transition Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 15. MCO - Moody's Corporation
    "MCO": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 30Y preserved at 30Y with 0 haircuts: structural regulatory NRSRO duopoly and covenant-mandated rating toll booth exhibit total insulation across all 5 competitive forces.",
        "5": 2, "6": "Y"
    },
    # 16. MSCI - MSCI
    "MSCI": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: index peer Rivalry (4_riv=1), asset manager Buyer fee pressure (4_buy=1), and direct-indexing/ESG Substitution (4_sub=1).",
        "5": 1, "6": "N"
    },
    # 17. NDAQ - Nasdaq, Inc.
    "NDAQ": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: equity exchange Rivalry (4_riv=1), broker/dealer Buyer fee pushback (4_buy=1), and ATS dark pool Substitution (4_sub=1).",
        "5": 1, "6": "N"
    },
    # 18. X.CA - TMX Group
    "X.CA": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: domestic ATS Rivalry (4_riv=1), Big 6 Canadian bank Buyer power (4_buy=1), and US cross-listing Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 19. DB1.DE - Deutsche Börse
    "DB1.DE": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: global derivatives Rivalry (4_riv=1), institutional dealer Buyer fee scrutiny (4_buy=1), and OTC bilateral Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 20. ENX.FR - Euronext
    "ENX.FR": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: European MTF trading Rivalry (4_riv=1), institutional broker Buyer pressure (4_buy=1), and off-exchange OTC Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 21. LSEG.GB - London Stock Exchange Group
    "LSEG.GB": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: financial data Rivalry (4_riv=1), dealer Buyer fee negotiations (4_buy=1), and desktop terminal AI Substitution (4_sub=1).",
        "5": 1, "6": "N"
    },
    # 22. AJG - Arthur J. Gallagher & Co.
    "AJG": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: broker M&A/commission Rivalry (4_riv=1), commercial Buyer price sensitivity (4_buy=1), and digital insurtech Substitution (4_sub=1).",
        "5": 1, "6": "N"
    },
    # 23. AON - Aon plc
    "AON": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: global broker Rivalry (4_riv=1), multinational Buyer fee scrutiny (4_buy=1), and corporate captive Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 24. BRO - Brown & Brown
    "BRO": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: middle-market broker Rivalry (4_riv=1), corporate Buyer fee pushback (4_buy=1), and digital small-business Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 25. ERIE - Erie Indemnity
    "ERIE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: P&C reciprocal policyholder Rivalry (4_riv=1), consumer Buyer price pushback (4_buy=1), and direct-to-consumer digital Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 26. MRSH - Marsh McLennan
    "MRSH": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: global commercial broker Rivalry (4_riv=1), multinational Buyer fee pushback (4_buy=1), and corporate captive Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 27. WTW - Willis Towers Watson
    "WTW": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 2, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe broker Rivalry and producer talent attrition (4_riv=2) trailing Marsh/Aon scale alongside corporate Buyer fee pressure (4_buy=1) and boutique Entrants (4_ent=1).",
        "5": "", "6": ""
    },
    # 28. IBKR - Interactive Brokers
    "IBKR": {
        "3_tb": 1, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "3a": "Scale economies shared", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: retail brokerage Rivalry (4_riv=1), price-conscious active trader Buyer power (4_buy=1), and neo-broker Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 29. MS - Morgan Stanley
    "MS": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: wirehouse/wealth Rivalry (4_riv=1), institutional Buyer fee pressure (4_buy=1), and advisor talent Supplier compensation (4_sup=1).",
        "5": 1, "6": "N"
    },
    # 30. RJF - Raymond James Financial
    "RJF": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for 2 moderate forces: wealth advisor recruiting Rivalry (4_riv=1) and retail client Buyer fee pressure (4_buy=1).",
        "5": 1, "6": "N"
    },
    # 31. SCHW - Charles Schwab Corporation
    "SCHW": {
        "3_tb": 1, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "3a": "Scale economies shared", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: mega-custodian Rivalry (4_riv=1), cash-sorting client Buyer behavior (4_buy=1), and fintech neo-broker Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 32. AZA.SE - Avanza
    "AZA.SE": {
        "3_tb": 1, "3_ia": 1, "3_se": 1, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for 2 moderate forces: domestic digital savings Rivalry (4_riv=1) and retail saver Buyer fee sensitivity (4_buy=1).",
        "5": 2, "6": "Y"
    },
    # 33. FBK.IT - FinecoBank
    "FBK.IT": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: Italian wealth advisory Rivalry (4_riv=1), client Buyer fee scrutiny (4_buy=1), and digital broker Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 34. SAVE.SE - Nordnet
    "SAVE.SE": {
        "3_tb": 1, "3_ia": 1, "3_se": 1, "3_rd": 0,
        "3a": "Scale economies shared", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for 2 moderate forces: pan-Nordic platform Rivalry (4_riv=1) and retail investor Buyer fee sensitivity (4_buy=1).",
        "5": 1, "6": "Y"
    },
    # 35. TCAP.GB - TP ICAP
    "TCAP.GB": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe structural Substitution from electronic swap execution and algorithmic cross-matching replacing voice broking (4_sub=2) alongside dealer Buyer fee pressure (4_buy=1), BGC Rivalry (4_riv=1), and electronic platform Entrants (4_ent=1).",
        "5": "", "6": ""
    },
    # 36. AFL - Aflac
    "AFL": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 37. GL - Globe Life
    "GL": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 2, "4_sub": 0,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe captive agent recruiting crisis and regulatory scrutiny post-DOJ investigation (4_sup=2) alongside price-sensitive policyholder Buyer churn (4_buy=1).",
        "5": "", "6": ""
    },
    # 38. GWO.CA - Great-West Lifeco
    "GWO.CA": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 39. MET - MetLife
    "MET": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 40. MFC.CA - Manulife Financial
    "MFC.CA": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 41. PFG - Principal Financial Group
    "PFG": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 42. POW.CA - Power Corporation of Canada
    "POW.CA": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 43. PRU - Prudential Financial
    "PRU": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 44. SLF.CA - Sun Life Financial
    "SLF.CA": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 45. AGN.NL - Aegon
    "AGN.NL": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 46. LGEN.GB - Legal & General
    "LGEN.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 47. MANTA.FI - Mandatum
    "MANTA.FI": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 48. NN.NL - NN Group
    "NN.NL": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 49. PRU.GB - Prudential plc
    "PRU.GB": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 50. SDLF.GB - Standard Life (ex-Phoenix)
    "SDLF.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 51. SLHN.CH - Swiss Life
    "SLHN.CH": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 15Y reduced by -10Y for 3 moderate forces: European demographic workforce shrinkage Substitution (4_sub=1), statutory pension Buyer conversion caps (4_buy=1), and asset management Rivalry (4_riv=1).",
        "5": "", "6": ""
    },
    # 52. STB.NO - Storebrand
    "STB.NO": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 15Y reduced by -10Y for 3 moderate forces: Nordic life/pension Rivalry (4_riv=1), corporate employer Buyer fee pressure (4_buy=1), and demographic aging Substitution (4_sub=1).",
        "5": "", "6": ""
    },
    # 53. BRK.B - Berkshire Hathaway
    "BRK.B": {
        "3_tb": 1, "3_ia": 2, "3_se": 1, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: rail/auto insurance Rivalry (4_riv=1), regulatory utility/shipper Buyer rate pressure (4_buy=1), and coal freight decarbonization Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 54. ACKB.BE - Ackermans & van Haaren
    "ACKB.BE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: marine engineering contract Rivalry (4_riv=1), government/developer Buyer procurement power (4_buy=1), and cyclical offshore project Substitution (4_sub=1).",
        "5": 2, "6": "N"
    },
    # 55. AKER.NO - Aker ASA
    "AKER.NO": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 56. EXO.NL - Exor
    "EXO.NL": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 57. GBLB.BE - Groupe Bruxelles Lambert
    "GBLB.BE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 58. III.GB - 3i Group
    "III.GB": {
        "3_tb": 0, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "3a": "Scale economies shared", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: European discount store Rivalry (4_riv=1), value-conscious consumer Buyer price pressure (4_buy=1), and cross-border ultra-cheap e-commerce Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 59. INDU C.SE - Industrivärden
    "INDU C.SE": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: capital goods peer Rivalry (4_riv=1), industrial Buyer capex cyclicality (4_buy=1), and powertrain transition Substitution (4_sub=1).",
        "5": 1, "6": "Y"
    },
    # 60. INVE B.SE - Investor AB
    "INVE B.SE": {
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for 3 moderate forces: industrial peer Rivalry (4_riv=1), institutional Buyer capex scrutiny (4_buy=1), and technology/patent cycle Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 61. KBCA.BE - KBC Ancora
    "KBCA.BE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 62. LATO B.SE - Latour
    "LATO B.SE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for 3 moderate forces: building product Rivalry (4_riv=1), construction contractor Buyer cyclicality (4_buy=1), and commercial real estate cycle Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 63. LUND B.SE - Lundbergs
    "LUND B.SE": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for 2 moderate forces: commercial office tenant Buyer negotiations (4_buy=1) and hybrid-work office space Substitution (4_sub=1).",
        "5": 2, "6": "Y"
    },
    # 64. TUB.BE - Financière de Tubize
    "TUB.BE": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
    # 65. AIG - American International Group
    "AIG": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4n": "",
        "5": "", "6": ""
    },
}

assert len(evaluations_map) == 65, f"Expected 65 entries in evaluations_map, got {len(evaluations_map)}"
print("Evaluations map has 65 companies.")

evaluated_list = []
all_errors = []
all_warnings = []

for c in companies:
    ident = c["identity"]
    cid = ident["id"]
    u = ident["universe"]
    curr_q = c["current_qualitative"]

    if cid not in evaluations_map:
        raise KeyError(f"Missing evaluation for company {cid}")

    em = evaluations_map[cid]

    # Deterministically calculate CAP if 3b == 'Y'
    if em["3b"] == "Y":
        m_tuple = (em["3_tb"], em["3_ia"], em["3_se"], em["3_rd"])
        cap_init = compute_initial_cap_from_scores(m_tuple)
        f_tuple = (em["4_ent"], em["4_riv"], em["4_buy"], em["4_sup"], em["4_sub"])
        cap_det, mod_h, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)
        g4_val = cap_det
    else:
        g4_val = ""

    qual_dict = {
        "1": curr_q.get("1", "Y"),
        "2": curr_q.get("2", "Y"),
        "2r": curr_q.get("2r", ""),
        "3_tb": em["3_tb"],
        "3_ia": em["3_ia"],
        "3_se": em["3_se"],
        "3_rd": em["3_rd"],
        "3a": em["3a"],
        "3b": em["3b"],
        "3m": curr_q.get("3m", ""),
        "4_ent": em["4_ent"],
        "4_riv": em["4_riv"],
        "4_buy": em["4_buy"],
        "4_sup": em["4_sup"],
        "4_sub": em["4_sub"],
        "4": g4_val,
        "4n": em["4n"],
        "5": em["5"],
        "6": em["6"],
        "calamity": curr_q.get("calamity", ""),
        "calamity_note": curr_q.get("calamity_note", ""),
        "note": curr_q.get("note", ""),
        "evidence": curr_q.get("evidence", ""),
    }

    item = {
        "id": cid,
        "ticker": ident["ticker"],
        "universe": u,
        "qualitative": qual_dict,
    }

    # Run validation via screener's validate_company_evaluation
    sanitized_qual, warnings, errors = validate_company_evaluation(item)
    if warnings:
        all_warnings.extend(warnings)
    if errors:
        all_errors.extend(errors)

    evaluated_list.append(item)

print(f"Total evaluated items: {len(evaluated_list)}")
print(f"Validation warnings: {len(all_warnings)}")
for w in all_warnings:
    print("  [WARN]", w)
print(f"Validation errors: {len(all_errors)}")
for e in all_errors:
    print("  [ERROR]", e)

if all_errors:
    print("Aborting write due to validation errors!")
    sys.exit(1)

# Write to evaluations/completed/batch_05_evaluated.json
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(evaluated_list, f, indent=2)

print(f"Successfully wrote evaluated array to {OUT_FILE}")
