"""One-time migration: v4.3 data -> v4.4 (superinvestor cross-check fixes: regulated infrastructure, reverse 2x2
check, businesses outside your markets, Uber, Kenvue).

Backs up data/<u>/ to data/<u>/backups/v4.3/ and applies Claude's re-scores from data/<u>/v4_4_rescore.csv
(id, code, value, note). Notes are appended to the company note as "v4.4: <code>: <note>". The Canada universe
(data/ca/) is new in v4.4 and needs no migration.

    python3 migrate_v4_4.py            # refuses if already applied (backups/v4.3 exists)
    python3 migrate_v4_4.py --force    # redo from backups/v4.3
"""
from __future__ import annotations

import argparse
import shutil
import sys

from screener.data import DATA_DIR, input_fields, load_universe, read_csv, write_csv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for key in ("us", "eu"):
        d = DATA_DIR / key
        bak = d / "backups" / "v4.3"
        if bak.exists():
            if not a.force:
                sys.exit(f"{bak} exists — v4.4 already applied; use --force to redo from it.")
        else:
            bak.mkdir(parents=True)
            shutil.copy2(d / "inputs.csv", bak / "inputs.csv")
        meta = load_universe(key)
        rows = read_csv(bak / "inputs.csv")
        by_id = {r["id"]: r for r in rows}
        changed = 0
        for x in read_csv(d / "v4_4_rescore.csv"):
            code = str(x["code"])                       # read_csv parses codes like "2.3" as numbers
            r = by_id.get(x["id"])
            if r is None:
                continue
            if x.get("value") is not None and r.get(code) != x["value"]:
                r[code] = x["value"]
                changed += 1
                if x.get("note"):
                    r["note"] = " | ".join(t for t in (r.get("note"), f"v4.4: {code}: {x['note']}") if t)
        write_csv(d / "inputs.csv", input_fields(meta), rows)
        print(f"{key}: {changed} values re-scored")


if __name__ == "__main__":
    main()
