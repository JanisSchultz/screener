"""Tests for dashboard filtering, specifically the 'Rejected at Gate X' filters."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.dashboard import build_dashboard_html, collect_screener_data


class DashboardGateFilterTests(unittest.TestCase):
    def test_dashboard_html_contains_gate_filter_logic(self):
        """Verify the generated dashboard HTML contains the fix for Gate 1-6 prefix matching."""
        data = {
            "version": "7.19",
            "generated_at": "2026-11-18T00:00:00Z",
            "summary": {"total_companies": 0, "quality_pass": 0, "growth_0g": 0, "valued": 0, "median_excess_irr": 0.0},
            "sectors": [],
            "moats": [],
            "universes": {},
            "companies": [],
            "changelog": [],
        }
        html = build_dashboard_html(data)
        # Check that the gate matching logic uses num extraction and checks G prefix
        self.assertIn("const gPrefix = 'G' + num;", html)
        self.assertIn("rejAt.startsWith(gPrefix)", html)
        self.assertIn("growth_0g: { col: 'g_org_exp', asc: false }", html)
        self.assertIn("tab === 'growth_0g'", html)
        for label in ("Prime Grade", "Growth at ~0g", "💎 Growth at ~0g", "💎 ~0g Growth", "Quality Grade", "Full Universe"):
            self.assertIn(label, html)
        for old_label in ("Prime Grade Calamity", "Calamity pass", "Quality Pass Funnel", "Calamity Watchlist", "Moat Universe", "Full Universe &amp; Waterfall", "Full Universe & Waterfall"):
            self.assertNotIn(old_label, html)

    def test_quality_grade_covers_g1_g2_g3_and_g6_flags(self):
        """Verify Prime Grade, Growth at ~0g, and Quality Grade all require g6_flags < 3."""
        screener_data = collect_screener_data(["us", "eu", "ca"])
        companies = screener_data["companies"]
        qg = [c for c in companies if c.get("passes_quality_grade")]
        self.assertEqual(len(qg), 443)
        for c in qg:
            st = c["gate_status"]
            self.assertEqual(st.get("1"), "pass")
            self.assertEqual(st.get("2"), "pass")
            self.assertNotIn(c.get("g3a_moat_archetype"), (None, "", "None"))
            self.assertEqual(st.get("3b"), "pass")
            self.assertLess(c.get("g6_flags"), 3)
        self.assertTrue(any(c.get("id") == "NFLX" for c in qg), "NFLX (1 G6 flag) should be in Quality Grade")

        pg = [c for c in companies if c.get("passes_prime_grade")]
        self.assertEqual(len(pg), 225)
        for c in pg:
            self.assertEqual(c.get("result"), "Quality pass")
            self.assertLess(c.get("g6_flags"), 3)

        g0 = [c for c in companies if c.get("passes_growth_0g")]
        self.assertEqual(len(g0), 25)
        self.assertEqual(sum(1 for c in g0 if c.get("passes_prime_grade")), 9)
        self.assertEqual(sum(1 for c in g0 if not c.get("passes_prime_grade") and (c.get("g4_cap") or 0) >= 15), 6)
        self.assertEqual(sum(1 for c in g0 if (c.get("g4_cap") or 0) < 15), 10)

    def test_gate_filter_matches_rejected_companies(self):
        """Ensure each 'Rejected at Gate X' filter matches the actual companies in the screener data."""
        screener_data = collect_screener_data(["us"])
        companies = screener_data["companies"]

        # Simulate the exact JS filter logic
        def js_filter(gate: str, tab: str = "all") -> list[dict]:
            result = []
            for c in companies:
                if tab == "all" and gate != "all":
                    if gate == "Quality pass" and c.get("result") != "Quality pass":
                        continue
                    if gate.startswith("Gate") or gate.startswith("G"):
                        num = re.sub(r"[^0-9]", "", gate)
                        if num:
                            g_prefix = "G" + num
                            gate_prefix = "Gate " + num
                            rej_at = c.get("rejected_at") or ""
                            res = c.get("result") or ""
                            matches = (
                                rej_at.startswith(g_prefix)
                                or rej_at.startswith(gate_prefix)
                                or (g_prefix in res)
                            )
                            if not matches:
                                continue
                result.append(c)
            return result

        # In US universe, there are rejected companies across gates
        for g_num in range(1, 7):
            matched = js_filter(f"Gate {g_num}")
            self.assertGreater(
                len(matched),
                0,
                f"Gate {g_num} filter returned 0 matches; expected rejected companies.",
            )
            for c in matched:
                rej_at = c.get("rejected_at", "")
                self.assertTrue(
                    rej_at.startswith(f"G{g_num}"),
                    f"Company {c.get('ticker')} has unexpected rejected_at: {rej_at}",
                )


if __name__ == "__main__":
    unittest.main()
