"""Pull edits made in a built workbook back into data/<universe>/ so the next build keeps them.

Synced: Qualitative (all Phase 1–3 inputs), Pre-Screen (Gate 6 sub-industry defaults and your markets), Quantitative
(all financial columns, incl. Peak EPS / Implied g / My overrides), and Methodology parameter values and their change log
(stored in universe.json; parameters only when they differ from screener/config.py). Previous data files are backed up first.

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

user_site = Path.home() / "Library/Python/3.9/lib/python/site-packages"
if user_site.exists() and str(user_site) not in sys.path:
    sys.path.insert(0, str(user_site))

import openpyxl

from screener import config as C
from screener.data import (DATA_DIR, FIN_COLUMNS, MARKET_FIELDS, PRESCREEN_FIELDS, input_fields,
                           latest_output, load_universe, write_csv)


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
    q_ws = wb["Qualitative"]
    q_map = {
        "ID (unique)": "id", "Ticker": "ticker", "Company": "company", "Country": "country",
        "GICS Sector": "sector", "GICS Sub-Industry": "sub_industry",
        "1. Simple to Understand (gate)": "1", "2. Essential Western Need (override)": "2",
        "2r. Essential Need / Risk reason": "2r",
        "3a. Moat Archetype": "3a", "3b. Pricing >= Inflation (gate)": "3b", "3m. Moat & erosion note": "3m",
        "4. Runway — CAP (yrs)": "4",
        "5. Management & Capital Allocation (0/1/2)": "5",
        "6. Peak Compounding & Fortress Balance Sheet (input)": "6",
        # Backward compatibility with pre-v6.21 workbooks
        "3. Runway — CAP (yrs)": "4",
        "4a. Moat Archetype": "3a", "4b. Pricing >= Inflation (gate)": "3b", "4m. Moat & erosion note": "3m",
        "Qualitative note": "note", "Key evidence / sources": "evidence",
    }
    for c in meta.get("extra_columns", []):
        q_map[c["header"]] = c["key"]
    keys, companies = table(q_ws, 1, 2, q_map)
    missing = set(fields) - {k for k in keys if k}
    if missing:
        sys.exit(f"Qualitative sheet is missing columns: {sorted(missing)}")
    _, prescreen = table(wb["Pre-Screen"], 4, 5, dict(zip(["GICS Sector", "GICS Sub-Industry", "Gate 6 default (N / blank)", "Note"],
                                                          PRESCREEN_FIELDS)), 4)
    ps = wb["Pre-Screen"]
    markets = [{"country": cell(ps.cell(r, 7).value), "in_market": cell(ps.cell(r, 8).value) or "Y"}
               for r in range(5, ps.max_row + 1) if ps.cell(r, 7).value not in (None, "")]
    v_ws = wb["Quantitative"]
    v_map = {t: k for k, t, *_ in FIN_COLUMNS}
    v_map.update({
        "Quote ccy": "quote_currency", "Peak EPS year": "peak_oe_year", "Last Peak Owner EPS": "peak_oe_eps",
        "My Peak EPS (override)": "peak_eps_est", "Share price": "price", "Cycle low multiple (5Y)": "mult_low_5y",
        "Cycle high multiple (5Y)": "mult_high_5y", "Cycle Owner EPS growth (g)": "cagr_oe_eps",
        "Implied Owner EPS g (5–10Y)": "g_implied", "My growth g (override)": "g_est", "Median ROIC 5Y (GAAP)": "roic_median",
        "Operating ROIC 5Y (Tangible)": "roic_operating", "My ROIC (override)": "roic_est",
        "New peak vs prior cycle (Y/N)": "p2p_ok", "Cash (m)": "cash_m",
        "Cash conversion (FCF ÷ NI)": "fcf_conv",
        "Analyst note": "fin_note", "Market cap (m, rep ccy)": "market_cap_m",
        "D&A latest FY (m)": "da_ttm_m", "CapEx latest FY (m)": "capex_ttm_m",
        "Dividends latest FY (m)": "dividends_ttm_m", "Interest expense (m)": "interest_m",
    })
    _, fins = table(v_ws, 1, 2, v_map)
    for f_row, c_row in zip(fins, companies):
        f_row["id"] = c_row["id"]

    defaults = {nm: val for _, ps in C.PARAMETER_GROUPS for nm, _, val, _, _ in ps}
    params, plog = {}, {}
    ws = wb["Methodology"]
    for r in range(1, ws.max_row + 1):
        nm = ws.cell(r, 3).value
        if nm in defaults:
            v = cell(ws.cell(r, 2).value)
            if v is not None and abs(float(v) - float(defaults[nm])) > 1e-12:
                params[nm] = v
            when, why = cell(ws.cell(r, 5).value), cell(ws.cell(r, 6).value)
            if when or why:
                plog[nm] = {"date": when, "reason": why}

    old = {c["id"]: c for c in meta["companies"]}
    norm = lambda v: None if v in ("", None) else v
    changed = [c["id"] for c in companies if c["id"] in old and any(norm(c.get(k)) != norm(old[c["id"]].get(k)) for k in fields)]
    print(f"From {path.name}:")
    print(f"  companies: {len(companies)} ({len(changed)} changed, "
          f"{len([c for c in companies if c['id'] not in old])} added, {len(set(old) - {c['id'] for c in companies})} removed)")
    for i in changed[:20]:
        print("   ~", i)
    print(f"  markets marked N: {[x['country'] for x in markets if x['in_market'] == 'N']}")
    print(f"  pre-screen Gate 6 'N' sub-industries: {sum(p.get('g6_default') == 'N' for p in prescreen)};  "
          f"financial rows with data: {sum(1 for f in fins if f.get('market_cap_m') is not None)}")
    print(f"  universe-specific parameters: {meta.get('parameters', {})} -> {params}")
    print(f"  parameter log entries: {len(meta.get('parameter_log', {}))} -> {len(plog)}")
    unlogged = sorted(nm for nm in params if not (plog.get(nm) or {}).get("reason"))
    if unlogged:
        print(f"  WARNING: changed parameters without a logged reason: {unlogged}")
    if a.dry_run:
        return

    d = DATA_DIR / a.universe
    backup = d / "backups" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup.mkdir(parents=True)
    for f in ("inputs.csv", "prescreen.csv", "markets.csv", "financials.csv", "universe.json"):
        if (d / f).exists():
            shutil.copy2(d / f, backup / f)
    write_csv(d / "inputs.csv", fields, companies)
    write_csv(d / "prescreen.csv", PRESCREEN_FIELDS, prescreen)
    write_csv(d / "markets.csv", MARKET_FIELDS, markets)
    write_csv(d / "financials.csv", [k for k, *_ in FIN_COLUMNS], fins)
    uj = json.loads((d / "universe.json").read_text(encoding="utf-8"))
    for k, val in (("parameters", params), ("parameter_log", plog)):
        if val:
            uj[k] = val
        else:
            uj.pop(k, None)
    (d / "universe.json").write_text(json.dumps(uj, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Synced. Backup of previous data: {backup.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
