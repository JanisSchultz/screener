"""Fetch Quantitative data into data/<universe>/{financials,technicals,benchmarks}.csv, then run build.py.

    python3 fetch_market_data.py us --ids MSFT AAPL       # test on a few companies
    python3 fetch_market_data.py us eu --funnel-only      # Quality-pass companies (default)
    python3 fetch_market_data.py eu --all                 # every company
    python3 fetch_market_data.py us --prices-only         # refresh weekly technicals + quotes only
    python3 fetch_market_data.py us eu ca --offline       # recompute from data/_cache only (no network)

Sources: SEC EDGAR companyfacts (US fundamentals, ~10 yrs) and Yahoo Finance via yfinance (quotes, FX,
weekly/monthly prices, ~4 yrs of statements for non-SEC filers). Fetched and computed fields overwrite the CSV
(incl. peak Owner EPS, cycle multiples, cycle g — see screener/fetch/par.py); analyst columns (peak_eps_est,
g_est, g_implied, fin_note) are preserved. A company whose fetch returns nothing keeps its previous row.
Dual listings named in universe.json "mirror" copy their PAR inputs from the primary listing.
A diff report of PAR inputs (old → new) is written to output/par_recompute_report.csv.
Cached responses live in data/_cache/ (--offline uses them whatever their age).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path
import sys
import warnings

user_site = Path.home() / "Library/Python/3.9/lib/python/site-packages"
if user_site.exists() and str(user_site) not in sys.path:
    sys.path.insert(0, str(user_site))

warnings.filterwarnings("ignore")

from screener.data import (BENCH_FIELDS, DATA_DIR, FIN_FIELDS, OUTPUT_DIR, TECH_FIELDS, load_universe,
                           universe_keys, write_csv)
from screener.fetch import metrics, par, settings
from screener.fetch.sources import SEC, Yahoo, split_adjust, technicals
from screener.gates import funnel_ids, par_valuation

ANALYST_FIELDS = ("peak_eps_est", "g_est", "roic_est", "g_implied", "fin_note")
PAR_FIELDS = ("peak_oe_year", "peak_oe_eps", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "p2p_ok")
AUTO = "[auto] "


def yahoo_symbol(c: dict, meta: dict) -> str:
    t = str(c["ticker"]).split(" / ")[0].strip().rstrip(".")
    if meta.get("symbol_rule") == "us":
        return t.replace(".", "-")
    suffix = meta.get("yahoo_suffix", {}).get(c.get("exchange"), "")
    return t.replace(" ", "-").replace(".", "-") + suffix


def set_auto_note(row: dict, notes: list[str]) -> None:
    """fin_note = analyst text (kept) + one '[auto] …' part rewritten on every fetch."""
    keep = [p for p in str(row.get("fin_note") or "").split(" | ") if p.strip() and not p.startswith(AUTO)]
    if notes:
        keep.append(AUTO + "; ".join(dict.fromkeys(notes)))
    row["fin_note"] = " | ".join(keep) or None


def num(x):
    return x if isinstance(x, (int, float)) else None


def seed_offline_fx(yh: Yahoo, meta: dict, syms: dict) -> None:
    """Offline: FX rates implied by stored rows (market cap in reporting ccy ÷ price × shares in quote ccy)."""
    for i, f in meta["financials"].items():
        q = yh.quote(syms[i]) if i in syms else None
        mc, px, qc, fc = num(f.get("market_cap_m")), num(f.get("price")), f.get("quote_currency"), f.get("fin_currency")
        if q and q.get("shares") and mc and px and qc and fc and qc != fc:
            yh.seed_fx(qc, fc, mc * 1e6 / (px * q["shares"]))


def fetch_universe(key: str, a, yh: Yahoo, state: dict) -> None:
    meta = load_universe(key)
    by_id = {c["id"]: c for c in meta["companies"]}
    if a.ids:
        ids = [i for i in a.ids if i in by_id]
        unknown = set(a.ids) - set(ids)
        if unknown:
            print(f"{key}: unknown ids {sorted(unknown)}")
    elif a.all:
        ids = list(by_id)
    else:
        ids = funnel_ids(meta)
    print(f"{key}: {'recomputing' if a.offline else 'fetching'} {len(ids)} companies")
    syms = {i: yahoo_symbol(by_id[i], meta) for i in by_id}
    if a.offline:
        seed_offline_fx(yh, meta, syms)

    # ---- benchmarks + weekly technicals (needs network)
    if not a.offline:
        bench = meta.get("benchmark_symbols", {})
        weekly = yh.weekly(sorted({syms[i] for i in ids} | set(bench.values())))
        mkt = weekly.get(bench.get("MARKET"), ([], [], []))[0]
        brows = []
        for name, sym in bench.items():
            if sym in weekly:
                t = technicals(*weekly[sym])
                if t:
                    brows.append({"name": name, "symbol": sym, **{k: t.get(k) for k in BENCH_FIELDS if k in t}})
        if brows:
            write_csv(DATA_DIR / key / "benchmarks.csv", BENCH_FIELDS, brows)
        tech = dict(meta["technicals"])
        for i in ids:
            w = weekly.get(syms[i])
            t = technicals(*w, market_closes=mkt) if w else {}
            if t or i not in tech:
                tech[i] = {"id": i, "symbol": syms[i], **t, "tech_note": "" if t else "no weekly price history"}
        write_csv(DATA_DIR / key / "technicals.csv", TECH_FIELDS,
                  [tech[c["id"]] for c in meta["companies"] if c["id"] in tech])

    # ---- fundamentals + PAR inputs
    fins = dict(meta["financials"])
    today = dt.date.today().isoformat()
    sec = None
    for n, i in enumerate(ids, 1):
        c, sym = by_id[i], syms[i]
        old = fins.get(i, {"id": i})
        q = yh.quote(sym) or {}
        if a.prices_only:
            row = dict(old)
        else:
            row = {"id": i, **{k: old.get(k) for k in ANALYST_FIELDS}}
            series, source = None, None
            if meta.get("symbol_rule") == "us":
                sec = sec or SEC()
                cik = sec.cik(str(c["ticker"]).split(" / ")[0])
                facts = sec.facts(cik) if cik else None
                if facts:
                    series, source = sec.annual_series(facts), "SEC EDGAR companyfacts"
                    row["fin_currency"] = "USD"
                    if series.get("ni") and not series.get("shares") and not series.get("eps"):
                        ys = yh.statements(sym)          # multi-class filers (e.g. V) tag EPS only per class
                        series["shares"], series["eps"] = ys.get("shares") or {}, ys.get("eps") or {}
            if not series or not series.get("ni"):
                series, source = yh.statements(sym), "Yahoo Finance annual statements (~4 yrs)"
                row["fin_currency"] = q.get("fin_currency") or old.get("fin_currency")
            if not series.get("ni") or not q:
                state["kept"].append(f"{key}:{i}")      # nothing fetched: never overwrite stored data
                continue
            series = split_adjust(series, yh.splits(sym) or {}, q.get("shares"))
            px = yh.year_end_prices(sym) if (series.get("shares") or series.get("eps")) else None
            fx_q_rep = yh.fx(q.get("currency"), row.get("fin_currency")) if q.get("currency") else None
            if px and fx_q_rep:
                px = {y: p * fx_q_rep for y, p in px.items()}
            elif px:
                px = None
            m = metrics.summarize(series, px)
            row.update({k: v for k, v in m.items() if k in FIN_FIELDS})
            row["source"] = f"{source}; FY{m.get('fiscal_year')}" if m.get("fiscal_year") else source

            notes = []
            pr = par.compute(series, yh.monthly_prices(sym), (1 / fx_q_rep) if fx_q_rep else None,
                             num(old.get("peak_eps_est")))
            notes += pr.pop("_notes", [])
            for k in PAR_FIELDS:
                row[k] = pr.get(k)
            if pr.get("peak_oe_eps") is None and old.get("peak_oe_eps") is not None:
                for k in PAR_FIELDS:
                    row[k] = old.get(k)
                notes.append("PAR inputs kept from previous data (could not compute)")
            elif pr.get("mult_low_5y") is None and old.get("mult_low_5y") is not None:
                row["mult_low_5y"], row["mult_high_5y"] = old.get("mult_low_5y"), old.get("mult_high_5y")
                notes.append("cycle multiples kept from previous data (no monthly prices)")
            # share basis check (ADRs, multi-class, units): statement shares vs quote shares
            sh = series.get("shares") or {}
            if sh and q.get("shares"):
                ratio = sh[max(sh)] / q["shares"]
                if not 0.67 <= ratio <= 1.5:
                    notes.append(f"check share basis (statements ÷ quote shares = {ratio:.2f})")
            # dividend check: cash-flow dividends can include dividends paid to minority shareholders
            mc_new = q["price"] * q["shares"] * fx_q_rep / 1e6 if (q.get("price") and q.get("shares") and fx_q_rep) else num(old.get("market_cap_m"))
            dv = num(row.get("dividends_ttm_m"))
            if q.get("dps") and q.get("price") and dv and mc_new:
                y_stmt, y_dps = dv / mc_new, q["dps"] / q["price"]
                if 1.3 * y_dps < y_stmt < 2.5 * y_dps:
                    row["dividends_ttm_m"] = y_dps * mc_new
                    notes.append("dividends = DPS × shares (cash-flow figure incl. minority dividends)")
            elif a.offline and dv and mc_new and dv / mc_new > 0.06:
                notes.append(f"dividend yield {dv / mc_new:.1%} unverified (cash-flow figure may include minority dividends)")
            set_auto_note(row, notes)
        row["as_of"] = old.get("as_of") if a.offline else today
        row["price"], row["quote_currency"] = q.get("price") or old.get("price"), q.get("currency") or old.get("quote_currency")
        fxr = yh.fx(row.get("quote_currency"), row.get("fin_currency")) if row.get("fin_currency") else None
        if q.get("price") and q.get("shares") and fxr:
            row["market_cap_m"] = q["price"] * q["shares"] * fxr / 1e6
        elif old.get("market_cap_m"):
            row["market_cap_m"] = old.get("market_cap_m")
        else:
            row["fin_note"] = (row.get("fin_note") or "") + " market cap n/a (FX or shares missing)"
        state["report"].append((key, i, old, row))
        fins[i] = row
        if n % 50 == 0:
            print(f"  {n}/{len(ids)}")
    write_csv(DATA_DIR / key / "financials.csv", FIN_FIELDS, [fins.get(c["id"], {"id": c["id"]}) for c in meta["companies"]])
    print(f"{key}: wrote financials.csv" + ("" if a.offline else ", technicals.csv, benchmarks.csv"))


def apply_mirrors(keys: list[str], yh: Yahoo, state: dict) -> None:
    """Dual listings: copy PAR inputs and analyst overrides from the primary listing ("mirror" in universe.json)."""
    for key in keys:
        meta = load_universe(key)
        mirror = meta.get("mirror") or {}
        if not mirror:
            continue
        fins = dict(meta["financials"])
        for i, src in mirror.items():
            skey, sid = src.split(":", 1)
            s = load_universe(skey)["financials"].get(sid)
            t = fins.get(i)
            if not s or not t:
                print(f"  mirror {key}:{i} <- {src}: missing row")
                continue
            old = dict(t)
            rate = yh.fx(s.get("quote_currency"), t.get("quote_currency"))
            if rate is None and num(s.get("price")) and num(t.get("price")):
                rate = t["price"] / s["price"]          # same share basis (1:1 ADR / dual line)
            for k in ("peak_oe_year", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "p2p_ok",
                      "sales_cagr", "sales_cagr_yrs", "buyback_yield", "retention_rate", "roiic",
                      "g_est", "g_implied"):
                t[k] = s.get(k)
            if num(t.get("sales_ttm_m")) is None and num(s.get("sales_ttm_m")) is not None:
                fin_rate = yh.fx(s.get("fin_currency"), t.get("fin_currency")) or rate or 1.0
                t["sales_ttm_m"] = num(s.get("sales_ttm_m")) * fin_rate
            for k in ("peak_oe_eps", "peak_eps_est"):
                t[k] = num(s.get(k)) * rate if (num(s.get(k)) is not None and rate) else None
            set_auto_note(t, [f"PAR inputs mirrored from {src}"])
            state["report"].append((key, i, old, t))
            fins[i] = t
        write_csv(DATA_DIR / key / "financials.csv", FIN_FIELDS, [fins.get(c["id"], {"id": c["id"]}) for c in meta["companies"]])
        print(f"{key}: mirrored {len(mirror)} dual listing(s)")


def write_report(state: dict) -> None:
    latest = {}
    for key, i, old, new in state["report"]:
        latest[(key, i)] = (old if (key, i) not in latest else latest[(key, i)][0], new)
    cols = ["universe", "id"] + [f"{k}_{s}" for k in ("peak_oe_eps", "peak_oe_year", "mult_low_5y", "mult_high_5y",
                                                       "cagr_oe_eps", "roic_median", "dividends_ttm_m") for s in ("old", "new")]
    cols += ["p2p_ok", "verdict_old", "verdict_new", "vs_par_old", "vs_par_new", "irr_old", "irr_new", "fin_note"]
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "par_recompute_report.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for (key, i), (old, new) in latest.items():
            po, pn = par_valuation(old), par_valuation(new)
            r = [key, i]
            for k in ("peak_oe_eps", "peak_oe_year", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "roic_median", "dividends_ttm_m"):
                r += [old.get(k), new.get(k)]
            r += [new.get("p2p_ok"), po["status"], pn["status"], po["vs_par"], pn["vs_par"], po["irr_5y"], pn["irr_5y"],
                  new.get("fin_note")]
            w.writerow(r)
    print(f"report: output/{path.name} ({len(latest)} rows); kept unchanged (no data): {len(state['kept'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("universes", nargs="*")
    sel = ap.add_mutually_exclusive_group()
    sel.add_argument("--ids", nargs="+")
    sel.add_argument("--all", action="store_true")
    sel.add_argument("--funnel-only", action="store_true", help="default")
    ap.add_argument("--prices-only", action="store_true")
    ap.add_argument("--offline", action="store_true", help="use data/_cache only; no network, technicals untouched")
    a = ap.parse_args()
    if a.offline and a.prices_only:
        sys.exit("--offline and --prices-only cannot be combined")
    settings.OFFLINE = a.offline

    yh = Yahoo()
    state = {"report": [], "kept": []}
    keys = a.universes or universe_keys()
    for key in keys:
        fetch_universe(key, a, yh, state)
    if not a.prices_only:
        apply_mirrors(keys, yh, state)
        write_report(state)


if __name__ == "__main__":
    sys.exit(main())
