"""Regression tests for the v7.2 remediation of audit items 1–5 (M&A growth, peak blend, status labels, share counts,
reporting-currency switches)."""
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
from screener.fetch import metrics, par, settings
from screener.fetch.sources import EODHD


def fin(**kw) -> dict:
    base = {"id": "TEST", "price": 100.0, "market_cap_m": 10000.0, "peak_oe_eps": 5.0, "cur_oe_eps": 5.0,
            "mult_low_5y": 15.0, "mult_high_5y": 25.0, "roic_median": 0.20, "roic_operating": 0.25,
            "sales_cagr": 0.08, "opcost_cagr": 0.08}
    base.update(kw)
    return base


def offline_eod(spot: dict) -> EODHD:
    settings.OFFLINE = True
    eod = EODHD(api_key="offline")
    for (a, b), r in spot.items():
        eod._fx[(a, b)] = r
        eod._fx_hist[(a, b)] = []
        eod._fx_hist[(b, a)] = []
    return eod


def fund_from(rows: dict, general_ccy: str = "GBP", highlights: dict | None = None, shares_now: float | None = None,
              bs_ccy: dict | None = None) -> dict:
    """rows: {period_end: (revenue, currency, shares)} -> minimal EODHD fundamentals JSON."""
    inc, bs, cf = {}, {}, {}
    for d, (rev, ccy, sh) in rows.items():
        inc[d] = {"totalRevenue": rev, "netIncome": rev / 10, "currency_symbol": ccy}
        bs[d] = {"totalAssets": rev * 2, "totalStockholderEquity": rev, "commonStockSharesOutstanding": sh,
                 "currency_symbol": (bs_ccy or {}).get(d, ccy)}
        cf[d] = {"totalCashFromOperatingActivities": rev / 8, "currency_symbol": (bs_ccy or {}).get(d, ccy)}
    return {"General": {"CurrencyCode": general_ccy}, "Highlights": highlights or {},
            "SharesStats": {"SharesOutstanding": shares_now} if shares_now else {},
            "Financials": {"Income_Statement": {"yearly": inc}, "Balance_Sheet": {"yearly": bs},
                           "Cash_Flow": {"yearly": cf}}}


class MaReinvestTests(unittest.TestCase):
    """Item 1: cash-funded M&A over the g0 window counts; stock-funded years are netted out by S_t."""

    def _base(self, yrs):
        return {"debt": {y: 0.0 for y in yrs}, "ni": {y: 100.0 for y in yrs}, "ebit": {y: 100.0 for y in yrs},
                "tax": {y: 0.0 for y in yrs}, "pretax": {y: 100.0 for y in yrs}, "sales": {y: 1000.0 for y in yrs},
                "equity": {y: 1000.0 for y in yrs}}

    def test_cash_one_off_counts_over_window(self):
        yrs = range(2015, 2026)
        s = {**self._base(yrs), "goodwill": {y: (100.0 if y < 2020 else 400.0) for y in yrs}}
        self.assertAlmostEqual(metrics.summarize(s)["ma_reinvest"], 300.0 / 1000.0, places=4)

    def test_deal_outside_window_ignored(self):
        yrs = range(2010, 2026)
        s = {**self._base(yrs), "goodwill": {y: (100.0 if y < 2012 else 400.0) for y in yrs}}
        self.assertAlmostEqual(metrics.summarize(s)["ma_reinvest"], 0.0, places=4)

    def test_stock_funded_year_skipped(self):
        yrs = range(2015, 2026)
        sh = {y: (100.0 if y < 2020 else 120.0) for y in yrs}
        s = {**self._base(yrs), "goodwill": {y: (100.0 if y < 2020 else 400.0) for y in yrs}, "shares": sh}
        self.assertAlmostEqual(metrics.summarize(s)["ma_reinvest"], 0.0, places=4)


