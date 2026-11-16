"""Generate and verify evaluations/completed/batch_15_evaluated.json.
"""
import json
import subprocess
import sys
from pathlib import Path

# Add project root and local working directory to sys.path
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_test import COMPANY_SCORES
from screener.apply_evaluation import validate_and_waterfall
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

BATCH_INPUT = ROOT / "evaluations" / "batches" / "batch_15.json"
BATCH_OUTPUT = ROOT / "evaluations" / "completed" / "batch_15_evaluated.json"

with open(BATCH_INPUT) as f:
    batch_data = json.load(f)

companies = batch_data["companies"]
print(f"Loaded {len(companies)} companies from {BATCH_INPUT}")

evaluated_array = []
warnings_found = []

for c in companies:
    ident = c["identity"]
    cid = ident["id"]
    uni = ident["universe"]
    cq = c["current_qualitative"]

    spec = COMPANY_SCORES[cid]
    m_tb, m_ia, m_se, m_rd = spec["moat"]
    f_ent, f_riv, f_buy, f_sup, f_sub = spec["forces"]
    g3a = spec["3a"]
    g3b = spec["3b"]
    g4n = spec["4n"]
    g5 = spec["5"]
    g6 = spec["6"]

    cap_init = compute_initial_cap_from_scores((m_tb, m_ia, m_se, m_rd))

    if g3b == "Y":
        cap_final, _, _ = compute_final_cap_from_scores(cap_init, (f_ent, f_riv, f_buy, f_sup, f_sub))
    else:
        cap_final = ""

    # Assemble raw qual
    qual_payload = {
        "1": "Y",
        "2": "Y",
        "2r": "",
        "3_tb": m_tb,
        "3_ia": m_ia,
        "3_se": m_se,
        "3_rd": m_rd,
        "3a": g3a,
        "3b": g3b,
        "3m": cq.get("3m", ""),
        "4_ent": f_ent if g3b == "Y" else "",
        "4_riv": f_riv if g3b == "Y" else "",
        "4_buy": f_buy if g3b == "Y" else "",
        "4_sup": f_sup if g3b == "Y" else "",
        "4_sub": f_sub if g3b == "Y" else "",
        "4": cap_final if g3b == "Y" else "",
        "4n": g4n if g3b == "Y" else "",
        "5": g5 if (g3b == "Y" and isinstance(cap_final, int) and cap_final >= 15) else "",
        "6": g6 if (g3b == "Y" and isinstance(cap_final, int) and cap_final >= 15 and g5 != 0) else "",
        "calamity": "",
        "calamity_note": "",
        "note": cq.get("note", ""),
        "evidence": cq.get("evidence", "")
    }

    entry = {
        "id": cid,
        "universe": uni,
        "qualitative": qual_payload
    }

    val_qual, _, warnings = validate_and_waterfall(entry)
    if warnings:
        warnings_found.append((cid, warnings))

    # Keep canonical order of keys
    canonical_keys = [
        "1", "2", "2r",
        "3_tb", "3_ia", "3_se", "3_rd", "3a", "3b", "3m",
        "4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n",
        "5", "6", "calamity", "calamity_note", "note", "evidence"
    ]
    ordered_qual = {k: val_qual.get(k, "") for k in canonical_keys}

    evaluated_entry = {
        "id": cid,
        "universe": uni,
        "qualitative": ordered_qual
    }
    evaluated_array.append(evaluated_entry)

if warnings_found:
    print(f"FAILED: {len(warnings_found)} warnings found during validation!")
    for cid, w in warnings_found:
        print(f"  {cid}: {w}")
    sys.exit(1)

print(f"Successfully evaluated all {len(evaluated_array)} companies without warnings.")

# Write to evaluations/completed/batch_15_evaluated.json
BATCH_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(BATCH_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(evaluated_array, f, indent=2, ensure_ascii=False)
print(f"Wrote completed evaluations to {BATCH_OUTPUT}")

# Dry-run validation of every entry via apply_evaluation.py
print("Running dry-run verification across all 68 evaluated companies...")
dry_run_failures = 0
for item in evaluated_array:
    cid = item["id"]
    p = subprocess.run(
        ["python3", str(ROOT / "screener" / "apply_evaluation.py"), "--dry-run", "--input", "-"],
        input=json.dumps(item),
        text=True,
        capture_output=True,
        cwd=str(ROOT)
    )
    if p.returncode != 0:
        print(f"Error on {cid}: returncode={p.returncode}")
        print("STDERR:", p.stderr)
        dry_run_failures += 1

if dry_run_failures == 0:
    print("ALL 68 COMPANIES SUCCESSFULLY VALIDATED VIA apply_evaluation.py --dry-run (0 errors)!")
else:
    print(f"Encountered {dry_run_failures} failures during dry-run!")
    sys.exit(1)
