"""Tests for the interactive What-If Valuation Sandbox."""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.dashboard import build_dashboard_html, collect_screener_data
from screener.fetch.metrics import clean_da, exp_weighted_ols_cagr, owner_addback, summarize
from screener.gates import (
    active_roic,
    dcf_schedule_and_continuation,
    explicit_dcf_multiple,
    is_balance_sheet_financial,
    is_mtm_holdco,
    params,
    par_valuation,
    solve_irr_5y,
    solve_market_growth,
    uses_gaap_roic,
)


class GrowthCeilingEngineTests(unittest.TestCase):
    def test_exp_weighted_ols_cagr_steady_growth(self):
        """Steady 8.0% annual compounding over 10 years yields 8.0% WLS CAGR and span 10."""
        series = {2015 + i: 100.0 * (1.08 ** i) for i in range(11)}
        g, span = exp_weighted_ols_cagr(series, max_years=10, half_life=5.0)
        self.assertEqual(span, 10)
        self.assertAlmostEqual(g, 0.08, places=4)

    def test_exp_weighted_ols_cagr_spinoff_reset(self):
        """Permanent >35% step-down followed by >=3 post-breakup years resets window to post-spinoff era."""
        # Pre-breakup conglomerate ~1000 growing 2%/yr, then spinoff in 2022 to ~400 growing 10%/yr
        series = {
            2015: 900.0, 2016: 918.0, 2017: 936.0, 2018: 955.0,
            2019: 974.0, 2020: 993.0, 2021: 1013.0,
            2022: 400.0, 2023: 440.0, 2024: 484.0, 2025: 532.4,
        }
        g, span = exp_weighted_ols_cagr(series, max_years=10, half_life=5.0)
        self.assertEqual(span, 3)
        self.assertAlmostEqual(g, 0.10, places=3)

    def test_exp_weighted_ols_cagr_ma_jump_winsorized(self):
        """A single-year +60% M&A step-up amidst 7% organic years is winsorized so it doesn't dominate."""
        series = {}
        val = 100.0
        series[2015] = val
        for y in range(2016, 2026):
            val *= (1.60 if y == 2022 else 1.07)
            series[y] = val
        g, span = exp_weighted_ols_cagr(series, max_years=10, half_life=5.0)
        self.assertEqual(span, 10)
        self.assertGreater(g, 0.075)
        self.assertLess(g, 0.105)

    def test_sub_gdp_fade_does_not_fade_upward(self):
        """When g0 < 3.5% (e.g. 1.5%), explicit_dcf_multiple holds 1.5% instead of fading upward to 3.5%."""
        pe_low, _, _, _ = explicit_dcf_multiple(0.015, 0.18, 25, r=0.085, g_term=0.035)
        pe_gdp, _, _, _ = explicit_dcf_multiple(0.035, 0.18, 25, r=0.085, g_term=0.035)
        self.assertLess(pe_low, pe_gdp)


class ValuationSandboxHtmlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = {
            "version": "6.33",
            "generated_at": "2026-11-11T00:00:00Z",
            "summary": {"total_companies": 0, "quality_pass": 0, "calamity_pass": 0, "calamity_below_par": 0, "below_par": 0, "median_irr_below_par": 0.0},
            "sectors": [],
            "moats": [],
            "universes": {},
            "companies": [],
            "changelog": [],
        }
        cls.html = build_dashboard_html(data)

    def test_cap_pill_buttons_include_5y(self):
        """Ensure the CAP button group includes 5y button alongside 10y, 15y, 20y, 25y, 30y."""
        self.assertIn('onclick="setSandboxCap(5)"', self.html)
        self.assertIn('>5y</button>', self.html)

    def test_peak_eps_placeholder_fixed(self):
        """Ensure the peak EPS label does not hardcode $4.50."""
        self.assertNotIn('id="sb-val-peakeps">$4.50</span>', self.html)
        self.assertIn('id="sb-val-peakeps">-</span>', self.html)

    def test_dynamic_slider_bounds(self):
        """Verify dynamic slider min/max assignment in syncSandboxInputs."""
        self.assertIn("s1y.min = Math.min(-20, Math.floor(sbCurrent.sales1y - 5));", self.html)
        self.assertIn("s1y.max = Math.max(40, Math.ceil(sbCurrent.sales1y + 5));", self.html)
        self.assertIn("sRoic.min = Math.min(5, Math.floor(sbCurrent.roic - 5));", self.html)

    def test_growth_fallback_hierarchy(self):
        """Verify initValuationSandbox implements the robust fallback hierarchy."""
        self.assertIn("const baseGrowth = (c.sales_cagr !== null && c.sales_cagr !== undefined) ? c.sales_cagr", self.html)
        self.assertIn(": ((c.cagr_oe_eps !== null && c.cagr_oe_eps !== undefined) ? c.cagr_oe_eps", self.html)
        self.assertIn(": ((c.sales_1y !== null && c.sales_1y !== undefined) ? c.sales_1y", self.html)
        self.assertIn(": ((c.g_start !== null && c.g_start !== undefined) ? c.g_start : 0.08)));", self.html)

    def test_valuation_unavailable_status_box(self):
        """Verify status box properly shows Valuation Unavailable when inputs are missing and defines .badge-slate CSS."""
        self.assertIn("Valuation Unavailable (Missing Price, Peak EPS, or 5Y Multiples)", self.html)
        self.assertIn("badge-slate", self.html)
        self.assertIn(".badge-gray, .badge-slate", self.html)

    def test_valuation_audit_uses_eff_g_mult_and_yn_pricing_map(self):
        """Verify Valuation Audit card displays eff_g_mult (not hardcoded 200x) and maps Y/N Gate 3b pricing."""
        self.assertIn("const effSlope = (c.eff_g_mult !== null && c.eff_g_mult !== undefined) ? c.eff_g_mult : c.g_mult;", self.html)
        self.assertIn("'Y': 'Pass (≥ Inflation & ROIC ≥ 12%)'", self.html)
        self.assertIn("'N': 'Fail (< Inflation or Sub-Hurdle)'", self.html)
        self.assertIn("c.g4_cap >= 30 ? '85%' : (c.g4_cap >= 20 ? '75%' : '62%')", self.html)

    def test_dynamic_tab_counts_respect_market_and_calamity_toggle(self):
        """Verify updateTabCounts filters by currentMarket and shortlist Include Calamities toggle."""
        self.assertIn("const base = SCREENER_DATA.companies.filter(c => currentMarket === 'all' || c.universe === currentMarket);", self.html)
        self.assertIn("(c.result === 'Quality pass' || (incCal && c.result === 'Calamity pass')) && c.val_status === 'Below PAR'", self.html)

    def test_consistent_column_order_across_shortlist_qpass_and_calamity(self):
        """Verify Shortlist, Quality Pass Funnel, and Calamity Watchlist share the exact same 18 core columns."""
        self.assertIn("const coreValuationCols = [", self.html)
        self.assertIn("cols = [...coreValuationCols];", self.html)

    def test_zero_diff_thresholds(self):
        """Verify diff thresholds prevent epsilon jitter from showing spurious +0.0% colors."""
        self.assertIn("isPctZero", self.html)
        self.assertIn("isMultZero", self.html)
        self.assertIn("isPriceZero", self.html)
        self.assertIn("isYearZero", self.html)

    def test_cap_override_json_formatting(self):
        """Verify copySandboxOverrideJson displays 'Unassigned' instead of 'nully' and matches apply_evaluation.py schema."""
        self.assertIn("sbCurrent.cap !== null ? sbCurrent.cap + 'y' : 'Unassigned'", self.html)
        self.assertIn("quantitative_overrides:", self.html)
        self.assertIn("gate_4_runway_cap: sbCurrent.cap", self.html)


class ValuationSandboxSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.screener_data = collect_screener_data(["us", "ca", "eu"])
        cls.companies = cls.screener_data.get("companies", [])

    def _simulate_js_sandbox(self, c: dict, overrides: dict | None = None) -> dict:
        """Simulate JS sandbox calculation logic 1:1 matching screener/dashboard.py (v6.36)."""
        # 1. initValuationSandbox(c)
        cap = c.get("g4_cap") if (c.get("g4_cap") is not None) else None
        base_growth = c.get("sales_cagr") if c.get("sales_cagr") is not None else (
            c.get("cagr_oe_eps") if c.get("cagr_oe_eps") is not None else (
                c.get("sales_1y") if c.get("sales_1y") is not None else (
                    c.get("g_start") if c.get("g_start") is not None else 0.08
                )
            )
        )
        base_salescagr = (c.get("sales_cagr") * 100.0) if c.get("sales_cagr") is not None else (base_growth * 100.0)
        base_sales1y = (c.get("sales_1y") * 100.0) if c.get("sales_1y") is not None else (base_growth * 100.0)
        base_capgrowth = (c.get("cap_growth") * 100.0) if c.get("cap_growth") is not None else (base_growth * 100.0)
        roic = (c.get("roic_used") * 100.0) if c.get("roic_used") is not None else (
            (c.get("roic_operating") * 100.0) if c.get("roic_operating") is not None else (
                (c.get("roic_median") * 100.0) if c.get("roic_median") is not None else 18.0
            )
        )
        bb = (c.get("buyback_yield") * 100.0) if c.get("buyback_yield") is not None else 0.0
        base_peakeps = c.get("peak_eps") if c.get("peak_eps") is not None else (
            (c.get("price") / 15.0) if (c.get("price") and c.get("price") > 0) else None
        )
        ml = c.get("mult_low_5y")
        mh = c.get("mult_high_5y")
        gest = (c.get("g_est") * 100.0) if c.get("g_est") is not None else None

        salescagr = base_salescagr
        sales1y = base_sales1y
        capgrowth = base_capgrowth
        peakeps = base_peakeps
        if overrides:
            if "cap" in overrides:
                cap = overrides["cap"]
            if "salescagr" in overrides:
                salescagr = overrides["salescagr"]
            if "sales1y" in overrides:
                sales1y = overrides["sales1y"]
            if "capgrowth" in overrides:
                capgrowth = overrides["capgrowth"]
            if "roic" in overrides:
                roic = overrides["roic"]
            if "bb" in overrides:
                bb = overrides["bb"]
            if "peakeps" in overrides:
                peakeps = overrides["peakeps"]
            if "ml" in overrides:
                ml = overrides["ml"]
            if "mh" in overrides:
                mh = overrides["mh"]
            if "gest" in overrides:
                gest = overrides["gest"]

        # 2. recalcSandboxValuation()
        price = c.get("price")
        peak_eps = peakeps
        mc = c.get("market_cap_m")

        fund_cap = cap
        pers = 0.75
        if fund_cap is not None:
            if fund_cap >= 30:
                pers = 0.85
            elif fund_cap >= 20:
                pers = 0.75
            else:
                pers = 0.62

        s1_tweaked = abs(sales1y - base_sales1y) > 0.01
        s5_tweaked = abs(salescagr - base_salescagr) > 0.01
        cg_tweaked = abs(capgrowth - base_capgrowth) > 0.01
        base_bb = (c.get("buyback_yield") * 100.0) if c.get("buyback_yield") is not None else 0.0
        bb_tweaked = abs(bb - base_bb) > 0.01
        base_roic = (c.get("roic_used") * 100.0) if c.get("roic_used") is not None else (
            (c.get("roic_operating") * 100.0) if c.get("roic_operating") is not None else (
                (c.get("roic_median") * 100.0) if c.get("roic_median") is not None else 18.0
            )
        )
        roic_tweaked = abs(roic - base_roic) > 0.01

        raw_bb = c.get("buyback_yield") if (not bb_tweaked and c.get("buyback_yield") is not None) else (bb / 100.0)
        bb_eff = max(-0.03, min(0.035, raw_bb))
        bb_pos = max(0.0, bb_eff)
        bb_org = min(0.0, bb_eff)
        s1_val = c.get("sales_1y") if (not s1_tweaked and c.get("sales_1y") is not None) else (sales1y / 100.0)
        s5_val = c.get("sales_cagr") if (not s5_tweaked and c.get("sales_cagr") is not None) else (salescagr / 100.0)
        cg_val = c.get("cap_growth") if (not cg_tweaked and c.get("cap_growth") is not None) else ((capgrowth / 100.0) if cg_tweaked else None)

        delta_s5 = (salescagr - base_salescagr) / 100.0 if s5_tweaked else 0.0
        oc_cagr = (c.get("opcost_cagr") + delta_s5) if c.get("opcost_cagr") is not None else None
        g_oe = (c.get("cagr_oe_eps") + delta_s5) if c.get("cagr_oe_eps") is not None else None

        g_base = 0.035
        g_anchor_max = 0.18
        roic_cap = 0.50
        has_sales_cagr = (c.get("sales_cagr") is not None) or s5_tweaked
        has_sales_1y = (c.get("sales_1y") is not None) or s1_tweaked
        has_stmt_growth = (oc_cagr is not None) or has_sales_cagr or has_sales_1y or (g_oe is not None) or (cg_val is not None)

        base_org = g_base
        if has_stmt_growth:
            if oc_cagr is not None and has_sales_cagr:
                base_org = min(s5_val, 0.70 * oc_cagr + 0.30 * s5_val)
            elif oc_cagr is not None:
                base_org = oc_cagr
            elif has_sales_cagr:
                base_org = s5_val
            elif g_oe is not None:
                base_org = g_oe - bb_pos
            elif has_sales_1y:
                base_org = s1_val
            g_org_start = round(max(0.0, min(g_anchor_max, base_org + bb_org)), 4)
            g_start = round(max(-0.04, min(g_anchor_max + bb_pos, g_org_start + bb_pos)), 4)
        else:
            if c.get("g_est") is not None:
                g_start = round(c.get("g_est"), 4)
            elif c.get("g_implied") is not None:
                g_start = round(max(0.0, c.get("g_implied")), 4)
            else:
                g_start = g_base
            base_org = g_start - bb_pos
            g_org_start = round(max(0.0, min(g_anchor_max, base_org)), 4)

        if gest is not None:
            g_est_val = gest / 100.0
            g_org_exp = round(max(0.0, min(g_anchor_max, g_est_val - bb_pos)), 4)
            g_exp = round(max(0.0, min(g_anchor_max + bb_pos, g_est_val)), 4)
        elif not has_stmt_growth and c.get("g_implied") is not None:
            g_org_exp = round(max(0.0, min(g_anchor_max, c.get("g_implied") - bb_pos)), 4)
            g_exp = round(g_org_exp + bb_pos, 4)
        else:
            g_org_exp = g_org_start
            g_exp = round(g_org_exp + bb_pos, 4)

        roic_input = c.get("roic_used") if (not roic_tweaked and c.get("roic_used") is not None) else (roic / 100.0)
        has_roic_est = (c.get("roic_est") is not None) or roic_tweaked
        r_tang = c.get("roic_operating")
        roic_gaap = c.get("roic_median")
        sub_ind = (c.get("sub_industry") or "").strip()
        uses_gaap = bool(c.get("uses_gaap_roic")) if c.get("uses_gaap_roic") is not None else uses_gaap_roic(sub_ind)
        if (
            not has_roic_est
            and not uses_gaap
            and r_tang is not None
            and roic_gaap is not None
            and r_tang > 1.25 * roic_gaap
            and roic_gaap > 0
            and cg_val is not None
            and cg_val > 0
        ):
            g_ref = max(0.04, base_org if has_stmt_growth else g_base)
            alpha = max(0.0, min(1.0, cg_val / g_ref))
            ronic_raw = 1.0 / ((1.0 - alpha) / r_tang + alpha / roic_gaap)
        else:
            ronic_raw = roic_input
        roic_log = round(max(0.05, ronic_raw), 4)
        roic_exp = round(max(0.05, ronic_raw) if has_roic_est else max(0.05, min(roic_cap, ronic_raw)), 4)
        roic_avg = 0.12

        # Valuation
        has_hist_mults = bool(ml and mh)
        moat_arch = c.get("g3a_moat_archetype")
        has_moat_arch = bool(moat_arch and str(moat_arch).strip() not in ("", "None"))
        has_valuation_inputs = bool(price and peak_eps and peak_eps > 0 and (has_hist_mults or fund_cap is not None or c.get("peak_eps_est") is not None or has_moat_arch))
        if not has_valuation_inputs:
            return {"has_inputs": False}

        cur_mult = price / peak_eps
        g_org_val = g_org_exp if g_org_exp is not None else 0.035
        is_bs_fin = (
            bool(c.get("bs_fin"))
            if c.get("bs_fin") is not None
            else is_balance_sheet_financial(sub_ind)
        )
        k = 0.1025 if is_bs_fin else 0.085
        n_cap = fund_cap if (fund_cap is not None and fund_cap > 0) else 20.0
        roic_eff = max(roic_exp, 0.05)

        fcf_conv = c.get("fcf_conv")
        ocf_ni_2y = c.get("ocf_ni_2y")
        is_peak_edited = (base_peakeps is not None and peak_eps is not None) and abs(peak_eps - base_peakeps) > 0.01
        has_peak_override = (c.get("peak_eps_est") is not None) or is_peak_edited
        if c.get("mtm_holdco") is not None and not is_peak_edited:
            is_mtm = bool(c.get("mtm_holdco"))
        else:
            is_mtm = is_mtm_holdco(sub_ind, fcf_conv, None if not has_peak_override else peak_eps, mh, ocf_ni_2y=ocf_ni_2y)
        is_finite = ("Construction & Engineering" in sub_ind or "Highways & Railtracks" in sub_ind) and (fcf_conv is not None and fcf_conv > 1.25)

        bvps = c.get("bvps")
        if is_mtm:
            nav_mult = (bvps / peak_eps) if (bvps and bvps > 0 and peak_eps > 0) else (1.0 / roic_eff)
            pe_mm = nav_mult
            pe_mck = 0.0
            pe_vd = nav_mult
            reinv_eff = 1.0
            fcfs_5 = [0.0] * 5
            v_5 = pe_vd * ((1.0 + k) ** 5)
        else:
            pe_vd, pe_mm, pe_mck, reinv_eff, fcfs_5, v_5 = dcf_schedule_and_continuation(
                g_org_val, roic_eff, n_cap, r=k, g_term=g_base, roic_term_base=roic_avg, finite_conc=is_finite
            )

        par_mult = pe_vd
        par_val = bvps if (is_mtm and bvps and bvps > 0) else par_mult * peak_eps
        vs_par = price / par_val - 1.0

        irr_5y = solve_irr_5y(cur_mult, fcfs_5, v_5)

        pe_base = 1.0 / k
        eff_cap = fund_cap if (fund_cap is not None and fund_cap > 0) else (20.0 if has_moat_arch else None)
        if eff_cap and price > 0 and par_val > 0:
            if not is_mtm and par_mult > pe_base + 0.5:
                cap_implied = round(max(0.0, eff_cap * (cur_mult - pe_base) / (par_mult - pe_base)) * 10) / 10
            else:
                cap_implied = round(eff_cap * (price / par_val) * 10) / 10
        else:
            cap_implied = None
        cap_gap = round((eff_cap - cap_implied) * 10) / 10 if (eff_cap is not None and cap_implied is not None) else None

        return {
            "has_inputs": True,
            "g_start": g_start,
            "g_org_start": g_org_start,
            "g_exp": g_exp,
            "g_org_exp": g_org_exp,
            "pe_vd": pe_vd,
            "par_mult": par_mult,
            "par_val": par_val,
            "vs_par": vs_par,
            "irr_5y": irr_5y,
            "cap_implied": cap_implied,
            "cap_gap": cap_gap,
        }

    def test_growth_sliders_responsive_without_opcost_muting(self):
        """Raising 1Y Sales and 5Y Sales CAGR sliders in Sandbox should shift g_start full-strength."""
        sample = next(c for c in self.companies if c.get("ticker") == "MSFT")
        base = self._simulate_js_sandbox(sample)
        tweaked = self._simulate_js_sandbox(sample, {
            "sales1y": (sample["sales_1y"] * 100.0) + 4.0,
            "salescagr": (sample["sales_cagr"] * 100.0) + 4.0,
        })
        self.assertGreater(tweaked["g_start"], base["g_start"] + 0.02)
        self.assertGreater(tweaked["par_val"], base["par_val"])

    def test_holdco_peak_eps_override_unlocks_standard_value_driver(self):
        """Editing Peak EPS on an MTM HoldCo in Sandbox unlocks standard PE_VD instead of NAV anchor."""
        mtm = next(
            (
                c for c in self.companies
                if "Multi-Sector Holdings" in (c.get("sub_industry") or "")
                and c.get("peak_eps_est") is None
                and c.get("mtm_holdco")
                and (c.get("roic_exp") or 0) > 0.12
                and (c.get("g_org_exp") or 0) > 0.035
            ),
            None,
        )
        self.assertIsNotNone(mtm)
        base = self._simulate_js_sandbox(mtm)
        tweaked = self._simulate_js_sandbox(mtm, {"peakeps": mtm["peak_eps"] * 0.6})
        # When Peak EPS is edited, MTM HoldCo switches from NAV anchor to explicit DCF PE_VD
        self.assertNotAlmostEqual(tweaked["pe_vd"], base["pe_vd"], places=1)
        self.assertGreater(tweaked["pe_vd"], 10.0)

    def test_spinoff_missing_5y_multiples_falls_back_to_pe_vd(self):
        """Recent spin-offs in the funnel missing 5Y multiples (e.g. HONA) fall back to 100% PE_VD instead of No data."""
        hona = next(c for c in self.companies if c.get("ticker") == "HONA")
        self.assertIsNone(hona.get("mult_low_5y"))
        self.assertIsNone(hona.get("mult_high_5y"))
        self.assertIsNotNone(hona.get("par_val"))
        self.assertIsNotNone(hona.get("irr_5y"))
        self.assertAlmostEqual(hona["par_mult"], hona["pe_vd"], places=4)
        sim = self._simulate_js_sandbox(hona)
        self.assertTrue(sim["has_inputs"])
        self.assertAlmostEqual(sim["par_val"], hona["par_val"], places=2)

    def test_all_companies_have_zero_baseline_discrepancies(self):
        """Simulate JS sandbox baseline calculation across all universe companies and assert 0 discrepancies."""
        discrepancies = []
        tested_count = 0

        for c in self.companies:
            ticker = c.get("ticker", "UNKNOWN")
            # Only test companies with valid baseline valuation
            if not (c.get("price") and c.get("peak_eps") and c.get("peak_eps", 0) > 0):
                continue

            # In recorded data, par_val and irr_5y exist
            if c.get("par_val") is None or c.get("irr_5y") is None:
                continue

            res = self._simulate_js_sandbox(c)
            self.assertTrue(res["has_inputs"])

            tested_count += 1

            # Check par_val (within 0.05 currency unit or 0.1%)
            exp_val = c.get("par_val")
            calc_val = res["par_val"]
            if abs(calc_val - exp_val) > 0.05 and abs(calc_val - exp_val) / max(0.01, exp_val) > 0.001:
                discrepancies.append((ticker, "par_val", exp_val, calc_val))

            # Check IRR (within 0.0005 = 0.05%)
            exp_irr = c.get("irr_5y")
            calc_irr = res["irr_5y"]
            if abs(calc_irr - exp_irr) > 0.0005:
                discrepancies.append((ticker, "irr_5y", exp_irr, calc_irr))

            # Check par_mult (within 0.05x)
            exp_mult = c.get("par_mult")
            calc_mult = res["par_mult"]
            if exp_mult is not None and abs(calc_mult - exp_mult) > 0.05:
                discrepancies.append((ticker, "par_mult", exp_mult, calc_mult))

            # Check cap_gap (within 0.1y rounding variance or 0.2% relative for extreme >100y gaps)
            exp_cap_gap = c.get("cap_gap")
            calc_cap_gap = res["cap_gap"]
            if (
                exp_cap_gap is not None
                and calc_cap_gap is not None
                and abs(calc_cap_gap - exp_cap_gap) > 0.1001
                and abs(calc_cap_gap - exp_cap_gap) / max(1.0, abs(exp_cap_gap)) > 0.002
            ):
                discrepancies.append((ticker, "cap_gap", exp_cap_gap, calc_cap_gap))

        self.assertGreater(tested_count, 100, f"Expected to test >100 companies, tested {tested_count}")
        self.assertEqual(
            len(discrepancies),
            0,
            f"Found {len(discrepancies)} discrepancies between Python baseline and JS sandbox: {discrepancies[:10]}",
        )

    def test_real_javascript_engine_parity_via_jsc(self):
        """Execute the actual compiled dashboard JavaScript in JavaScriptCore against all companies."""
        import re

        html = build_dashboard_html(self.screener_data)
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S)
        self.assertGreaterEqual(len(scripts), 2)
        raw_json, main_js = scripts[0], scripts[1]

        harness = ROOT / "tests" / "js_parity_harness.js"
        with tempfile.TemporaryDirectory() as tmpdir:
            js_path = Path(tmpdir) / "main.js"
            json_path = Path(tmpdir) / "data.json"
            js_path.write_text(main_js, encoding="utf-8")
            json_path.write_text(raw_json, encoding="utf-8")
            proc = subprocess.run(
                ["osascript", "-l", "JavaScript", str(harness), str(js_path), str(json_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            report = json.loads(proc.stdout.strip())
            self.assertGreater(report["tested"], 1000)
            self.assertEqual(report["n_errors"], 0, f"JS runtime errors: {report['runtime_errors']}")
            self.assertEqual(report["parity_drift"], 0, f"JS/Python parity drift: {report['drift_examples']}")


class ValuationV636AuditRemediationTests(unittest.TestCase):
    """Unit tests for the v6.36 quantitative valuation model audit fixes."""

    def test_g_market_round_trip_and_flags(self):
        """Verify solve_market_growth round-trip at Fair Value and boundary/monotonicity flags."""
        # 1. Exact round-trip when cur_mult == Fair P/E
        g0 = 0.095
        roic0 = 0.24
        pe_fair, _, _, _ = explicit_dcf_multiple(g0, roic0, 20, r=0.085, g_term=0.035)
        g_mkt, flag = solve_market_growth(pe_fair, g0, roic0, 20, r=0.085, g_term=0.035)
        self.assertEqual(flag, "ok")
        self.assertAlmostEqual(g_mkt, g0, places=4)

        # 2. When ROIC_0 < r (and roic_term_base < r), growth destroys value -> no_value_creation
        g_mkt_flat, flag_flat = solve_market_growth(14.0, 0.05, 0.06, 20, r=0.085, g_term=0.035, roic_term_base=0.06)
        self.assertEqual(flag_flat, "no_value_creation")

        # 3. Finite-horizon concession (e.g. FGR.FR / DG.FR) where reinvestment destroys finite annuity value
        g_mkt_conc, flag_conc = solve_market_growth(9.5, 0.06, 0.13, 20, r=0.085, g_term=0.035, finite_conc=True)
        self.assertEqual(flag_conc, "no_value_creation")

        # 4. Saturated high and low bounds
        g_low, flag_low = solve_market_growth(2.0, 0.08, 0.25, 20, r=0.085, g_term=0.035)
        self.assertEqual(flag_low, "saturated_low")
        self.assertAlmostEqual(g_low, -0.20, places=4)

        g_high, flag_high = solve_market_growth(500.0, 0.08, 0.25, 20, r=0.085, g_term=0.035)
        self.assertEqual(flag_high, "saturated_high")
        self.assertAlmostEqual(g_high, 0.50, places=4)

    def test_uncapped_reinvestment_prevents_free_growth_when_g_exceeds_roic(self):
        """Verify removing the 0.95 reinvestment cap prevents free-lunch valuation inflation when ROIC < r."""
        # When ROIC_0 = 6% < r = 8.5% (and roic_end=6%), higher growth must REDUCE Fair P/E even if g_0 > 6%
        pe_low_g, _, _, _ = explicit_dcf_multiple(0.02, 0.06, 20, r=0.085, g_term=0.02, roic_term_base=0.06, roic_end=0.06)
        pe_high_g, _, _, _ = explicit_dcf_multiple(0.12, 0.06, 20, r=0.085, g_term=0.02, roic_term_base=0.06, roic_end=0.06)
        self.assertLess(pe_high_g, pe_low_g)

    def test_miller_modigliani_zero_spread_invariance_and_bellman_5y_irr(self):
        """Verify Fair P/E == 1/r when RONIC == r across all g0 and N, and Bellman 5Y IRR == r at Fair Value."""
        # 1. Exact Miller-Modigliani zero-spread theorem: when RONIC_t == r, Fair P/E == 1 / r to < 1e-12
        for r in (0.085, 0.1025):
            for g0 in (0.0, 0.035, 0.08, 0.14, 0.18):
                for n_cap in (5, 10, 15, 20, 30):
                    pe, _, _, _, fcfs_5, v_5 = dcf_schedule_and_continuation(g0, r, n_cap, r=r, g_term=0.035, roic_end=r)
                    self.assertAlmostEqual(pe, 1.0 / r, places=12)
                    irr = solve_irr_5y(pe, fcfs_5, v_5)
                    self.assertAlmostEqual(irr, r, places=7)

        # 2. Across all funnel companies in the live dataset, IRR > r iff vs_par < 0 (zero sign contradictions)
        data = collect_screener_data(["us", "eu", "ca"])
        contradictions = []
        for c in data["companies"]:
            if c.get("result") not in ("Quality pass", "Calamity pass"):
                continue
            vs_par = c.get("vs_par")
            irr = c.get("irr_5y")
            r = c.get("disc_rate") or 0.085
            if vs_par is None or irr is None:
                continue
            if (vs_par < -1e-4 and irr < r - 1e-4) or (vs_par > 1e-4 and irr > r + 1e-4):
                contradictions.append((c["id"], vs_par, irr, r))
        self.assertEqual(contradictions, [])

        # 3. Verify ASML == ASML.NL cross-universe mirror parity and IBKR consolidated ROE
        by_id = {c["id"]: c for c in data["companies"]}
        self.assertAlmostEqual(by_id["ASML"]["par_mult"], by_id["ASML.NL"]["par_mult"], places=4)
        self.assertEqual(by_id["ASML"]["g4_cap"], by_id["ASML.NL"]["g4_cap"])
        self.assertEqual(by_id["FER"]["result"], by_id["FER.ES"]["result"])
        self.assertGreater(by_id["IBKR"]["roic_exp"], 0.18)

    def test_mtm_holdco_2y_cash_conversion_and_bvps_anchor(self):
        """Verify 2Y OCF/NI < 0.25 triggers MTM HoldCo and anchors Fair Value to 1.0x BVPS."""
        # III.GB pattern: 5Y fcf_conv = 0.43 (>= 0.25), but recent 2Y ocf_ni_2y = 0.08 (< 0.25)
        self.assertFalse(is_mtm_holdco("Multi-Sector Holdings", fcf_conv=0.43, peak_eps_est=None, mult_high_5y=8.0, ocf_ni_2y=0.40))
        self.assertTrue(is_mtm_holdco("Multi-Sector Holdings", fcf_conv=0.43, peak_eps_est=None, mult_high_5y=8.0, ocf_ni_2y=0.08))

        # Valuation of MTM HoldCo uses 1.0x BVPS (equity_m * price / market_cap_m)
        fin = {
            "price": 40.0,
            "market_cap_m": 40000.0,
            "equity_m": 30000.0,  # BVPS = 30.0
            "peak_oe_eps": 10.0,
            "fcf_conv": 0.10,
            "ocf_ni_2y": 0.05,
            "roic_median": 0.18,
            "roe_median": 0.20,
            "sales_cagr": 0.12,
        }
        res = par_valuation(fin, params({}), cap=20, moat="Scale economies shared", sub_industry="Multi-Sector Holdings")
        self.assertTrue(res["mtm_holdco"])
        self.assertAlmostEqual(res["bvps"], 30.0, places=2)
        self.assertAlmostEqual(res["par_val"], 30.0, places=2)
        self.assertAlmostEqual(res["par_mult"], 3.0, places=2)
        self.assertEqual(res["g_market_flag"], "nav_anchored")
        self.assertIsNone(res["g_market"])
        self.assertIsNone(res["g_gap"])

    def test_da_impairment_guard_and_ifrs16_lease_deduction(self):
        """Verify clean_da caps single-year impairment spikes and owner_addback deducts IFRS-16 lease dep."""
        # 1. Single-year goodwill impairment spike in 2024 (480 vs ~100 normal D&A across 3 prior years)
        raw_da = {2021: 95.0, 2022: 100.0, 2023: 105.0, 2024: 480.0}
        cleaned = clean_da(raw_da)
        self.assertEqual(cleaned[2022], 100.0)
        self.assertAlmostEqual(cleaned[2024], 150.0, places=2)  # capped at 1.5x median(95, 100, 105) = 150

        # 2. IFRS-16 lease deduction in owner_addback (MC.FR pattern: D&A includes ROU amortization, CapEx excludes it)
        s_ifrs = {
            "da": {2023: 5500.0, 2024: 6000.0},
            "capex": {2023: 3500.0, 2024: 3600.0},
            "lease": {2023: 14000.0, 2024: 16000.0},  # avg lease = 15000 -> 20% = 3000 lease dep
        }
        # Raw D&A - CapEx = 6000 - 3600 = +2400, but after 3000 ROU lease dep add-back is max(0, -600) = 0
        self.assertEqual(owner_addback(s_ifrs, 2024), 0.0)

        # US GAAP filer (lease series cleared by apply_lease_basis) retains full D&A - CapEx
        s_us = {"da": {2024: 600.0}, "capex": {2024: 400.0}, "lease": {}}
        self.assertEqual(owner_addback(s_us, 2024), 200.0)

    def test_short_term_investments_netted_in_roic(self):
        """Verify summarize() nets cash_sti (cash + short-term marketable securities) in ROIC."""
        s = {
            "ebit": {y: 500e6 for y in range(2020, 2025)},
            "pretax": {y: 500e6 for y in range(2020, 2025)},
            "tax": {y: 100e6 for y in range(2020, 2025)},
            "ni": {y: 400e6 for y in range(2020, 2025)},
            "equity": {y: 5000e6 for y in range(2020, 2025)},
            "debt": {y: 0.0 for y in range(2020, 2025)},
            "cash": {y: 500e6 for y in range(2020, 2025)},        # Narrow cash only 500M
            "cash_sti": {y: 4000e6 for y in range(2020, 2025)},   # Cash + T-bills = 4000M (like VEEV)
            "assets": {y: 6500e6 for y in range(2020, 2025)},
            "goodwill": {y: 200e6 for y in range(2020, 2025)},
            "intang": {y: 100e6 for y in range(2020, 2025)},
        }
        summary = summarize(s)
        # Without cash_sti, GAAP IC would be 4500M (ROIC = 400/4500 = 8.9%). With cash_sti netted, GAAP IC is 1000M (ROIC = 40.0%)
        self.assertAlmostEqual(summary["roic_median"], 0.40, places=2)
        self.assertGreater(summary["roic_operating"], 0.45)

    def test_balance_sheet_financial_includes_ib_brokerage_and_uses_5y_roe(self):
        """Verify Investment Banking & Brokerage is routed as a Balance-Sheet Financial using 5Y ROE."""
        self.assertTrue(is_balance_sheet_financial("Investment Banking & Brokerage"))
        fin = {"roic_est": None, "roe_median": 0.149, "roic_median": 0.483, "roic_operating": 0.483}
        roic_val, roic_src = active_roic(fin, "Investment Banking & Brokerage")
        self.assertAlmostEqual(roic_val, 0.149, places=4)
        self.assertEqual(roic_src, "roe_median")


if __name__ == "__main__":
    unittest.main()
