"""Tests for the dashboard passcode lock gate (code 6767 + progressive lockout)."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.dashboard import build_dashboard_html


def _minimal_data() -> dict:
    return {
        "version": "7.19",
        "generated_at": "2026-11-21T00:00:00Z",
        "summary": {
            "total_companies": 0,
            "quality_pass": 0,
            "growth_0g": 0,
            "valued": 0,
            "median_excess_irr": 0.0,
        },
        "sectors": [],
        "moats": [],
        "universes": {},
        "companies": [],
        "changelog": [],
    }


class PasscodeLockGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.html = build_dashboard_html(_minimal_data())

    def test_body_starts_locked_and_hides_non_gate_content(self):
        self.assertIn('<body class="passcode-locked">', self.html)
        self.assertIn(
            "body.passcode-locked > :not(#passcode-gate) {\n      display: none !important;\n    }",
            self.html,
        )

    def test_passcode_gate_markup_and_keypad_present(self):
        self.assertIn('id="passcode-gate"', self.html)
        self.assertIn('role="dialog"', self.html)
        self.assertIn('aria-modal="true"', self.html)
        for dot_idx in range(4):
            self.assertIn(f'data-dot="{dot_idx}"', self.html)
        for digit in range(10):
            self.assertIn(f'data-digit="{digit}"', self.html)
        self.assertIn('data-action="clear"', self.html)
        self.assertIn('data-action="backspace"', self.html)

    def test_passcode_constants_and_progressive_lockout_logic(self):
        self.assertIn("const PASSCODE = '6767';", self.html)
        self.assertIn("const MAX_ATTEMPTS = 3;", self.html)
        self.assertIn("const BASE_LOCKOUT_SECONDS = 30;", self.html)
        self.assertIn("const MAX_LOCKOUT_SECONDS = 900;", self.html)
        self.assertIn(
            "BASE_LOCKOUT_SECONDS * Math.pow(2, state.lockoutCount - 1)",
            self.html,
        )

    def test_session_and_local_storage_persistence(self):
        self.assertIn("const SESSION_KEY = 'screener_passcode_unlocked';", self.html)
        self.assertIn("const STATE_KEY = 'screener_passcode_state';", self.html)
        self.assertIn("window.sessionStorage.getItem(SESSION_KEY)", self.html)
        self.assertIn("window.sessionStorage.setItem(SESSION_KEY, '1')", self.html)
        self.assertIn("window.localStorage.getItem(STATE_KEY)", self.html)
        self.assertIn("window.localStorage.setItem(STATE_KEY, JSON.stringify(st))", self.html)

    def test_init_is_deferred_behind_passcode_gate(self):
        self.assertIn("document.addEventListener('DOMContentLoaded', startPasscodeGate);", self.html)
        self.assertNotIn("document.addEventListener('DOMContentLoaded', init);", self.html)

    def test_no_unescaped_double_braces_in_passcode_section(self):
        start = self.html.index("/* Passcode Lock Gate */")
        end = self.html.index("</style>", start)
        css_chunk = self.html[start:end]
        self.assertNotIn("{{", css_chunk)
        self.assertNotIn("}}", css_chunk)

        js_start = self.html.index("// Passcode Lock Gate Controller")
        js_end = self.html.index("</script>", js_start)
        js_chunk = self.html[js_start:js_end]
        self.assertNotIn("{{", js_chunk)
        self.assertNotIn("}}", js_chunk)
        # Ensure template literal interpolations rendered as single ${...}
        self.assertTrue(re.search(r"\$\{mins\}:\$\{String\(rem\)", js_chunk))


if __name__ == "__main__":
    unittest.main()
