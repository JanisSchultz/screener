"""Tests for the v6.30 4-Filter Credible Growth Engine & Equity Bond Below PAR Maths."""
from __future__ import annotations

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

    def test_cap_30_step_down_weight_075(self):
        # g_raw = 10%, GDP base = 3.5%, CAP 30 weight = 0.75 -> 0.75*0.10 + 0.25*0.035 = 0.08375 (8.375%)
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.08375, places=5)
        self.assertAlmostEqual(val["g_imp"], val["g_exp"])
        self.assertEqual(val["exp_coupon"], val["imp_coupon"])

    def test_cap_20_step_down_weight_060(self):
        # g_raw = 10%, GDP base = 3.5%, CAP 20 weight = 0.60 -> 0.60*0.10 + 0.40*0.035 = 0.074 (7.40%)
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_exp"], 0.0740, places=4)

    def test_cap_15_step_down_weight_045(self):
        # g_raw = 10%, GDP base = 3.5%, CAP 15 weight = 0.45 -> 0.45*0.10 + 0.55*0.035 = 0.06425 (6.425%)
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=15)
        self.assertAlmostEqual(val["g_exp"], 0.06425, places=5)

    def test_unpopulated_cap_falls_back_to_default_weight_060(self):
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=None)
        self.assertAlmostEqual(val["g_exp"], 0.0740, places=4)

    def test_analyst_override_g_est_precedes_automated_filters(self):
        fin = sample_fin(sales_ttm_m=5000.0, cagr_oe_eps=0.15, sales_cagr=0.04, g_est=0.11)
        val = par_valuation(fin, self.p, cap=20)
        self.assertEqual(val["g_exp"], 0.11)
        self.assertIsNone(val["g_fund"])
        self.assertIsNone(val["g_demand"])

    def test_filter1_capital_supply_ceiling_binds_high_payout_dilutive_business(self):
        # High-payout / low-ROIIC / share-diluting business (e.g. BLK / insurer archetype):
        # retention = 0.30, roiic = 0.06, roic_median = 0.12 -> r_inc = 0.09
        # zc_pricing = 0.015 (Scale moat, roic_op = 0.20 < 0.30), dilution = -0.015
        # g_fund = 0.30 * 0.09 + 0.015 - 0.015 = 0.027 (2.70%) < g_demand (8.5%)
        # Below 3.5% GDP -> No Free Lunch keeps 2.70%
        fin = sample_fin(
            sales_ttm_m=20000.0,
            retention_rate=0.30,
            roiic=0.06,
            roic_median=0.12,
            roic_operating=0.20,
            buyback_yield=-0.015,
            sales_cagr=0.12,
            sales_cagr_yrs=5,
            g_implied=0.085,
        )
        val = par_valuation(fin, self.p, cap=20, moat="Scale economies shared")
        self.assertAlmostEqual(val["g_fund"], 0.0270, places=4)
        self.assertAlmostEqual(val["g_demand"], 0.1025, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0270, places=4)

    def test_filter1_zero_capital_tollbooth_not_penalized_for_high_payout_or_goodwill(self):
        # Pure Tollbooth with >= 35% Operating ROIC (e.g. CME / SPGI):
        # Even with 95% dividend payout (retention = 0.05) or M&A goodwill depressing GAAP ROIC to 11%,
        # Zero-Capital Pricing grants g_fund = 18.0%, pre-fade g_demand = 13.5% (12% sales + 1% bb + 0.5% margin) ->
        # faded at CAP 30 (w=0.75): 0.75*0.135 + 0.25*0.035 = 11.00% -> bounded by Large-Rev Size Gravity at 10.00%
        fin = sample_fin(
            sales_ttm_m=15300.0,
            retention_rate=0.05,
            roiic=0.05,
            roic_median=0.11,
            roic_operating=1.50,
            roic_est=0.35,
            buyback_yield=0.01,
            sales_cagr=0.12,
            sales_cagr_yrs=5,
            cagr_oe_eps=0.13,
            g_implied=0.095,
        )
        val = par_valuation(fin, self.p, cap=30, moat="Toll booth / Switching costs")
        self.assertEqual(val["g_fund"], 0.180)
        self.assertEqual(val["g_demand"], 0.135)
        self.assertAlmostEqual(val["g_exp"], 0.1000, places=4)

    def test_prefade_18pct_cap_and_no_g_implied_lock_frees_googl_to_mega_ceiling(self):
        # GOOGL archetype: 17.15% 5Y sales CAGR + 1.77% buybacks -> pre-fade g_demand = 18.0%, g_fund = 18.0%.
        # At CAP 15 (w = 0.45): faded_g = 0.45*0.18 + 0.55*0.035 = 10.025%.
        # Legacy g_implied = 7.0% no longer locks GOOGL; Mega-Rev Size Gravity (8.50%) bounds cleanly!
        fin_googl = sample_fin(
            sales_ttm_m=402836.0,
            retention_rate=1.0,
            roiic=0.3316,
            roic_median=0.2883,
            roic_operating=0.3166,
            roic_est=0.35,
            sales_cagr=0.1715,
            sales_cagr_yrs=5,
            buyback_yield=0.0177,
            cagr_oe_eps=0.3447,
            g_implied=0.070,
        )
        val = par_valuation(fin_googl, self.p, cap=15, moat="Toll booth / Switching costs")
        self.assertEqual(val["g_fund"], 0.180)
        self.assertEqual(val["g_demand"], 0.180)
        self.assertAlmostEqual(val["g_exp"], 0.0850, places=4)

    def test_g_implied_used_strictly_as_fallback_when_statement_growth_missing(self):
        # When both sales_cagr and cagr_oe_eps are missing (e.g. BAM.CA / newly listed holding company),
        # g_implied serves as already-faded fallback bounded by Size Gravity
        fin_fallback = sample_fin(
            sales_ttm_m=6000.0,
            cagr_oe_eps=None,
            sales_cagr=None,
            g_implied=0.085,
        )
        val = par_valuation(fin_fallback, self.p, cap=15)
        self.assertAlmostEqual(val["g_exp"], 0.0850, places=4)

    def test_objective_fade_undercuts_optimistic_staple_g_implied(self):
        # PG archetype: 2.7% 5Y sales + 0.8% buybacks (+0.5% mix = 4.0% pre-fade demand) ->
        # at CAP 20 (w=0.60): 0.60*0.040 + 0.40*0.035 = 3.80%, undercutting optimistic g_implied = 6.0%!
        fin_pg = sample_fin(
            sales_ttm_m=87000.0,
            retention_rate=0.40,
            roic_median=0.22,
            roic_operating=0.50,
            sales_cagr=0.027,
            sales_cagr_yrs=5,
            buyback_yield=0.008,
            cagr_oe_eps=0.038,
            g_implied=0.060,
        )
        val = par_valuation(fin_pg, self.p, cap=20, moat="Scale economies shared")
        self.assertAlmostEqual(val["g_exp"], 0.0380, places=4)

    def test_filter2_demand_and_margin_ceiling_cuts_margin_expansion_story(self):
        # Margin-expansion story (e.g. OTIS archetype):
        # Historical OE EPS grew 9.6% via margin expansion, g_implied entered as 8.0%,
        # but actual 5Y sales_cagr = 2.5% + buyback_yield = 2.0% -> top_per_share = 4.5%
        # Margin ceiling allows at most +0.5% -> g_demand = 5.0%
        # At CAP 20 (w = 0.60): 0.60 * 0.05 + 0.40 * 0.035 = 0.044 (4.40%)
        fin = sample_fin(
            sales_ttm_m=14000.0,
            retention_rate=0.60,
            roic_median=0.35,
            roic_operating=0.40,
            sales_cagr=0.025,
            sales_cagr_yrs=5,
            buyback_yield=0.020,
            cagr_oe_eps=0.096,
            g_implied=0.080,
        )
        val = par_valuation(fin, self.p, cap=20, moat="Toll booth / Switching costs")
        self.assertAlmostEqual(val["g_demand"], 0.0500, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0440, places=4)

    def test_filter2_short_3y_window_safeguard_only_when_p2p_ok(self):
        # 3Y Yahoo window with temporary destocking (sales_cagr = 1.0%, bb = 0.0%), 5Y cycle OE CAGR = 8.0%:
        # When p2p_ok == 'Y': blends 0.5*(1.0%) + 0.5*(8.0%) = 4.5% (and since g=8% >= 4.5%, +0.5% -> 5.0%)
        fin_ok = sample_fin(
            sales_ttm_m=10000.0, sales_cagr=0.010, sales_cagr_yrs=3,
            buyback_yield=0.0, cagr_oe_eps=0.080, p2p_ok="Y", g_implied=0.075,
        )
        val_ok = par_valuation(fin_ok, self.p, cap=20)
        self.assertAlmostEqual(val_ok["g_demand"], 0.0500, places=4)

        # When p2p_ok == 'N' (stagnant cycle, e.g. LVMH): no upward rescue
        fin_stag = sample_fin(
            sales_ttm_m=90000.0, sales_cagr=0.007, sales_cagr_yrs=3,
            buyback_yield=0.0, cagr_oe_eps=0.000, p2p_ok="N", g_implied=0.075,
        )
        val_stag = par_valuation(fin_stag, self.p, cap=20)
        # top_per_share = 0.7%, g = 0.0% < 0.7% -> 0.5*0.7% + 0.5*0.0% = 0.35% -> floored at 2.0%
        self.assertAlmostEqual(val_stag["g_exp"], 0.0200, places=4)

    def test_asymmetric_low_growth_not_faded_up(self):
        # g_raw = 2.8% < 3.5% GDP -> No Free Lunch! Kept at 2.8%, NOT faded up toward 3.5%
        fin_low = sample_fin(cagr_oe_eps=0.028)
        for cap_val in (30, 20, 15):
            val = par_valuation(fin_low, self.p, cap=cap_val)
            self.assertAlmostEqual(val["g_exp"], 0.028, places=4)

    def test_negative_cagr_floored_at_two_percent(self):
        fin_neg = sample_fin(cagr_oe_eps=-0.10)
        val = par_valuation(fin_neg, self.p, cap=30)
        self.assertAlmostEqual(val["g_exp"], 0.02, places=4)

    def test_filter4b_revenue_size_gravity_frees_high_multiple_mid_revenue_compounder(self):
        # ISRG archetype: Market Cap = $180B USD, but Revenue = $10B USD (< $15B) -> MID/SM tier (12.0% cap)!
        # sales_cagr = 17.0%, cagr_oe_eps = 16.0% < 17.0% -> g_demand = 0.5*17% + 0.5*16% = 16.5%
        # At CAP 20 (w=0.60): 0.60*0.165 + 0.40*0.035 = 0.113 (11.30% > 8.5% Mega & 10.0% Large caps!)
        fin_isrg = sample_fin(
            market_cap_m=180000.0, sales_ttm_m=10000.0,
            sales_cagr=0.17, sales_cagr_yrs=5, cagr_oe_eps=0.16, roic_est=0.35, g_implied=0.13,
        )
        val = par_valuation(fin_isrg, self.p, cap=20, moat="Toll booth / Switching costs")
        self.assertEqual(val["scale_tier"], "MID/SM")
        self.assertEqual(val["scale_cap"], 0.120)
        self.assertAlmostEqual(val["g_exp"], 0.1130, places=4)

    def test_filter4b_mega_and_large_revenue_ceilings(self):
        # Mega-Revenue >= $50B USD -> capped at 8.5%
        fin_mega = sample_fin(sales_ttm_m=80000.0, cagr_oe_eps=0.20)
        val_mega = par_valuation(fin_mega, self.p, cap=30)
        self.assertEqual(val_mega["scale_tier"], "MEGA")
        self.assertEqual(val_mega["scale_cap"], 0.085)
        self.assertAlmostEqual(val_mega["g_exp"], 0.085, places=4)

        # Large-Revenue $15B-$50B USD -> 18% pre-fade cap + CAP 30 fade = 14.375% -> capped cleanly at 10.0%!
        fin_large = sample_fin(sales_ttm_m=30000.0, cagr_oe_eps=0.20, roic_est=0.35)
        val_large = par_valuation(fin_large, self.p, cap=30, moat="Toll booth / Switching costs")
        self.assertEqual(val_large["scale_tier"], "LARGE")
        self.assertEqual(val_large["scale_cap"], 0.100)
        self.assertAlmostEqual(val_large["g_exp"], 0.100, places=4)

    def test_currency_normalization_on_revenue_tiers(self):
        # European enterprise with 50,000M EUR revenue (~$54B USD) -> MEGA tier (8.5% cap)
        fin_eur = sample_fin(sales_ttm_m=50000.0, fin_currency="EUR", cagr_oe_eps=0.15)
        val_eur = par_valuation(fin_eur, self.p, cap=20)
        self.assertEqual(val_eur["scale_tier"], "MEGA")
        self.assertEqual(val_eur["scale_cap"], 0.085)

        # Canadian enterprise with 15,000M CAD revenue (~$10.8B USD) -> MID/SM tier (12.0% cap)
        fin_cad = sample_fin(sales_ttm_m=15000.0, fin_currency="CAD", cagr_oe_eps=0.15)
        val_cad = par_valuation(fin_cad, self.p, cap=20)
        self.assertEqual(val_cad["scale_tier"], "MID/SM")
        self.assertEqual(val_cad["scale_cap"], 0.120)

    def test_metrics_summarize_computes_median_buyback_immune_to_merger_spike(self):
        # 2020->2021 (-2% shares), 2021->2022 (+30% M&A stock jump), 2022->2023 (-2%), 2023->2024 (-2%), 2024->2025 (-2%)
        # Median YoY reduction should be +2.04% (100/98 - 1), completely ignoring the one-year FY22 merger jump!
        series = {
            "sales": {2020: 100e6, 2021: 110e6, 2022: 140e6, 2023: 154e6, 2024: 169e6, 2025: 186e6},
            "ni": {2020: 20e6, 2021: 22e6, 2022: 28e6, 2023: 31e6, 2024: 34e6, 2025: 38e6},
            "ebit": {2020: 26e6, 2021: 28e6, 2022: 36e6, 2023: 40e6, 2024: 44e6, 2025: 49e6},
            "dividends": {2020: 6e6, 2021: 6.6e6, 2022: 8.4e6, 2023: 9.3e6, 2024: 10.2e6, 2025: 11.4e6},
            "equity": {2020: 80e6, 2021: 85e6, 2022: 150e6, 2023: 160e6, 2024: 170e6, 2025: 180e6},
            "debt": {y: 20e6 for y in range(2020, 2026)},
            "cash": {y: 10e6 for y in range(2020, 2026)},
            "shares": {2020: 100e6, 2021: 98e6, 2022: 120e6, 2023: 117.6e6, 2024: 115.25e6, 2025: 112.94e6},
        }
        m = metrics.summarize(series)
        self.assertEqual(m["sales_cagr_yrs"], 5)
        self.assertAlmostEqual(m["sales_cagr"], (186.0 / 100.0) ** 0.2 - 1.0, places=3)
        self.assertGreater(m["buyback_yield"], 0.019)
        self.assertAlmostEqual(m["retention_rate"], 0.70, places=3)
        self.assertIsNotNone(m["roiic"])

    def test_growth_margin_of_safety_calculation(self):
        fin = sample_fin(cagr_oe_eps=0.10)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_gap"], round(val["g_exp"] - val["g_market"], 4), places=4)

    def test_pillar2_hist_cap_clamps_zirp_bubble_midpoint(self):
        fin = sample_fin(mult_low_5y=30.0, mult_high_5y=90.0, g_est=0.10, roic_operating=0.35)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["par_mult"], 30.0, places=4)

    def test_cap_growth_slope_differentiates_when_g_implied_populated(self):
        # g_implied = 10%, GDP = 3.5%:
        # CAP 30 (w=0.75): g_exp = 0.08375, t_growth = 240 * 0.08375 = 20.10
        # CAP 20 (w=0.60): g_exp = 0.07400, t_growth = 200 * 0.07400 = 14.80
        # CAP 15 (w=0.45): g_exp = 0.06425, t_growth = 170 * 0.06425 = 10.9225
        fin = sample_fin(mult_low_5y=20.0, mult_high_5y=40.0, g_implied=0.10, roic_operating=0.35)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)
        self.assertAlmostEqual(v30["par_mult"], (20.10 + 30.0 + 35.0) / 3.0, places=4)
        self.assertAlmostEqual(v20["par_mult"], (14.80 + 30.0 + 35.0) / 3.0, places=4)
        self.assertAlmostEqual(v15["par_mult"], (10.9225 + 30.0 + 35.0) / 3.0, places=4)
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
        fin = sample_fin(mult_low_5y=18.0, mult_high_5y=36.0, g_implied=0.085, roic_operating=0.22)
        val0 = par_valuation(fin, self.p, cap=15)
        fin_at_par = sample_fin(
            price=val0["par_val"], peak_oe_eps=5.0,
            mult_low_5y=18.0, mult_high_5y=36.0, g_implied=0.085, roic_operating=0.22,
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
