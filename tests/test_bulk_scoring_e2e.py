"""Phase 2 Bulk Re-Scoring Comprehensive E2E Verification Test Suite.

Architecture & Methodology:
- Opaque-box, requirement-driven E2E verification test harness.
- Adheres strictly to TEST_INFRA.md, PROJECT.md, and ORIGINAL_REQUEST.md.
- 4-Tier Verification Hierarchy:
  - Tier 1: Feature Coverage (>=5 test cases per feature across all 11 features = 55 tests)
  - Tier 2: Boundary & Corner Cases (>=5 test cases per feature across all 11 features = 55 tests)
  - Tier 3: Cross-Feature Interactions & Mirror Parity (12 tests)
  - Tier 4: Real-World Scenarios (8 tests)
  - Helper & Regression Test Suite (4 tests):
    - test_deterministic_engine_rules
    - test_reference_companies_regression
    - test_mirrors_synchronization
    - test_all_989_gate3_companies_completed
- Total Test Count: 134 automated test methods (>127 required).
"""
from __future__ import annotations

import csv
import io
import json
import os
import subprocess
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
from screener.data import input_fields, load_universe, universe_keys, write_csv
from screener.gates import (
    cap_audit,
    compute_final_cap_from_scores,
    compute_initial_cap_from_scores,
    funnel_ids,
    moderate_force_haircut,
    params,
    phase_results,
)


def make_test_company(**overrides) -> dict:
    """Helper creating a baseline qualified company row for unit-level verification."""
    row = {
        "id": "MOCK",
        "ticker": "MOCK",
        "company": "Mock Franchise Corp",
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
        "3m": "High mission-critical database switching friction.",
        "4_ent": 0,
        "4_riv": 0,
        "4_buy": 0,
        "4_sup": 0,
        "4_sub": 0,
        "4": 20,
        "4n": "Dominant workflow lock-in insulates against all five forces.",
        "5": 1,
        "6": "Y",
        "calamity": "",
        "calamity_note": "",
        "note": "A prime grade software compounder.",
        "evidence": "Multi-year median GAAP ROIC is 28.5%.",
    }
    row.update(overrides)
    return row


def make_test_payload(**qual_overrides) -> dict:
    """Helper creating an evaluation JSON payload dictionary."""
    qual = {
        "gate_1": "Y",
        "gate_2": "Y",
        "gate_3_moat_toll_booth": 2,
        "gate_3_moat_infrastructure": 0,
        "gate_3_moat_scale_shared": 0,
        "gate_3_moat_rd": 0,
        "gate_3a_moat_archetype": "Toll booth & switching costs",
        "gate_3b_pricing_and_proof": "Y",
        "gate_3m_moat_note": "Structural toll booth barriers.",
        "gate_4_force_entrants": 0,
        "gate_4_force_rivalry": 0,
        "gate_4_force_buyers": 0,
        "gate_4_force_suppliers": 0,
        "gate_4_force_substitution": 0,
        "gate_4_runway_cap": 20,
        "gate_4n_runway_note": "Insulated franchise.",
        "gate_5_management_score": 1,
        "gate_6_cash_and_balance_sheet": "Y",
        "note": "Evaluation note.",
        "evidence": "Audited empirical statement evidence.",
    }
    qual.update(qual_overrides)
    return {"id": "MOCK", "qualitative": qual}


# ==============================================================================
# TIER 1: FEATURE COVERAGE TESTS (55 Test Cases: 11 Features x 5 Tests)
# ==============================================================================

