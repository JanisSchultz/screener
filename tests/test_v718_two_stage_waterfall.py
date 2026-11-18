"""Opaque-box E2E verification suite for v7.18 Two-Stage Munger Waterfall & Diagnostic Scorecard.

Derived from `.agents/teamwork/ORIGINAL_REQUEST.md` and `QUALITATIVE_EVALUATION_SPEC.md` /
`COMPANY_EVALUATION_SPEC.md`. Exercises real engine modules (`apply_evaluation`, `bulk_scorer`,
`gates`, `dashboard`, `config`), real datasets (`data/{us,eu,ca}/inputs.csv`), compiled HTML/JS
cockpit execution in JavaScriptCore, and specification consistency.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener import bulk_scorer
from screener import config as C
from screener.apply_evaluation import validate_and_waterfall
from screener.bulk_scorer import (
    REFERENCE_SNAPSHOT,
    audit_gate_3_universe,
    ingest_evaluations,
    validate_company_evaluation,
)
from screener.dashboard import build_dashboard_html, collect_screener_data
from screener.gates import params, phase_results


def _make_payload(**qual_overrides) -> dict:
    qual = {
        "gate_1": "Y",
        "gate_2": "Y",
        "gate_3_moat_toll_booth": 2,
        "gate_3_moat_infrastructure": 0,
        "gate_3_moat_scale_shared": 0,
        "gate_3_moat_rd": 0,
        "gate_3a_moat_archetype": "Toll booth & switching costs",
        "gate_3b_pricing_and_proof": "Y",
        "gate_3m_moat_note": "Structural switching barriers.",
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
        "evidence": "Audited empirical evidence.",
    }
    qual.update(qual_overrides)
    return {"id": "MOCK_V718", "qualitative": qual}


def _load_all_input_rows() -> list[tuple[str, dict[str, str]]]:
    rows: list[tuple[str, dict[str, str]]] = []
    for u in ("us", "eu", "ca"):
        with open(ROOT / "data" / u / "inputs.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append((u, row))
    return rows


class WaterfallEngineValidationTests(unittest.TestCase):
    """R1: Two-Stage Waterfall validation, scrubbing, and audit invariants."""

    def setUp(self):
        self.p = params({})

    def test_stage1_early_stop_scrubs_downstream_on_g1_g2_g3(self):
        cases = [
            ("G1=N", {"gate_1": "N"}),
            ("G2=N", {"gate_2": "N", "gate_2_reason": "Cyclical."}),
            ("G3a=None", {"gate_3_moat_toll_booth": 0, "gate_3a_moat_archetype": "None"}),
            ("G3b=N", {"gate_3b_pricing_and_proof": "N"}),
        ]
        for label, overrides in cases:
            with self.subTest(case=label):
                payload = _make_payload(**overrides)
                qual_ae, _, _ = validate_and_waterfall(payload)
                self.assertEqual(qual_ae.get("5", ""), "", f"apply_evaluation failed to scrub 5 on {label}")
                self.assertEqual(qual_ae.get("6", ""), "", f"apply_evaluation failed to scrub 6 on {label}")

                qual_bs, _, errs = validate_company_evaluation(payload)
                self.assertEqual(errs, [], f"unexpected errors on {label}: {errs}")
                self.assertEqual(qual_bs.get("5", ""), "", f"bulk_scorer failed to scrub 5 on {label}")
                self.assertEqual(qual_bs.get("6", ""), "", f"bulk_scorer failed to scrub 6 on {label}")

    def test_stage2_gate4_under_15_preserves_g5_g6(self):
        for g5_val in (0, 1, 2):
            for g6_val in ("Y", "N"):
                with self.subTest(g5=g5_val, g6=g6_val):
                    payload = _make_payload(
                        gate_4_force_substitution=2,  # 20Y init -> 10Y final (< 15)
                        gate_5_management_score=g5_val,
                        gate_6_cash_and_balance_sheet=g6_val,
                    )
                    qual_ae, _, warns_ae = validate_and_waterfall(payload)
                    self.assertEqual(qual_ae["4"], 10)
                    self.assertEqual(qual_ae["5"], g5_val)
                    self.assertEqual(qual_ae["6"], g6_val)
                    self.assertFalse(any("scrubbed '5'" in w or "scrubbed '6'" in w for w in warns_ae))
                    self.assertEqual(phase_results(qual_ae, self.p)["result"], C.RES_REJ[4])

                    qual_bs, warns_bs, errs_bs = validate_company_evaluation(payload)
                    self.assertEqual(errs_bs, [])
                    self.assertEqual(qual_bs["4"], 10)
                    self.assertEqual(int(qual_bs["5"]), g5_val)
                    self.assertEqual(qual_bs["6"], g6_val)
                    self.assertFalse(any("cleared '5'" in w or "cleared '6'" in w for w in warns_bs))

    def test_stage2_gate5_zero_preserves_g6(self):
        for g6_val in ("Y", "N"):
            with self.subTest(g6=g6_val):
                payload = _make_payload(
                    gate_5_management_score=0,
                    gate_6_cash_and_balance_sheet=g6_val,
                )
                qual_ae, _, warns_ae = validate_and_waterfall(payload)
                self.assertEqual(warns_ae, [])
                self.assertEqual(qual_ae["5"], 0)
                self.assertEqual(qual_ae["6"], g6_val)
                self.assertEqual(phase_results(qual_ae, self.p)["result"], C.RES_REJ[5])

                qual_bs, warns_bs, errs_bs = validate_company_evaluation(payload)
                self.assertEqual(errs_bs, [])
                self.assertEqual(int(qual_bs["5"]), 0)
                self.assertEqual(qual_bs["6"], g6_val)
                self.assertFalse(any("cleared '6'" in w for w in warns_bs))

    def test_gate5_invalid_inputs_rejected_and_cleared(self):
        for bad_g5 in (-1, 3, "9", "bad", True, 1.5):
            with self.subTest(bad_g5=bad_g5):
                payload = _make_payload(gate_5_management_score=bad_g5)
                qual_ae, _, warns_ae = validate_and_waterfall(payload)
                self.assertEqual(qual_ae.get("5", ""), "")
                self.assertTrue(
                    any("5" in w and "invalid" in w.lower() for w in warns_ae),
                    f"Expected invalid Gate 5 warning for {bad_g5!r}, got {warns_ae}",
                )

                _, _, errs_bs = validate_company_evaluation(payload)
                self.assertTrue(
                    any("'5'" in e or "gate 5" in e.lower() for e in errs_bs),
                    f"Expected Gate 5 error for {bad_g5!r}, got {errs_bs}",
                )

    def test_gate6_invalid_inputs_rejected_and_cleared(self):
        for bad_g6 in ("maybe", "YES", "X", "0", 1):
            with self.subTest(bad_g6=bad_g6):
                payload = _make_payload(gate_6_cash_and_balance_sheet=bad_g6)
                qual_ae, _, warns_ae = validate_and_waterfall(payload)
                self.assertEqual(qual_ae.get("6", ""), "")
                self.assertTrue(
                    any("6" in w and "invalid" in w.lower() for w in warns_ae),
                    f"Expected invalid Gate 6 warning for {bad_g6!r}, got {warns_ae}",
                )

                _, _, errs_bs = validate_company_evaluation(payload)
                self.assertTrue(
                    any("'6'" in e or "gate 6" in e.lower() for e in errs_bs),
                    f"Expected Gate 6 error for {bad_g6!r}, got {errs_bs}",
                )

    def test_blank_g5_or_g6_past_gate3_triggers_warning_even_on_g4_or_g5_reject(self):
        # Gate 4 CAP < 15 with blank Gate 5 and blank Gate 6
        p_g4_blank = _make_payload(
            gate_4_force_substitution=2,
            gate_5_management_score="",
            gate_6_cash_and_balance_sheet="",
        )
        _, warns_g4, errs_g4 = validate_company_evaluation(p_g4_blank)
        self.assertEqual(errs_g4, [])
        self.assertTrue(any("gate 5" in w.lower() for w in warns_g4), f"Missing blank G5 warning: {warns_g4}")
        self.assertTrue(any("gate 6" in w.lower() for w in warns_g4), f"Missing blank G6 warning: {warns_g4}")

        # Gate 5 = 0 and blank Gate 6
        p_g5_blank = _make_payload(
            gate_5_management_score=0,
            gate_6_cash_and_balance_sheet="",
        )
        _, warns_g5, errs_g5 = validate_company_evaluation(p_g5_blank)
        self.assertEqual(errs_g5, [])
        self.assertTrue(any("gate 6" in w.lower() for w in warns_g5), f"Missing blank G6 warning on G5=0: {warns_g5}")

    def test_gate3b_failure_always_cascades_stage1_scrub(self):
        # 1. Unit checks across both force-computed CAP and standalone CAP when 3b = N
        scenarios = [
            (
                "force_computed_cap_10",
                {
                    "gate_3b_pricing_and_proof": "N",
                    "gate_4_force_substitution": 2,  # 20Y init -> 10Y final
                    "gate_4n_runway_note": "Substitution risk.",
                    "gate_5_management_score": 1,
                    "gate_6_cash_and_balance_sheet": "Y",
                },
            ),
            (
                "standalone_cap_20",
                {
                    "gate_3b_pricing_and_proof": "N",
                    "gate_4_force_entrants": "",
                    "gate_4_force_rivalry": "",
                    "gate_4_force_buyers": "",
                    "gate_4_force_suppliers": "",
                    "gate_4_force_substitution": "",
                    "gate_4_runway_cap": 20,
                    "gate_4n_runway_note": "Legacy CAP.",
                    "gate_5_management_score": 2,
                    "gate_6_cash_and_balance_sheet": "N",
                },
            ),
        ]
        downstream_keys = (*C.FORCE_SCORE_CODES, "4", "4n", "5", "6")
        for label, overrides in scenarios:
            with self.subTest(scenario=label):
                payload = _make_payload(**overrides)
                qual_ae, _, warns_ae = validate_and_waterfall(payload)
                for k in downstream_keys:
                    self.assertEqual(qual_ae.get(k, ""), "", f"apply_evaluation left {k} non-blank on {label}")
                self.assertTrue(any("3b" in w.lower() for w in warns_ae))
                self.assertEqual(phase_results(qual_ae, self.p)["result"], C.RES_REJ[3])

                qual_bs, warns_bs, errs_bs = validate_company_evaluation(payload)
                self.assertEqual(errs_bs, [], f"unexpected errors on {label}: {errs_bs}")
                for k in downstream_keys:
                    self.assertEqual(qual_bs.get(k, ""), "", f"bulk_scorer left {k} non-blank on {label}")
                self.assertTrue(any("3b" in w.lower() for w in warns_bs))
                self.assertFalse(any("blank" in w.lower() for w in warns_bs), f"spurious blank G5/G6 warning: {warns_bs}")

        # 2. Isolated end-to-end ingest_evaluations -> audit_gate_3_universe verification
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_data = Path(tmpdir) / "data"
            shutil.copytree(ROOT / "data", tmp_data)
            orig_data_dir = bulk_scorer.DATA_DIR
            try:
                bulk_scorer.DATA_DIR = tmp_data
                nvda_payload = _make_payload(
                    gate_3b_pricing_and_proof="N",
                    gate_4_force_substitution=2,
                    gate_4n_runway_note="Substitution risk caps runway below 15Y.",
                    gate_5_management_score=1,
                    gate_6_cash_and_balance_sheet="Y",
                )
                nvda_payload["id"] = "NVDA"
                summary = ingest_evaluations([nvda_payload], dry_run=False, sync_mirrors_after=False)
                self.assertEqual(summary["errors"], [])
                self.assertEqual(summary["applied"], 1)

                audit = audit_gate_3_universe()
                self.assertEqual(audit["waterfall_violations"], [])
                self.assertEqual(audit["stage2_discrepancies"], [])
            finally:
                bulk_scorer.DATA_DIR = orig_data_dir

    def test_standalone_gate4_rejects_bool_and_non_integer_float(self):
        for bad_4 in (15.5, 10.2, True, False, "15.5", 17):
            with self.subTest(bad_4=bad_4):
                qual_ae, _, warns_ae = validate_and_waterfall({"qualitative": {"gate_4_runway_cap": bad_4}})
                self.assertEqual(qual_ae.get("4", ""), "", f"Expected {bad_4!r} to be cleared")
                self.assertTrue(
                    any("gate 4 cap" in w.lower() and "invalid" in w.lower() for w in warns_ae),
                    f"Expected invalid Gate 4 CAP warning for {bad_4!r}, got {warns_ae}",
                )

        for good_4, expected in ((15, 15), (15.0, 15), ("15", 15), (0, 0), ("0", 0)):
            with self.subTest(good_4=good_4):
                qual_ae, _, warns_ae = validate_and_waterfall({"qualitative": {"gate_4_runway_cap": good_4}})
                self.assertEqual(qual_ae.get("4"), expected)
                self.assertIs(type(qual_ae.get("4")), int)
                self.assertEqual(warns_ae, [])

    def test_bulk_scorer_audit_and_reference_snapshot_clean(self):
        audit = audit_gate_3_universe()
        self.assertTrue(audit["count_target_met"], audit)
        self.assertTrue(audit["reference_companies_verified"], audit["reference_discrepancies"])
        self.assertEqual(audit["formula_discrepancies"], [])
        self.assertEqual(audit["moat_alignment_discrepancies"], [])
        self.assertEqual(audit["missing_4n_notes"], [])
        self.assertEqual(audit["waterfall_violations"], [])
        self.assertTrue(audit["mirror_parity_ok"], audit["mirror_discrepancies"])
        self.assertEqual(audit["unscored_companies_count"], 0)
        self.assertEqual(audit["scored_companies_count"], 989)
        self.assertEqual(audit["stage2_advancing_count"], 483)
        # If Stage 2 discrepancy list is present on audit dict, verify it is empty
        for key in ("stage2_discrepancies", "missing_stage2_scores"):
            if key in audit:
                self.assertEqual(audit[key], [], f"{key} non-empty: {audit[key]}")

        # CRM in REFERENCE_SNAPSHOT must have verified non-empty 5 and 6 matching US inputs.csv
        crm_ref = REFERENCE_SNAPSHOT["CRM"]
        self.assertIn(int(crm_ref["5"]), (0, 1, 2))
        self.assertIn(crm_ref["6"], ("Y", "N"))
        self.assertEqual(REFERENCE_SNAPSHOT["NUE"]["4"], "")
        self.assertEqual(REFERENCE_SNAPSHOT["NUE"]["5"], "")
        self.assertEqual(REFERENCE_SNAPSHOT["NUE"]["6"], "")

        proc = subprocess.run(
            [sys.executable, str(ROOT / "screener" / "bulk_scorer.py"), "--audit"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("v7.19", proc.stdout)


class FunnelAndScorecardInvarianceTests(unittest.TestCase):
    """R2 + Funnel Invariance: 483 advancing, 506 G3 rejects, 124 Stage-2 diagnostic rows, 225 Prime / 25 Growth at ~0g."""

    @classmethod
    def setUpClass(cls):
        cls.all_rows = _load_all_input_rows()
        cls.screener_data = collect_screener_data(["us", "eu", "ca"])

    def test_funnel_and_prime_grade_invariance(self):
        # Threshold invariant
        self.assertEqual(params({})["thr_cap"], 15)

        # Total & Gate 3 counts from CSVs
        self.assertEqual(len(self.all_rows), 1175)
        per_u_total = {u: sum(1 for uu, _ in self.all_rows if uu == u) for u in ("us", "eu", "ca")}
        self.assertEqual(per_u_total, {"us": 515, "eu": 602, "ca": 58})

        g3_rows = [(u, r) for u, r in self.all_rows if r.get("1") == "Y" and r.get("2") == "Y"]
        self.assertEqual(len(g3_rows), 989)
        per_u_g3 = {u: sum(1 for uu, _ in g3_rows if uu == u) for u in ("us", "eu", "ca")}
        self.assertEqual(per_u_g3, {"us": 445, "eu": 495, "ca": 49})

        advancing = []
        g3_rejected = []
        for u, r in g3_rows:
            fails_g3 = r.get("3a") == "None" or r.get("3b") == "N"
            if fails_g3:
                g3_rejected.append((u, r))
            else:
                advancing.append((u, r))

        self.assertEqual(len(advancing), 483)
        self.assertEqual(len(g3_rejected), 506)
        rej_ids = {r["id"] for _, r in g3_rejected}
        self.assertIn("APD", rej_ids)
        self.assertIn("EL", rej_ids)

        # All 506 Gate-3 rejects keep 4_*, 4, 4n, 5, 6 strictly blank ""
        for _, r in g3_rejected:
            for k in (*C.FORCE_SCORE_CODES, "4", "4n", "5", "6"):
                self.assertEqual(r.get(k, ""), "", f"{r['id']} G3 reject has non-blank {k}={r.get(k)!r}")

        # Dashboard / phase_results counts invariance
        companies = self.screener_data["companies"]
        self.assertEqual(len(companies), 1175)
        self.assertEqual(self.screener_data["summary"]["total_companies"], 1175)

        prime_grade = [c for c in companies if c.get("passes_prime_grade")]
        quality_grade = [c for c in companies if c.get("passes_quality_grade")]
        growth_0g = [c for c in companies if c.get("passes_growth_0g")]
        to_review = [c for c in companies if c.get("result") == C.RES_REVIEW or c.get("review_at")]

        self.assertEqual(len(prime_grade), 225)
        self.assertEqual(len(quality_grade), 443)
        self.assertEqual(len(growth_0g), 25)
        self.assertEqual(len(to_review), 0)
        self.assertEqual(self.screener_data["summary"]["quality_pass"], 225)
        self.assertEqual(self.screener_data["summary"]["growth_0g"], 25)
        self.assertNotIn("calamity_pass", self.screener_data["summary"])

    def test_all_483_advancing_have_complete_g5_g6_without_changing_rejections(self):
        companies_by_uid = {(c["universe"], c["id"]): c for c in self.screener_data["companies"]}
        g3_rows = [(u, r) for u, r in self.all_rows if r.get("1") == "Y" and r.get("2") == "Y"]
        advancing = [
            (u, r)
            for u, r in g3_rows
            if not (r.get("3a") == "None" or r.get("3b") == "N")
        ]
        self.assertEqual(len(advancing), 483)

        g4_rejects = []
        g5_rejects = []
        for u, r in advancing:
            cid = r["id"]
            self.assertIn(r.get("5"), ("0", "1", "2"), f"{cid} invalid/blank Gate 5: {r.get('5')!r}")
            self.assertIn(r.get("6"), ("Y", "N"), f"{cid} invalid/blank Gate 6: {r.get('6')!r}")

            c = companies_by_uid[(u, cid)]
            self.assertIn(c.get("g5_mgmt"), (0, 1, 2), f"{cid} missing g5_mgmt in dashboard payload")
            self.assertIn(c.get("g6_cash"), ("Y", "N"), f"{cid} missing g6_cash in dashboard payload")
            self.assertEqual(c.get("g6_answer"), c.get("g6_cash"))

            if int(r["4"]) < 15:
                g4_rejects.append((u, cid))
                self.assertEqual(c["result"], C.RES_REJ[4], f"{cid} CAP={r['4']} must stay {C.RES_REJ[4]}")
            elif r["5"] == "0":
                g5_rejects.append((u, cid))
                self.assertEqual(c["result"], C.RES_REJ[5], f"{cid} 5=0 must stay {C.RES_REJ[5]}")

        self.assertEqual(len(g4_rejects), 108)
        self.assertEqual(
            {u: sum(1 for uu, _ in g4_rejects if uu == u) for u in ("us", "eu", "ca")},
            {"us": 57, "eu": 51, "ca": 0},
        )
        self.assertEqual(len(g5_rejects), 16)
        self.assertEqual(
            {u: sum(1 for uu, _ in g5_rejects if uu == u) for u in ("us", "eu", "ca")},
            {"us": 9, "eu": 7, "ca": 0},
        )
        expected_g5_ids = {
            ("us", "BA"), ("us", "INTU"), ("us", "ROP"), ("us", "PANW"), ("us", "CSGP"),
            ("us", "CCI"), ("us", "ES"), ("us", "SO"), ("us", "D"),
            ("eu", "ABI.BE"), ("eu", "DGE.GB"), ("eu", "NESN.CH"), ("eu", "RTO.GB"),
            ("eu", "DIM.FR"), ("eu", "SRT3.DE"), ("eu", "ADP.FR"),
        }
        self.assertEqual(set(g5_rejects), expected_g5_ids)

    def test_note_hygiene_across_all_124_stage2_diagnostic_rows(self):
        g3_rows = [(u, r) for u, r in self.all_rows if r.get("1") == "Y" and r.get("2") == "Y"]
        stage2_diag = []
        for u, r in g3_rows:
            if r.get("3a") == "None" or r.get("3b") == "N":
                continue
            if int(r["4"]) < 15 or r.get("5") == "0":
                stage2_diag.append((u, r))

        self.assertEqual(len(stage2_diag), 124)

        stale_bypass_re = re.compile(
            r"Downstream\s+(?:gates?(?:\s*5[-–]6|\s*6)?\s+)?bypassed\s+per\s+(?:strict\s+)?waterfall\.?",
            re.IGNORECASE,
        )
        diag_re = re.compile(r"\[Diagnostic G5=([012]) \| G6=([YN]):\s*([^\]]+)\]")

        for u, r in stage2_diag:
            cid = r["id"]
            note = r.get("note", "")
            self.assertIsNone(
                stale_bypass_re.search(note),
                f"{u}:{cid} still has stale bypass text in note: {note!r}",
            )
            m = diag_re.search(note)
            self.assertIsNotNone(m, f"{u}:{cid} missing [Diagnostic G5=<0|1|2> | G6=<Y|N>: ...] in note: {note!r}")
            if m is not None:
                self.assertEqual(m.group(1), r.get("5"), f"{u}:{cid} diagnostic G5 in note != column '5'")
                self.assertEqual(m.group(2), r.get("6"), f"{u}:{cid} diagnostic G6 in note != column '6'")
                self.assertGreater(len(m.group(3).strip()), 5, f"{u}:{cid} diagnostic rationale too short")

        # CRM note must reflect CAP = 5Y (no stale CAP = 10)
        crm = next(r for u, r in stage2_diag if u == "us" and r["id"] == "CRM")
        crm_note = crm.get("note", "")
        self.assertRegex(crm_note, r"\bCAP\s*=\s*5Y\b")
        self.assertNotRegex(crm_note, r"\bCAP\s*=\s*10\b")


class DashboardV718UITests(unittest.TestCase):
    """R3: Dashboard v7.19 UI, Growth at ~0g tab, stepper sub-labels, G5/G6 cards, table columns, and version bump."""

    @classmethod
    def setUpClass(cls):
        cls.data = collect_screener_data(["us", "eu", "ca"])
        cls.html = build_dashboard_html(cls.data)

    def test_config_version_and_changelog_v719(self):
        self.assertEqual(C.SCREENER_VERSION, "7.19")
        self.assertIn("7.19", C.CHANGELOG)
        self.assertIsInstance(C.CHANGELOG["7.19"], list)
        self.assertGreater(len(C.CHANGELOG["7.19"]), 0)
        self.assertIn("7.19", self.html)

    def test_dashboard_html_contains_v719_cards_and_table_columns(self):
        for token in (
            "dossier-g5-mgmt",
            "dossier-g6-cash",
            "dossier-g6-answer",
            "Management &amp; Allocation (G5)",
            "Cash &amp; Fortress B/S (G6)",
            "g5_mgmt",
            "G5 Mgmt",
            "g6_cash",
            "G6 B/S",
            "💎 Growth at ~0g",
            "💎 ~0g Growth",
            "kpi-growth-0g",
            "count-growth-0g",
        ):
            # Support either raw '&' or '&amp;' in HTML/JS template
            alt = token.replace("&amp;", "&")
            self.assertTrue(token in self.html or alt in self.html, f"Missing v7.19 UI token: {token}")

        self.assertIn(
            "cols = [...coreValuationCols, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.sector];",
            self.html,
        )
        self.assertIn(
            "cols = [...coreValuationCols, ALL_COLS.g5_mgmt, ALL_COLS.g6_cash, ALL_COLS.result, ALL_COLS.rejected_at, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.sector];",
            self.html,
        )
        # Verify compactKeys unchanged
        self.assertIn(
            "'cur_mult', 'par_mult', 'term_mult', 'g_market', 'sales_1_3_5y', 'g_org_exp', 'g4_cap', 'roic_used'",
            self.html,
        )

    def test_dashboard_runtime_js_openDrawer_and_renderTable_via_jsc(self):
        if shutil.which("osascript") is None:
            self.skipTest("osascript (JavaScriptCore) not available")

        scripts = re.findall(r"<script[^>]*>(.*?)</script>", self.html, flags=re.S)
        self.assertGreaterEqual(len(scripts), 2)
        raw_json, main_js = scripts[0], scripts[1]

        jxa_harness = r"""
