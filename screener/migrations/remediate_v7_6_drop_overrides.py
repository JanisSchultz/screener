"""v7.6: remove analyst overrides and analyst notes from data/<universe>/financials.csv.

The valuation uses statement data only. This one-off migration
1. drops the override columns peak_eps_est, g_est, roic_est and g_implied (financials.csv is rewritten with the
   current FIN_FIELDS);
2. reduces fin_note to its machine-written '[auto] …' part (the analyst text quoted retired mechanics and old
   numbers; company rationale lives in inputs.csv note / evidence / 3m);
3. writes output/v7.6 removed overrides & notes.csv with every removed value for the record.

Usage:
    python3 screener/migrations/remediate_v7_6_drop_overrides.py [--dry-run]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.data import DATA_DIR, FIN_FIELDS, OUTPUT_DIR, read_csv, write_csv

UNIVERSES = ["us", "eu", "ca"]
OVERRIDE_FIELDS = ("peak_eps_est", "g_est", "roic_est", "g_implied")
AUTO = "[auto] "


def auto_part(note) -> str | None:
    """Keep only the '[auto] …' part(s) of a fin_note."""
    parts = [p.strip() for p in str(note or "").split(" | ") if p.strip().startswith(AUTO)]
    return " | ".join(parts) or None


def migrate(dry_run: bool = False) -> list[dict]:
    removed = []
    for u in UNIVERSES:
        path = DATA_DIR / u / "financials.csv"
        if not path.exists():
            continue
        rows = read_csv(path)
        for r in rows:
            old_note, new_note = r.get("fin_note"), auto_part(r.get("fin_note"))
            ov = {k: r.get(k) for k in OVERRIDE_FIELDS if r.get(k) not in (None, "")}
            if ov or (old_note or None) != new_note:
                removed.append({"universe": u, "id": r.get("id"), **{k: ov.get(k) for k in OVERRIDE_FIELDS},
                                "fin_note_removed_text": " | ".join(
                                    p.strip() for p in str(old_note or "").split(" | ")
                                    if p.strip() and not p.strip().startswith(AUTO)) or None,
                                "fin_note_kept": new_note})
            r["fin_note"] = new_note
            for k in OVERRIDE_FIELDS:
                r.pop(k, None)
        if not dry_run:
            write_csv(path, FIN_FIELDS, rows)
    if not dry_run and removed:
        out = OUTPUT_DIR / "v7.6 removed overrides & notes.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(removed[0]))
            w.writeheader()
            w.writerows(removed)
    return removed


if __name__ == "__main__":
    res = migrate(dry_run="--dry-run" in sys.argv)
    n_ov = sum(1 for r in res if any(r.get(k) for k in OVERRIDE_FIELDS))
    n_note = sum(1 for r in res if r.get("fin_note_removed_text"))
    print(f"{len(res)} rows changed: {n_ov} with overrides, {n_note} with analyst note text"
          + (" (dry run)" if "--dry-run" in sys.argv else ""))
