#!/usr/bin/env python3
"""Deep audit of Slide 10/15 table AST geometry, V-4 font hierarchy, batch.json sync, and live Screener data parity."""
import json
from pathlib import Path
import sys

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
sys.path.insert(0, str(ROOT))

PRES_READ = json.loads((ROOT / "output/deck/pres_read.json").read_text())
BATCH_JSON = json.loads((ROOT / "output/deck/batch.json").read_text())
EMU = 12700.0


def emu(v, u="EMU"):
    return float(v) if u == "PT" else float(v) / EMU


print("=== 1. TABLE AST GEOMETRY (SLIDES 10 & 15) ===")
for s_idx in (10, 15):
    slide = PRES_READ["slides"][s_idx - 1]
    print(f"Slide {s_idx}:")
    for el in slide["pageElements"]:
        eid = el["objectId"]
        sz = el.get("size", {})
        tr = el.get("transform", {})
        w = emu(sz.get("width", {}).get("magnitude", 0), sz.get("width", {}).get("unit", "EMU")) * abs(tr.get("scaleX", 1))
        h = emu(sz.get("height", {}).get("magnitude", 0), sz.get("height", {}).get("unit", "EMU")) * abs(tr.get("scaleY", 1))
        x = emu(tr.get("translateX", 0), tr.get("unit", "EMU"))
        y = emu(tr.get("translateY", 0), tr.get("unit", "EMU"))
        if "table" in el:
            row_heights = [emu(r.get("rowHeight", {}).get("magnitude", 0), r.get("rowHeight", {}).get("unit", "EMU"))
                           for r in el["table"].get("tableRows", [])]
            print(f"  TABLE {eid}: bbox=({x:.2f}, {y:.2f}, {x+w:.2f}, {y+h:.2f}) w={w:.2f} h={h:.2f}")
            print(f"    tableRows rowHeights (pt): {[round(rh, 2) for rh in row_heights]}, sum={sum(row_heights):.2f}")
        elif "shape" in el:
            txt = "".join(r.get("textRun", {}).get("content", "") for r in el["shape"].get("text", {}).get("textElements", [])).strip().replace("\n", " ")
            if txt:
                print(f"  SHAPE {eid}: bbox=({x:.2f}, {y:.2f}, {x+w:.2f}, {y+h:.2f}) text={txt[:45]!r}")

print("\n=== 2. FONT SIZE HIERARCHY AUDIT (V-4) ===")
for s_idx, slide in enumerate(PRES_READ["slides"], 1):
    sizes = []
    for el in slide["pageElements"]:
        eid = el["objectId"]
        if "shape" in el:
            for te in el["shape"].get("text", {}).get("textElements", []):
                tr = te.get("textRun")
                if not tr or tr.get("content", "") in ("", "\n"):
                    continue
                fs = tr.get("style", {}).get("fontSize", {}).get("magnitude")
                bold = tr.get("style", {}).get("bold", False)
                sizes.append((fs, bold, eid, tr["content"].strip()[:30]))
        elif "table" in el:
            for row in el["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    for te in cell.get("text", {}).get("textElements", []):
                        tr = te.get("textRun")
                        if not tr or tr.get("content", "") in ("", "\n"):
                            continue
                        fs = tr.get("style", {}).get("fontSize", {}).get("magnitude")
                        bold = tr.get("style", {}).get("bold", False)
                        sizes.append((fs, bold, eid, tr["content"].strip()[:20]))
    max_fs = max(s[0] for s in sizes if s[0] is not None)
    body_candidates = [s for s in sizes if s[0] is not None and 10.5 <= s[0] < 14.0]
    if body_candidates:
        print(f"  Slide {s_idx:02d} (max={max_fs}pt): runs in [10.5, 14.0)pt -> {[(s[0], s[1], s[3]) for s in body_candidates]}")

print("\n=== 3. LIVE SCREENER DATA PARITY (SLIDE 14 & 15) ===")
from screener.dashboard import collect_screener_data
from screener.data import universe_keys
d = collect_screener_data(universe_keys())
print("Summary keys:", d.get("summary"))
rows = d.get("rows", [])
prime = [r for r in rows if r.get("grade") == "Prime" or r.get("tier") == "Prime" or r.get("prime")]
print(f"Total rows: {len(rows)}")
by_tick = {r.get("ticker"): r for r in rows}
for t in ("MSFT", "SPGI", "ASML.NL", "COST", "WM", "CRM", "ZTS", "PGHN.CH", "PGR"):
    r = by_tick.get(t)
    if r:
        keys = {k: r.get(k) for k in ("ticker", "cap", "cur_mult", "par_mult", "term_mult", "g0", "g_market", "irr_5y", "vs_par", "price", "par_val", "term_val", "gate4", "gate6", "quality_grade", "prime_grade") if k in r}
        print(f"  {t}: {keys}")
    else:
        print(f"  {t}: NOT FOUND")
