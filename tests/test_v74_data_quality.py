"""v7.4: M&A spend only in acquisition years; Yahoo capex on one basis; fiscal-year stubs; consolidated ROE."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.fetch import metrics, settings
from screener.fetch import sources as S


def base_series(yrs) -> dict:
    return {"debt": {y: 0.0 for y in yrs}, "ni": {y: 100.0 for y in yrs}, "ebit": {y: 100.0 for y in yrs},
            "tax": {y: 0.0 for y in yrs}, "pretax": {y: 100.0 for y in yrs}, "sales": {y: 1000.0 for y in yrs},
            "equity": {y: 1000.0 for y in yrs}}


class MaSpendTests(unittest.TestCase):
    def test_intangible_growth_without_goodwill_growth_is_not_ma(self):
        yrs = range(2015, 2026)
        s = {**base_series(yrs), "goodwill": {y: 500.0 for y in yrs},
             "intang": {y: 100.0 + 40.0 * (y - 2015) for y in yrs}}            # capitalised development only
        self.assertAlmostEqual(metrics.summarize(s)["ma_reinvest"], 0.0, places=4)

    def test_acquisition_year_counts_goodwill_and_intangibles(self):
        yrs = range(2015, 2026)
        s = {**base_series(yrs), "goodwill": {y: (500.0 if y < 2020 else 800.0) for y in yrs},
             "intang": {y: (100.0 if y < 2020 else 300.0) for y in yrs}}
        # deal year: Δ(goodwill + intangibles) 500 less the FX allowance 0.035 × (600 − 3 × 100)
        self.assertAlmostEqual(metrics.summarize(s)["ma_reinvest"], (500.0 - 10.5) / 1000.0, places=4)


class ConsolidatedRoeTests(unittest.TestCase):
    def test_consolidated_roe_uses_assets_minus_liabilities(self):
        yrs = range(2020, 2026)
        s = {"ni": {y: 25.0 for y in yrs}, "minority_interest": {y: 75.0 for y in yrs},
             "pretax": {y: 100.0 for y in yrs}, "tax": {y: 0.0 for y in yrs},
             "equity": {y: 1000.0 for y in yrs}, "nci": {y: 740.0 for y in yrs},     # IBKR: equity already incl. NCI
             "assets": {y: 5000.0 for y in yrs}, "liab": {y: 4000.0 for y in yrs}}
        self.assertAlmostEqual(metrics.summarize(s)["roe_median"], 100.0 / 1000.0)   # no double-counted NCI

    def test_minority_profit_uses_equity_plus_nci(self):
        yrs = range(2020, 2026)
        s = {"ni": {y: 25.0 for y in yrs}, "minority_interest": {y: 75.0 for y in yrs},
             "pretax": {y: 100.0 for y in yrs}, "tax": {y: 0.0 for y in yrs},
             "equity": {y: 250.0 for y in yrs}, "nci": {y: 750.0 for y in yrs}}  # IBKR-like Up-C
        self.assertAlmostEqual(metrics.summarize(s)["roe_median"], 100.0 / 1000.0)   # not 100 / 250


class StatementRowTests(unittest.TestCase):
    def setUp(self):
        settings.OFFLINE = True
        self.eod = S.EODHD(api_key="offline")
        self.tmp = tempfile.TemporaryDirectory()
        self._cache = S.CACHE
        S.CACHE = Path(self.tmp.name)

    def tearDown(self):
        S.CACHE = self._cache
        self.tmp.cleanup()

    def _fund(self, capex: dict, extra_cf: dict | None = None, ticker: str = "TEST.LSE", industry: str = "Software"):
        inc, bs, cf = {}, {}, {}
        for d, cx in capex.items():
            inc[d] = {"totalRevenue": 1000.0, "netIncome": 100.0, "currency_symbol": "GBP"}
            bs[d] = {"totalAssets": 2000.0, "totalStockholderEquity": 1000.0, "currency_symbol": "GBP"}
            cf[d] = {"totalCashFromOperatingActivities": 200.0, "capitalExpenditures": cx, "currency_symbol": "GBP"}
        for d, row in (extra_cf or {}).items():
            cf[d] = row
        return {"General": {"CurrencyCode": "GBP", "PrimaryTicker": ticker, "Industry": industry},
                "Financials": {"Income_Statement": {"yearly": inc}, "Balance_Sheet": {"yearly": bs},
                               "Cash_Flow": {"yearly": cf}}}

    def _yahoo(self, capex: dict, ticker: str = "TEST.L"):
        d = S.CACHE / "yahoo"
        d.mkdir(parents=True, exist_ok=True)
        cf = {"Capital Expenditure": {k: -v for k, v in capex.items()},
              "Operating Cash Flow": {k: 200.0 for k in capex}}
        (d / f"stmt_{ticker}.json").write_text(json.dumps({"cf": cf}))

    def test_fiscal_year_stub_does_not_overwrite_primary_row(self):
        fund = self._fund({"2024-02-29": 80.0},
                          extra_cf={"2024-03-31": {"capitalExpenditures": 0.0, "netIncome": 100.0, "dividendsPaid": -30.0}})
        s = self.eod.annual_series(fund)
        self.assertEqual(s["capex"][2023], 80.0)                  # SBRY-like 03-31 stub with capex 0 ignored
        self.assertEqual(s["period_end"][2023], "2024-02-29")
        self.assertEqual(s["dividends"][2023], -30.0)             # but fills a field the primary row lacks

    def test_systematic_yahoo_gap_replaces_all_years(self):
        yrs = {f"{y}-12-31": 100.0 for y in range(2022, 2026)}
        self._yahoo({"2022-12-31": 152.0, "2023-12-31": 148.0, "2024-12-31": 145.0, "2025-12-31": 150.0})
        s = self.eod.annual_series(self._fund(yrs))
        self.assertEqual([s["capex"][y] for y in range(2022, 2026)], [152.0, 148.0, 145.0, 150.0])

    def test_single_broken_year_replaced_alone(self):
        yrs = {f"{y}-12-31": 100.0 for y in range(2022, 2026)}
        yrs["2025-12-31"] = 7.0                                       # LSEG-like near-zero EODHD capex
        self._yahoo({"2022-12-31": 100.0, "2023-12-31": 102.0, "2024-12-31": 120.0, "2025-12-31": 105.0})
        s = self.eod.annual_series(self._fund(yrs))
        self.assertEqual([s["capex"][y] for y in range(2022, 2026)], [100.0, 100.0, 100.0, 105.0])

    def test_banks_keep_eodhd_capex(self):
        yrs = {f"{y}-12-31": 100.0 for y in range(2022, 2026)}
        self._yahoo({d: 300.0 for d in yrs})
        s = self.eod.annual_series(self._fund(yrs, industry="Banks - Regional"))
        self.assertEqual(s["capex"][2025], 100.0)


if __name__ == "__main__":
    unittest.main()
