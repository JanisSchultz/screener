import json
import sys
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation, load_universe_inputs
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
from eval_definitions import EVALUATIONS

with open(ROOT / "evaluations/batches/batch_08.json") as f:
    batch = json.load(f)

companies = batch["companies"]
assert len(companies) == 65, f"Expected 65 companies, got {len(companies)}"
assert len(EVALUATIONS) == 65, f"Expected 65 evaluations, got {len(EVALUATIONS)}"

# Load universe inputs for comparison/validation
universes = {"us": {}, "eu": {}, "ca": {}}
for u in universes:
    rows, _ = load_universe_inputs(u)
    universes[u] = {r["id"]: r for r in rows}

evaluated_list = []
total_errors = 0
total_warnings = 0

for i, comp in enumerate(companies):
    cid = comp["identity"]["id"]
    u = comp["identity"]["universe"]
    assert cid in EVALUATIONS, f"Missing evaluation for {cid}"
    
    qual = EVALUATIONS[cid]
    payload = {
        "id": cid,
        "ticker": comp["identity"]["ticker"],
        "universe": u,
        "qualitative": qual
    }
    
    existing_row = universes[u].get(cid)
    sanitized, warnings, errors = validate_company_evaluation(payload, existing_row=existing_row)
    
    if errors:
        print(f"ERROR on {cid}: {errors}")
        total_errors += len(errors)
    if warnings:
        print(f"WARNING on {cid}: {warnings}")
        total_warnings += len(warnings)
        
    evaluated_list.append({
        "id": cid,
        "universe": u,
        "qualitative": sanitized
    })

print(f"\nVerification finished: {len(evaluated_list)} evaluated companies.")
print(f"Total Errors: {total_errors}")
print(f"Total Warnings: {total_warnings}")

# Check breakdown
quality_pass = [c for c in evaluated_list if c["qualitative"].get("6") == "Y"]
calamity_pass = [c for c in evaluated_list if c["qualitative"].get("calamity") == "Y"]
fail_g6 = [c for c in evaluated_list if c["qualitative"].get("6") == "N" and c["qualitative"].get("calamity") != "Y"]
fail_g5 = [c for c in evaluated_list if c["qualitative"].get("5") == 0 or c["qualitative"].get("5") == "0"]
fail_g4 = [c for c in evaluated_list if str(c["qualitative"].get("4", "")).isdigit() and int(c["qualitative"].get("4")) < 15]
fail_g3 = [c for c in evaluated_list if c["qualitative"].get("3b") == "N" or c["qualitative"].get("3a") == "None"]

print(f"\nBreakdown:")
print(f"  Quality Pass: {len(quality_pass)} -> {[c['id'] for c in quality_pass]}")
print(f"  Calamity Pass: {len(calamity_pass)} -> {[c['id'] for c in calamity_pass]}")
print(f"  Fail Gate 6: {len(fail_g6)} -> {[c['id'] for c in fail_g6]}")
print(f"  Fail Gate 5: {len(fail_g5)} -> {[c['id'] for c in fail_g5]}")
print(f"  Fail Gate 4: {len(fail_g4)} -> {[c['id'] for c in fail_g4]}")
print(f"  Fail Gate 3: {len(fail_g3)} -> {[c['id'] for c in fail_g3]}")
