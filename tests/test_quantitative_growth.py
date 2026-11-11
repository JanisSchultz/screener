"""Tests for the v6.32 3-Anchor Starting Growth (g_start), Operating Cost Smoothing, Mauboussin Galton ROIC Regression & Logarithmic Decay Curve (g_exp)."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.fetch import metrics
from screener.gates import params, par_valuation, solve_irr_5y


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
        # For roic_operating = 0.25 and CAP = 20 (pers = 0.75):
        # roic_log = 0.12 + 0.25 * ln(1 + 0.13/0.25) = 0.2247
        # roic_exp = 0.75 * (0.2247 - 0.12) + 0.12 = 0.1985
        # roic_fade_ratio = 0.1985 / 0.2247 = 0.8834
        # Anchor 1 (1Y sales + bb): 14.0% + 1.0% = 15.0%
        # Anchor 2 (5Y sales + bb): 11.0% + 1.0% = 12.0% (cagr_oe_eps = 13.0% >= 12.0%, so no margin haircut)
        # Anchor 3 (Cap growth * roic_fade_ratio + bb): 8.0% * 0.8834 + 1.0% = 8.07%
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
        self.assertAlmostEqual(val["g_cap"], round(0.08 * val["roic_fade_ratio"] + 0.01, 4), places=4)
        self.assertAlmostEqual(val["g_start"], round((0.1500 + 0.1200 + val["g_cap"]) / 3.0, 4), places=4)

    def test_opcost_smoothing_tempers_windfalls_and_cushions_dips(self):
        # Windfall case: 1Y sales +40%, 1Y OpCost +20% -> effective 1Y sales = 0.5*40% + 0.5*min(40%, 20%) = 30%
        # 5Y sales +16%, 5Y OpCost +12% -> effective 5Y sales = 0.5*16% + 0.5*min(16%, 12%) = 14%
        fin_windfall = sample_fin(
            sales_ttm_m=20000.0,
            sales_1y=0.40,
            opcost_1y=0.20,
            sales_cagr=0.16,
            opcost_cagr=0.12,
            cap_growth=0.10,
            buyback_yield=0.0,
            cagr_oe_eps=0.25,
        )
        val_w = par_valuation(fin_windfall, self.p, cap=20)
        # Anchor 1: 30% clamped to 22.0%; Anchor 2: 14.0%
        self.assertAlmostEqual(val_w["g_1y"], 0.2200, places=4)
        self.assertAlmostEqual(val_w["g_hist"], 0.1400, places=4)

        # Cost bloat case: 1Y sales +4%, 1Y OpCost +10% -> min(4%, 10%) = 4%, so cost bloat never inflates growth
        fin_bloat = sample_fin(
            sales_ttm_m=20000.0,
            sales_1y=0.04,
            opcost_1y=0.10,
            sales_cagr=0.04,
            opcost_cagr=0.08,
            cap_growth=0.04,
            buyback_yield=0.0,
            cagr_oe_eps=0.05,
        )
        val_b = par_valuation(fin_bloat, self.p, cap=20)
        self.assertAlmostEqual(val_b["g_1y"], 0.0400, places=4)
        self.assertAlmostEqual(val_b["g_hist"], 0.0400, places=4)

        # Cyclical dip case (ODFL archetype): 1Y sales -6.0%, 1Y OpCost -3.0% -> effective 1Y = -4.5% -> floored at -4.0%,
        # or -5.0% and -2.0% -> effective 1Y = -3.5%
        fin_dip = sample_fin(
            sales_ttm_m=10000.0,
            sales_1y=-0.05,
            opcost_1y=-0.02,
            sales_cagr=0.08,
            opcost_cagr=0.08,
            cap_growth=0.08,
            buyback_yield=0.0,
            cagr_oe_eps=0.09,
        )
        val_d = par_valuation(fin_dip, self.p, cap=20)
        self.assertAlmostEqual(val_d["g_1y"], -0.0350, places=4)

    def test_mauboussin_galton_roic_regression_and_value_driver_pe(self):
        # Ultra-light network (e.g. MA): Operating ROIC = 250%, CAP = 30 (pers = 0.85)
        fin_ultra = sample_fin(roic_operating=2.50, mult_low_5y=25.0, mult_high_5y=60.0)
        val_u = par_valuation(fin_ultra, self.p, cap=30)
        # roic_log = 0.12 + 0.25 * ln(1 + 2.38/0.25) = 0.7082
        # roic_exp = 0.85 * (0.7082 - 0.12) + 0.12 = 0.6200
        self.assertGreater(val_u["roic_exp"], 0.50)
        self.assertIsNotNone(val_u["pe_mm"])
        self.assertIsNotNone(val_u["pe_mck"])
        self.assertAlmostEqual(val_u["pe_vd"], 0.5 * val_u["pe_mm"] + 0.5 * val_u["pe_mck"], places=4)
        self.assertAlmostEqual(val_u["par_mult"], 0.75 * val_u["pe_vd"] + 0.25 * val_u["t_hist"], places=4)

    def test_logarithmic_mauboussin_fade_cap30_cap20_cap15(self):
        fin = sample_fin(cagr_oe_eps=0.10)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)

        self.assertGreater(v30["g_start"], v20["g_start"])
        self.assertGreater(v20["g_start"], v15["g_start"])
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
            roic_operating=0.12,
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
            roic_operating=2.54,
        )
        val = par_valuation(fin_ma, self.p, cap=20, moat="Toll booth / Switching costs")
        self.assertGreater(val["g_start"], 0.145)
        self.assertGreater(val["g_exp"], 0.085)
        self.assertGreater(val["roic_exp"], 0.50)
        self.assertGreater(val["pe_vd"], 25.0)

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
        self.assertLess(val["g_start"], 0.040)
        self.assertLess(val["g_exp"], 0.040)

    def test_progressive_insurer_archetype_scales_smoothly(self):
        # PGR archetype: $87.7B revenue, 16.9% 1Y sales, 15.5% 5Y sales, 16.4% capital growth, +0.16% buybacks, CAP 15
        fin_pgr = sample_fin(
            sales_ttm_m=87696.0,
            sales_1y=0.169,
            sales_cagr=0.155,
            cap_growth=0.164,
            buyback_yield=0.0016,
            cagr_oe_eps=0.180,
            roic_operating=0.206,
        )
        val = par_valuation(fin_pgr, self.p, cap=15, moat="Scale economies shared")
        self.assertGreater(val["g_start"], 0.150)
        self.assertGreater(val["g_exp"], 0.078)
        self.assertLess(val["g_exp"], 0.088)

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
        )
        val = par_valuation(fin_googl, self.p, cap=15, moat="Toll booth / Switching costs")
        self.assertEqual(val["scale_tier"], "HYPER")
        self.assertGreater(val["g_start"], 0.155)
        self.assertGreater(val["g_exp"], 0.075)
        self.assertLess(val["g_exp"], 0.085)

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
            roic_operating=0.12,
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
            roic_operating=0.12,
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
        # g_start <= 3.5% GDP -> No Free Lunch! Kept at g_start, NOT faded up toward 3.5%
        fin_low = sample_fin(cagr_oe_eps=0.028, roic_operating=0.12)
        for cap_val in (30, 20, 15):
            val = par_valuation(fin_low, self.p, cap=cap_val)
            self.assertAlmostEqual(val["g_start"], 0.0280, places=4)
            self.assertAlmostEqual(val["g_exp"], 0.0280, places=4)

    def test_negative_cagr_floored_at_two_percent(self):
        fin_neg = sample_fin(cagr_oe_eps=-0.10)
        val = par_valuation(fin_neg, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.02, places=4)

    def test_continuous_size_factor_and_currency_normalization(self):
        fin_eur = sample_fin(sales_ttm_m=50000.0, fin_currency="EUR", cagr_oe_eps=0.15)
        val_eur = par_valuation(fin_eur, self.p, cap=20)
        self.assertEqual(val_eur["scale_tier"], "MEGA")
        self.assertAlmostEqual(val_eur["size_factor"], round(1.08 - 0.11 * math.log10(50.0 * 1.08), 4), places=4)

        fin_cad = sample_fin(sales_ttm_m=15000.0, fin_currency="CAD", cagr_oe_eps=0.15)
        val_cad = par_valuation(fin_cad, self.p, cap=20)
        self.assertEqual(val_cad["scale_tier"], "MID/SM")
        self.assertGreater(val_cad["size_factor"], val_eur["size_factor"])
        self.assertGreater(val_cad["g_exp"], val_eur["g_exp"])

    def test_metrics_summarize_computes_sales_1y_opcost_cap_growth_and_median_buyback(self):
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
        self.assertAlmostEqual(m["opcost_1y"], (186.0 - 49.0) / (169.0 - 44.0) - 1.0, places=3)
        self.assertAlmostEqual(m["opcost_cagr"], ((186.0 - 49.0) / (100.0 - 26.0)) ** 0.2 - 1.0, places=3)
        self.assertIsNotNone(m["cap_growth"])
        self.assertAlmostEqual(m["cap_growth"], 0.10, places=2)
        self.assertGreater(m["buyback_yield"], 0.019)

    def test_growth_margin_of_safety_calculation(self):
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_gap"], round(val["g_exp"] - val["g_market"], 4), places=4)

    def test_uncapped_harmonic_5y_pe_dampens_spikes_without_35_cap(self):
        # Low = 20x, High = 100x -> arithmetic mean is 60x, but harmonic mean is 2*20*100/120 = 33.33x
        fin_spike = sample_fin(mult_low_5y=20.0, mult_high_5y=100.0, g_est=0.10, roic_operating=0.35)
        val_spike = par_valuation(fin_spike, self.p, cap=20)
        self.assertAlmostEqual(val_spike["t_hist"], 2.0 * 20.0 * 100.0 / 120.0, places=4)
        self.assertAlmostEqual(val_spike["par_mult"], 0.75 * val_spike["pe_vd"] + 0.25 * val_spike["t_hist"], places=4)

        # True high-multiple compounder (e.g. Hermes): Low = 38x, High = 52x -> harmonic mean = 43.91x (not capped at 35.0!)
        fin_hermes = sample_fin(mult_low_5y=38.0, mult_high_5y=52.0, g_est=0.082, roic_operating=0.55)
        val_hermes = par_valuation(fin_hermes, self.p, cap=30)
        self.assertGreater(val_hermes["t_hist"], 43.0)
        self.assertAlmostEqual(val_hermes["par_mult"], 0.75 * val_hermes["pe_vd"] + 0.25 * val_hermes["t_hist"], places=4)

    def test_pure_75_25_par_mult_not_capped_by_mult_high_5y(self):
        # When 0.75 * pe_vd + 0.25 * t_hist exceeds mult_high_5y (e.g. BLK / depressed 5Y range), par_mult is not capped at mh
        fin = sample_fin(mult_low_5y=12.0, mult_high_5y=15.0, g_est=0.09, roic_operating=0.35)
        val = par_valuation(fin, self.p, cap=20)
        self.assertGreater(val["par_mult"], 15.0)
        self.assertAlmostEqual(val["par_mult"], 0.75 * val["pe_vd"] + 0.25 * val["t_hist"], places=4)

    def test_value_driver_differentiates_across_cap_tiers_and_handles_g_equal_k(self):
        fin = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, cagr_oe_eps=0.10, roic_operating=0.35)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)
        self.assertGreater(v30["pe_vd"], v20["pe_vd"])
        self.assertGreater(v20["pe_vd"], v15["pe_vd"])
        self.assertGreater(v30["par_mult"], v20["par_mult"])
        self.assertGreater(v20["par_mult"], v15["par_mult"])

        # Exact continuity when g_exp == k = 0.0875
        fin_eq_k = sample_fin(mult_low_5y=20.0, mult_high_5y=30.0, g_est=0.0875, roic_operating=0.30)
        val_eq_k = par_valuation(fin_eq_k, self.p, cap=20)
        self.assertIsNotNone(val_eq_k["pe_mck"])
        self.assertGreater(val_eq_k["pe_mck"], 20.0)

    def test_value_driver_penalizes_low_roic_grower_vs_high_roic_grower(self):
        fin_low_roic = sample_fin(mult_low_5y=20.0, mult_high_5y=30.0, g_est=0.09, roic_operating=0.12)
        fin_high_roic = sample_fin(mult_low_5y=20.0, mult_high_5y=30.0, g_est=0.09, roic_operating=0.40)
        val_low = par_valuation(fin_low_roic, self.p, cap=20)
        val_high = par_valuation(fin_high_roic, self.p, cap=20)
        self.assertGreater(val_high["pe_vd"], val_low["pe_vd"] + 5.0)
        self.assertGreater(val_high["par_mult"], val_low["par_mult"] + 3.5)

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

    def test_mid_cycle_compares_owner_eps_like_for_like_at_peak(self):
        # Amortisation-heavy compounder at peak: GAAP EPS 6.0 but Owner EPS (600 + 500 - 100) / 100 = 10.0 = peak,
        # so the 50/50 haircut must not fire (a GAAP-vs-Owner comparison would wrongly give 8.0).
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=600.0, da_ttm_m=500.0, capex_ttm_m=100.0,
                         peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 10.0, places=4)
        self.assertAlmostEqual(val["cur_mult"], 10.0, places=4)

    def test_mid_cycle_blend_uses_owner_eps_on_genuine_decline(self):
        # Genuine decline: current Owner EPS (400 + 300 - 100) / 100 = 6.0 < peak 10.0 -> 0.5 * (10 + 6) = 8.0
        # (a GAAP basis of 4.0 would give 7.0).
        fin = sample_fin(price=100.0, market_cap_m=10000.0, ni_ttm_m=400.0, da_ttm_m=300.0, capex_ttm_m=100.0,
                         peak_oe_eps=10.0)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["peak_eps"], 8.0, places=4)

    def test_gaap_roic_selected_for_balance_sheet_financials_and_concessions(self):
        # Insurer / Bank / Concession should use roic_median (0.104) instead of roic_operating (0.217)
        fin = sample_fin(roic_median=0.104, roic_operating=0.217, fcf_conv=1.0)
        val_ins = par_valuation(fin, self.p, cap=20, sub_industry="Property & Casualty Insurance")
        val_bank = par_valuation(fin, self.p, cap=20, sub_industry="Diversified Banks (mapped)")
        val_conc = par_valuation(fin, self.p, cap=20, sub_industry="Construction & Engineering (mapped)")
        self.assertAlmostEqual(val_ins["roic_exp"], 0.104, places=4)
        self.assertAlmostEqual(val_bank["roic_exp"], 0.104, places=4)
        self.assertAlmostEqual(val_conc["roic_exp"], 0.104, places=4)

        # Insurance Brokers and Payment Networks should continue using roic_operating (0.217)
        val_broker = par_valuation(fin, self.p, cap=20, sub_industry="Insurance Brokers")
        val_pay = par_valuation(fin, self.p, cap=20, sub_industry="Transaction & Payment Processing Services")
        self.assertGreater(val_broker["roic_exp"], 0.17)
        self.assertGreater(val_pay["roic_exp"], 0.17)

    def test_mtm_holdco_uses_nav_value_driver_physics(self):
        # 3i Group / Investor AB style Mark-to-Market HoldCo (fcf_conv is None or < 0.25)
        fin_mtm = sample_fin(
            roic_median=0.1972, roic_operating=0.1972,
            mult_low_5y=4.3, mult_high_5y=7.2,
            fcf_conv=None, peak_eps_est=None,
        )
        val_mtm = par_valuation(fin_mtm, self.p, cap=30, sub_industry="Multi-Sector Holdings (mapped)")
        expected_nav_pe = 1.0 / val_mtm["roic_exp"]
        self.assertAlmostEqual(val_mtm["pe_vd"], expected_nav_pe, places=4)
        self.assertAlmostEqual(val_mtm["pe_mm"], expected_nav_pe, places=4)
        self.assertAlmostEqual(val_mtm["pe_mck"], expected_nav_pe, places=4)
        self.assertAlmostEqual(val_mtm["par_mult"], 0.75 * expected_nav_pe + 0.25 * val_mtm["t_hist"], places=4)

        # Operating HoldCo consolidating cash-generating subsidiaries (fcf_conv >= 0.25) uses standard Value Driver
        fin_op_holdco = sample_fin(
            roic_median=0.15, roic_operating=0.18,
            mult_low_5y=15.0, mult_high_5y=25.0,
            fcf_conv=0.80, peak_eps_est=None,
        )
        val_op = par_valuation(fin_op_holdco, self.p, cap=20, sub_industry="Multi-Sector Holdings (mapped)")
        self.assertGreater(val_op["pe_vd"], 1.0 / val_op["roic_exp"] + 2.0)

    def test_finite_concession_omits_stage2_terminal_perpetuity(self):
        # Eiffage / Vinci style IFRIC-12 Concessionaire (fcf_conv > 1.25 in Construction & Engineering)
        fin_conc = sample_fin(
            roic_median=0.1342, roic_operating=0.4025,
            mult_low_5y=5.7, mult_high_5y=7.9,
            fcf_conv=1.82,
        )
        val_conc = par_valuation(fin_conc, self.p, cap=15, sub_industry="Construction & Engineering (mapped)")
        # Compare against a non-concession with the same GAAP ROIC
        val_std = par_valuation(fin_conc, self.p, cap=15, sub_industry="Industrial Machinery & Supplies & Components")
        self.assertAlmostEqual(val_conc["roic_exp"], 0.1286, places=3)
        self.assertLess(val_conc["pe_mck"], 9.0)
        self.assertLess(val_conc["pe_vd"], val_std["pe_vd"] - 3.0)
        self.assertAlmostEqual(val_conc["par_mult"], 0.75 * val_conc["pe_vd"] + 0.25 * val_conc["t_hist"], places=4)

    def test_textbook_5y_cash_flow_irr_satisfies_npv_zero(self):
        # 1. Zero-dividend case reduces exactly to (1 + g_exp) * (par_val / price)^0.2 - 1
        irr_zero_div = solve_irr_5y(price=100.0, par_val=130.0, g_exp=0.09, dy=0.0)
        self.assertAlmostEqual(irr_zero_div, 1.09 * (1.30 ** 0.2) - 1.0, places=9)

        # 2. At-PAR case (price == par_val) reduces to exact geometric compounding (1 + g_exp) * (1 + dy) - 1
        irr_at_par = solve_irr_5y(price=100.0, par_val=100.0, g_exp=0.08, dy=0.025)
        self.assertAlmostEqual(irr_at_par, 1.08 * 1.025 - 1.0, places=9)

        # 3. General Below-PAR and Above-PAR cases satisfy exact 5-year DCF cash-flow equation:
        #    P_0 = sum_{t=1..5} [D_0 * (1 + g_exp)^t / (1 + IRR)^t] + [PAR_Val * (1 + g_exp)^5 / (1 + IRR)^5]
        for price, par_val, g_exp, dy in (
            (80.0, 120.0, 0.085, 0.030),
            (150.0, 100.0, 0.065, 0.040),
            (100.0, 145.0, 0.105, 0.012),
        ):
            irr = solve_irr_5y(price=price, par_val=par_val, g_exp=g_exp, dy=dy)
            self.assertIsNotNone(irr)
            d0 = price * dy
            pv_divs = sum((d0 * ((1.0 + g_exp) ** t)) / ((1.0 + irr) ** t) for t in range(1, 6))
            pv_term = (par_val * ((1.0 + g_exp) ** 5)) / ((1.0 + irr) ** 5)
            self.assertAlmostEqual(pv_divs + pv_term, price, places=7)


if __name__ == "__main__":
    unittest.main()
