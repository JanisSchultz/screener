"""v7.5: ROE as the capital return when invested capital is <= 0 in >= 2 of 5 years (customer / clearing cash)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import gates as G
from screener.fetch import metrics


def fin(**kw) -> dict:
    base = {"id": "TEST", "price": 100.0, "market_cap_m": 10000.0, "peak_oe_eps": 5.0, "cur_oe_eps": 5.0,
            "mult_low_5y": 15.0, "mult_high_5y": 25.0, "roic_median": 0.073, "roic_operating": 0.073,
            "roe_median": 0.19, "ic_neg_years": 4, "ma_reinvest": 0.5, "sales_cagr": 0.09}
    base.update(kw)
    return base


class RoeAsCapitalTests(unittest.TestCase):
    def setUp(self):
        self.p = G.params({})

    def _val(self, sub="Financial Exchanges & Data", **kw):
        return G.par_valuation(fin(**kw), self.p, cap=20, moat="Toll booth", sub_industry=sub)

    def test_clearing_cash_balance_sheet_uses_roe(self):
        v = self._val()                                    # DB1-like
        self.assertEqual(v["roic_source"], "roe_median")
        self.assertAlmostEqual(v["roic_exp"], 0.19)
        self.assertEqual(v["ma_alpha"], 0.0)               # ROE is goodwill-inclusive: no M&A blend
        self.assertEqual(v["k"], 0.085)                    # fee business: operating discount rate
        self.assertTrue(v["roic_basis_gaap"])

    def test_implausible_roe_keeps_gaap(self):
        v = self._val(roe_median=2.34, roic_median=1.07, roic_operating=1.07)   # FTNT-like buyback-shrunk equity
        self.assertEqual(v["roic_source"], "roic_operating")

    def test_single_negative_year_unchanged(self):
        self.assertEqual(self._val(ic_neg_years=1)["roic_source"], "roic_operating")

    def test_balance_sheet_financial_unchanged(self):
        v = self._val(sub="Property & Casualty Insurance")
        self.assertEqual((v["roic_source"], v["k"]), ("roe_median", 0.1025))

    def test_summarize_counts_negative_capital_years(self):
        yrs = range(2020, 2026)
        s = {"ebit": {y: 100.0 for y in yrs}, "tax": {y: 0.0 for y in yrs}, "pretax": {y: 100.0 for y in yrs},
             "ni": {y: 100.0 for y in yrs}, "equity": {y: 500.0 for y in yrs},
             "cash": {y: (800.0 if y < 2024 else 100.0) for y in yrs}, "assets": {y: 3000.0 for y in yrs}}
        self.assertEqual(metrics.summarize(s)["ic_neg_years"], 3)    # 2021-2023 of the 2021-2025 window


if __name__ == "__main__":
    unittest.main()
