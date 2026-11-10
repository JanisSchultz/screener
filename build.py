"""Compile the standalone interactive HTML cockpit from data/ into output/screener.html.

Usage:
    python3 build.py                # all universes (US, EU, CA)
    python3 build.py us             # single universe
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from screener.dashboard import build_dashboard, collect_screener_data
from screener.data import universe_keys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("universes", nargs="*", help=f"default: all ({', '.join(universe_keys())})")
    a = ap.parse_args()

    keys = a.universes or universe_keys()
    t0 = time.time()
    
    print(f"Compiling Quality & Moat Screener HTML Cockpit for: {', '.join(keys)}...")
    data = collect_screener_data(keys)
    out_path = build_dashboard(keys)
    elapsed = time.time() - t0

    summary = data["summary"]
    print(f"\n✓ Dashboard built in {elapsed:.2f}s:")
    print(f"  • File: {out_path}")
    print(f"  • Secondary File: {out_path.parent / 'index.html'}")
    print(f"  • GitHub Pages File: docs/index.html")
    print(f"  • Total Companies: {summary['total_companies']}")
    print(f"  • Quality Pass Funnel: {summary['quality_pass']}")
    print(f"  • Calamity Watchlist (Conditional): {summary['calamity_pass']} ({summary['calamity_below_par']} Below PAR)")
    print(f"  • Below PAR Shortlist: {summary['below_par']} (Median 5Y IRR: {summary['median_irr_below_par']*100:.1f}%)")
    print(f"\nTo view, open in browser: open \"{out_path}\"")


if __name__ == "__main__":
    main()
