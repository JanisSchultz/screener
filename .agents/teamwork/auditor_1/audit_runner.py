"""Forensic Integrity Auditor Script (Updated).
Runs comprehensive empirical verification checks across:
1. Authenticity & text diversity of batch evaluations
2. Preservation of 11 Phase 1 reference companies vs git baseline & R2 mirror sync requirements
3. Deterministic CAP calculations & zero manual overrides
4. Calamity rules & anchor gate non-waivability
5. Sequential Munger waterfall & mirror synchronization
"""
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.gates import (
    compute_initial_cap_from_scores,
    compute_final_cap_from_scores,
    normalize_moat_label,
)
from screener.config import (
    MOAT_SCORE_CODES,
    FORCE_SCORE_CODES,
    MOAT_SCORE_SPEC,
)

REFERENCE_TICKERS = {
    "SPGI", "COST", "ASML.NL", "ASML", "MSFT", "WM",
    "RMS.FR", "CNR.CA", "HSY", "CRM", "NUE"
}

SCORE_KEYS = [
    "1", "2", "2r",
    "3_tb", "3_ia", "3_se", "3_rd", "3a", "3b", "3m",
    "4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n",
    "5", "6",
    "calamity", "calamity_note"
]

QUAL_MIRROR_COLS = [
    "1", "2", "2r",
    "3_tb", "3_ia", "3_se", "3_rd", "3a", "3b", "3m",
    "4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n",
    "5", "6",
    "calamity", "calamity_note",
    "note", "evidence"
]

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def run_git_show(ref_path):
    cmd = ["git", "show", f"HEAD:{ref_path}"]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    reader = csv.DictReader(res.stdout.splitlines())
    return list(reader)

print("=" * 80)
print("STARTING FORENSIC INTEGRITY AUDIT")
print("=" * 80)

# ---------------------------------------------------------
# Check 1: Authenticity & Diversity Forensics
# ---------------------------------------------------------
print("\n--- CHECK 1: AUTHENTICITY & TEXT DIVERSITY ---")
batch_dir = ROOT / "evaluations" / "completed"
batch_files = sorted(batch_dir.glob("batch_*_evaluated.json"))
print(f"Found {len(batch_files)} completed batch files.")

total_batch_companies = 0
all_4n_notes = []
all_batch_ids = []
unique_evaluations = {}

for bf in batch_files:
    with open(bf, "r", encoding="utf-8") as f:
        data = json.load(f)
    comps = data if isinstance(data, list) else data.get("companies", [])
    total_batch_companies += len(comps)
    for c in comps:
        cid = c.get("id") or (c.get("identity", {}).get("id") if "identity" in c else None)
        all_batch_ids.append(cid)
        qual = c.get("qualitative") or c
        note_4n = qual.get("4n", "")
        if note_4n:
            all_4n_notes.append((cid, note_4n))
        unique_evaluations[cid] = qual

print(f"Total companies evaluated across batch files: {total_batch_companies}")
print(f"Unique company IDs in batches: {len(set(all_batch_ids))}")
print(f"Total non-empty 4n notes in batches: {len(all_4n_notes)}")

unique_notes = set(n for _, n in all_4n_notes)
print(f"Unique non-empty 4n notes: {len(unique_notes)}")
uniqueness_ratio = len(unique_notes) / len(all_4n_notes) if all_4n_notes else 0
print(f"4n Uniqueness ratio: {uniqueness_ratio:.4f}")

# Check for duplicate 4n notes across different companies
note_counts = Counter(n for _, n in all_4n_notes)
duplicates = [n for n, count in note_counts.items() if count > 1]
print(f"Duplicate 4n notes found: {len(duplicates)}")
if duplicates:
    for d in duplicates:
        matching_cids = [cid for cid, n in all_4n_notes if n == d]
        print(f"  Count {note_counts[d]}: {matching_cids} -> {d[:100]}...")

# Text diversity metrics
total_words = sum(len(n.split()) for _, n in all_4n_notes)
avg_word_count = total_words / len(all_4n_notes) if all_4n_notes else 0
all_words = [w.lower() for _, n in all_4n_notes for w in re.findall(r'\b[a-zA-Z]{3,}\b', n)]
vocab_size = len(set(all_words))
print(f"Total words in 4n notes: {total_words}")
print(f"Average word count per 4n note: {avg_word_count:.1f} words")
print(f"Vocabulary size (distinct words >=3 letters): {vocab_size}")