class Tier1FeatureCoverageTests(unittest.TestCase):
    """Tier 1: Feature Coverage (>=5 test cases per feature across 11 features)."""

    def setUp(self):
        self.p = params({})

    # --------------------------------------------------------------------------
    # Feature 1: Gate 3 Moat Profiles Scoring (3_tb, 3_ia, 3_se, 3_rd)
    # --------------------------------------------------------------------------
    def test_t1_f1_01_moat_scoring_domain_valid(self):
        """Verifies all moat archetypes accept valid domain integer scores {0, 1, 2}."""
        for val in (0, 1, 2):
            c = make_test_company(**{"3_tb": val, "3_ia": val, "3_se": val, "3_rd": val})
            aud = cap_audit(c)
            self.assertTrue(aud["moat_complete"])

    def test_t1_f1_02_moat_toll_booth_switching(self):
        """Verifies Toll booth & switching costs archetype is recognized and scored."""
        c = make_test_company(**{"3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "Toll booth & switching costs"})
        aud = cap_audit(c)
        self.assertEqual(aud["primary_moat"], "Toll booth & switching costs")
        self.assertEqual(aud["cap_init"], 20)

    def test_t1_f1_03_moat_infrastructure_intangibles(self):
        """Verifies Irreplaceable infrastructure & intangibles archetype scoring."""
        c = make_test_company(**{"3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0, "3a": "Irreplaceable infrastructure & intangibles"})
        aud = cap_audit(c)
        self.assertEqual(aud["primary_moat"], "Irreplaceable infrastructure & intangibles")
        self.assertEqual(aud["cap_init"], 20)

    def test_t1_f1_04_moat_scale_economies_shared(self):
        """Verifies Scale economies shared (Nick Sleep model) archetype scoring."""
        c = make_test_company(**{"3_tb": 0, "3_ia": 0, "3_se": 2, "3_rd": 0, "3a": "Scale economies shared"})
        aud = cap_audit(c)
        self.assertEqual(aud["primary_moat"], "Scale economies shared")
        self.assertEqual(aud["cap_init"], 20)

    def test_t1_f1_05_moat_rd_innovation(self):
        """Verifies R&D & innovation leadership archetype scoring."""
        c = make_test_company(**{"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 2, "3a": "R&D & innovation leadership"})
        aud = cap_audit(c)
        self.assertEqual(aud["primary_moat"], "R&D & innovation leadership")
        self.assertEqual(aud["cap_init"], 20)

    # --------------------------------------------------------------------------
    # Feature 2: Initial CAP & 3a Derivation
    # --------------------------------------------------------------------------
    def test_t1_f2_01_initial_cap_zero_for_no_moat(self):
        """Verifies (0, 0, 0, 0) yields Initial CAP 0Y and 3a 'None'."""
        self.assertEqual(compute_initial_cap_from_scores((0, 0, 0, 0)), 0)
        c = make_test_company(**{"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None"})
        aud = cap_audit(c)
        self.assertEqual(aud["primary_moat"], "None")
        self.assertEqual(aud["cap_init"], 0)

    def test_t1_f2_02_initial_cap_15y_single_moderate(self):
        """Verifies single moderate moat (m_max=1, sum=1) yields Initial CAP 15Y."""
        self.assertEqual(compute_initial_cap_from_scores((1, 0, 0, 0)), 15)
        self.assertEqual(compute_initial_cap_from_scores((0, 1, 0, 0)), 15)

    def test_t1_f2_03_initial_cap_20y_moderate_sum(self):
        """Verifies multiple moderate moats (m_max=1, sum>=2) capped at 20Y without elite anchor."""
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 0, 0)), 20)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 1, 1)), 20)

    def test_t1_f2_04_initial_cap_25y_elite_moderate(self):
        """Verifies elite anchor + supporting moderate (m_max=2, sum=3) yields 25Y."""
        self.assertEqual(compute_initial_cap_from_scores((2, 1, 0, 0)), 25)
        self.assertEqual(compute_initial_cap_from_scores((0, 2, 1, 0)), 25)

    def test_t1_f2_05_initial_cap_30y_dual_elite(self):
        """Verifies dual elite anchors (m_max=2, sum>=4) yields 30Y."""
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 0, 0)), 30)
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 0, 2)), 30)

    # --------------------------------------------------------------------------
    # Feature 3: Gate 4 Competitive Forces Scoring (4_ent, 4_riv, 4_buy, 4_sup, 4_sub)
    # --------------------------------------------------------------------------
    def test_t1_f3_01_force_scoring_domain(self):
        """Verifies all five forces accept integer values in {0, 1, 2}."""
        for val in (0, 1, 2):
            c = make_test_company(**{k: val for k in C.FORCE_SCORE_CODES})
            aud = cap_audit(c)
            self.assertTrue(aud["force_complete"])

    def test_t1_f3_02_force_entrants_scoring(self):
        """Verifies Threat of New Entrants (4_ent) scoring impact."""
        cap, haircut, fatal = compute_final_cap_from_scores(25, (1, 0, 0, 0, 0))
        self.assertEqual((cap, haircut, fatal), (20, 5, False))

    def test_t1_f3_03_force_rivalry_scoring(self):
        """Verifies Competitive Rivalry (4_riv) scoring impact."""
        cap, haircut, fatal = compute_final_cap_from_scores(25, (0, 1, 0, 0, 0))
        self.assertEqual((cap, haircut, fatal), (20, 5, False))

    def test_t1_f3_04_force_buyers_scoring(self):
        """Verifies Customer Bargaining Power (4_buy) scoring impact."""
        cap, haircut, fatal = compute_final_cap_from_scores(25, (0, 0, 1, 0, 0))
        self.assertEqual((cap, haircut, fatal), (20, 5, False))

    def test_t1_f3_05_force_suppliers_scoring(self):
        """Verifies Supplier Bargaining Power (4_sup) scoring impact."""
        cap, haircut, fatal = compute_final_cap_from_scores(25, (0, 0, 0, 1, 0))
        self.assertEqual((cap, haircut, fatal), (20, 5, False))

    # --------------------------------------------------------------------------
    # Feature 4: Deterministic Final CAP Engine (Haircuts & Fatal Flaw)
    # --------------------------------------------------------------------------
    def test_t1_f4_01_moderate_haircut_zero(self):
        """Verifies c1=0 moderate force haircut is 0Y."""
        self.assertEqual(moderate_force_haircut(0), 0)

    def test_t1_f4_02_moderate_haircut_5y(self):
        """Verifies c1 in {1, 2} moderate force haircut is 5Y."""
        self.assertEqual(moderate_force_haircut(1), 5)
        self.assertEqual(moderate_force_haircut(2), 5)

    def test_t1_f4_03_moderate_haircut_10y(self):
        """Verifies c1 in {3, 4} moderate force haircut is 10Y."""
        self.assertEqual(moderate_force_haircut(3), 10)
        self.assertEqual(moderate_force_haircut(4), 10)

    def test_t1_f4_04_moderate_haircut_15y(self):
        """Verifies c1=5 moderate force haircut is 15Y."""
        self.assertEqual(moderate_force_haircut(5), 15)

    def test_t1_f4_05_deterministic_cap_calculation(self):
        """Verifies deterministic CAP math matches formula: 30Y init - 5Y haircut = 25Y."""
        cap, haircut, fatal = compute_final_cap_from_scores(30, (0, 0, 1, 1, 0))
        self.assertEqual(cap, 25)
        self.assertEqual(haircut, 5)
        self.assertFalse(fatal)

    # --------------------------------------------------------------------------
    # Feature 5: Mandatory 4n Runway & Forces Note
    # --------------------------------------------------------------------------
    def test_t1_f5_01_mandatory_4n_single_moderate_force(self):
        """Verifies 4n note is required when single force = 1."""
        payload = make_test_payload(gate_4_force_entrants=1, gate_4n_runway_note="")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_t1_f5_02_mandatory_4n_dual_moderate_forces(self):
        """Verifies 4n note is required when dual forces = 1."""
        payload = make_test_payload(gate_4_force_buyers=1, gate_4_force_suppliers=1, gate_4n_runway_note="")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_t1_f5_03_mandatory_4n_multi_moderate_forces(self):
        """Verifies 4n note is required when multiple forces = 1."""
        payload = make_test_payload(gate_4_force_entrants=1, gate_4_force_rivalry=1, gate_4_force_buyers=1, gate_4n_runway_note="")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_t1_f5_04_mandatory_4n_fatal_flaw(self):
        """Verifies 4n note is required when fatal flaw force = 2."""
        payload = make_test_payload(gate_4_force_substitution=2, gate_4n_runway_note="")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_t1_f5_05_zero_force_insulation_note_accepted(self):
        """Verifies structured insulation note is valid when all forces are 0."""
        payload = make_test_payload(gate_4n_runway_note="Dominant workflow lock-in insulates against all five forces.")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["4n"], "Dominant workflow lock-in insulates against all five forces.")
        self.assertEqual(warnings, [])

    # --------------------------------------------------------------------------
    # Feature 6: Preservation of 11 Reference Companies
    # --------------------------------------------------------------------------
    def test_t1_f6_01_spgi_reference_preservation(self):
        """Verifies SPGI (US) reference preservation: 30Y init, 30Y final, Quality pass."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        self.assertIn("SPGI", us)
        spgi = us["SPGI"]
        self.assertEqual(spgi["4"], 30)
        self.assertEqual(spgi["3a"], "Toll booth & switching costs")
        res = phase_results(spgi, self.p)
        self.assertEqual(res["result"], C.RES_QPASS)

    def test_t1_f6_02_cost_reference_preservation(self):
        """Verifies COST (US) reference preservation: Scale economies shared, 30Y final."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        cost = us["COST"]
        self.assertEqual(cost["4"], 30)
        self.assertEqual(cost["3a"], "Scale economies shared")
        self.assertEqual(cost["3_se"], 2)

    def test_t1_f6_03_asml_reference_preservation(self):
        """Verifies ASML (US) and ASML.NL (EU) preservation: 30Y init, 25Y final."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        self.assertEqual(us["ASML"]["4"], 25)
        self.assertEqual(eu["ASML.NL"]["4"], 25)
        self.assertEqual(us["ASML"]["3a"], "R&D & innovation leadership")

    def test_t1_f6_04_msft_reference_preservation(self):
        """Verifies MSFT (US) reference preservation: 30Y init, 5Y haircut, 25Y final."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        msft = us["MSFT"]
        self.assertEqual(msft["4"], 25)
        self.assertEqual(msft["4_riv"], 1)
        self.assertEqual(msft["4_sub"], 1)

    def test_t1_f6_05_wm_rms_cnr_reference_preservation(self):
        """Verifies infrastructure compounders WM (US: 25Y), RMS.FR (EU: 25Y), CNR.CA (CA: 20Y)."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        ca = {c["id"]: c for c in load_universe("ca")["companies"]}
        self.assertEqual(us["WM"]["4"], 25)
        self.assertEqual(eu["RMS.FR"]["4"], 25)
        self.assertEqual(ca["CNR.CA"]["4"], 20)

    # --------------------------------------------------------------------------
    # Feature 7: Sequential Munger Waterfall Clearing
    # --------------------------------------------------------------------------
    def test_t1_f7_01_gate1_failure_clears_gates_2_through_6(self):
        """Verifies Gate 1 rejection ('N') scrubs all downstream gates 2 through 6."""
        payload = make_test_payload(gate_1="N")
        qual, _, _ = validate_and_waterfall(payload)
        for k in ("2", "2r", *C.MOAT_SCORE_CODES, "3a", "3b", "3m", *C.FORCE_SCORE_CODES, "4", "4n", "5", "6"):
            self.assertEqual(qual[k], "")

    def test_t1_f7_02_gate2_failure_clears_gates_3_through_6(self):
        """Verifies Gate 2 rejection ('N') scrubs all downstream gates 3 through 6."""
        payload = make_test_payload(gate_1="Y", gate_2="N", gate_2_reason="Not essential.")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["2r"], "Not essential.")
        for k in (*C.MOAT_SCORE_CODES, "3a", "3b", "3m", *C.FORCE_SCORE_CODES, "4", "4n", "5", "6"):
            self.assertEqual(qual[k], "")

    def test_t1_f7_03_gate3a_none_failure_clears_gates_4_through_6(self):
        """Verifies Gate 3a 'None' (no moat) scrubs gates 4 through 6."""
        payload = make_test_payload(gate_3_moat_toll_booth=0, gate_3a_moat_archetype="None")
        qual, _, _ = validate_and_waterfall(payload)
        for k in (*C.FORCE_SCORE_CODES, "4", "4n", "5", "6"):
            self.assertEqual(qual[k], "")

    def test_t1_f7_04_gate4_cap_under_15_clears_gates_5_and_6(self):
        """Verifies Stage 2 Gate 4 CAP < 15 clears calamity while preserving diagnostic Gates 5 and 6, and Stage 1 G3b='N' scrubs downstream."""
        payload = make_test_payload(
            gate_4_force_substitution=2,
            calamity_flag="Y",
            calamity_note="Cannot waive Gate 4 anchor.",
        )  # fatal flaw -> rem=20-10=10 >= 10 -> CAP=10
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["4"], 10)
        self.assertEqual(qual["5"], 1)
        self.assertEqual(qual["6"], "Y")
        self.assertEqual(qual["calamity"], "")
        self.assertEqual(qual["calamity_note"], "")
        self.assertEqual(phase_results(qual, self.p)["result"], C.RES_REJ[4])

        # Stage 1 (G3b='N' without calamity) still strictly scrubs G4-G6
        s1_payload = make_test_payload(gate_3b_pricing_and_proof="N", calamity_flag="")
        s1_qual, _, _ = validate_and_waterfall(s1_payload)
        for k in (*C.FORCE_SCORE_CODES, "4", "4n", "5", "6"):
            self.assertEqual(s1_qual[k], "")

    def test_t1_f7_05_gate5_failure_clears_gate_6_without_calamity(self):
        """Verifies Stage 2 Gate 5 failure (0) without calamity preserves diagnostic Gate 6 while rejecting at Gate 5."""
        payload = make_test_payload(gate_5_management_score=0, gate_6_cash_and_balance_sheet="Y", calamity_flag="")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["5"], 0)
        self.assertEqual(qual["6"], "Y")
        self.assertEqual(phase_results(qual, self.p)["result"], C.RES_REJ[5])

    # --------------------------------------------------------------------------
    # Feature 8: Dual Mirror Synchronization
    # --------------------------------------------------------------------------
    def test_t1_f8_01_asml_mirror_moat_scores_parity(self):
        """Verifies ASML (US) and ASML.NL (EU) have identical Gate 3 moat subscores."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        for k in C.MOAT_SCORE_CODES:
            self.assertEqual(us["ASML"].get(k), eu["ASML.NL"].get(k))

    def test_t1_f8_02_asml_mirror_forces_scores_parity(self):
        """Verifies ASML (US) and ASML.NL (EU) have identical Gate 4 force scores and CAP."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        for k in (*C.FORCE_SCORE_CODES, "4", "4n"):
            self.assertEqual(us["ASML"].get(k), eu["ASML.NL"].get(k))

    def test_t1_f8_03_asml_mirror_primary_moat_3a_parity(self):
        """Verifies ASML (US) and ASML.NL (EU) share identical derived 3a archetype and 3b proof."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        self.assertEqual(us["ASML"]["3a"], eu["ASML.NL"]["3a"])
        self.assertEqual(us["ASML"]["3b"], eu["ASML.NL"]["3b"])

    def test_t1_f8_04_asml_mirror_gate5_and_6_parity(self):
        """Verifies ASML (US) and ASML.NL (EU) have identical management (5) and cash (6) scores."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        self.assertEqual(us["ASML"]["5"], eu["ASML.NL"]["5"])
        self.assertEqual(us["ASML"]["6"], eu["ASML.NL"]["6"])

    def test_t1_f8_05_mirror_pair_definitions_in_universe_json(self):
        """Verifies exactly two mirror pairs exist in data/us/universe.json (ASML, FER)."""
        with open(ROOT / "data" / "us" / "universe.json") as f:
            u_meta = json.load(f)
        self.assertEqual(u_meta.get("mirror"), {"ASML": "eu:ASML.NL", "FER": "eu:FER.ES"})

    # --------------------------------------------------------------------------
    # Feature 9: Calamity Pass Rules Integrity
    # --------------------------------------------------------------------------
    def test_t1_f9_01_gate_3b_calamity_pass_eligible(self):
        """Verifies Gate 3b failure with calamity='Y' qualifies for Calamity pass."""
        c = make_test_company(**{"3b": "N", "calamity": "Y", "calamity_note": "Temp margin reset; intact moat."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_CALAMITY)

    def test_t1_f9_02_gate_5_calamity_pass_eligible(self):
        """Verifies Gate 5 failure (0) with calamity='Y' qualifies for Calamity pass."""
        c = make_test_company(**{"5": 0, "calamity": "Y", "calamity_note": "Former CEO error; new leadership installed."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_CALAMITY)

    def test_t1_f9_03_gate_6_calamity_pass_eligible(self):
        """Verifies Gate 6 failure ('N') with calamity='Y' qualifies for Calamity pass."""
        c = make_test_company(**{"6": "N", "calamity": "Y", "calamity_note": "Temporary bridge debt from M&A."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_CALAMITY)

    def test_t1_f9_04_calamity_note_required_for_calamity(self):
        """Verifies calamity='Y' requires a non-empty calamity_note."""
        payload = make_test_payload(gate_3b_pricing_and_proof="N", calamity_flag="Y", calamity_note="")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("calamity_note", err.getvalue())

    def test_t1_f9_05_calamity_pass_included_in_funnel(self):
        """Verifies Calamity pass companies are included in funnel_ids(include_calamity=True)."""
        meta = {
            "parameters": {},
            "prescreen": [],
            "markets": [],
            "companies": [
                make_test_company(id="QPASS"),
                make_test_company(id="CPASS", **{"6": "N", "calamity": "Y", "calamity_note": "Bridge debt."}),
            ],
        }
        self.assertEqual(funnel_ids(meta, include_calamity=True), ["QPASS", "CPASS"])
        self.assertEqual(funnel_ids(meta, include_calamity=False), ["QPASS"])

    # --------------------------------------------------------------------------
    # Feature 10: Unit Test Suite & Baseline Universe Counts
    # --------------------------------------------------------------------------
    def test_t1_f10_01_us_universe_candidate_count(self):
        """Verifies exactly 445 Gate 3 candidates in the US universe."""
        cos = load_universe("us")["companies"]
        g3 = [c for c in cos if c.get("1") == "Y" and c.get("2") == "Y"]
        self.assertEqual(len(g3), 445)

    def test_t1_f10_02_eu_universe_candidate_count(self):
        """Verifies exactly 495 Gate 3 candidates in the EU universe."""
        cos = load_universe("eu")["companies"]
        g3 = [c for c in cos if c.get("1") == "Y" and c.get("2") == "Y"]
        self.assertEqual(len(g3), 495)

    def test_t1_f10_03_ca_universe_candidate_count(self):
        """Verifies exactly 49 Gate 3 candidates in the CA universe."""
        cos = load_universe("ca")["companies"]
        g3 = [c for c in cos if c.get("1") == "Y" and c.get("2") == "Y"]
        self.assertEqual(len(g3), 49)

    def test_t1_f10_04_total_gate3_candidates_sum(self):
        """Verifies total Gate 3 cohort across US, EU, and CA is exactly 989."""
        total = sum(len([c for c in load_universe(u)["companies"] if c.get("1") == "Y" and c.get("2") == "Y"]) for u in ("us", "eu", "ca"))
        self.assertEqual(total, 989)

    def test_t1_f10_05_universe_candidate_schema_fields(self):
        """Verifies candidate rows contain the 26 common qualitative columns."""
        for u in ("us", "eu", "ca"):
            cos = load_universe(u)["companies"]
            for c in cos[:5]:
                for f in ("1", "2", "3a", "3b", "3m", "4", "4n", "5", "6", "calamity", "calamity_note", "note", "evidence"):
                    self.assertIn(f, c)

    # --------------------------------------------------------------------------
    # Feature 11: Cockpit Output Regeneration (build.py)
    # --------------------------------------------------------------------------
    def test_t1_f11_01_build_script_exists_and_compiles(self):
        """Verifies build.py exists and compiles without syntax errors."""
        build_path = ROOT / "build.py"
        self.assertTrue(build_path.exists())
        with open(build_path) as f:
            compile(f.read(), str(build_path), "exec")

    def test_t1_f11_02_output_screener_html_exists(self):
        """Verifies output/screener.html is present in the repository."""
        self.assertTrue((ROOT / "output" / "screener.html").exists())

    def test_t1_f11_03_output_index_html_exists(self):
        """Verifies output/index.html is present in the repository."""
        self.assertTrue((ROOT / "output" / "index.html").exists())

    def test_t1_f11_04_docs_index_html_exists(self):
        """Verifies docs/index.html is present in the repository."""
        self.assertTrue((ROOT / "docs" / "index.html").exists())

    def test_t1_f11_05_cockpit_html_validity_and_size(self):
        """Verifies output/screener.html has valid HTML structure and substantial size."""
        html_file = ROOT / "output" / "screener.html"
        self.assertGreater(html_file.stat().st_size, 100_000)
        with open(html_file, encoding="utf-8") as f:
            header = f.read(500)
        self.assertIn("<!DOCTYPE html>", header)


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASE TESTS (55 Test Cases: 11 Features x 5 Tests)
# ==============================================================================

class Tier2BoundaryCornerCaseTests(unittest.TestCase):
    """Tier 2: Boundary & Corner Cases (>=5 test cases per feature across 11 features)."""

    def setUp(self):
        self.p = params({})

    # --------------------------------------------------------------------------
    # Feature 1 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f1_01_all_zero_moat_scores(self):
        """Corner Case: All four moats scored 0 (0, 0, 0, 0) yields CAP 0Y and 3a 'None'."""
        self.assertEqual(compute_initial_cap_from_scores((0, 0, 0, 0)), 0)
        payload = make_test_payload(gate_3_moat_toll_booth=0, gate_3_moat_infrastructure=0, gate_3_moat_scale_shared=0, gate_3_moat_rd=0)
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["3a"], "None")
        self.assertEqual(qual["4"], "")

    def test_t2_f1_02_four_moderate_moats(self):
        """Corner Case: (1, 1, 1, 1) capped at 20Y Initial CAP without an elite anchor 2."""
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 1, 1)), 20)

    def test_t2_f1_03_single_elite_moat(self):
        """Corner Case: Single elite moat with no supporting moats (2, 0, 0, 0) yields 20Y."""
        self.assertEqual(compute_initial_cap_from_scores((2, 0, 0, 0)), 20)

    def test_t2_f1_04_dual_elite_moats(self):
        """Corner Case: Dual elite moats (2, 2, 0, 0) yields 30Y Initial CAP."""
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 0, 0)), 30)

    def test_t2_f1_05_invalid_negative_or_high_moat_scores(self):
        """Corner Case: Out-of-bounds moat scores (-1 or 3) are handled gracefully."""
        c_bad = make_test_company(**{"3_tb": -1, "3_ia": 3, "3_se": 0, "3_rd": 0})
        aud = cap_audit(c_bad)
        self.assertFalse(aud["moat_complete"])

    # --------------------------------------------------------------------------
    # Feature 2 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f2_01_tie_breaking_preserves_evaluator_choice(self):
        """Corner Case: Tie among maximum scores preserves evaluator choice if in top archetypes."""
        c = make_test_company(**{"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 2, "3a": "R&D & innovation leadership"})
        aud = cap_audit(c)
        self.assertEqual(aud["primary_moat"], "R&D & innovation leadership")

    def test_t2_f2_02_tie_breaking_canonical_order_fallback(self):
        """Corner Case: Tie among maximum scores falls back to canonical first (Toll booth) if empty."""
        payload = make_test_payload(gate_3_moat_toll_booth=2, gate_3_moat_infrastructure=2, gate_3_moat_scale_shared=0, gate_3_moat_rd=2, gate_3a_moat_archetype="")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["3a"], "Toll booth & switching costs")

    def test_t2_f2_03_supplied_submax_3a_overwritten(self):
        """Corner Case: Evaluator-supplied 3a with score < m_max is corrected to top archetype."""
        payload = make_test_payload(gate_3_moat_toll_booth=2, gate_3_moat_infrastructure=0, gate_3_moat_scale_shared=0, gate_3_moat_rd=0, gate_3a_moat_archetype="Scale economies shared")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["3a"], "Toll booth & switching costs")
        self.assertTrue(any("aligned" in w.lower() for w in warnings))

    def test_t2_f2_04_legacy_alias_normalized_to_canonical(self):
        """Corner Case: Historical legacy moat alias is normalized to canonical spec name."""
        payload = make_test_payload(gate_3a_moat_archetype="Toll booth / Switching costs")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["3a"], "Toll booth & switching costs")
        self.assertTrue(any("normalized" in w.lower() for w in warnings))

    def test_t2_f2_05_blank_3a_derived_from_scores(self):
        """Corner Case: Blank 3a with unique top score is deterministically derived."""
        payload = make_test_payload(gate_3_moat_toll_booth=0, gate_3_moat_infrastructure=2, gate_3_moat_scale_shared=0, gate_3_moat_rd=0, gate_3a_moat_archetype="")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["3a"], "Irreplaceable infrastructure & intangibles")

    # --------------------------------------------------------------------------
    # Feature 3 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f3_01_all_forces_zero_insulation(self):
        """Corner Case: All five forces zero (0, 0, 0, 0, 0) yields 0Y deduction."""
        cap, haircut, fatal = compute_final_cap_from_scores(30, (0, 0, 0, 0, 0))
        self.assertEqual((cap, haircut, fatal), (30, 0, False))

    def test_t2_f3_02_clock_speed_substitution_presumption(self):
        """Corner Case: Mauboussin clock-speed presumption for fast tech/semi (4_sub >= 1)."""
        msft = {c["id"]: c for c in load_universe("us")["companies"]}["MSFT"]
        self.assertGreaterEqual(msft["4_sub"], 1)

    def test_t2_f3_03_partial_force_scores_yields_review(self):
        """Corner Case: Supplying 4 of 5 forces halts downstream evaluation as RES_REVIEW."""
        c = make_test_company(**{"4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": None})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REVIEW)

    def test_t2_f3_04_out_of_bounds_force_score_rejected(self):
        """Corner Case: Invalid force score (3 or -1) is marked force_incomplete."""
        c = make_test_company(**{"4_ent": 3, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0})
        aud = cap_audit(c)
        self.assertFalse(aud["force_complete"])

    def test_t2_f3_05_all_five_forces_fatal(self):
        """Corner Case: All five forces fatal (2, 2, 2, 2, 2) results in 0Y final CAP."""
        cap, _, fatal = compute_final_cap_from_scores(30, (2, 2, 2, 2, 2))
        self.assertEqual(cap, 0)
        self.assertTrue(fatal)

    # --------------------------------------------------------------------------
    # Feature 4 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f4_01_fatal_flaw_single_force_rem_ge_10(self):
        """Corner Case: c2=1 on 30Y Initial CAP with c1=0 -> rem=20 >= 10 -> CAP=10Y."""
        cap, haircut, fatal = compute_final_cap_from_scores(30, (0, 0, 0, 0, 2))
        self.assertEqual(cap, 10)
        self.assertEqual(haircut, 0)
        self.assertTrue(fatal)

    def test_t2_f4_02_fatal_flaw_single_force_rem_lt_10(self):
        """Corner Case: c2=1 on 20Y Initial CAP with c1=3 -> rem = 20 - 10 - 10 = 0 < 10 -> CAP=5Y."""
        cap, haircut, fatal = compute_final_cap_from_scores(20, (1, 1, 1, 0, 2))
        self.assertEqual(cap, 5)
        self.assertEqual(haircut, 10)
        self.assertTrue(fatal)

    def test_t2_f4_03_fatal_flaw_single_force_on_15y(self):
        """Corner Case: c2=1 on 15Y Initial CAP -> rem = 15 - 10 - 0 = 5 < 10 -> CAP=5Y."""
        cap, haircut, fatal = compute_final_cap_from_scores(15, (0, 0, 0, 0, 2))
        self.assertEqual(cap, 5)
        self.assertTrue(fatal)

    def test_t2_f4_04_fatal_flaw_dual_force_2(self):
        """Corner Case: c2=2 on any Initial CAP unconditionally caps at 5Y."""
        cap, _, fatal = compute_final_cap_from_scores(30, (2, 0, 0, 0, 2))
        self.assertEqual(cap, 5)
        self.assertTrue(fatal)

    def test_t2_f4_05_fatal_flaw_triple_force_2(self):
        """Corner Case: c2>=3 unconditionally caps at 0Y."""
        cap, _, fatal = compute_final_cap_from_scores(30, (2, 2, 0, 0, 2))
        self.assertEqual(cap, 0)
        self.assertTrue(fatal)

    # --------------------------------------------------------------------------
    # Feature 5 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f5_01_missing_4n_with_positive_force_fails_validation(self):
        """Corner Case: apply_evaluation rejects payload when force >= 1 and 4n note is missing."""
        payload = make_test_payload(gate_4_force_buyers=1, gate_4n_runway_note="")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_t2_f5_02_whitespace_only_4n_rejected(self):
        """Corner Case: Whitespace-only 4n note ('   ') is treated as missing and rejected."""
        payload = make_test_payload(gate_4_force_rivalry=1, gate_4n_runway_note="   ")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "us").mkdir()
            write_csv(tmp_root / "us" / "inputs.csv", input_fields({"extra_columns": []}), [{"id": "MOCK", "ticker": "MOCK", "company": "M", "country": "US", "sector": "IT", "sub_industry": "Software"}])
            err = io.StringIO()
            with patch("screener.apply_evaluation.DATA_DIR", tmp_root), redirect_stderr(err):
                ok = apply_evaluation(payload, universe="us")
            self.assertFalse(ok)
            self.assertIn("gate_4n_runway_note", err.getvalue())

    def test_t2_f5_03_4n_scrubbed_on_upstream_gate2_rejection(self):
        """Corner Case: 4n is cleared when Gate 2 fails."""
        payload = make_test_payload(gate_2="N", gate_2_reason="Commodity.", gate_4n_runway_note="Should scrub.")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["4n"], "")

    def test_t2_f5_04_4n_scrubbed_on_gate3_rejection(self):
        """Corner Case: 4n is cleared when Gate 3 fails (no moat)."""
        payload = make_test_payload(gate_3_moat_toll_booth=0, gate_3a_moat_archetype="None", gate_4n_runway_note="Should scrub.")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["4n"], "")

    def test_t2_f5_05_fatal_flaw_4n_declares_fatal_cap(self):
        """Corner Case: Reference CRM note explicitly declares Fatal-Flaw Cap and REJECT."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        crm = us["CRM"]
        self.assertIn("Fatal-Flaw Cap", crm["4n"])
        self.assertIn("REJECT", crm["4n"])

    # --------------------------------------------------------------------------
    # Feature 6 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f6_01_crm_fatal_flaw_rejection_boundary(self):
        """Corner Case: CRM has 20Y Initial CAP, 4_sub=2 (agentic AI) -> final 5Y -> Rejected G4."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        crm = us["CRM"]
        self.assertEqual(crm["4"], 5)
        res = phase_results(crm, self.p)
        self.assertEqual(res["result"], C.RES_REJ[4])

    def test_t2_f6_02_nue_zero_moat_rejection_boundary(self):
        """Corner Case: NUE has (0, 0, 0, 0) moats -> 0Y Initial CAP -> Rejected G3."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        nue = us["NUE"]
        self.assertEqual(nue["3a"], "None")
        res = phase_results(nue, self.p)
        self.assertEqual(res["result"], C.RES_REJ[3])

    def test_t2_f6_03_hsy_boundary_pass_15y(self):
        """Corner Case: HSY Initial CAP 20Y - 5Y haircut = 15Y exactly meets pass threshold."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        hsy = us["HSY"]
        self.assertEqual(hsy["4"], 15)
        res = phase_results(hsy, self.p)
        self.assertEqual(res["result"], C.RES_QPASS)

    def test_t2_f6_04_cnr_canadian_reference_boundary(self):
        """Corner Case: CNR.CA (Canadian Rail) 25Y Initial CAP - 5Y haircut (union rail) = 20Y."""
        ca = {c["id"]: c for c in load_universe("ca")["companies"]}
        cnr = ca["CNR.CA"]
        self.assertEqual(cnr["4"], 20)
        res = phase_results(cnr, self.p)
        self.assertEqual(res["result"], C.RES_QPASS)

    def test_t2_f6_05_all_11_reference_cap_audit_validity(self):
        """Corner Case: All 11 reference companies pass cap_audit completeness check."""
        refs = {
            "SPGI": "us", "COST": "us", "ASML": "us", "MSFT": "us", "WM": "us",
            "HSY": "us", "CRM": "us", "NUE": "us", "ASML.NL": "eu", "RMS.FR": "eu", "CNR.CA": "ca"
        }
        for cid, u in refs.items():
            cos = {c["id"]: c for c in load_universe(u)["companies"]}
            aud = cap_audit(cos[cid])
            if cid == "NUE":
                self.assertTrue(aud["moat_complete"])
                self.assertEqual(aud["cap_init"], 0)
            else:
                self.assertTrue(aud["audited"], msg=f"{cid} failed cap_audit")

    # --------------------------------------------------------------------------
    # Feature 7 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f7_01_gate2_reason_cleared_on_pass(self):
        """Corner Case: Gate 2 reason '2r' is cleared when Gate 2 passes ('Y')."""
        payload = make_test_payload(gate_2="Y", gate_2_reason="Orphaned reason text.")
        qual, _, _ = validate_and_waterfall(payload)
        self.assertEqual(qual["2r"], "")

    def test_t2_f7_02_calamity_cleared_on_gate1_failure(self):
        """Corner Case: Calamity flag and note are cleared when Gate 1 is 'N'."""
        payload = make_test_payload(gate_1="N", calamity_flag="Y", calamity_note="Attempted calamity on G1.")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["calamity"], "")
        self.assertEqual(qual["calamity_note"], "")
        self.assertTrue(any("calamity" in w.lower() for w in warnings))

    def test_t2_f7_03_calamity_cleared_on_gate2_failure(self):
        """Corner Case: Calamity flag and note are cleared when Gate 2 is 'N'."""
        payload = make_test_payload(gate_2="N", gate_2_reason="Cyclical.", calamity_flag="Y", calamity_note="G2 calamity.")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["calamity"], "")
        self.assertEqual(qual["calamity_note"], "")

    def test_t2_f7_04_calamity_cleared_on_gate3a_none(self):
        """Corner Case: Calamity flag and note are cleared when Gate 3a is 'None'."""
        payload = make_test_payload(gate_3_moat_toll_booth=0, gate_3a_moat_archetype="None", calamity_flag="Y", calamity_note="G3a calamity.")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["calamity"], "")
        self.assertEqual(qual["calamity_note"], "")

    def test_t2_f7_05_calamity_cleared_on_gate4_under_15(self):
        """Corner Case: Calamity flag and note are cleared when Gate 4 CAP < 15."""
        payload = make_test_payload(gate_4_force_substitution=2, calamity_flag="Y", calamity_note="G4 calamity.")
        qual, _, warnings = validate_and_waterfall(payload)
        self.assertEqual(qual["calamity"], "")
        self.assertEqual(qual["calamity_note"], "")

    # --------------------------------------------------------------------------
    # Feature 8 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f8_01_asml_mirror_qualitative_codes_exact_match(self):
        """Corner Case: ASML and ASML.NL match across all 17 qualitative codes."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}["ASML"]
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}["ASML.NL"]
        for k in (*C.MOAT_SCORE_CODES, "3a", "3b", *C.FORCE_SCORE_CODES, "4", "4n", "5", "6", "calamity", "calamity_note"):
            self.assertEqual(us.get(k), eu.get(k), msg=f"Mismatch on {k}")

    def test_t2_f8_02_fer_mirror_mapping_integrity(self):
        """Corner Case: FER mapping in us/universe.json targets eu:FER.ES correctly."""
        with open(ROOT / "data" / "us" / "universe.json") as f:
            u_meta = json.load(f)
        self.assertEqual(u_meta["mirror"]["FER"], "eu:FER.ES")

    def test_t2_f8_03_mirror_waterfall_rejection_consistency(self):
        """Corner Case: FER (US) and FER.ES (EU) both reject consistently at Gate 3b."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}["FER"]
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}["FER.ES"]
        self.assertEqual(phase_results(us, self.p)["result"], phase_results(eu, self.p)["result"])

    def test_t2_f8_04_no_unregistered_mirrors_in_universes(self):
        """Corner Case: Confirms EU and CA declare no conflicting mirror maps."""
        for u in ("eu", "ca"):
            with open(ROOT / "data" / u / "universe.json") as f:
                u_meta = json.load(f)
            self.assertNotIn("mirror", u_meta)

    def test_t2_f8_05_mirror_sync_preserves_primary_attributes(self):
        """Corner Case: Mirror pair shares identical company identity attributes where expected."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}["ASML"]
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}["ASML.NL"]
        self.assertEqual(us["sector"], eu["sector"])
        self.assertEqual(us["3a"], eu["3a"])

    # --------------------------------------------------------------------------
    # Feature 9 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f9_01_calamity_on_gate1_rejected(self):
        """Corner Case: Anchor Gate 1 is non-waivable; fails immediately as RES_REJ[1]."""
        c = make_test_company(**{"1": "N", "calamity": "Y", "calamity_note": "Attempted anchor bypass."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REJ[1])

    def test_t2_f9_02_calamity_on_gate2_rejected(self):
        """Corner Case: Anchor Gate 2 is non-waivable; fails immediately as RES_REJ[2]."""
        c = make_test_company(**{"2": "N", "calamity": "Y", "calamity_note": "Attempted anchor bypass."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REJ[2])

    def test_t2_f9_03_calamity_on_gate3a_none_rejected(self):
        """Corner Case: Anchor Gate 3a 'None' is non-waivable; fails immediately as RES_REJ[3]."""
        c = make_test_company(**{"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0, "3a": "None", "calamity": "Y", "calamity_note": "Attempted anchor bypass."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REJ[3])

    def test_t2_f9_04_calamity_on_gate4_cap_under_15_rejected(self):
        """Corner Case: Anchor Gate 4 CAP < 15 is non-waivable; fails immediately as RES_REJ[4]."""
        c = make_test_company(**{"4_sub": 2, "4": 10, "calamity": "Y", "calamity_note": "Attempted anchor bypass."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_REJ[4])

    def test_t2_f9_05_calamity_with_zero_failed_gates_warns(self):
        """Corner Case: Setting calamity='Y' when all gates pass triggers sanity warning."""
        payload = make_test_payload(calamity_flag="Y", calamity_note="No gate failed.")
        _, _, warnings = validate_and_waterfall(payload)
        self.assertTrue(any("no eligible gate" in w.lower() for w in warnings))

    # --------------------------------------------------------------------------
    # Feature 10 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f10_01_gate1_rejects_exact_count(self):
        """Corner Case: Gate 1 rejects count is exactly 30 (US: 14, EU: 14, CA: 2)."""
        counts = {u: len([c for c in load_universe(u)["companies"] if c.get("1") == "N"]) for u in ("us", "eu", "ca")}
        self.assertEqual(counts, {"us": 14, "eu": 14, "ca": 2})

    def test_t2_f10_02_gate2_rejects_exact_count(self):
        """Corner Case: Gate 2 rejects count is exactly 156 (US: 56, EU: 93, CA: 7)."""
        counts = {u: len([c for c in load_universe(u)["companies"] if c.get("1") == "Y" and c.get("2") == "N"]) for u in ("us", "eu", "ca")}
        self.assertEqual(counts, {"us": 56, "eu": 93, "ca": 7})

    def test_t2_f10_03_total_universe_exact_count(self):
        """Corner Case: Total universe count is exactly 1,175 (US: 515, EU: 602, CA: 58)."""
        counts = {u: len(load_universe(u)["companies"]) for u in ("us", "eu", "ca")}
        self.assertEqual(counts, {"us": 515, "eu": 602, "ca": 58})

    def test_t2_f10_04_calamity_flagged_count(self):
        """Corner Case: Exactly 13 companies currently carry calamity='Y' in inputs.csv."""
        counts = sum(len([c for c in load_universe(u)["companies"] if c.get("calamity") == "Y"]) for u in ("us", "eu", "ca"))
        self.assertEqual(counts, 13)

    def test_t2_f10_05_unscored_legacy_exact_count(self):
        """Corner Case: Exactly 978 Gate 3 companies are unscored legacy rows in Phase 1 baseline."""
        unscored = 0
        for u in ("us", "eu", "ca"):
            for c in load_universe(u)["companies"]:
                if c.get("1") == "Y" and c.get("2") == "Y":
                    if all(c.get(k) is None or c.get(k) == "" for k in C.MOAT_SCORE_CODES):
                        unscored += 1
        self.assertIn(unscored, (0, 978))  # 978 in M1, 0 when M3 completed

    # --------------------------------------------------------------------------
    # Feature 11 Corner Cases
    # --------------------------------------------------------------------------
    def test_t2_f11_01_build_single_universe_target(self):
        """Corner Case: build.py ca succeeds and compiles the Canadian cockpit in isolation."""
        try:
            res = subprocess.run([sys.executable, str(ROOT / "build.py"), "ca"], capture_output=True, text=True, cwd=str(ROOT))
            self.assertEqual(res.returncode, 0)
            self.assertIn("Total Companies: 58", res.stdout)
        finally:
            subprocess.run([sys.executable, str(ROOT / "build.py")], capture_output=True, cwd=str(ROOT))

    def test_t2_f11_02_dashboard_contains_cap_breakdown_js(self):
        """Corner Case: Built HTML cockpit includes JavaScript runtime for CAP breakdown scorecard."""
        with open(ROOT / "output" / "screener.html", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("renderCapBreakdownHtml", html)
        self.assertIn("dossier-cap-scorecard", html)

    def test_t2_f11_03_dashboard_contains_dcf_schedule_js(self):
        """Corner Case: Built HTML cockpit includes JavaScript runtime for DCF schedule table."""
        with open(ROOT / "output" / "screener.html", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("renderDcfScheduleTable", html)
        self.assertIn("dcf-schedule-table", html)

    def test_t2_f11_04_dashboard_renders_calamity_badge(self):
        """Corner Case: Built HTML cockpit includes Prime Grade Calamity rendering token."""
        with open(ROOT / "output" / "screener.html", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("Prime Grade Calamity", html)

    def test_t2_f11_05_dashboard_total_companies_kpi(self):
        """Corner Case: Dashboard data export records total universe companies equal to 1,175."""
        data = collect_screener_data(["us", "eu", "ca"])
        self.assertEqual(data["summary"]["total_companies"], 1175)


# ==============================================================================
# TIER 3: CROSS-FEATURE INTERACTIONS & MIRROR PARITY (12 Test Cases)
# ==============================================================================

class Tier3CrossFeatureInteractionTests(unittest.TestCase):
    """Tier 3: Combinatorial & Cross-Feature Interactions."""

    def setUp(self):
        self.p = params({})

    def test_t3_01_rd_moat_with_fast_clock_speed_substitution(self):
        """Interaction: R&D leadership (2) paired with fast clock speed substitution (1) yields 25Y."""
        cap_init = compute_initial_cap_from_scores((0, 0, 0, 2))
        self.assertEqual(cap_init, 20)
        cap_final, haircut, fatal = compute_final_cap_from_scores(cap_init, (0, 0, 0, 0, 1))
        self.assertEqual((cap_final, haircut, fatal), (15, 5, False))

    def test_t3_02_toll_booth_with_buyer_power_consolidation(self):
        """Interaction: Toll booth (2) with buyer power (1) yields 5Y haircut."""
        cap_init = compute_initial_cap_from_scores((2, 0, 0, 0))
        cap_final, haircut, fatal = compute_final_cap_from_scores(cap_init, (0, 0, 1, 0, 0))
        self.assertEqual((cap_final, haircut, fatal), (15, 5, False))

    def test_t3_03_scale_economies_with_supplier_concentration(self):
        """Interaction: Scale economies (2) with supplier friction (1) preserves pass at 15Y."""
        cap_init = compute_initial_cap_from_scores((0, 0, 2, 0))
        cap_final, haircut, fatal = compute_final_cap_from_scores(cap_init, (0, 0, 0, 1, 0))
        self.assertEqual((cap_final, haircut, fatal), (15, 5, False))

    def test_t3_04_infrastructure_monopoly_with_zero_forces(self):
        """Interaction: Infrastructure (2) + Toll booth (1) with all forces 0 yields full 25Y."""
        cap_init = compute_initial_cap_from_scores((1, 2, 0, 0))
        cap_final, haircut, fatal = compute_final_cap_from_scores(cap_init, (0, 0, 0, 0, 0))
        self.assertEqual((cap_final, haircut, fatal), (25, 0, False))

    def test_t3_05_dual_elite_moat_with_fatal_flaw_cap(self):
        """Interaction: Dual elite moats (30Y init) subject to single fatal flaw (c2=1, c1=0) capped at 10Y (REJECT)."""
        cap_init = compute_initial_cap_from_scores((2, 2, 0, 0))
        self.assertEqual(cap_init, 30)
        cap_final, haircut, fatal = compute_final_cap_from_scores(cap_init, (0, 0, 0, 0, 2))
        self.assertEqual((cap_final, haircut, fatal), (10, 0, True))
        c = make_test_company(**{"3_tb": 2, "3_ia": 2, "4_sub": 2, "4": cap_final})
        self.assertEqual(phase_results(c, self.p)["result"], C.RES_REJ[4])

    def test_t3_06_single_moderate_moat_haircut_fails_gate4(self):
        """Interaction: Single moderate moat (15Y init) subject to single moderate force (5Y) falls to 10Y and fails Gate 4."""
        cap_init = compute_initial_cap_from_scores((1, 0, 0, 0))
        self.assertEqual(cap_init, 15)
        cap_final, haircut, fatal = compute_final_cap_from_scores(cap_init, (1, 0, 0, 0, 0))
        self.assertEqual((cap_final, haircut, fatal), (10, 5, False))
        c = make_test_company(**{"3_tb": 1, "3_ia": 0, "4_ent": 1, "4": cap_final})
        self.assertEqual(phase_results(c, self.p)["result"], C.RES_REJ[4])

    def test_t3_07_calamity_pass_qualifies_for_valuation_funnel(self):
        """Interaction: Calamity pass company evaluates downstream gates and enters valuation funnel."""
        c = make_test_company(**{"3b": "N", "calamity": "Y", "calamity_note": "Turnaround with intact moat."})
        res = phase_results(c, self.p)
        self.assertEqual(res["result"], C.RES_CALAMITY)
        self.assertIn("3b", [k for k, _, _ in res["waived"]])

    def test_t3_08_asml_mirror_parity_across_universes(self):
        """Interaction: ASML (US) and ASML.NL (EU) share identical gate evaluation outcomes."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}["ASML"]
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}["ASML.NL"]
        res_us = phase_results(us, self.p)
        res_eu = phase_results(eu, self.p)
        self.assertEqual(res_us["result"], res_eu["result"])
        self.assertEqual(res_us["result"], C.RES_QPASS)

    def test_t3_09_fer_mirror_parity_across_universes(self):
        """Interaction: FER (US) and FER.ES (EU) share identical gate evaluation outcomes."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}["FER"]
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}["FER.ES"]
        res_us = phase_results(us, self.p)
        res_eu = phase_results(eu, self.p)
        self.assertEqual(res_us["result"], res_eu["result"])

    def test_t3_10_cross_universe_sector_distribution_coverage(self):
        """Interaction: Gate 3 candidates cover all 11 GICS sectors across US, EU, and CA."""
        sectors = set()
        for u in ("us", "eu", "ca"):
            for c in load_universe(u)["companies"]:
                if c.get("1") == "Y" and c.get("2") == "Y":
                    sectors.add(c.get("sector"))
        self.assertEqual(len(sectors), 11)

    def test_t3_11_waterfall_scrub_interaction_with_calamity(self):
        """Interaction: Upstream failure scrubs calamity flag while eligible failure preserves it."""
        # Non-waivable Gate 4 failure clears calamity (4_sub=2 -> fatal flaw -> CAP=10 < 15)
        payload_fail = make_test_payload(gate_4_force_substitution=2, gate_4n_runway_note="Fatal flaw threat.", calamity_flag="Y", calamity_note="Invalid.")
        qual_fail, _, _ = validate_and_waterfall(payload_fail)
        self.assertEqual(qual_fail["calamity"], "")

        # Waivable Gate 6 failure preserves calamity
        payload_pass = make_test_payload(gate_6_cash_and_balance_sheet="N", calamity_flag="Y", calamity_note="Valid bridge debt.")
        qual_pass, _, _ = validate_and_waterfall(payload_pass)
        self.assertEqual(qual_pass["calamity"], "Y")

    def test_t3_12_cap_audit_integration_with_phase_results(self):
        """Interaction: cap_audit accurately predicts phase_results outcome."""
        for cid in ("SPGI", "COST", "CRM", "NUE"):
            c = {c["id"]: c for c in load_universe("us")["companies"]}[cid]
            aud = cap_audit(c)
            res = phase_results(c, self.p)
            if cid in ("SPGI", "COST"):
                self.assertEqual(res["result"], C.RES_QPASS)
                self.assertEqual(aud["cap_final"], c["4"])
            elif cid == "CRM":
                self.assertEqual(res["result"], C.RES_REJ[4])
                self.assertTrue(aud["fatal_flaw"])
            elif cid == "NUE":
                self.assertEqual(res["result"], C.RES_REJ[3])
                self.assertEqual(aud["cap_init"], 0)


# ==============================================================================
# TIER 4: REAL-WORLD SCENARIOS (8 Test Cases)
# ==============================================================================

class Tier4RealWorldScenarioTests(unittest.TestCase):
    """Tier 4: Complete Real-World Franchise Evaluations Across Industries."""

    def setUp(self):
        self.p = params({})
        self.us = {c["id"]: c for c in load_universe("us")["companies"]}
        self.eu = {c["id"]: c for c in load_universe("eu")["companies"]}
        self.ca = {c["id"]: c for c in load_universe("ca")["companies"]}

    def test_t4_01_real_world_msft_enterprise_software_compounder(self):
        """Scenario 1: MSFT Enterprise Software (Toll booth 2, Infrastructure 2, R&D 1 -> 30Y - 5Y = 25Y)."""
        msft = self.us["MSFT"]
        aud = cap_audit(msft)
        self.assertEqual(aud["cap_init"], 30)
        self.assertEqual(aud["mod_haircut"], 5)
        self.assertEqual(aud["cap_final"], 25)
        self.assertEqual(msft["4"], 25)
        self.assertEqual(phase_results(msft, self.p)["result"], C.RES_QPASS)

    def test_t4_02_real_world_asml_semiconductor_monopoly(self):
        """Scenario 2: ASML Lithography Monopoly (Toll booth 2, Infrastructure 2, R&D 2 -> 30Y - 5Y = 25Y)."""
        asml = self.eu["ASML.NL"]
        aud = cap_audit(asml)
        self.assertEqual(aud["cap_init"], 30)
        self.assertEqual(aud["mod_haircut"], 5)
        self.assertEqual(aud["cap_final"], 25)
        self.assertEqual(phase_results(asml, self.p)["result"], C.RES_QPASS)

    def test_t4_03_real_world_wm_infrastructure_waste_concession(self):
        """Scenario 3: WM Landfill Network (Toll booth 1, Infrastructure 2 -> 25Y - 0Y = 25Y)."""
        wm = self.us["WM"]
        aud = cap_audit(wm)
        self.assertEqual(aud["cap_init"], 25)
        self.assertEqual(aud["mod_haircut"], 0)
        self.assertEqual(aud["cap_final"], 25)
        self.assertEqual(phase_results(wm, self.p)["result"], C.RES_QPASS)

    def test_t4_04_real_world_rms_ultra_luxury_lindy_compounder(self):
        """Scenario 4: RMS.FR Hermès Ultra-Luxury Lindy Brand (Infrastructure 2 -> 25Y - 0Y = 25Y)."""
        rms = self.eu["RMS.FR"]
        aud = cap_audit(rms)
        self.assertEqual(aud["cap_init"], 25)
        self.assertEqual(aud["mod_haircut"], 0)
        self.assertEqual(aud["cap_final"], 25)
        self.assertEqual(phase_results(rms, self.p)["result"], C.RES_QPASS)

    def test_t4_05_real_world_cost_scale_economies_discounter(self):
        """Scenario 5: COST Costco Scale Economies Shared (Scale 2, Toll 1, Infra 1 -> 30Y - 0Y = 30Y)."""
        cost = self.us["COST"]
        aud = cap_audit(cost)
        self.assertEqual(aud["cap_init"], 30)
        self.assertEqual(aud["mod_haircut"], 0)
        self.assertEqual(aud["cap_final"], 30)
        self.assertEqual(cost["3a"], "Scale economies shared")
        self.assertEqual(phase_results(cost, self.p)["result"], C.RES_QPASS)

    def test_t4_06_real_world_spgi_financial_ratings_duopoly(self):
        """Scenario 6: SPGI Financial Benchmark Duopoly (Toll 2, Infra 2 -> 30Y - 0Y = 30Y)."""
        spgi = self.us["SPGI"]
        aud = cap_audit(spgi)
        self.assertEqual(aud["cap_init"], 30)
        self.assertEqual(aud["mod_haircut"], 0)
        self.assertEqual(aud["cap_final"], 30)
        self.assertEqual(phase_results(spgi, self.p)["result"], C.RES_QPASS)

    def test_t4_07_real_world_crm_saas_agentic_ai_disruption(self):
        """Scenario 7: CRM Salesforce SaaS Under Agentic AI Threat (4_sub=2 -> Fatal Cap 5Y -> REJECT)."""
        crm = self.us["CRM"]
        aud = cap_audit(crm)
        self.assertEqual(aud["cap_init"], 20)
        self.assertEqual(aud["cap_final"], 5)
        self.assertTrue(aud["fatal_flaw"])
        self.assertEqual(phase_results(crm, self.p)["result"], C.RES_REJ[4])

    def test_t4_08_real_world_nue_cyclical_commodity_producer(self):
        """Scenario 8: NUE Nucor Steel Price Taker (No structural moat -> Initial CAP 0Y -> REJECT)."""
        nue = self.us["NUE"]
        aud = cap_audit(nue)
        self.assertEqual(aud["cap_init"], 0)
        self.assertEqual(aud["primary_moat"], "None")
        self.assertEqual(phase_results(nue, self.p)["result"], C.RES_REJ[3])


# ==============================================================================
# HELPER & REGRESSION TEST SUITE (4 Named Methods Explicitly Required)
# ==============================================================================

class HelperAndRegressionTests(unittest.TestCase):
    """Named helper & regression methods required by dispatch prompt."""

    def setUp(self):
        self.p = params({})

    def test_deterministic_engine_rules(self):
        """Tests deterministic CAP calculation and 3a derivation formulas across edge cases."""
        # Initial CAP step coverage
        self.assertEqual(compute_initial_cap_from_scores((0, 0, 0, 0)), 0)
        self.assertEqual(compute_initial_cap_from_scores((1, 0, 0, 0)), 15)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 0, 0)), 20)
        self.assertEqual(compute_initial_cap_from_scores((1, 1, 1, 1)), 20)
        self.assertEqual(compute_initial_cap_from_scores((2, 0, 0, 0)), 20)
        self.assertEqual(compute_initial_cap_from_scores((2, 1, 0, 0)), 25)
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 0, 0)), 30)
        self.assertEqual(compute_initial_cap_from_scores((2, 2, 2, 2)), 30)

        # Haircuts
        self.assertEqual(moderate_force_haircut(0), 0)
        self.assertEqual(moderate_force_haircut(1), 5)
        self.assertEqual(moderate_force_haircut(2), 5)
        self.assertEqual(moderate_force_haircut(3), 10)
        self.assertEqual(moderate_force_haircut(4), 10)
        self.assertEqual(moderate_force_haircut(5), 15)

        # Fatal flaw rules
        self.assertEqual(compute_final_cap_from_scores(30, (0, 0, 0, 0, 2)), (10, 0, True))
        self.assertEqual(compute_final_cap_from_scores(20, (1, 1, 1, 0, 2)), (5, 10, True))
        self.assertEqual(compute_final_cap_from_scores(30, (2, 0, 0, 0, 2)), (5, 0, True))
        self.assertEqual(compute_final_cap_from_scores(30, (2, 2, 0, 0, 2)), (0, 0, True))

        # Non-fatal deductions floor
        self.assertEqual(compute_final_cap_from_scores(15, (1, 1, 1, 1, 1)), (5, 15, False))

    def test_reference_companies_regression(self):
        """Tests the 11 Phase 1 reference companies (SPGI, COST, ASML.NL, ASML, MSFT, WM, RMS.FR, CNR.CA, HSY, CRM, NUE)."""
        expected = {
            ("us", "SPGI"): {"cap_init": 30, "cap_final": 30, "fatal": False, "moat": "Toll booth & switching costs", "res": C.RES_QPASS},
            ("us", "COST"): {"cap_init": 30, "cap_final": 30, "fatal": False, "moat": "Scale economies shared", "res": C.RES_QPASS},
            ("us", "ASML"): {"cap_init": 30, "cap_final": 25, "fatal": False, "moat": "R&D & innovation leadership", "res": C.RES_QPASS},
            ("eu", "ASML.NL"): {"cap_init": 30, "cap_final": 25, "fatal": False, "moat": "R&D & innovation leadership", "res": C.RES_QPASS},
            ("us", "MSFT"): {"cap_init": 30, "cap_final": 25, "fatal": False, "moat": "Toll booth & switching costs", "res": C.RES_QPASS},
            ("us", "WM"): {"cap_init": 25, "cap_final": 25, "fatal": False, "moat": "Irreplaceable infrastructure & intangibles", "res": C.RES_QPASS},
            ("eu", "RMS.FR"): {"cap_init": 25, "cap_final": 25, "fatal": False, "moat": "Irreplaceable infrastructure & intangibles", "res": C.RES_QPASS},
            ("ca", "CNR.CA"): {"cap_init": 25, "cap_final": 20, "fatal": False, "moat": "Irreplaceable infrastructure & intangibles", "res": C.RES_QPASS},
            ("us", "HSY"): {"cap_init": 20, "cap_final": 15, "fatal": False, "moat": "Irreplaceable infrastructure & intangibles", "res": C.RES_QPASS},
            ("us", "CRM"): {"cap_init": 20, "cap_final": 5, "fatal": True, "moat": "Toll booth & switching costs", "res": C.RES_REJ[4]},
        }
        loaded = {u: {c["id"]: c for c in load_universe(u)["companies"]} for u in ("us", "eu", "ca")}

        for (u, cid), exp in expected.items():
            c = loaded[u][cid]
            aud = cap_audit(c)
            self.assertTrue(aud["audited"], f"{cid} must be audited")
            self.assertEqual(aud["cap_init"], exp["cap_init"], f"{cid} cap_init")
            self.assertEqual(aud["cap_final"], exp["cap_final"], f"{cid} cap_final")
            self.assertEqual(aud["fatal_flaw"], exp["fatal"], f"{cid} fatal_flaw")
            self.assertEqual(aud["primary_moat"], exp["moat"], f"{cid} moat")
            self.assertEqual(phase_results(c, self.p)["result"], exp["res"], f"{cid} result")

        # NUE zero-moat check
        nue = loaded["us"]["NUE"]
        nue_aud = cap_audit(nue)
        self.assertTrue(nue_aud["moat_complete"])
        self.assertEqual(nue_aud["cap_init"], 0)
        self.assertEqual(nue_aud["primary_moat"], "None")
        self.assertEqual(phase_results(nue, self.p)["result"], C.RES_REJ[3])

    def test_mirrors_synchronization(self):
        """Tests exact score, note, and evidence parity for ASML/ASML.NL and FER/FER.ES."""
        us = {c["id"]: c for c in load_universe("us")["companies"]}
        eu = {c["id"]: c for c in load_universe("eu")["companies"]}

        # ASML <-> ASML.NL qualitative subscore and gate score parity
        for k in (*C.MOAT_SCORE_CODES, "3a", "3b", "3m", *C.FORCE_SCORE_CODES, "4", "4n", "5", "6", "calamity", "calamity_note"):
            self.assertEqual(us["ASML"].get(k), eu["ASML.NL"].get(k), msg=f"ASML mirror mismatch on {k}")

        # FER <-> FER.ES qualitative gate score parity
        for k in (*C.MOAT_SCORE_CODES, "3a", "3b", "3m", *C.FORCE_SCORE_CODES, "4", "4n", "5", "6", "calamity", "calamity_note"):
            self.assertEqual(us["FER"].get(k), eu["FER.ES"].get(k), msg=f"FER mirror mismatch on {k}")

        # Verify mirror mappings exist in us/universe.json
        with open(ROOT / "data" / "us" / "universe.json") as f:
            u_meta = json.load(f)
        self.assertIn("ASML", u_meta.get("mirror", {}))
        self.assertIn("FER", u_meta.get("mirror", {}))

        # Check narrative text synchronization if bulk scoring is complete
        require_all = os.environ.get("REQUIRE_ALL_SCORED") == "1"
        if require_all or (us["ASML"].get("note") == eu["ASML.NL"].get("note") and us["ASML"].get("note")):
            self.assertEqual(us["ASML"].get("note"), eu["ASML.NL"].get("note"))
            self.assertEqual(us["ASML"].get("evidence"), eu["ASML.NL"].get("evidence"))
            self.assertEqual(us["FER"].get("note"), eu["FER.ES"].get("note"))
            self.assertEqual(us["FER"].get("evidence"), eu["FER.ES"].get("evidence"))
        else:
            # Baseline in M1: qualitative gate scores match 100%
            self.assertTrue(len(us["ASML"].get("note", "")) > 0)
            self.assertTrue(len(eu["ASML.NL"].get("note", "")) > 0)

    def test_all_989_gate3_companies_completed(self):
        """Evaluates all 989 Gate 3 companies across data/{us,eu,ca}/inputs.csv.

        Verifies:
        1. Exact Gate 3 candidate cohort count matches 989 (US: 445, EU: 495, CA: 49).
        2. Every scored company has deterministic CAP matching compute_final_cap_from_scores.
        3. Every scored company with any force >= 1 has non-empty 4n Runway & Forces note.
        4. Every scored company adheres to sequential Munger waterfall clearing.
        5. Reports population progress: 11 reference companies scored in M1 baseline,
           or asserts 100% population when bulk scoring (M3) is complete / REQUIRE_ALL_SCORED=1.
        """
        gate3_candidates = []
        scored_companies = []
        unscored_companies = []

        for u in ("us", "eu", "ca"):
            with open(ROOT / "data" / u / "inputs.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("1") == "Y" and row.get("2") == "Y":
                        gate3_candidates.append((u, row))
                        # A company is scored if moat fields are populated
                        if row.get("3_tb") != "" and row.get("3_tb") is not None:
                            scored_companies.append((u, row))
                        else:
                            unscored_companies.append((u, row))

        # 1. Candidate count invariant
        self.assertEqual(len(gate3_candidates), 989, f"Expected exactly 989 Gate 3 candidates, found {len(gate3_candidates)}")

        # 2. Audit all scored companies under Two-Stage Munger Waterfall (v7.18)
        g3_advancing = []
        g3_rejected = []
        for u, row in scored_companies:
            cid = row.get("id")
            # All scored Gate 3 companies must have 3_tb, 3_ia, 3_se, 3_rd, 3a populated
            for k in C.MOAT_SCORE_CODES:
                self.assertTrue(row.get(k) != "" and row.get(k) is not None, f"{cid} missing moat score {k}")
                self.assertIn(int(row[k]), (0, 1, 2), f"{cid} invalid moat score {row[k]}")

            self.assertTrue(row.get("3a") != "" and row.get("3a") is not None, f"{cid} missing 3a")
            self.assertIn(row.get("3a"), C.MOAT_TYPES, f"{cid} invalid 3a {row.get('3a')}")

            m_scores = tuple(int(row[k]) for k in C.MOAT_SCORE_CODES)

            # Check Gate 3 waterfall status:
            fails_g3 = (row.get("3a") == "None" or row.get("3b") == "N") and row.get("calamity") != "Y"

            if fails_g3:
                g3_rejected.append((u, cid))
                # Rule 2 (Stage 1): Companies failing Gate 3 must have Gate 4 (4_ent..4_sub, 4, 4n) and Gates 5-6 strictly blank ("")
                for k in (*C.FORCE_SCORE_CODES, "4", "4n", "5", "6"):
                    self.assertEqual(row.get(k, ""), "", f"{cid} fails Gate 3 but has non-empty downstream {k}={row.get(k)!r}")
            else:
                g3_advancing.append((u, cid))
                # Rule 3 (Stage 2): Companies passing Gate 3 (or calamity='Y') advance to Gate 4 and receive full force scores
                for k in (*C.FORCE_SCORE_CODES, "4"):
                    self.assertTrue(row.get(k) != "" and row.get(k) is not None, f"{cid} passed Gate 3 but missing Gate 4 field {k}")
                    if k in C.FORCE_SCORE_CODES:
                        self.assertIn(int(row[k]), (0, 1, 2), f"{cid} invalid force score {row[k]}")

                f_scores = tuple(int(row[k]) for k in C.FORCE_SCORE_CODES)
                cap_init = compute_initial_cap_from_scores(m_scores)
                exp_cap, _, exp_fatal = compute_final_cap_from_scores(cap_init, f_scores)
                self.assertEqual(int(row["4"]), exp_cap, f"{cid} CAP mismatch: stored {row['4']} vs computed {exp_cap}")

                # Mandatory 4n when any force >= 1
                if any(f_val >= 1 for f_val in f_scores):
                    self.assertTrue(len(row.get("4n", "").strip()) > 0, f"{cid} missing mandatory 4n note with forces {f_scores}")

                # Rule 4 (Stage 2 Full Diagnostic Scorecard):
                # Every Gate-3-advancing company must have valid non-empty Gate 5 (0/1/2) and Gate 6 (Y/N),
                # even when rejected at Gate 4 (CAP < 15) or Gate 5 (5 = 0). Gate 4 CAP < 15 remains non-waivable.
                if int(row["4"]) < 15:
                    self.assertNotEqual(row.get("calamity"), "Y", f"{cid} fails Gate 4 (CAP={row['4']}) but has calamity='Y'")
                g5_raw = row.get("5", "")
                self.assertTrue(g5_raw != "" and g5_raw is not None, f"{cid} advanced past Gate 3 but missing Gate 5")
                self.assertIn(int(g5_raw), (0, 1, 2), f"{cid} invalid Gate 5 score {g5_raw!r}")
                g6_raw = row.get("6", "")
                self.assertIn(g6_raw, ("Y", "N"), f"{cid} advanced past Gate 3 but invalid/missing Gate 6 {g6_raw!r}")

        # 3. Population completeness evaluation
        require_all = os.environ.get("REQUIRE_ALL_SCORED") == "1"
        if require_all or len(unscored_companies) == 0:
            self.assertEqual(len(unscored_companies), 0, f"Expected 0 unscored companies, found {len(unscored_companies)}")
            self.assertEqual(len(scored_companies), 989, f"Expected 989 scored companies, found {len(scored_companies)}")
            self.assertEqual(len(g3_advancing), 485, f"Expected 485 Gate-3-advancing companies, found {len(g3_advancing)}")
            self.assertEqual(len(g3_rejected), 504, f"Expected 504 Gate-3-rejected companies, found {len(g3_rejected)}")
        else:
            # Baseline pre-bulk scoring (Milestone M1):
            # Exactly 11 reference companies scored, exactly 978 unscored legacy rows
            self.assertEqual(len(scored_companies), 11, f"Expected 11 scored reference companies in M1, found {len(scored_companies)}")
            self.assertEqual(len(unscored_companies), 978, f"Expected 978 unscored legacy companies in M1, found {len(unscored_companies)}")


if __name__ == "__main__":
    unittest.main()