ObjC.import('Foundation');
function readFile(p) { return $.NSString.stringWithContentsOfFileEncodingError(p, $.NSUTF8StringEncoding, null).js; }
function run(argv) {
  const src = readFile(argv[0]);
  const json = readFile(argv[1]);
  const handler = {
    get: (t, p) => {
      if (p === Symbol.toPrimitive) return () => '';
      if (p === 'length') return 0;
      if (p === 'style' || p === 'dataset') return {};
      if (p === 'classList') return { add() {}, remove() {}, toggle() {}, contains() { return false; } };
      return U;
    },
    apply: () => U,
    set: () => true,
  };
  const U = new Proxy(function () {}, handler);
  const elements = {};
  const el = (id) => {
    if (!elements[id]) {
      const base = {
        id, style: {}, dataset: {}, textContent: '', innerHTML: '', value: '', className: '',
        options: [], children: [],
        classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
        addEventListener() {}, setAttribute() {}, getAttribute() { return null; }, appendChild() {},
        querySelectorAll() { return []; }, querySelector() { return U; }, focus() {}, scrollIntoView() {}, closest() { return U; }
      };
      elements[id] = new Proxy(base, {
        get: (t, p) => (p in t ? t[p] : U),
        set: (t, p, v) => { t[p] = v; return true; },
      });
    }
    return elements[id];
  };
  const doc = {
    getElementById: (id) => id === 'screener-raw-data' ? { textContent: json } : el(id),
    querySelectorAll: () => [], querySelector: () => U, addEventListener() {}, createElement: () => el('_tmp' + Math.random()),
    body: U, documentElement: U,
  };
  const fakeConsole = { log() {}, error() {}, warn() {} };
  const probe = `
    function inspectDrawer(cid) {
      openDrawer(cid);
      const row = document.getElementById('dossier-g56-row');
      return {
        stepper: document.getElementById('dossier-stepper').innerHTML,
        g56Display: row.style.display || '',
        g5Mgmt: document.getElementById('dossier-g5-mgmt').textContent,
        g6Cash: document.getElementById('dossier-g6-cash').textContent,
        g6Ans: document.getElementById('dossier-g6-answer').textContent,
      };
    }
    function inspectTable(tab, compact, sampleRows) {
      currentTab = tab;
      compactColumns = compact;
      renderTable(sampleRows);
      return {
        head: document.getElementById('table-head').innerHTML,
        body: document.getElementById('table-body').innerHTML,
      };
    }
    function inspectGrowth0gFilter() {
      document.getElementById('filter-search').value = '';
      document.getElementById('filter-sector').value = 'all';
      document.getElementById('filter-moat').value = 'all';
      document.getElementById('filter-gate').value = 'all';
      document.getElementById('filter-val').value = 'all';
      currentMarket = 'all';
      setTab('growth_0g');
      const gateDisplay = document.getElementById('filter-gate').style.display || '';
      const allCount = sortData(getFilteredData()).length;
      const defaultSort = { col: sortColumn, asc: sortAsc };
      document.getElementById('filter-gate').value = 'Quality pass';
      const primeFilteredCount = getFilteredData().length;
      const resetVisible = hasActiveFilters();
      document.getElementById('filter-gate').value = 'all';
      return { gateDisplay, allCount, defaultSort, primeFilteredCount, resetVisible };
    }
    const byId = Object.fromEntries(SCREENER_DATA.companies.map(c => [c.universe + ':' + c.id, c]));
    const sample = [
      byId['us:COST'],
      byId['us:BA'],
      byId['us:CRM'],
      byId['us:EL'],
      byId['us:NUE'],
    ].filter(Boolean);
    return {
      cost: inspectDrawer('COST'),
      ba: inspectDrawer('BA'),
      crm: inspectDrawer('CRM'),
      el: inspectDrawer('EL'),
      googl: inspectDrawer('GOOGL'),
      nue: inspectDrawer('NUE'),
      tbl_moat_exp: inspectTable('moat_universe', false, sample),
      tbl_all_exp: inspectTable('all', false, sample),
      tbl_qpass_exp: inspectTable('qpass', false, sample),
      tbl_g0_exp: inspectTable('growth_0g', false, sample),
      tbl_g0_cmp: inspectTable('growth_0g', true, sample),
      tbl_moat_cmp: inspectTable('moat_universe', true, sample),
      tbl_all_cmp: inspectTable('all', true, sample),
      g0_filter: inspectGrowth0gFilter(),
    };
  `;
  const fn = new Function(
    'document', 'window', 'console', 'localStorage', 'navigator', 'setTimeout', 'alert', 'prompt', 'location', 'history',
    src + '\n' + probe
  );
  const win = { addEventListener() {}, location: U, innerWidth: 1400, matchMedia: () => ({ matches: false, addEventListener() {} }) };
  const res = fn(doc, win, fakeConsole, { getItem() { return null; }, setItem() {} }, U, () => 0, () => {}, () => {}, U, U);
  return JSON.stringify(res);
}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            js_path = tmp / "main.js"
            json_path = tmp / "data.json"
            harness_path = tmp / "v718_ui_harness.js"
            js_path.write_text(main_js, encoding="utf-8")
            json_path.write_text(raw_json, encoding="utf-8")
            harness_path.write_text(jxa_harness, encoding="utf-8")

            proc = subprocess.run(
                ["osascript", "-l", "JavaScript", str(harness_path), str(js_path), str(json_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            out = json.loads(proc.stdout.strip())

        # 1. COST (Quality Pass, CAP 30Y, G5=2 -> ELITE, G6=Y -> Pass)
        cost = out["cost"]
        self.assertIn("PASS · 30Y", cost["stepper"])
        self.assertIn("ELITE", cost["stepper"])
        self.assertIn("PASS", cost["stepper"])
        self.assertNotEqual(cost["g56Display"], "none")
        self.assertEqual(cost["g5Mgmt"], "Elite Compounder")
        self.assertEqual(cost["g6Cash"], "Pass")
        self.assertEqual(cost["g6Ans"], "Y")

        # 2. BA (Gate 5 = 0 Reject — verifies JS falsy 0 handling)
        ba = out["ba"]
        self.assertIn("FAIL", ba["stepper"])
        self.assertNotEqual(ba["g56Display"], "none")
        self.assertEqual(ba["g5Mgmt"], "Red Flag")
        self.assertIn(ba["g6Ans"], ("Y", "N"))

        # 3. CRM (Gate 4 < 15 Reject with CAP = 5Y and diagnostic G5/G6)
        crm = out["crm"]
        self.assertIn("FAIL · 5Y", crm["stepper"])
        self.assertNotEqual(crm["g56Display"], "none")
        self.assertEqual(crm["g5Mgmt"], "Red Flag")
        self.assertEqual(crm["g6Cash"], "Pass")
        self.assertEqual(crm["g6Ans"], "Y")

        # 4. EL (Gate 3 Reject after calamity retirement — G4/G5/G6 are BLANK)
        el = out["el"]
        self.assertNotIn("WAIVED", el["stepper"])
        self.assertIn("BLANK", el["stepper"])
        self.assertEqual(el["g56Display"], "none")
        self.assertEqual(el["g6Ans"], "blank")

        # 5. GOOGL (Former calamity 3b=Y — Stage-2 G6 FAIL without WAIVED)
        googl = out["googl"]
        self.assertNotIn("WAIVED", googl["stepper"])
        self.assertIn("PASS · 20Y", googl["stepper"])
        self.assertNotEqual(googl["g56Display"], "none")
        self.assertEqual(googl["g5Mgmt"], "Standard Pass")
        self.assertEqual(googl["g6Cash"], "Fail")
        self.assertEqual(googl["g6Ans"], "N")

        # 6. NUE (Gate 3 Reject — G4/G5/G6 remain BLANK and 2-card G5/G6 row hidden)
        nue = out["nue"]
        self.assertIn("BLANK", nue["stepper"])
        self.assertEqual(nue["g56Display"], "none")
        self.assertEqual(nue["g6Ans"], "blank")

        # 7. Table columns: G5 Mgmt and G6 B/S present in expanded moat_universe, all, and both growth_0g modes
        for tab_key in ("tbl_moat_exp", "tbl_all_exp", "tbl_g0_exp", "tbl_g0_cmp"):
            self.assertIn("G5 Mgmt", out[tab_key]["head"], f"Missing G5 Mgmt in {tab_key}")
            self.assertIn("G6 B/S", out[tab_key]["head"], f"Missing G6 B/S in {tab_key}")
            self.assertIn("0/2", out[tab_key]["body"], f"Missing 0/2 cell in {tab_key}")
            self.assertIn("2/2", out[tab_key]["body"], f"Missing 2/2 cell in {tab_key}")

        for tab_key in ("tbl_g0_exp", "tbl_g0_cmp"):
            self.assertIn("Gate Status", out[tab_key]["head"], f"Missing Gate Status in {tab_key}")
            self.assertIn("Failing Gate", out[tab_key]["head"], f"Missing Failing Gate in {tab_key}")

        for tab_key in ("tbl_qpass_exp", "tbl_moat_cmp", "tbl_all_cmp"):
            self.assertNotIn("G5 Mgmt", out[tab_key]["head"], f"Unexpected G5 Mgmt in {tab_key}")
            self.assertNotIn("G6 B/S", out[tab_key]["head"], f"Unexpected G6 B/S in {tab_key}")

        # 8. Growth at ~0g runtime tab state, default sort, and #filter-gate
        g0f = out["g0_filter"]
        self.assertEqual(g0f["gateDisplay"], "inline-block")
        self.assertEqual(g0f["allCount"], 25)
        self.assertEqual(g0f["defaultSort"], {"col": "g_org_exp", "asc": False})
        self.assertEqual(g0f["primeFilteredCount"], 9)
        self.assertTrue(g0f["resetVisible"])

    def test_built_output_html_files_exist_and_match_v719(self):
        for rel in ("output/screener.html", "output/index.html", "docs/index.html"):
            path = ROOT / rel
            self.assertTrue(path.exists(), f"Missing built artifact: {rel}")
            text = path.read_text(encoding="utf-8")
            self.assertIn("7.19", text, f"{rel} not rebuilt at v7.19")
            self.assertIn("dossier-g5-mgmt", text, f"{rel} missing v7.19 G5/G6 dossier cards")
            self.assertIn("💎 Growth at ~0g", text, f"{rel} missing Growth at ~0g tab")


class SpecConsistencyV718Tests(unittest.TestCase):
    """R3: QUALITATIVE_EVALUATION_SPEC.md and COMPANY_EVALUATION_SPEC.md match v7.19 Two-Stage Waterfall."""

    def test_specs_document_v719_two_stage_waterfall(self):
        for fname in ("QUALITATIVE_EVALUATION_SPEC.md", "COMPANY_EVALUATION_SPEC.md"):
            with self.subTest(spec=fname):
                text = (ROOT / fname).read_text(encoding="utf-8")
                first_lines = "\n".join(text.splitlines()[:15])
                self.assertIn("v7.19", first_lines, f"{fname} header not updated to v7.19")
                self.assertIn("Two-Stage", text, f"{fname} missing Two-Stage Waterfall documentation")
                self.assertNotIn("calamit", text.lower(), f"{fname} still references calamity")
                # Gate 4 / Gate 5 must NOT instruct leaving Gate 5/6 blank when Gate 4 or Gate 5 fails
                self.assertNotIn("Leave Gates 5–6 completely blank/null.", text)
                self.assertNotIn("Leave Gate 6 completely blank/null.", text)


if __name__ == "__main__":
    unittest.main()
