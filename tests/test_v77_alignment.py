"""v7.7: one source for model parameters, spec-aligned estimator, hurdle-aware dashboard."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import config as C
from screener import gates as G
from screener.dashboard import build_dashboard_html
from screener.fetch import metrics


def growth_series(rate: float) -> dict:
    yrs = range(2014, 2026)
    lvl = {y: 1000.0 * (1 + rate) ** (y - 2014) for y in yrs}
    return {"sales": lvl, "ni": {y: v / 10 for y, v in lvl.items()}, "ebit": {y: v / 8 for y, v in lvl.items()},
            "tax": {y: 0.0 for y in yrs}, "pretax": {y: v / 10 for y, v in lvl.items()},
            "equity": {y: 1000.0 for y in yrs}}


class ParameterSourceTests(unittest.TestCase):
    def test_param_default_matches_config(self):
        self.assertEqual(C.param_default("par_g_base"), 0.030)
        self.assertEqual(C.param_default("par_g_anchor_max"), 0.130)
        self.assertEqual(C.param_default("par_roic_term_max"), 0.200)
        self.assertEqual(G.params({})["par_roic_term_max"], 0.200)

    def test_fetch_time_growth_honours_parameters(self):
        s = growth_series(0.25)                                   # strong grower: tanh asymptote binds
        default = metrics.summarize(s)["sales_cagr"]
        lower = metrics.summarize(s, None, {**G.params({}), "par_g_anchor_max": 0.10})["sales_cagr"]
        self.assertLess(default, 0.13)
        self.assertLess(lower, 0.10)
        self.assertLess(lower, default)

    def test_terminal_roic_ceiling_parameter(self):
        fin = {"price": 100.0, "market_cap_m": 1e4, "peak_oe_eps": 5.0, "cur_oe_eps": 5.0, "sales_cagr": 0.09,
               "roic_operating": 0.45, "roic_median": 0.40}
        p = G.params({})
        base = G.par_valuation(fin, p, cap=20, moat="Brand")
        same = G.par_valuation(fin, {**p, "par_roic_term_max": 0.20}, cap=20, moat="Brand")
        lower = G.par_valuation(fin, {**p, "par_roic_term_max": 0.15}, cap=20, moat="Brand")
        self.assertEqual(base["par_mult"], same["par_mult"])          # default reproduces today exactly
        self.assertLess(lower["par_mult"], base["par_mult"])
        self.assertLess(lower["term_mult"], base["term_mult"])

    def test_no_duplicate_growth_constants(self):
        self.assertFalse(hasattr(metrics, "G_BASE_STAT"))
        self.assertFalse(hasattr(metrics, "G_MAX_STAT"))
        self.assertFalse(hasattr(metrics, "implied_shares"))
        self.assertFalse(hasattr(G, "compress_g0"))


class DashboardHurdleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = build_dashboard_html({"version": "7.7", "generated_at": "x", "universes": {}, "companies": [],
                                         "changelog": [], "summary": {"total_companies": 0, "quality_pass": 0,
                                                                      "calamity_pass": 0, "valued": 0,
                                                                      "median_excess_irr": None}})

    def test_irr_colours_relative_to_hurdle(self):
        self.assertIn("function irrColor(c, irr)", self.html)
        self.assertIn("irr >= r + 0.035", self.html)
        self.assertNotIn("val >= 0.12 ?", self.html)

    def test_ronic_column_and_kpi(self):
        self.assertIn("roic_used: { key: 'roic_exp', label: 'RONIC₀', num: true }", self.html)
        self.assertIn("Median IRR vs hurdle", self.html)
        self.assertIn("roicTermMax", self.html)


if __name__ == "__main__":
    unittest.main()
