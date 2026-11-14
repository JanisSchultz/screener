"""Build a single SQLite3 / sql.js-compatible database (data/fundamentals.sqlite)
from the EODHD cache and universe CSVs across all universes (us, eu, ca)."""
from __future__ import annotations

import os
from pathlib import Path
import sqlite3

from ..data import DATA_DIR, FIN_FIELDS, PANEL_FIELDS, TECH_FIELDS, load_universe, read_csv, universe_keys
from ..gates import results as compute_gate_results
from .sources import EODHD, _f, _fval, symbol_cache

DB_PATH = DATA_DIR / "fundamentals.sqlite"

QUARTERLY_FIELDS = [
    "universe", "id", "ticker", "eodhd_symbol", "quarter_end", "filing_date", "fin_currency",
    "revenue_m", "gross_profit_m", "opex_m", "ebit_m", "ebitda_m", "da_m",
    "pretax_income_m", "tax_m", "net_income_m",
    "ocf_m", "capex_m", "fcf_reported_m", "sbc_m", "dividends_paid_m", "share_buybacks_m",
    "cash_m", "lt_debt_m", "total_debt_m", "net_debt_m", "equity_m", "goodwill_m", "intangibles_m", "total_assets_m",
    "diluted_shares_m", "eps_street", "eps_estimate",
]


def _extract_quarterly_rows(universe: str, cid: str, ticker: str, symbol: str, fund_data: dict) -> list[dict]:
    fin = fund_data.get("Financials") or {}
    inc = (fin.get("Income_Statement") or {}).get("quarterly") or {}
    bs = (fin.get("Balance_Sheet") or {}).get("quarterly") or {}
    cf = (fin.get("Cash_Flow") or {}).get("quarterly") or {}
    earn_hist = (fund_data.get("Earnings") or {}).get("History") or {}
    _, fin_ccy = EODHD._detect_currencies(symbol, fund_data, None)

    osh_q = (fund_data.get("outstandingShares") or {}).get("quarterly") or {}
    osh_by_q: dict[str, float] = {}
    for v in osh_q.values():
        if isinstance(v, dict) and v.get("dateFormatted") and _f(v.get("shares")):
            osh_by_q[str(v["dateFormatted"])[:7]] = float(_f(v["shares"]))

    m = lambda v: round(v / 1e6, 3) if v is not None else None
    r4 = lambda v: round(v, 4) if v is not None else None

    all_q = sorted(set(inc.keys()) | set(bs.keys()) | set(cf.keys()))
    # Keep up to the latest 40 quarters (10 years of quarterly statements) to keep the SQLite DB fast and compact
    rows = []
    for d_str in all_q[-40:]:
        i_r, b_r, c_r = inc.get(d_str) or {}, bs.get(d_str) or {}, cf.get(d_str) or {}
        rev = _fval(i_r, "totalRevenue", "grossProfit")
        ni = _fval(i_r, "netIncomeApplicableToCommonShares", "netIncome", "netIncomeFromContinuingOps")
        if rev is None and ni is None:
            continue
        ebit = _fval(i_r, "operatingIncome", "ebit")
        da_cands = [abs(x) for x in (
            _fval(i_r, "reconciledDepreciation"),
            _fval(i_r, "depreciationAndAmortization"),
            _fval(c_r, "depreciation"),
        ) if x is not None]
        da = max(da_cands) if da_cands else None
        sh = osh_by_q.get(d_str[:7]) or _fval(b_r, "commonStockSharesOutstanding")
        eh = earn_hist.get(d_str) or {}
        buybacks_raw = _fval(c_r, "salePurchaseOfStock")

        rows.append({
            "universe": universe,
            "id": cid,
            "ticker": ticker,
            "eodhd_symbol": symbol,
            "quarter_end": d_str,
            "filing_date": i_r.get("filing_date") or b_r.get("filing_date") or c_r.get("filing_date"),
            "fin_currency": i_r.get("currency_symbol") or fin_ccy,
            "revenue_m": m(rev),
            "gross_profit_m": m(_fval(i_r, "grossProfit")),
            "opex_m": m(_fval(i_r, "totalOperatingExpenses")),
            "ebit_m": m(ebit),
            "ebitda_m": m(_fval(i_r, "ebitda")),
            "da_m": m(da),
            "pretax_income_m": m(_fval(i_r, "incomeBeforeTax")),
            "tax_m": m(_fval(i_r, "incomeTaxExpense", "taxProvision")),
            "net_income_m": m(ni),
            "ocf_m": m(_fval(c_r, "totalCashFromOperatingActivities")),
            "capex_m": m(abs(_fval(c_r, "capitalExpenditures"))) if _fval(c_r, "capitalExpenditures") is not None else None,
            "fcf_reported_m": m(_fval(c_r, "freeCashFlow")),
            "sbc_m": m(abs(_fval(c_r, "stockBasedCompensation"))) if _fval(c_r, "stockBasedCompensation") is not None else None,
            "dividends_paid_m": m(abs(_fval(c_r, "dividendsPaid"))) if _fval(c_r, "dividendsPaid") is not None else None,
            "share_buybacks_m": m(-buybacks_raw) if buybacks_raw is not None else None,
            "cash_m": m(_fval(b_r, "cashAndEquivalents", "cash", "cashAndShortTermInvestments")),
            "lt_debt_m": m(_fval(b_r, "longTermDebt", "longTermDebtTotal")),
            "total_debt_m": m(_fval(b_r, "shortLongTermDebtTotal", "longTermDebtTotal", "longTermDebt")),
            "net_debt_m": m(_fval(b_r, "netDebt")),
            "equity_m": m(_fval(b_r, "totalStockholderEquity", "commonStockTotalEquity")),
            "goodwill_m": m(_fval(b_r, "goodWill")),
            "intangibles_m": m(_fval(b_r, "intangibleAssets")),
            "total_assets_m": m(_fval(b_r, "totalAssets")),
            "diluted_shares_m": round(sh / 1e6, 3) if sh else None,
            "eps_street": r4(_f(eh.get("epsActual"))),
            "eps_estimate": r4(_f(eh.get("epsEstimate"))),
        })
    return rows


