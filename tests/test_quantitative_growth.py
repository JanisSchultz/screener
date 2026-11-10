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
        # g = 15%, base = 6%, lambda = 0.25 -> 0.25 * (0.15 - 0.06) + 0.06 = 0.0225 + 0.06 = 0.0825 (8.25%)
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.0825, places=4)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])
        self.assertEqual(val["exp_coupon"], val["imp_coupon"])

    def test_cap_20_persistence_lambda_015(self):
        # g = 15%, base = 6%, lambda = 0.15 -> 0.15 * (0.15 - 0.06) + 0.06 = 0.0135 + 0.06 = 0.0735 (7.35%)
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_exp"], 0.0735, places=4)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])

    def test_cap_15_persistence_lambda_010(self):
        # g = 15%, base = 6%, lambda = 0.10 -> 0.10 * (0.15 - 0.06) + 0.06 = 0.009 + 0.06 = 0.069 (6.90%)
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=15)
        self.assertAlmostEqual(val["g_exp"], 0.0690, places=4)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])

    def test_unpopulated_cap_falls_back_to_default_lambda_015(self):
        fin = sample_fin(cagr_oe_eps=0.15)
        val = par_valuation(fin, self.p, cap=None)
        self.assertAlmostEqual(val["g_exp"], 0.0735, places=4)

    def test_analyst_override_g_est_precedes_cap_formula(self):
        fin = sample_fin(cagr_oe_eps=0.15, g_est=0.11)
        val = par_valuation(fin, self.p, cap=30)
        self.assertEqual(val["g_exp"], 0.11)
        self.assertEqual(val["g_imp"], 0.11)

    def test_bottom_up_g_implied_disciplined_by_cap_fade(self):
        # In v6.29, bottom-up g_implied is disciplined by Gate 4 CAP persistence fade (no Inside View bypass)
        # At CAP 15 (lambda = 0.10) and g_implied = 9.5%: 0.10 * (0.095 - 0.06) + 0.06 = 0.0635 (6.35%)
        fin = sample_fin(cagr_oe_eps=0.15, g_implied=0.095)
        val = par_valuation(fin, self.p, cap=15)
        self.assertAlmostEqual(val["g_exp"], 0.0635, places=4)
        self.assertAlmostEqual(val["g_imp"], 0.0635, places=4)

    def test_asymmetric_low_growth_not_faded_up(self):
        # g = 3.5% < 6.0% -> no free lunch! Kept at 3.5%, NOT faded up to 6%
        fin_low = sample_fin(cagr_oe_eps=0.035)
        val30 = par_valuation(fin_low, self.p, cap=30)
        val20 = par_valuation(fin_low, self.p, cap=20)
        val15 = par_valuation(fin_low, self.p, cap=15)
        self.assertAlmostEqual(val30["g_exp"], 0.035, places=4)
        self.assertAlmostEqual(val20["g_exp"], 0.035, places=4)
        self.assertAlmostEqual(val15["g_exp"], 0.035, places=4)

    def test_negative_cagr_floored_at_two_percent(self):
        # g = -0.10 -> floored at 2.0%
        fin_neg = sample_fin(cagr_oe_eps=-0.10)
        val = par_valuation(fin_neg, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.02, places=4)

    def test_hypergrowth_capped_at_par_g_cap_12_pct(self):
        # Even with 60% historical CAGR and CAP 30 (lambda 0.25):
        # 0.25 * (0.60 - 0.06) + 0.06 = 0.135 + 0.06 = 0.195 -> capped at 0.12 (12%)
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
        # At g_est = 10%, ROIC = 35%, CAP = 20 -> t_growth = 20.0, t_hist = 35.0, t_roic = 35.0 -> PAR = 30.0
        fin = sample_fin(mult_low_5y=30.0, mult_high_5y=90.0, g_est=0.10, roic_operating=0.35)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["par_mult"], 30.0, places=4)

    def test_cap_growth_slope_differentiates_when_g_implied_populated(self):
        # Under v6.29, g_implied = 10% fades via CAP persistence (lambda 0.25, 0.15, 0.10)
        # CAP 30: g_exp = 0.25*(0.10-0.06)+0.06 = 7.0%, t_growth = 240.0*0.07 = 16.8
        # CAP 20: g_exp = 0.15*(0.10-0.06)+0.06 = 6.6%, t_growth = 200.0*0.066 = 13.2
        # CAP 15: g_exp = 0.10*(0.10-0.06)+0.06 = 6.4%, t_growth = 170.0*0.064 = 10.88
        fin = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, g_implied=0.10, roic_operating=0.35)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)
        self.assertAlmostEqual(v30["par_mult"], (16.8 + 30.0 + 35.0) / 3.0, places=4)
        self.assertAlmostEqual(v20["par_mult"], (13.2 + 30.0 + 35.0) / 3.0, places=4)
        self.assertAlmostEqual(v15["par_mult"], (10.88 + 30.0 + 35.0) / 3.0, places=4)
        self.assertGreater(v30["par_mult"], v20["par_mult"])
        self.assertGreater(v20["par_mult"], v15["par_mult"])

    def test_reinvestment_efficiency_penalizes_low_roic_grower(self):
        # At ROIC = 15% and g = 9%, FCF payout is (1 - 0.09/0.15) = 0.40 vs benchmark (1 - 0.09/0.35) = 0.7429 -> eta = 0.5385
        fin_low_roic = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, g_est=0.09, roic_operating=0.15)
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
        self.assertAlmostEqual(val_at_par["g_market"], val0["g_exp"], places=4)
        self.assertAlmostEqual(val_at_par["g_gap"], 0.0, places=4)
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

    def test_mega_cap_scale_ceiling_par_g_cap_mega(self):
        # Enterprise with MCap $150B (> $100B) -> MEGA tier with scale cap = 6.5%
        # Even with historical 25% CAGR and CAP 30, g_exp cannot exceed 6.5%
        fin = sample_fin(market_cap_m=150000.0, cagr_oe_eps=0.25)
        val = par_valuation(fin, self.p, cap=30)
        self.assertEqual(val["scale_tier"], "MEGA")
        self.assertEqual(val["scale_cap"], 0.065)
        self.assertAlmostEqual(val["g_exp"], 0.065, places=4)

    def test_large_cap_scale_ceiling_par_g_cap_large(self):
        # Enterprise with MCap $50B ($25B - $100B) -> LARGE tier with scale cap = 8.0%
        # With historical 25% CAGR and CAP 30 (faded to 10.75%), g_exp is capped at 8.0%
        fin = sample_fin(market_cap_m=50000.0, cagr_oe_eps=0.25)
        val = par_valuation(fin, self.p, cap=30)
        self.assertEqual(val["scale_tier"], "LARGE")
        self.assertEqual(val["scale_cap"], 0.080)
        self.assertAlmostEqual(val["g_exp"], 0.080, places=4)

    def test_mid_small_cap_scale_ceiling(self):
        # Enterprise with MCap $5B (< $25B) -> MID/SM tier with scale cap = 12.0%
        # With historical 25% CAGR and CAP 30: 0.25 * (0.25 - 0.06) + 0.06 = 0.1075 (10.75%)
        fin = sample_fin(market_cap_m=5000.0, cagr_oe_eps=0.25)
        val = par_valuation(fin, self.p, cap=30)
        self.assertEqual(val["scale_tier"], "MID/SM")
        self.assertEqual(val["scale_cap"], 0.120)
        self.assertAlmostEqual(val["g_exp"], 0.1075, places=4)

    def test_turnaround_reality_clamp_on_stagnant_track_record(self):
        # Stagnant track record (e.g. LVMH: cagr = 0.03% < 1.0%), analyst entered g_implied = 7.5%
        # Turnaround clamp clamps raw target to par_g_base (6.0%), resulting in g_exp = 6.00%
        fin = sample_fin(market_cap_m=200000.0, fin_currency="EUR", cagr_oe_eps=0.0003, g_implied=0.075)
        val = par_valuation(fin, self.p, cap=20)
        self.assertEqual(val["scale_tier"], "MEGA")
        self.assertAlmostEqual(val["g_exp"], 0.060, places=4)

    def test_negative_historical_cagr_turnaround_clamp(self):
        # Negative track record (e.g. Exelon: cagr = -7.7%), analyst entered g_implied = 13.5%
        # Turnaround clamp clamps raw target to par_g_base (6.0%), resulting in g_exp = 6.00%
        fin = sample_fin(market_cap_m=48000.0, cagr_oe_eps=-0.077, g_implied=0.135)
        val = par_valuation(fin, self.p, cap=15)
        self.assertEqual(val["scale_tier"], "LARGE")
        self.assertAlmostEqual(val["g_exp"], 0.060, places=4)

    def test_currency_normalization_to_usd(self):
        # Swedish enterprise with MCap 1,300,000M SEK (~$123.5B USD) -> MEGA tier
        fin_sek = sample_fin(market_cap_m=1300000.0, fin_currency="SEK", cagr_oe_eps=0.15)
        val_sek = par_valuation(fin_sek, self.p, cap=20)
        self.assertEqual(val_sek["scale_tier"], "MEGA")
        self.assertEqual(val_sek["scale_cap"], 0.065)

        # Canadian enterprise with MCap 15,000M CAD (~$10.8B USD) -> MID/SM tier
        fin_cad = sample_fin(market_cap_m=15000.0, fin_currency="CAD", cagr_oe_eps=0.15)
        val_cad = par_valuation(fin_cad, self.p, cap=20)
        self.assertEqual(val_cad["scale_tier"], "MID/SM")
        self.assertEqual(val_cad["scale_cap"], 0.120)


if __name__ == "__main__":
    unittest.main()