class PeakBlendTests(unittest.TestCase):
    """Item 2: peak weight decays with age; pre-listing years are left out of the Owner EPS series."""

    def setUp(self):
        self.p = G.params({})

    def test_peak_weight_schedule(self):
        self.assertEqual(G.peak_weight(2025, 2025), 0.5)
        self.assertEqual(G.peak_weight(2025, 2024), 0.5)
        self.assertAlmostEqual(G.peak_weight(2025, 2023), 1.0 / 3.0)
        self.assertAlmostEqual(G.peak_weight(2025, 2022), 1.0 / 6.0)
        self.assertEqual(G.peak_weight(2025, 2021), 0.0)
        self.assertEqual(G.peak_weight(None, 2021), 0.5)          # field missing: v7.1 behaviour

    def test_active_eps_uses_decayed_weight(self):
        v = G.par_valuation(fin(peak_oe_eps=8.0, cur_oe_eps=4.0, peak_oe_year=2021, cur_oe_year=2025), self.p,
                            cap=20, moat="Brand", sub_industry="Software")
        self.assertAlmostEqual(v["peak_eps"], 4.0)
        self.assertEqual(v["peak_weight"], 0.0)
        v = G.par_valuation(fin(peak_oe_eps=8.0, cur_oe_eps=4.0, peak_oe_year=2024, cur_oe_year=2025), self.p,
                            cap=20, moat="Brand", sub_industry="Software")
        self.assertAlmostEqual(v["peak_eps"], 6.0)

    def test_pre_listing_years_left_out(self):
        yrs = range(2019, 2026)
        s = {"ni": {y: (300.0 if y == 2021 else 100.0) for y in yrs}, "shares": {y: 100.0 for y in yrs},
             "ocf": {y: 400.0 for y in yrs}, "period_end": {y: f"{y}-12-31" for y in yrs}}
        self.assertEqual(par.compute(s, None, 1.0)["peak_oe_year"], 2021)
        out = par.compute(s, None, 1.0, listing_date="2024-04-26")
        self.assertEqual(out["peak_oe_year"], 2024)
        self.assertEqual(out["cur_oe_year"], 2025)
        self.assertTrue(any("pre-listing FY2019–FY2023" in n for n in out["_notes"]))
        # a first bar at the start of the price history says nothing about the listing date
        self.assertEqual(par.compute(s, None, 1.0, listing_date="2014-01-02")["peak_oe_year"], 2021)


class StatusTests(unittest.TestCase):
    """Item 3 + no-data plumbing: no Below/Above PAR label; blocking [auto] notes give No data."""

    def setUp(self):
        self.p = G.params({})

    def test_status_is_valued_on_both_sides_of_fair_value(self):
        for price in (50.0, 500.0):
            v = G.par_valuation(fin(price=price), self.p, cap=20, moat="Brand", sub_industry="Software")
            self.assertEqual(v["status"], C.V_VALUED)
            self.assertIsNotNone(v["vs_par"])
        self.assertFalse(hasattr(C, "V_BELOW_PAR"))

    def test_blocking_notes_give_no_data(self):
        for tok in G.BLOCKING_AUTO_NOTES:
            v = G.par_valuation(fin(fin_note=f"analyst | [auto] {tok} (detail)"), self.p, cap=20, moat="Brand",
                                sub_industry="Software")
            self.assertEqual(v["status"], C.V_NODATA, tok)

    def test_js_sandbox_mirrors_blocking_notes(self):
        html = build_dashboard_html({"version": "7.2", "generated_at": "x", "universes": {}, "companies": [],
                                     "changelog": [], "summary": {"total_companies": 0, "quality_pass": 0,
                                                                  "calamity_pass": 0, "valued": 0, "median_excess_irr": None}})
        js = "const BLOCKING_AUTO_NOTES = [" + ", ".join(f"'{t}'" for t in G.BLOCKING_AUTO_NOTES) + "];"
        self.assertIn(js, html)
        self.assertNotIn("Below PAR", html)


class ShareBasisTests(unittest.TestCase):
    """Item 4: post-FY splits of any ratio; merger / glitch share counts are flagged, multi-class is not."""

    def _rows(self, sh_last):
        return {f"{y}-03-31": (1000.0 + 50 * (y - 2021), "GBP", 168.0 if y == 2026 else sh_last) for y in range(2021, 2027)}

    def test_post_fy_consolidation_rescales_statement_shares(self):
        eod = offline_eod({})
        fund = fund_from(self._rows(168.0), shares_now=124.0)
        s = eod.annual_series(fund, splits={"2026-08-17": 0.75}, last_bar_date="2026-11-13")
        self.assertAlmostEqual(s["shares"][2025], 168.0 * 0.75)
        # a split dated after the last price bar is not applied yet
        s = eod.annual_series(fund, splits={"2026-12-01": 0.75}, last_bar_date="2026-11-13")
        self.assertAlmostEqual(s["shares"][2025], 168.0)

    def _quote(self, stats, mcap, stmt):
        eod = offline_eod({})
        fund = {"General": {"CurrencyCode": "USD"}, "Highlights": {"MarketCapitalization": mcap},
                "SharesStats": {"SharesOutstanding": stats}}
        return eod.quote("TEST.US", fund_data=fund, eod_bars=[{"date": "2026-11-13", "close": 100.0}],
                         series={"shares": {2025: stmt}})

    def test_merger_after_fy_is_flagged(self):
        q = self._quote(stats=614e6, mcap=614e6 * 100.0, stmt=333e6)          # KMB-like
        self.assertAlmostEqual(q["share_basis_flag"], 1.84)
        self.assertEqual(q["shares"], 614e6)

    def test_multi_class_is_not_flagged(self):
        q = self._quote(stats=500e6, mcap=1000e6 * 100.0, stmt=1000e6)        # single class in SharesStats
        self.assertIsNone(q["share_basis_flag"])
        self.assertAlmostEqual(q["shares"], 1000e6)


