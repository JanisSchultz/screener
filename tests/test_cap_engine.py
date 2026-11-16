"""Unit & integration tests for the v7.16 Auditable Two-Step CAP Engine (Gate 3 Moat Profile & Gate 4 Forces)."""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import config as C
from screener.apply_evaluation import apply_evaluation, validate_and_waterfall
from screener.dashboard import build_dashboard_html, collect_screener_data
from screener.data import load_universe, universe_keys, write_csv, input_fields
from screener.gates import (
    cap_audit,
    compute_final_cap_from_scores,
    compute_initial_cap_from_scores,
    moderate_force_haircut,
    params,
    phase_results,
)


class Step1InitialCapTests(unittest.TestCase):
    def test_zero_moats_yields_zero_cap(self):
        self.assertEqual(compute_initial_cap_from_scores((0, 0, 0, 0)), 0)

    def test_moderate_moats_capped_at_20y_without_elite_anchor(self):
        self.assertEqual(compute_initial_cap_from_scores((1, 0, 0, 0)), 15)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 0, 0)), 20)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 1, 0)), 20)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 1, 1)), 20)

    def test_elite_anchor_stacking_steps_20_25_30(self):
        self.assertEqual(compute_initial_cap_from_scores((2, 0, 0, 0)), 20)
        self.assertEqual(compute_initial_cap_from_scores((0, 2, 1, 0)), 25)
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 0, 0)), 30)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 2, 0)), 30)
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 0, 2)), 30)


class Step2FinalCapTests(unittest.TestCase):
    def test_tiered_moderate_haircuts(self):
        self.assertEqual(moderate_force_haircut(0), 0)
        self.assertEqual(moderate_force_haircut(1), 5)
        self.assertEqual(moderate_force_haircut(2), 5)
        self.assertEqual(moderate_force_haircut(3), 10)
        self.assertEqual(moderate_force_haircut(4), 10)
        self.assertEqual(moderate_force_haircut(5), 15)

    def test_non_fatal_deductions_and_5y_floor(self):
        self.assertEqual(compute_final_cap_from_scores(30, (0, 0, 0, 0, 0)), (30, 0, False))
        self.assertEqual(compute_final_cap_from_scores(30, (0, 1, 0, 0, 1)), (25, 5, False))
        self.assertEqual(compute_final_cap_from_scores(30, (1, 1, 1, 0, 0)), (20, 10, False))
        self.assertEqual(compute_final_cap_from_scores(30, (1, 1, 1, 1, 1)), (15, 15, False))
        self.assertEqual(compute_final_cap_from_scores(15, (1, 1, 1, 1, 1)), (5, 15, False))

    def test_fatal_flaw_caps_at_or_below_10y(self):
        # Single Force=2 on 30Y initial CAP -> capped at 10Y
        self.assertEqual(compute_final_cap_from_scores(30, (0, 0, 0, 0, 2)), (10, 0, True))
        # Single Force=2 on 20Y initial CAP with 3 ones -> 20 - 10 - 10 = 0 <= 5 -> 5Y
        self.assertEqual(compute_final_cap_from_scores(20, (1, 1, 1, 0, 2)), (5, 10, True))
        # Single Force=2 on 15Y initial CAP -> 5Y
        self.assertEqual(compute_final_cap_from_scores(15, (0, 0, 0, 0, 2)), (5, 0, True))
        # Two Force=2 -> 5Y
        self.assertEqual(compute_final_cap_from_scores(30, (2, 0, 0, 0, 2)), (5, 0, True))
        # Three+ Force=2 -> 0Y
        self.assertEqual(compute_final_cap_from_scores(30, (2, 2, 0, 0, 2)), (0, 0, True))