# Check business-model specific terms
business_terms = [
    "patent", "clinical", "hyperscaler", "concession", "pipeline", "brand",
    "switching cost", "oem", "saas", "subscriber", "semiconductor", "cloud",
    "contract", "regulatory", "distribution", "terminal", "logistics"
]
terms_found = {term: sum(1 for _, n in all_4n_notes if term in n.lower()) for term in business_terms}
print("Sample business specific terms frequency in 4n notes:")
for t, c in terms_found.items():
    print(f"  '{t}': {c} occurrences")

# ---------------------------------------------------------
# Check 2: Reference Preservation
# ---------------------------------------------------------
print("\n--- CHECK 2: REFERENCE PRESERVATION ---")
ref_score_violations = []
ref_all_violations = []

for u in ("us", "eu", "ca"):
    rel_path = f"data/{u}/inputs.csv"
    curr_rows = {r["id"]: r for r in load_csv(ROOT / rel_path)}
    base_rows = {r["id"]: r for r in run_git_show(rel_path)}

    for ref_id in REFERENCE_TICKERS:
        if ref_id in base_rows:
            if ref_id not in curr_rows:
                ref_all_violations.append(f"Reference company {ref_id} deleted from {rel_path}!")
                continue
            base_r = base_rows[ref_id]
            curr_r = curr_rows[ref_id]
            
            diffs = {}
            for k in base_r.keys():
                b_val = base_r.get(k, "")
                c_val = curr_r.get(k, "")
                if b_val != c_val:
                    diffs[k] = (b_val, c_val)
            if diffs:
                ref_all_violations.append(f"Reference company {ref_id} ({u}) modified: {list(diffs.keys())}")
                score_diffs = {k: v for k, v in diffs.items() if k in SCORE_KEYS}
                if score_diffs:
                    ref_score_violations.append(f"Reference company {ref_id} ({u}) score modified: {score_diffs}")
            else:
                print(f"  PASS: Reference company {ref_id} ({u}) 100% preserved (all fields identical)")

print(f"Reference Company Score Violations: {len(ref_score_violations)}")
print(f"Reference Company Total Modifications: {len(ref_all_violations)}")
if ref_all_violations:
    for av in ref_all_violations:
        print(f"  Detail: {av}")

# ---------------------------------------------------------
# Check 3: Deterministic CAP Calculation & No Manual Overrides
# ---------------------------------------------------------
print("\n--- CHECK 3: NO MANUAL OVERRIDE ON DETERMINISTIC CAP ---")
override_violations = []
gate3_count = 0

for u in ("us", "eu", "ca"):
    rows = load_csv(ROOT / f"data/{u}/inputs.csv")
    for r in rows:
        if r.get("1") != "Y" or r.get("2") != "Y":
            continue
        gate3_count += 1
        cid = r["id"]

        # Check Gate 3 Moat Scores
        m_vals = [r.get(c, "") for c in MOAT_SCORE_CODES]
        if any(v == "" for v in m_vals):
            override_violations.append(f"[{cid}] Incomplete moat scores: {m_vals}")
            continue

        m_tuple = tuple(int(v) for v in m_vals)
        exp_init_cap = compute_initial_cap_from_scores(m_tuple)
        m_max = max(m_tuple)

        # Check 3a alignment
        stored_3a = normalize_moat_label(r.get("3a", ""))
        if m_max == 0:
            if stored_3a != "None":
                override_violations.append(f"[{cid}] 3a is '{stored_3a}' but max moat is 0 (expected 'None')")
        else:
            top_archs = [arch for (code, arch, _) in MOAT_SCORE_SPEC if int(r[code]) == m_max]
            if stored_3a not in top_archs:
                override_violations.append(f"[{cid}] 3a '{stored_3a}' not in top archetypes {top_archs}")

        # Check Final CAP 4 if company passed Gate 3
        g3a = stored_3a
        g3b = r.get("3b", "")
        calamity = r.get("calamity", "") == "Y"
        passed_g3 = (g3a != "None") and (g3b == "Y" or calamity)

        if passed_g3:
            f_vals = [r.get(c, "") for c in FORCE_SCORE_CODES]
            if any(v == "" for v in f_vals):
                override_violations.append(f"[{cid}] Passed Gate 3 but incomplete force scores: {f_vals}")
                continue
            f_tuple = tuple(int(v) for v in f_vals)
            exp_final_cap, mod_h, fatal_flaw = compute_final_cap_from_scores(exp_init_cap, f_tuple)

            stored_4 = r.get("4", "")
            if stored_4 == "":
                override_violations.append(f"[{cid}] Passed Gate 3 but '4' (Final CAP) is blank")
            else:
                try:
                    s4_int = int(stored_4)
                    if s4_int != exp_final_cap:
                        override_violations.append(
                            f"[{cid}] CAP override detected! stored 4={s4_int} != computed exp={exp_final_cap} "
                            f"(init={exp_init_cap}, forces={f_tuple}, fatal={fatal_flaw})"
                        )
                except ValueError:
                    override_violations.append(f"[{cid}] Final CAP '4' is not integer: {stored_4!r}")

