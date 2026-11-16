import json
import sys
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation, load_universe_inputs
from eval_definitions import EVALUATIONS

with open(ROOT / "evaluations/batches/batch_08.json") as f:
    batch = json.load(f)

# Load universe inputs for comparison/validation
universes = {"us": {}, "eu": {}, "ca": {}}
for u in universes:
    rows, _ = load_universe_inputs(u)
    universes[u] = {r["id"]: r for r in rows}

evaluated_list = []

for comp in batch["companies"]:
    cid = comp["identity"]["id"]
    u = comp["identity"]["universe"]
    
    qual = EVALUATIONS[cid]
    payload = {
        "id": cid,
        "ticker": comp["identity"]["ticker"],
        "universe": u,
        "qualitative": qual
    }
    
    existing_row = universes[u].get(cid)
    sanitized, warnings, errors = validate_company_evaluation(payload, existing_row=existing_row)
    assert not errors, f"Unexpected error for {cid}: {errors}"
    
    evaluated_list.append({
        "id": cid,
        "universe": u,
        "qualitative": sanitized
    })

out_path = ROOT / "evaluations/completed/batch_08_evaluated.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(evaluated_list, f, indent=2)

print(f"Successfully wrote {len(evaluated_list)} evaluated companies to {out_path} ({out_path.stat().st_size} bytes)")
