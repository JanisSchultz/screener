"""Assemble, validate, and write evaluations/completed/batch_09_evaluated.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
THIS_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
from screener.bulk_scorer import validate_company_evaluation, QUAL_COLUMNS
from eval_part1 import PART_1
from eval_part2 import PART_2
from eval_part3 import PART_3

# Combine all evaluations
ALL_EVALS = {}
ALL_EVALS.update(PART_1)
ALL_EVALS.update(PART_2)
ALL_EVALS.update(PART_3)

print(f"Total defined evaluations: {len(ALL_EVALS)}")

# Load input batch
batch_file = ROOT / "evaluations" / "batches" / "batch_09.json"
with open(batch_file, "r", encoding="utf-8") as f:
    batch_data = json.load(f)

companies = batch_data["companies"]
print(f"Total companies in batch_09.json: {len(companies)}")

# Check for completeness
missing = [c["identity"]["id"] for c in companies if c["identity"]["id"] not in ALL_EVALS]
if missing:
    print(f"ERROR: Missing evaluations for {len(missing)} companies: {missing}")
    sys.exit(1)

# Build evaluated list
evaluated_list = []
total_warnings = 0
total_errors = 0

for c in companies:
    ident = c["identity"]
    cid = ident["id"]
    u = ident["universe"]
    cur_q = c["current_qualitative"]
    ev_def = ALL_EVALS[cid]

    # Assemble qualitative dictionary
    qual = {
        "1": "Y",
        "2": "Y",
        "2r": "",
        "3_tb": ev_def["3_tb"],
        "3_ia": ev_def["3_ia"],
        "3_se": ev_def["3_se"],
        "3_rd": ev_def["3_rd"],
        "3a": ev_def["3a"],
        "3b": ev_def["3b"],
        "3m": ev_def["3m"],
        "4_ent": ev_def.get("4_ent", ""),
        "4_riv": ev_def.get("4_riv", ""),
        "4_buy": ev_def.get("4_buy", ""),
        "4_sup": ev_def.get("4_sup", ""),
        "4_sub": ev_def.get("4_sub", ""),
        "4": ev_def.get("4", ""),
        "4n": ev_def.get("4n", ""),
        "5": ev_def.get("5", ""),
        "6": ev_def.get("6", ""),
        "calamity": ev_def.get("calamity", ""),
        "calamity_note": ev_def.get("calamity_note", ""),
        "note": ev_def["note"],
        "evidence": ev_def["evidence"],
    }

    # Deterministic CAP calculations
    m_scores = (qual["3_tb"], qual["3_ia"], qual["3_se"], qual["3_rd"])
    cap_init = compute_initial_cap_from_scores(m_scores)
    m_max = max(m_scores)

    # Validate 3a alignment
    if m_max == 0:
        assert qual["3a"] == "None", f"[{cid}] Expected 3a='None' but got {qual['3a']}"
    else:
        # Check that 3a is one of the archetypes achieving max
        arch_map = {
            0: "Toll booth & switching costs",
            1: "Irreplaceable infrastructure & intangibles",
            2: "Scale economies shared",
            3: "R&D & innovation leadership"
        }
        valid_archs = [arch_map[i] for i, s in enumerate(m_scores) if s == m_max]
        assert qual["3a"] in valid_archs, f"[{cid}] 3a '{qual['3a']}' not in valid top archetypes {valid_archs}"

    # Waterfall check: if fails Gate 3
    if qual["3a"] == "None" or qual["3b"] == "N":
        assert qual["3b"] == "N" or qual["3a"] == "None"
        for k in ["4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n", "5", "6"]:
            qual[k] = ""
    else:
        # Gate 3 passes!
        # Check that force scores are present
        f_scores = (qual["4_ent"], qual["4_riv"], qual["4_buy"], qual["4_sup"], qual["4_sub"])
        assert all(isinstance(x, int) and x in (0, 1, 2) for x in f_scores), f"[{cid}] Incomplete/invalid force scores: {f_scores}"
        cap_final, mod_h, fatal = compute_final_cap_from_scores(cap_init, f_scores)
        qual["4"] = cap_final

        # Check 4n is present if any force >= 1
        if any(x >= 1 for x in f_scores):
            assert qual["4n"], f"[{cid}] Missing 4n note when force >= 1"

        if cap_final < 15:
            qual["5"] = ""
            qual["6"] = ""
        else:
            assert isinstance(qual["5"], int) and qual["5"] in (0, 1, 2), f"[{cid}] Invalid Gate 5 score: {qual['5']}"
            if qual["5"] == 0:
                qual["6"] = ""
            else:
                assert qual["6"] in ("Y", "N"), f"[{cid}] Invalid Gate 6: {qual['6']}"

    # Test via bulk_scorer.validate_company_evaluation
    payload_item = {
        "id": cid,
        "universe": u,
        "qualitative": qual,
    }
    sanitized, warnings, errors = validate_company_evaluation(payload_item, existing_row=cur_q)
    if warnings:
        print(f"[{cid}] Warnings: {warnings}")
        total_warnings += len(warnings)
    if errors:
        print(f"[{cid}] ERRORS: {errors}")
        total_errors += len(errors)

    evaluated_list.append(payload_item)

print(f"Validation complete! Total warnings: {total_warnings}, Total errors: {total_errors}")
if total_errors > 0:
    print("Cannot proceed with errors!")
    sys.exit(1)

# Write output file
out_path = ROOT / "evaluations" / "completed" / "batch_09_evaluated.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(evaluated_list, f, indent=2, ensure_ascii=False)

print(f"Successfully wrote {len(evaluated_list)} evaluated companies to {out_path}")
