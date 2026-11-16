"""Complete qualitative evaluations generator for Batch 04 (65 companies).
Strictly adheres to QUALITATIVE_EVALUATION_SPEC.md and COMPANY_EVALUATION_SPEC.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation, load_universe_inputs
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

BATCH_INPUT = ROOT / "evaluations" / "batches" / "batch_04.json"
TARGET_OUTPUT = ROOT / "evaluations" / "completed" / "batch_04_evaluated.json"

# Detailed qualitative profiles:
# For each company:
# cid: {
#   "moat": (3_tb, 3_ia, 3_se, 3_rd),
#   "3b": "Y" or "N",
#   "3a": preferred archetype name if tie,
#   "forces": (4_ent, 4_riv, 4_buy, 4_sup, 4_sub) if 3b=="Y" else None,
#   "4n": str if 3b=="Y" else "",
#   "5": int or "" (if cap>=15: 1 or 2, else ""),
#   "6": "Y", "N", or "" (if cap>=15: "Y" or "N", else "")
# }

COMPANY_PROFILES = {
    # 1. Energy
    "VPK.NL": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for port hub terminal rivalry (4_riv=1), petrochemical customer bargaining power (4_buy=1), and secular energy transition substitution (4_sub=1); irreplaceable waterfront concessions insulate against new entrants.",
        "5": 1, "6": "Y",
    },
    # 2. Asset Management & Custody Banks (Failing G3)
    "AMP": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    "ARES": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 4. BAM.CA (Quality Pass)
    "BAM.CA": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for institutional fundraising rivalry (4_riv=1), sovereign wealth LP fee pressure (4_buy=1), and higher risk-free rate substitution (4_sub=1); sticky closed-end fund lockups insulate franchise.",
        "5": 2, "6": "Y",
    },
    # 5. BEN (Failing G3)
    "BEN": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 6. BLK (Quality Pass)
    "BLK": {
        "moat": (2, 1, 2, 0), "3b": "Y", "3a": "Scale economies shared",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for Vanguard index rivalry (4_riv=1), institutional index fee compression (4_buy=1), and direct indexing substitution (4_sub=1); iShares scale shared and Aladdin OS provide structural insulation.",
        "5": 1, "6": "Y",
    },
    # 7. BNY (Custody Bank, G6=N)
    "BNY": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for custody triopoly rivalry (4_riv=1), institutional buyer fee compression (4_buy=1), and digital ledger settlement substitution (4_sub=1); entrenched operational plumbing insulates against new entrants.",
        "5": 1, "6": "N",
    },
    # 8. BX (Quality Pass)
    "BX": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for alternative asset rivalry (4_riv=1), institutional LP fee negotiation (4_buy=1), and retail wealth product liquidity substitution (4_sub=1); locked-up fund structures insulate capital base.",
        "5": 1, "6": "Y",
    },
    # 9. IVZ (Failing G3)
    "IVZ": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 10. NTRS (Custody Bank, G6=N)
    "NTRS": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for wealth servicing rivalry (4_riv=1), client fee negotiation (4_buy=1), and technology automation substitution (4_sub=1); fiduciary trust lock-in insulates client assets.",
        "5": 1, "6": "N",
    },
    # 11. STT (Custody Bank, G6=N)
    "STT": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for custody rivalry (4_riv=1), institutional buyer fee compression (4_buy=1), and middle-office automation substitution (4_sub=1); entrenched custody workflows insulate franchise.",
        "5": 1, "6": "N",
    },
    # 12. TROW (Failing G3)
    "TROW": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 13. ABDN.GB (Failing G3)
    "ABDN.GB": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 14. AMUN.FR (Failing G3)
    "AMUN.FR": {
        "moat": (1, 0, 1, 0), "3b": "N", "3a": "Scale economies shared",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 15. AZM.IT (Failing G3)
    "AZM.IT": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 16. BAER.CH (Failing G3)
    "BAER.CH": {
        "moat": (1, 1, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 17. BGN.IT (Failing G3)
    "BGN.IT": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 18. BMED.IT (Failing G3)
    "BMED.IT": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 19. BPT.GB (Failing G3)
    "BPT.GB": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 20. CVC.NL (Quality Pass)
    "CVC.NL": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for European private equity rivalry (4_riv=1), institutional LP fee pressure (4_buy=1), and macro fundraising cycle substitution (4_sub=1); long-term fund lockups insulate capital base.",
        "5": 1, "6": "Y",
    },
    # 21. EMG.GB (Failing G3)
    "EMG.GB": {
        "moat": (1, 0, 0, 1), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 22. EQT.SE (Quality Pass)
    "EQT.SE": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for private capital rivalry (4_riv=1), institutional LP fee negotiation (4_buy=1), and PE exit multiple substitution (4_sub=1); long-duration fund commitments insulate fee base.",
        "5": 1, "6": "Y",
    },
    # 23. ICG.GB (Failing G3)
    "ICG.GB": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 24. MNG.GB (Failing G3)
    "MNG.GB": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 25. PGHN.CH (Quality Pass)
    "PGHN.CH": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for wealth management channel rivalry (4_riv=1), evergreen fund fee pressure (4_buy=1), and semi-liquid liquidity substitution (4_sub=1); customized client mandates insulate capital.",
        "5": 1, "6": "Y",
    },
    # 26. QLT.GB (Failing G3)
    "QLT.GB": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 27. STJ.GB (Failing G3)
    "STJ.GB": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 28. VONN.CH (Failing G3)
    "VONN.CH": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 29. VZN.CH (Quality Pass)
    "VZN.CH": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for Swiss banking retirement advisory rivalry (4_riv=1), mass affluent fee consciousness (4_buy=1), and digital wealth substitution (4_sub=1); integrated platform lock-in insulates client assets.",
        "5": 1, "6": "Y",
    },
    # 30. AXP (Closed-Loop Network, G6=N)
    "AXP": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for premium card reward rivalry (4_riv=1), merchant interchange regulation pushback (4_buy=1), and alternative payment substitution (4_sub=1); closed-loop merchant/cardholder network insulates franchise.",
        "5": 2, "6": "N",
    },
    # 31. COF (Failing G3 - None)
    "COF": {
        "moat": (0, 0, 0, 0), "3b": "N", "3a": "None",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 32. CMBN.CH (Failing G3)
    "CMBN.CH": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 33. BAC (Diversified Bank, G6=N)
    "BAC": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for money-center banking rivalry (4_riv=1), deposit yield competition (4_buy=1), and fintech payment substitution (4_sub=1); nationwide retail deposit footprint insulates funding.",
        "5": 1, "6": "N",
    },
    # 34. BMO.CA (Canadian Bank, G6=N)
    "BMO.CA": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for Big 6 domestic rivalry (4_riv=1), commercial borrower margin pressure (4_buy=1), and US Midwest banking cycle substitution (4_sub=1); Canadian statutory banking oligopoly insulates core franchise.",
        "5": 1, "6": "N",
    },
    # 35. BNS.CA (Canadian Bank, G6=N)
    "BNS.CA": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for domestic Big 6 rivalry (4_riv=1), international deposit cost pressure (4_buy=1), and emerging market restructuring substitution (4_sub=1); domestic Canadian oligopoly insulates earnings base.",
        "5": 1, "6": "N",
    },
    # 36. C (Failing G3)
    "C": {
        "moat": (1, 1, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 37. CM.CA (Canadian Bank, G6=N)
    "CM.CA": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for Canadian retail rivalry (4_riv=1), domestic mortgage renewal pressure (4_buy=1), and digital banking substitution (4_sub=1); Canadian statutory banking oligopoly insulates core franchise.",
        "5": 1, "6": "N",
    },
    # 38. JPM (Diversified Bank, G6=N)
    "JPM": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for universal banking rivalry (4_riv=1), corporate client rate sensitivity (4_buy=1), and private credit disintermediation substitution (4_sub=1); unmatched global scale and fortress deposit base insulate franchise.",
        "5": 2, "6": "N",
    },
    # 39. NA.CA (Canadian Bank, G6=N)
    "NA.CA": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for Quebec and national banking rivalry (4_riv=1), borrower margin pressure (4_buy=1), and retail digital substitution (4_sub=1); dominant Quebec fortress deposit base insulates funding.",
        "5": 2, "6": "N",
    },
    # 40. PNC (Super-Regional Bank, G6=N)
    "PNC": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for super-regional rivalry (4_riv=1), corporate borrower pricing leverage (4_buy=1), and digital banking substitution (4_sub=1); sticky middle-market treasury management insulates core relationships.",
        "5": 1, "6": "N",
    },
    # 41. RY.CA (Canadian Bank, G6=N)
    "RY.CA": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for Canadian oligopoly rivalry (4_riv=1), mortgage renewal borrower pressure (4_buy=1), and US business cycle substitution (4_sub=1); unassailable Canadian market leadership insulates franchise.",
        "5": 2, "6": "N",
    },
    # 42. TD.CA (Canadian Bank, G6=N)
    "TD.CA": {
        "moat": (2, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 30Y reduced by -10Y for domestic oligopoly rivalry (4_riv=1), borrower price consciousness (4_buy=1), and US regulatory asset cap constraints (4_sub=1); dominant Canadian retail footprint insulates core deposit funding.",
        "5": 1, "6": "N",
    },
    # 43. TFC (Failing G3)
    "TFC": {
        "moat": (1, 0, 0, 0), "3b": "N", "3a": "Toll booth & switching costs",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 44. USB (Regional Bank, G6=N)
    "USB": {
        "moat": (2, 1, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for regional banking rivalry (4_riv=1), deposit cost pressure (4_buy=1), and fintech merchant acquiring substitution (4_sub=1); differentiated payment processing ecosystem insulates fee revenue.",
        "5": 1, "6": "N",
    },
    # 45. WFC (Diversified Bank, G6=N)
    "WFC": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for domestic banking rivalry (4_riv=1), deposit beta pressure (4_buy=1), and non-bank lending substitution (4_sub=1); entrenched retail branch network insulates low-cost funding.",
        "5": 1, "6": "N",
    },
    # 46. A5G.IE (Failing G4, CAP=5)
    "A5G.IE": {
        "moat": (1, 0, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for domestic duopoly rivalry (4_riv=1), mortgage political price sensitivity (4_buy=1), and Revolut neo-bank payment substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 47. ABN.NL (Failing G4, CAP=5)
    "ABN.NL": {
        "moat": (1, 0, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for Dutch banking rivalry (4_riv=1), mortgage broker price transparency (4_buy=1), and non-bank mortgage substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 48. ACA.FR (Failing G3)
    "ACA.FR": {
        "moat": (0, 1, 0, 0), "3b": "N", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 49. BAMI.IT (Failing G3)
    "BAMI.IT": {
        "moat": (0, 1, 0, 0), "3b": "N", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 50. BCP.PT (Failing G4, CAP=5)
    "BCP.PT": {
        "moat": (0, 1, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for Iberian banking rivalry (4_riv=1), mortgage spread sensitivity (4_buy=1), and commoditized spread-lending substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 51. BG.AT (Failing G4, CAP=5)
    "BG.AT": {
        "moat": (1, 0, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for Austrian banking rivalry (4_riv=1), depositor yield sensitivity (4_buy=1), and interest-rate spread substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 52. BIRG.IE (Failing G4, CAP=5)
    "BIRG.IE": {
        "moat": (1, 0, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for Irish banking rivalry (4_riv=1), political mortgage pressure (4_buy=1), and fintech digital substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 53. BKT.ES (Failing G4, CAP=10)
    "BKT.ES": {
        "moat": (1, 1, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 20Y reduced by -10Y for Spanish banking rivalry (4_riv=1), commercial borrower rate pressure (4_buy=1), and ECB rate easing cycle substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 54. BMPS.IT (Failing G3 - None)
    "BMPS.IT": {
        "moat": (0, 0, 0, 0), "3b": "N", "3a": "None",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 55. BNP.FR (Failing G3)
    "BNP.FR": {
        "moat": (1, 1, 0, 0), "3b": "N", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 56. BPE.IT (Failing G3)
    "BPE.IT": {
        "moat": (0, 1, 0, 0), "3b": "N", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 57. CABK.ES (Fortress Bank, G6=N)
    "CABK.ES": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for Iberian banking rivalry (4_riv=1), domestic borrower rate consciousness (4_buy=1), and interest rate cycle normalization (4_sub=1); dominant Spanish retail branch and bancassurance network insulates deposit base.",
        "5": 1, "6": "N",
    },
    # 58. CBK.DE (Failing G3)
    "CBK.DE": {
        "moat": (0, 1, 0, 0), "3b": "N", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 59. DANSKE.DK (Failing G4, CAP=5)
    "DANSKE.DK": {
        "moat": (1, 0, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for Nordic banking rivalry (4_riv=1), digital borrower price transparency (4_buy=1), and fintech payment substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 60. DNB.NO (Fortress Bank, G6=N)
    "DNB.NO": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for Norwegian regional banking rivalry (4_riv=1), mortgage borrower rate sensitivity (4_buy=1), and digital payment substitution (4_sub=1); unassailable domestic deposit leadership insulates funding.",
        "5": 1, "6": "N",
    },
    # 61. EBS.AT (Failing G4, CAP=5)
    "EBS.AT": {
        "moat": (1, 0, 0, 0), "3b": "Y", "3a": "Toll booth & switching costs",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 15Y reduced by -10Y for CEE banking rivalry (4_riv=1), government windfall bank taxes (4_buy=1), and regional geopolitical/digital substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 62. INGA.NL (Failing G4, CAP=10)
    "INGA.NL": {
        "moat": (1, 1, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 20Y reduced by -10Y for European digital banking rivalry (4_riv=1), zero-cost deposit switching (4_buy=1), and neo-bank platform substitution (4_sub=1).",
        "5": "", "6": "",
    },
    # 63. INVP.GB (Failing G3)
    "INVP.GB": {
        "moat": (0, 1, 0, 0), "3b": "N", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": None, "4n": "", "5": "", "6": "",
    },
    # 64. ISP.IT (Fortress Bank, G6=N)
    "ISP.IT": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for Italian banking rivalry (4_riv=1), retail deposit BTP competition (4_buy=1), and rate cycle normalization (4_sub=1); dominant Italian retail branch and wealth distribution network insulates franchise.",
        "5": 2, "6": "N",
    },
    # 65. KBC.BE (Fortress Bank, G6=N)
    "KBC.BE": {
        "moat": (1, 2, 0, 0), "3b": "Y", "3a": "Irreplaceable infrastructure & intangibles",
        "forces": (0, 1, 1, 0, 1),
        "4n": "Initial CAP 25Y reduced by -10Y for Belgian market rivalry (4_riv=1), retail deposit pricing pressure (4_buy=1), and monetary easing substitution (4_sub=1); integrated bank-insurance cross-selling model insulates client relationships.",
        "5": 2, "6": "N",
    },
}

def generate():
    with open(BATCH_INPUT, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    # Load universe data for audit & validation
    universes = ("us", "eu", "ca")
    universe_indices = {}
    for u in universes:
        rows, _ = load_universe_inputs(u)
        for r in rows:
            universe_indices[r["id"]] = r

    evaluated_companies = []
    total_warnings = 0
    total_errors = 0

    for comp in batch_data["companies"]:
        cid = comp["identity"]["id"]
        u = comp["identity"]["universe"]
        cur_q = comp["current_qualitative"]

        if cid not in COMPANY_PROFILES:
            raise ValueError(f"Missing evaluation profile for {cid}")

        prof = COMPANY_PROFILES[cid]
        m_tuple = prof["moat"]
        cap_init = compute_initial_cap_from_scores(m_tuple)
        g3b = prof["3b"]
        primary_3a = prof["3a"]

        # Forces and Final CAP
        f_tuple = prof["forces"]
        if f_tuple is not None and cap_init > 0:
            cap_final, mod_h, fatal = compute_final_cap_from_scores(cap_init, f_tuple)
            g4_val = cap_final
            g4n_val = prof["4n"]
            g4_forces = {
                "4_ent": f_tuple[0],
                "4_riv": f_tuple[1],
                "4_buy": f_tuple[2],
                "4_sup": f_tuple[3],
                "4_sub": f_tuple[4],
            }
        else:
            g4_val = ""
            g4n_val = ""
            g4_forces = {
                "4_ent": "",
                "4_riv": "",
                "4_buy": "",
                "4_sup": "",
                "4_sub": "",
            }

        g5_val = prof["5"]
        g6_val = prof["6"]

        # Ensure note for BX begins with "Passes all 6 gates. " if quality pass
        note_text = cur_q.get("note", "")
        if cid == "BX" and not note_text.startswith("Passes all 6 gates. "):
            note_text = "Passes all 6 gates. " + note_text

        qual_payload = {
            "1": "Y",
            "2": "Y",
            "2r": "",
            "3_tb": m_tuple[0],
            "3_ia": m_tuple[1],
            "3_se": m_tuple[2],
            "3_rd": m_tuple[3],
            "3a": primary_3a,
            "3b": g3b,
            "3m": cur_q.get("3m", ""),
            "4_ent": g4_forces["4_ent"],
            "4_riv": g4_forces["4_riv"],
            "4_buy": g4_forces["4_buy"],
            "4_sup": g4_forces["4_sup"],
            "4_sub": g4_forces["4_sub"],
            "4": g4_val,
            "4n": g4n_val,
            "5": g5_val,
            "6": g6_val,
            "calamity": "",
            "calamity_note": "",
            "note": note_text,
            "evidence": cur_q.get("evidence", ""),
        }

        eval_item = {
            "id": cid,
            "universe": u,
            "qualitative": qual_payload,
        }

        # Validate using bulk_scorer validator
        existing_row = universe_indices.get(cid)
        sanitized_qual, warnings, errors = validate_company_evaluation(eval_item, existing_row=existing_row)

        if errors:
            print(f"ERROR on {cid}: {errors}")
            total_errors += len(errors)
        if warnings:
            # Report unexpected warnings
            print(f"WARNING on {cid}: {warnings}")
            total_warnings += len(warnings)

        # Update eval_item with sanitized_qual to ensure exact parity
        eval_item["qualitative"] = sanitized_qual
        evaluated_companies.append(eval_item)

    print(f"\nEvaluation summary:")
    print(f"Total evaluated: {len(evaluated_companies)}")
    print(f"Total warnings: {total_warnings}")
    print(f"Total errors: {total_errors}")

    if total_errors == 0:
        TARGET_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(TARGET_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(evaluated_companies, f, indent=2)
        print(f"Successfully wrote evaluated array to {TARGET_OUTPUT}")
    else:
        print("Aborting write due to errors.")
        sys.exit(1)

if __name__ == "__main__":
    generate()
