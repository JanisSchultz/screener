"""Tests for v7.19 Calamity retirement and the Growth at ~0g discovery tier."""
from __future__ import annotations

import csv
import json
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import config as C
from screener.apply_evaluation import validate_and_waterfall
from screener.dashboard import build_dashboard_html, collect_screener_data
from screener.data import DATA_DIR, load_universe
from screener.gates import G_FLAG_OK, G_FLAG_SAT_HI, G_FLAG_SAT_LO, funnel_ids, params, phase_results


def base_company(**overrides) -> dict:
    row = {
        "id": "TEST",
        "ticker": "TEST",
        "company": "Test Corp",
        "country": "United States",
        "sector": "Information Technology",
        "sub_industry": "Application Software",
        "1": "Y",
        "2": "Y",
        "2r": "",
        "3_tb": 2,
        "3_ia": 0,
        "3_se": 0,
        "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Strong switching costs.",
        "4_ent": 0,
        "4_riv": 0,
        "4_buy": 0,
        "4_sup": 0,
        "4_sub": 0,
        "4": 20,
        "4n": "",
        "5": 1,
        "6": "Y",
        "note": "Test note",
        "evidence": "Test evidence",
    }
    row.update(overrides)
    return row


class CalamityRetirementTests(unittest.TestCase):
    def setUp(self):
        self.p = params({})

    def test_calamity_constants_removed_from_config(self):
        for attr in ("CALAMITY_GATES", "CALAMITY_FLAG_DEF", "RES_CALAMITY", "V_CALAMITY"):
            self.assertFalse(hasattr(C, attr), f"Stale constant {attr} still present in config.py")
        self.assertEqual(C.FUNNEL_RESULTS, (C.RES_QPASS,))
        self.assertNotIn("Calamity pass", C.Q_RESULTS)

    def test_gate_failures_never_waived(self):
        self.assertEqual(phase_results(base_company(**{"3b": "N"}), self.p)["result"], C.RES_REJ[3])
        self.assertEqual(phase_results(base_company(**{"4_sub": 2, "4": 10}), self.p)["result"], C.RES_REJ[4])
        self.assertEqual(phase_results(base_company(**{"5": 0}), self.p)["result"], C.RES_REJ[5])
        self.assertEqual(phase_results(base_company(**{"6": "N"}), self.p)["result"], C.RES_REJ[6])

        clean_res = phase_results(base_company(), self.p)
        self.assertEqual(clean_res["result"], C.RES_QPASS)
        self.assertNotIn("waived", clean_res)

    def test_funnel_ids_only_includes_quality_pass(self):
        meta = {
            "parameters": {},
            "prescreen": [],
            "markets": [],
            "companies": [
                base_company(id="CLEAN"),
                base_company(id="FAIL6", **{"6": "N"}),
                base_company(id="FAIL3B", **{"3b": "N"}),
            ],
        }
        self.assertEqual(funnel_ids(meta), ["CLEAN"])

    def test_inputs_csv_and_sqlite_retired_calamity(self):
        for u in ("us", "eu", "ca"):
            with (DATA_DIR / u / "inputs.csv").open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fields = reader.fieldnames or []
                self.assertNotIn("calamity", fields)
                self.assertNotIn("calamity_note", fields)
                for r in reader:
                    self.assertNotIn("calamit", (r.get("note", "") + r.get("evidence", "")).lower(), f"{u}:{r['id']}")

        db_path = DATA_DIR / "fundamentals.sqlite"
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cols = [row[1] for row in conn.execute("PRAGMA table_info(companies)").fetchall()]
            cal_results = conn.execute("SELECT COUNT(*) FROM companies WHERE result = 'Calamity pass'").fetchone()[0]
            conn.close()
            self.assertNotIn("calamity", cols)
            self.assertEqual(len(cols), 27)
            self.assertEqual(cal_results, 0)

    def test_baseline_prime_grade_and_former_calamity_outcomes(self):
        counts = {k: len(funnel_ids(load_universe(k))) for k in ("us", "eu", "ca")}
        self.assertEqual(counts, {"us": 110, "eu": 104, "ca": 11})
        self.assertEqual(sum(counts.values()), 225)

        data = collect_screener_data(["us", "eu", "ca"])
        by_id = {c["id"]: c for c in data["companies"]}

        # APD & EL (3b = N) are Stage-1 scrubbed Gate-3 rejects
        for cid in ("APD", "EL"):
            c = by_id[cid]
            self.assertEqual(c["result"], C.RES_REJ[3])
            self.assertFalse(c["passes_quality_grade"])
            self.assertEqual(c["g4_cap"], None)
            self.assertIsNone(c["g5_mgmt"])
            self.assertIsNone(c["g6_cash"])

        # 11 3b=Y former calamity rows retain full G4-G6; 10 remain in Quality Grade (RTX excluded by g6_flags=3)
        former_3b_y = ("DGE.GB", "NESN.CH", "RTO.GB", "GOOGL", "NDAQ", "HONA", "NOC", "RTX", "EFX", "SNPS", "TXN")
        qg_count = 0
        for cid in former_3b_y:
            c = by_id[cid]
            self.assertIsNotNone(c["g4_cap"], cid)
            self.assertIn(c["g5_mgmt"], (0, 1, 2), cid)
            self.assertIn(c["g6_cash"], ("Y", "N"), cid)
            if cid == "RTX":
                self.assertEqual(c["g6_flags"], 3)
                self.assertFalse(c["passes_quality_grade"])
            else:
                self.assertTrue(c["passes_quality_grade"], cid)
                qg_count += 1
        self.assertEqual(qg_count, 10)
        self.assertEqual(sum(1 for c in data["companies"] if c["passes_quality_grade"]), 443)


