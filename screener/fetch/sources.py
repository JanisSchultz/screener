"""Data sources: SEC EDGAR companyfacts (US fundamentals, ~10 yrs) and Yahoo Finance via yfinance
(prices, weekly history, FX, and ~4 yrs of annual statements for non-SEC filers)."""
from __future__ import annotations

import datetime as dt
import json
import math
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from ..data import DATA_DIR
from . import settings

CACHE = DATA_DIR / "_cache"


def _cached(path: Path, fetch, days=settings.CACHE_DAYS):
    if path.exists() and (settings.OFFLINE or (time.time() - path.stat().st_mtime) < days * 86400):
        return json.loads(path.read_text())
    if settings.OFFLINE:                    # offline: use the cache whatever its age, never fetch
        return None
    data = fetch()
    if data is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    return data


# --------------------------------------------------------------------------- SEC
class SEC:
    def __init__(self):
        import requests
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": settings.SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"})
        self._last = 0.0
        self._ciks = None

    def _get(self, url):
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

    # concept fallbacks per series; first concept with data wins per year
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
        for c in concepts:                      # companies switch tags over time: fill each year
            ser = {}                            # from the first concept that reports it
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
                fy = end.year if end.month > 6 else end.year - 1   # fiscal year label by period end
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

        # D&A: prefer combined line items; if not reported or if split depreciation + amortization is larger, use split sum
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


# ------------------------------------------------------------------------- Yahoo
class Yahoo:
    def __init__(self):
        import yfinance as yf
        self.yf = yf
        self._fx = {}

    def fx(self, frm: str, to: str):
        """Rate to convert 1 unit of `frm` into `to` (handles GBp/ZAc pence quotes)."""
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

    def seed_fx(self, frm: str, to: str, rate: float):
        """Offline: register a rate implied by stored data (e.g. market cap ÷ price × shares)."""
        if frm in ("GBp", "GBX"):
            frm, rate = "GBP", rate * 100
        if frm and to and rate and frm != to:
            self._fx.setdefault((frm, to), rate)

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
                return None                       # Yahoo occasionally returns incomplete metadata

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
        return _cached(CACHE / "yahoo" / f"quote_{symbol}.json", fetch, days=1)

    def statements(self, symbol: str) -> dict:
        """~4 years of annual statements -> series dict compatible with metrics.summarize (fiscal-year keys)."""
        def fetch():
            t = self.yf.Ticker(symbol)
            out = {}
            frames = {"is": t.income_stmt, "cf": t.cashflow, "bs": t.balance_sheet}
            for k, df in frames.items():
                if df is None or df.empty:
                    continue
                out[k] = {str(idx): {str(c.date()): _f(df.loc[idx, c]) for c in df.columns} for idx in df.index}
            return out
        if not settings.OFFLINE:
            time.sleep(settings.YAHOO_PAUSE_S)
        raw = _cached(CACHE / "yahoo" / f"stmt_{symbol}.json", fetch) or {}
        pick = lambda sheet, *names: next((raw.get(sheet, {}).get(n) for n in names if raw.get(sheet, {}).get(n)), {})

        def ser(sheet, *names):
            d = {}
            for date, v in pick(sheet, *names).items():
                if v is None:
                    continue
                y = dt.date.fromisoformat(date)
                d[y.year if y.month > 6 else y.year - 1] = v
            return d

        return {
            "sales": ser("is", "Total Revenue", "Operating Revenue"),
            "ni": ser("is", "Net Income Common Stockholders", "Net Income"),
            "eps": ser("is", "Diluted EPS", "Basic EPS"),
            "ebit": ser("is", "EBIT", "Operating Income"),
            "pretax": ser("is", "Pretax Income"),
            "tax": ser("is", "Tax Provision"),
            "interest": ser("is", "Interest Expense", "Interest Expense Non Operating"),
            "ocf": ser("cf", "Operating Cash Flow", "Cash Flow From Continuing Operating Activities"),
            "capex": ser("cf", "Capital Expenditure"),
            "sbc": ser("cf", "Stock Based Compensation"),
            "da": ser("cf", "Depreciation And Amortization", "Depreciation"),
            "dividends": ser("cf", "Cash Dividends Paid", "Common Stock Dividend Paid"),
            "equity": ser("bs", "Stockholders Equity", "Common Stock Equity"),
            "debt": ser("bs", "Long Term Debt", "Long Term Debt And Capital Lease Obligation"),
            "cash": ser("bs", "Cash And Cash Equivalents"),
            "goodwill": ser("bs", "Goodwill"),
            "intang": ser("bs", "Other Intangible Assets"),
            "assets": ser("bs", "Total Assets"),
            "shares": ser("is", "Diluted Average Shares") or ser("bs", "Ordinary Shares Number", "Share Issued"),
        }

    def weekly(self, symbols: list[str]):
        """2 years of weekly OHLCV for many symbols -> {symbol: (closes, volumes, dates)}."""
        out = {}
        for i in range(0, len(symbols), 100):
            chunk = symbols[i:i + 100]
            df = self.yf.download(chunk, period="2y", interval="1wk", progress=False, auto_adjust=True,
                                  group_by="ticker", threads=True)
            for s in chunk:
                try:
                    sub = df[s] if len(chunk) > 1 else df
                    sub = sub.dropna(subset=["Close"])
                    out[s] = (list(sub["Close"].astype(float)), list(sub["Volume"].astype(float)),
                              [d.date().isoformat() for d in sub.index])
                except Exception:
                    pass
        return out

    def splits(self, symbol: str) -> dict:
        def fetch():
            sp = self.yf.Ticker(symbol).splits
            return {str(d.date()): float(x) for d, x in sp.items() if x and x > 0}
        return _cached(CACHE / "yahoo" / f"splits_{symbol}.json", fetch)

    def monthly_prices(self, symbol: str) -> dict:
        """{month (ISO date of the monthly bar): close}, ~12 years, split-adjusted, quote currency."""
        def fetch():
            h = self.yf.Ticker(symbol).history(period="12y", interval="1mo", auto_adjust=False)
            return {str(d.date()): float(c) for d, c in h["Close"].dropna().items()}
        return _cached(CACHE / "yahoo" / f"px12y_{symbol}.json", fetch) or {}

    def year_end_prices(self, symbol: str) -> dict:
        raw = self.monthly_prices(symbol)
        out = {}
        for d, c in sorted(raw.items()):
            y = dt.date.fromisoformat(d)
            out[y.year] = c          # last monthly close of each calendar year
        return out


def split_adjust(series: dict, splits: dict, ref_shares: float | None = None) -> dict:
    """Restate per-share and share-count series to today's share basis (prices from Yahoo are split-adjusted).
    A filing already restates every split before its filing date, so a year's value needs the product of only
    the *latest* k splits after its fiscal year (k = 0 … all). Pick the k that brings the share count closest to
    today's count (`ref_shares`: quote shares, else the latest year's count adjusted for later splits)."""
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


def _f(x):
    try:
        x = float(x)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


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
