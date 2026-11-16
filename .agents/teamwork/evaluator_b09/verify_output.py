import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
from screener.config import MOAT_TYPES

out_file = ROOT / "evaluations" / "completed" / "batch_09_evaluated.json"
assert out_file.exists(), f"{out_file} does not exist"

with open(out_file, "r", encoding="utf-8") as f:
    data = json.load(f)

assert isinstance(data, list), "Output is not a list"
assert len(data) == 65, f"Expected 65 companies, got {len(data)}"

growth_regex = re.compile(r"\[5-10Y g:.*?\]")

passed_count = 0
failed_g3_count = 0
failed_g4_count = 0
failed_g5_count = 0
failed_g6_count = 0

for item in data:
    cid = item["id"]
    u = item["universe"]
    qual = item["qualitative"]

    assert qual["1"] == "Y", f"[{cid}] G1 not Y"
    assert qual["2"] == "Y", f"[{cid}] G2 not Y"
    assert qual["2r"] == "", f"[{cid}] 2r not empty"

    m_scores = (qual["3_tb"], qual["3_ia"], qual["3_se"], qual["3_rd"])
    assert all(isinstance(x, int) and x in (0, 1, 2) for x in m_scores), f"[{cid}] Invalid moat scores: {m_scores}"
    cap_init = compute_initial_cap_from_scores(m_scores)
    m_max = max(m_scores)

    if m_max == 0:
        assert qual["3a"] == "None", f"[{cid}] Expected 3a='None', got {qual['3a']}"
    else:
        assert qual["3a"] in MOAT_TYPES, f"[{cid}] Invalid 3a: {qual['3a']}"

    assert qual["3b"] in ("Y", "N"), f"[{cid}] Invalid 3b: {qual['3b']}"
    assert qual["3m"], f"[{cid}] Empty 3m note"

    # Waterfall check
    if qual["3a"] == "None" or qual["3b"] == "N":
        failed_g3_count += 1
        for k in ["4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n", "5", "6"]:
            assert qual[k] == "", f"[{cid}] {k} should be empty for G3 reject, got {qual[k]!r}"
        assert "Fails Gate 3" in qual["note"] or "Rejected at Gate 3" in qual["note"], f"[{cid}] G3 note missing failure reason: {qual['note']}"
    else:
        f_scores = (qual["4_ent"], qual["4_riv"], qual["4_buy"], qual["4_sup"], qual["4_sub"])
        assert all(isinstance(x, int) and x in (0, 1, 2) for x in f_scores), f"[{cid}] Invalid force scores: {f_scores}"
        cap_final, mod_h, fatal = compute_final_cap_from_scores(cap_init, f_scores)
        assert qual["4"] == cap_final, f"[{cid}] G4 CAP mismatch: expected {cap_final}, got {qual['4']}"

        if any(x >= 1 for x in f_scores):
            assert qual["4n"], f"[{cid}] Missing 4n note when force >= 1"

        if cap_final < 15:
            failed_g4_count += 1
            assert qual["5"] == "", f"[{cid}] G5 should be empty for G4 reject, got {qual['5']!r}"
            assert qual["6"] == "", f"[{cid}] G6 should be empty for G4 reject, got {qual['6']!r}"
            assert "Fails Gate 4" in qual["note"], f"[{cid}] G4 note missing failure reason: {qual['note']}"
        else:
            assert isinstance(qual["5"], int) and qual["5"] in (0, 1, 2), f"[{cid}] Invalid G5 score: {qual['5']}"
            if qual["5"] == 0:
                failed_g5_count += 1
                assert qual["6"] == "", f"[{cid}] G6 should be empty for G5 reject, got {qual['6']!r}"
                assert "Fails Gate 5" in qual["note"], f"[{cid}] G5 note missing failure reason: {qual['note']}"
            else:
                assert qual["6"] in ("Y", "N"), f"[{cid}] Invalid G6: {qual['6']}"
                if qual["6"] == "N":
                    failed_g6_count += 1
                    assert "Fails Gate 6" in qual["note"], f"[{cid}] G6 note missing failure reason: {qual['note']}"
                else:
                    passed_count += 1
                    assert "Passes all 6 gates" in qual["note"], f"[{cid}] Pass note missing statement: {qual['note']}"
                    assert growth_regex.search(qual["note"]), f"[{cid}] Quality pass note missing [5-10Y g: ...]: {qual['note']}"

print("All assertions passed!")
print(f"Summary: Total = {len(data)}")
print(f"  Quality Pass: {passed_count}")
print(f"  Failed Gate 6: {failed_g6_count}")
print(f"  Failed Gate 5: {failed_g5_count}")
print(f"  Failed Gate 4: {failed_g4_count}")
print(f"  Failed Gate 3: {failed_g3_count}")
