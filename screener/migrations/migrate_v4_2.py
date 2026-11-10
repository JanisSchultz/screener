"""One-time migration: v4.1 data -> v4.2 ("sure and simple").

Backs up data/<u>/ to data/<u>/backups/v4.1/ and
  * replaces the six moat scores by one 'Primary moat' and caps CAP at 5 where no moat scored 2 (the old moat gate),
  * folds 1.1 Geopolitics into Gate 2 and sets Gate 2 = N for businesses that live outside your markets,
  * writes markets.csv (your markets by listing country),
  * merges confidence (worst of v3 / v4) and notes, and drops the removed fields.

    python3 migrate_v4_2.py            # refuses if inputs.csv is already v4.2
    python3 migrate_v4_2.py --force    # redo from backups/v4.1
"""
from __future__ import annotations

import argparse
import shutil
import sys

from screener import config as C
from screener.data import DATA_DIR, MARKET_FIELDS, input_fields, load_universe, read_csv, write_csv

FILES = ("inputs.csv", "financials.csv", "holdings.csv", "prescreen.csv", "universe.json")
MOATS = [("3.2a", "Switching costs"), ("3.2b", "Scale economies"), ("3.2c", "Network effects"),
         ("3.2d", "Physical assets"), ("3.2e", "Intangibles"), ("3.2f", "Counter-positioning / process")]
YOUR_MARKETS = {"United States", "Sweden", "Norway", "Denmark", "Finland", "Germany", "United Kingdom", "France", "Italy",
                "Spain", "Switzerland", "Austria", "Netherlands", "Belgium", "Ireland", "Portugal"}
# London-listed businesses whose assets / customers sit mainly in one emerging market (judgement, v4.2)
OUTSIDE = {"BGEO.GB": "Georgian bank (Lion Finance) — business outside your markets",
           "TBCG.GB": "Georgian bank (TBC) — business outside your markets",
           "AAF.GB": "Telecoms in sub-Saharan Africa — business outside your markets",
           "EDV.GB": "Gold mines in West Africa — business outside your markets",
           "PAF.GB": "Gold mines in South Africa — business outside your markets",
           "FRES.GB": "Silver / gold mines in Mexico — business outside your markets",
           "HOC.GB": "Precious-metal mines in Peru / Argentina — business outside your markets",
           "ANTO.GB": "Copper mines in Chile — business outside your markets"}
RANK = {"H": 0, "M": 1, "L": 2}


def num(v):
    return v if isinstance(v, (int, float)) else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for key in ("us", "eu"):
        d = DATA_DIR / key
        bak = d / "backups" / "v4.1"
        header = (d / "inputs.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
        if "3.3m" in header:
            if not a.force:
                sys.exit(f"{d}/inputs.csv is already v4.2 — use --force to redo from backups/v4.1.")
        else:
            bak.mkdir(parents=True, exist_ok=True)
            for f in FILES:
                if (d / f).exists():
                    shutil.copy2(d / f, bak / f)
        meta = load_universe(key)
        rows = read_csv(bak / "inputs.csv")
        capped = gate2 = 0
        for r in rows:
            scores = [(num(r.get(c)), name) for c, name in MOATS]
            best = max(s for s, _ in scores)
            r["3.2"] = next(name for s, name in scores if s == best) if best > 0 else "None"
            if best < 2 and num(r.get("3.3n")) > 5:
                r["3.3n"] = 5
                capped += 1
            r["3.3m"] = " | ".join(t for t in (r.get("3.2br"), r.get("3.3t")) if t) or None
            reason = None
            if r.get("1.1g") == "N":
                reason = "Customers mainly in sanctioned / pariah jurisdictions (former 1.1 Geopolitics gate)"
            if r["id"] in OUTSIDE:
                reason = OUTSIDE[r["id"]]
            if reason and r.get("0.2") != "N":
                r["0.2"], r["0.2r"] = "N", " | ".join(t for t in (r.get("0.2r"), reason) if t)
                gate2 += 1
            confs = [c for c in (r.get("confidence"), r.get("conf_v4")) if c in RANK]
            r["confidence"] = max(confs, key=RANK.get) if confs else None
            r["note"] = " | ".join(t for t in (r.get("note_v4"), r.get("note")) if t) or None
        write_csv(d / "inputs.csv", input_fields(meta), rows)
        countries = sorted({r["country"] for r in rows if r.get("country")})
        write_csv(d / "markets.csv", MARKET_FIELDS,
                  [{"country": c, "in_market": "Y" if c in YOUR_MARKETS else "N"} for c in countries])
        out = [c for c in countries if c not in YOUR_MARKETS]
        print(f"{key}: {len(rows)} companies -> v4.2 inputs; CAP capped at 5 for {capped}; Gate 2 set N for {gate2}; "
              f"markets N: {out}")
    _ = C  # config imported so input_fields() reflects the v4.2 field list


if __name__ == "__main__":
    main()
