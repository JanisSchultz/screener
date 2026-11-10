"""One-time migration: v4.4 data -> v5.0 (superinvestor quality filter: 'Chris Hohn bar').

Backs up data/<u>/ to data/<u>/backups/v4.4/ (if not already present) and applies re-scores from
data/<u>/v5_0_rescore.csv (id, code, value, note). Notes are appended as "v5.0: <code>: <note>".

    python3 migrate_v5_0.py            # refuses if already applied (backups/v4.4/inputs.csv exists)
    python3 migrate_v5_0.py --force    # redo from backups/v4.4
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
    for key in ("us", "eu", "ca"):
        d = DATA_DIR / key
        bak = d / "backups" / "v4.4"
        if bak.exists() and (bak / "inputs.csv").exists():
            if not a.force:
                pass  # Use existing backup
        else:
            bak.mkdir(parents=True, exist_ok=True)
            shutil.copy2(d / "inputs.csv", bak / "inputs.csv")
            if (d / "prescreen.csv").exists():
                shutil.copy2(d / "prescreen.csv", bak / "prescreen.csv")
        meta = load_universe(key)
        rows = read_csv(bak / "inputs.csv")
        by_id = {r["id"]: r for r in rows}
        changed = 0
        rescore_file = d / "v5_0_rescore.csv"
        if rescore_file.exists():
            for x in read_csv(rescore_file):
                code = str(x["code"])                       # read_csv parses codes like "2.3" as numbers
                r = by_id.get(x["id"])
                if r is None:
                    continue
                val = int(x["value"]) if str(x["value"]).isdigit() else x["value"]
                if x.get("value") is not None and r.get(code) != val:
                    r[code] = val
                    changed += 1
                    if x.get("note"):
                        r["note"] = " | ".join(t for t in (r.get("note"), f"v5.0: {code}: {x['note']}") if t)
        write_csv(d / "inputs.csv", input_fields(meta), rows)
        print(f"{key}: {changed} values re-scored")


if __name__ == "__main__":
    main()
