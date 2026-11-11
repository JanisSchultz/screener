"""Tests for the v6.31 3-Anchor Starting Growth (g_start) & Logarithmic Mauboussin Decay Curve (g_exp)."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.fetch import metrics
from screener.gates import params, par_valuation


def sample_fin(**overrides) -> dict:
    fin = {
        "price": 100.0,
        "market_cap_m": 10000.0,
        "peak_oe_eps": 5.0,
        "peak_eps_est": None,
        "mult_low_5y": 15.0,
        "mult_high_5y": 25.0,
        "cagr_oe_eps": 0.10,
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

    def test_three_anchor_starting_growth_average(self):
        # Anchor 1 (1Y sales + bb): 14.0% + 1.0% = 15.0%
        # Anchor 2 (5Y sales + bb): 11.0% + 1.0% = 12.0% (cagr_oe_eps = 13.0% >= 12.0%, so no margin haircut)
        # Anchor 3 (Cap growth + bb): 8.0% + 1.0% = 9.0%
        # g_start = (15.0% + 12.0% + 9.0%) / 3 = 12.0%
        fin = sample_fin(
            sales_ttm_m=10000.0,
            sales_1y=0.14,
            sales_cagr=0.11,
            cap_growth=0.08,
            buyback_yield=0.01,
            cagr_oe_eps=0.13,
        )
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_1y"], 0.1500, places=4)
        self.assertAlmostEqual(val["g_hist"], 0.1200, places=4)
        self.assertAlmostEqual(val["g_cap"], 0.0900, places=4)
        self.assertAlmostEqual(val["g_start"], 0.1200, places=4)

    def test_logarithmic_mauboussin_fade_cap30_cap20_cap15(self):
        # For g_start = 10.0%, Rev = $2.5B USD (from $10B market_cap_m / 4.0 -> size_factor = 1.08 - 0.11*log10(2.5) = 1.0362):
        # g_log = 0.035 + 0.12 * ln(1 + 0.065/0.12) = 0.0870
        fin = sample_fin(cagr_oe_eps=0.10)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)

        self.assertAlmostEqual(v30["g_start"], 0.1000, places=4)
        self.assertAlmostEqual(v30["g_log"], 0.0869, places=4)
        self.assertGreater(v30["g_exp"], v20["g_exp"])
        self.assertGreater(v20["g_exp"], v15["g_exp"])
        self.assertAlmostEqual(v30["g_imp"], v30["g_exp"], places=4)
        self.assertEqual(v30["exp_coupon"], v30["imp_coupon"])

    def test_unpopulated_cap_falls_back_to_default_persistence_075(self):
        fin = sample_fin(cagr_oe_eps=0.10)
        v_none = par_valuation(fin, self.p, cap=None)
        v_20 = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(v_none["g_exp"], v_20["g_exp"], places=4)

    def test_analyst_override_g_est_sets_g_exp_while_preserving_objective_g_start(self):
        fin = sample_fin(
            sales_ttm_m=5000.0,
            sales_1y=0.06,
            sales_cagr=0.06,
            cap_growth=0.06,
            cagr_oe_eps=0.06,
            g_est=0.05,
        )
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_start"], 0.0600, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0500, places=4)

    def test_mastercard_archetype_operating_asset_growth_sustains_compounder(self):
        # MA archetype: $32.8B revenue, 16.0% 1Y sales, 16.4% 5Y sales, 10.0% operating capital growth, +2.05% buybacks
        fin_ma = sample_fin(
            sales_ttm_m=32791.0,
            sales_1y=0.1602,
            sales_cagr=0.1642,
            cap_growth=0.1002,
            buyback_yield=0.0205,
            cagr_oe_eps=0.1846,
            roic_operating=0.618,
            roic_est=0.35,
        )
        val = par_valuation(fin_ma, self.p, cap=20, moat="Toll booth / Switching costs")
        # g_1y = 18.07%, g_hist = 18.47%, g_cap = 12.07% -> g_start = 16.20%
        # Fades smoothly via log + Mauboussin (CAP 20 pers=0.75, size_factor=0.913) to ~9.49%
        self.assertAlmostEqual(val["g_start"], 0.1620, places=3)
        self.assertGreater(val["g_exp"], 0.092)
        self.assertLess(val["g_exp"], 0.098)

    def test_mature_staple_pg_archetype_bounded_by_slow_capital_and_sales_growth(self):
        # PG archetype: $84.3B revenue, 0.3% 1Y sales, 3.5% 5Y sales, 0.9% operating capital growth, +0.9% buybacks
        fin_pg = sample_fin(
            sales_ttm_m=84284.0,
            sales_1y=0.003,
            sales_cagr=0.035,
            cap_growth=0.009,
            buyback_yield=0.009,
            cagr_oe_eps=0.038,
            roic_operating=0.30,
        )
        val = par_valuation(fin_pg, self.p, cap=20, moat="Scale economies shared")
        # g_1y = 1.2%, g_hist = 4.1% (margin blend), g_cap = 1.8% -> g_start ~ 2.37% <= 3.5% -> No Free Lunch!
        self.assertLess(val["g_start"], 0.040)
        self.assertLess(val["g_exp"], 0.040)

    def test_progressive_insurer_archetype_scales_smoothly(self):
        # PGR archetype: $87.7B revenue, 16.9% 1Y sales, 15.5% 5Y sales, 16.4% capital growth, +0.16% buybacks, CAP 20
        fin_pgr = sample_fin(
            sales_ttm_m=87696.0,
            sales_1y=0.169,
            sales_cagr=0.155,
            cap_growth=0.164,
            buyback_yield=0.0016,
            cagr_oe_eps=0.180,
            roic_operating=0.25,
        )
        val = par_valuation(fin_pgr, self.p, cap=15, moat="Scale economies shared")
        self.assertAlmostEqual(val["g_start"], 0.1643, places=3)
        self.assertAlmostEqual(val["g_exp"], 0.0825, places=3)

    def test_hyper_scale_googl_fades_via_continuous_log_revenue_and_cap15(self):
        # GOOGL archetype: $402.8B revenue, CAP 15 (pers=0.62, size_factor=0.793)
        fin_googl = sample_fin(
            sales_ttm_m=402836.0,
            sales_1y=0.151,
            sales_cagr=0.1715,
            cap_growth=0.141,
            buyback_yield=0.0177,
            cagr_oe_eps=0.3447,
            roic_operating=0.3166,
            roic_est=0.35,
        )
        val = par_valuation(fin_googl, self.p, cap=15, moat="Toll booth / Switching costs")
        self.assertEqual(val["scale_tier"], "HYPER")
        self.assertAlmostEqual(val["g_start"], 0.1722, places=3)
        self.assertAlmostEqual(val["g_exp"], 0.0799, places=3)

    def test_anchor2_margin_contraction_check(self):
        # When 5Y OE EPS CAGR (3.0%) lagged 5Y sales + buybacks (8.0% + 2.0% = 10.0%),
        # Anchor 2 blends 50/50: 0.5 * 10.0% + 0.5 * 3.0% = 6.5%
        fin = sample_fin(
            sales_ttm_m=14000.0,
            sales_1y=0.08,
            sales_cagr=0.08,
            cap_growth=0.08,
            buyback_yield=0.02,
            cagr_oe_eps=0.03,
        )
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_1y"], 0.1000, places=4)
        self.assertAlmostEqual(val["g_hist"], 0.0650, places=4)
        self.assertAlmostEqual(val["g_cap"], 0.1000, places=4)
        self.assertAlmostEqual(val["g_start"], (0.10 + 0.065 + 0.10) / 3.0, places=4)

    def test_anchor1_floor_limits_single_year_cyclical_contraction(self):
        # If 1Y sales dropped -15% in a cyclical downturn, Anchor 1 is floored at -4.0%
        fin = sample_fin(
            sales_ttm_m=10000.0,
            sales_1y=-0.15,
            sales_cagr=0.08,
            cap_growth=0.07,
            buyback_yield=0.0,
            cagr_oe_eps=0.08,
        )
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_1y"], -0.0400, places=4)
        self.assertAlmostEqual(val["g_start"], (-0.04 + 0.08 + 0.07) / 3.0, places=4)

    def test_g_implied_used_strictly_as_fallback_when_statement_growth_missing(self):
        fin_fallback = sample_fin(
            sales_ttm_m=6000.0,
            cagr_oe_eps=None,
            sales_1y=None,
            sales_cagr=None,
            cap_growth=None,
            g_implied=0.085,
        )
        val = par_valuation(fin_fallback, self.p, cap=15)
        self.assertAlmostEqual(val["g_start"], 0.0850, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0850, places=4)

    def test_asymmetric_low_growth_not_faded_up(self):
        # g_start = 2.8% < 3.5% GDP -> No Free Lunch! Kept at 2.8%, NOT faded up toward 3.5%
        fin_low = sample_fin(cagr_oe_eps=0.028)
        for cap_val in (30, 20, 15):
            val = par_valuation(fin_low, self.p, cap=cap_val)
            self.assertAlmostEqual(val["g_start"], 0.0280, places=4)
            self.assertAlmostEqual(val["g_exp"], 0.0280, places=4)

    def test_negative_cagr_floored_at_two_percent(self):
        fin_neg = sample_fin(cagr_oe_eps=-0.10)
        val = par_valuation(fin_neg, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.02, places=4)

    def test_continuous_size_factor_and_currency_normalization(self):
        # European enterprise with 50,000M EUR revenue (~$54B USD) -> MEGA tier, size_factor = 1.08 - 0.11*log10(54) = 0.8894
        fin_eur = sample_fin(sales_ttm_m=50000.0, fin_currency="EUR", cagr_oe_eps=0.15)
        val_eur = par_valuation(fin_eur, self.p, cap=20)
        self.assertEqual(val_eur["scale_tier"], "MEGA")
        self.assertAlmostEqual(val_eur["size_factor"], round(1.08 - 0.11 * math.log10(50.0 * 1.08), 4), places=4)

        # Canadian enterprise with 15,000M CAD revenue (~$10.8B USD) -> MID/SM tier, higher size_factor
        fin_cad = sample_fin(sales_ttm_m=15000.0, fin_currency="CAD", cagr_oe_eps=0.15)
        val_cad = par_valuation(fin_cad, self.p, cap=20)
        self.assertEqual(val_cad["scale_tier"], "MID/SM")
        self.assertGreater(val_cad["size_factor"], val_eur["size_factor"])
        self.assertGreater(val_cad["g_exp"], val_eur["g_exp"])

    def test_metrics_summarize_computes_sales_1y_cap_growth_and_median_buyback(self):
        series = {
            "sales": {2020: 100e6, 2021: 110e6, 2022: 140e6, 2023: 154e6, 2024: 169e6, 2025: 186e6},
            "ni": {2020: 20e6, 2021: 22e6, 2022: 28e6, 2023: 31e6, 2024: 34e6, 2025: 38e6},
            "ebit": {2020: 26e6, 2021: 28e6, 2022: 36e6, 2023: 40e6, 2024: 44e6, 2025: 49e6},
            "dividends": {2020: 6e6, 2021: 6.6e6, 2022: 8.4e6, 2023: 9.3e6, 2024: 10.2e6, 2025: 11.4e6},
            "equity": {2020: 80e6, 2021: 88e6, 2022: 150e6, 2023: 165e6, 2024: 181.5e6, 2025: 199.65e6},
            "assets": {2020: 120e6, 2021: 131e6, 2022: 200e6, 2023: 219e6, 2024: 240e6, 2025: 263e6},
            "debt": {y: 20e6 for y in range(2020, 2026)},
            "cash": {y: 10e6 for y in range(2020, 2026)},
            "shares": {2020: 100e6, 2021: 98e6, 2022: 120e6, 2023: 117.6e6, 2024: 115.25e6, 2025: 112.94e6},
        }
        m = metrics.summarize(series)
        self.assertEqual(m["sales_cagr_yrs"], 5)
        self.assertAlmostEqual(m["sales_1y"], 186.0 / 169.0 - 1.0, places=3)
        self.assertAlmostEqual(m["sales_cagr"], (186.0 / 100.0) ** 0.2 - 1.0, places=3)
        self.assertIsNotNone(m["cap_growth"])
        self.assertAlmostEqual(m["cap_growth"], 0.10, places=2)
        self.assertGreater(m["buyback_yield"], 0.019)

    def test_growth_margin_of_safety_calculation(self):
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_gap"], round(val["g_exp"] - val["g_market"], 4), places=4)

    def test_pillar2_hist_cap_clamps_zirp_bubble_midpoint(self):
        fin = sample_fin(mult_low_5y=30.0, mult_high_5y=90.0, g_est=0.10, roic_operating=0.35)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["par_mult"], 30.0, places=4)

    def test_cap_growth_slope_differentiates_across_cap_tiers(self):
        fin = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, cagr_oe_eps=0.10, roic_operating=0.35)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)
        self.assertGreater(v30["par_mult"], v20["par_mult"])
        self.assertGreater(v20["par_mult"], v15["par_mult"])

    def test_reinvestment_efficiency_penalizes_low_roic_grower(self):
        fin_low_roic = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, g_est=0.09, roic_operating=0.15)
        val = par_valuation(fin_low_roic, self.p, cap=20)
        expected_eta = (1.0 - 0.09 / 0.15) / (1.0 - 0.09 / 0.35)
        expected_t_growth = 200.0 * expected_eta * 0.09
        expected_par = (expected_t_growth + 30.0 + 15.0) / 3.0
        self.assertAlmostEqual(val["par_mult"], expected_par, places=4)

    def test_closed_form_g_market_inversion_round_trip(self):
        fin = sample_fin(mult_low_5y=18.0, mult_high_5y=36.0, cagr_oe_eps=0.085, roic_operating=0.22)
        val0 = par_valuation(fin, self.p, cap=15)
        fin_at_par = sample_fin(
            price=val0["par_val"], peak_oe_eps=5.0,
            mult_low_5y=18.0, mult_high_5y=36.0, cagr_oe_eps=0.085, roic_operating=0.22,
        )
        val_at_par = par_valuation(fin_at_par, self.p, cap=15)
        self.assertAlmostEqual(val_at_par["g_market"], val0["g_exp"], places=4)
        self.assertAlmostEqual(val_at_par["g_gap"], 0.0, places=4)

    def test_mid_cycle_blend_when_current_eps_below_peak(self):
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=600.0, peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 8.0, places=4)
        self.assertAlmostEqual(val["cur_mult"], 100.0 / 8.0, places=4)

    def test_compounder_at_peak_untouched(self):
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=1000.0, peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 10.0, places=4)

    def test_analyst_override_takes_precedence_over_mid_cycle(self):
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=600.0, peak_oe_eps=10.0, peak_eps_est=7.2)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 7.2, places=4)

    def test_negative_net_income_floored_at_zero(self):
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=-500.0, peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 5.0, places=4)


if __name__ == "__main__":
    unittest.main()
