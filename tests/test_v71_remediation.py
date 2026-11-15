"""Regression tests for the v7.1 quantitative-model forensic-audit remediation."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import config as C
from screener import gates as G
from screener.apply_evaluation import validate_and_waterfall
from screener.fetch import metrics, par, settings
from screener.fetch.sources import EODHD, _same_company, safe_name, stale_fundamentals, symbol_cache


def fin(**kw) -> dict:
    base = {"id": "TEST", "price": 100.0, "market_cap_m": 10000.0, "peak_oe_eps": 5.0, "cur_oe_eps": 5.0,
            "mult_low_5y": 15.0, "mult_high_5y": 25.0, "roic_median": 0.20, "roic_operating": 0.25,
            "sales_cagr": 0.08, "opcost_cagr": 0.08}
    base.update(kw)
    return base


class ValuationCoreTests(unittest.TestCase):
    def setUp(self):
        self.p = G.params({})

    def test_negative_fair_value_is_no_value_not_below_par(self):
        v = G.par_valuation(fin(roic_operating=0.04, roic_median=0.04, sales_cagr=0.18, opcost_cagr=0.18), self.p,
                            cap=20, moat="Brand", sub_industry="Software")
        self.assertLess(v["par_mult"], 0)
        self.assertEqual(v["status"], C.V_NOVALUE)
        for k in ("vs_par", "irr_5y", "cap_implied", "cap_gap", "g_gap", "g_market"):
            self.assertIsNone(v[k], k)

    def test_ma_reinvest_drives_ronic_blend_not_capital_growth(self):
        heavy = fin(roic_operating=0.30, roic_median=0.08, cap_growth=0.10)
        v_org = G.par_valuation(heavy, self.p, cap=20, moat="Brand", sub_industry="Software")
        self.assertAlmostEqual(v_org["roic_exp"], 0.30, places=4)        # no acquisitions: tangible ROIC
        # spends 50% of NOPAT on acquisitions at 8% GAAP ROIC -> bought growth 4% of g0 = 8% -> w = 0.5
        v_ma = G.par_valuation({**heavy, "ma_reinvest": 0.5}, self.p, cap=20, moat="Brand", sub_industry="Software")
        self.assertAlmostEqual(v_ma["ma_alpha"], 0.5)
        self.assertAlmostEqual(v_ma["roic_exp"], round(1 / (0.5 / 0.30 + 0.5 / 0.08), 4), places=4)

    def test_g_gap_blank_when_market_growth_saturated(self):
        v = G.par_valuation(fin(price=900.0, roic_operating=0.0900, roic_median=0.09), self.p, cap=20, moat="Brand",
                            sub_industry="Software")
        self.assertEqual(v["g_market_flag"], G.G_FLAG_SAT_HI)
        self.assertIsNone(v["g_gap"])

    def test_ronic_at_or_below_r_flagged(self):
        v = G.par_valuation(fin(roic_operating=0.07, roic_median=0.07), self.p, cap=20, moat="Brand", sub_industry="Software")
        self.assertTrue(v["ronic_le_r"])
        self.assertFalse(G.par_valuation(fin(), self.p, cap=20, moat="Brand", sub_industry="Software")["ronic_le_r"])

    def test_stale_fundamentals_note_gives_no_data(self):
        v = G.par_valuation(fin(fin_note="analyst text | [auto] stale fundamentals (revenue/balance sheet end FY2020)"),
                            self.p, cap=20, moat="Brand", sub_industry="Software")
        self.assertEqual(v["status"], C.V_NODATA)

    def test_no_data_path_carries_financial_classification(self):
        v = G.par_valuation(fin(peak_oe_eps=None, cur_oe_eps=None, price=None), self.p, sub_industry="Diversified Banks")
        self.assertEqual(v["status"], C.V_NODATA)
        self.assertTrue(v["bs_fin"])
        self.assertAlmostEqual(v["k"], 0.1025)

    def test_no_statement_growth_falls_back_to_base_rate(self):
        # v7.6: no g_implied override — capital growth alone is not growth evidence, g0 = g_base
        v = G.par_valuation(fin(sales_cagr=None, opcost_cagr=None, cap_growth=0.05, g_implied=0.10), self.p, cap=20)
        self.assertAlmostEqual(v["g_org_exp"], 0.03, places=4)

    def test_irr_below_minus_fifty_percent_is_solved(self):
        pe, _, _, _, f5, v5 = G.dcf_schedule_and_continuation(0.05, 0.20, 20)
        irr = G.solve_irr_5y(pe * 60.0, f5, v5)
        self.assertIsNotNone(irr)
        self.assertLess(irr, -0.5)

    def test_rounding_matches_js_math_round(self):
        self.assertEqual(G._r4(-0.00015), -0.0001)          # JS Math.round rounds half toward +inf
        self.assertEqual(G._r1(2.25), 2.3)


class PipelineTests(unittest.TestCase):
    def test_tangible_roic_has_no_addback(self):
        ebit, tax = {2024: 100.0}, {2024: 0.0}
        eq, debt, cash = {2023: 1000.0, 2024: 1000.0}, {}, {}
        gw, ig = {2023: 600.0, 2024: 600.0}, {}
        g0, t0 = metrics.roic_series(ebit, tax, eq, debt, cash, gw, ig)
        self.assertAlmostEqual(g0[2024], 100.0 / 1000.0)
        self.assertAlmostEqual(t0[2024], 100.0 / 400.0)            # v7.3: same NOPAT on tangible capital

    def test_invested_capital_includes_minorities_and_short_term_debt(self):
        eq_ic, debt_ic = metrics.ic_inputs({"equity": {2024: 100.0}, "nci": {2024: 50.0},
                                            "debt": {2024: 30.0}, "st_debt": {2024: 20.0}})
        self.assertEqual(eq_ic[2024], 150.0)
        self.assertEqual(debt_ic[2024], 50.0)

    def test_ma_reinvest_from_goodwill_growth(self):
        yrs = range(2019, 2025)
        base = {"debt": {y: 0.0 for y in yrs}, "ni": {y: 100.0 for y in yrs}, "ebit": {y: 100.0 for y in yrs},
                "tax": {y: 0.0 for y in yrs}, "pretax": {y: 100.0 for y in yrs}, "sales": {y: 1000.0 for y in yrs},
                "equity": {y: 1000.0 for y in yrs}}
        serial = {**base, "goodwill": {y: 200.0 + 30.0 * (y - 2019) for y in yrs}}
        # v7.2: Σ spend ÷ Σ NOPAT over the g0 window (FX allowance 0.035 × (320 − 300) in FY2024)
        self.assertAlmostEqual(metrics.summarize(serial)["ma_reinvest"], (150.0 - 0.7) / 500.0, places=4)
        one_off = {**base, "goodwill": {2019: 200.0, 2020: 2200.0, 2021: 2150.0, 2022: 2100.0, 2023: 2050.0, 2024: 2000.0}}
        # a cash-funded transformational deal now counts: 2000 spent over 5 years of 100 NOPAT (capped at 3.0)
        self.assertAlmostEqual(metrics.summarize(one_off)["ma_reinvest"], 3.0, places=4)
        stock = {**one_off, "shares": {2019: 100.0, 2020: 140.0, 2021: 140.0, 2022: 140.0, 2023: 140.0, 2024: 140.0}}
        self.assertAlmostEqual(metrics.summarize(stock)["ma_reinvest"], 0.0, places=4)    # stock deal: netted by S_t

    def test_impairment_guard_keeps_genuine_step_ups(self):
        da = {2020: 100.0, 2021: 100.0, 2022: 100.0, 2023: 300.0, 2024: 100.0}
        self.assertAlmostEqual(metrics.clean_da(da)[2023], 150.0)                           # transient: capped
        merger = {**da, 2024: 290.0}
        self.assertEqual(metrics.clean_da(merger)[2023], 300.0)                             # persistent: kept
        capex = {2020: 100.0, 2021: 100.0, 2022: 100.0, 2023: 400.0}
        self.assertEqual(metrics.clean_da(da, capex)[2023], 300.0)                          # capex build-out: kept

    def test_latest_debt_falls_back_to_prior_year(self):
        s = {"ni": {2023: 10.0, 2024: 10.0}, "debt": {2023: 500.0}, "equity": {2023: 100.0, 2024: 100.0}}
        self.assertEqual(metrics.summarize(s)["lt_debt_m"], 500.0 / 1e6)

    def test_peak_to_peak_cagr_uses_actual_gap_and_point_in_time_availability(self):
        self.assertEqual(par._available(2024, {2024: "2025-06-30"}).isoformat(), "2025-09-30")
        self.assertEqual(par._available(2024).isoformat(), "2025-04-01")
        s = {"ni": {2015: 100.0, 2016: 50.0, 2017: 50.0, 2018: 50.0, 2019: 50.0, 2020: 50.0, 2021: 50.0,
                    2022: 50.0, 2023: 50.0, 2024: 200.0},
             "shares": {y: 100.0 for y in range(2015, 2025)}, "ocf": {y: 300.0 for y in range(2015, 2025)}}
        out = par.compute(s, None, 1.0)
        self.assertAlmostEqual(out["cagr_oe_eps"], round((2.0 / 1.0) ** (1 / 9) - 1, 4))

    def test_resolver_rejects_substring_names(self):
        self.assertFalse(_same_company("Nexi", "Nexity SA"))
        self.assertFalse(_same_company("Terna", "GEK TERNA Holdings Real Estate Construction S.A."))
        self.assertTrue(_same_company("Prysmian", "Prysmian S.p.A"))

    def test_cache_file_names_avoid_reserved_device_names(self):
        self.assertEqual(symbol_cache("CON.XETRA").name, "_CON.XETRA.json")      # Continental: OneDrive cannot sync CON.*
        self.assertEqual(symbol_cache("CON.XETRA", "eod").parent.name, "eod")
        self.assertEqual(safe_name("LPT1.F"), "_LPT1.F")
        self.assertEqual(safe_name("CONTI.F"), "CONTI.F")
        self.assertEqual(symbol_cache("MSFT.US").name, "MSFT.US.json")

    def test_stale_fundamentals_detection(self):
        s = {"sales": {2020: 1.0}, "equity": {2020: 1.0}, "ocf": {2024: 1.0}, "ni": {2024: 1.0}}
        self.assertIn("stale fundamentals", stale_fundamentals(s))
        fresh = {"sales": {2025: 1.0}, "equity": {2025: 1.0}, "ocf": {2025: 1.0}, "ni": {2025: 1.0}}
        self.assertIsNone(stale_fundamentals(fresh))

    def test_reporting_currency_switch_converted_by_value(self):
        settings.OFFLINE = True
        eod = EODHD(api_key="offline")
        eod._fx[("GBP", "USD")] = 1.30
        eod._fx_hist = {("GBP", "USD"): [], ("USD", "GBP"): []}     # spot rate only (deterministic after online runs)
        inc, bs, cf = {}, {}, {}
        for y, (rev, ccy) in {2019: (100.0, "GBP"), 2020: (104.0, "GBP"), 2021: (108.0, "GBP"),
                              2022: (146.0, "USD"), 2023: (152.0, "USD")}.items():
            d = f"{y}-06-30"
            inc[d] = {"totalRevenue": rev, "netIncome": rev / 10, "currency_symbol": ccy}
            bs[d] = {"totalAssets": rev * 2, "totalStockholderEquity": rev, "currency_symbol": ccy}
            cf[d] = {"totalCashFromOperatingActivities": rev / 8, "currency_symbol": ccy}
        fund = {"General": {"CurrencyCode": "GBP"}, "Financials": {"Income_Statement": {"yearly": inc},
                "Balance_Sheet": {"yearly": bs}, "Cash_Flow": {"yearly": cf}}}
        s = eod.annual_series(fund)
        self.assertAlmostEqual(s["sales"][2020], 108.0 * 1.30, places=6)      # FY2021 (GBP) converted to USD
        self.assertEqual(s["ccy"][2020], "USD")
        self.assertAlmostEqual(s["sales"][2021], 146.0, places=6)


class IngestionTests(unittest.TestCase):
    def test_sandbox_payload_does_not_touch_calamity(self):
        qual, fin_ov, _ = validate_and_waterfall({"qualitative": {"gate_4_runway_cap": 20},
                                                  "quantitative_overrides": {"g_est": 0.09}})
        self.assertNotIn("calamity", qual)
        self.assertNotIn("calamity_note", qual)


if __name__ == "__main__":
    unittest.main()