class GateWaterfallAndIngestionTests(unittest.TestCase):
    def setUp(self):
        self.p = params({})

    def test_deterministic_cap_overwrites_manual_override(self):
        payload = {
            "qualitative": {
                "gate_1": "Y",
                "gate_2": "Y",
                "gate_3_moat_toll_booth": 2,
                "gate_3_moat_infrastructure": 2,
                "gate_3_moat_scale_shared": 0,
                "gate_3_moat_rd": 1,
                "gate_3a_moat_archetype": "Toll booth & switching costs",
                "gate_3b_pricing_and_proof": "Y",
                "gate_3m_moat_note": "Moat proof.",
                "gate_4_force_entrants": 0,
                "gate_4_force_rivalry": 1,
                "gate_4_force_buyers": 0,
                "gate_4_force_suppliers": 0,
                "gate_4_force_substitution": 1,
                "gate_4_runway_cap": 30,  # attempted manual override (formula says 25)
                "gate_4n_runway_note": "Rivalry and substitution clock speed.",
                "gate_5_management_score": 1,
                "gate_6_cash_and_balance_sheet": "Y",
            }
        }
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["4"], 25)
        self.assertTrue(any("Deterministic Gate 4 CAP" in w for w in warnings))

    def test_tie_breaking_on_primary_moat_3a(self):
        # ASML-like tie (2 on TB, IA, RD): explicitly choosing RD is respected
        aud_rd = cap_audit({"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 2, "3a": "R&D & innovation leadership"})
        self.assertEqual(aud_rd["primary_moat"], "R&D & innovation leadership")
        # Picking an archetype with score 0 is corrected to canonical first max-scorer
        aud_fix = cap_audit({"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0, "3a": "Scale economies shared"})
        self.assertEqual(aud_fix["primary_moat"], "Toll booth & switching costs")
        # All zero -> None & Gate 3 rejection
        c_zero = {"1": "Y", "2": "Y", "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3b": "Y", "4": 20, "5": 1, "6": "Y"}
        self.assertEqual(phase_results(c_zero, self.p)["result"], C.RES_REJ[3])

    def test_incomplete_subscores_stop_as_to_review(self):
        c_part_m = {"1": "Y", "2": "Y", "3_tb": 2, "3_ia": None, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs", "3b": "Y", "4": 20, "5": 1, "6": "Y"}
        self.assertEqual(phase_results(c_part_m, self.p)["result"], C.RES_REVIEW)

        c_part_f = {"1": "Y", "2": "Y", "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs", "3b": "Y", "4_ent": 0, "4_riv": None, "4": 20, "5": 1, "6": "Y"}
        self.assertEqual(phase_results(c_part_f, self.p)["result"], C.RES_REVIEW)

    def test_waterfall_scrubs_new_subcolumns_on_upstream_rejection(self):
        payload_g2_fail = {
            "qualitative": {
                "gate_1": "Y",
                "gate_2": "N",
                "gate_2_reason": "Cyclical.",
                "gate_3_moat_toll_booth": 2,
                "gate_3_moat_infrastructure": 0,
                "gate_3_moat_scale_shared": 0,
                "gate_3_moat_rd": 0,
                "gate_3a_moat_archetype": "Toll booth & switching costs",
                "gate_3b_pricing_and_proof": "Y",
                "gate_4_force_entrants": 0,
                "gate_4_force_rivalry": 0,
                "gate_4_force_buyers": 0,
                "gate_4_force_suppliers": 0,
                "gate_4_force_substitution": 0,
                "gate_4_runway_cap": 20,
                "gate_4n_runway_note": "Should be scrubbed.",
            }
        }
        qual, _, _ = validate_and_waterfall(payload_g2_fail)
        for k in (*C.MOAT_SCORE_CODES, "3a", "3b", *C.FORCE_SCORE_CODES, "4", "4n"):
            self.assertEqual(qual[k], "")

    def test_nonzero_force_requires_4n_note_in_apply_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            u_dir = tmp_root / "us"
            u_dir.mkdir(parents=True)
            meta = {"extra_columns": []}
            fields = input_fields(meta)
            write_csv(u_dir / "inputs.csv", fields, [{"id": "X", "ticker": "X", "company": "X Co", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            bad_payload = {
                "id": "X",
                "qualitative": {
                    "gate_1": "Y", "gate_2": "Y",
                    "gate_3_moat_toll_booth": 2, "gate_3_moat_infrastructure": 0, "gate_3_moat_scale_shared": 0, "gate_3_moat_rd": 0,
                    "gate_3b_pricing_and_proof": "Y", "gate_3m_moat_note": "Moat",
                    "gate_4_force_entrants": 0, "gate_4_force_rivalry": 1, "gate_4_force_buyers": 0, "gate_4_force_suppliers": 0, "gate_4_force_substitution": 0,
                    "gate_4n_runway_note": "",
                    "gate_5_management_score": 1, "gate_6_cash_and_balance_sheet": "Y",
                    "note": "Note", "evidence": "Ev",
                },
            }
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(bad_payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_legacy_alias_normalized_with_warning(self):
        payload = {"qualitative": {"gate_1": "Y", "gate_2": "Y", "gate_3a_moat_archetype": "Toll booth / Switching costs", "gate_3b_pricing_and_proof": "Y", "gate_4_runway_cap": 25, "gate_5_management_score": 1, "gate_6_cash_and_balance_sheet": "Y"}}
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["3a"], "Toll booth & switching costs")
        self.assertEqual(qual["4"], 25)
        self.assertTrue(any("Normalized legacy Gate 3a" in w for w in warnings))


class UniverseDataAndDashboardAuditTests(unittest.TestCase):
    def test_all_universe_3a_labels_are_canonical(self):
        for u in universe_keys():
            meta = load_universe(u)
            for c in meta["companies"]:
                v3a = c.get("3a")
                if v3a is not None:
                    self.assertIn(v3a, C.MOAT_TYPES, msg=f"{u}:{c['id']} has non-canonical 3a={v3a!r}")

    def test_pilot_reference_companies_and_asml_mirror_parity(self):
        expected = {
            ("us", "SPGI"): (30, 30, False),
            ("us", "COST"): (30, 30, False),
            ("eu", "ASML.NL"): (30, 25, False),
            ("us", "ASML"): (30, 25, False),
            ("us", "MSFT"): (30, 25, False),
            ("us", "WM"): (25, 25, False),
            ("eu", "RMS.FR"): (25, 25, False),
            ("ca", "CNR.CA"): (25, 20, False),
            ("us", "HSY"): (20, 15, False),
            ("us", "CRM"): (20, 5, True),
        }
        loaded = {u: {c["id"]: c for c in load_universe(u)["companies"]} for u in universe_keys()}
        for (u, cid), (exp_init, exp_final, exp_fatal) in expected.items():
            row = loaded[u][cid]
            aud = cap_audit(row)
            self.assertTrue(aud["audited"], msg=f"{cid} should be fully CAP-audited")
            self.assertEqual(aud["cap_init"], exp_init, msg=f"{cid} cap_init mismatch")
            self.assertEqual(aud["cap_final"], exp_final, msg=f"{cid} cap_final mismatch")
            self.assertEqual(row.get("4"), exp_final, msg=f"{cid} stored 4 mismatch")
            self.assertEqual(aud["fatal_flaw"], exp_fatal, msg=f"{cid} fatal_flaw mismatch")

        # NUE Gate 3 rejection check
        nue_aud = cap_audit(loaded["us"]["NUE"])
        self.assertTrue(nue_aud["moat_complete"])
        self.assertEqual(nue_aud["cap_init"], 0)
        self.assertEqual(nue_aud["primary_moat"], "None")

        # ASML <-> ASML.NL qualitative sub-score parity
        for k in (*C.MOAT_SCORE_CODES, "3a", "3b", *C.FORCE_SCORE_CODES, "4", "4n"):
            self.assertEqual(loaded["us"]["ASML"].get(k), loaded["eu"]["ASML.NL"].get(k), msg=f"ASML mirror mismatch on {k}")

    def test_dashboard_exports_and_renders_cap_audit(self):
        data = collect_screener_data(["us"])
        by_id = {c["id"]: c for c in data["companies"]}
        msft = by_id["MSFT"]
        self.assertTrue(msft["cap_audited"])
        self.assertEqual(msft["cap_init"], 30)
        self.assertEqual(msft["cap_haircut"], 5)
        self.assertEqual(msft["g4_cap"], 25)
        html = build_dashboard_html(data)
        self.assertIn("renderCapBreakdownHtml", html)
        self.assertIn("dossier-cap-scorecard", html)
        self.assertIn("audit-cap-derivation", html)


if __name__ == "__main__":
    unittest.main()
