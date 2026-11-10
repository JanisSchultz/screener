"""One-time migration: v4.0 data -> v4.1 (model types, Understandability, cyclical flag, financial estimates).

Backs up data/<u>/ to data/<u>/backups/v4.0/, adds the new Inputs / Financials / Holdings columns, seeds the
business-model type from the sub-industry, then applies Claude's re-scores (data/<u>/v4_1_rescore.csv: id, code,
value, note) and the analyst estimates for banks / insurers / holding companies (data/<u>/v4_1_fin_estimates.csv).

    python3 migrate_v4_1.py            # refuses if inputs.csv is already v4.1
    python3 migrate_v4_1.py --force    # redo from backups/v4.0
"""
from __future__ import annotations

import argparse
import shutil
import sys

from screener.data import (DATA_DIR, FIN_FIELDS, HOLD_FIELDS, input_fields, load_universe, read_csv, write_csv)

FILES = ("inputs.csv", "financials.csv", "holdings.csv", "prescreen.csv", "universe.json")
EST = ("cet1", "solvency", "combined_ratio", "nav_m", "nav_cagr", "ltv")
NOTE_TAG = "v4.1:"


def rule_type(sub: str) -> str:
    if "Insurance Brokers" in sub:
        return "Operating"
    if "Insurance" in sub or "Reinsurance" in sub:
        return "Insurer"
    if any(k in sub for k in ("Diversified Banks", "Regional Banks", "Consumer Finance", "Investment Banking",
                              "Diversified Financial")):
        return "Bank"
    return "Holding" if "Multi-Sector" in sub else "Operating"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for key in ("us", "eu"):
        d = DATA_DIR / key
        bak = d / "backups" / "v4.0"
        header = (d / "inputs.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
        if "0.0" in header:
            if not a.force:
                sys.exit(f"{d}/inputs.csv is already v4.1 — use --force to redo from backups/v4.0.")
        else:
            bak.mkdir(parents=True, exist_ok=True)
            for f in FILES:
                if (d / f).exists():
                    shutil.copy2(d / f, bak / f)
        meta = load_universe(key)
        rows = read_csv(bak / "inputs.csv")
        by_id = {r["id"]: r for r in rows}
        for r in rows:
            r["0.0"] = rule_type(r.get("sub_industry") or "")
            r["note_v4"] = r.get("note_v4")
        changed = 0
        for x in read_csv(d / "v4_1_rescore.csv"):
            x["code"] = str(x["code"])                 # read_csv parses codes like "0.1" / "2.3" as numbers
            r = by_id.get(x["id"])
            if r is None:
                continue
            if x["code"] == "note":
                r["note_v4"] = " | ".join(t for t in (r.get("note_v4"), x.get("note")) if t)
                continue
            if x.get("value") is not None and r.get(x["code"]) != x["value"]:
                changed += 1
                r[x["code"]] = x["value"]
            if x.get("note"):
                r["note_v4"] = " | ".join(t for t in (r.get("note_v4"), f"{NOTE_TAG} {x['code']}: {x['note']}") if t)
        write_csv(d / "inputs.csv", input_fields(meta), rows)

        fins = {f["id"]: f for f in read_csv(bak / "financials.csv")}
        n_est = 0
        for e in read_csv(d / "v4_1_fin_estimates.csv"):
            f = fins.setdefault(e["id"], {"id": e["id"]})
            for k in EST:
                if e.get(k) is not None:
                    f[k] = e[k]
                    n_est += 1
            if e.get("fin_note"):
                tag = f"{e['fin_note']} (conf {e.get('conf') or '?'})"
                f["fin_note"] = " | ".join(t for t in (tag, f.get("fin_note")) if t)
        write_csv(d / "financials.csv", FIN_FIELDS, [fins.get(c["id"], {"id": c["id"]}) for c in rows])
        write_csv(d / "holdings.csv", HOLD_FIELDS, read_csv(bak / "holdings.csv"))
        print(f"{key}: {len(rows)} companies -> v4.1 inputs ({changed} re-scored values), {n_est} financial estimates")


if __name__ == "__main__":
    main()
