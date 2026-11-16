"""Generate evaluated batch 10 and validate against framework invariants."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.apply_evaluation import validate_and_waterfall
from screener.gates import compute_final_cap_from_scores, compute_initial_cap_from_scores

BATCH_FILE = ROOT / "evaluations" / "batches" / "batch_10.json"
OUTPUT_FILE = ROOT / "evaluations" / "completed" / "batch_10_evaluated.json"

with open(BATCH_FILE, "r", encoding="utf-8") as f:
    batch_raw = json.load(f)

companies_in = batch_raw["companies"]

# Dictionary of evaluations for all 65 companies
EVALUATIONS = {
    # 1. EMR
    "EMR": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): terminal substitution threat from energy transition decarbonization of hydrocarbon processing and open-architecture software-defined automation (4_sub=2), compounded by process automation rivalry with ABB and Siemens (4_riv=1).",
        "5": "", "6": "",
    },
    # 2. ETN
    "ETN": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe terminal substitution threat in legacy Vehicle segment from commercial fleet electrification (4_sub=2) alongside electrical equipment capacity rivalry (4_riv=1) and hyperscaler buyer bargaining power (4_buy=1).",
        "5": "", "6": "",
    },
    # 3. ROK
    "ROK": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): terminal substitution threat from virtualized PLCs and open software-defined automation (OPAF) decoupling software from proprietary Allen-Bradley hardware (4_sub=2), coupled with global rivalry from Siemens (4_riv=1) and OEM buyer leverage (4_buy=1).",
        "5": "", "6": "",
    },
    # 4. VRT
    "VRT": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 2, "4_sup": 0, "4_sub": 1,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe hyperscaler buyer bargaining power and Open Compute Project (OCP) design standardization stripping hardware pricing power (4_buy=2), alongside full-suite electrical rivalry from Schneider and Eaton (4_riv=1) and rapid liquid-cooling technology resets (4_sub=1).",
        "5": "", "6": "",
    },
    # 5. ABBN.CH
    "ABBN.CH": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for electrification and industrial automation rivalry with Siemens and Schneider (4_riv=1) and technological evolution in robotics and digital motion controls (4_sub=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 6. HUBN.CH
    "HUBN.CH": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 7. LAGR B.SE
    "LAGR B.SE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -5Y for M&A competition for high-return Nordic private assets (4_riv=1) and technological shifts across decentralized niche product lines (4_sub=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 8. LR.FR
    "LR.FR": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for commercial and data center electrical equipment rivalry with Schneider Electric (4_riv=1) and evolving smart building digital protocols (4_sub=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 9. NEX.FR
    "NEX.FR": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 10. NKT.DK
    "NKT.DK": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 11. PRY.IT
    "PRY.IT": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for transmission cable rivalry with Nexans and NKT (4_riv=1), sovereign grid operator buyer concentration (4_buy=1), and specialized raw material supplier volatility (4_sup=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
    # 12. SU.FR
    "SU.FR": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for data center and industrial electrification rivalry with ABB and Siemens (4_riv=1) and open automation architecture evolution (4_sub=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 13. ROL
    "ROL": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for pest control rivalry with Rentokil/Terminix (4_riv=1) and demographic technician labor scarcity and wage inflation (4_sup=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 14. RSG
    "RSG": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for rational duopoly rivalry with Waste Management (4_riv=1) and driver labor and equipment cost pressures (4_sup=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    # 15. VLTO
    "VLTO": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for water analytics rivalry with Xylem and Danaher (4_riv=1) and ongoing evolution in digital water sensing protocols (4_sub=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    # 16. WCN.CA
    "WCN.CA": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for commercial collection rivalry in secondary markets (4_riv=1) and driver labor wage inflation (4_sup=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    # 17. RTO.GB (Calamity Pass)
    "RTO.GB": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for North American pest control rivalry with Rollins (4_riv=1), customer contract pushback during branch integration (4_buy=1), and technician labor scarcity and termite warranty inflation (4_sup=1) yielding Final CAP 15Y.",
        "5": 0, "6": "N",
    },
    # 18. GEV
    "GEV": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): terminal substitution threat from 15-30 year grid decarbonization phasing down fossil gas turbines (4_sub=2) alongside wind turbine pricing rivalry (4_riv=1) and consolidated utility buyer power (4_buy=1).",
        "5": "", "6": "",
    },
    # 19. GNRC
    "GNRC": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 20. ENR.DE
    "ENR.DE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe execution and substitution risks across long-cycle wind turbine and grid infrastructure contracts (4_sub=2), compounded by global turbine rivalry (4_riv=1) and utility buyer bargaining power (4_buy=1).",
        "5": "", "6": "",
    },
    # 21. NDX1.DE
    "NDX1.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 22. VWS.DK
    "VWS.DK": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 23. FER.ES
    "FER.ES": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 24. GET.FR
    "GET.FR": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 25. ADP
    "ADP": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for HCM software rivalry with Workday and Paychex (4_riv=1) and AI-driven automation of routine HR workflows (4_sub=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    # 26. PAYX
    "PAYX": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -5Y for SMB payroll rivalry with ADP, Gusto, and Rippling (4_riv=1) and cloud/AI self-service payroll automation (4_sub=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
    # 27. ADEN.CH
    "ADEN.CH": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 28. RAND.NL
    "RAND.NL": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 29. DD
    "DD": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 30. HON
    "HON": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): terminal substitution threat from energy transition phasing down fossil fuel refining and UOP petrochemical licensing (4_sub=2), compounded by process automation rivalry with Siemens and Emerson (4_riv=1) and industrial customer consolidation (4_buy=1).",
        "5": "", "6": "",
    },
    # 31. MMM
    "MMM": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): existential regulatory and litigation prohibition of fluorochemicals forcing complete PFAS phase-out (4_sub=2), alongside materials science rivalry (4_riv=1) and OEM buyer price scrutiny (4_buy=1).",
        "5": "", "6": "",
    },
    # 32. LIFCO B.SE
    "LIFCO B.SE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -5Y for private asset acquisition competition in Northern Europe (4_riv=1) and technology shifts across niche industrial and dental product lines (4_sub=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 33. SIE.DE
    "SIE.DE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -5Y for industrial automation and software rivalry with Schneider and Rockwell (4_riv=1) and virtualized PLC/open automation standards evolution (4_sub=1) yielding Final CAP 15Y.",
        "5": 1, "6": "N",
    },
    # 34. SMIN.GB
    "SMIN.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 35. DOV
    "DOV": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 36. FTV
    "FTV": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe technological substitution from AI-driven automated testing and cloud-integrated sensor platforms (4_sub=2), compounded by instrument rivalry (4_riv=1) and industrial customer capex cyclicality (4_buy=1).",
        "5": "", "6": "",
    },
    # 37. GWW
    "GWW": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for digital B2B distribution rivalry with Amazon Business and Fastenal (4_riv=1) and e-commerce price transparency (4_sub=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 38. HUBB
    "HUBB": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for utility component rivalry with Eaton and ABB (4_riv=1) and regulated utility procurement consolidation (4_buy=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
    # 39. IEX
    "IEX": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe return dilution and cost of capital headwinds on serial M&A roll-up model across fragmented operating units (4_sub=2), alongside fluidics rivalry (4_riv=1) and industrial OEM procurement pressure (4_buy=1).",
        "5": "", "6": "",
    },
    # 40. IR
    "IR": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 41. ITW
    "ITW": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for industrial equipment rivalry across diversified markets (4_riv=1), automotive OEM buyer bargaining power (4_buy=1), and raw material input cost volatility (4_sup=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 42. NDSN
    "NDSN": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -5Y for fluid dispensing rivalry with Graco (4_riv=1) and advanced electronics packaging technology transitions (4_sub=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
    # 43. OTIS
    "OTIS": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for global elevator oligopoly rivalry with Schindler and KONE (4_riv=1) and technician labor scarcity and wage inflation (4_sup=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    # 44. PH
    "PH": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for motion control rivalry with Bosch Rexroth (4_riv=1) and gradual electrification of mobile hydraulic systems (4_sub=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 45. PNR
    "PNR": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 46. SNA
    "SNA": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for mobile tool truck rivalry with Mac and Matco (4_riv=1), technician tool capex sensitivity (4_buy=1), and EV powertrain transitions reducing mechanical repair intensity (4_sub=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 47. XYL
    "XYL": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 48. AALB.NL
    "AALB.NL": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 49. ACLN.CH
    "ACLN.CH": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -5Y for heavy turbocharger rivalry with MAN Energy Solutions (4_riv=1) and maritime alternative fuel transition architectures (4_sub=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 50. ALFA.SE
    "ALFA.SE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): cyclical shipbuilding and refinery capex exposure combined with low-cost Asian competitive encroachment in heat exchangers (4_sub=2), compounded by processing equipment rivalry (4_riv=1) and shipyard buyer leverage (4_buy=1).",
        "5": "", "6": "",
    },
    # 51. ANDR.AT
    "ANDR.AT": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 52. ATCO A.SE
    "ATCO A.SE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -5Y for compressor and vacuum rivalry with Ingersoll Rand and Pfeiffer Vacuum (4_riv=1) and semiconductor fab capex cycle exposure (4_sub=1) yielding Final CAP 20Y.",
        "5": 2, "6": "Y",
    },
    # 53. G1A.DE
    "G1A.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 54. GF.CH
    "GF.CH": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 55. HILS.GB
    "HILS.GB": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 56. IMI.GB
    "IMI.GB": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for 3 moderate forces: process automation valve rivalry with Emerson (4_riv=1), industrial OEM procurement price pressure (4_buy=1), and energy transition headwinds on fossil power generation applications (4_sub=1) yielding Final CAP 10Y.",
        "5": "", "6": "",
    },
    # 57. IP.IT
    "IP.IT": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 2, "4_sup": 0, "4_sub": 1,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): severe buyer bargaining power and volume cyclicality from consolidated agricultural and construction machinery OEMs (4_buy=2), alongside mobile hydraulics rivalry (4_riv=1) and machinery electrification (4_sub=1).",
        "5": "", "6": "",
    },
    # 58. KBX.DE
    "KBX.DE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for commercial vehicle braking rivalry with ZF (4_riv=1) and state rail / truck OEM procurement bargaining power (4_buy=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
    # 59. KCR.FI
    "KCR.FI": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 60. KGX.DE
    "KGX.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "", "5": "", "6": "",
    },
    # 61. KNEBV.FI
    "KNEBV.FI": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for elevator oligopoly rivalry with Otis and Schindler (4_riv=1) and demographic technician labor scarcity and wage inflation (4_sup=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 62. RAA.DE
    "RAA.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -10Y for commercial food equipment rivalry with Electrolux Professional and Ali Group (4_riv=1), restaurant chain capex sensitivity (4_buy=1), and specialized stainless steel and sensor input costs (4_sup=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    # 63. ROR.GB
    "ROR.GB": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for actuator rivalry with Emerson and Flowserve (4_riv=1), energy EPC contractor procurement pressure (4_buy=1), and 15-30 year energy transition headwinds phasing down oil and gas pipeline infrastructure (4_sub=1) yielding Final CAP 10Y.",
        "5": "", "6": "",
    },
    # 64. SAND.SE
    "SAND.SE": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for underground mining equipment rivalry with Epiroc (4_riv=1) and cyclical mining house capex bargaining power (4_buy=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
    # 65. SCHP.CH
    "SCHP.CH": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for elevator oligopoly rivalry with Otis and KONE (4_riv=1) and technician labor scarcity and wage inflation (4_sup=1) yielding Final CAP 15Y.",
        "5": 1, "6": "Y",
    },
}

# Verification & Build loop
out_companies = []
all_passed_checks = True

for c in companies_in:
    cid = c["identity"]["id"]
    u = c["identity"]["universe"]
    cq = c["current_qualitative"]

    if cid not in EVALUATIONS:
        print(f"Error: Missing evaluation for {cid}")
        all_passed_checks = False
        continue

    eval_spec = EVALUATIONS[cid]
    merged_q = dict(cq)

    # Update with new evaluated fields
    for k, v in eval_spec.items():
        merged_q[k] = v

    # If 3b == 'Y', verify and set 4 deterministically
    if merged_q.get("3b") == "Y":
        m_tuple = (int(merged_q["3_tb"]), int(merged_q["3_ia"]), int(merged_q["3_se"]), int(merged_q["3_rd"]))
        cap_init = compute_initial_cap_from_scores(m_tuple)
        f_tuple = (int(merged_q["4_ent"]), int(merged_q["4_riv"]), int(merged_q["4_buy"]), int(merged_q["4_sup"]), int(merged_q["4_sub"]))
        cap_final, h, fatal = compute_final_cap_from_scores(cap_init, f_tuple)
        merged_q["4"] = cap_final
    elif merged_q.get("3b") == "N":
        # Clear downstream
        for k in ["4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n", "5", "6"]:
            merged_q[k] = ""

    # Test through validate_and_waterfall
    test_payload = {"id": cid, "qualitative": merged_q}
    cleaned_q, _, warnings = validate_and_waterfall(test_payload)

    # Disallow warnings that indicate structural errors (warnings about legitimate normalizations are ok, but let's check)
    real_warnings = [w for w in warnings if not w.startswith("Waterfall: scrubbed")]
    if real_warnings:
        print(f"Warning for {cid}: {real_warnings}")

    # Build final qualitative dict strictly adhering to schema
    final_q = {
        "1": cleaned_q.get("1", ""),
        "2": cleaned_q.get("2", ""),
        "2r": cleaned_q.get("2r", ""),
        "3_tb": cleaned_q.get("3_tb", ""),
        "3_ia": cleaned_q.get("3_ia", ""),
        "3_se": cleaned_q.get("3_se", ""),
        "3_rd": cleaned_q.get("3_rd", ""),
        "3a": cleaned_q.get("3a", ""),
        "3b": cleaned_q.get("3b", ""),
        "3m": cleaned_q.get("3m", ""),
        "4_ent": cleaned_q.get("4_ent", ""),
        "4_riv": cleaned_q.get("4_riv", ""),
        "4_buy": cleaned_q.get("4_buy", ""),
        "4_sup": cleaned_q.get("4_sup", ""),
        "4_sub": cleaned_q.get("4_sub", ""),
        "4": cleaned_q.get("4", ""),
        "4n": cleaned_q.get("4n", ""),
        "5": cleaned_q.get("5", ""),
        "6": cleaned_q.get("6", ""),
        "calamity": cleaned_q.get("calamity", ""),
        "calamity_note": cleaned_q.get("calamity_note", ""),
        "note": cleaned_q.get("note", ""),
        "evidence": cleaned_q.get("evidence", ""),
    }

    out_companies.append({
        "id": cid,
        "universe": u,
        "qualitative": final_q
    })

print(f"Total evaluated companies: {len(out_companies)} / {len(companies_in)}")

# Write to output file
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(out_companies, f, indent=2)

print(f"Successfully generated {OUTPUT_FILE}")
