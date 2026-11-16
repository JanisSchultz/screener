import json
import sys
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import ingest_evaluations
from eval_definitions import EVALUATIONS

with open(ROOT / "evaluations/batches/batch_08.json") as f:
    batch = json.load(f)

payloads = []
for comp in batch["companies"]:
    cid = comp["identity"]["id"]
    u = comp["identity"]["universe"]
    payloads.append({
        "id": cid,
        "ticker": comp["identity"]["ticker"],
        "universe": u,
        "qualitative": EVALUATIONS[cid]
    })

summary = ingest_evaluations(payloads, dry_run=True, sync_mirrors_after=False)
print("Ingestion Summary (DRY RUN):")
print(f"  Total evaluated: {summary['total_evaluated']}")
print(f"  Applied: {summary['applied']}")
print(f"  Rejected: {summary['rejected']}")
print(f"  Errors: {len(summary['errors'])}")
print(f"  Warnings: {len(summary['warnings'])}")
print(f"  Diffs count: {len(summary['diffs'])}")
if summary['errors']:
    print("Errors:")
    for e in summary['errors']:
        print("  -", e)
