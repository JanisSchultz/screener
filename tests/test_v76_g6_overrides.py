"""v7.6: Gate 6 rule check as review flags, no analyst overrides, non-cash-marks data check."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import gates as G
from screener.dashboard import build_dashboard_html
from screener.data import FIN_FIELDS
from screener.fetch import metrics
from screener.migrations.remediate_v7_6_drop_overrides import auto_part


def series(ni: dict, ocf: dict) -> dict:
    return {"ni": ni, "ocf": ocf}


class NonCashMarksTests(unittest.TestCase):
    def test_hedge_marks_flagged(self):            # SAF-like: IFRS profit swings, cash flow steady
        s = series({2021: 0.04, 2022: -2.46, 2023: 3.44, 2024: -0.67, 2025: 7.18},
                   {2021: 2.44, 2022: 3.54, 2023: 4.27, 2024: 4.73, 2025: 5.72})
        self.assertIn("earnings dominated by non-cash marks", metrics.noncash_marks(s))

    def test_investment_gains_flagged(self):       # BRK-like: unrealised gains, NI 2x OCF
        s = series({2021: 89.8, 2022: -22.8, 2023: 96.2, 2024: 89.0, 2025: 67.0},
                   {2021: 39.4, 2022: 37.2, 2023: 49.2, 2024: 30.6, 2025: 46.0})
        self.assertIsNotNone(metrics.noncash_marks(s))

    def test_impairment_loss_not_flagged(self):    # CARL-like: one write-off year, profits below cash flow
        s = series({2021: 6.9, 2022: -3.8, 2023: 5.8, 2024: -0.5, 2025: 6.0},
                   {2021: 11.0, 2022: 10.5, 2023: 11.2, 2024: 10.9, 2025: 11.5})
        self.assertIsNone(metrics.noncash_marks(s))

    def test_blocking_note_gives_no_data(self):
        fin = {"price": 100.0, "market_cap_m": 1e4, "peak_oe_eps": 5.0, "cur_oe_eps": 5.0, "sales_cagr": 0.08,
               "roic_operating": 0.25, "fin_note": "[auto] earnings dominated by non-cash marks (NI sign changes 3x)"}
        self.assertEqual(G.par_valuation(fin, G.params({}), cap=20, moat="Brand")["status"], "No data")


class Gate6CheckTests(unittest.TestCase):
    def setUp(self):
        self.p = G.params({})

    def test_thresholds(self):
        fin = {"g6_netdebt_yrs": 4.5, "g6_intcov": 6.0, "fcf_conv": 0.79, "p2p_ok": "Y"}
        self.assertEqual(G.g6_checks(fin, "Railroads", self.p),
                         {"netdebt": "flag", "intcov": "ok", "fcfconv": "flag", "p2p": "ok"})

    def test_balance_sheet_financial_na(self):
        fin = {"g6_netdebt_yrs": 30.0, "g6_intcov": 1.2, "fcf_conv": 0.3, "p2p_ok": "N"}
        self.assertEqual(G.g6_checks(fin, "Property & Casualty Insurance", self.p),
                         {"netdebt": "n/a", "intcov": "n/a", "fcfconv": "info", "p2p": "flag"})

    def test_flags_never_change_gate_result_or_valuation(self):
        c = {"id": "X", "1": "Y", "2": "Y", "3a": "Brand", "3b": "Y", "4": 20, "5": 2, "6": "Y"}
        self.assertEqual(G.phase_results(c, self.p)["result"], "Quality pass")

    def test_summarize_three_year_medians(self):
        yrs = range(2020, 2026)
        s = {"ni": {y: 100.0 for y in yrs}, "ebit": {y: 150.0 for y in yrs}, "interest": {y: 10.0 for y in yrs},
             "debt": {y: 500.0 for y in yrs}, "st_debt": {y: 100.0 for y in yrs}, "cash": {y: 200.0 for y in yrs},
             "equity": {y: 1000.0 for y in yrs}}
        out = metrics.summarize(s)
        self.assertAlmostEqual(out["g6_netdebt_yrs"], 4.0)          # (500 + 100 − 200) / 100
        self.assertAlmostEqual(out["g6_intcov"], 15.0)


class NoOverrideTests(unittest.TestCase):
    def test_override_columns_gone(self):
        for k in ("peak_eps_est", "g_est", "roic_est", "g_implied"):
            self.assertNotIn(k, FIN_FIELDS)

    def test_override_values_ignored(self):
        p = G.params({})
        base = {"price": 100.0, "market_cap_m": 1e4, "peak_oe_eps": 5.0, "cur_oe_eps": 5.0, "sales_cagr": 0.08,
                "roic_operating": 0.25, "roic_median": 0.2}
        v0 = G.par_valuation(base, p, cap=20, moat="Brand")
        v1 = G.par_valuation({**base, "peak_eps_est": 9.0, "g_est": 0.12, "roic_est": 0.9}, p, cap=20, moat="Brand")
        self.assertEqual((v0["peak_eps"], v0["par_mult"]), (v1["peak_eps"], v1["par_mult"]))

    def test_migration_keeps_only_auto_notes(self):
        self.assertEqual(auto_part("Old analyst text 35.0% cap | [auto] short history"), "[auto] short history")
        self.assertIsNone(auto_part("Only analyst text"))

    def test_js_mirror_has_noncash_token(self):
        html = build_dashboard_html({"version": "7.6", "generated_at": "x", "universes": {}, "companies": [],
                                     "changelog": [], "summary": {"total_companies": 0, "quality_pass": 0,
                                                                  "calamity_pass": 0, "valued": 0, "median_excess_irr": None}})
        self.assertIn("'earnings dominated by non-cash marks'", html)
        self.assertIn("g6Markers", html)


if __name__ == "__main__":
    unittest.main()
