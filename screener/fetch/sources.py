"""Data sources: EODHD Fundamentals & EOD Historical Prices/FX API (primary),
plus legacy SEC EDGAR and Yahoo Finance wrappers for backwards compatibility."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
from statistics import median
import threading
import time
import warnings

warnings.filterwarnings("ignore")

from .. import config as C
from ..data import DATA_DIR
from . import metrics, par, settings

CACHE = DATA_DIR / "_cache"
EODHD_CACHE = CACHE / "eodhd"
CCY_CLOSE_PAIR_LOG = 0.4        # |ln fx| below this (GBP/USD, CHF/USD, CAD/USD …): currency switch decided per block
CCY_AMBIGUOUS_MARGIN = 0.05     # block decision closer than this (in log points) = ambiguous -> flagged for review
FX_HISTORY_START = "2010-01-01"

# Windows / OneDrive reserve these device names for any file stem ("CON.XETRA.json" for Continental cannot sync)
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}


def safe_name(name: str) -> str:
    """File-name-safe cache stem: reserved device names (CON, PRN, AUX, NUL, COM1, LPT1 …) get a '_' prefix."""
    return "_" + name if name.split(".", 1)[0].upper() in RESERVED_NAMES else name


def symbol_cache(symbol: str, sub: str | None = None) -> Path:
    """data/_cache/eodhd[/sub]/<symbol>.json with reserved device names made OneDrive-safe."""
    return (EODHD_CACHE / sub if sub else EODHD_CACHE) / f"{safe_name(symbol)}.json"


def _load_api_key() -> str:
    key = os.environ.get("EODHD_API_KEY", "").strip()
    if key:
        return key
    env_path = DATA_DIR.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "EODHD_API_KEY":
                    return v.strip().strip("'").strip('"')
    return ""


def _cached(path: Path, fetch, days=settings.CACHE_DAYS, force_refresh: bool = False):
    if path.exists() and not force_refresh:
        if settings.OFFLINE or (time.time() - path.stat().st_mtime) < days * 86400:
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
    if settings.OFFLINE:                    # offline: use the cache whatever its age, never fetch
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None
    data = fetch()
    if data is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    return data


def _f(x):
    if x is None or x == "" or x == "None" or x == "NA":
        return None
    try:
        v = float(x)
        return None if (math.isnan(v) or math.isinf(v)) else v
    except (TypeError, ValueError):
        return None


def _fval(row: dict | None, *keys: str) -> float | None:
    if not isinstance(row, dict):
        return None
    for k in keys:
        v = _f(row.get(k))
        if v is not None:
            return v
    return None


def _norm_name(name: str | None) -> str:
    if not name:
        return ""
    s = name.lower()
    for tok in (" inc.", " inc", " corp.", " corp", " corporation", " plc", " n.v.", " nv", " s.a.", " sa",
                " se", " ag", " ab", " asa", " oyj", " a/s", " s.p.a.", " spa", " ltd.", " ltd", " limited",
                " holding", " holdings", " group", " co.", " company", " the "):
        s = s.replace(tok, " ")
    return re.sub(r"[^a-z0-9]+", "", s)


def _name_tokens(name: str | None) -> list[str]:
    s = (name or "").lower()
    for tok in (" inc.", " inc", " corp.", " corp", " corporation", " plc", " n.v.", " nv", " s.a.", " sa",
                " se", " ag", " ab", " asa", " oyj", " a/s", " s.p.a.", " spa", " ltd.", " ltd", " limited",
                " holding", " holdings", " group", " co.", " company", " the "):
        s = s.replace(tok, " ")
    return [t for t in re.split(r"[^a-z0-9]+", s) if t]


def _same_company(target: str | None, hit: str | None) -> bool:
    """Word-boundary name match: one name's tokens are a prefix of the other's ("Prysmian" ~ "Prysmian SpA"),
    never a substring inside a word ("Nexi" !~ "Nexity", "Terna" !~ "GEK Terna Holdings")."""
    a, b = _name_tokens(target), _name_tokens(hit)
    if not a or not b:
        return False
    n = min(len(a), len(b))
    return a[:n] == b[:n]


def stale_fundamentals(s: dict, today: dt.date | None = None) -> str | None:
    """'[auto]' note text when a listing's statements are stale: revenue / balance sheet ending >= 2 fiscal years
    before cash flow / net income (thin secondary listings, e.g. PRY.IT on 0NUX.LSE), or the latest revenue /
    balance-sheet year >= 3 years old. Valuation treats such rows as No data until refetched."""
    last = lambda k: max((y for y, v in (s.get(k) or {}).items() if v is not None), default=None)
    core = [y for y in (last("sales"), last("equity")) if y is not None]
    if not core:
        return None
    flow = max((y for y in (last("ocf"), last("ni")) if y is not None), default=None)
    if flow is not None and flow - min(core) >= 2:
        return f"stale fundamentals (revenue/balance sheet end FY{min(core)}, cash flow FY{flow})"
    if max(core) <= (today or dt.date.today()).year - 3:
        return f"stale fundamentals (latest FY{max(core)})"
    return None


# ------------------------------------------------------------------------- EODHD
class EODHD:
    """Clean per-company fundamentals, EOD prices, splits, and FX from EODHD API."""

    EXCHANGE_MAP = {
        "US": "US",
        "Toronto Stock Exchange": "TO",
        "London Stock Exchange": "LSE",
        "Xetra": "XETRA",
        "Euronext Paris": "PA",
        "SIX Swiss Exchange": "SW",
        "Nasdaq Stockholm": "ST",
        "Borsa Italiana": "MI",
        "Euronext Amsterdam": "AS",
        "Bolsa de Madrid": "MC",
        "Nasdaq Copenhagen": "CO",
        "Oslo Børs": "OL",
        "Nasdaq Helsinki": "HE",
        "Warsaw SE": "WAR",
        "Euronext Brussels": "BR",
        "Athens SE": "AT",
        "Wiener Börse": "VI",
        "Euronext Dublin": "IR",
        "Euronext Lisbon": "LS",
    }

    BENCHMARK_MAP = {
        "SPY": "SPY.US",
        "XLC": "XLC.US",
        "XLY": "XLY.US",
        "XLP": "XLP.US",
        "XLE": "XLE.US",
        "XLF": "XLF.US",
        "XLV": "XLV.US",
        "XLI": "XLI.US",
        "XLK": "XLK.US",
        "XLB": "XLB.US",
        "XLRE": "XLRE.US",
        "XLU": "XLU.US",
        "EXSA.DE": "EXSA.XETRA",
        "XIU.TO": "XIU.TO",
    }

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or _load_api_key()
        self._lock = threading.Lock()
        self._last_req = 0.0
        self._local = threading.local()
        self._fx: dict[tuple[str, str], float | None] = {}
        self._fx_hist: dict[tuple[str, str], list] = {}
        self._ex_symbols: dict[str, dict[str, dict]] = {}
        self._symbol_map_path = EODHD_CACHE / "symbol_map.json"
        self._symbol_map: dict[str, str] = {}
        self._transient: set[str] = set()      # paths whose last request failed with 5xx / timeout (not a 404)
        if self._symbol_map_path.exists():
            try:
                self._symbol_map = json.loads(self._symbol_map_path.read_text(encoding="utf-8"))
            except Exception:
                self._symbol_map = {}

    def _session(self):
        s = getattr(self._local, "session", None)
        if s is None:
            import requests
            s = requests.Session()
            s.headers.update({"Accept-Encoding": "gzip, deflate", "User-Agent": settings.SEC_USER_AGENT})
            self._local.session = s
        return s

    def _get(self, path: str, params: dict | None = None):
        if settings.OFFLINE:
            return None
        if not self.api_key:
            raise RuntimeError("EODHD_API_KEY not found in .env or environment")
        with self._lock:
            now = time.time()
            wait = (1.0 / settings.EODHD_MAX_RPS) - (now - self._last_req)
            if wait > 0:
                time.sleep(wait)
            self._last_req = time.time()
        q = {"api_token": self.api_key, "fmt": "json"}
        if params:
            q.update(params)
        url = f"https://eodhd.com/api/{path.lstrip('/')}"
        for attempt in range(3):
            try:
                r = self._session().get(url, params=q, timeout=30)
                if r.status_code == 404:
                    return None
                if r.status_code == 429:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as exc:
                msg = str(exc)
                if any(s in msg for s in ("nodename nor servname", "Name or service not known", "Failed to establish a new connection", "Max retries exceeded", "Failed to resolve")):
                    raise RuntimeError(f"Network unreachable (sandboxed): {exc}") from exc
                if attempt == 2:
                    self._transient.add(path)
                    return None
                time.sleep(1.0 * (attempt + 1))
        self._transient.add(path)
        return None

    def transient_failure(self, symbol: str) -> bool:
        """True when a request for `symbol` failed transiently: never remap a listing on a temporary error."""
        return any(symbol in p for p in self._transient)

    def user_info(self) -> dict | None:
        """Query /api/user to check daily API quota usage and limits."""
        return self._get("user")

    def save_symbol_map(self) -> None:
        self._symbol_map_path.parent.mkdir(parents=True, exist_ok=True)
        self._symbol_map_path.write_text(json.dumps(dict(sorted(self._symbol_map.items())), indent=2), encoding="utf-8")

    def exchange_symbols(self, ex_code: str) -> dict[str, dict]:
        """Return {Code.upper(): item_dict} for an EODHD exchange code (1 API call, cached 30 days)."""
        if ex_code in self._ex_symbols:
            return self._ex_symbols[ex_code]
        data = _cached(
            symbol_cache(ex_code, "exchanges"),
            lambda: self._get(f"exchange-symbol-list/{ex_code}"),
            days=30,
        )
        by_code = {}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("Code"):
                    by_code[str(item["Code"]).upper()] = item
        self._ex_symbols[ex_code] = by_code
        return by_code

    def search_symbol(self, query: str) -> list[dict]:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", query.strip())
        data = _cached(
            EODHD_CACHE / "search" / f"{safe_name(safe)}.json",
            lambda: self._get(f"search/{query.strip()}"),
            days=30,
        )
        return data if isinstance(data, list) else []

    def benchmark_symbol(self, sym: str) -> str:
        if sym in self.BENCHMARK_MAP:
            return self.BENCHMARK_MAP[sym]
        if "." not in sym:
            return f"{sym}.US"
        return sym

    def default_symbol(self, c: dict, meta: dict) -> str:
        """Deterministic heuristic EODHD symbol (used before or without exchange list lookup)."""
        t = str(c["ticker"]).split(" / ")[0].strip()
        if meta.get("symbol_rule") == "us":
            return t.replace(".", "-").replace(" ", "-") + ".US"
        ex_name = c.get("exchange") or ""
        ex_code = self.EXCHANGE_MAP.get(ex_name, "US")
        # Clean London trailing dots (e.g. BP. -> BP, TW. -> TW, BT.A -> BT-A)
        if ex_code == "LSE":
            t_clean = t.rstrip(".").replace(".", "-").replace(" ", "-")
            return f"{t_clean}.{ex_code}"
        t_clean = t.rstrip(".").replace(".", "-").replace(" ", "-")
        return f"{t_clean}.{ex_code}"

    def resolve_symbol(self, c: dict, meta: dict) -> str:
        """Fast deterministic EODHD SYMBOL.EXCHANGE resolution (uses cached symbol_map override if present)."""
        key = meta.get("key") or ("us" if meta.get("symbol_rule") == "us" else "eu")
        cid = c["id"]
        map_key = f"{key}:{cid}"
        if map_key in self._symbol_map:
            return self._symbol_map[map_key]
        heur = self.default_symbol(c, meta)
        self._symbol_map[map_key] = heur
        return heur

    def fallback_resolve(self, c: dict, meta: dict) -> str | None:
        """Called only when `default_symbol` returns 404 from EODHD: searches EODHD /api/search/ and exchange list."""
        if settings.OFFLINE:
            return None
        key = meta.get("key") or ("us" if meta.get("symbol_rule") == "us" else "eu")
        cid = c["id"]
        map_key = f"{key}:{cid}"
        heur = self.default_symbol(c, meta)
        ex_name = "US" if meta.get("symbol_rule") == "us" else (c.get("exchange") or "US")
        ex_code = self.EXCHANGE_MAP.get(ex_name, "US")
        raw_t = str(c["ticker"]).split(" / ")[0].strip()

        candidates = []
        for cand in (
            raw_t,
            raw_t.rstrip("."),
            raw_t.replace(" ", "-").replace(".", "-"),
            raw_t.rstrip(".").replace(" ", "-").replace(".", "-"),
            raw_t.replace(" ", ""),
            raw_t.replace(".", ""),
            raw_t.replace(" ", "_"),
            raw_t[:-3].strip() if raw_t.upper().endswith(" FI") else "",
            raw_t[:-4].strip() if raw_t.upper().endswith(" SDB") else "",
        ):
            cand_u = cand.strip().upper()
            if cand_u and cand_u not in candidates:
                candidates.append(cand_u)

        target_name = c.get("company")
        home_iso = str(cid).rsplit(".", 1)[1].upper() if "." in str(cid) else "US"
        home_iso = {"UK": "GB"}.get(home_iso, home_iso)

        def same_issuer(h: dict) -> bool:
            isin = str(h.get("ISIN") or "")
            if len(isin) >= 2:
                return isin[:2].upper() == home_iso or _norm_name(h.get("Name")) == _norm_name(target_name)
            return _norm_name(h.get("Name")) == _norm_name(target_name)

        comp_q = (c.get("company") or "").replace("'", " ").replace("’", " ")
        queries = [comp_q, raw_t.rstrip(".")] if ex_code == "MI" else [raw_t.rstrip("."), comp_q]
        for q in queries:
            if not q:
                continue
            hits = self.search_symbol(q)
            if not hits:
                continue
            # 1. Exact exchange + candidate ticker match
            for h in hits:
                if str(h.get("Exchange")).upper() == ex_code and str(h.get("Code")).upper() in candidates:
                    sym = f"{h['Code']}.{h['Exchange']}"
                    if sym != heur:
                        self._symbol_map[map_key] = sym
                        return sym
            # 2. Exact exchange + company name match
            for h in hits:
                if str(h.get("Exchange")).upper() == ex_code and _same_company(target_name, h.get("Name")):
                    sym = f"{h['Code']}.{h['Exchange']}"
                    if sym != heur:
                        self._symbol_map[map_key] = sym
                        return sym
            # 3. Cross-exchange match: MUST match company name (prefer Frankfurt F for Borsa Italiana listings)
            pref_ex = (
                ("F", "XETRA", "PA", "AS", "STU", "DU", "MU", "MI", "MIL", "LSE", "SW", "MC", "BR", "ST", "CO", "HE", "OL", "VI", "IR", "LS", "WAR", "AT", "TO", "US")
                if ex_code == "MI"
                else ("XETRA", "F", "PA", "AS", "STU", "DU", "MU", "MI", "MIL", "LSE", "SW", "MC", "BR", "ST", "CO", "HE", "OL", "VI", "IR", "LS", "WAR", "AT", "TO", "US")
            )
            matched = []
            for h in hits:
                h_ex = str(h.get("Exchange") or "").upper()
                if h_ex in pref_ex and _same_company(target_name, h.get("Name")) and same_issuer(h):
                    matched.append((pref_ex.index(h_ex), f"{h['Code']}.{h['Exchange']}"))
            if matched:
                matched.sort(key=lambda x: x[0])
                for _, sym in matched:
                    if sym == heur:
                        continue
                    f_test = self.fundamentals(sym)
                    if f_test:
                        s_test = self.annual_series(f_test)
                        if s_test.get("ni") and s_test.get("sales") and not stale_fundamentals(s_test):
                            self._symbol_map[map_key] = sym
                            return sym
        return None

    def fundamentals(self, symbol: str) -> dict | None:
        """Fetch full unfiltered EODHD fundamentals JSON (1 request = 10 API calls) and cache in data/_cache/eodhd/{symbol}.json."""
        path = symbol_cache(symbol)
        data = _cached(
            path,
            lambda: self._get(f"fundamentals/{symbol}"),
            days=settings.FUND_CACHE_DAYS,
            force_refresh=settings.REFRESH_FUNDAMENTALS,
        )
        return data if isinstance(data, dict) and ("Financials" in data or "General" in data) else None

    def eod(self, symbol: str, start: str = "2014-01-01") -> list[dict]:
        """Fetch 12+ years of daily EOD bars (1 request = 1 API call) and cache in data/_cache/eodhd/eod/{symbol}.json."""
        path = symbol_cache(symbol, "eod")
        data = _cached(
            path,
            lambda: self._get(f"eod/{symbol}", {"from": start, "period": "d"}),
            days=settings.EOD_CACHE_DAYS,
        )
        return data if isinstance(data, list) else []

    def splits(self, symbol: str, fund_data: dict | None = None, start: str = "2014-01-01") -> dict[str, float]:
        """Return {ISO_date: split_factor}. Skips API call if LastSplitDate in fundamentals is before `start`."""
        if isinstance(fund_data, dict):
            sd = fund_data.get("SplitsDividends") or {}
            last_split = sd.get("LastSplitDate")
            if not last_split or str(last_split) < start:
                return {}
        path = symbol_cache(symbol, "splits")
        raw = _cached(
            path,
            lambda: self._get(f"splits/{symbol}", {"from": start}),
            days=settings.FUND_CACHE_DAYS,
        )
        out: dict[str, float] = {}
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict) or not item.get("date") or not item.get("split"):
                    continue
                sp_str = str(item["split"])
                if "/" in sp_str:
                    a, b = sp_str.split("/", 1)
                    fa, fb = _f(a), _f(b)
                    if fa and fb and fb > 0:
                        out[str(item["date"])] = fa / fb
        elif isinstance(fund_data, dict):
            sd = fund_data.get("SplitsDividends") or {}
            last_split = sd.get("LastSplitDate")
            fac_str = str(sd.get("LastSplitFactor") or "")
            if last_split and str(last_split) >= start and ":" in fac_str:
                a, b = fac_str.split(":", 1)
                fa, fb = _f(a), _f(b)
                if fa and fb and fb > 0:
                    out[str(last_split)] = fa / fb
        return out

    def fx(self, frm: str | None, to: str | None) -> float | None:
        """Rate to convert 1 unit of `frm` into `to` (handles GBp/GBX/ZAc sub-unit quotes)."""
        if not frm or not to:
            return None
        scale = 1.0
        if frm in ("GBp", "GBX"):
            frm, scale = "GBP", 0.01
        elif frm == "ZAc":
            frm, scale = "ZAR", 0.01
        to_scale = 1.0
        if to in ("GBp", "GBX"):
            to, to_scale = "GBP", 100.0
        elif to == "ZAc":
            to, to_scale = "ZAR", 100.0
        if frm == to:
            return scale * to_scale

        k = (frm, to)
        if k not in self._fx:
            rate = self._fetch_fx_pair(frm, to)
            if rate is None:
                inv = self._fetch_fx_pair(to, frm)
                if inv and inv > 0:
                    rate = 1.0 / inv
            if rate is None and frm != "USD" and to != "USD":
                r1 = self._fetch_fx_pair(frm, "USD") or (1.0 / self._fetch_fx_pair("USD", frm) if self._fetch_fx_pair("USD", frm) else None)
                r2 = self._fetch_fx_pair("USD", to) or (1.0 / self._fetch_fx_pair(to, "USD") if self._fetch_fx_pair(to, "USD") else None)
                if r1 and r2:
                    rate = r1 * r2
            if rate is None:
                # Fallback to static config FX_TO_USD table or legacy Yahoo FX cache
                u_frm, u_to = C.FX_TO_USD.get(frm), C.FX_TO_USD.get(to)
                if u_frm and u_to:
                    rate = u_frm / u_to
            self._fx[k] = rate
        return None if self._fx[k] is None else self._fx[k] * scale * to_scale

    def _fx_history(self, frm: str, to: str) -> list:
        """Daily [date, close] history of frm->to (EODHD {frm}{to}.FOREX since 2010), cached; [] when unavailable."""
        k = (frm, to)
        if k not in self._fx_hist:
            path = EODHD_CACHE / "fx" / f"hist_{frm}{to}.json"

            def fetch():
                bars = self._get(f"eod/{frm}{to}.FOREX", {"from": FX_HISTORY_START, "period": "d"})
                rows = [[str(b["date"]), _f(b.get("close"))] for b in bars if isinstance(b, dict) and b.get("date")] \
                    if isinstance(bars, list) else []
                return [r for r in rows if r[1] and r[1] > 0] or None

            val = _cached(path, fetch, days=settings.FUND_CACHE_DAYS)
            self._fx_hist[k] = val if isinstance(val, list) else []
        return self._fx_hist[k]

    def fx_on(self, frm: str | None, to: str | None, date: str | None) -> tuple[float | None, bool]:
        """(rate converting 1 frm into to at `date`, True if from FX history). Last close on or before the date;
        falls back to the spot rate fx() (False) when no history is cached or the date is outside it."""
        if not frm or not to or frm == to:
            return self.fx(frm, to), True
        if date:
            d = str(date)[:10]
            for pair, invert in (((frm, to), False), ((to, frm), True)):
                hist = self._fx_history(*pair)
                if hist and hist[0][0] <= d:
                    lo, hi = 0, len(hist) - 1
                    while lo < hi:                      # last index with hist[i][0] <= d
                        mid = (lo + hi + 1) // 2
                        if hist[mid][0] <= d:
                            lo = mid
                        else:
                            hi = mid - 1
                    rate = hist[lo][1]
                    return (1.0 / rate if invert else rate), True
        return self.fx(frm, to), False

    def _fetch_fx_pair(self, frm: str, to: str) -> float | None:
        path = EODHD_CACHE / "fx" / f"fx_{frm}{to}.json"
        start = (dt.date.today() - dt.timedelta(days=30)).isoformat()

        def fetch():
            bars = self._get(f"eod/{frm}{to}.FOREX", {"from": start, "period": "d"})
            if isinstance(bars, list) and bars:
                last_close = _f(bars[-1].get("close"))
                if last_close and last_close > 0:
                    return last_close
            return None

        val = _cached(path, fetch, days=settings.EOD_CACHE_DAYS)
        if isinstance(val, (int, float)) and val > 0:
            return float(val)
        # Check legacy yahoo fx cache if offline
        yh_path = CACHE / "yahoo" / f"fx_{frm}{to}.json"
        if yh_path.exists():
            try:
                v = json.loads(yh_path.read_text(encoding="utf-8"))
                if isinstance(v, (int, float)) and v > 0:
                    return float(v)
            except Exception:
                pass
        return None


    @staticmethod
    def _split_adjusted_bars(eod_bars: list[dict], splits: dict[str, float]) -> list[tuple[str, float, float]]:
        """Return [(date_str, split_adj_close, volume)] sorted chronologically.
        Adjusts raw `close` strictly for stock splits (avoiding dividend-reinvestment distortion in historical P/E)."""
        if not eod_bars:
            return []
        sp_events = sorted((d, r) for d, r in (splits or {}).items() if r and r > 0)
        out = []
        for b in eod_bars:
            d = b.get("date")
            c = _f(b.get("close"))
            v = _f(b.get("volume")) or 0.0
            if not d or c is None or c <= 0:
                continue
            factor = 1.0
            for sp_d, sp_r in sp_events:
                if d < sp_d:
                    factor *= sp_r
            out.append((str(d), c / factor, v))
        out.sort(key=lambda x: x[0])
        return out

    def monthly_prices(self, symbol: str, eod_bars: list[dict] | None = None, splits: dict[str, float] | None = None) -> dict[str, float]:
        """{ISO_date_of_month_end_bar: split_adjusted_close} over ~12 years in quote currency."""
        bars = eod_bars if eod_bars is not None else self.eod(symbol)
        adj = self._split_adjusted_bars(bars, splits or {})
        by_ym: dict[str, tuple[str, float]] = {}
        for d, c, _ in adj:
            by_ym[d[:7]] = (d, c)
        return {d: c for d, c in by_ym.values()}

    def year_end_prices(self, symbol: str, eod_bars: list[dict] | None = None, splits: dict[str, float] | None = None) -> dict[int, float]:
        """{calendar_year: last_monthly_close} in quote currency."""
        mp = self.monthly_prices(symbol, eod_bars, splits)
        out: dict[int, float] = {}
        for d, c in sorted(mp.items()):
            out[int(d[:4])] = c
        return out

    def weekly_bars(self, eod_bars: list[dict], splits: dict[str, float] | None = None) -> tuple[list[float], list[float], list[str]]:
        """Aggregate daily EOD bars into weekly (closes, volumes, dates) over the latest ~2.5 years."""
        adj = self._split_adjusted_bars(eod_bars, splits or {})
        if not adj:
            return [], [], []
        cutoff = (dt.date.fromisoformat(adj[-1][0]) - dt.timedelta(days=800)).isoformat()
        recent = [x for x in adj if x[0] >= cutoff]
        by_wk: dict[tuple[int, int], list[tuple[str, float, float]]] = {}
        for d, c, v in recent:
            iso = dt.date.fromisoformat(d).isocalendar()
            by_wk.setdefault((iso[0], iso[1]), []).append((d, c, v))
        closes, volumes, dates = [], [], []
        for wk in sorted(by_wk):
            items = by_wk[wk]
            dates.append(items[-1][0])
            closes.append(items[-1][1])
            volumes.append(sum(x[2] for x in items))
        return closes, volumes, dates

    @staticmethod
    def _detect_currencies(symbol: str, fund_data: dict | None, latest_price: float | None) -> tuple[str | None, str | None]:
        """Return (quote_currency, fin_currency), normalizing LSE pence to 'GBp' and statement currency to 'GBP'."""
        if not isinstance(fund_data, dict):
            return None, None
        gen = fund_data.get("General") or {}
        hl = fund_data.get("Highlights") or {}
        ss = fund_data.get("SharesStats") or {}
        fin = fund_data.get("Financials") or {}
        inc = fin.get("Income_Statement") or {}
        yearly = inc.get("yearly") or {}

        q_ccy = gen.get("CurrencyCode") or None
        fin_ccy = inc.get("currency_symbol")
        if yearly:
            latest_dt = max(yearly)
            fin_ccy = (yearly[latest_dt] or {}).get("currency_symbol") or fin_ccy
        fin_ccy = fin_ccy or q_ccy
        if fin_ccy in ("GBX", "GBp"):
            fin_ccy = "GBP"
        elif fin_ccy == "ZAc":
            fin_ccy = "ZAR"

        if q_ccy in ("GBX", "GBp"):
            q_ccy = "GBp"
        elif q_ccy == "GBP" and symbol.endswith(".LSE"):
            # Verify whether EOD price is in pence (GBp) or pounds (GBP)
            mcap = _f(hl.get("MarketCapitalization"))
            sh = _f(ss.get("SharesOutstanding"))
            if latest_price and mcap and sh and sh > 0 and (latest_price * sh) / mcap > 25.0:
                q_ccy = "GBp"
            elif latest_price and latest_price > 100.0:
                q_ccy = "GBp"
        return q_ccy, fin_ccy

    def quote(self, symbol: str, fund_data: dict | None = None, eod_bars: list[dict] | None = None,
              series: dict | None = None) -> dict:
        """Build quote dict {price, currency, shares, fin_currency, dps, market_cap_raw} from EODHD data."""
        fund = fund_data if fund_data is not None else self.fundamentals(symbol)
        bars = eod_bars if eod_bars is not None else self.eod(symbol)
        hl = (fund or {}).get("Highlights") or {}
        ss = (fund or {}).get("SharesStats") or {}
        sd = (fund or {}).get("SplitsDividends") or {}
        val = (fund or {}).get("Valuation") or {}

        px = _f(bars[-1].get("close")) if bars else None
        q_ccy, fin_ccy = self._detect_currencies(symbol, fund, px)
        mcap_raw = _f(hl.get("MarketCapitalization"))
        if mcap_raw is None and _f(hl.get("MarketCapitalizationMln")):
            mcap_raw = _f(hl.get("MarketCapitalizationMln")) * 1e6

        sh_stats = _f(ss.get("SharesOutstanding"))
        sh_series = (series or {}).get("shares") or {}
        latest_stmt_sh = sh_series[max(sh_series)] if sh_series else None

        # If EOD price is missing, infer from MarketCapitalization / SharesOutstanding
        if px is None and mcap_raw and sh_stats and sh_stats > 0:
            px = mcap_raw / sh_stats
            if q_ccy == "GBp":
                px *= 100.0

        # Reconcile share count for market_cap_m so multi-class shares (e.g. ROG.SW, MAERSK-B.CO, BRK-B.US)
        # use whole-firm share count on the exact same basis as `price` and `owner_eps`
        px_in_main_ccy = (px * 0.01) if (px and q_ccy in ("GBp", "GBX", "ZAc")) else px
        imp_mcap_sh = (mcap_raw / px_in_main_ccy) if (mcap_raw and px_in_main_ccy and px_in_main_ccy > 0) else None

        shares = sh_stats
        share_flag = None
        if latest_stmt_sh and latest_stmt_sh > 0:
            if not shares or shares <= 0:
                shares = latest_stmt_sh
            elif not (0.75 <= shares / latest_stmt_sh <= 1.33):
                market_pair = bool(imp_mcap_sh and 0.95 <= imp_mcap_sh / shares <= 1.05)
                if imp_mcap_sh and 0.75 <= imp_mcap_sh / latest_stmt_sh <= 1.33 and not market_pair:
                    # SharesStats counts a single share class while statements (aligned to the traded class in
                    # annual_series) and the market cap count the whole firm (ROG, BRK-B, INVE-B): keep that basis
                    shares = imp_mcap_sh
                else:
                    # v7.2: SharesStats (and the market cap) disagree with the latest statements — a merger, issuance,
                    # consolidation or buyback after the fiscal year (KMB, WAT, OMC) or a statement glitch (AC.PA).
                    # Market cap uses the current count; the valuation is blocked until reviewed (fetch_market_data).
                    share_flag = round(shares / latest_stmt_sh, 2)
        elif imp_mcap_sh and (not shares or not (0.75 <= shares / imp_mcap_sh <= 1.33)):
            shares = imp_mcap_sh

        dps = _f(hl.get("DividendShare")) or _f(sd.get("ForwardAnnualDividendRate"))
        # Note: DividendShare is in main currency (e.g. GBP or EUR/USD); if quote_currency is GBp, convert DPS to GBp
        if dps is not None and q_ccy in ("GBp", "GBX"):
            dy_hl = _f(hl.get("DividendYield")) or _f(sd.get("ForwardAnnualDividendYield"))
            if px and dy_hl and dy_hl > 0 and abs((dps / px) - dy_hl) > abs((dps * 100.0 / px) - dy_hl):
                dps *= 100.0

        return {
            "price": px,
            "currency": q_ccy,
            "shares": shares,
            "fin_currency": fin_ccy,
            "dps": dps,
            "market_cap_raw": mcap_raw,
            "share_basis_flag": share_flag,
            "statement_shares": latest_stmt_sh,
            "trailing_pe": _f(val.get("TrailingPE")) or _f(hl.get("PERatio")),
            "forward_pe": _f(val.get("ForwardPE")),
        }

    def annual_series(self, fund_data: dict, latest_price: float | None = None,
                      splits: dict[str, float] | None = None, ccy_override: str | None = None,
                      last_bar_date: str | None = None) -> dict:
        """Extract clean multi-decade annual series from EODHD Fundamentals JSON.
        ccy_override ("convert" / "keep") forces the reporting-currency block decision (fetch_market_data
        CCY_SWITCH_OVERRIDES); last_bar_date bounds which post-FY splits are applied to statement share counts."""
        fin = fund_data.get("Financials") or {}
        inc = (fin.get("Income_Statement") or {}).get("yearly") or {}
        qtr_inc = (fin.get("Income_Statement") or {}).get("quarterly") or {}
        bs = (fin.get("Balance_Sheet") or {}).get("yearly") or {}
        cf = (fin.get("Cash_Flow") or {}).get("yearly") or {}
        hl = fund_data.get("Highlights") or {}
        ss = fund_data.get("SharesStats") or {}
        gen = fund_data.get("General") or {}
        earn_ann = (fund_data.get("Earnings") or {}).get("Annual") or {}

        is_bank = (
            "Bank" in str(gen.get("Industry") or "")
            or gen.get("GicGroup") == "Banks"
            or gen.get("GicIndustry") in ("Banks", "Consumer Finance")
        )

        osh_raw = (fund_data.get("outstandingShares") or {}).get("annual") or {}
        osh_by_yr: dict[int, float] = {}
        for v in osh_raw.values():
            if isinstance(v, dict) and v.get("date") and _f(v.get("shares")):
                try:
                    osh_by_yr[int(str(v["date"])[:4])] = float(_f(v["shares"]))
                except (ValueError, TypeError):
                    pass

        keys = ("sales", "opcost", "ni", "minority_interest", "eps", "eps_street", "ebit", "pretax", "tax", "interest",
                "ocf", "capex", "sbc", "da", "dividends",
                "equity", "nci", "debt", "st_debt", "cash", "cash_sti", "lease", "goodwill", "intang", "assets", "shares")
        out: dict[str, dict[int, float]] = {k: {} for k in keys}
        out["period_end"] = {}          # {fy: "YYYY-MM-DD"} (strings; used for point-in-time availability in par.py)
        inc_ccys: dict[int, str] = {}
        bs_ccys: dict[int, str] = {}
        cf_ccys: dict[int, str] = {}
        bs_shares: dict[int, float] = {}

        all_dates = sorted(set(inc.keys()) | set(bs.keys()) | set(cf.keys()))
        inc_dates = sorted(inc.keys())
        for d_str in all_dates:
            try:
                day = dt.date.fromisoformat(d_str)
            except ValueError:
                continue
            fy = day.year if day.month > 6 else day.year - 1
            i_r, b_r, c_r = inc.get(d_str) or {}, bs.get(d_str) or {}, cf.get(d_str) or {}

            rev_raw = _fval(i_r, "totalRevenue", "grossProfit")
            gp_raw = _fval(i_r, "grossProfit")
            op_inc = _fval(i_r, "operatingIncome")

            # Skip trailing single-quarter transition stubs in yearly table (e.g. FERG.US 2026-07-31)
            if inc_dates and d_str == inc_dates[-1] and len(inc_dates) >= 2 and rev_raw and rev_raw > 0:
                prev_rev = _fval(inc.get(inc_dates[-2]) or {}, "totalRevenue", "grossProfit")
                q_rev = _fval(qtr_inc.get(d_str) or {}, "totalRevenue", "grossProfit")
                if prev_rev and prev_rev > 0 and q_rev and q_rev > 0:
                    if rev_raw < 0.45 * prev_rev and 0.80 <= (rev_raw / q_rev) <= 1.25:
                        continue

            # For Banks & Consumer Lenders, grossProfit is Net Banking Revenue (NII + Non-Interest Income),
            # stripping out deposit interest expense (costOfRevenue) that distorts gross revenue in rate cycles.
            if (
                is_bank
                and gp_raw is not None
                and gp_raw > 0
                and (rev_raw is None or gp_raw >= 0.25 * rev_raw)
                and (op_inc is None or gp_raw > op_inc)
            ):
                sales = gp_raw
            else:
                sales = rev_raw

            ni_common = _fval(i_r, "netIncomeApplicableToCommonShares")
            ni_base = _fval(i_r, "netIncome", "netIncomeFromContinuingOps")
            if ni_common is not None and ni_base is not None and ni_base > 0 and ni_common > 2.5 * ni_base:
                ni = ni_base
            else:
                ni = ni_common if ni_common is not None else ni_base
            if ni is None:
                ni = _fval(c_r, "netIncome")
            # Require at least revenue or net income to count as a reported fiscal year
            if sales is None and ni is None:
                continue

            def _main_ccy(c):
                return "GBP" if c in ("GBX", "GBp") else ("ZAR" if c == "ZAc" else c)

            r_ccy = _main_ccy(i_r.get("currency_symbol") or b_r.get("currency_symbol") or c_r.get("currency_symbol"))
            if r_ccy:
                inc_ccys[fy] = str(r_ccy)
            if b_r.get("currency_symbol"):
                bs_ccys[fy] = str(_main_ccy(b_r["currency_symbol"]))
            if c_r.get("currency_symbol"):
                cf_ccys[fy] = str(_main_ccy(c_r["currency_symbol"]))

            pretax = _fval(i_r, "incomeBeforeTax")
            tax = _fval(i_r, "incomeTaxExpense", "taxProvision")
            interest = _fval(i_r, "interestExpense")
            mi = _fval(i_r, "minorityInterest") if _fval(b_r, "commonStockTotalEquity") is None else None

            # Prefer operatingIncome (true GAAP operating profit = Revenue - COGS - OpEx);
            # for banks/insurers where operatingIncome may be absent or >= revenue, fall back cleanly
            ebit_raw = _fval(i_r, "ebit")
            if op_inc is not None and (sales is None or op_inc < sales):
                ebit = op_inc
            elif ebit_raw is not None and (sales is None or ebit_raw < sales):
                ebit = ebit_raw
            elif pretax is not None and (sales is None or pretax < sales):
                ebit = pretax
            else:
                ebit = op_inc if op_inc is not None else ebit_raw

            # Direct Recurring Operating Cost (OpCost = COGS + OpEx), including years with GAAP operating losses (ebit <= 0)
            opcost = (sales - ebit) if (sales is not None and ebit is not None and sales > ebit and sales > 0) else None
            if not is_bank and sales and sales > 0:
                cor = _fval(i_r, "costOfRevenue")
                sga = _fval(i_r, "sellingGeneralAdministrative")
                rnd = _fval(i_r, "researchDevelopment")
                opex_tot = _fval(i_r, "totalOperatingExpenses")
                if cor and cor > 0 and sga and sga > 0:
                    direct_cost = cor + sga + max(0.0, rnd or 0.0)
                    if 0.35 * sales <= direct_cost <= 1.25 * sales:
                        if (opex_tot is not None and opex_tot < 0) or (
                            ebit is not None and ebit <= 0 and opex_tot and opex_tot > 2.2 * (sga + max(0.0, rnd or 0.0))
                        ):
                            opcost = direct_cost

            ocf = _fval(c_r, "totalCashFromOperatingActivities")
            capex = _fval(c_r, "capitalExpenditures")
            sbc = _fval(c_r, "stockBasedCompensation")
            # Deterministic D&A priority (not max): cash-flow depreciation → income-statement D&A → reconciled
            # depreciation. reconciledDepreciation often includes impairments (e.g. DGE FY26 2,480 vs 747 D&A).
            da_raw = None
            da_opts = [x for x in (_fval(c_r, "depreciation"), _fval(i_r, "depreciationAndAmortization"),
                                   _fval(i_r, "reconciledDepreciation")) if x is not None]
            for da_src in da_opts:
                if da_src != 0:
                    da_raw = da_src
                    break
            if da_raw is None and da_opts:
                da_raw = da_opts[0]
            da = abs(da_raw) if da_raw is not None else None
            div = _fval(c_r, "dividendsPaid")

            eq = _fval(b_r, "totalStockholderEquity", "commonStockTotalEquity")
            nci = _fval(b_r, "noncontrollingInterestInConsolidatedEntity")
            debt = _fval(b_r, "longTermDebt", "longTermDebtTotal")
            st_debt = _fval(b_r, "shortLongTermDebt", "shortTermDebt") if debt is not None else None
            if debt is None:
                debt = _fval(b_r, "shortLongTermDebtTotal")      # already total (long- + short-term) debt
            cash = _fval(b_r, "cashAndEquivalents", "cash", "cashAndShortTermInvestments")
            cash_sti = _fval(b_r, "cashAndShortTermInvestments", "cash", "cashAndEquivalents")
            if cash_sti is not None and cash is not None and cash_sti < cash:
                cash_sti = cash
            lease = _fval(b_r, "capitalLeaseObligations")
            gw = _fval(b_r, "goodWill")
            intang = _fval(b_r, "intangibleAssets")
            assets = _fval(b_r, "totalAssets")

            bs_sh = _fval(b_r, "commonStockSharesOutstanding")
            if bs_sh and bs_sh > 0:
                bs_shares[fy] = bs_sh
            o_sh = osh_by_yr.get(fy)
            sh = o_sh if (o_sh and o_sh > 0) else bs_sh
            if o_sh and bs_sh and bs_sh > 0 and not (0.33 <= o_sh / bs_sh <= 3.0):
                # If one of the two share sources has a unit outlier, pick the one closer to SharesStats
                sh_ref = _f(ss.get("SharesOutstanding"))
                if sh_ref and sh_ref > 0:
                    sh = o_sh if abs(math.log(o_sh / sh_ref)) <= abs(math.log(bs_sh / sh_ref)) else bs_sh

            e_st = _f((earn_ann.get(d_str) or {}).get("epsActual"))

            for k, val in (
                ("sales", sales), ("opcost", opcost), ("ni", ni), ("minority_interest", mi), ("ebit", ebit), ("pretax", pretax),
                ("tax", tax), ("interest", interest), ("ocf", ocf), ("capex", capex),
                ("sbc", sbc), ("da", da), ("dividends", div), ("equity", eq), ("nci", nci),
                ("debt", debt), ("st_debt", st_debt), ("cash", cash), ("cash_sti", cash_sti), ("lease", lease),
                ("goodwill", gw), ("intang", intang),
                ("assets", assets), ("shares", sh), ("eps_street", e_st),
            ):
                if val is not None:
                    out[k][fy] = val
            out["period_end"][fy] = d_str

        # 0. Reconcile IFRS PP&E-only EODHD CapEx and missing D&A/SBC against cached Yahoo statements (which sum PP&E + Intangibles).
        pt_sym = (fund_data.get("General") or {}).get("PrimaryTicker")
        if pt_sym and out["period_end"]:
            y_stmt_path = next(
                (p for p in (CACHE / "yahoo" / f"stmt_{safe_name(ys)}.json" for ys in _yahoo_sym_candidates(pt_sym))
                 if p.exists()),
                None,
            )
            if y_stmt_path is not None:
                try:
                    y_cf = (json.loads(y_stmt_path.read_text(encoding="utf-8")).get("cf") or {})
                    y_cap = y_cf.get("Capital Expenditure") or {}
                    y_ocf = y_cf.get("Operating Cash Flow") or {}
                    y_da = y_cf.get("Depreciation And Amortization") or {}
                    y_sbc = y_cf.get("Stock Based Compensation") or {}
                except Exception:
                    y_cap, y_ocf, y_da, y_sbc = {}, {}, {}, {}
                for fy, d_str in out["period_end"].items():
                    yv, yo = _f(y_cap.get(d_str)), _f(y_ocf.get(d_str))
                    eo = out["ocf"].get(fy)
                    if not (eo and yo and 0.90 <= abs(yo / eo) <= 1.10):
                        continue
                    ec = out["capex"].get(fy)
                    if yv is not None and abs(yv) > 0 and (ec is None or abs(yv) > 1.5 * abs(ec)):
                        out["capex"][fy] = abs(yv)
                    if out["da"].get(fy) is None:
                        yda = _f(y_da.get(d_str))
                        if yda is not None:
                            out["da"][fy] = abs(yda)
                    if out["sbc"].get(fy) is None:
                        ysbc = _f(y_sbc.get(d_str))
                        if ysbc is not None:
                            out["sbc"][fy] = abs(ysbc)

        # 1. Reporting Currency Transition Normalization (e.g. GMAB DKK->USD, NSIS-B DKK->EUR, CPG GBP->USD):
        # Each section (income, balance sheet, cash flow) is checked against its own currency label so partial
        # restatements (NSIS-B 2022 income restated to EUR, balance sheet / cash flow still DKK; DGE FY23) convert only
        # the items still in the old currency. Conversions use the FX rate at each fiscal period end (fx_on).
        # - Close pairs (|ln fx| < 0.4, e.g. GBP/USD, CHF/USD): growth and FX moves are the same size, so the contiguous
        #   old-currency block before the final target-currency run is decided as ONE unit on 3-year medians (a COVID
        #   trough next to the switch no longer leaves CPG FY2014-19 in GBP inside a USD series).
        # - Far pairs (DKK/NOK/SEK -> EUR) and isolated label islands: per-year value test against the next year.
        # Ambiguous or unresolved switches add '[auto] currency switch unresolved …' (valuation No data, see gates.py).
        out["ccy"] = dict(inc_ccys)     # {fy: currency of the income statement after normalisation}
        out["_notes"] = []
        if inc_ccys and len(set(inc_ccys.values()) | set(bs_ccys.values()) | set(cf_ccys.values())) > 1 and out["sales"]:
            target_ccy = inc_ccys[max(inc_ccys)]
            inc_keys = ("sales", "opcost", "ni", "minority_interest", "ebit", "pretax", "tax", "interest")
            bs_keys = ("equity", "nci", "debt", "st_debt", "cash", "cash_sti", "lease", "goodwill", "intang", "assets")
            cf_keys = ("ocf", "capex", "sbc", "da", "dividends")
            yrs_sorted = sorted(out["sales"])
            spot_used = False
            unresolved: list[str] = []
            # integrity notes only for years the valuation uses (10-year g0 / ROIC / Owner EPS windows)
            window_start = yrs_sorted[-1] - 10

            def _sec_val(ref_k: str, yr: int) -> float:
                v = abs(out[ref_k].get(yr) or 0.0)
                if ref_k == "assets" and v > 0:
                    gwi_yr = abs(out["goodwill"].get(yr) or 0.0) + abs(out["intang"].get(yr) or 0.0)
                    return max(0.25 * v, v - gwi_yr)
                return v

            def _rate(frm: str, yr: int) -> float | None:
                nonlocal spot_used
                rate, hist = self.fx_on(frm, target_ccy, out["period_end"].get(yr))
                spot_used = spot_used or (rate is not None and not hist and yr > window_start)
                return rate

            def _convert(sec_keys, sec_ref_key, yr, rate):
                for mk in sec_keys:
                    if yr in out[mk]:
                        out[mk][yr] = out[mk][yr] * rate
                if sec_ref_key == "sales":
                    out["ccy"][yr] = target_ccy

            for sec_ref_key, sec_keys, sec_lab in (("sales", inc_keys, inc_ccys), ("assets", bs_keys, bs_ccys),
                                                   ("ocf", cf_keys, cf_ccys)):
                if not out[sec_ref_key]:
                    continue
                # a year's old currency: its own section label, else the income-statement label
                lab = {y: (sec_lab.get(y) if sec_lab.get(y) not in (None, target_ccy) else inc_ccys.get(y))
                       for y in yrs_sorted}
                k = len(yrs_sorted) - 1
                while k > 0 and lab.get(yrs_sorted[k - 1]) in (None, target_ccy):
                    k -= 1
                block: list[int] = []
                j = k - 1
                while (j >= 0 and lab.get(yrs_sorted[j]) not in (None, target_ccy)
                       and lab[yrs_sorted[j]] == lab[yrs_sorted[k - 1]]):
                    block.insert(0, yrs_sorted[j])
                    j -= 1
                spot = self.fx(lab[block[0]], target_ccy) if block else None
                if not (spot and spot > 0 and abs(math.log(spot)) < CCY_CLOSE_PAIR_LOG):
                    block = []
                block_set = set(block)
                if block:
                    rates = {y: _rate(lab[y], y) for y in block}
                    tail = [y for y in block[-3:] if _sec_val(sec_ref_key, y) > 0 and rates.get(y)]
                    head = [y for y in yrs_sorted[k:k + 3] if _sec_val(sec_ref_key, y) > 0]
                    if tail and head:
                        ref = median(_sec_val(sec_ref_key, y) for y in head)
                        raw = median(_sec_val(sec_ref_key, y) for y in tail)
                        conv = median(_sec_val(sec_ref_key, y) * rates[y] for y in tail)
                        margin = abs(math.log(raw / ref)) - abs(math.log(conv / ref))
                        forced = ccy_override in ("convert", "keep")
                        if (ccy_override == "convert") if forced else margin > 0:
                            for y in block:
                                if rates.get(y):
                                    _convert(sec_keys, sec_ref_key, y, rates[y])
                        if sec_ref_key == "sales" and not forced and yrs_sorted[k] > window_start:
                            b0, b1 = block[-1], yrs_sorted[k]
                            jump = (_sec_val("sales", b1) / _sec_val("sales", b0)) if _sec_val("sales", b0) > 0 else None
                            if abs(margin) < CCY_AMBIGUOUS_MARGIN:
                                unresolved.append(f"FY{b1}: {lab[b0]}→{target_ccy} ambiguous by value")
                            elif jump is not None and not (0.75 <= jump <= 1.33):
                                unresolved.append(f"FY{b1}: revenue ×{jump:.2f} at the {lab[b0]}→{target_ccy} switch")

                ref_val = _sec_val(sec_ref_key, yrs_sorted[-1])
                for idx in range(len(yrs_sorted) - 2, -1, -1):
                    y = yrs_sorted[idx]
                    y_ccy = lab.get(y)
                    cur_val = _sec_val(sec_ref_key, y)
                    if not (cur_val > 0 and ref_val > 0):
                        continue
                    if y not in block_set and y_ccy and y_ccy != target_ccy:
                        fx_rate = _rate(y_ccy, y)
                        if fx_rate and fx_rate > 0:
                            # Value-based test (no FX band): convert only when it shrinks the year-on-year jump, so
                            # GBP→USD (DGE FY22) is converted while mislabelled years already in target currency are not.
                            raw_ratio = cur_val / ref_val
                            adj_ratio = (cur_val * fx_rate) / ref_val
                            if abs(math.log(adj_ratio)) + 0.02 < abs(math.log(raw_ratio)):
                                _convert(sec_keys, sec_ref_key, y, fx_rate)
                                cur_val = _sec_val(sec_ref_key, y)
                    ref_val = cur_val

            # Latest year among the first 2 in a new currency: its revenue must match the TTM figure (RTO FY2025 is
            # labelled USD but carries a GBP-converted value).
            last_old = next((y for y in reversed(yrs_sorted) if inc_ccys.get(y) not in (None, target_ccy)), None)
            rev_ttm = _f(hl.get("RevenueTTM"))
            last_rev = out["sales"].get(yrs_sorted[-1])
            if (ccy_override not in ("convert", "keep") and last_old is not None
                    and len([y for y in yrs_sorted if y > last_old]) <= 2 and rev_ttm and last_rev and last_rev > 0
                    and not (0.75 <= rev_ttm / last_rev <= 1.33)):
                unresolved.append(f"FY{yrs_sorted[-1]} revenue ×{rev_ttm / last_rev:.2f} vs TTM after the switch")
            if unresolved:
                out["_notes"].append("currency switch unresolved (" + "; ".join(unresolved) + ")")
            if spot_used:
                out["_notes"].append("FX history n/a — spot rate used for the currency switch")

        # 2. Historical Share Count Split / Glitch Reconciliation:
        # Reconcile single-year unadjusted pre-split share counts (e.g. SAMPO 2023 1/5th, SQN 2022 1/10th, SFZN 2023 1/10th)
        # and unadjusted historical pre-split share counts against the latest share count basis.
        if len(out["shares"]) >= 3:
            sh_yrs = sorted(out["shares"])
            # First pass: fix isolated 1-year share count glitches where year y jumps by >1.85x or <0.54x vs BOTH neighbors
            for i in range(1, len(sh_yrs) - 1):
                y_prev, y_cur, y_next = sh_yrs[i - 1], sh_yrs[i], sh_yrs[i + 1]
                s_prev, s_cur, s_next = out["shares"][y_prev], out["shares"][y_cur], out["shares"][y_next]
                if s_prev > 0 and s_cur > 0 and s_next > 0 and (0.75 <= s_prev / s_next <= 1.33):
                    r_prev = s_cur / s_prev
                    if r_prev < 0.54 or r_prev > 1.85:
                        out["shares"][y_cur] = 0.5 * (s_prev + s_next)
            # Also check if the very last year in `out["shares"]` is an isolated 2x/0.5x glitch relative to SharesOutstanding AND prior year (e.g. HON 2025)
            sh_ref = _f(ss.get("SharesOutstanding"))
            if sh_ref and sh_ref > 0 and len(sh_yrs) >= 2:
                y_last, y_prev = sh_yrs[-1], sh_yrs[-2]
                s_last, s_prev = out["shares"][y_last], out["shares"][y_prev]
                if s_last > 0 and s_prev > 0 and (0.75 <= s_prev / sh_ref <= 1.33):
                    if s_last / sh_ref > 1.75 or s_last / sh_ref < 0.57:
                        out["shares"][y_last] = sh_ref
            # Latest year deviates > 15% from the prior year while the balance-sheet count agrees with it (±5%):
            # the outstandingShares figure is the glitch (HEIO FY2025 362.9m vs 281m) -> use the balance-sheet count
            y_last, y_prev = sh_yrs[-1], sh_yrs[-2]
            s_last, s_prev, b_last = out["shares"][y_last], out["shares"][y_prev], bs_shares.get(y_last)
            if s_last > 0 and s_prev > 0 and b_last and not (0.85 <= s_last / s_prev <= 1.18) and 0.95 <= b_last / s_prev <= 1.05:
                out["shares"][y_last] = b_last
            # Second pass: if a recent stock split occurred (`splits` or `LastSplitFactor`) and earlier years
            # are unadjusted by that exact split factor, adjust them to the current post-split basis
            sd = fund_data.get("SplitsDividends") or {}
            cand_factors: list[float] = []
            for sp_d, sp_r in (splits or {}).items():
                if sp_d >= "2019-01-01" and sp_r and (sp_r >= 1.8 or sp_r <= 0.55):
                    cand_factors.append(sp_r)
            fac_str = str(sd.get("LastSplitFactor") or "")
            last_sp_dt = str(sd.get("LastSplitDate") or "")
            if last_sp_dt >= "2019-01-01" and ":" in fac_str:
                a_s, b_s = fac_str.split(":", 1)
                fa, fb = _f(a_s), _f(b_s)
                if fa and fb and fb > 0:
                    r_sp = fa / fb
                    if (r_sp >= 1.8 or r_sp <= 0.55) and not any(abs(r_sp - x) < 0.05 for x in cand_factors):
                        cand_factors.append(r_sp)
            if cand_factors:
                latest_sh = out["shares"][sh_yrs[-1]]
                for y in sh_yrs[:-1]:
                    s_y = out["shares"][y]
                    if s_y > 0 and latest_sh > 0:
                        ratio_to_latest = latest_sh / s_y
                        for cf_val in cand_factors:
                            if 0.72 <= (ratio_to_latest / cf_val) <= 1.38:
                                out["shares"][y] = s_y * cf_val
                                break

        # 2b. Split / consolidation of ANY ratio after the latest fiscal year (JMAT 3:4 on 2026-08-17 after the Mar-2026
        # year end): every statement count is pre-split while the price is post-split. Rescale all years when the
        # current SharesStats count confirms the factor (±10%) AND visibly disagrees with the statements (> 15%), so
        # small spin-off price adjustments (SPGI 1.057) never rescale shares; splits after the last price bar wait.
        pe_last = out["period_end"].get(max(out["period_end"])) if out["period_end"] else None
        sh_now = _f(ss.get("SharesOutstanding"))
        if pe_last and sh_now and sh_now > 0 and out["shares"] and out["shares"][max(out["shares"])] > 0:
            latest_sh = out["shares"][max(out["shares"])]
            gap = sh_now / latest_sh
            for sp_d, sp_r in sorted((splits or {}).items()):
                if (sp_d > str(pe_last)[:10] and (last_bar_date is None or sp_d <= str(last_bar_date)[:10])
                        and sp_r and sp_r > 0 and abs(math.log(gap)) > 0.15 and 0.90 <= gap / sp_r <= 1.10):
                    out["shares"] = {y: v * sp_r for y, v in out["shares"].items()}
                    break

        # 3. Multi-class / ADR share-basis alignment:
        # Check if statement shares differ by a class/ADR multiplier from traded share basis (e.g. BRK-B 1:1500)
        if out["shares"] and out["ni"]:
            last_fy = max(out["shares"])
            last_sh = out["shares"][last_fy]
            mcap = _f(hl.get("MarketCapitalization"))
            gen_ccy = (fund_data.get("General") or {}).get("CurrencyCode")
            px_main = (latest_price * 0.01) if (latest_price and gen_ccy in ("GBX", "GBp", "ZAc")) else latest_price
            sh_out_ref = _f(ss.get("SharesOutstanding"))
            imp_mcap_sh = (mcap / px_main) if (mcap and px_main and px_main > 0) else sh_out_ref
            eps_hl = _f(hl.get("DilutedEpsTTM")) or _f(hl.get("EarningsShare"))
            last_ni = out["ni"].get(last_fy)
            if (
                imp_mcap_sh
                and last_sh > 0
                and not (0.40 <= last_sh / imp_mcap_sh <= 2.50)
                and not (sh_out_ref and 0.40 <= last_sh / sh_out_ref <= 2.50)
            ):
                # Verify via Highlights EPS whether traded price is on `imp_mcap_sh` per-share basis
                if eps_hl and eps_hl > 0 and last_ni and last_ni > 0:
                    imp_eps_sh = last_ni / eps_hl
                    if 0.50 <= imp_eps_sh / imp_mcap_sh <= 2.0 and not (0.40 <= last_sh / imp_eps_sh <= 2.50):
                        scale_sh = imp_mcap_sh / last_sh
                        out["shares"] = {y: v * scale_sh for y, v in out["shares"].items()}

        # Compute clean GAAP EPS = NI / shares so `implied_shares` in metrics.py is never corrupted by Non-GAAP Street EPS
        for y, n_val in out["ni"].items():
            sh_val = out["shares"].get(y)
            if n_val is not None and sh_val and sh_val > 0:
                out["eps"][y] = n_val / sh_val

        # Impairment guard on D&A (after currency normalisation so all years are on the same basis)
        out["da"] = metrics.clean_da(out["da"], out["capex"])

        return out

    def panel_rows(self, cid: str, ticker: str, symbol: str, fund_data: dict,
                   series: dict | None = None, ye_prices: dict[int, float] | None = None) -> list[dict]:
        """Build multi-year historical fundamental panel rows (PANEL_FIELDS) for a company."""
        fin = fund_data.get("Financials") or {}
        inc = (fin.get("Income_Statement") or {}).get("yearly") or {}
        bs = (fin.get("Balance_Sheet") or {}).get("yearly") or {}
        cf = (fin.get("Cash_Flow") or {}).get("yearly") or {}
        s = series if series is not None else self.annual_series(fund_data)
        _, fin_ccy = self._detect_currencies(symbol, fund_data, None)

        tax_rate = {
            y: (s["tax"][y] / s["pretax"][y])
            for y in s.get("tax", {})
            if s.get("pretax", {}).get(y)
        }
        eq_ic, debt_ic = metrics.ic_inputs(s)
        roic_g, roic_t = metrics.roic_series(
            s.get("ebit", {}), tax_rate, eq_ic, debt_ic,
            {**s.get("cash", {}), **s.get("cash_sti", {})}, s.get("goodwill", {}), s.get("intang", {}), s.get("assets", {}),
        )
        fcf_ser = metrics.true_fcf(s.get("ocf", {}), s.get("capex", {}), s.get("sbc", {}), s.get("da", {}), s.get("lease", {}))
        oe_ser = par.owner_eps_series(s)

        by_fy_dates: dict[int, str] = {}
        for d_str in sorted(set(inc.keys()) | set(bs.keys()) | set(cf.keys())):
            try:
                day = dt.date.fromisoformat(d_str)
                fy = day.year if day.month > 6 else day.year - 1
                by_fy_dates[fy] = d_str
            except ValueError:
                continue

        rows = []
        m = lambda v: round(v / 1e6, 3) if v is not None else None
        r4 = lambda v: round(v, 4) if v is not None else None

        for fy in sorted(by_fy_dates):
            d_str = by_fy_dates[fy]
            i_r, b_r, c_r = inc.get(d_str) or {}, bs.get(d_str) or {}, cf.get(d_str) or {}
            rev = s["sales"].get(fy)
            ni = s["ni"].get(fy)
            if rev is None and ni is None:
                continue
            ebit = s["ebit"].get(fy)
            da = s["da"].get(fy)
            pretax = s["pretax"].get(fy)
            tax = s["tax"].get(fy)
            tr = tax_rate.get(fy)
            eff_tr = metrics.DEFAULT_TAX if (tr is None or not (0.0 <= tr <= 0.40)) else tr
            nopat = ebit * (1.0 - eff_tr) if ebit is not None else None

            eq = s["equity"].get(fy)
            debt = s["debt"].get(fy)
            cash = s["cash"].get(fy)
            cash_op = (s.get("cash_sti") or {}).get(fy, cash)
            gw = s["goodwill"].get(fy)
            intang = s["intang"].get(fy)
            ic_g = (eq_ic[fy] + (debt_ic.get(fy) or 0.0) - (cash_op or 0.0)) if fy in eq_ic else None
            ic_t = max(ic_g - ((gw or 0.0) + (intang or 0.0)), (1.0 / 3.0) * ic_g) if (ic_g is not None and ic_g > 0) else None
            tbv = (eq - ((gw or 0.0) + (intang or 0.0))) if eq is not None else None

            ocf = s["ocf"].get(fy)
            capex = s["capex"].get(fy)
            sbc = s["sbc"].get(fy)
            div = s["dividends"].get(fy)
            fcf_rep = _fval(c_r, "freeCashFlow")
            o_fcf = fcf_ser.get(fy)
            buybacks_raw = _fval(c_r, "salePurchaseOfStock")
            buybacks = -buybacks_raw if buybacks_raw is not None else None

            sh = s["shares"].get(fy)
            st_debt = _fval(b_r, "shortLongTermDebt", "shortTermDebt")
            tot_debt = _fval(b_r, "shortLongTermDebtTotal", "longTermDebtTotal") or ((debt or 0.0) + (st_debt or 0.0) if (debt is not None or st_debt is not None) else None)
            net_debt = _fval(b_r, "netDebt")
            if net_debt is None and tot_debt is not None and cash is not None:
                net_debt = tot_debt - cash

            rows.append({
                "id": cid,
                "ticker": ticker,
                "eodhd_symbol": symbol,
                "fy": fy,
                "period_end": d_str,
                "filing_date": i_r.get("filing_date") or b_r.get("filing_date") or c_r.get("filing_date"),
                "fin_currency": (s.get("ccy") or {}).get(fy) or i_r.get("currency_symbol") or fin_ccy,
                "revenue_m": m(rev),
                "cogs_m": m(_fval(i_r, "costOfRevenue")),
                "gross_profit_m": m(_fval(i_r, "grossProfit")),
                "rd_m": m(_fval(i_r, "researchDevelopment")),
                "sga_m": m(_fval(i_r, "sellingGeneralAdministrative")),
                "opex_m": m(_fval(i_r, "totalOperatingExpenses")),
                "opcost_m": m(rev - ebit) if (rev is not None and ebit is not None and rev > ebit) else None,
                "ebitda_m": m(_fval(i_r, "ebitda") or ((ebit + da) if (ebit is not None and da is not None) else None)),
                "da_m": m(da),
                "ebit_m": m(ebit),
                "interest_expense_m": m(abs(s["interest"][fy])) if s["interest"].get(fy) is not None else None,
                "interest_income_m": m(_fval(i_r, "interestIncome")),
                "pretax_income_m": m(pretax),
                "tax_m": m(tax),
                "eff_tax_rate": r4(tr),
                "net_income_m": m(_fval(i_r, "netIncome") or ni),
                "net_income_common_m": m(ni),
                "ocf_m": m(ocf),
                "capex_m": m(abs(capex)) if capex is not None else None,
                "fcf_reported_m": m(fcf_rep),
                "owner_fcf_m": m(o_fcf),
                "sbc_m": m(abs(sbc)) if sbc is not None else None,
                "dividends_paid_m": m(abs(div)) if div is not None else None,
                "share_buybacks_m": m(buybacks),
                "net_borrowings_m": m(_fval(c_r, "netBorrowings")),
                "working_capital_change_m": m(_fval(c_r, "changeInWorkingCapital")),
                "cash_m": m(cash),
                "cash_and_st_inv_m": m(_fval(b_r, "cashAndShortTermInvestments") or cash),
                "receivables_m": m(_fval(b_r, "netReceivables")),
                "inventory_m": m(_fval(b_r, "inventory")),
                "current_assets_m": m(_fval(b_r, "totalCurrentAssets")),
                "ppe_net_m": m(_fval(b_r, "propertyPlantAndEquipmentNet", "propertyPlantEquipment")),
                "goodwill_m": m(gw),
                "intangibles_m": m(intang),
                "total_assets_m": m(s["assets"].get(fy)),
                "accounts_payable_m": m(_fval(b_r, "accountsPayable")),
                "current_deferred_rev_m": m(_fval(b_r, "currentDeferredRevenue")),
                "current_liab_m": m(_fval(b_r, "totalCurrentLiabilities")),
                "st_debt_m": m(st_debt),
                "lt_debt_m": m(debt),
                "total_debt_m": m(tot_debt),
                "net_debt_m": m(net_debt),
                "total_liab_m": m(_fval(b_r, "totalLiab")),
                "equity_m": m(eq),
                "retained_earnings_m": m(_fval(b_r, "retainedEarnings")),
                "net_working_capital_m": m(_fval(b_r, "netWorkingCapital")),
                "ic_gaap_m": m(ic_g),
                "ic_tangible_m": m(ic_t),
                "nopat_m": m(nopat),
                "roic_gaap": r4(roic_g.get(fy)),
                "roic_tangible": r4(roic_t.get(fy)),
                "roe": r4(ni / eq) if (ni is not None and eq and eq > 0) else None,
                "rote": r4(ni / tbv) if (ni is not None and tbv and tbv > 0) else None,
                "gross_margin": r4(_fval(i_r, "grossProfit") / rev) if (_fval(i_r, "grossProfit") is not None and rev and rev > 0) else None,
                "ebit_margin": r4(ebit / rev) if (ebit is not None and rev and rev > 0) else None,
                "net_margin": r4(ni / rev) if (ni is not None and rev and rev > 0) else None,
                "fcf_conversion": r4(o_fcf / ni) if (o_fcf is not None and ni and ni > 0) else None,
                "diluted_shares_m": round(sh / 1e6, 3) if sh else None,
                "eps_gaap": r4(s["eps"].get(fy)),
                "eps_street": r4(s["eps_street"].get(fy)),
                "owner_eps": r4(oe_ser.get(fy)),
                "ye_price_quote": round(ye_prices[fy], 2) if (ye_prices and fy in ye_prices) else None,
            })
        return rows

    def prefetch_batch(self, symbols: list[str], fetch_fundamentals: bool = True, fetch_eod: bool = True) -> None:
        """Concurrent prefetcher for EODHD fundamentals and EOD price series."""
        if settings.OFFLINE:
            return
        todo_fund = [
            s for s in symbols
            if fetch_fundamentals and (
                settings.REFRESH_FUNDAMENTALS
                or not (symbol_cache(s)).exists()
                or (time.time() - (symbol_cache(s)).stat().st_mtime) >= settings.FUND_CACHE_DAYS * 86400
            )
        ]
        todo_eod = [
            s for s in symbols
            if fetch_eod and (
                not (symbol_cache(s, "eod")).exists()
                or (time.time() - (symbol_cache(s, "eod")).stat().st_mtime) >= settings.EOD_CACHE_DAYS * 86400
            )
        ]
        if not todo_fund and not todo_eod:
            return

        total_tasks = len(todo_fund) + len(todo_eod)
        done = 0
        with ThreadPoolExecutor(max_workers=settings.EODHD_WORKERS) as pool:
            futs = []
            for s in todo_fund:
                futs.append(pool.submit(self.fundamentals, s))
            for s in todo_eod:
                futs.append(pool.submit(self.eod, s))
            for _ in as_completed(futs):
                done += 1
                if done % 100 == 0 or done == total_tasks:
                    print(f"  prefetched {done}/{total_tasks} EODHD payloads", flush=True)

        # Prefetch splits only for symbols whose cached fundamentals indicate a split since 2014-01-01
        if fetch_eod:
            todo_splits = []
            for s in symbols:
                sp_path = symbol_cache(s, "splits")
                if sp_path.exists():
                    continue
                fp = symbol_cache(s)
                if fp.exists():
                    fund = self.fundamentals(s)
                    last_sp = ((fund or {}).get("SplitsDividends") or {}).get("LastSplitDate")
                    if last_sp and str(last_sp) >= "2014-01-01":
                        todo_splits.append((s, fund))
            if todo_splits:
                with ThreadPoolExecutor(max_workers=settings.EODHD_WORKERS) as pool:
                    list(pool.map(lambda x: self.splits(x[0], x[1]), todo_splits))


# --------------------------------------------------------------------------- SEC (Legacy)
class SEC:
    def __init__(self):
        self.s = None
        if not settings.OFFLINE:
            import requests
            self.s = requests.Session()
            self.s.headers.update({"User-Agent": settings.SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"})
        self._last = 0.0
        self._ciks = None

    def _get(self, url):
        if self.s is None:
            import requests
            self.s = requests.Session()
            self.s.headers.update({"User-Agent": settings.SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"})
        wait = 1 / settings.SEC_MAX_RPS - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()
        r = self.s.get(url, timeout=60)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def cik(self, ticker: str):
        if self._ciks is None:
            d = _cached(CACHE / "sec" / "company_tickers.json",
                        lambda: self._get("https://www.sec.gov/files/company_tickers.json"))
            self._ciks = {v["ticker"].upper(): v["cik_str"] for v in d.values()}
        t = ticker.upper()
        return self._ciks.get(t) or self._ciks.get(t.replace(".", "-")) or self._ciks.get(t.replace(".", ""))

    def facts(self, cik: int):
        return _cached(CACHE / "sec" / f"CIK{cik:010d}.json",
                       lambda: self._get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"))

    CONCEPTS = {
        "sales": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                  "RevenueFromContractWithCustomerIncludingAssessedTax", "RevenuesNetOfInterestExpense"],
        "ni": ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"],
        "eps": ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted", "EarningsPerShareBasic"],
        "ocf": ["NetCashProvidedByUsedInOperatingActivities",
                "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
        "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireOtherPropertyPlantAndEquipment",
                  "PaymentsToAcquireProductiveAssets", "PaymentsToAcquireOtherProductiveAssets",
                  "PaymentsForCapitalImprovements", "PaymentsToDevelopRealEstateAssets", "PaymentsToAcquireRealEstate"],
        "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
        "da": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet",
               "OtherDepreciationAndAmortization", "Depreciation"],
        "dividends": ["PaymentsOfOrdinaryDividends", "PaymentsOfDividendsCommonStock", "PaymentsOfDividends",
                      "DividendsCommonStockCash", "DividendsCommonStock", "DividendsCash"],
        "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
        "debt": ["LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations",
                 "SeniorLongTermNotes", "SeniorNotes"],
        "cash": ["CashAndCashEquivalentsAtCarryingValue",
                 "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
        "goodwill": ["Goodwill"],
        "intang": ["IntangibleAssetsNetExcludingGoodwill", "FiniteLivedIntangibleAssetsNet"],
        "ebit": ["OperatingIncomeLoss"],
        "pretax": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                   "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
        "tax": ["IncomeTaxExpenseBenefit"],
        "interest": ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"],
        "assets": ["Assets"],
        "shares": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"],
    }
    COMBINED_DA = ["DepreciationAndAmortization", "DepreciationDepletionAndAmortization",
                   "DepreciationAmortizationAndAccretionNet", "OtherDepreciationAndAmortization"]
    DEPREC = ["Depreciation", "DepreciationAndAmortizationExcludingAmortizationOfIntangibleAssets"]
    AMORT = ["AmortizationOfIntangibleAssets", "FiniteLivedIntangibleAssetsAmortizationExpense",
             "AmortizationOfAcquiredIntangibleAssets"]

    INSTANT = {"equity", "debt", "cash", "goodwill", "intang", "assets"}

    def _extract_series(self, gaap: dict, concepts: list[str], is_instant: bool = False) -> dict:
        merged = {}
        for c in concepts:
            ser = {}
            units = gaap.get(c, {}).get("units", {})
            vals = units.get("USD") or units.get("USD/shares") or units.get("shares") or []
            for v in vals:
                if v.get("form") not in ("10-K", "10-K/A", "20-F", "40-F") or v.get("fp") != "FY":
                    continue
                end = dt.date.fromisoformat(v["end"])
                if not is_instant:
                    if "start" not in v:
                        continue
                    days = (end - dt.date.fromisoformat(v["start"])).days
                    if not 330 <= days <= 400:
                        continue
                fy = end.year if end.month > 6 else end.year - 1
                prev = ser.get(fy)
                if prev is None or v.get("filed", "") > prev[1]:
                    ser[fy] = (v["val"], v.get("filed", ""))
            for y, (val, _) in ser.items():
                merged.setdefault(y, val)
        return merged

    def annual_series(self, facts: dict) -> dict:
        gaap = facts.get("facts", {}).get("us-gaap", {})
        out = {}
        for key, concepts in self.CONCEPTS.items():
            if key == "da":
                continue
            out[key] = self._extract_series(gaap, concepts, is_instant=(key in self.INSTANT))

        da_comb = {}
        for c in self.COMBINED_DA:
            s = self._extract_series(gaap, [c])
            for y, v in s.items():
                if y not in da_comb or v > da_comb[y]:
                    da_comb[y] = v

        deprec = self._extract_series(gaap, self.DEPREC)
        amort = self._extract_series(gaap, self.AMORT)
        da_merged = dict(da_comb)
        for y in set(deprec) | set(amort):
            split_val = deprec.get(y, 0) + amort.get(y, 0)
            if y not in da_merged or split_val > da_merged[y]:
                da_merged[y] = split_val
        out["da"] = da_merged
        return out


# ------------------------------------------------------------------------- Yahoo (Cross-Validation & Gap-Fill)
def _yahoo_sym_candidates(sym: str) -> list[str]:
    """Map EODHD symbol (e.g. AAPL.US, EXPN.LSE, AMS.MC) to candidate Yahoo Finance tickers."""
    out = []
    if sym.endswith(".US"):
        out.append(sym[:-3])
    elif sym.endswith(".LSE"):
        out.append(sym[:-4] + ".L")
    out.append(sym)
    return list(dict.fromkeys(out))


class Yahoo:
    def __init__(self):
        self.yf = None
        if not settings.OFFLINE:
            try:
                import yfinance as yf
                self.yf = yf
            except ImportError:
                self.yf = None
        self._fx = {}

    def fx(self, frm: str, to: str):
        if not frm or not to:
            return None
        scale = 1.0
        if frm in ("GBp", "GBX"):
            frm, scale = "GBP", 0.01
        if frm == "ZAc":
            frm, scale = "ZAR", 0.01
        if frm == to:
            return scale
        k = (frm, to)
        if k not in self._fx:
            def fetch():
                try:
                    h = self.yf.Ticker(f"{frm}{to}=X").history(period="5d")
                    return float(h["Close"].dropna().iloc[-1])
                except Exception:
                    return None
            self._fx[k] = _cached(CACHE / "yahoo" / f"fx_{frm}{to}.json", fetch, days=1)
            if self._fx[k] is None and settings.OFFLINE:
                self._fx[k] = self._cross(frm, to)
        return None if self._fx[k] is None else self._fx[k] * scale


    def _cross(self, frm: str, to: str):
        known = {k: v for k, v in self._fx.items() if v}
        if (to, frm) in known:
            return 1 / known[(to, frm)]
        for (a, c), r in known.items():
            if a == frm:
                if (to, c) in known:
                    return r / known[(to, c)]
                if (c, to) in known:
                    return r * known[(c, to)]
        return None

    def quote(self, symbol: str) -> dict:
        def fetch():
            try:
                return _quote(symbol)
            except Exception:
                return None

        def _quote(symbol):
            t = self.yf.Ticker(symbol)
            fi = t.fast_info
            try:
                info = t.info
            except Exception:
                info = {}
            return {"price": _f(fi.get("lastPrice")), "currency": fi.get("currency"),
                    "shares": _f(fi.get("shares")) or _f(info.get("sharesOutstanding")),
                    "fin_currency": info.get("financialCurrency") or fi.get("currency"),
                    "dps": _f(info.get("trailingAnnualDividendRate"))}
        if not settings.OFFLINE:
            time.sleep(settings.YAHOO_PAUSE_S)
        return _cached(CACHE / "yahoo" / f"quote_{safe_name(symbol)}.json", fetch, days=1)

    def statements(self, symbol: str, force_refresh: bool = False) -> dict | None:
        """Fetch and cache annual financial statements (is, cf, bs) in data/_cache/yahoo/stmt_{y_sym}.json."""
        cands = _yahoo_sym_candidates(symbol)
        for ys in cands:
            p = CACHE / "yahoo" / f"stmt_{safe_name(ys)}.json"
            if p.exists() and not force_refresh and (settings.OFFLINE or (time.time() - p.stat().st_mtime) < settings.FUND_CACHE_DAYS * 86400):
                try:
                    return json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass
        if settings.OFFLINE or self.yf is None:
            return None
        for ys in cands:
            def fetch(y_sym=ys):
                try:
                    t = self.yf.Ticker(y_sym)
                    def df_to_dict(df):
                        if df is None or df.empty:
                            return {}
                        out = {}
                        for row_name, row in df.iterrows():
                            out[str(row_name)] = {str(col)[:10]: _f(val) for col, val in row.items()}
                        return out
                    res = {"is": df_to_dict(t.financials), "cf": df_to_dict(t.cashflow), "bs": df_to_dict(t.balance_sheet)}
                    return res if (res["is"] or res["cf"] or res["bs"]) else None
                except Exception:
                    return None
            time.sleep(settings.YAHOO_PAUSE_S)
            data = _cached(CACHE / "yahoo" / f"stmt_{safe_name(ys)}.json", fetch,
                           days=settings.FUND_CACHE_DAYS, force_refresh=force_refresh)
            if data:
                return data
        return None


def split_adjust(series: dict, splits: dict, ref_shares: float | None = None) -> dict:
    """Restate per-share and share-count series to today's share basis."""
    if not splits:
        return series
    order = sorted((dt.date.fromisoformat(d), r) for d, r in splits.items() if r and r > 0)
    shares = series.get("shares") or {}

    def candidates(y):
        later = [r for d, r in order if d > dt.date(y, 12, 31)]
        out, f = [1.0], 1.0
        for r in reversed(later):
            f *= r
            out.append(f)
        return out
    ref = ref_shares
    if not ref and shares:
        ly = max(shares)
        ref = shares[ly] * candidates(ly)[-1]

    def applied(y):
        c, v = candidates(y), shares.get(y)
        if len(c) == 1:
            return 1.0
        if not ref or not v or v <= 0:
            return c[-1]
        return min(c, key=lambda f: abs(math.log(v * f / ref)))
    out = dict(series)
    if series.get("eps"):
        out["eps"] = {y: v / applied(y) for y, v in series["eps"].items()}
    if shares:
        out["shares"] = {y: v * applied(y) for y, v in shares.items()}
    return out


def technicals(closes, volumes, dates, market_closes=None) -> dict:
    """30-wk MA, its value 5 weeks earlier, 52-wk high, breakout volume ratio, 52-wk relative strength."""
    if len(closes) < 36:
        return {}
    ma = lambda end: sum(closes[end - 30:end]) / 30
    n = len(closes)
    out = {"as_of": dates[-1], "price": closes[-1], "ma30": ma(n), "ma30_prev": ma(n - 5),
           "high_52w": max(closes[-52:])}
    prior = [v for v in volumes[-11:-1] if v]
    if prior and volumes[-1]:
        out["vol_ratio"] = volumes[-1] / (sum(prior) / len(prior))
    if n >= 53:
        ret = closes[-1] / closes[-53] - 1
        if market_closes and len(market_closes) >= 53:
            ret -= market_closes[-1] / market_closes[-53] - 1
            out["rs_52w"] = ret
    return out
