"""Pull edits made in a built workbook back into data/<universe>/ so the next build keeps them.

Synced: Inputs (all Phase 1–3 inputs), Overrides, Pre-Screen (circle of competence), Holdings, Financials
(all columns, incl. analyst g / g_moat), Methodology parameter values (stored as universe-specific values in
universe.json when they differ from screener/config.py). Previous data files are backed up first.

    python3 sync_from_excel.py us                    # from the latest output/ version
    python3 sync_from_excel.py eu path/to/file.xlsx  # from a specific workbook
    python3 sync_from_excel.py us --dry-run          # show what would change
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import openpyxl

from screener import config as C
from screener.data import (DATA_DIR, FIN_COLUMNS, HOLD_COLUMNS, OVERRIDE_FIELDS, PRESCREEN_FIELDS, input_fields,
                           latest_output, load_universe, write_csv)
from screener.workbook import Builder


def cell(v):
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return None if v == "" else v


def table(ws, header_row, first_row, keys_by_title, max_col=None):
    keys = [keys_by_title.get(c.value) for c in ws[header_row]][:max_col]
    out = []
    for row in ws.iter_rows(min_row=first_row, max_col=max_col, values_only=True):
        if row[0] in (None, ""):
            continue
        out.append({k: cell(v) for k, v in zip(keys, row) if k})
    return keys, out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("universe")
    ap.add_argument("workbook", nargs="?")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    meta = load_universe(a.universe)
    path = Path(a.workbook) if a.workbook else latest_output(meta["file_stem"])
    if not path or not path.exists():
        sys.exit("No workbook found to sync from.")
    wb = openpyxl.load_workbook(path)           # input cells hold values; formulas are not needed

    fields = input_fields(meta)
    keys, companies = table(wb["Inputs"], 1, 2, {t: k for k, t, *_ in Builder(meta, "x").input_columns()})
    missing = set(fields) - {k for k in keys if k}
    if missing:
        sys.exit(f"Inputs sheet is missing columns: {sorted(missing)}")
    _, overrides = table(wb["Overrides"], 4, 5, dict(zip(
        ["Company ID", "Criterion code", "New score (0/1/2)", "Reason / evidence", "Analyst", "Date"], OVERRIDE_FIELDS)), 6)
    _, prescreen = table(wb["Pre-Screen"], 4, 5, dict(zip(["GICS Sector", "GICS Sub-Industry", "In circle (Y/N)", "Note"],
                                                          PRESCREEN_FIELDS)), 4)
    _, holdings = table(wb["Holdings"], 4, 5, {t: k for k, t, *_ in HOLD_COLUMNS}, len(HOLD_COLUMNS))
    holdings = [h for h in holdings if h.get("id")]
    _, fins = table(wb["Financials"], 1, 2, {t: k for k, t, *_ in FIN_COLUMNS}, len(FIN_COLUMNS))

    defaults = {nm: val for _, ps in C.PARAMETER_GROUPS for nm, _, val, _, _ in ps}
    params = {}
    ws = wb["Methodology"]
    for r in range(1, ws.max_row + 1):
        nm = ws.cell(r, 3).value
        if nm in defaults:
            v = cell(ws.cell(r, 2).value)
            if v is not None and abs(float(v) - float(defaults[nm])) > 1e-12:
                params[nm] = v

    old = {c["id"]: c for c in meta["companies"]}
    norm = lambda v: None if v in ("", None) else v
    changed = [c["id"] for c in companies if c["id"] in old and any(norm(c.get(k)) != norm(old[c["id"]].get(k)) for k in fields)]
    print(f"From {path.name}:")
    print(f"  companies: {len(companies)} ({len(changed)} changed, "
          f"{len([c for c in companies if c['id'] not in old])} added, {len(set(old) - {c['id'] for c in companies})} removed)")
    for i in changed[:20]:
        print("   ~", i)
    print(f"  overrides: {len(meta['overrides'])} -> {len(overrides)};  holdings: {len(meta['holdings'])} -> {len(holdings)}")
    print(f"  pre-screen 'N' sub-industries: {sum(p.get('in_circle') == 'N' for p in prescreen)};  "
          f"financial rows with data: {sum(1 for f in fins if f.get('market_cap_m') is not None)}")
    print(f"  universe-specific parameters: {meta.get('parameters', {})} -> {params}")
    if a.dry_run:
        return

    d = DATA_DIR / a.universe
    backup = d / "backups" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup.mkdir(parents=True)
    for f in ("inputs.csv", "overrides.csv", "prescreen.csv", "holdings.csv", "financials.csv", "universe.json"):
        if (d / f).exists():
            shutil.copy2(d / f, backup / f)
    write_csv(d / "inputs.csv", fields, companies)
    write_csv(d / "overrides.csv", OVERRIDE_FIELDS, overrides)
    write_csv(d / "prescreen.csv", PRESCREEN_FIELDS, prescreen)
    write_csv(d / "holdings.csv", [k for k, *_ in HOLD_COLUMNS], holdings)
    write_csv(d / "financials.csv", [k for k, *_ in FIN_COLUMNS], fins)
    uj = json.loads((d / "universe.json").read_text(encoding="utf-8"))
    if params:
        uj["parameters"] = params
    else:
        uj.pop("parameters", None)
    (d / "universe.json").write_text(json.dumps(uj, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Synced. Backup of previous data: {backup.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
