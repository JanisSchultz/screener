"""Fetch Quantitative data from EODHD into data/<universe>/{financials,fundamentals_panel,technicals,benchmarks}.csv.

    python3 fetch_market_data.py us --ids SPGI BLK        # test on specific companies
    python3 fetch_market_data.py us eu ca --funnel-only   # Quality-pass + Calamity-pass companies (default)
    python3 fetch_market_data.py us eu ca --all           # every company (fetches funnel first, then rest)
    python3 fetch_market_data.py us --prices-only         # refresh EOD prices, weekly technicals & quotes only
    python3 fetch_market_data.py us eu ca --offline       # recompute from data/_cache/eodhd only (no network)
    python3 fetch_market_data.py --check-quota            # inspect EODHD daily API call quota

Sources: EODHD Fundamentals API (full unfiltered 20-40 yr annual & quarterly statements, 1 request = 10 API calls per
company, cached in data/_cache/eodhd/{SYMBOL}.json) and EODHD Historical EOD / Splits / FOREX API (1 API call per
symbol, cached in data/_cache/eodhd/eod/{SYMBOL}.json).
Fetched and computed fields overwrite financials.csv and fundamentals_panel.csv (no analyst overrides since v7.6;
fin_note holds only the machine-written '[auto]' data notes). A company whose fetch returns nothing keeps its
previous row. Dual listings named in universe.json "mirror" copy their PAR inputs from the primary listing.
A diff report of PAR inputs (old -> new) is written to output/par_recompute_report.csv.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path
import sys
import time
import warnings

user_site = Path.home() / "Library/Python/3.9/lib/python/site-packages"
if user_site.exists() and str(user_site) not in sys.path:
    sys.path.insert(0, str(user_site))

warnings.filterwarnings("ignore")

from screener.data import (
    BENCH_FIELDS,
    DATA_DIR,
    FIN_FIELDS,
    OUTPUT_DIR,
    PANEL_FIELDS,
    QUAL_CODES,
    TECH_FIELDS,
    input_fields,
    load_universe,
    universe_keys,
    write_csv,
)
from screener.fetch import metrics, par, settings, sources
from screener.fetch.sources import EODHD, stale_fundamentals, symbol_cache, technicals
from screener.fetch.sqlite_db import build_sqlite_db
from screener.gates import funnel_ids, is_balance_sheet_financial, params, par_valuation

PAR_FIELDS = ("peak_oe_year", "peak_oe_eps", "cur_oe_eps", "cur_oe_year", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "p2p_ok")
AUTO = "[auto] "
US_GAAP_UNIVERSES = ("us",)     # operating-lease cost sits outside D&A under US GAAP -> no IFRS-16 lease deduction
# Non-US-universe companies that file under US GAAP (no IFRS-16 right-of-use depreciation inside D&A)
US_GAAP_IDS = {
    "ABBN.CH", "ALC.CH", "LOGN.CH", "QIA.DE", "STMMI.FR",
    "WCN.CA", "CP.CA", "QSR.CA", "SHOP.CA", "ENB.CA", "TRP.CA", "IMO.CA", "CNR.CA", "FTS.CA", "EMA.CA", "H.CA",
}


# v7.2 statement-integrity reviews (both empty by default; add an id once its data has been checked by hand):
# SHARE_BASIS_REVIEWED_IDS clears '[auto] share count changed since FY…' (valuation on statement shares);
# CCY_SWITCH_OVERRIDES forces the reporting-currency block decision ("convert" / "keep") and clears
# '[auto] currency switch unresolved …'.
SHARE_BASIS_REVIEWED_IDS: set[str] = set()
CCY_SWITCH_OVERRIDES: dict[str, str] = {
    "IMO.CA": "keep",       # Imperial Oil reports in CAD throughout; EODHD labels FY2014-20 "USD"
}


def listing_date(fund: dict | None, esym: str, bars: list | None) -> str | None:
    """First trading day of the primary listing (None for secondary listings, whose history can start late)."""
    if not bars or not bars[0].get("date"):
        return None
    primary = ((fund or {}).get("General") or {}).get("PrimaryTicker")
    return str(bars[0]["date"]) if (not primary or primary == esym) else None


def apply_lease_basis(series: dict, key: str, cid: str | None = None, sub_industry: str | None = None) -> dict:
    """IFRS-16 lessees carry right-of-use depreciation inside D&A; US GAAP filers do not. Drop the lease series for
    US GAAP universes and US-GAAP Canadian filers so owner_addback / true_fcf only deduct lease depreciation for IFRS reporters.
    Also tags balance-sheet financials (`_is_bs_financial`) from the universe `sub_industry`."""
    if not series:
        return series
    if key in US_GAAP_UNIVERSES or (cid and cid in US_GAAP_IDS):
        series["lease"] = {}
    if sub_industry:
        series["_is_bs_financial"] = is_balance_sheet_financial(sub_industry) or ("Consumer Finance" in str(sub_industry))
    return series


def set_auto_note(row: dict, notes: list[str]) -> None:
    """fin_note = the machine-written '[auto] …' data notes only, rewritten on every fetch (v7.6: no analyst text)."""
    row["fin_note"] = (AUTO + "; ".join(dict.fromkeys(notes))) if notes else None


def num(x):
    return x if isinstance(x, (int, float)) else None


def check_and_report_quota(eod: EODHD, est_calls: int = 0) -> dict | None:
    if settings.OFFLINE:
        return None
    try:
        u = eod.user_info()
    except RuntimeError as exc:
        sys.exit(str(exc))
    if not u:
        print("EODHD quota: could not query /api/user")
        return None
    used = int(u.get("apiRequests") or 0)
    limit = int(u.get("dailyRateLimit") or 100000)
    rem = limit - used
    print(f"EODHD quota: {used:,} / {limit:,} API calls used today ({rem:,} remaining)")
    if est_calls > 0:
        print(f"Estimated API calls for this run: ~{est_calls:,} (leaving ~{max(0, rem - est_calls):,} remaining)")
        if rem - est_calls < settings.EODHD_MIN_QUOTA_RESERVE:
            sys.exit(
                f"Aborting: estimated {est_calls:,} calls would leave fewer than "
                f"{settings.EODHD_MIN_QUOTA_RESERVE:,} reserve calls."
            )
    return u


def estimate_calls_for_symbols(symbols: list[str], prices_only: bool) -> int:
    calls = 0
    now = time.time()
    for s in set(symbols):
        if not prices_only:
            fp = symbol_cache(s)
            if settings.REFRESH_FUNDAMENTALS or not fp.exists() or (now - fp.stat().st_mtime) >= settings.FUND_CACHE_DAYS * 86400:
                calls += 10
        ep = symbol_cache(s, "eod")
        if not ep.exists() or (now - ep.stat().st_mtime) >= settings.EOD_CACHE_DAYS * 86400:
            calls += 1
    return calls


def fetch_universe(key: str, a, eod: EODHD, state: dict) -> None:
    meta = load_universe(key)
    by_id = {c["id"]: c for c in meta["companies"]}
    f_ids = funnel_ids(meta)
    if a.ids:
        ids = [i for i in a.ids if i in by_id]
        unknown = set(a.ids) - set(ids)
        if unknown:
            print(f"{key}: unknown ids {sorted(unknown)}")
    elif a.all:
        # Always prioritize funnel companies first, then the remaining universe
        f_set = set(f_ids)
        ids = list(f_ids) + [i for i in by_id if i not in f_set]
    else:
        ids = f_ids

    if not ids:
        return

    print(f"{key}: resolving EODHD symbols for {len(ids)} companies...", flush=True)
    syms = {i: eod.resolve_symbol(by_id[i], meta) for i in by_id}
    if not a.offline:
        eod.save_symbol_map()

    bench = meta.get("benchmark_symbols", {})
    bench_syms = {name: eod.benchmark_symbol(sym) for name, sym in bench.items()}
    target_syms = [syms[i] for i in ids]

    if not a.offline:
        est = estimate_calls_for_symbols(target_syms + list(bench_syms.values()), a.prices_only)
        check_and_report_quota(eod, est)
        print(f"{key}: fetching {len(ids)} companies from EODHD...", flush=True)
        eod.prefetch_batch(
            target_syms,
            fetch_fundamentals=not a.prices_only,
            fetch_eod=True,
        )
        eod.prefetch_batch(list(bench_syms.values()), fetch_fundamentals=False, fetch_eod=True)

    # ---- benchmarks + weekly technicals (derived from cached EOD daily bars)
    if not a.offline:
        mkt_sym = bench_syms.get("MARKET")
        mkt_bars = eod.eod(mkt_sym) if mkt_sym else []
        mkt_closes = eod.weekly_bars(mkt_bars)[0] if mkt_bars else []
        brows = []
        for name, bsym in bench_syms.items():
            bars = eod.eod(bsym)
            if bars:
                w = eod.weekly_bars(bars)
                t = technicals(*w) if w[0] else {}
                if t:
                    brows.append({"name": name, "symbol": bench[name], **{k: t.get(k) for k in BENCH_FIELDS if k in t}})
        if brows:
            write_csv(DATA_DIR / key / "benchmarks.csv", BENCH_FIELDS, brows)

        tech = dict(meta["technicals"])
        for i in ids:
            esym = syms[i]
            bars = eod.eod(esym)
            fund = eod.fundamentals(esym) if (symbol_cache(esym)).exists() else None
            sp = eod.splits(esym, fund) if bars else {}
            w = eod.weekly_bars(bars, sp) if bars else ([], [], [])
            t = technicals(*w, market_closes=mkt_closes) if w[0] else {}
            if t or i not in tech:
                tech[i] = {"id": i, "symbol": esym, **t, "tech_note": "" if t else "no weekly price history"}
        write_csv(
            DATA_DIR / key / "technicals.csv",
            TECH_FIELDS,
            [tech[c["id"]] for c in meta["companies"] if c["id"] in tech],
        )

    # ---- fundamentals + PAR inputs + multi-year panel
    fins = dict(meta["financials"])
    yh = sources.Yahoo() if (not a.offline and not a.prices_only) else None
    today = dt.date.today().isoformat()
    for n, i in enumerate(ids, 1):
        c, esym = by_id[i], syms[i]
        old = fins.get(i, {"id": i})
        fund = eod.fundamentals(esym)
        if yh is not None:
            yh.statements(esym, force_refresh=a.refresh_fundamentals)
        s_check = eod.annual_series(fund) if fund else {}
        if (
            (not fund or not (s_check.get("ni") and s_check.get("sales")) or stale_fundamentals(s_check))
            and not a.offline and not a.prices_only and not eod.transient_failure(esym)
        ):
            alt_sym = eod.fallback_resolve(c, meta)
            if alt_sym and alt_sym != esym:
                esym = alt_sym
                syms[i] = esym
                eod.save_symbol_map()
                fund = eod.fundamentals(esym)
        bars = eod.eod(esym)
        sp = eod.splits(esym, fund) if (fund or bars) else {}
        latest_px = float(bars[-1]["close"]) if (bars and bars[-1].get("close") is not None) else num(old.get("price"))
        last_bar = str(bars[-1].get("date")) if bars else None
        series = apply_lease_basis(
            eod.annual_series(fund, latest_price=latest_px, splits=sp, ccy_override=CCY_SWITCH_OVERRIDES.get(i),
                              last_bar_date=last_bar) if fund else {}, key, i, c.get("sub_industry"))
        q = eod.quote(esym, fund_data=fund, eod_bars=bars, series=series) if (fund or bars) else {}
        if q.get("share_basis_flag") and i in SHARE_BASIS_REVIEWED_IDS and q.get("statement_shares"):
            q["shares"] = q["statement_shares"]          # reviewed: value on the statement share basis

        if a.prices_only:
            row = dict(old)
        else:
            if not series.get("ni") or not (q.get("price") or old.get("price")):
                state["kept"].append(f"{key}:{i}")      # nothing fetched: never overwrite stored data
                continue
            row = {"id": i}
            row["fin_currency"] = q.get("fin_currency") or old.get("fin_currency")
            q_ccy = q.get("currency") or old.get("quote_currency")

            mp = eod.monthly_prices(esym, bars, sp) if bars else {}
            ye_px = eod.year_end_prices(esym, bars, sp) if bars else None
            fx_q_rep = eod.fx(q_ccy, row.get("fin_currency")) if (q_ccy and row.get("fin_currency")) else None
            if ye_px and fx_q_rep:
                px_rep = {y: p * fx_q_rep for y, p in ye_px.items()}
            else:
                px_rep = None

            m = metrics.summarize(series, px_rep, params(meta))
            row.update({k: v for k, v in m.items() if k in FIN_FIELDS})
            row["source"] = f"EODHD ({esym}); FY{m.get('fiscal_year')}" if m.get("fiscal_year") else f"EODHD ({esym})"

            notes = list(series.get("_notes") or [])     # statement-integrity notes from annual_series (currency)
            stale = stale_fundamentals(series)
            if stale:
                notes.append(stale)
            pr = par.compute(
                series,
                mp,
                (1.0 / fx_q_rep) if fx_q_rep else None,
                listing_date(fund, esym, bars),
            )
            notes += pr.pop("_notes", [])
            marks = metrics.noncash_marks(series)
            if marks:
                notes.append(marks)
            for k in PAR_FIELDS:
                row[k] = pr.get(k)
            if pr.get("peak_oe_eps") is None and old.get("peak_oe_eps") is not None:
                for k in PAR_FIELDS:
                    row[k] = old.get(k)
                notes.append("PAR inputs kept from previous data (could not compute)")
            elif pr.get("mult_low_5y") is None and old.get("mult_low_5y") is not None:
                row["mult_low_5y"], row["mult_high_5y"] = old.get("mult_low_5y"), old.get("mult_high_5y")
                notes.append("cycle multiples kept from previous data (no monthly prices)")

            # Share basis check (ADRs, multi-class, units): statement shares vs quote shares
            sh = series.get("shares") or {}
            if sh and q.get("shares"):
                ratio = sh[max(sh)] / q["shares"]
                if q.get("share_basis_flag") and i not in SHARE_BASIS_REVIEWED_IDS:
                    notes.append(f"share count changed since FY{max(sh)} (current ÷ statements = {q['share_basis_flag']:.2f})")
                elif not 0.67 <= ratio <= 1.5:
                    notes.append(f"check share basis (statements ÷ quote shares = {ratio:.2f})")

            # Dividend check: cash-flow dividends can include dividends paid to minority shareholders
            px_now = q.get("price") or num(old.get("price"))
            mc_new = (
                px_now * q["shares"] * fx_q_rep / 1e6
                if (px_now and q.get("shares") and fx_q_rep)
                else num(old.get("market_cap_m"))
            )
            dv = num(row.get("dividends_ttm_m"))
            same_ccy = (row.get("fin_currency") or "").upper() == ("GBP" if q_ccy in ("GBp", "GBX") else (q_ccy or "")).upper()
            if q.get("dps") and px_now and dv and mc_new and same_ccy:
                y_stmt, y_dps = dv / mc_new, q["dps"] / px_now
                if y_stmt > 1.3 * y_dps:        # v7.4: no upper bound (ORK.NO cash-flow figure 2.66× incl. specials)
                    row["dividends_ttm_m"] = y_dps * mc_new
                    notes.append("dividends = DPS × shares (cash-flow figure incl. specials / minority dividends)")
            elif a.offline and dv and mc_new and dv / mc_new > 0.06:
                notes.append(f"dividend yield {dv / mc_new:.1%} unverified (cash-flow figure may include minority dividends)")
            set_auto_note(row, notes)

        row["as_of"] = old.get("as_of") if (a.offline or a.prices_only) else today     # date of the fundamentals
        row["price"] = q.get("price") or old.get("price")
        row["quote_currency"] = q.get("currency") or old.get("quote_currency")
        fxr = eod.fx(row.get("quote_currency"), row.get("fin_currency")) if row.get("fin_currency") else None
        if row.get("price") and q.get("shares") and fxr:
            row["market_cap_m"] = row["price"] * q["shares"] * fxr / 1e6
        elif q.get("market_cap_raw") and row.get("fin_currency"):
            q_main_ccy = "GBP" if row.get("quote_currency") in ("GBp", "GBX") else row.get("quote_currency")
            fx_mcap = eod.fx(q_main_ccy, row.get("fin_currency"))
            if fx_mcap:
                row["market_cap_m"] = q["market_cap_raw"] * fx_mcap / 1e6
            else:
                print(f"  WARNING {key}:{i}: no FX {q_main_ccy}->{row.get('fin_currency')}; market cap kept from previous data")
                row["market_cap_m"] = old.get("market_cap_m")
        elif old.get("market_cap_m"):
            row["market_cap_m"] = old.get("market_cap_m")
        else:
            row["fin_note"] = ((row.get("fin_note") + "; ") if row.get("fin_note") else AUTO) + "market cap n/a (FX or shares missing)"

        state["report"].append((key, i, old, row))
        fins[i] = row
        if n % 100 == 0:
            print(f"  processed {n}/{len(ids)}", flush=True)

    write_csv(DATA_DIR / key / "financials.csv", FIN_FIELDS, [fins.get(c["id"], {"id": c["id"]}) for c in meta["companies"]])

    # Build multi-year fundamentals_panel.csv for all companies in this universe that have cached EODHD fundamentals
    panel_all: list[dict] = []
    for c in meta["companies"]:
        cid = c["id"]
        esym = syms[cid]
        fp = symbol_cache(esym)
        if not fp.exists():
            continue
        fund = eod.fundamentals(esym)
        if not fund:
            continue
        ep = symbol_cache(esym, "eod")
        bars = eod.eod(esym) if ep.exists() else []
        sp = eod.splits(esym, fund) if bars else {}
        ye_px = eod.year_end_prices(esym, bars, sp) if bars else None
        latest_px = float(bars[-1]["close"]) if (bars and bars[-1].get("close") is not None) else num((fins.get(cid) or {}).get("price"))
        ser = apply_lease_basis(eod.annual_series(fund, latest_price=latest_px), key, cid, c.get("sub_industry"))
        panel_all.extend(eod.panel_rows(cid, str(c["ticker"]), esym, fund, series=ser, ye_prices=ye_px))
    if panel_all:
        write_csv(DATA_DIR / key / "fundamentals_panel.csv", PANEL_FIELDS, panel_all)

    print(
        f"{key}: wrote financials.csv, fundamentals_panel.csv ({len(panel_all)} company-year rows)"
        + ("" if a.offline else ", technicals.csv, benchmarks.csv"),
        flush=True,
    )


def apply_mirrors(keys: list[str], eod: EODHD, state: dict) -> None:
    """Dual listings: copy PAR inputs, analyst overrides, and qualitative gate scores from the primary listing ("mirror" in universe.json)."""
    for key in keys:
        meta = load_universe(key)
        mirror = meta.get("mirror") or {}
        if not mirror:
            continue
        fins = dict(meta["financials"])
        cmap = {c["id"]: c for c in meta["companies"]}
        inputs_changed = False
        for i, src in mirror.items():
            skey, sid = src.split(":", 1)
            s_meta = load_universe(skey)
            s = s_meta["financials"].get(sid)
            t = fins.get(i)
            s_co = next((c for c in s_meta["companies"] if c["id"] == sid), None)
            t_co = cmap.get(i)
            if s_co and t_co:
                for qk in [*QUAL_CODES, "calamity", "calamity_note"]:
                    if t_co.get(qk) != s_co.get(qk):
                        t_co[qk] = s_co.get(qk)
                        inputs_changed = True
            if not s or not t:
                print(f"  mirror {key}:{i} <- {src}: missing row")
                continue
            old = dict(t)
            rate = eod.fx(s.get("quote_currency"), t.get("quote_currency"))
            if rate is None and num(s.get("price")) and num(t.get("price")):
                rate = t["price"] / s["price"]          # same share basis (1:1 ADR / dual line)
            for k in (
                "peak_oe_year", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "p2p_ok",
                "roic_median", "roic_operating", "fcf_conv", "roe_median", "ocf_ni_2y",
                "sales_1y", "sales_cagr", "sales_cagr_yrs", "opcost_1y", "opcost_cagr",
                "cap_growth", "ma_reinvest", "buyback_yield", "retention_rate", "roiic",
                "cur_oe_year", "ic_neg_years", "g6_netdebt_yrs", "g6_intcov",
            ):
                t[k] = s.get(k)
            if num(t.get("sales_ttm_m")) is None and num(s.get("sales_ttm_m")) is not None:
                fin_rate = eod.fx(s.get("fin_currency"), t.get("fin_currency")) or rate
                if fin_rate:
                    t["sales_ttm_m"] = num(s.get("sales_ttm_m")) * fin_rate
                else:
                    print(f"  WARNING mirror {key}:{i}: no FX {s.get('fin_currency')}->{t.get('fin_currency')}; sales left blank")
            for k in ("peak_oe_eps", "cur_oe_eps"):
                t[k] = round(num(s.get(k)) * rate, 4) if (num(s.get(k)) is not None and rate) else None
            set_auto_note(t, [f"PAR inputs mirrored from {src}"])
            state["report"].append((key, i, old, t))
            fins[i] = t
        if inputs_changed:
            write_csv(DATA_DIR / key / "inputs.csv", input_fields(meta), meta["companies"])
        write_csv(DATA_DIR / key / "financials.csv", FIN_FIELDS, [fins.get(c["id"], {"id": c["id"]}) for c in meta["companies"]])
        print(f"{key}: mirrored {len(mirror)} dual listing(s)")


def write_report(state: dict) -> None:
    latest = {}
    for key, i, old, new in state["report"]:
        latest[(key, i)] = (old if (key, i) not in latest else latest[(key, i)][0], new)
    if not latest:
        print(f"report: 0 rows updated; kept unchanged (no data): {len(state['kept'])}")
        return
    metas = {key: load_universe(key) for key in {k for k, _ in latest}}
    cmaps = {key: {c["id"]: c for c in m["companies"]} for key, m in metas.items()}
    pmaps = {key: params(m) for key, m in metas.items()}
    cols = ["universe", "id"] + [
        f"{k}_{s}"
        for k in ("peak_oe_eps", "peak_oe_year", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "roic_median", "dividends_ttm_m")
        for s in ("old", "new")
    ]
    cols += ["p2p_ok", "verdict_old", "verdict_new", "vs_par_old", "vs_par_new", "irr_old", "irr_new", "fin_note"]
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "par_recompute_report.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for (key, i), (old, new) in latest.items():
            c = cmaps.get(key, {}).get(i, {})
            p = pmaps.get(key)
            po = par_valuation(old, p, cap=c.get("4"), moat=c.get("3a"), sub_industry=c.get("sub_industry"))
            pn = par_valuation(new, p, cap=c.get("4"), moat=c.get("3a"), sub_industry=c.get("sub_industry"))
            r = [key, i]
            for k in ("peak_oe_eps", "peak_oe_year", "mult_low_5y", "mult_high_5y", "cagr_oe_eps", "roic_median", "dividends_ttm_m"):
                r += [old.get(k), new.get(k)]
            r += [
                new.get("p2p_ok"), po["status"], pn["status"], po["vs_par"], pn["vs_par"],
                po["irr_5y"], pn["irr_5y"], new.get("fin_note"),
            ]
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
    ap.add_argument("--offline", action="store_true", help="use data/_cache/eodhd only; no network, technicals untouched")
    ap.add_argument("--refresh-fundamentals", action="store_true", help="force re-download of cached fundamentals")
    ap.add_argument("--check-quota", action="store_true", help="query EODHD /api/user quota and exit")
    a = ap.parse_args()
    if a.offline and a.prices_only:
        sys.exit("--offline and --prices-only cannot be combined")
    settings.OFFLINE = a.offline
    settings.REFRESH_FUNDAMENTALS = a.refresh_fundamentals

    eod = EODHD()
    if a.check_quota:
        check_and_report_quota(eod)
        return 0

    state = {"report": [], "kept": []}
    keys = a.universes or universe_keys()
    for key in keys:
        fetch_universe(key, a, eod, state)
    apply_mirrors(keys, eod, state)
    write_report(state)
    build_sqlite_db()
    return 0


if __name__ == "__main__":
    sys.exit(main())
