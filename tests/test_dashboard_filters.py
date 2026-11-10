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
            "version": "6.27",
            "generated_at": "2026-11-10T00:00:00Z",
            "summary": {"total_companies": 0, "quality_pass": 0, "calamity_pass": 0, "calamity_below_par": 0, "below_par": 0, "median_irr_below_par": 0.0},
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
                    if gate == "Calamity pass" and c.get("result") != "Calamity pass":
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