class CurrencySwitchTests(unittest.TestCase):
    """Item 5: close-pair blocks decided as one unit; far pairs per year; ambiguous switches flagged."""

    def test_close_pair_block_converted_across_trough(self):
        eod = offline_eod({("GBP", "USD"): 1.32})
        # GBP block with a COVID trough right before the switch (CPG-like); FY = calendar year - 1 for Jun year ends
        revs = {2017: 22.5, 2018: 23.0, 2019: 24.9, 2020: 19.9, 2021: 17.9, 2022: 25.5, 2023: 31.0}
        rows = {f"{y}-09-30": (v, "GBP", 1.0) for y, v in revs.items()}
        rows.update({"2024-09-30": (42.0, "USD", 1.0), "2025-09-30": (46.0, "USD", 1.0)})
        s = eod.annual_series(fund_from(rows, "USD"))
        for y in revs:
            self.assertAlmostEqual(s["sales"][y], revs[y] * 1.32, places=6)
        self.assertFalse(any("unresolved" in n for n in s["_notes"]))
        self.assertTrue(any("spot rate" in n for n in s["_notes"]))

    def test_far_pair_keeps_per_year_value_test(self):
        eod = offline_eod({("DKK", "EUR"): 0.134})
        # FY2022 already restated to EUR but labelled DKK (NSIS-like): only the older DKK years are converted
        rows = {"2020-12-31": (2000.0, "DKK", 1.0), "2021-12-31": (2100.0, "DKK", 1.0),
                "2022-12-31": (300.0, "DKK", 1.0), "2023-12-31": (310.0, "EUR", 1.0), "2024-12-31": (320.0, "EUR", 1.0)}
        s = eod.annual_series(fund_from(rows, "DKK"))
        self.assertAlmostEqual(s["sales"][2022], 300.0)
        self.assertAlmostEqual(s["sales"][2021], 2100.0 * 0.134, places=6)

    def test_ambiguous_switch_flagged_and_override_clears(self):
        eod = offline_eod({("CHF", "USD"): 1.13})
        # values already in USD but labelled CHF (SREN-like): converting or not is equally plausible
        revs = {2019: 44.0, 2020: 45.0, 2021: 46.0, 2022: 47.4, 2023: 48.0}
        rows = {f"{y}-12-31": (v, "CHF", 1.0) for y, v in revs.items()}
        rows.update({"2024-12-31": (50.2, "USD", 1.0)})
        s = eod.annual_series(fund_from(rows, "CHF"))
        self.assertTrue(any("currency switch unresolved" in n for n in s["_notes"]))
        s = eod.annual_series(fund_from(rows, "CHF"), ccy_override="keep")
        self.assertFalse(any("unresolved" in n for n in s["_notes"]))
        self.assertAlmostEqual(s["sales"][2023], 48.0)

    def test_latest_year_checked_against_ttm(self):
        eod = offline_eod({("GBP", "USD"): 1.30})
        revs = {2020: 2.79, 2021: 2.95, 2022: 3.71, 2023: 5.38, 2024: 5.44}
        rows = {f"{y}-12-31": (v, "GBP", 1.0) for y, v in revs.items()}
        rows.update({"2025-12-31": (5.13, "USD", 1.0)})                    # RTO-like: GBP value labelled USD
        s = eod.annual_series(fund_from(rows, "GBX", highlights={"RevenueTTM": 7.13}))
        self.assertTrue(any("vs TTM" in n for n in s["_notes"]))

    def test_fx_on_falls_back_to_spot_offline(self):
        eod = offline_eod({("GBP", "USD"): 1.25})
        self.assertEqual(eod.fx_on("GBP", "USD", "2019-09-30"), (1.25, False))
        eod._fx_hist[("GBP", "USD")] = [["2019-01-02", 1.27], ["2019-09-30", 1.23], ["2019-10-01", 1.22]]
        self.assertEqual(eod.fx_on("GBP", "USD", "2019-09-30"), (1.23, True))
        eod._fx_hist[("USD", "GBP")] = [["2019-01-02", 0.8]]
        self.assertAlmostEqual(eod.fx_on("USD", "GBP", "2019-09-30")[0], 0.8)


if __name__ == "__main__":
    unittest.main()
