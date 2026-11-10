"""Remediate the v6.21 Gate 3/4 architectural swap across all universes.

In v6.21, Gate 3 (Moat & Pricing) and Gate 4 (Runway CAP) were swapped.
Companies that had failed Old Gate 3 (Runway CAP < 15) had their Moat columns
purged in v6.9 and were subsequently stranded in 'To review (blank gate)' at
the new Gate 3.

This script restores their historical moat archetype, pricing power, and
moat notes from data/<universe>/backups/pre_waterfall/inputs.csv and strictly
enforces the v6.23 sequential waterfall:
- If Gate 3 fails (3a == 'None' or 3b == 'N'): Gate 4 is cleared ('') -> Rejected at Gate 3.
- If Gate 3 passes (3a != 'None' and 3b == 'Y'): Gate 4 is populated with CAP (0, 5, 10) -> Rejected at Gate 4.
- In both cases, downstream Gates 5 and 6 are cleared ('').
"""
from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.data import DATA_DIR, load_universe, read_csv, write_csv
from screener.gates import results
import collections

UNIVERSES = ["us", "eu", "ca"]


def remediate_universe(universe: str, dry_run: bool = False) -> dict:
    u_dir = DATA_DIR / universe
    inputs_path = u_dir / "inputs.csv"
    backup_source = u_dir / "backups" / "pre_waterfall" / "inputs.csv"

    if not inputs_path.exists() or not backup_source.exists():
        print(f"Skipping {universe}: missing inputs.csv or pre_waterfall backup.")
        return {}

    # Load current universe & identify stranded companies
    meta = load_universe(universe)
    res_before = results(meta)
    counts_before = collections.Counter(r["result"] for r in res_before.values())
    stranded_ids = {c["id"] for c in meta["companies"] if res_before[c["id"]]["result"] == "To review (blank gate)"}

    print(f"\n========================================================")
    print(f"Remediating {universe.upper()} ({len(stranded_ids)} stranded companies)")
    print(f"========================================================")

    # Load pre_waterfall backup
    with backup_source.open(newline="", encoding="utf-8") as f:
        bk_rows = {r["id"]: r for r in csv.DictReader(f)}

    # Read current raw inputs
    with inputs_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        current_rows = list(reader)

    updated_rows = []
    g3_rej = 0
    g4_rej = 0
    not_matched = 0

    for r in current_rows:
        row = dict(r)
        cid = row["id"]

        if cid in stranded_ids:
            bk = bk_rows.get(cid)
            if not bk:
                print(f"Warning: {cid} not found in pre_waterfall backup.")
                not_matched += 1
                updated_rows.append(row)
                continue

            m_arch = bk.get("4a") or "None"
            m_price = bk.get("4b") or "N"
            m_note = bk.get("4m") or ""
            cap_val = bk.get("3") or ""

            # Ensure Gate 2 is explicitly marked Y
            if not row.get("2"):
                row["2"] = "Y"
                row["2r"] = ""

            # Set Gate 3
            row["3a"] = m_arch
            row["3b"] = m_price
            if m_note and not row.get("3m"):
                row["3m"] = m_note

            # Apply waterfall
            if m_arch == "None" or m_price == "N":
                row["4"] = ""
                row["5"] = ""
                row["6"] = ""
                g3_rej += 1
            else:
                row["4"] = cap_val
                row["5"] = ""
                row["6"] = ""
                g4_rej += 1

        updated_rows.append(row)

    print(f"Updated {g3_rej + g4_rej} companies:")
    print(f"  - Classified as Rejected – G3 Moat & Pricing: {g3_rej}")
    print(f"  - Classified as Rejected – G4 Runway (<15Y) : {g4_rej}")
    if not_matched:
        print(f"  - Unmatched in backup: {not_matched}")

    if not dry_run:
        # Create a backup before writing
        backup_dest = u_dir / "backups" / "pre_remediation_inputs.csv"
        shutil.copy2(inputs_path, backup_dest)
        print(f"Backed up current inputs to {backup_dest.name}")

        # Write updated CSV
        with inputs_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        print(f"Successfully wrote updated inputs to {inputs_path}")

        # Verify new results
        meta_after = load_universe(universe)
        res_after = results(meta_after)
        counts_after = collections.Counter(r["result"] for r in res_after.values())
        print(f"\nFunnel counts after remediation:")
        for k, v in counts_after.most_common():
            print(f"  {k:45}: {v}")

        return counts_after

    return counts_before


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--universe", "-u", choices=UNIVERSES + ["all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets = UNIVERSES if args.universe == "all" else [args.universe]
    for u in targets:
        remediate_universe(u, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
