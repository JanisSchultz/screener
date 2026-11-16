"""Evaluation generator and validator for Batch 13.
Produces /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/evaluations/completed/batch_13_evaluated.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

BATCH_IN_PATH = ROOT / "evaluations" / "batches" / "batch_13.json"
BATCH_OUT_PATH = ROOT / "evaluations" / "completed" / "batch_13_evaluated.json"

def main():
    with open(BATCH_IN_PATH, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    companies = batch_data["companies"]
    print(f"Loaded {len(companies)} companies from batch 13.")

    # Explicit qualitative profile mapping for batch 13 companies
    # key: id -> dict of overrides/sub-scores
    scores_map = {
        # 1. NOD.NO (Semiconductors, fast)
        "NOD.NO": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 15Y reduced by -10Y for Chinese fabless entrant pressure (4_ent=1), price rivalry (4_riv=1), OEM buyer power (4_buy=1), and fast semiconductor clock speed (4_sub=1).",
        },
        # 2. STMMI.FR (Semiconductors, fast) - fails 3b
        "STMMI.FR": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 3. CRWD (Systems Software, fast) - fails 3b
        "CRWD": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 4. FTNT (Systems Software, fast) - PASS
        "FTNT": {
            "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 1, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 25Y reduced by -10Y for cybersecurity peer rivalry (4_riv=1), enterprise procurement consolidation (4_buy=1), and cloud SASE clock speed (4_sub=1).",
            "5": 2, "6": "Y",
        },
        # 5. NOW (Systems Software, fast) - fails Gate 4
        "NOW": {
            "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 1, "3b": "Y",
            "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 1,
            "4n": "Initial CAP 25Y reduced by -15Y for AI-native agent entrants (4_ent=1), enterprise software rivalry (4_riv=1), corporate seat-compression buyer power (4_buy=1), GPU compute supplier costs (4_sup=1), and agentic software substitution & clock speed (4_sub=1).",
        },
        # 6. PANW (Systems Software, fast) - fails Gate 4
        "PANW": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 15Y reduced by -10Y for venture-backed security entrants (4_ent=1), platform rivalry (4_riv=1), buyer discount pressure (4_buy=1), and rapid cybersecurity architectural clock speed (4_sub=1).",
        },
        # 7. TWLO (Systems Software, fast) - fails 3b
        "TWLO": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 8-11. Tech Distributors (fast) - fail 3b
        "CDW": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "BC8.DE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "CCC.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "SCT.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 12. AAPL (Hardware, fast) - PASS
        "AAPL": {
            "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 1, "4_sub": 1,
            "4n": "Initial CAP 20Y reduced by -5Y for TSMC foundry supplier concentration (4_sup=1) and consumer device clock speed (4_sub=1).",
            "5": 2, "6": "Y",
        },
        # 13-20. Hardware, Storage & Peripherals (fast) - fail 3b
        "DELL": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "HPE": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "HPQ": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "NTAP": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "P": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "SNDK": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "STX": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 1, "3b": "N",
        },
        "WDC": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 1, "3b": "N",
        },
        # 21-22. Aluminum / Commodity Chemicals - fail 3b
        "NHY.NO": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "DOW": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 23. CRH (Construction Materials) - PASS
        "CRH": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 20Y reduced by -5Y for regional bidding rivalry (4_riv=1) and public/commercial buyer bargaining (4_buy=1).",
            "5": 2, "6": "Y",
        },
        # 24. MLM (Construction Materials) - fails Gate 6
        "MLM": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 20Y preserved with zero force haircuts due to natural local quarry monopolies and structural infrastructure demand.",
            "5": 1, "6": "N",
        },
        # 25. VMC (Construction Materials) - PASS
        "VMC": {
            "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 20Y preserved with zero force haircuts due to local quarry haul-radius insulation and structural aggregates demand.",
            "5": 1, "6": "Y",
        },
        # 26-28. European Construction Materials - fail 3b
        "BZU.IT": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "HEI.DE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "HOLN.CH": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 29-31. Copper / Smelting - fail 3b
        "FCX": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "FM.CA": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "NDA.DE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 32. BASF - Diversified Chemicals - fails 3b
        "BAS.DE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 33-36. Diversified Metals & Mining - fail 3b
        "TECK.B.CA": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "AAL.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "BOL.SE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "RIO.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 37-41. Fertilizers & Ag Chemicals - fail 3b
        "CF": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "MOS": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "NTR.CA": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "SDF.DE": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "YAR.NO": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 42-43. Forest Products - fail 3b
        "HOLM B.SE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "SCA B.SE": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 44. APD (Industrial Gases) - CALAMITY PASS
        "APD": {
            "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
            "calamity": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
            "4n": "Initial CAP 25Y reduced by -10Y for oligopoly rivalry (4_riv=1), industrial buyer power (4_buy=1), and hydrogen transition project risk (4_sub=1).",
            "5": 0, "6": "N",
        },
        # 45. LIN (Industrial Gases) - PASS
        "LIN": {
            "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 30Y reduced by -10Y for oligopolistic industrial gas rivalry (4_riv=1), large buyer bargaining power (4_buy=1), and power/energy supplier exposure (4_sup=1).",
            "5": 2, "6": "Y",
        },
        # 46. AI.FR (Industrial Gases) - PASS
        "AI.FR": {
            "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 30Y reduced by -10Y for gas triopoly rivalry (4_riv=1), industrial buyer bargaining power (4_buy=1), and power/energy supplier exposure (4_sup=1).",
            "5": 2, "6": "Y",
        },
        # 47. BALL (Containers) - fails 3b
        "BALL": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 48. CCL.B.CA (Containers/Labels) - PASS
        "CCL.B.CA": {
            "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -10Y for packaging converter rivalry (4_riv=1), multinational CPG buyer leverage (4_buy=1), and polymer resin supplier exposure (4_sup=1).",
            "5": 2, "6": "Y",
        },
        # 49. AMCR (Packaging) - fails 3b
        "AMCR": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 50. AVY (Packaging) - fails Gate 4
        "AVY": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
            "4n": "Initial CAP 15Y reduced by -10Y for private label entrant risk (4_ent=1), packaging converter rivalry (4_riv=1), and retail customer bargaining power (4_buy=1).",
        },
        # 51-58. Paper & Packaging Products - fail 3b
        "IP": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "PKG": {
            "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "SW": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "HUH1V.FI": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "MNDI.GB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "SIGN.CH": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "STERV.FI": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "UPM.FI": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 59. ALB (Specialty Chemicals) - fails 3b
        "ALB": {
            "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 60. ECL (Specialty Chemicals) - PASS
        "ECL": {
            "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 25Y reduced by -5Y for specialty chemical rivalry (4_riv=1) and petrochemical raw material supplier leverage (4_sup=1).",
            "5": 1, "6": "Y",
        },
        # 61. IFF (Specialty Chemicals) - fails Gate 4
        "IFF": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
            "4n": "Initial CAP 15Y reduced by -10Y for flavor/fragrance rivalry (4_riv=1), CPG buyer leverage (4_buy=1), and botanical raw material supplier pressure (4_sup=1).",
        },
        # 62-63. Specialty Chemicals - fail 3b
        "LYB": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        "PPG": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
        # 64. SHW (Specialty Chemicals) - PASS
        "SHW": {
            "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0, "3b": "Y",
            "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
            "4n": "Initial CAP 30Y reduced by -10Y for coatings rivalry (4_riv=1), TiO2/petrochemical supplier input cycles (4_sup=1), and environmental coating regulation substitution (4_sub=1).",
            "5": 2, "6": "Y",
        },
        # 65. AKE.FR (Specialty Chemicals) - fails 3b
        "AKE.FR": {
            "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "N",
        },
    }

    evaluated_companies = []
    total_warnings = 0
    total_errors = 0

    for c in companies:
        cid = c["identity"]["id"]
        uni = c["identity"]["universe"]
        cur_q = c["current_qualitative"]

        if cid not in scores_map:
            print(f"ERROR: Missing scores mapping for {cid}")
            sys.exit(1)

        ovr = scores_map[cid]

        # Assemble full qualitative dictionary
        # Preserve existing base fields (1, 2, 2r, 3m, note, evidence, calamity_note)
        # Apply sub-scores and ensure correct waterfall clearing
        q_dict = {
            "1": cur_q.get("1", "Y"),
            "2": cur_q.get("2", "Y"),
            "2r": cur_q.get("2r", ""),
            "3_tb": ovr["3_tb"],
            "3_ia": ovr["3_ia"],
            "3_se": ovr["3_se"],
            "3_rd": ovr["3_rd"],
            "3b": ovr["3b"],
            "3m": cur_q.get("3m", ""),
            "4_ent": ovr.get("4_ent", ""),
            "4_riv": ovr.get("4_riv", ""),
            "4_buy": ovr.get("4_buy", ""),
            "4_sup": ovr.get("4_sup", ""),
            "4_sub": ovr.get("4_sub", ""),
            "4": "",  # will be deterministically populated by validate_company_evaluation
            "4n": ovr.get("4n", ""),
            "5": ovr.get("5", ""),
            "6": ovr.get("6", ""),
            "calamity": ovr.get("calamity", cur_q.get("calamity", "")),
            "calamity_note": cur_q.get("calamity_note", ""),
            "note": cur_q.get("note", ""),
            "evidence": cur_q.get("evidence", ""),
        }

        # Run validation and waterfall clearing
        payload = {
            "id": cid,
            "universe": uni,
            "qualitative": q_dict,
        }
        sanitized_qual, warnings, errors = validate_company_evaluation(payload)

        if errors:
            print(f"Validation ERRORS for {cid}: {errors}")
            total_errors += len(errors)
        if warnings:
            # print(f"Validation warnings for {cid}: {warnings}")
            total_warnings += len(warnings)

        evaluated_companies.append({
            "id": cid,
            "universe": uni,
            "qualitative": sanitized_qual,
        })

    print(f"\nCompleted evaluation of {len(evaluated_companies)} companies.")
    print(f"Total validation errors: {total_errors}")
    print(f"Total validation warnings: {total_warnings}")

    if total_errors > 0:
        print("Aborting write due to validation errors.")
        sys.exit(1)

    # Write output JSON file
    BATCH_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BATCH_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(evaluated_companies, f, indent=2)

    print(f"Successfully wrote evaluated batch to: {BATCH_OUT_PATH}")

if __name__ == "__main__":
    main()
