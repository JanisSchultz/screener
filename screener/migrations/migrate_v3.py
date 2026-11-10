"""One-time migration: v2 data (data/<u>/backups/v2/) -> v3 data files.

Carries the 12 v2 criteria that map onto the v3 framework, leaves new fields blank for pre-scoring,
moves ROIC into financials.csv and creates empty Phase 4–5 templates.

    python3 migrate_v3.py            # refuses if inputs.csv is already v3
    python3 migrate_v3.py --force
"""
from __future__ import annotations

import argparse
import json
import sys

from screener import config as C
from screener.data import (BENCH_FIELDS, DATA_DIR, FIN_FIELDS, HOLD_FIELDS, OVERRIDE_FIELDS, PRESCREEN_FIELDS,
                           TECH_FIELDS, input_fields, read_csv, write_csv)

YAHOO_SUFFIX = {"London Stock Exchange": ".L", "Xetra": ".DE", "Euronext Paris": ".PA", "SIX Swiss Exchange": ".SW",
                "Nasdaq Stockholm": ".ST", "Borsa Italiana": ".MI", "Euronext Amsterdam": ".AS",
                "Bolsa de Madrid": ".MC", "Nasdaq Copenhagen": ".CO", "Oslo Børs": ".OL", "Nasdaq Helsinki": ".HE",
                "Warsaw SE": ".WA", "Euronext Brussels": ".BR", "Athens SE": ".AT", "Wiener Börse": ".VI",
                "Euronext Dublin": ".IR", "Euronext Lisbon": ".LS"}

V3_NOTE = ("v3: Phases 1–3 replace the v2 pillars. Twelve v2 criteria were carried over unchanged (see 'Carried from' "
           "on Methodology); the 16 new v3 fields were pre-scored by Claude from public knowledge as of "
           "November 2026, sub-industry baseline first, then company-specific adjustment — see 'Confidence v3' and "
           "'v3 note' on Inputs. Pre-Screen inputs are the investor's own and default to 'in circle'.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for key in ("us", "eu"):
        d = DATA_DIR / key
        src = d / "backups" / "v2"
        cur = (d / "inputs.csv").read_text(encoding="utf-8").splitlines()[0]
        if "1.1a" in cur.split(",") and not a.force:
            sys.exit(f"{d}/inputs.csv is already v3 — use --force to redo from backups/v2.")
        meta = json.loads((src / "universe.json").read_text(encoding="utf-8"))
        old = read_csv(src / "inputs.csv")

        meta.pop("metric_columns", None)
        meta.pop("roic_note", None)
        meta["how_produced"] = [t for t in meta["how_produced"]
                                if not t.startswith("4. The 'Ref:'") and not t.startswith("4. Pillar 5")] + [V3_NOTE]
        if key == "us":
            meta["benchmark_symbols"] = {"MARKET": "SPY", **C.US_SECTOR_ETFS}
            meta["symbol_rule"] = "us"
        else:
            meta["benchmark_symbols"] = {"MARKET": "EXSA.DE"}
            meta["symbol_rule"] = "eu"
            meta["yahoo_suffix"] = YAHOO_SUFFIX
        meta["fx_note"] = ("Financial statement values are in the reporting currency; market cap is converted into "
                           "that currency by the fetcher so yields are like-for-like.")

        rows, fins = [], []
        for o in old:
            r = {k: o.get(k) for k in ["id", "ticker", "company", "country", "sector", "sub_industry"]}
            for x in meta.get("extra_columns", []):
                r[x["key"]] = o.get(x["key"])
            for f in C.FIELDS:
                if f["legacy"] == "moat":
                    r[f["code"]] = o.get("moat")
                elif f["legacy"]:
                    r[f["code"]] = o.get(f["legacy"])
            r.update(confidence=o.get("confidence"), note=o.get("note"), evidence=o.get("evidence"),
                     last_reviewed=o.get("last_reviewed"))
            rows.append(r)
            fin = {"id": o["id"]}
            if o.get("roic_10y") is not None:
                fin.update(roic_median=o["roic_10y"], source="v1 workbook (10Y avg ROIC; source undocumented)")
            if o.get("rev_cagr") is not None:
                fin["cagr_sales_10"] = o["rev_cagr"]
                fin["source"] = (fin.get("source", "v1 workbook") + "; sales CAGR FY15–25 from v1 EDGAR ref")
            if o.get("roic_judgement"):
                fin.update(roic_judgement=o["roic_judgement"], source="v1 workbook (ROIC Pass/Fail judgement)")
            fins.append(fin)

        subs = sorted({(r["sector"], r["sub_industry"]) for r in rows})
        (d / "universe.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        write_csv(d / "inputs.csv", input_fields(meta), rows)
        write_csv(d / "financials.csv", FIN_FIELDS, fins)
        write_csv(d / "prescreen.csv", PRESCREEN_FIELDS,
                  [{"sector": s, "sub_industry": u, "in_circle": "Y"} for s, u in subs])
        for name, fields in (("technicals.csv", TECH_FIELDS), ("benchmarks.csv", BENCH_FIELDS),
                             ("holdings.csv", HOLD_FIELDS), ("overrides.csv", OVERRIDE_FIELDS)):
            write_csv(d / name, fields, [])
        print(f"{key}: {len(rows)} companies, {len(subs)} sub-industries -> v3 data files")


if __name__ == "__main__":
    main()