class Growth0gTierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = collect_screener_data(["us", "eu", "ca"])
        cls.companies = cls.data["companies"]
        cls.html = build_dashboard_html(cls.data)

    def test_growth_0g_live_counts_and_cohorts(self):
        g0_list = [c for c in self.companies if c["passes_growth_0g"]]
        self.assertEqual(len(g0_list), 25)
        self.assertEqual(self.data["summary"]["growth_0g"], 25)

        prime = [c for c in g0_list if c["passes_prime_grade"]]
        g6_fail_runway = [c for c in g0_list if not c["passes_prime_grade"] and (c.get("g4_cap") or 0) >= 15]
        cap_short = [c for c in g0_list if (c.get("g4_cap") or 0) < 15]

        self.assertEqual(len(prime), 9)
        self.assertEqual(len(g6_fail_runway), 6)
        self.assertEqual(len(cap_short), 10)

        for c in g0_list:
            self.assertTrue(c["passes_quality_grade"])
            self.assertEqual(c["val_status"], C.V_VALUED)
            self.assertIn(c["g_market_flag"], (G_FLAG_OK, G_FLAG_SAT_LO))
            self.assertLess(c["g_market"], 0.05)
            self.assertGreaterEqual(c["g_org_exp"], 0.05)

    def test_growth_0g_predicate_boundaries(self):
        base_fin = {
            "price": 100.0,
            "market_cap_m": 10_000.0,
            "peak_oe_eps": 5.0,
            "cur_oe_eps": 5.0,
            "sales_cagr": 0.08,
            "roic_operating": 0.25,
            "roic_median": 0.25,
            "fcf_conv": 1.0,
            "g6_netdebt_yrs": 1.0,
            "g6_intcov": 10.0,
            "p2p_ok": "Y",
        }
        base_co = base_company(id="BND", ticker="BND")

        def eval_case(val_overrides: dict, co_overrides: dict | None = None) -> bool:
            co = dict(base_co)
            if co_overrides:
                co.update(co_overrides)
            val_res = {
                "status": C.V_VALUED,
                "g_market_flag": G_FLAG_OK,
                "g_market": 0.0499,
                "g_org_exp": 0.05,
                "k": 0.085,
                "irr_5y": 0.09,
            }
            val_res.update(val_overrides)
            fake_meta = {
                "title": "US",
                "index_name": "S&P 500",
                "currency": "USD",
                "as_of": "2026-11-18",
                "parameters": {},
                "prescreen": [],
                "markets": [],
                "companies": [co],
                "financials": {"BND": base_fin},
            }
            with patch("screener.dashboard.universe_keys", return_value=["us"]), \
                 patch("screener.dashboard.load_universe", return_value=fake_meta), \
                 patch("screener.dashboard._load_sales_cagrs", return_value={}), \
                 patch("screener.dashboard.par_valuation", return_value=val_res):
                d = collect_screener_data(["us"])
                return d["companies"][0]["passes_growth_0g"]

        # Exact boundary inclusion: g_market = 0.0499 (< 0.05), g_org_exp = 0.05 (>= 0.05)
        self.assertTrue(eval_case({"g_market": 0.0499, "g_org_exp": 0.05}))
        # saturated_low allowed
        self.assertTrue(eval_case({"g_market_flag": G_FLAG_SAT_LO, "g_market": -0.20, "g_org_exp": 0.05}))
        # g_market == 0.05 excluded
        self.assertFalse(eval_case({"g_market": 0.05, "g_org_exp": 0.05}))
        # g_org_exp < 0.05 excluded
        self.assertFalse(eval_case({"g_market": 0.02, "g_org_exp": 0.0499}))
        # saturated_high / no_value_creation / multi_root / nav_anchored excluded
        self.assertFalse(eval_case({"g_market_flag": G_FLAG_SAT_HI, "g_market": 0.02}))
        self.assertFalse(eval_case({"g_market_flag": "no_value_creation", "g_market": 0.02}))
        # Non-Valued excluded
        self.assertFalse(eval_case({"status": C.V_NOVALUE}))
        self.assertFalse(eval_case({"status": C.V_NODATA}))
        # Non-Quality Grade (3b = N) excluded
        self.assertFalse(eval_case({}, {"3b": "N"}))

    def test_dashboard_html_has_growth_0g_and_no_calamity(self):
        self.assertIn("💎 Growth at ~0g", self.html)
        self.assertIn("💎 ~0g Growth", self.html)
        self.assertIn("id=\"kpi-growth-0g\"", self.html)
        self.assertIn("id=\"count-growth-0g\"", self.html)
        changelog_json = json.dumps(self.data["changelog"], ensure_ascii=False)
        html_active = self.html.replace(changelog_json, "")
        self.assertNotIn("calamity", html_active.lower())
        self.assertNotIn("waived", html_active.lower())

        # Tab bar order check
        idx_qpass = self.html.index('data-tab="qpass"')
        idx_g0 = self.html.index('data-tab="growth_0g"')
        idx_qg = self.html.index('data-tab="moat_universe"')
        idx_all = self.html.index('data-tab="all"')
        idx_meth = self.html.index('data-tab="methodology"')
        self.assertTrue(idx_qpass < idx_g0 < idx_qg < idx_all < idx_meth)

    def test_stage1_3b_n_always_scrubs_without_calamity(self):
        payload = {
            "qualitative": {
                "gate_1": "Y",
                "gate_2": "Y",
                "gate_3a_moat_archetype": "Toll booth & switching costs",
                "gate_3b_pricing_and_proof": "N",
                "gate_4_runway_cap": 20,
                "gate_5_management_score": 1,
                "gate_6_cash_and_balance_sheet": "Y",
            }
        }
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["4"], "")
        self.assertEqual(qual["5"], "")
        self.assertEqual(qual["6"], "")
        self.assertTrue(any("3b" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
