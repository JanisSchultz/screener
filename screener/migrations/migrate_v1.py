"""One-time migration: v1 workbooks -> data/<universe>/ CSV + JSON source files.

    python migrate_v1.py            # refuses to overwrite existing data/
    python migrate_v1.py --force

The v1 workbooks are only read, never modified.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import openpyxl

from screener.data import DATA_DIR, OVERRIDE_FIELDS, ROOT, input_fields, write_csv

V1_US = ROOT / "Quality & Moat Screen – Nasdaq-100 ∪ S&P 500 (as of 2026-10-31) (1).xlsx"
V1_EU = ROOT / "Quality & Moat Screen – STOXX Europe 600 (as of 2026-10-31) (1).xlsx"

# v1 Screen columns holding the 20 criterion inputs, in config.CRITERIA order
V1_SCORE_COLS = ["H", "I", "J", "K", "N", "O", "P", "Q", "T", "U", "V", "W",
                 "Z", "AA", "AB", "AC", "AD", "AE", "AI", "AJ"]

ISO2 = {"Austria": "AT", "Belgium": "BE", "Denmark": "DK", "Finland": "FI", "France": "FR",
        "Germany": "DE", "Greece": "GR", "Ireland": "IE", "Italy": "IT", "Netherlands": "NL",
        "Norway": "NO", "Poland": "PL", "Portugal": "PT", "Spain": "ES", "Sweden": "SE",
        "Switzerland": "CH", "United Kingdom": "GB"}

# v1 US rationales end with an auto-generated weak-point list; v2 computes it live.
AUTO_SUFFIX = re.compile(r"\s*(Weak points \(0\):.*|No criterion scored 0;.*)$")


def scores(ws, r):
    return {code: int(ws[f"{col}{r}"].value)
            for code, col in zip(input_codes(), V1_SCORE_COLS)}


def input_codes():
    from screener.config import CRITERIA
    return [c[0] for c in CRITERIA]


def methodology_text(ws):
    """Pull the free-text blocks out of a v1 Methodology sheet."""
    rows = [(c.row, c.value) for c in ws["A"] if isinstance(c.value, str)]
    get = lambda prefix: next(v for _, v in rows if v.startswith(prefix))
    how_start = next(r for r, v in rows if v == "How the scores were produced")
    how = [v for r, v in rows if r > how_start and not v.startswith("Sources:")]
    return {
        "universe_text": get("Universe as of"),
        "caveat": get("CAVEAT"),
        "how_produced": how,
        "sources": get("Sources:"),
    }


def migrate_us():
    wb = openpyxl.load_workbook(V1_US, data_only=True)
    ws = wb["Screen"]
    meta = {
        "title": "Quality & Moat Screen — Nasdaq-100 ∪ S&P 500 constituents",
        "file_stem": "Quality & Moat Screen – Nasdaq-100 ∪ S&P 500 (as of 2026-10-31)",
        "as_of": "2026-10-31",
        "show_country": False,
        "extra_columns": [
            {"key": "in_sp500", "header": "In S&P 500", "fmt": "@", "width": 9, "validation": ["Y", "N"]},
            {"key": "in_ndx", "header": "In Nasdaq-100", "fmt": "@", "width": 9, "validation": ["Y", "N"]},
        ],
        "metric_columns": [
            {"key": "rev_cagr", "header": "Ref: Revenue CAGR FY15–25 (EDGAR)", "fmt": "0.0%", "width": 11},
            {"key": "ni_down_years", "header": "Ref: Net-income down-years", "fmt": "0", "width": 9},
            {"key": "ni_years", "header": "Ref: Net-income years compared", "fmt": "0", "width": 9},
            {"key": "gm_range_pp", "header": "Ref: Gross-margin range (pp)", "fmt": "0.0", "width": 10},
            {"key": "inv_minus_rev_pp", "header": "Ref: Inventory − revenue growth (pp/yr)", "fmt": "0.0", "width": 11},
        ],
        "breakdowns": [
            {"title": "GICS sector", "field": "sector"},
            {"title": "Index membership", "flags": [
                ["Both", {"in_sp500": "Y", "in_ndx": "Y"}],
                ["S&P 500 only", {"in_sp500": "Y", "in_ndx": "N"}],
                ["Nasdaq-100 only", {"in_sp500": "N", "in_ndx": "Y"}],
            ]},
        ],
        "roic_note": "10Y Avg ROIC carried over from v1 ('Ref: 10Y Avg ROIC'); v1 did not document its source.",
    }
    meta.update(methodology_text(wb["Methodology"]))
    meta["how_produced"] = [
        re.sub(r"Columns AT–AW are reference figures only \(they do not feed any score\)",
               "The 'Ref:' metric columns on Inputs do not feed any score; since v2 they drive the "
               "P5 data check on Screen, which flags disagreement for review. Data", t)
        if t.startswith("4.") else
        ("5. Rationale = short analyst note. Since v2 the list of criteria scored 0 is computed "
         "live on Screen ('Weak points') instead of being typed into the note." if t.startswith("5.") else t)
        for t in meta["how_produced"]]

    rows = []
    for r in range(2, ws.max_row + 1):
        if not ws[f"A{r}"].value:
            continue
        ticker = ws[f"A{r}"].value
        ni = ws[f"AU{r}"].value
        m = re.fullmatch(r"(\d+) of (\d+)", str(ni or ""))
        num = lambda v: v if isinstance(v, (int, float)) else None
        row = {
            "id": ticker.split(" / ")[0].strip(), "ticker": ticker, "company": ws[f"B{r}"].value,
            "country": "United States", "sector": ws[f"C{r}"].value, "sub_industry": ws[f"D{r}"].value,
            "in_sp500": ws[f"E{r}"].value, "in_ndx": ws[f"F{r}"].value,
            "confidence": ws[f"AS{r}"].value, "roic_10y": num(ws[f"AX{r}"].value), "roic_judgement": None,
            "moat": ws[f"AQ{r}"].value, "note": AUTO_SUFFIX.sub("", ws[f"AR{r}"].value or ""),
            "rev_cagr": num(ws[f"AT{r}"].value),
            "ni_down_years": int(m.group(1)) if m else None, "ni_years": int(m.group(2)) if m else None,
            "gm_range_pp": num(ws[f"AV{r}"].value), "inv_minus_rev_pp": num(ws[f"AW{r}"].value),
        }
        row.update(scores(ws, r))
        rows.append(row)
    return meta, rows, None


def migrate_eu():
    wb = openpyxl.load_workbook(V1_EU, data_only=True)
    ws = wb["Screen"]
    meta = {
        "title": "Quality & Moat Screen — STOXX Europe 600 constituents",
        "file_stem": "Quality & Moat Screen – STOXX Europe 600 (as of 2026-10-31)",
        "as_of": "2026-10-31",
        "show_country": True,
        "extra_columns": [
            {"key": "exchange", "header": "Listing exchange", "fmt": "@", "width": 18},
            {"key": "index_weight_pct", "header": "Index weight (%) in EXSA, 29 Oct 2026", "fmt": "0.00", "width": 11},
        ],
        "metric_columns": [],
        "breakdowns": [
            {"title": "GICS sector (mapped)", "field": "sector"},
            {"title": "Country", "field": "country"},
        ],
        "roic_note": "No numeric ROIC in v1: the Pass/Fail ROIC judgement is carried over from v1 "
                     "('Phase 3 ROIC Hurdle'). Enter a numeric 10Y Avg ROIC to override the judgement.",
    }
    meta.update(methodology_text(wb["Methodology"]))
    meta["how_produced"] = [
        t + " Since v2, analyst re-evaluations are logged criterion by criterion on the Overrides sheet; "
            "the 8 pre-v2 re-evaluations are kept on 'Re-evaluation history' (their pre-change "
            "criterion scores were not preserved in v1, so they stay baked into the base scores)."
        if t.startswith("5.") else t for t in meta["how_produced"]]

    rows = []
    for r in range(2, ws.max_row + 1):
        if not ws[f"A{r}"].value:
            continue
        country = ws[f"C{r}"].value
        judg = ws[f"AT{r}"].value
        row = {
            "id": f"{ws[f'A{r}'].value}.{ISO2[country]}", "ticker": ws[f"A{r}"].value,
            "company": ws[f"B{r}"].value, "country": country, "sector": ws[f"D{r}"].value,
            "sub_industry": ws[f"E{r}"].value, "exchange": ws[f"F{r}"].value,
            "index_weight_pct": ws[f"G{r}"].value, "confidence": ws[f"AS{r}"].value,
            "roic_10y": None, "roic_judgement": judg if judg in ("Pass", "Fail") else None,
            "moat": ws[f"AQ{r}"].value, "note": ws[f"AR{r}"].value,
        }
        row.update(scores(ws, r))
        rows.append(row)

    by_ticker = {}
    for row in rows:
        by_ticker.setdefault(row["ticker"], []).append(row["id"])
    rv = wb["Re-evaluations"]
    hdr = [c.value for c in rv[1]]
    reeval = []
    for vals in rv.iter_rows(min_row=2, values_only=True):
        if vals[0]:
            d = dict(zip(hdr, vals))
            d = {"id": by_ticker[vals[0]][0], **d}
            reeval.append(d)
    return meta, rows, (["id"] + hdr, reeval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for key, fn in (("us", migrate_us), ("eu", migrate_eu)):
        d = DATA_DIR / key
        if (d / "inputs.csv").exists() and not a.force:
            sys.exit(f"{d} already has data — use --force to overwrite.")
        meta, rows, reeval = fn()
        d.mkdir(parents=True, exist_ok=True)
        (d / "universe.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        write_csv(d / "inputs.csv", input_fields(meta), rows)
        if not (d / "overrides.csv").exists() or a.force:
            write_csv(d / "overrides.csv", OVERRIDE_FIELDS, [])
        if reeval:
            write_csv(d / "reevaluations.csv", *reeval)
        print(f"{key}: {len(rows)} companies -> {d}")


if __name__ == "__main__":
    main()
