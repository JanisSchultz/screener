"""Source data schema, loading/saving (data/<universe>/) and output versioning."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from .config import FIELDS

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

# ------------------------------------------------------------------ schema
BASE_FIELDS = ["id", "ticker", "company", "country", "sector", "sub_industry"]
QUAL_CODES = [f["code"] for f in FIELDS]
TAIL_FIELDS = ["confidence", "conf_v4", "note", "note_v4", "evidence", "last_reviewed", "reviewed"]
PRESCREEN_FIELDS = ["sector", "sub_industry", "sole_owner", "note"]

# (key, header, number format, width). Money in millions of the *reporting* currency; market cap converted
# into that currency so yields are like-for-like. Ratios as fractions (0.15 = 15%).
FIN_COLUMNS = [
    ("id", "ID", "@", 11), ("fin_currency", "Reporting currency", "@", 8), ("as_of", "Data as of", "@", 11),
    ("source", "Source", "@", 16),
    ("price", "Share price (quote ccy)", "#,##0.00", 10), ("quote_currency", "Quote ccy", "@", 6),
    ("market_cap_m", "Market cap (m, reporting ccy)", "#,##0", 12),
    ("ni_ttm_m", "Net income latest FY (m)", "#,##0", 11), ("ocf_ttm_m", "Operating cash flow latest FY (m)", "#,##0", 11),
    ("capex_ttm_m", "CapEx latest FY (m, positive)", "#,##0", 10), ("sbc_ttm_m", "Stock-based comp latest FY (m)", "#,##0", 10),
    ("dividends_ttm_m", "Dividends paid latest FY (m)", "#,##0", 10), ("lt_debt_m", "Long-term debt (m)", "#,##0", 10),
    ("interest_m", "Interest expense latest FY (m)", "#,##0", 10), ("ebit_ttm_m", "EBIT latest FY (m)", "#,##0", 10),
    ("total_assets_m", "Total assets (m)", "#,##0", 11), ("sales_ttm_m", "Sales latest FY (m)", "#,##0", 11),
    ("roic_median", "Median ROIC (GAAP, incl. goodwill)", "0.0%", 9),
    ("roic_tangible_median", "Median tangible ROIC", "0.0%", 9), ("roic_years", "ROIC years", "0", 6),
    ("fcf_conv", "True FCF ÷ NI (multi-yr)", "0%", 9), ("fcf_conv_years", "FCF conv. years", "0", 6),
    ("ni_margin_med", "Median net margin (≤10 yrs)", "0.0%", 9), ("fcf_margin_med", "Median True FCF margin (≤10 yrs)", "0.0%", 9),
    ("ni_avg_m", "Average net income (≤10 yrs, m)", "#,##0", 11), ("margin_years", "Margin years", "0", 6),
    ("roe_median", "Median ROE", "0.0%", 8), ("rote_median", "Median return on tangible equity", "0.0%", 8),
    ("equity_m", "Equity latest FY (m)", "#,##0", 11), ("tbv_m", "Tangible equity latest FY (m)", "#,##0", 11),
    ("cagr_bv_10", "Book value CAGR 10y", "0.0%", 8), ("cagr_bv_5", "Book value CAGR 5y", "0.0%", 8),
    ("cagr_bv_3", "Book value CAGR 3y", "0.0%", 8),
    ("cagr_eps_10", "EPS CAGR 10y", "0.0%", 8), ("cagr_eps_5", "EPS CAGR 5y", "0.0%", 8), ("cagr_eps_3", "EPS CAGR 3y", "0.0%", 8),
    ("cagr_sales_10", "Sales CAGR 10y", "0.0%", 8), ("cagr_sales_5", "Sales CAGR 5y", "0.0%", 8),
    ("cagr_sales_3", "Sales CAGR 3y", "0.0%", 8),
    ("cagr_fcf_10", "True FCF CAGR 10y", "0.0%", 8), ("cagr_fcf_5", "True FCF CAGR 5y", "0.0%", 8),
    ("cagr_fcf_3", "True FCF CAGR 3y", "0.0%", 8),
    ("mcap_delta_m", "Δ market cap over window (m)", "#,##0", 11), ("retained_m", "Σ retained earnings over window (m)", "#,##0", 11),
    ("dollar_years", "$1-test window (yrs)", "0", 6),
    ("roic_judgement", "ROIC judgement if no data (Pass/Fail)", "@", 9),
    ("g_est", "Analyst growth g (blank = fallback)", "0.0%", 9), ("g_moat_est", "Analyst g_moat (blank = g)", "0.0%", 9),
    ("e_norm_est", "Analyst normalised earnings (m; blank = formula)", "#,##0", 11),
    ("cet1", "Bank: CET1 ratio", "0.0%", 8), ("solvency", "Insurer: solvency ratio", "0%", 8),
    ("combined_ratio", "Insurer: combined ratio (cycle avg)", "0.0%", 8),
    ("nav_m", "Holding: NAV (m, reporting ccy)", "#,##0", 11), ("nav_cagr", "Holding: NAV/share CAGR (~10 yrs)", "0.0%", 8),
    ("ltv", "Holding: loan-to-value", "0%", 8),
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
HOLD_COLUMNS = [
    ("holding_id", "Holding #", "@", 8), ("id", "Company ID", "@", 11), ("entry_date", "Entry date", "yyyy-mm-dd", 11),
    ("entry_price", "Entry price", "#,##0.00", 10), ("shares", "Shares", "#,##0", 9),
    ("fx_to_base", "FX: quote ccy → your base ccy (blank = 1)", "0.0000", 9),
    ("entry_eb", "Equity Bond Y_c + g at entry", "0.0%", 9), ("moat_decay", "Analyst moat-decay flag (Y)", "@", 9),
    ("notes", "Notes", "@", 30),
]
FIN_FIELDS = [c[0] for c in FIN_COLUMNS]
TECH_FIELDS = [c[0] for c in TECH_COLUMNS]
BENCH_FIELDS = [c[0] for c in BENCH_COLUMNS]
HOLD_FIELDS = [c[0] for c in HOLD_COLUMNS]


def universe_keys() -> list[str]:
    return sorted(p.name for p in DATA_DIR.iterdir() if (p / "universe.json").exists())


def load_universe(key: str) -> dict:
    d = DATA_DIR / key
    meta = json.loads((d / "universe.json").read_text(encoding="utf-8"))
    meta["key"] = key
    meta["companies"] = read_csv(d / "inputs.csv")
    opt = lambda name: read_csv(d / name) if (d / name).exists() else []
    meta["prescreen"] = opt("prescreen.csv")
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


# ---------------------------------------------------------------- versioning
def _versions(stem: str) -> list[tuple[int, int]]:
    out = []
    for p in OUTPUT_DIR.glob(f"{glob_escape(stem)} v*.xlsx"):
        m = re.search(r" v(\d+)\.(\d+)\.xlsx$", p.name)
        if m:
            out.append((int(m.group(1)), int(m.group(2))))
    return sorted(out)


def glob_escape(s: str) -> str:
    return re.sub(r"([\[\]?*])", r"[\1]", s)


def next_version(stem: str, major: int | None = None) -> str:
    """Next free version for a file stem: v3.0, v3.1, ... (or a new major)."""
    from .config import CHANGELOG
    existing = _versions(stem)
    framework_major = max(int(v.split(".")[0]) for v in CHANGELOG)
    major = major or max([framework_major] + [ma for ma, _ in existing])
    minors = [mi for ma, mi in existing if ma == major]
    return f"{major}.{(max(minors) + 1) if minors else 0}"


def output_path(stem: str, version: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR / f"{stem} v{version}.xlsx"


def latest_output(stem: str) -> Path | None:
    v = _versions(stem)
    return output_path(stem, f"{v[-1][0]}.{v[-1][1]}") if v else None
