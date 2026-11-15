"""v7.3: operating ROIC on tangible capital without the D&A add-back; GAAP fallback when invested capital <= 0."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.fetch import metrics


class TangibleCapitalBaseTests(unittest.TestCase):
    def _series(self, equity: float, cash: float) -> dict:
        yrs = range(2020, 2026)
        return {"ebit": {y: 100.0 for y in yrs}, "tax": {y: 0.0 for y in yrs}, "pretax": {y: 100.0 for y in yrs},
                "ni": {y: 100.0 for y in yrs}, "equity": {y: equity for y in yrs}, "cash": {y: cash for y in yrs},
                "goodwill": {y: 300.0 for y in yrs}, "assets": {y: 2000.0 for y in yrs},
                "da": {y: 80.0 for y in yrs}, "capex": {y: 20.0 for y in yrs}}

    def test_addback_does_not_inflate_operating_roic(self):
        out = metrics.summarize(self._series(equity=1000.0, cash=0.0))
        self.assertAlmostEqual(out["roic_median"], 100.0 / 1000.0)
        self.assertAlmostEqual(out["roic_operating"], 100.0 / 700.0)      # D&A − capex (60) not added to NOPAT
        self.assertGreater(out["owner_add_m"], 0.0)                         # Owner EPS add-back itself unchanged

    def test_negative_invested_capital_falls_back_to_gaap(self):
        # customer cash exceeds equity (ADYEN-like): GAAP IC <= 0 -> no tangible figure -> roic_operating = GAAP
        out = metrics.summarize(self._series(equity=500.0, cash=800.0))
        self.assertIsNotNone(out["roic_median"])
        self.assertEqual(out["roic_operating"], out["roic_median"])

    def test_one_negative_capital_year_falls_back_to_gaap(self):
        # DB1-like: invested capital negative in most years, one tiny positive year -> no tangible median
        s = self._series(equity=1000.0, cash=0.0)
        s["cash"] = {y: (1500.0 if y < 2025 else 990.0) for y in s["equity"]}
        out = metrics.summarize(s)
        self.assertEqual(out["roic_operating"], out["roic_median"])

    def test_single_net_cash_year_is_tolerated(self):
        # SPGI-like: one net-cash year in the window does not discard four sound tangible years
        s = self._series(equity=1000.0, cash=0.0)
        s["cash"] = {y: (1100.0 if y == 2022 else 0.0) for y in s["equity"]}
        out = metrics.summarize(s)
        self.assertAlmostEqual(out["roic_operating"], 100.0 / 700.0)


if __name__ == "__main__":
    unittest.main()
