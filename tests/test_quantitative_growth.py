"""Tests for the v6.26 Gate 4 CAP-Linked Growth Engine & Expected Growth (g_exp) Maths."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import config as C
from screener.gates import params, par_valuation


def sample_fin(**overrides) -> dict:
    fin = {
        "price": 100.0,
        "market_cap_m": 10000.0,
        "peak_oe_eps": 5.0,
        "peak_eps_est": None,
        "mult_low_5y": 15.0,
        "mult_high_5y": 25.0,
        "cagr_oe_eps": 0.15,
        "dividends_ttm_m": 200.0,
        "roic_median": 0.20,
        "roic_operating": 0.25,
        "roic_est": None,
        "g_est": None,
        "g_implied": None,
    }
    fin.update(overrides)
    return fin


class QuantitativeGrowthTests(unittest.TestCase):
    def setUp(self):
        self.p = params({})

    def test_cap_30_persistence_lambda_025(self):
        # g = 15%, base = 7%, lambda = 0.25 -> 0.25 * (0.15 - 0.07) + 0.07 = 0.02 + 0.07 = 0.09 (9.0%)
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.09, places=4)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])
        self.assertEqual(val["exp_coupon"], val["imp_coupon"])

    def test_cap_20_persistence_lambda_015(self):
        # g = 15%, base = 7%, lambda = 0.15 -> 0.15 * (0.15 - 0.07) + 0.07 = 0.012 + 0.07 = 0.082 (8.2%)
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_exp"], 0.082, places=4)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])

    def test_cap_15_persistence_lambda_010(self):
        # g = 15%, base = 7%, lambda = 0.10 -> 0.10 * (0.15 - 0.07) + 0.07 = 0.008 + 0.07 = 0.078 (7.8%)
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=15)
        self.assertAlmostEqual(val["g_exp"], 0.078, places=4)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])

    def test_unpopulated_cap_falls_back_to_default_lambda_015(self):
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=None)
        self.assertAlmostEqual(val["g_exp"], 0.082, places=4)

    def test_analyst_override_g_est_precedes_cap_formula(self):
        fin = sample_fin(cagr_oe_eps=0.15, g_est=0.11)
        val = par_valuation(fin, self.p, cap=30)
        self.assertEqual(val["g_exp"], 0.11)
        self.assertEqual(val["g_imp"], 0.11)

    def test_bottom_up_g_implied_precedes_cap_formula(self):
        fin = sample_fin(cagr_oe_eps=0.15, g_implied=0.095)
        val = par_valuation(fin, self.p, cap=15)
        self.assertEqual(val["g_exp"], 0.095)
        self.assertEqual(val["g_imp"], 0.095)

    def test_negative_cagr_floored_at_zero_inside_regression(self):
        # g = -0.10 -> max(0, -0.10) = 0.0 -> lambda * (0 - 0.07) + 0.07
        # For lambda=0.25: 0.25 * (-0.07) + 0.07 = -0.0175 + 0.07 = 0.0525 (5.25%)
        # For lambda=0.15: 0.15 * (-0.07) + 0.07 = -0.0105 + 0.07 = 0.0595 (5.95%)
        fin_neg = sample_fin(cagr_oe_eps=-0.10)
        val30 = par_valuation(fin_neg, self.p, cap=30)
        self.assertAlmostEqual(val30["g_exp"], 0.0525, places=4)

        val20 = par_valuation(fin_neg, self.p, cap=20)
        self.assertAlmostEqual(val20["g_exp"], 0.0595, places=4)

    def test_hypergrowth_capped_at_par_g_cap_12_pct(self):
        # Even with 60% historical CAGR and CAP 30 (lambda 0.25):
        # 0.25 * (0.60 - 0.07) + 0.07 = 0.1325 + 0.07 = 0.2025 -> capped at 0.12 (12%)
        fin = sample_fin(cagr_oe_eps=0.60)
        val = par_valuation(fin, self.p, cap=30)
        self.assertEqual(val["g_exp"], 0.12)

    def test_growth_margin_of_safety_calculation(self):
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=20)
        # g_gap must equal round(g_exp - g_market, 4)
        self.assertAlmostEqual(val["g_gap"], round(val["g_exp"] - val["g_market"], 4), places=4)

    def test_pillar2_hist_cap_clamps_zirp_bubble_midpoint(self):
        # Midpoint of (30, 90) is 60.0 -> clamped to par_hist_cap = 35.0
        # At g_implied = 10%, ROIC = 35%, CAP = 20 -> t_growth = 20.0, t_hist = 35.0, t_roic = 35.0 -> PAR = 30.0
        fin = sample_fin(mult_low_5y=30.0, mult_high_5y=90.0, g_implied=0.10, roic_operating=0.35)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["par_mult"], 30.0, places=4)

    def test_cap_growth_slope_differentiates_when_g_implied_populated(self):
        fin = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, g_implied=0.10, roic_operating=0.35)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)
        # t_hist = 30, t_roic = 35; t_growth = 24.0 (CAP 30), 20.0 (CAP 20), 17.0 (CAP 15)
        self.assertAlmostEqual(v30["par_mult"], (24.0 + 30.0 + 35.0) / 3.0, places=4)
        self.assertAlmostEqual(v20["par_mult"], (20.0 + 30.0 + 35.0) / 3.0, places=4)
        self.assertAlmostEqual(v15["par_mult"], (17.0 + 30.0 + 35.0) / 3.0, places=4)
        self.assertGreater(v30["par_mult"], v20["par_mult"])
        self.assertGreater(v20["par_mult"], v15["par_mult"])

    def test_reinvestment_efficiency_penalizes_low_roic_grower(self):
        # At ROIC = 15% and g = 9%, FCF payout is (1 - 0.09/0.15) = 0.40 vs benchmark (1 - 0.09/0.35) = 0.7429 -> eta = 0.5385
        fin_low_roic = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, g_implied=0.09, roic_operating=0.15)
        val = par_valuation(fin_low_roic, self.p, cap=20)
        expected_eta = (1.0 - 0.09 / 0.15) / (1.0 - 0.09 / 0.35)
        expected_t_growth = 200.0 * expected_eta * 0.09
        expected_par = (expected_t_growth + 30.0 + 15.0) / 3.0
        self.assertAlmostEqual(val["par_mult"], expected_par, places=4)

    def test_closed_form_g_market_inversion_round_trip(self):
        # When current price equals PAR value (and raw PAR <= mult_high_5y), g_market equals g_exp
        fin = sample_fin(mult_low_5y=18.0, mult_high_5y=36.0, g_implied=0.085, roic_operating=0.22)
        val0 = par_valuation(fin, self.p, cap=15)
        fin_at_par = sample_fin(
            price=val0["par_val"], peak_oe_eps=5.0,
            mult_low_5y=18.0, mult_high_5y=36.0, g_implied=0.085, roic_operating=0.22
        )
        val_at_par = par_valuation(fin_at_par, self.p, cap=15)
        self.assertAlmostEqual(val_at_par["g_market"], 0.085, places=4)
        self.assertAlmostEqual(val_at_par["g_gap"], 0.0, places=4)

    def test_mid_cycle_blend_when_current_eps_below_peak(self):
        # Peak = 10.0, NI = 600M, MC = 10,000M, Price = 100.0 -> cur_eps = 6.0
        # Active EPS = 0.5 * (10.0 + 6.0) = 8.0
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=600.0, peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 8.0, places=4)
        self.assertAlmostEqual(val["cur_mult"], 100.0 / 8.0, places=4)

    def test_compounder_at_peak_untouched(self):
        # Peak = 10.0, NI = 1000M, MC = 10,000M, Price = 100.0 -> cur_eps = 10.0
        # Active EPS remains 10.0
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=1000.0, peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 10.0, places=4)

    def test_analyst_override_takes_precedence_over_mid_cycle(self):
        # Peak = 10.0, cur_eps = 6.0, but analyst set peak_eps_est = 7.2
        # Active EPS must equal 7.2
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=600.0, peak_oe_eps=10.0, peak_eps_est=7.2)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 7.2, places=4)

    def test_negative_net_income_floored_at_zero(self):
        # Peak = 10.0, NI = -500M -> cur_eps = -5.0 (floored to 0.0)
        # Active EPS = 0.5 * (10.0 + 0.0) = 5.0
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=-500.0, peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 5.0, places=4)


if __name__ == "__main__":
    unittest.main()