def build_sqlite_db(keys: list[str] | None = None, db_path: Path = DB_PATH) -> Path:
    """Create/replace data/fundamentals.sqlite (compatible with Python sqlite3 and browser sql.js)."""
    eod = EODHD()
    ukeys = keys or universe_keys()
    tmp_path = db_path.with_name(f"{db_path.name}.{os.getpid()}.tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    conn = sqlite3.connect(str(tmp_path))
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = OFF;")
    cur.execute("PRAGMA synchronous = OFF;")

    # 1. companies table
    cur.execute(
        """
        CREATE TABLE companies (
            universe TEXT,
            id TEXT,
            ticker TEXT,
            eodhd_symbol TEXT,
            company TEXT,
            country TEXT,
            sector TEXT,
            sub_industry TEXT,
            exchange TEXT,
            g1 TEXT,
            g2 TEXT,
            g3a TEXT,
            g3b TEXT,
            g4 REAL,
            g5 REAL,
            g6 TEXT,
            calamity TEXT,
            result TEXT,
            PRIMARY KEY (universe, id)
        )
        """
    )

    # 2. financials_latest table
    fin_col_defs = ", ".join(["universe TEXT"] + [
        f'"{c}" TEXT' if c in ("id", "fin_currency", "as_of", "source", "quote_currency", "p2p_ok", "fin_note")
        else f'"{c}" INTEGER' if c in ("peak_oe_year", "sales_cagr_yrs")
        else f'"{c}" REAL'
        for c in FIN_FIELDS
    ])
    cur.execute(f"CREATE TABLE financials_latest ({fin_col_defs}, PRIMARY KEY (universe, id))")

    # 3. annual_fundamentals table
    ann_col_defs = ", ".join(["universe TEXT"] + [
        f'"{c}" TEXT' if c in ("id", "ticker", "eodhd_symbol", "period_end", "filing_date", "fin_currency")
        else f'"{c}" INTEGER' if c == "fy"
        else f'"{c}" REAL'
        for c in PANEL_FIELDS
    ])
    cur.execute(f"CREATE TABLE annual_fundamentals ({ann_col_defs}, PRIMARY KEY (universe, id, fy))")

    # 4. quarterly_fundamentals table
    qtr_col_defs = ", ".join([
        f'"{c}" TEXT' if c in ("universe", "id", "ticker", "eodhd_symbol", "quarter_end", "filing_date", "fin_currency")
        else f'"{c}" REAL'
        for c in QUARTERLY_FIELDS
    ])
    cur.execute(f"CREATE TABLE quarterly_fundamentals ({qtr_col_defs}, PRIMARY KEY (universe, id, quarter_end))")

    # 5. technicals_latest table
    tech_col_defs = ", ".join(["universe TEXT"] + [
        f'"{c}" TEXT' if c in ("id", "symbol", "as_of", "tech_note") else f'"{c}" REAL'
        for c in TECH_FIELDS
    ])
    cur.execute(f"CREATE TABLE technicals_latest ({tech_col_defs}, PRIMARY KEY (universe, id))")

    comp_rows, fin_rows, ann_rows, qtr_rows, tech_rows = [], [], [], [], []

    for k in ukeys:
        meta = load_universe(k)
        res = compute_gate_results(meta)
        for c in meta["companies"]:
            cid = c["id"]
            esym = eod.resolve_symbol(c, meta)
            comp_rows.append((
                k, cid, str(c.get("ticker") or ""), esym, c.get("company"),
                c.get("country"), c.get("sector"), c.get("sub_industry"), c.get("exchange") or "US",
                c.get("1"), c.get("2"), c.get("3a"), c.get("3b"),
                c.get("4"), c.get("5"), c.get("6"), c.get("calamity"),
                (res.get(cid) or {}).get("result"),
            ))
            f_row = meta["financials"].get(cid, {"id": cid})
            fin_rows.append((k, *[f_row.get(col) for col in FIN_FIELDS]))

            t_row = meta["technicals"].get(cid)
            if t_row:
                tech_rows.append((k, *[t_row.get(col) for col in TECH_FIELDS]))

            fp = symbol_cache(esym)
            if fp.exists():
                fund = eod.fundamentals(esym)
                if fund:
                    qtr_rows.extend(_extract_quarterly_rows(k, cid, str(c.get("ticker") or ""), esym, fund))

        panel_csv = DATA_DIR / k / "fundamentals_panel.csv"
        if panel_csv.exists():
            for pr in read_csv(panel_csv):
                ann_rows.append((k, *[pr.get(col) for col in PANEL_FIELDS]))

    cur.executemany(
        f"INSERT OR REPLACE INTO companies VALUES ({','.join(['?'] * 18)})",
        comp_rows,
    )
    cur.executemany(
        f"INSERT OR REPLACE INTO financials_latest VALUES ({','.join(['?'] * (1 + len(FIN_FIELDS)))})",
        fin_rows,
    )
    cur.executemany(
        f"INSERT OR REPLACE INTO annual_fundamentals VALUES ({','.join(['?'] * (1 + len(PANEL_FIELDS)))})",
        ann_rows,
    )
    cur.executemany(
        f"INSERT OR REPLACE INTO quarterly_fundamentals VALUES ({','.join(['?'] * len(QUARTERLY_FIELDS))})",
        [tuple(r.get(col) for col in QUARTERLY_FIELDS) for r in qtr_rows],
    )
    cur.executemany(
        f"INSERT OR REPLACE INTO technicals_latest VALUES ({','.join(['?'] * (1 + len(TECH_FIELDS)))})",
        tech_rows,
    )

    cur.execute("CREATE INDEX idx_ann_id ON annual_fundamentals (universe, id);")
    cur.execute("CREATE INDEX idx_qtr_id ON quarterly_fundamentals (universe, id);")
    cur.execute("CREATE INDEX idx_comp_res ON companies (universe, result);")

    conn.commit()
    cur.execute("VACUUM;")
    conn.close()
    tmp_path.replace(db_path)
    print(
        f"sqlite: wrote {db_path.relative_to(DATA_DIR.parent)} "
        f"({len(comp_rows)} companies, {len(ann_rows)} annual rows, {len(qtr_rows)} quarterly rows)"
    )
    return db_path
