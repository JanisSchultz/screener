"""v7.1 remediation of stale fin_notes and wrong-company listings.

1. fin_note analyst text written under earlier model versions quotes valuation snapshots ("At 34.77x peak Owner EPS …
   trades Above PAR (+44.1% vs PAR value of 319.25 DKK)", "expected 5Y IRR", "PAR multiple") that contradict the live
   model. Those sentences are stripped; the business rationale and the machine-written '[auto] …' part are kept.
2. eu:NEXI.IT and eu:TRN.IT were mapped to other companies (Nexity SA, GEK Terna) by the old name-substring resolver.
   Their symbol_map entries are removed so the next online fetch re-resolves them, and their rows are marked
   '[auto] stale fundamentals …' (valuation No data) until then.
3. Writes output/v7.1 fin_note review.csv: old / new note and any cited 'Operating ROIC normalized to X%' versus the
   computed tangible ROIC and RONIC₀ (flag when > 5pp apart) for the user's review.

Usage:
    python3 screener/migrations/remediate_v7_1_fin_notes.py [--dry-run]
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.data import DATA_DIR, FIN_FIELDS, OUTPUT_DIR, read_csv, write_csv

UNIVERSES = ["us", "eu", "ca"]
AUTO = "[auto] "
WRONG_LISTINGS = {"eu:NEXI.IT": "Nexity SA", "eu:TRN.IT": "GEK Terna Holdings"}
SNAPSHOT = re.compile(
    r"\b(?:above|below)\s+PAR\b|\bPAR\s+(?:value|multiple|val)\b|\b(?:premium|discount)\s+(?:vs\.?|to)\s+(?:the\s+)?"
    r"(?:fundamental\s+)?PAR\b|\bIRR\b|^At\s+[\d.,]+x\s+peak\s+Owner\s+EPS|\bvs\.?\s+PAR\b|\bcur_mult\b",
    re.I,
)
CITED_ROIC = re.compile(r"Operating ROIC (?:normalized to|of) ([\d.]+)%", re.I)
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"'])")


def strip_snapshots(note: str) -> tuple[str, list[str]]:
    parts = [p for p in str(note or "").split(" | ") if p.strip()]
    analyst = [p for p in parts if not p.startswith(AUTO)]
    auto = [p for p in parts if p.startswith(AUTO)]
    kept_parts, removed = [], []
    for part in analyst:
        sents = SENTENCE.split(part.strip())
        keep = [s for s in sents if not SNAPSHOT.search(s)]
        removed += [s for s in sents if SNAPSHOT.search(s)]
        if keep:
            kept_parts.append(" ".join(keep))
    return " | ".join(kept_parts + auto), removed


def mark_stale(row: dict, why: str) -> None:
    keep = [p for p in str(row.get("fin_note") or "").split(" | ") if p.strip() and not p.startswith(AUTO)]
    row["fin_note"] = " | ".join(keep + [AUTO + f"stale fundamentals ({why}; refetch required)"])


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    old_notes: dict[tuple[str, str], str] = {}
    removed_by: dict[tuple[str, str], list[str]] = {}
    for u in UNIVERSES:
        path = DATA_DIR / u / "financials.csv"
        rows = read_csv(path)
        n_changed = 0
        for row in rows:
            key = (u, row["id"])
            old_notes[key] = str(row.get("fin_note") or "")
            new, removed = strip_snapshots(row.get("fin_note"))
            lk = f"{u}:{row['id']}"
            if lk in WRONG_LISTINGS:
                row["fin_note"] = new
                mark_stale(row, f"was mapped to {WRONG_LISTINGS[lk]}")
                new = row["fin_note"]
            if new != old_notes[key]:
                n_changed += 1
                removed_by[key] = removed
                row["fin_note"] = new or None
        print(f"{u}: {n_changed} fin_notes changed")
        if not a.dry_run:
            bdir = DATA_DIR / u / "backups" / "pre_v7_1_fin_notes"
            bdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, bdir / "financials.csv")
            write_csv(path, FIN_FIELDS, rows)

    smap = DATA_DIR / "_cache" / "eodhd" / "symbol_map.json"
    if smap.exists():
        m = json.loads(smap.read_text(encoding="utf-8"))
        gone = [k for k in WRONG_LISTINGS if m.pop(k, None) is not None]
        print(f"symbol_map: removed {gone}")
        if not a.dry_run and gone:
            smap.write_text(json.dumps(dict(sorted(m.items())), indent=2), encoding="utf-8")

    if a.dry_run:
        print("[DRY RUN] nothing written")
        return

    from screener.dashboard import collect_screener_data
    data = collect_screener_data(UNIVERSES)
    out = OUTPUT_DIR / "v7.1 fin_note review.csv"
    cols = ["universe", "id", "result", "val_status", "cited_op_roic", "roic_operating", "roic_exp", "gap_pp", "flag",
            "removed_sentences", "old_note", "new_note"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in data["companies"]:
            key = (c["universe"], c["id"])
            old = old_notes.get(key, "")
            m_roic = CITED_ROIC.search(old)
            cited = float(m_roic.group(1)) / 100.0 if m_roic else None
            ref = c.get("roic_operating")
            gap = (cited - ref) * 100.0 if (cited is not None and ref is not None) else None
            if key not in removed_by and cited is None:
                continue
            w.writerow({
                "universe": c["universe"], "id": c["id"], "result": c["result"], "val_status": c["val_status"],
                "cited_op_roic": cited, "roic_operating": None if ref is None else round(ref, 4),
                "roic_exp": c.get("roic_exp"), "gap_pp": None if gap is None else round(gap, 1),
                "flag": "ROIC claim differs > 5pp" if (gap is not None and abs(gap) > 5.0) else "",
                "removed_sentences": " ‖ ".join(removed_by.get(key, [])), "old_note": old, "new_note": c.get("fin_note") or "",
            })
    print(f"review: {out}")


if __name__ == "__main__":
    main()