print(f"Total Gate 3 companies checked: {gate3_count}")
print(f"CAP Override / Derivation Violations: {len(override_violations)}")
for ov in override_violations[:10]:
    print(f"  FAIL: {ov}")
if not override_violations:
    print("  PASS: Zero manual CAP overrides across all Gate 3 companies!")

# ---------------------------------------------------------
# Check 4: Calamity Rule Check
# ---------------------------------------------------------
print("\n--- CHECK 4: CALAMITY RULE INTEGRITY ---")
calamity_violations = []
calamity_count = 0

for u in ("us", "eu", "ca"):
    rows = load_csv(ROOT / f"data/{u}/inputs.csv")
    for r in rows:
        cid = r["id"]
        if r.get("calamity") == "Y":
            calamity_count += 1
            g1 = r.get("1", "")
            g2 = r.get("2", "")
            g3a = normalize_moat_label(r.get("3a", ""))
            g3b = r.get("3b", "")
            g4_str = r.get("4", "")
            g5 = r.get("5", "")
            g6 = r.get("6", "")
            cnote = r.get("calamity_note", "")

            # Anchor gates check
            if g1 != "Y":
                calamity_violations.append(f"[{cid}] Calamity on failed Anchor Gate 1 ({g1})")
            if g2 != "Y":
                calamity_violations.append(f"[{cid}] Calamity on failed Anchor Gate 2 ({g2})")
            if g3a == "None":
                calamity_violations.append(f"[{cid}] Calamity on failed Anchor Gate 3a ({g3a})")
            try:
                g4_int = int(g4_str)
                if g4_int < 15:
                    calamity_violations.append(f"[{cid}] Calamity on failed Anchor Gate 4 (CAP={g4_int} < 15)")
            except ValueError:
                calamity_violations.append(f"[{cid}] Calamity on missing/invalid Anchor Gate 4 ({g4_str!r})")

            # Must have at least one eligible gate failed
            eligible = (g3b == "N" or g5 == "0" or g6 == "N")
            if not eligible:
                calamity_violations.append(f"[{cid}] Calamity set but no eligible gate (3b, 5, 6) failed (3b={g3b}, 5={g5}, 6={g6})")

            # Calamity note must exist
            if not cnote or len(cnote.strip()) < 10:
                calamity_violations.append(f"[{cid}] Calamity set but calamity_note is empty or trivial")

print(f"Total Calamity companies found: {calamity_count}")
print(f"Calamity Violations: {len(calamity_violations)}")
for cv in calamity_violations[:10]:
    print(f"  FAIL: {cv}")
if not calamity_violations:
    print(f"  PASS: All {calamity_count} calamity companies strictly obey anchor gates and rules!")

# ---------------------------------------------------------
# Check 5: Sequential Waterfall & Mirror Synchronization
# ---------------------------------------------------------
print("\n--- CHECK 5: SEQUENTIAL WATERFALL & MIRROR SYNCHRONIZATION ---")
waterfall_violations = []

