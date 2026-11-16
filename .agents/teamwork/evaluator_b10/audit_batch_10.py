"""Independent forensic audit for batch_10_evaluated.json."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.apply_evaluation import apply_evaluation, validate_and_waterfall
from screener.gates import compute_final_cap_from_scores, compute_initial_cap_from_scores

BATCH_INPUT = ROOT / "evaluations" / "batches" / "batch_10.json"
BATCH_EVAL = ROOT / "evaluations" / "completed" / "batch_10_evaluated.json"

with open(BATCH_INPUT, "r", encoding="utf-8") as f:
    input_data = json.load(f)
with open(BATCH_EVAL, "r", encoding="utf-8") as f:
    eval_data = json.load(f)

input_comps = {c["identity"]["id"]: c for c in input_data["companies"]}
eval_comps = {c["id"]: c for c in eval_data}

print(f"Auditing Batch 10 Evaluated: {len(eval_data)} companies...")
assert len(eval_data) == 65, f"Expected 65 companies, got {len(eval_data)}"
assert set(input_comps.keys()) == set(eval_comps.keys()), "Company IDs mismatch!"

failures = []

for cid, comp in eval_comps.items():
    orig = input_comps[cid]
    q = comp["qualitative"]
    ident = orig["identity"]

    # 1. Identity & Universe
    if comp["universe"] != ident["universe"]:
        failures.append(f"{cid}: Universe mismatch ({comp['universe']} vs {ident['universe']})")

    # 2. Gate 1 & 2
    if q.get("1") != "Y":
        failures.append(f"{cid}: Gate 1 is not 'Y'")
    if q.get("2") != "Y":
        failures.append(f"{cid}: Gate 2 is not 'Y'")

    # 3. Gate 3 Moat Scores
    m_scores = [q.get("3_tb"), q.get("3_ia"), q.get("3_se"), q.get("3_rd")]
    for code, val in zip(["3_tb", "3_ia", "3_se", "3_rd"], m_scores):
        if val not in (0, 1, 2):
            failures.append(f"{cid}: Invalid moat score {code}={val}")

    m_tuple = tuple(int(x) for x in m_scores if x in (0, 1, 2))
    cap_init = compute_initial_cap_from_scores(m_tuple)
    m_max = max(m_tuple) if m_tuple else 0

    # 3a derivation
    top_archs = []
    if m_scores[0] == m_max and m_max > 0:
        top_archs.append("Toll booth & switching costs")
    if m_scores[1] == m_max and m_max > 0:
        top_archs.append("Irreplaceable infrastructure & intangibles")
    if m_scores[2] == m_max and m_max > 0:
        top_archs.append("Scale economies shared")
    if m_scores[3] == m_max and m_max > 0:
        top_archs.append("R&D & innovation leadership")

    if m_max == 0 and q.get("3a") != "None":
        failures.append(f"{cid}: Gate 3a expected 'None' when all moat scores 0, got {q.get('3a')}")
    elif m_max > 0 and q.get("3a") not in top_archs:
        failures.append(f"{cid}: Gate 3a '{q.get('3a')}' not among top archetypes {top_archs}")

    # Gate 3b
    g3b = q.get("3b")
    if g3b not in ("Y", "N"):
        failures.append(f"{cid}: Invalid Gate 3b: {g3b}")

    calamity = q.get("calamity") == "Y"

    # Sequential Waterfall
    if g3b == "N" and not calamity:
        # Must scrub downstream
        for k in ["4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n", "5", "6"]:
            if q.get(k) != "":
                failures.append(f"{cid}: Gate 3b failed, but '{k}' is '{q.get(k)}' instead of ''")
    else:
        # Gate 3 passes or calamity
        f_scores = [q.get("4_ent"), q.get("4_riv"), q.get("4_buy"), q.get("4_sup"), q.get("4_sub")]
        for code, val in zip(["4_ent", "4_riv", "4_buy", "4_sup", "4_sub"], f_scores):
            if val not in (0, 1, 2):
                failures.append(f"{cid}: Invalid force score {code}={val}")

        f_tuple = tuple(int(x) for x in f_scores if x in (0, 1, 2))
        cap_final, h, fatal = compute_final_cap_from_scores(cap_init, f_tuple)

        if q.get("4") != cap_final:
            failures.append(f"{cid}: Final CAP mismatch: got {q.get('4')}, expected {cap_final} (Initial {cap_init}, forces {f_tuple})")

        # 4n note check
        if any(x >= 1 for x in f_tuple):
            if not q.get("4n") or len(q.get("4n", "").strip()) < 10:
                failures.append(f"{cid}: Missing or too short 4n note when forces >= 1")

        # Downstream of Gate 4
        if cap_final < 15:
            if q.get("5") != "" or q.get("6") != "":
                failures.append(f"{cid}: Final CAP {cap_final} < 15, but 5='{q.get('5')}', 6='{q.get('6')}'")
        else:
            # Final CAP >= 15
            g5 = q.get("5")
            if calamity:
                if g5 not in (0, 1, 2):
                    failures.append(f"{cid}: Calamity Gate 5 invalid: {g5}")
            else:
                if g5 not in (1, 2):
                    failures.append(f"{cid}: Gate 5 expected 1 or 2, got {g5}")

            g6 = q.get("6")
            if g6 not in ("Y", "N"):
                failures.append(f"{cid}: Gate 6 expected 'Y' or 'N', got {g6}")

            if g6 == "Y" or calamity:
                # Check for forward growth formula in note
                note = q.get("note", "")
                if "[5-10Y g:" not in note:
                    failures.append(f"{cid}: Quality/Calamity pass note missing '[5-10Y g: ...]'")

    # Ingestion check with dry-run
    _, _, warnings = validate_and_waterfall({"id": cid, "qualitative": q})
    real_warnings = [w for w in warnings if not w.startswith("Waterfall: scrubbed")]
    if real_warnings:
        failures.append(f"{cid}: validate_and_waterfall produced warnings: {real_warnings}")

    # Dry-run apply_evaluation
    ok = apply_evaluation({"id": cid, "universe": comp["universe"], "qualitative": q}, dry_run=True)
    if not ok:
        failures.append(f"{cid}: apply_evaluation failed")

if failures:
    print(f"FAILED with {len(failures)} errors:")
    for f_err in failures:
        print(" -", f_err)
    sys.exit(1)
else:
    print("ALL 65 COMPANIES PASSED COMPLETE AUDIT WITH 0 ERRORS AND 0 WARNINGS!")
