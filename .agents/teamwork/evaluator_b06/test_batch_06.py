"""Exhaustive verification test suite for batch_06_evaluated.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores
from screener.config import MOAT_SCORE_CODES, FORCE_SCORE_CODES, MOAT_SCORE_SPEC
from screener.bulk_scorer import ingest_evaluations

def test_batch_06():
    batch_in_path = ROOT / "evaluations" / "batches" / "batch_06.json"
    batch_out_path = ROOT / "evaluations" / "completed" / "batch_06_evaluated.json"

    assert batch_in_path.exists(), "batch_06.json missing"
    assert batch_out_path.exists(), "batch_06_evaluated.json missing"

    with open(batch_in_path, "r", encoding="utf-8") as f:
        data_in = json.load(f)
    with open(batch_out_path, "r", encoding="utf-8") as f:
        data_out = json.load(f)

    assert len(data_in["companies"]) == 65, f"Expected 65 in input, got {len(data_in['companies'])}"
    assert len(data_out) == 65, f"Expected 65 in output, got {len(data_out)}"

    in_companies = {c["id"]: c for c in data_in["companies"]}

    quality_pass_count = 0
    g3_reject_count = 0
    g4_reject_count = 0
    g6_reject_count = 0

    for idx, item in enumerate(data_out):
        cid = item["id"]
        assert cid in in_companies, f"Unknown company {cid}"
        in_c = in_companies[cid]
        ident = in_c["identity"]
        assert item["universe"] == ident["universe"], f"Universe mismatch for {cid}"

        qual = item["qualitative"]
        assert qual["1"] == "Y", f"[{cid}] Gate 1 must be 'Y'"
        assert qual["2"] == "Y", f"[{cid}] Gate 2 must be 'Y'"

        # Gate 3 Moat Profiles
        m_tuple = tuple(int(qual[c]) for c in MOAT_SCORE_CODES)
        cap_init = compute_initial_cap_from_scores(m_tuple)
        m_max = max(m_tuple)
        if m_max == 0:
            expected_3a = "None"
        else:
            top_archs = [arch for (code, arch, _) in MOAT_SCORE_SPEC if qual[code] == m_max]
            expected_3a = qual["3a"]
            assert expected_3a in top_archs, f"[{cid}] 3a '{expected_3a}' not in top archetypes {top_archs}"

        g3b = qual["3b"]
        assert g3b in ("Y", "N"), f"[{cid}] Invalid 3b '{g3b}'"
        assert len(qual["3m"]) > 20, f"[{cid}] 3m note too short"

        if g3b == "N" or expected_3a == "None":
            g3_reject_count += 1
            # Waterfall clearing
            for fc in FORCE_SCORE_CODES:
                assert qual[fc] == "", f"[{cid}] Gate 3 failed but {fc} is not empty"
            assert qual["4"] == "", f"[{cid}] Gate 3 failed but 4 is not empty"
            assert qual["4n"] == "", f"[{cid}] Gate 3 failed but 4n is not empty"
            assert qual["5"] == "", f"[{cid}] Gate 3 failed but 5 is not empty"
            assert qual["6"] == "", f"[{cid}] Gate 3 failed but 6 is not empty"
            assert "Fails Gate 3" in qual["note"] or "Rejected – G3" in qual["note"] or "Gate 3" in qual["note"], f"[{cid}] note should explain G3 rejection"
        else:
            # Gate 3 passed
            f_tuple = tuple(int(qual[fc]) for fc in FORCE_SCORE_CODES)
            if ident.get("is_fast_clock_speed"):
                assert f_tuple[4] >= 1, f"[{cid}] Fast clock speed company must have 4_sub >= 1"

            cap_final, mod_h, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)
            assert int(qual["4"]) == cap_final, f"[{cid}] Gate 4 CAP {qual['4']} != formula {cap_final}"

            has_force = any(x >= 1 for x in f_tuple)
            if has_force:
                assert len(qual["4n"]) > 20, f"[{cid}] 4n note mandatory when force >= 1"

            if cap_final < 15:
                g4_reject_count += 1
                assert qual["5"] == "", f"[{cid}] Final CAP < 15 but 5 is not empty"
                assert qual["6"] == "", f"[{cid}] Final CAP < 15 but 6 is not empty"
                assert "Fails Gate 4" in qual["note"] or "CAP = " in qual["note"], f"[{cid}] note should explain G4 rejection"
            else:
                # Gate 4 passed
                assert str(qual["5"]) in ("1", "2"), f"[{cid}] Final CAP >= 15 requires 5 in (1, 2)"
                assert qual["6"] in ("Y", "N"), f"[{cid}] Final CAP >= 15 requires 6 in ('Y', 'N')"

                if qual["6"] == "Y":
                    quality_pass_count += 1
                    assert "[5-10Y g:" in qual["note"], f"[{cid}] Quality pass note must contain [5-10Y g: ...]"
                else:
                    g6_reject_count += 1
                    assert "Fails Gate 6" in qual["note"] or "Rejected – G6" in qual["note"], f"[{cid}] Gate 6 reject note mismatch"

        assert len(qual["note"]) > 30, f"[{cid}] Note too short"
        assert len(qual["evidence"]) > 30, f"[{cid}] Evidence too short"

    print("Exhaustive verification PASSED!")
    print(f"Summary of Batch 06 (65 companies):")
    print(f"  - Quality Pass: {quality_pass_count}")
    print(f"  - Gate 6 Rejections: {g6_reject_count}")
    print(f"  - Gate 4 Rejections: {g4_reject_count}")
    print(f"  - Gate 3 Rejections: {g3_reject_count}")
    print(f"  - Total: {quality_pass_count + g6_reject_count + g4_reject_count + g3_reject_count} / 65")

if __name__ == "__main__":
    test_batch_06()
