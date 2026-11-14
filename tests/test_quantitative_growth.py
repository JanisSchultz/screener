"""Tests for the v6.35 Operating Cost Base Growth Ceiling (g_org_exp), Explicit Mauboussin-Fade DCF (r=8.5%), and FCF-Conserved 5Y IRR."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.fetch import metrics
from screener.gates import explicit_dcf_multiple, params, par_valuation, solve_implied_dcf_growth, solve_irr_5y


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

    def test_opcost_cagr_primary_growth_ceiling_and_fallback_chain(self):
        # When opcost_cagr is present (8.5%), it anchors g_org_exp directly regardless of 1Y slump (-4.0%)
        fin = sample_fin(
            sales_ttm_m=10000.0,
            sales_1y=-0.04,
            sales_cagr=0.075,
            opcost_cagr=0.085,
            cap_growth=0.070,
            buyback_yield=0.020,
            cagr_oe_eps=0.11,
        )
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_org_exp"], 0.0850, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.1050, places=4)

        # Fallback to sales_cagr when opcost_cagr is None
        fin_no_oc = dict(fin, opcost_cagr=None)
        val_no_oc = par_valuation(fin_no_oc, self.p, cap=20)
        self.assertAlmostEqual(val_no_oc["g_org_exp"], 0.0750, places=4)
        self.assertAlmostEqual(val_no_oc["g_exp"], 0.0950, places=4)

        # Fallback to cagr_oe_eps - bb_pos when sales_cagr is also None
        fin_oe_only = dict(fin_no_oc, sales_cagr=None)
        val_oe = par_valuation(fin_oe_only, self.p, cap=20)
        self.assertAlmostEqual(val_oe["g_org_exp"], 0.0900, places=4)
        self.assertAlmostEqual(val_oe["g_exp"], 0.1100, places=4)

    def test_1y_slump_does_not_penalize_growth_ceiling_when_opcost_cagr_intact(self):
        # Slump-Cannibal Compounder archetype: 1Y sales -5%, 5Y OpCost CAGR +8.0%, +2.5% buybacks
        fin_slump = sample_fin(
            sales_ttm_m=10000.0,
            sales_1y=-0.05,
            opcost_1y=-0.02,
            sales_cagr=0.08,
            opcost_cagr=0.08,
            cap_growth=0.08,
            buyback_yield=0.025,
            cagr_oe_eps=0.10,
        )
        fin_normal = dict(fin_slump, sales_1y=0.08, opcost_1y=0.08)
        val_slump = par_valuation(fin_slump, self.p, cap=20)
        val_norm = par_valuation(fin_normal, self.p, cap=20)
        self.assertAlmostEqual(val_slump["g_org_exp"], 0.0800, places=4)
        self.assertAlmostEqual(val_slump["par_val"], val_norm["par_val"], places=4)

    def test_mauboussin_galton_roic_regression_and_explicit_dcf_pe(self):
        # Ultra-light network (e.g. MA): Operating ROIC = 250%, CAP = 30 (pers = 0.85)
        fin_ultra = sample_fin(roic_operating=2.50, mult_low_5y=25.0, mult_high_5y=60.0)
        val_u = par_valuation(fin_ultra, self.p, cap=30)
        self.assertGreater(val_u["roic_exp"], 0.50)
        self.assertIsNotNone(val_u["pe_mm"])
        self.assertIsNotNone(val_u["pe_mck"])
        # pe_vd = Stage 1 PV (pe_mm) + Stage 2 Terminal PV (pe_mck), and par_mult = 100% pe_vd
        self.assertAlmostEqual(val_u["pe_vd"], val_u["pe_mm"] + val_u["pe_mck"], places=4)
        self.assertAlmostEqual(val_u["par_mult"], val_u["pe_vd"], places=4)

    def test_explicit_mauboussin_fade_dcf_cap30_cap20_cap15(self):
        fin = sample_fin(opcost_cagr=0.09, roic_operating=0.28)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)

        self.assertAlmostEqual(v30["g_org_exp"], 0.0900, places=4)
        self.assertAlmostEqual(v20["g_org_exp"], 0.0900, places=4)
        self.assertAlmostEqual(v15["g_org_exp"], 0.0900, places=4)
        # Longer CAP runway produces higher Stage 1 + Stage 2 DCF Fair P/E
        self.assertGreater(v30["par_mult"], v20["par_mult"])
        self.assertGreater(v20["par_mult"], v15["par_mult"])

    def test_unpopulated_cap_falls_back_to_default_20y_dcf(self):
        fin = sample_fin(opcost_cagr=0.09)
        v_none = par_valuation(fin, self.p, cap=None)
        v_20 = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(v_none["par_mult"], v_20["par_mult"], places=4)

    def test_analyst_override_g_est_sets_g_exp_and_g_org_exp(self):
        fin = sample_fin(
            sales_ttm_m=5000.0,
            sales_1y=0.06,
            sales_cagr=0.06,
            opcost_cagr=0.06,
            cap_growth=0.06,
            cagr_oe_eps=0.06,
            buyback_yield=0.01,
            roic_operating=0.12,
            g_est=0.08,
        )
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_org_exp"], 0.0700, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0800, places=4)

    def test_mastercard_archetype_operating_asset_growth_sustains_compounder(self):
        # MA archetype: $32.8B revenue, 14.5% OpCost CAGR (capped at LARGE scale_cap = 10.5%), +2.05% buybacks
        fin_ma = sample_fin(
            sales_ttm_m=32791.0,
            sales_1y=0.1602,
            sales_cagr=0.1642,
            opcost_cagr=0.1450,
            cap_growth=0.1002,
            buyback_yield=0.0205,
            cagr_oe_eps=0.1846,
            roic_operating=2.54,
        )
        val = par_valuation(fin_ma, self.p, cap=20, moat="Toll booth / Switching costs")
        self.assertAlmostEqual(val["g_org_exp"], 0.1050, places=4)
        self.assertGreater(val["g_exp"], 0.125)
        self.assertGreater(val["roic_exp"], 0.50)
        self.assertGreater(val["pe_vd"], 25.0)

    def test_mature_staple_pg_archetype_bounded_by_slow_opcost_growth(self):
        # PG archetype: $84.3B revenue, 2.8% OpCost CAGR, +0.9% buybacks
        fin_pg = sample_fin(
            sales_ttm_m=84284.0,
            sales_1y=0.003,
            sales_cagr=0.035,
            opcost_cagr=0.028,
            cap_growth=0.009,
            buyback_yield=0.009,
            cagr_oe_eps=0.038,
            roic_operating=0.30,
        )
        val = par_valuation(fin_pg, self.p, cap=20, moat="Scale economies shared")
        self.assertAlmostEqual(val["g_org_exp"], 0.0280, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0370, places=4)

    def test_hyper_scale_googl_capped_by_hyper_scale_cap(self):
        # GOOGL archetype: $402.8B revenue -> HYPER scale_cap = 9.5%
        fin_googl = sample_fin(
            sales_ttm_m=402836.0,
            sales_1y=0.151,
            sales_cagr=0.1715,
            opcost_cagr=0.145,
            cap_growth=0.141,
            buyback_yield=0.0177,
            cagr_oe_eps=0.3447,
            roic_operating=0.3166,
        )
        val = par_valuation(fin_googl, self.p, cap=15, moat="Toll booth / Switching costs")
        self.assertEqual(val["scale_tier"], "HYPER")
        self.assertAlmostEqual(val["g_org_exp"], 0.0950, places=4)

    def test_g_implied_used_strictly_as_fallback_when_statement_growth_missing(self):
        fin_fallback = sample_fin(
            sales_ttm_m=6000.0,
            cagr_oe_eps=None,
            sales_1y=None,
            sales_cagr=None,
            opcost_cagr=None,
            cap_growth=None,
            g_implied=0.085,
        )
        val = par_valuation(fin_fallback, self.p, cap=15)
        self.assertAlmostEqual(val["g_org_exp"], 0.0850, places=4)
        self.assertAlmostEqual(val["g_exp"], 0.0850, places=4)

    def test_low_growth_preserved_down_to_two_percent_floor(self):
        fin_low = sample_fin(opcost_cagr=0.028, roic_operating=0.12)
        for cap_val in (30, 20, 15):
            val = par_valuation(fin_low, self.p, cap=cap_val)
            self.assertAlmostEqual(val["g_org_exp"], 0.0280, places=4)
            self.assertAlmostEqual(val["g_exp"], 0.0280, places=4)

    def test_negative_cagr_floored_at_two_percent(self):
        fin_neg = sample_fin(opcost_cagr=-0.10)
        val = par_valuation(fin_neg, self.p, cap=30)
        self.assertAlmostEqual(val["g_org_exp"], 0.02, places=4)

    def test_scale_tier_and_currency_normalization(self):
        fin_eur = sample_fin(sales_ttm_m=50000.0, fin_currency="EUR", opcost_cagr=0.15)
        val_eur = par_valuation(fin_eur, self.p, cap=20)
        self.assertEqual(val_eur["scale_tier"], "MEGA")
        self.assertAlmostEqual(val_eur["g_org_exp"], 0.0980, places=4)

        fin_cad = sample_fin(sales_ttm_m=15000.0, fin_currency="CAD", opcost_cagr=0.15)
        val_cad = par_valuation(fin_cad, self.p, cap=20)
        self.assertEqual(val_cad["scale_tier"], "MID/SM")
        self.assertAlmostEqual(val_cad["g_org_exp"], 0.1200, places=4)

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
        fin = sample_fin(opcost_cagr=0.09)
        val = par_valuation(fin, self.p, cap=20)
        self.assertAlmostEqual(val["g_gap"], round(val["g_org_exp"] - val["g_market"], 4), places=4)

    def test_pure_explicit_dcf_independent_of_5y_historical_multiples(self):
        # Fair P/E (par_mult) is 100% pure Explicit DCF and does not change when 5Y low/high multiples vary
        fin1 = sample_fin(mult_low_5y=12.0, mult_high_5y=15.0, g_est=0.09, roic_operating=0.35)
        fin2 = sample_fin(mult_low_5y=35.0, mult_high_5y=60.0, g_est=0.09, roic_operating=0.35)
        val1 = par_valuation(fin1, self.p, cap=20)
        val2 = par_valuation(fin2, self.p, cap=20)
        self.assertAlmostEqual(val1["par_mult"], val1["pe_vd"], places=4)
        self.assertAlmostEqual(val1["par_mult"], val2["par_mult"], places=4)

    def test_explicit_dcf_differentiates_across_cap_tiers_and_penalizes_low_roic(self):
        fin = sample_fin(opcost_cagr=0.09, roic_operating=0.35)
        v30 = par_valuation(fin, self.p, cap=30)
        v20 = par_valuation(fin, self.p, cap=20)
        v15 = par_valuation(fin, self.p, cap=15)
        self.assertGreater(v30["pe_vd"], v20["pe_vd"])
        self.assertGreater(v20["pe_vd"], v15["pe_vd"])

        fin_low_roic = sample_fin(g_est=0.09, roic_operating=0.12)
        fin_high_roic = sample_fin(g_est=0.09, roic_operating=0.40)
        val_low = par_valuation(fin_low_roic, self.p, cap=20)
        val_high = par_valuation(fin_high_roic, self.p, cap=20)
        self.assertGreater(val_high["par_mult"], val_low["par_mult"] + 4.0)

    def test_dcf_g_market_inversion_round_trip(self):
        fin = sample_fin(opcost_cagr=0.085, roic_operating=0.22)
        val0 = par_valuation(fin, self.p, cap=15)
        fin_at_par = sample_fin(
            price=val0["par_val"], peak_oe_eps=5.0,
            opcost_cagr=0.085, roic_operating=0.22,
        )
        val_at_par = par_valuation(fin_at_par, self.p, cap=15)
        self.assertAlmostEqual(val_at_par["g_market"], val0["g_org_exp"], places=4)
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
        self.assertAlmostEqual(val_mtm["pe_mck"], 0.0, places=4)
        self.assertAlmostEqual(val_mtm["par_mult"], expected_nav_pe, places=4)

        # Operating HoldCo consolidating cash-generating subsidiaries (fcf_conv >= 0.25) uses standard Explicit DCF
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
        self.assertAlmostEqual(val_conc["pe_mck"], 0.0, places=4)
        self.assertLess(val_conc["pe_vd"], val_std["pe_vd"] - 5.0)
        self.assertAlmostEqual(val_conc["par_mult"], val_conc["pe_vd"], places=4)

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

    def test_buyback_neutrality_in_pe_vd_and_fcf_cap_in_5y_irr(self):
        """Positive buybacks increase per-share g_exp without inflating firm-level PE_VD, and obey FCF payout conservation in 5Y IRR."""
        fin_no_bb = sample_fin(
            price=100.0, market_cap_m=10000.0, dividends_ttm_m=150.0,
            sales_ttm_m=12000.0, sales_1y=0.08, sales_cagr=0.08, opcost_cagr=0.08, cap_growth=0.08,
            cagr_oe_eps=0.08, buyback_yield=0.0, roic_operating=0.30,
        )
        fin_with_bb = sample_fin(
            price=100.0, market_cap_m=10000.0, dividends_ttm_m=150.0,
            sales_ttm_m=12000.0, sales_1y=0.08, sales_cagr=0.08, opcost_cagr=0.08, cap_growth=0.08,
            cagr_oe_eps=0.105, buyback_yield=0.025, roic_operating=0.30,
        )
        v_no = par_valuation(fin_no_bb, self.p, cap=20)
        v_bb = par_valuation(fin_with_bb, self.p, cap=20)
        # Per-share growth rises with buybacks, while organic firm growth and PE_VD stay neutral!
        self.assertGreater(v_bb["g_exp"], v_no["g_exp"] + 0.02)
        self.assertAlmostEqual(v_bb["g_org_exp"], v_no["g_org_exp"], places=4)
        self.assertAlmostEqual(v_bb["pe_vd"], v_no["pe_vd"], places=4)
        self.assertAlmostEqual(v_bb["par_val"], v_no["par_val"], places=4)

        # At expensive current multiple (e.g. 50x P/E), FCF yield cannot fund 1.5% div + full buybacks:
        fin_expensive = dict(fin_with_bb, price=250.0, market_cap_m=25000.0, dividends_ttm_m=375.0)
        v_exp = par_valuation(fin_expensive, self.p, cap=20)
        # Fair Value is 100% independent of current share price!
        self.assertAlmostEqual(v_exp["par_val"], v_bb["par_val"], places=4)
        # g_irr is capped below v_bb["g_irr"] due to FCF conservation at 50x P/E
        self.assertLess(v_exp["g_irr"], v_bb["g_irr"])

    def test_market_implied_cap_zero_moat_floor_and_at_par_identity(self):
        """Market-Implied CAP equals 0.0y at <= 1/k = 11.76x and equals Fundamental CAP at Fair Value."""
        fin = sample_fin(mult_low_5y=18.0, mult_high_5y=28.0, g_est=0.085, roic_operating=0.28)
        v0 = par_valuation(fin, self.p, cap=20)

        # At Fair Value -> Market-Implied CAP == 20.0y
        v_par = par_valuation(dict(fin, price=v0["par_val"]), self.p, cap=20)
        self.assertAlmostEqual(v_par["cap_implied"], 20.0, places=1)
        self.assertAlmostEqual(v_par["cap_gap"], 0.0, places=1)

        # At 10.0x P/E (< 1/k = 11.76x) -> Market-Implied CAP == 0.0y
        v_cheap = par_valuation(dict(fin, price=10.0 * v0["peak_eps"]), self.p, cap=20)
        self.assertAlmostEqual(v_cheap["cap_implied"], 0.0, places=1)
        self.assertAlmostEqual(v_cheap["cap_gap"], 20.0, places=1)

    def test_g_market_round_trip_with_buybacks_and_mtm_holdco(self):
        """g_market == g_org_exp (g_gap == 0.0) holds at Price == Fair Value even with non-zero buybacks and on MTM HoldCos."""
        fin_bb = sample_fin(
            sales_ttm_m=15000.0, sales_1y=0.10, sales_cagr=0.10, opcost_cagr=0.095, cap_growth=0.09,
            cagr_oe_eps=0.12, buyback_yield=0.02, roic_operating=0.32,
            mult_low_5y=18.0, mult_high_5y=30.0,
        )
        v0 = par_valuation(fin_bb, self.p, cap=20)
        v_at_par = par_valuation(dict(fin_bb, price=v0["par_val"]), self.p, cap=20)
        self.assertAlmostEqual(v_at_par["g_market"], v0["g_org_exp"], places=4)
        self.assertAlmostEqual(v_at_par["g_gap"], 0.0, places=4)

        # MTM HoldCo round-trip & realistic sensitivity
        fin_mtm = sample_fin(
            roic_median=0.18, roic_operating=0.18,
            mult_low_5y=4.5, mult_high_5y=7.5,
            fcf_conv=None, peak_eps_est=None, cagr_oe_eps=0.08,
        )
        vm0 = par_valuation(fin_mtm, self.p, cap=20, sub_industry="Multi-Sector Holdings (mapped)")
        vm_par = par_valuation(dict(fin_mtm, price=vm0["par_val"]), self.p, cap=20, sub_industry="Multi-Sector Holdings (mapped)")
        self.assertAlmostEqual(vm_par["g_market"], vm0["g_org_exp"], places=4)
        self.assertAlmostEqual(vm_par["g_gap"], 0.0, places=4)

    def test_insurer_missing_ocf_not_misclassified_as_mtm_holdco(self):
        """Standard operating insurers missing OCF tags (fcf_conv=None) use normal PE_VD, not 1/ROIC_exp."""
        fin_ins = sample_fin(
            roic_median=0.145, roic_operating=0.145,
            mult_low_5y=10.5, mult_high_5y=14.8,
            fcf_conv=None, peak_eps_est=None, cagr_oe_eps=0.075,
        )
        val_ins = par_valuation(fin_ins, self.p, cap=20, sub_industry="Multi-line Insurance (mapped)")
        self.assertGreater(val_ins["pe_vd"], 1.0 / val_ins["roic_exp"] + 3.0)

    def test_cur_eps_guards_multi_class_share_basis_and_unstripped_spike(self):
        """Multi-class 'check share basis' notes and >1.5x latest-year spikes do not corrupt Active Peak EPS."""
        # Multi-class share basis mismatch (e.g. dual-class firm market_cap_m vs single-class peak_oe_eps)
        fin_mc = sample_fin(
            price=200.0, market_cap_m=45000.0, ni_ttm_m=900.0, peak_oe_eps=10.0,
            fin_note="[auto] short history (4y); check share basis (mktcap/price = 1.9x shares)",
        )
        val_mc = par_valuation(fin_mc, self.p, cap=20)
        self.assertAlmostEqual(val_mc["peak_eps"], 10.0, places=4)

        # Latest-year non-cash disposal spike left out of peak_oe_eps should not prevent mid-cycle check or inflate cur_eps
        fin_spike = sample_fin(
            price=100.0, market_cap_m=10000.0, ni_ttm_m=2200.0, peak_oe_eps=8.0,
            fin_note="[auto] non-cash earnings spike left out of peak: 2025",
        )
        val_sp = par_valuation(fin_spike, self.p, cap=20)
        self.assertAlmostEqual(val_sp["peak_eps"], 8.0, places=4)


if __name__ == "__main__":
    unittest.main()