for u in ("us", "eu", "ca"):
    rows = load_csv(ROOT / f"data/{u}/inputs.csv")
    for r in rows:
        cid = r["id"]
        g1 = r.get("1", "")
        g2 = r.get("2", "")
        g3a = normalize_moat_label(r.get("3a", ""))
        g3b = r.get("3b", "")
        calamity = r.get("calamity") == "Y"

        if g1 == "N":
            downstream = [k for k in ("2", "2r", *MOAT_SCORE_CODES, "3a", "3b", "3m", *FORCE_SCORE_CODES, "4", "4n", "5", "6") if r.get(k, "") != ""]
            if downstream:
                waterfall_violations.append(f"[{cid}] Gate 1='N' but downstream not blank: {downstream}")
            continue

        if g2 == "N":
            downstream = [k for k in (*MOAT_SCORE_CODES, "3a", "3b", "3m", *FORCE_SCORE_CODES, "4", "4n", "5", "6") if r.get(k, "") != ""]
            if downstream:
                waterfall_violations.append(f"[{cid}] Gate 2='N' but downstream not blank: {downstream}")
            continue

        # If reaching Gate 3:
        if g1 == "Y" and g2 == "Y":
            failed_g3 = (g3a == "None") or (g3b == "N" and not calamity)
            if failed_g3:
                downstream = [k for k in (*FORCE_SCORE_CODES, "4", "4n", "5", "6") if r.get(k, "") != ""]
                if downstream:
                    waterfall_violations.append(f"[{cid}] Gate 3 failed but downstream not blank: {downstream}")
            else:
                # Gate 3 passed:
                g4_str = r.get("4", "")
                try:
                    g4_int = int(g4_str)
                    if g4_int < 15:
                        downstream = [k for k in ("5", "6") if r.get(k, "") != ""]
                        if downstream:
                            waterfall_violations.append(f"[{cid}] Gate 4 CAP < 15 ({g4_int}) but Gates 5-6 not blank: {downstream}")
                    else:
                        # Gate 4 passed (CAP >= 15): Gate 5 must be evaluated
                        g5_val = r.get("5", "")
                        if g5_val == "":
                            waterfall_violations.append(f"[{cid}] Gate 4 CAP >= 15 ({g4_int}) but Gate 5 is blank")
                        elif g5_val == "0" and not calamity:
                            # Gate 5 failed without calamity: Gate 6 must be blank
                            if r.get("6", "") != "":
                                waterfall_violations.append(f"[{cid}] Gate 5=0 without calamity but Gate 6 not blank: {r.get('6')!r}")
                        else:
                            # Gate 5 passed or calamity: Gate 6 must be evaluated
                            if r.get("6", "") == "":
                                waterfall_violations.append(f"[{cid}] Gate 5={g5_val} but Gate 6 is blank")
                except ValueError:
                    waterfall_violations.append(f"[{cid}] Gate 3 passed but Gate 4 not an integer: {g4_str!r}")

                # Check mandatory 4n
                forces = [int(r[fc]) for fc in FORCE_SCORE_CODES if r.get(fc, "") != ""]
                if any(f in (1, 2) for f in forces) and not r.get("4n", "").strip():
                    waterfall_violations.append(f"[{cid}] Force >= 1 but 4n note is empty")

print(f"Waterfall Violations: {len(waterfall_violations)}")
for wv in waterfall_violations[:10]:
    print(f"  FAIL: {wv}")
if not waterfall_violations:
    print("  PASS: 100% strict Munger sequential waterfall compliance across all universes!")

# Mirror Parity Check
print("\n--- MIRROR PARITY CHECK ---")
mirror_violations = []
us_meta = json.loads((ROOT / "data" / "us" / "universe.json").read_text(encoding="utf-8"))
mirrors = us_meta.get("mirror", {})

us_rows_map = {r["id"]: r for r in load_csv(ROOT / "data" / "us" / "inputs.csv")}
eu_rows_map = {r["id"]: r for r in load_csv(ROOT / "data" / "eu" / "inputs.csv")}

for tgt, src_spec in mirrors.items():
    src_uni, src_id = src_spec.split(":") if ":" in src_spec else ("eu", src_spec)
    src_map = eu_rows_map if src_uni == "eu" else us_rows_map
    tgt_r = us_rows_map.get(tgt)
    src_r = src_map.get(src_id)

    if not tgt_r or not src_r:
        mirror_violations.append(f"Mirror pair missing: tgt={tgt}, src={src_id}")
        continue

    for col in QUAL_MIRROR_COLS:
        v_tgt = tgt_r.get(col, "")
        v_src = src_r.get(col, "")
        if v_tgt != v_src:
            mirror_violations.append(f"Mirror mismatch on {tgt} vs {src_id} for '{col}': tgt={v_tgt!r} != src={v_src!r}")

print(f"Mirror Qualitative Violations: {len(mirror_violations)}")
for mv in mirror_violations:
    print(f"  FAIL: {mv}")
if not mirror_violations:
    print("  PASS: Dual-listed mirror tickers match 100% character-for-character across all qualitative fields!")

print("\n" + "=" * 80)
print("FORENSIC VERDICT SUMMARY:")
clean_verdict = (
    not ref_score_violations
    and not override_violations
    and not calamity_violations
    and not waterfall_violations
    and not mirror_violations
    and uniqueness_ratio > 0.95
)
if clean_verdict:
    print("FORENSIC VERDICT: CLEAN")
else:
    print("FORENSIC VERDICT: INTEGRITY VIOLATION")
print("=" * 80)
