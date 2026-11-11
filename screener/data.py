"""Source data schema and CSV/JSON loading/saving (data/<universe>/)."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from .config import FIELDS

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DOCS_DIR = ROOT / "docs"

# ------------------------------------------------------------------ schema
BASE_FIELDS = ["id", "ticker", "company", "country", "sector", "sub_industry"]
QUAL_CODES = [f["code"] for f in FIELDS]
TAIL_FIELDS = ["calamity", "calamity_note", "note", "evidence"]
PRESCREEN_FIELDS = ["sector", "sub_industry", "g6_default", "note"]
MARKET_FIELDS = ["country", "in_market"]

# (key, header, number format, width). Money in millions of the *reporting* currency; market cap converted
# into that currency so yields are like-for-like. Ratios as fractions (0.15 = 15%).
FIN_COLUMNS = [
    ("id", "ID", "@", 11), ("fin_currency", "Reporting currency", "@", 8), ("as_of", "Data as of", "@", 11),
    ("source", "Source", "@", 16),
    ("price", "Share price (quote ccy)", "#,##0.00", 10), ("quote_currency", "Quote ccy", "@", 6),
    ("market_cap_m", "Market cap (m, reporting ccy)", "#,##0", 12),
    ("sales_ttm_m", "Revenue latest FY (m)", "#,##0", 11),
    ("ni_ttm_m", "Net income latest FY (m)", "#,##0", 11),
    ("capex_ttm_m", "CapEx latest FY (m, positive)", "#,##0", 10),
    ("da_ttm_m", "Depreciation & amortisation latest FY (m)", "#,##0", 10),
    ("dividends_ttm_m", "Dividends paid latest FY (m)", "#,##0", 10),
    ("lt_debt_m", "Long-term debt (m)", "#,##0", 10),
    ("cash_m", "Cash (m)", "#,##0", 10),
    ("interest_m", "Interest expense latest FY (m)", "#,##0", 10),
    ("ebit_ttm_m", "EBIT latest FY (m)", "#,##0", 10),
    ("roic_median", "Median ROIC 5y (GAAP, incl. goodwill)", "0.0%", 9),
    ("roic_operating", "Median Operating ROIC 5y (Tangible)", "0.0%", 9),
    ("fcf_conv", "Owner FCF ÷ NI (multi-yr)", "0%", 9),
    ("peak_oe_year", "Peak Owner EPS year", "0", 8),
    ("peak_oe_eps", "Last peak Owner EPS (quote ccy)", "#,##0.00", 11),
    ("mult_low_5y", "Cycle low multiple (5y)", "0.0", 9),
    ("mult_high_5y", "Cycle high multiple (5y)", "0.0", 9),
    ("cagr_oe_eps", "Cycle Owner EPS CAGR (g)", "0.0%", 9),
    ("p2p_ok", "New peak vs prior cycle (Y/N)", "@", 7),
    ("sales_1y", "Sales growth (1y YoY)", "0.0%", 9),
    ("sales_cagr", "Sales CAGR (3–5y)", "0.0%", 9),
    ("sales_cagr_yrs", "Sales CAGR window (yrs)", "0", 7),
    ("opcost_1y", "Operating cost growth (1y YoY)", "0.0%", 9),
    ("opcost_cagr", "Operating cost CAGR (3–5y)", "0.0%", 9),
    ("cap_growth", "Operating capital growth (5y med)", "0.0%", 9),
    ("buyback_yield", "Net buyback / dilution yield (3–5y)", "0.0%", 9),
    ("retention_rate", "5y earnings retention (1 − div/NI)", "0.0%", 9),
    ("roiic", "Incremental ROIC (3–5y ΔNOPAT/ΔIC)", "0.0%", 9),
    ("g_implied", "Implied Owner EPS g (5–10y)", "0.0%", 10),
    ("peak_eps_est", "My Peak EPS (blank = reported)", "#,##0.00", 10),
    ("g_est", "My growth g (blank = cycle CAGR)", "0.0%", 10),
    ("roic_est", "My ROIC (blank = operating ROIC)", "0.0%", 10),
    ("fin_note", "Note", "@", 30),
]
TECH_COLUMNS = [
    ("id", "ID", "@", 11), ("symbol", "Price symbol", "@", 11), ("as_of", "As of (week)", "@", 11),
    ("price", "Weekly close", "#,##0.00", 10), ("ma30", "30-wk MA", "#,##0.00", 10),
    ("ma30_prev", "30-wk MA 5 wks ago", "#,##0.00", 10), ("high_52w", "52-wk high", "#,##0.00", 10),
    ("vol_ratio", "Volume ÷ 10-wk avg", "0.00", 8), ("rs_52w", "52-wk return vs market", "0.0%", 9),
    ("tech_note", "Note", "@", 20),
]
BENCH_COLUMNS = [
    ("name", "Benchmark (MARKET or sector)", "@", 24), ("symbol", "Symbol", "@", 10), ("as_of", "As of", "@", 11),
    ("price", "Weekly close", "#,##0.00", 10), ("ma30", "30-wk MA", "#,##0.00", 10),
    ("ma30_prev", "30-wk MA 5 wks ago", "#,##0.00", 10), ("high_52w", "52-wk high", "#,##0.00", 10),
]
FIN_FIELDS = [c[0] for c in FIN_COLUMNS]
TECH_FIELDS = [c[0] for c in TECH_COLUMNS]
BENCH_FIELDS = [c[0] for c in BENCH_COLUMNS]


def universe_keys() -> list[str]:
    return sorted(p.name for p in DATA_DIR.iterdir() if (p / "universe.json").exists())


def load_universe(key: str) -> dict:
    d = DATA_DIR / key
    meta = json.loads((d / "universe.json").read_text(encoding="utf-8"))
    meta["key"] = key
    meta["companies"] = read_csv(d / "inputs.csv")
    opt = lambda name: read_csv(d / name) if (d / name).exists() else []
    meta["prescreen"] = opt("prescreen.csv")
    meta["markets"] = opt("markets.csv")
    meta["financials"] = {r["id"]: r for r in opt("financials.csv")}
    meta["technicals"] = {r["id"]: r for r in opt("technicals.csv")}
    meta["benchmarks"] = opt("benchmarks.csv")
    meta["holdings"] = opt("holdings.csv")
    meta["reevaluations"] = opt("reevaluations.csv") or None
    return meta


def input_fields(meta: dict) -> list[str]:
    return BASE_FIELDS + [c["key"] for c in meta.get("extra_columns", [])] + QUAL_CODES + TAIL_FIELDS


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return [{k: _parse(v) for k, v in row.items()} for row in csv.DictReader(f)]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def _parse(v):
    """CSV text -> int/float where it looks numeric, None for blank, else str."""
    if v is None:
        return None
    v = v.strip()
    if v == "":
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d*\.\d+(e-?\d+)?|-?\d+e-?\d+", v, re.I):
        return float(v)
    return v
