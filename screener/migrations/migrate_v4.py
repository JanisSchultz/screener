"""One-time migration: v3 data -> v4 (gate-based framework) data files.

Backs up data/<u>/ to data/<u>/backups/v3/, converts the v3 scores mechanically (see "Seeded from" on
Methodology), merges Claude's pre-scores for the new fields from data/<u>/v4_prescore.csv and removes
overrides.csv (the Overrides sheet is gone in v4; both universes had no overrides).

    python3 migrate_v4.py            # refuses if inputs.csv is already v4
    python3 migrate_v4.py --force    # redo from backups/v3
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from screener.data import DATA_DIR, HOLD_FIELDS, PRESCREEN_FIELDS, input_fields, load_universe, read_csv, write_csv

FILES = ("inputs.csv", "prescreen.csv", "overrides.csv", "holdings.csv", "universe.json")
EROSION = {"3.3a": "technological disruption", "3.3b": "counter-positioning challenger",
           "3.3c": "substitution / disintermediation", "3.3d": "regulation / patent cliff",
           "3.3e": "brand dilution", "3.3f": "talent appeal"}
PRESCORED = ["0.1", "1.1g", "1.2", "1.1b", "3.2d", "conf_v4", "note_v4"]
V4_NOTE = ("v4: gate-based framework. v3 scores converted mechanically (Methodology → 'Seeded from'); Simplicity, "
           "Geopolitics, Maslow level, Customer Breadth and Irreplaceable Physical Assets pre-scored by Claude from "
           "public knowledge as of November 2026 (sub-industry baseline, then company adjustments) — see 'Confidence v4' "
           "and 'v4 note' on Inputs. Gate 2 (Sole-Owner) is the investor's own and defaults to Y.")


def num(v):
    return v if isinstance(v, (int, float)) else 0


def convert(o: dict, meta: dict) -> dict:
    r = {k: o.get(k) for k in ["id", "ticker", "company", "country", "sector", "sub_industry"]}
    for x in meta.get("extra_columns", []):
        r[x["key"]] = o.get(x["key"])
    yn = lambda ok: "Y" if ok else "N"
    r.update({
        "0.2": "N" if o.get("ps_exclude") == "Y" else None, "0.2r": o.get("ps_reason"),
        "1.1b": o.get("3.1b"),
        "1.3": yn(num(o.get("1.4")) >= 1), "1.4": yn(num(o.get("1.3")) >= 1),
        "2.1a": o.get("2.1a"), "2.1b": o.get("2.1b"), "2.2a": o.get("2.2a"), "2.2b": o.get("2.2b"),
        "2.3": yn(o.get("2.3b") == 2 or (o.get("2.3b") == 1 and o.get("2.3a") == 2)),
        "3.1a": o.get("3.1a"),
        "3.2a": o.get("3.2a"), "3.2b": o.get("3.2b"), "3.2c": o.get("3.2c"),
        "3.2d": o.get("3.2e"),                      # baseline: v3 Efficient Scale, replaced by the pre-score
        "3.2e": o.get("3.2d"), "3.2f": o.get("3.2f"),
        "3.2br": o.get("3.2br") or o.get("3.2bb"),
        "3.3n": o.get("3.3n"),
        "3.3t": "; ".join(f"{t} ({'high' if o.get(c) == 0 else 'moderate'})" for c, t in EROSION.items()
                          if isinstance(o.get(c), int) and o.get(c) < 2) or None,
        "3.4": min(num(o.get("3.4a")), num(o.get("3.4c"))),
        "confidence": "L" if "L" in (o.get("confidence"), o.get("conf_v3")) else
                      "M" if "M" in (o.get("confidence"), o.get("conf_v3")) else "H",
        "note": " | ".join(x for x in (o.get("note_v3"), o.get("note")) if x) or None,
        "evidence": o.get("evidence"), "last_reviewed": o.get("last_reviewed"),
    })
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for key in ("us", "eu"):
        d = DATA_DIR / key
        bak = d / "backups" / "v3"
        header = (d / "inputs.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
        if "0.1" in header:
            if not a.force:
                sys.exit(f"{d}/inputs.csv is already v4 — use --force to redo from backups/v3.")
        else:
            bak.mkdir(parents=True, exist_ok=True)
            for f in FILES:
                if (d / f).exists():
                    shutil.copy2(d / f, bak / f)
        pre = {r["id"]: r for r in read_csv(d / "v4_prescore.csv")} if (d / "v4_prescore.csv").exists() else {}
        old = read_csv(bak / "inputs.csv")
        meta = load_universe(key)                   # universe.json + extra_columns
        rows = []
        for o in old:
            r = convert(o, meta)
            p = pre.get(o["id"], {})
            for k in PRESCORED:
                if p.get(k) is not None:
                    r[k] = p[k]
            rows.append(r)
        missing = sum(1 for o in old if o["id"] not in pre)
        write_csv(d / "inputs.csv", input_fields(meta), rows)
        write_csv(d / "prescreen.csv", PRESCREEN_FIELDS,
                  [{"sector": p["sector"], "sub_industry": p["sub_industry"], "sole_owner": p.get("in_circle") or "Y",
                    "note": p.get("note")} for p in read_csv(bak / "prescreen.csv")])
        write_csv(d / "holdings.csv", HOLD_FIELDS, [{("entry_eb" if k == "entry_bith" else k): v for k, v in h.items()}
                                                    for h in read_csv(bak / "holdings.csv")])
        (d / "overrides.csv").unlink(missing_ok=True)
        uj = json.loads((d / "universe.json").read_text(encoding="utf-8"))
        uj["how_produced"] = [t for t in uj.get("how_produced", []) if not t.startswith("v4:")] + [V4_NOTE]
        (d / "universe.json").write_text(json.dumps(uj, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{key}: {len(rows)} companies -> v4 inputs ({len(pre)} pre-scored, {missing} without pre-score)")


if __name__ == "__main__":
    main()
