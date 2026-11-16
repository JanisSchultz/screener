"""Unit tests for screener/bulk_scorer.py verifying all capabilities and constraints."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import (
    REFERENCE_COMPANIES,
    REFERENCE_SNAPSHOT,
    TARGET_GATE_3_COUNTS,
    TOTAL_GATE_3_TARGET,
    audit_gate_3_universe,
    calculate_caps_and_archetype,
    export_batch_context,
    format_4n_note,
    get_gate_3_companies,
    ingest_evaluations,
    is_fast_clock_speed,
    sync_mirrors,
    validate_company_evaluation,
    verify_reference_companies,
)


class BulkScorerCoreTests(unittest.TestCase):
    def test_gate_3_company_discovery_exact_counts(self):
        """Identify all 989 Gate 3 companies (US: 445, EU: 495, CA: 49)."""
        all_g3 = get_gate_3_companies()
        self.assertEqual(len(all_g3), TOTAL_GATE_3_TARGET)

        counts = {}
        for u in ("us", "eu", "ca"):
            u_comps = get_gate_3_companies(universes=(u,))
            counts[u] = len(u_comps)
            self.assertEqual(counts[u], TARGET_GATE_3_COUNTS[u])

        self.assertEqual(counts, TARGET_GATE_3_COUNTS)

        # Scored vs unscored partition: 11 reference scored, 978 unscored
        scored = get_gate_3_companies(scored_only=True)
        unscored = get_gate_3_companies(unscored_only=True)
        self.assertEqual(len(scored), 11)
        self.assertEqual(len(unscored), 978)

        # All 11 scored are reference companies
        scored_ids = {c["id"] for c in scored}
        self.assertEqual(scored_ids, REFERENCE_COMPANIES)

    def test_reference_company_preservation(self):
        """Strictly verify the 11 Phase 1 reference companies against immutable snapshot."""
        ok, discrepancies = verify_reference_companies()
        self.assertTrue(ok, f"Reference discrepancies found: {discrepancies}")
        self.assertEqual(len(discrepancies), 0)

        # Ensure attempting to mutate a reference company in an evaluation payload is blocked/guarded
        tamper_payload = {
            "id": "MSFT",
            "qualitative": {
                "3_tb": 0,  # attempt to tamper verified 3_tb=2
                "3_ia": 0,
                "4_riv": 2,
            },
        }
        sanitized, warnings, errors = validate_company_evaluation(tamper_payload)
        self.assertTrue(any("Reference Company Guard" in w for w in warnings))

    def test_fast_clock_speed_detection(self):
        """Verify Mauboussin outside-view clock speed detection."""
        self.assertTrue(is_fast_clock_speed("Information Technology", "Application Software"))
        self.assertTrue(is_fast_clock_speed("Information Technology", "Semiconductors"))
        self.assertTrue(is_fast_clock_speed("Health Care", "Pharmaceuticals"))
        self.assertTrue(is_fast_clock_speed("Health Care", "Biotechnology"))
        self.assertTrue(is_fast_clock_speed("Health Care", "Life Sciences Tools & Services"))
        self.assertFalse(is_fast_clock_speed("Industrials", "Rail Transportation"))
        self.assertFalse(is_fast_clock_speed("Consumer Staples", "Packaged Foods & Meats"))
        self.assertFalse(is_fast_clock_speed("Financials", "Financial Exchanges & Data"))

    def test_deterministic_cap_and_moat_calculations(self):
        """Verify Initial CAP, primary moat tie-breaking, and Final CAP formulas."""
        # 1. Zero moat -> 0Y & None
        res_zero = calculate_caps_and_archetype({"3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0})
        self.assertEqual(res_zero["cap_init"], 0)
        self.assertEqual(res_zero["primary_moat"], "None")

        # 2. Single elite moat -> 20Y
        res_single = calculate_caps_and_archetype({"3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0})
        self.assertEqual(res_single["cap_init"], 20)
        self.assertEqual(res_single["primary_moat"], "Toll booth & switching costs")

        # 3. Elite + supporting -> 25Y
        res_stack = calculate_caps_and_archetype({"3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0})
        self.assertEqual(res_stack["cap_init"], 25)
        self.assertEqual(res_stack["primary_moat"], "Irreplaceable infrastructure & intangibles")

        # 4. Dual elite -> 30Y
        res_dual = calculate_caps_and_archetype({"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0})
        self.assertEqual(res_dual["cap_init"], 30)

        # 5. Tie-breaking preserves supplied 3a if in top archetypes
        res_tie = calculate_caps_and_archetype(
            {"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 2},
            current_3a="R&D & innovation leadership",
        )
        self.assertEqual(res_tie["primary_moat"], "R&D & innovation leadership")

        # 6. Tie-breaking falls back to canonical first order if supplied 3a is invalid/sub-max
        res_tie_def = calculate_caps_and_archetype(
            {"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 2},
            current_3a="Scale economies shared",
        )
        self.assertEqual(res_tie_def["primary_moat"], "Toll booth & switching costs")

        # 7. Moderate haircut: 2 moderate forces -> -5Y haircut on 30Y initial CAP -> 25Y final CAP
        res_haircut = calculate_caps_and_archetype(
            {"3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0},
            force_scores={"4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0},
        )
        self.assertEqual(res_haircut["cap_final"], 25)
        self.assertEqual(res_haircut["mod_haircut"], 5)
        self.assertFalse(res_haircut["fatal_flaw"])

        # 8. Fatal-flaw cap: single force=2 on 20Y initial CAP with 3 ones -> 5Y final CAP
        res_fatal = calculate_caps_and_archetype(
            {"3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0},
            force_scores={"4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2},
        )
        self.assertEqual(res_fatal["cap_final"], 5)
        self.assertTrue(res_fatal["fatal_flaw"])

    def test_4n_note_formatting(self):
        """Verify standardized 4n Runway & Forces note generation."""
        # Case 1: Benign / All 0
        n_benign = format_4n_note(30, 0, 30, {"4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0})
        self.assertIn("insulates the franchise across all five competitive forces", n_benign)

        # Case 2: Moderate haircut
        n_mod = format_4n_note(
            30, 5, 25,
            {"4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 0},
            force_rationales={"4_buy": "Foundry concentration", "4_sup": "Zeiss optics bottleneck"},
            insulation="EUV physics monopoly",
        )
        self.assertIn("Initial CAP 30Y reduced by -5Y", n_mod)
        self.assertIn("4_buy=1", n_mod)
        self.assertIn("4_sup=1", n_mod)
        self.assertIn("EUV physics monopoly", n_mod)

        # Case 3: Fatal flaw
        n_fatal = format_4n_note(
            20, 10, 5,
            {"4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2},
            force_rationales={"4_sub": "Agentic AI seat substitution", "4_buy": "Enterprise seat scrutiny", "4_riv": "Suite rivalry", "4_ent": "AI build-cost drop"},
        )
        self.assertIn("Fatal-Flaw Cap triggered (Final CAP = 5Y, REJECT)", n_fatal)
        self.assertIn("4_sub=2", n_fatal)

    def test_munger_waterfall_clearing(self):
        """Verify sequential Munger reject waterfall clearing on gate rejections."""
        # 1. Gate 3 zero moat -> downstream cleared
        payload_g3_fail = {
            "id": "TEST_CO_1",
            "qualitative": {
                "1": "Y", "2": "Y",
                "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
                "3b": "Y",  # attempting to pass 3b with zero moat
                "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
                "4": 20, "4n": "Should be scrubbed",
                "5": 1, "6": "Y",
            },
        }
        qual, warnings, errors = validate_company_evaluation(payload_g3_fail)
        self.assertEqual(qual["3a"], "None")
        for k in ("4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n", "5", "6"):
            self.assertEqual(qual[k], "")

        # 2. Gate 4 CAP < 15 -> Gates 5 and 6 cleared
        payload_g4_fail = {
            "id": "TEST_CO_2",
            "qualitative": {
                "1": "Y", "2": "Y",
                "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
                "3a": "Toll booth & switching costs", "3b": "Y", "3m": "Moat note",
                "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
                "4": 30,  # manual override attempt; formula computes 5
                "4n": "Fatal flaw note",
                "5": 1, "6": "Y",
            },
        }
        qual, warnings, errors = validate_company_evaluation(payload_g4_fail)
        self.assertEqual(qual["4"], 5)
        self.assertEqual(qual["5"], "")
        self.assertEqual(qual["6"], "")
        # Gate 4 force subscores and note remain populated for auditability
        self.assertEqual(qual["4_sub"], 2)
        self.assertEqual(qual["4n"], "Fatal flaw note")

        # 3. Missing 4n note when force >= 1 triggers validation error
        payload_missing_4n = {
            "id": "TEST_CO_3",
            "qualitative": {
                "1": "Y", "2": "Y",
                "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
                "3a": "Toll booth & switching costs", "3b": "Y", "3m": "Moat note",
                "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
                "4n": "",  # missing!
                "5": 1, "6": "Y",
            },
        }
        qual, warnings, errors = validate_company_evaluation(payload_missing_4n)
        self.assertTrue(any("4n" in err for err in errors))

    def test_batch_context_exporter(self):
        """Verify export_batch_context generates complete dossiers with financial & clock-speed indicators."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_p = Path(tmp_dir)
            exported = export_batch_context(out_dir=out_p, batch_size=5, universe="ca", unscored_only=False)
            self.assertGreater(len(exported), 0)

            # Read back first batch
            data = json.loads(exported[0].read_text(encoding="utf-8"))
            self.assertIn("batch_metadata", data)
            self.assertIn("companies", data)
            first_c = data["companies"][0]
            self.assertIn("identity", first_c)
            self.assertIn("current_qualitative", first_c)
            self.assertIn("financial_context", first_c)
            self.assertIn("is_fast_clock_speed", first_c["identity"])

    def test_audit_compliance_engine(self):
        """Verify audit_gate_3_universe runs cleanly and validates all baseline checks."""
        audit = audit_gate_3_universe()
        self.assertTrue(audit["count_target_met"])
        self.assertEqual(audit["total_gate_3"], 989)
        self.assertTrue(audit["reference_companies_verified"])
        self.assertEqual(len(audit["formula_discrepancies"]), 0)
        self.assertEqual(len(audit["moat_alignment_discrepancies"]), 0)
        self.assertEqual(len(audit["missing_4n_notes"]), 0)
        self.assertEqual(len(audit["waterfall_violations"]), 0)
        self.assertEqual(len(audit["calamity_violations"]), 0)


if __name__ == "__main__":
    unittest.main()
