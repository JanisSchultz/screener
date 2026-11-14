"""Tests for the v6.25 Conditional Calamity Pass tier (Gates 3b, 5, and 6 only)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import config as C
from screener.apply_evaluation import validate_and_waterfall
from screener.dashboard import build_dashboard_html
from screener.data import load_universe
from screener.gates import funnel_ids, params, phase_results


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
        "3a": "Toll booth / Switching costs",
        "3b": "Y",
        "3m": "Strong switching costs.",
        "4": 20,
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
        "note": "Test note",
        "evidence": "Test evidence",
    }
    row.update(overrides)
    return row


class CalamityGateTests(unittest.TestCase):
    def setUp(self):
        self.p = params({})

    def test_clean_pass_remains_quality_pass(self):
        res = phase_results(base_company(), self.p)
        self.assertEqual(res["result"], C.RES_QPASS)
        self.assertEqual(res["waived"], [])
        self.assertEqual(res["rejected_at"], "")

    def test_gate_3b_calamity_passes_when_anchors_pass(self):
        c = base_company(**{"3b": "N", "calamity": "Y", "calamity_note": "Temp ROIC dip; catalyst + kill-switch."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_CALAMITY)
        self.assertEqual(res["status"]["3b"], "fail")
        self.assertEqual([k for k, _, _ in res["waived"]], ["3b"])
        self.assertEqual(res["rejected_at"], "")

    def test_gate_5_and_6_calamity_passes(self):
        c = base_company(**{"5": 0, "6": "N", "calamity": "Y", "calamity_note": "New CEO + deleveraging."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_CALAMITY)
        self.assertEqual([k for k, _, _ in res["waived"]], ["5", "6"])

    def test_non_waivable_anchor_gates_still_reject(self):
        for field, val, expected_phase in [("1", "N", 1), ("2", "N", 2), ("3a", "None", 3), ("4", 10, 4)]:
            c = base_company(**{field: val, "6": "N", "calamity": "Y", "calamity_note": "Attempted override."})
            res = phase_results(c, self.p)
            self.assertEqual(res["result"], C.RES_REJ[expected_phase], msg=f"Failed anchor check for {field}={val}")
            self.assertEqual(res["waived"], [])

    def test_blank_3a_with_3b_calamity_requires_review(self):
        c = base_company(**{"3a": "", "3b": "N", "calamity": "Y", "calamity_note": "Temp dip."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REVIEW)
        self.assertEqual(res["review_at"], "G3 Moat & Pricing >= Infl.")

    def test_blank_downstream_gate_stops_as_to_review(self):
        c = base_company(**{"3b": "N", "4": "", "calamity": "Y", "calamity_note": "Temp dip."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REVIEW)
        self.assertEqual(res["review_at"], "G4 Runway (15+ Yrs)")

    def test_funnel_ids_includes_and_excludes_calamity(self):
        meta = {
            "parameters": {},
            "prescreen": [],
            "markets": [],
            "companies": [
                base_company(id="CLEAN"),
                base_company(id="CAL", **{"6": "N", "calamity": "Y", "calamity_note": "Bridge debt."}),
                base_company(id="REJ", **{"4": 10, "calamity": "Y", "calamity_note": "Secular threat."}),
            ],
        }
        self.assertEqual(funnel_ids(meta, include_calamity=True), ["CLEAN", "CAL"])
        self.assertEqual(funnel_ids(meta, include_calamity=False), ["CLEAN"])


class ApplyEvaluationWaterfallTests(unittest.TestCase):
    def test_3b_calamity_preserves_downstream_gates(self):
        payload = {
            "qualitative": {
                "gate_1": "Y",
                "gate_2": "Y",
                "gate_3a_moat_archetype": "Toll booth / Switching costs",
                "gate_3b_pricing_and_proof": "N",
                "gate_4_runway_cap": 20,
                "gate_5_management_score": 1,
                "gate_6_cash_and_balance_sheet": "Y",
                "calamity_flag": "Y",
                "calamity_note": "Temporary margin reset; moat intact; kill switch 24m.",
            }
        }
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(warnings, [])
        self.assertEqual(qual["3b"], "N")
        self.assertEqual(qual["4"], 20)
        self.assertEqual(qual["5"], 1)
        self.assertEqual(qual["6"], "Y")
        self.assertEqual(qual["calamity"], "Y")

    def test_gate4_failure_clears_calamity_and_downstream(self):
        payload = {
            "qualitative": {
                "gate_1": "Y",
                "gate_2": "Y",
                "gate_3a_moat_archetype": "Toll booth / Switching costs",
                "gate_3b_pricing_and_proof": "N",
                "gate_4_runway_cap": 10,
                "gate_5_management_score": 1,
                "gate_6_cash_and_balance_sheet": "N",
                "calamity_flag": "Y",
                "calamity_note": "Should not survive Gate 4 failure.",
            }
        }
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["5"], "")
        self.assertEqual(qual["6"], "")
        self.assertEqual(qual["calamity"], "")
        self.assertEqual(qual["calamity_note"], "")
        self.assertTrue(any("calamity" in w.lower() for w in warnings))

    def test_quantitative_only_payload_leaves_qual_empty(self):
        payload = {"id": "RTO.GB", "quantitative_overrides": {"g_implied": 0.055, "roic_est": 0.35}}
        qual, fin, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual, {})
        self.assertEqual(fin["g_implied"], "0.055")
        self.assertEqual(warnings, [])


class DashboardAndDataIntegrityTests(unittest.TestCase):
    def test_universe_baseline_counts_preserved(self):
        counts = {k: len(funnel_ids(load_universe(k), include_calamity=False)) for k in ("us", "eu", "ca")}
        self.assertEqual(counts, {"us": 109, "eu": 103, "ca": 11})

    def test_dashboard_html_renders_calamity_tier(self):
        payload = {
            "version": "6.25",
            "generated_at": "2026-11-10",
            "summary": {
                "total_companies": 2,
                "quality_pass": 1,
                "calamity_pass": 1,
                "calamity_below_par": 1,
                "below_par": 1,
                "median_irr_below_par": 0.14,
            },
            "universes": {"us": {"key": "us", "title": "US", "index_name": "US", "currency": "USD", "as_of": "2026-11-10", "parameters": {}}},
            "companies": [
                {
                    "id": "CLEAN", "ticker": "CLEAN", "company": "Clean Co", "country": "United States",
                    "sector": "Information Technology", "sub_industry": "Systems Software", "universe": "us",
                    "g1": "Y", "g2": "Y", "g2_reason": None, "g3a_moat_archetype": "Toll booth / Switching costs",
                    "g3b_pricing": "Y", "g3m_moat_note": "Moat", "g4_cap": 20, "g5_mgmt": 2, "g6_cash": "Y",
                    "calamity_flag": "", "calamity_note": "", "note": "Clean", "evidence": "Ev",
                    "result": C.RES_QPASS, "rejected_at": "", "review_at": "",
                    "gate_status": {"1": "pass", "2": "pass", "3b": "pass", "4": "pass", "5": "pass", "6": "pass"},
                    "failed_gates": [], "waived_gates": [], "waived_keys": [],
                    "price": 90.0, "quote_currency": "USD", "val_status": C.V_BELOW_PAR,
                    "par_val": 110.0, "vs_par": -0.18, "cur_mult": 18.0, "par_mult": 22.0, "irr_5y": 0.14,
                    "roic_used": 0.3, "roic_operating": 0.3, "roic_median": 0.25, "fcf_conv": 1.0,
                    "g_gap": 0.02, "cap_gap": 3.0, "fin_note": "",
                },
                {
                    "id": "CAL6", "ticker": "CAL6", "company": "Calamity Co", "country": "United States",
                    "sector": "Information Technology", "sub_industry": "Application Software", "universe": "us",
                    "g1": "Y", "g2": "Y", "g2_reason": None, "g3a_moat_archetype": "Toll booth / Switching costs",
                    "g3b_pricing": "Y", "g3m_moat_note": "Moat", "g4_cap": 20, "g5_mgmt": 1, "g6_cash": "N",
                    "calamity_flag": "Y", "calamity_note": "Temporary M&A bridge debt; 24m deleveraging catalyst.",
                    "note": "Calamity", "evidence": "Ev",
                    "result": C.RES_CALAMITY, "rejected_at": "", "review_at": "",
                    "gate_status": {"1": "pass", "2": "pass", "3b": "pass", "4": "pass", "5": "pass", "6": "fail"},
                    "failed_gates": ["G6 Cash & Fortress Balance Sheet"],
                    "waived_gates": ["G6 Cash & Fortress Balance Sheet"], "waived_keys": ["6"],
                    "price": 80.0, "quote_currency": "USD", "val_status": C.V_BELOW_PAR,
                    "par_val": 100.0, "vs_par": -0.20, "cur_mult": 16.0, "par_mult": 20.0, "irr_5y": 0.16,
                    "roic_used": 0.28, "roic_operating": 0.28, "roic_median": 0.2, "fcf_conv": 0.72,
                    "g_imp": 0.08, "g_market": 0.05, "g_gap": 0.03, "cap_implied": 16.0, "cap_gap": 4.0, "fin_note": "",
                },
            ],
            "changelog": C.CHANGELOG,
        }
        html = build_dashboard_html(payload)
        self.assertIn("Calamity Watchlist", html)
        self.assertIn("Include Calamities", html)
        self.assertIn("Temporary M&A bridge debt; 24m deleveraging catalyst.", html)
        for token in ("Growth Ceiling", "Mkt Implied g", "g Margin", "Our CAP", "Mkt CAP", "CAP Gap", "dossier-g-imp", "dossier-cap-implied"):
            self.assertIn(token, html)


if __name__ == "__main__":
    unittest.main()
