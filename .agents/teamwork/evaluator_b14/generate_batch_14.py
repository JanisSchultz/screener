#!/usr/bin/env python3
"""Build and validate batch 14 evaluated payload."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation

# Load batch 14 input dossier
with open(ROOT / "evaluations/batches/batch_14.json") as f:
    batch_raw = json.load(f)

companies_input = {c["identity"]["id"]: c for c in batch_raw["companies"]}

# Scored configurations for the 17 passing Gate 3 companies
pass_g3_configs = {
    "CRDA.GB": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe substitution risk and technological obsolescence in specialty lipid delivery and bio-based synthesis (4_sub=2) alongside customer procurement pushback from CPG conglomerates (4_buy=1), specialty chemical peer rivalry (4_riv=1), and Asian bio-fermentation entrants (4_ent=1).",
        "5": "", "6": "",
    },
    "DSFIR.NL": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership", "3b": "Y",
        "4_ent": 0, "4_riv": 2, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe commodity vitamin substitution from low-cost Chinese producers (4_sub=2) and intense competitive rivalry across animal nutrition and taste ingredients (4_riv=2) alongside CPG customer procurement pressure (4_buy=1).",
        "5": "", "6": "",
    },
    "EMSN.CH": {
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 2, "4_sup": 0, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe automotive OEM customer bargaining power amid European auto contraction (4_buy=2) and structural substitution threats from Chinese EV architectures and alternative polymers (4_sub=2) alongside Asian polymer entrant pressure (4_ent=1) and specialty chemical rivalry (4_riv=1).",
        "5": "", "6": "",
    },
    "FPE3.DE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for specialty lubricant rivalry (4_riv=1), industrial buyer procurement pushback (4_buy=1), base oil supplier price volatility (4_sup=1), and EV drivetrain fluid substitution (4_sub=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    "GIVN.CH": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 30Y reduced by -10Y for flavor/fragrance oligopoly rivalry (4_riv=1), mega-CPG buyer negotiation leverage (4_buy=1), and natural botanical/aroma feedstocks supplier volatility (4_sup=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    "NSIS B.DK": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 30Y reduced by -10Y for industrial biosolutions rivalry with IFF (4_riv=1), detergent and dairy customer buyer power (4_buy=1), and fermentation substrate energy/agricultural inputs (4_sup=1) yielding Final CAP 20Y.",
        "5": 1, "6": "Y",
    },
    "SIKA.CH": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for construction chemicals rivalry with Saint-Gobain/Mapei (4_riv=1), construction contractor buyer pressure (4_buy=1), petrochemical raw material inputs (4_sup=1), and alternative building materials substitution (4_sub=1) yielding Final CAP 15Y.",
        "5": 2, "6": "Y",
    },
    "SY1.DE": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 2, "4_buy": 1, "4_sup": 1, "4_sub": 1,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe competitive rivalry and antitrust investigations into flavor/fragrance pricing practices (4_riv=2) alongside CPG customer bargaining power (4_buy=1), raw material supply friction (4_sup=1), Asian aroma chemical entrants (4_ent=1), and formulation substitution (4_sub=1).",
        "5": "", "6": "",
    },
    "DLR": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 2, "4_sup": 2, "4_sub": 1,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe buyer power and self-building from hyperscale tech giants (4_buy=2) and critical power grid interconnection and electrical capacity bottlenecks (4_sup=2) alongside intense private equity development rivalry (4_riv=1), entrant capital (4_ent=1), and server efficiency substitution (4_sub=1).",
        "5": "", "6": "",
    },
    "WELL": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 2, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe caregiver labor shortages and wage inflation (4_sup=2) and substitution threats from home healthcare and aging-in-place technologies (4_sub=2) alongside private developer supply entrants (4_ent=1), local operator rivalry (4_riv=1), and resident price sensitivity (4_buy=1).",
        "5": "", "6": "",
    },
    "SAGA B.SE": {
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for light industrial market rivalry (4_riv=1) and SME tenant negotiation friction (4_buy=1) yielding Final CAP 15Y.",
        "5": 2, "6": "N",
    },
    "SGRO.GB": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for prime European logistics developer rivalry (4_riv=1) and large-scale 3PL tenant negotiations (4_buy=1) yielding Final CAP 20Y.",
        "5": 1, "6": "N",
    },
    "WDP.BE": {
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for Benelux logistics property rivalry (4_riv=1) and 3PL tenant bargaining power (4_buy=1) yielding Final CAP 15Y.",
        "5": 2, "6": "N",
    },
    "IRM": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 2, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Terminal substitution from enterprise paperless digitization (4_sub=2) and critical power grid bottlenecks in data center expansion (4_sup=2) alongside data center rivalry (4_riv=1) and corporate buyer volume attrition (4_buy=1).",
        "5": "", "6": "",
    },
    "UTG.GB": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 2, "4_sup": 1, "4_sub": 2,
        "4n": "Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT): Severe geopolitical and regulatory demand shocks from UK international student visa restrictions (4_buy=2) and substitution toward remote learning / living at home amid student affordability crises (4_sub=2) alongside regional PBSA entrant capacity (4_ent=1), student housing rivalry (4_riv=1), and construction cost inflation (4_sup=1).",
        "5": "", "6": "",
    },
    "CSGP": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for residential portal rivalry against Zillow (4_riv=1), commercial broker pushback on subscription pricing (4_buy=1), and digital platform technology clock speed (4_sub=1) yielding Final CAP 15Y.",
        "5": 0, "6": "",
    },
    "AMT": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for wireless tower rivalry with Crown Castle/SBA (4_riv=1), wireless carrier tenant concentration and amendment pushback (4_buy=1), and alternative connectivity substitution from small cells and direct-to-cell satellite constellations (4_sub=1) yielding Final CAP 15Y.",
        "5": 1, "6": "N",
    },
}

# Gate 3 Moat scores for the 48 Gate 3 failing companies
fail_g3_configs = {
    # Specialty chemicals failing Gate 3b
    "AKZA.NL": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 1, "3a": "R&D & innovation leadership"},
    "EVK.DE": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1, "3a": "Toll booth & switching costs"},
    "JMAT.GB": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1, "3a": "Toll booth & switching costs"},
    "SYENS.BE": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1, "3a": "Toll booth & switching costs"},
    "UMI.BE": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1, "3a": "Toll booth & switching costs"},

    # Steel failing Gate 3b
    "STLD": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "ACX.ES": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "MT.FR": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "SSAB B.SE": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "TKA.DE": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "VOE.AT": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Data Center REITs failing Gate 3b
    "EQIX": {"3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Diversified REITs failing Gate 3b
    "BLND.GB": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "COV.FR": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "LAND.GB": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "MRL.ES": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Health Care REITs failing Gate 3b
    "DOC": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs"},
    "VTR": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs"},
    "AED.BE": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs"},
    "PHP.GB": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs"},

    # Industrial REITs failing Gate 3b
    "PLD": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "BBOX.GB": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "LMP.GB": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Multi-Family Residential REITs failing Gate 3b
    "CPT": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "ESS": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "MAA": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "UDR": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "VMRK": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Office REITs failing Gate 3b
    "ARE": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "BXP": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "DLN.GB": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "GFC.FR": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Real Estate Operating Companies failing Gate 3b
    "ALLN.CH": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "BALD B.SE": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "CAST.SE": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "LEG.DE": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "MOBN.CH": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "PSPN.CH": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "SPSN.CH": {"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"},
    "TEG.DE": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "VNA.DE": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Real Estate Services failing Gate 3b
    "CBRE": {"3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs"},

    # Retail REITs failing Gate 3b
    "FRT": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "KIM": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "O": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "REG": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
    "SPG": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},

    # Single-Family Residential REITs failing Gate 3b
    "INVH": {"3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"},
}

evaluated_list = []
total_errors = 0
total_warnings = 0

for cid, comp in companies_input.items():
    ident = comp["identity"]
    cur_q = comp["current_qualitative"]
    universe = ident["universe"]

    qual = {
        "1": cur_q.get("1", "Y"),
        "2": cur_q.get("2", "Y"),
        "2r": cur_q.get("2r", ""),
        "3m": cur_q.get("3m", ""),
        "calamity": "",
        "calamity_note": "",
        "note": cur_q.get("note", ""),
        "evidence": cur_q.get("evidence", ""),
    }

    if cid in pass_g3_configs:
        cfg = pass_g3_configs[cid]
        qual["3_tb"] = cfg["3_tb"]
        qual["3_ia"] = cfg["3_ia"]
        qual["3_se"] = cfg["3_se"]
        qual["3_rd"] = cfg["3_rd"]
        qual["3a"] = cfg["3a"]
        qual["3b"] = cfg["3b"]
        qual["4_ent"] = cfg["4_ent"]
        qual["4_riv"] = cfg["4_riv"]
        qual["4_buy"] = cfg["4_buy"]
        qual["4_sup"] = cfg["4_sup"]
        qual["4_sub"] = cfg["4_sub"]
        qual["4n"] = cfg["4n"]
        qual["5"] = cfg["5"]
        qual["6"] = cfg["6"]
    elif cid in fail_g3_configs:
        cfg = fail_g3_configs[cid]
        qual["3_tb"] = cfg["3_tb"]
        qual["3_ia"] = cfg["3_ia"]
        qual["3_se"] = cfg["3_se"]
        qual["3_rd"] = cfg["3_rd"]
        qual["3a"] = cfg["3a"]
        qual["3b"] = "N"
        qual["4_ent"] = ""
        qual["4_riv"] = ""
        qual["4_buy"] = ""
        qual["4_sup"] = ""
        qual["4_sub"] = ""
        qual["4"] = ""
        qual["4n"] = ""
        qual["5"] = ""
        qual["6"] = ""
    else:
        print(f"ERROR: {cid} not configured!")
        sys.exit(1)

    payload = {
        "id": cid,
        "ticker": ident["ticker"],
        "universe": universe,
        "qualitative": qual,
    }

    sanitized_qual, warnings, errors = validate_company_evaluation(payload)
    if errors:
        print(f"Validation ERROR on {cid}: {errors}")
        total_errors += len(errors)
    if warnings:
        total_warnings += len(warnings)

    item = {
        "id": cid,
        "universe": universe,
        "qualitative": sanitized_qual,
    }
    evaluated_list.append(item)

print(f"Processed {len(evaluated_list)} companies.")
print(f"Total validation errors: {total_errors}, total warnings: {total_warnings}")

if total_errors == 0:
    out_path = ROOT / "evaluations/completed/batch_14_evaluated.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(evaluated_list, f, indent=2, ensure_ascii=False)
    print(f"Wrote validated output to {out_path}")
else:
    print("Aborting write due to errors.")
    sys.exit(1)
