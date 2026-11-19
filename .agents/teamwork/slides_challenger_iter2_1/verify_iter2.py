#!/usr/bin/env python3
"""
Independent empirical verification harness for Iteration 2 of:
Quality & Moat Screener (v7.19) — Google Slides Deck 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ

Read-only script residing inside .agents/teamwork/slides_challenger_iter2_1/.
Does NOT modify any file in output/ or the repository.
"""

import json
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
LIVE_LIST_PATH = Path("/Users/janis.schultz/.gemini/antigravity/brain/1b621f0f-b0fa-4cff-9962-ba92bfb7ba97/.system_generated/steps/11/output.txt")
LIVE_INFO_PATH = Path("/Users/janis.schultz/.gemini/antigravity/brain/1b621f0f-b0fa-4cff-9962-ba92bfb7ba97/.system_generated/steps/12/output.txt")
PRES_READ_PATH = ROOT / "output/deck/pres_read.json"
BATCH_JSON_PATH = ROOT / "output/deck/batch.json"
PPTX_PATH = ROOT / "output/Quality_Moat_Screener_v7.19.pptx"
PDF_PATH = ROOT / "output/verify/deck_export.pdf"
VERIFY_DIR = ROOT / "output/verify"
CHARTS_DIR = ROOT / "output/charts"

EMU_PER_PT = 12700.0


def load_step_json(path: Path):
    text = path.read_text(encoding="utf-8")
    idx = text.find("Command output:\n")
    if idx != -1:
        text = text[idx + len("Command output:\n"):]
    return json.loads(text)


def emu_to_pt(val, unit="EMU"):
    if val is None:
        return 0.0
    if unit == "PT":
        return float(val)
    return float(val) / EMU_PER_PT


def get_bbox_pt(elem):
    """Return (x1, y1, x2, y2) in PT on 720x405 canvas. Uses tableColumns/tableRows for tables."""
    tr = elem.get("transform", {})
    sx = float(tr.get("scaleX", 1.0))
    sy = float(tr.get("scaleY", 1.0))
    tx = emu_to_pt(tr.get("translateX", 0), tr.get("unit", "EMU"))
    ty = emu_to_pt(tr.get("translateY", 0), tr.get("unit", "EMU"))

    if "table" in elem:
        tbl = elem["table"]
        w = sum(
            emu_to_pt(c.get("columnWidth", {}).get("magnitude", 0),
                      c.get("columnWidth", {}).get("unit", "EMU"))
            for c in tbl.get("tableColumns", [])
        )
        h = sum(
            emu_to_pt(r.get("rowHeight", {}).get("magnitude", 0),
                      r.get("rowHeight", {}).get("unit", "EMU"))
            for r in tbl.get("tableRows", [])
        )
        return (tx, ty, tx + w, ty + h)

    size = elem.get("size", {})
    w_obj = size.get("width", {})
    h_obj = size.get("height", {})
    w_base = emu_to_pt(w_obj.get("magnitude", 0), w_obj.get("unit", "EMU"))
    h_base = emu_to_pt(h_obj.get("magnitude", 0), h_obj.get("unit", "EMU"))
    w = w_base * abs(sx)
    h = h_base * abs(sy)
    x1 = tx if sx >= 0 else tx - w
    y1 = ty if sy >= 0 else ty - h
    return (x1, y1, x1 + w, y1 + h)


def rgb_from_dict(c):
    return (float(c.get("red", 0.0)), float(c.get("green", 0.0)), float(c.get("blue", 0.0)))


def blend_rgb(fg, bg, alpha):
    return tuple(alpha * f + (1.0 - alpha) * b for f, b in zip(fg, bg))


def rgb_to_hex(rgb):
    r, g, b = [max(0, min(255, round(v * 255))) for v in rgb]
    return f"#{r:02X}{g:02X}{b:02X}"


def rel_lum(rgb):
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast_ratio(rgb1, rgb2):
    l1, l2 = rel_lum(rgb1), rel_lum(rgb2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def extract_text_from_elements(text_elements):
    return "".join(te["textRun"].get("content", "") for te in (text_elements or []) if "textRun" in te)


def get_slide_bg_rgb(slide):
    bg = slide.get("pageProperties", {}).get("pageBackgroundFill", {})
    sf = bg.get("solidFill", {})
    if sf and "color" in sf and "rgbColor" in sf["color"]:
        return rgb_from_dict(sf["color"]["rgbColor"])
    return (1.0, 1.0, 1.0)


def check_png(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False, 0, 0, len(data), "Invalid PNG signature"
    if data[12:16] != b"IHDR":
        return False, 0, 0, len(data), "Missing IHDR"
    w, h = struct.unpack(">II", data[16:24])
    return True, w, h, len(data), "OK"


def resolve_z_bg(slide, target_idx, target_bbox):
    """
    Resolve effective background RGB behind element at target_idx by compositing
    z-ordered shapes below target_idx (index 0 .. target_idx-1) whose bbox overlaps target_bbox
    (specifically containing the center of target_bbox or having >= 50% area overlap).
    """
    tx1, ty1, tx2, ty2 = target_bbox
    cx, cy = (tx1 + tx2) / 2.0, (ty1 + ty2) / 2.0
    curr_rgb = get_slide_bg_rgb(slide)
    elems = slide.get("pageElements", [])
    for j in range(target_idx):
        oe = elems[j]
        if "shape" not in oe:
            continue
        ox1, oy1, ox2, oy2 = get_bbox_pt(oe)
        if not (ox1 - 0.5 <= cx <= ox2 + 0.5 and oy1 - 0.5 <= cy <= oy2 + 0.5):
            continue
        osp = oe["shape"].get("shapeProperties", {}).get("shapeBackgroundFill", {})
        if osp.get("propertyState") == "NOT_RENDERED" or "solidFill" not in osp:
            continue
        sf = osp["solidFill"]
        oc = sf.get("color", {}).get("rgbColor")
        if oc is None:
            continue
        alpha = float(sf.get("alpha", 1.0))
        curr_rgb = blend_rgb(rgb_from_dict(oc), curr_rgb, alpha)
    return curr_rgb


def main():
    live_slides = load_step_json(LIVE_LIST_PATH)
    live_info = load_step_json(LIVE_INFO_PATH)
    pres_read = json.loads(PRES_READ_PATH.read_text(encoding="utf-8"))
    batch_ops = json.loads(BATCH_JSON_PATH.read_text(encoding="utf-8"))

    # =========================================================
    # 1. EXACT LIVE AST PARITY & BATCH PARITY
    # =========================================================
    print("=== 1. LIVE AST PARITY & BATCH PARITY ===")
    live_ids = [s["objectId"] for s in live_slides]
    info_ids = [s["objectId"] for s in live_info.get("slides", [])]
    pres_ids = [s["objectId"] for s in pres_read.get("slides", [])]

    def strip_ephemeral(obj):
        if isinstance(obj, list):
            return [strip_ephemeral(x) for x in obj]
        if isinstance(obj, dict):
            return {k: strip_ephemeral(v) for k, v in obj.items() if k != "contentUrl"}
        return obj

    print(f"Presentation title: {live_info.get('title')}")
    print(f"Slide counts: list-slides={len(live_ids)}, info={len(info_ids)}, pres_read={len(pres_ids)}")
    print(f"Slide IDs & order identical: {live_ids == info_ids == pres_ids}")
    print(f"Full slide AST identical (live list-slides == info.slides): {live_slides == live_info.get('slides', [])}")
    print(f"Full slide AST identical raw (live list-slides == pres_read.slides): {live_slides == pres_read.get('slides', [])}")
    print(f"Full slide AST identical modulo ephemeral image.contentUrl (live == pres_read): {strip_ephemeral(live_slides) == strip_ephemeral(pres_read.get('slides', []))}")

    # Collect all batch text strings and speaker notes
    batch_add_tb = [op["text"].strip() for op in batch_ops if op.get("op") == "add-textbox" and op.get("text", "").strip()]
    batch_cell = [op["text"].strip() for op in batch_ops if op.get("op") == "set-table-cell" and op.get("text", "").strip()]
    batch_all_texts = batch_add_tb + batch_cell
    batch_notes = [op["text"].strip() for op in batch_ops if op.get("op") == "set-notes"]

    live_shape_texts = []
    live_cell_texts = []
    live_notes = []
    for s in live_slides:
        for el in s.get("pageElements", []):
            if "shape" in el:
                t = extract_text_from_elements(el["shape"].get("text", {}).get("textElements", [])).strip()
                if t:
                    live_shape_texts.append(t)
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        t = extract_text_from_elements(cell.get("text", {}).get("textElements", [])).strip()
                        if t:
                            live_cell_texts.append(t)
        np = s.get("slideProperties", {}).get("notesPage", {})
        nid = np.get("notesProperties", {}).get("speakerNotesObjectId")
        nt = ""
        for ne in np.get("pageElements", []):
            if ne.get("objectId") == nid:
                nt = extract_text_from_elements(ne.get("shape", {}).get("text", {}).get("textElements", [])).strip()
        live_notes.append(nt)

    live_all_texts = live_shape_texts + live_cell_texts
    missing_texts = [t for t in batch_all_texts if t not in set(live_all_texts)]
    extra_texts = [t for t in live_all_texts if t not in set(batch_all_texts)]
    # Exact multiset / ordered comparison
    exact_text_multiset_eq = (sorted(batch_all_texts) == sorted(live_all_texts))
    exact_notes_eq = (batch_notes == live_notes)

    print(f"Batch ops total: {len(batch_ops)}")
    print(f"Batch text strings: add-textbox={len(batch_add_tb)} + set-table-cell={len(batch_cell)} = {len(batch_all_texts)}")
    print(f"Live text strings: shape={len(live_shape_texts)} + table-cell={len(live_cell_texts)} = {len(live_all_texts)}")
    print(f"Missing batch texts in live: {len(missing_texts)}, Extra live texts not in batch: {len(extra_texts)}")
    print(f"Exact text multiset parity (batch == live): {exact_text_multiset_eq}")
    print(f"Batch notes count: {len(batch_notes)}, Live notes count: {len(live_notes)}, Exact ordered notes parity: {exact_notes_eq}")

    # =========================================================
    # 2. ALL 302 TEXT RUNS WCAG 2.0 CONTRAST AUDIT
    # =========================================================
    print("\n=== 2. EXHAUSTIVE 302-RUN WCAG 2.0 CONTRAST AUDIT (SHAPES + TABLES) ===")
    shape_runs = 0
    cell_runs = 0
    wcag_failures = []
    missing_fg = []
    bad_fonts = []
    all_crs = []
    spot_checks = {}

    target_eids = {
        "textbox_1795014495931827000_131",
        "textbox_1795014495931840000_141",
        "textbox_1795014495931910000_205",
        "textbox_1795014495931902000_198",
        "textbox_1795014495932139000_311",
        "textbox_1795014495932275000_383",
        "textbox_1795014495932282000_388",
        "textbox_1795014495932292000_393",
        "textbox_1795014495932299000_398",
    }
    target_cells = {(3, 3), (4, 3), (5, 3), (6, 0), (6, 3), (6, 4)}

    for s_idx, slide in enumerate(live_slides, 1):
        elems = slide.get("pageElements", [])
        for idx, elem in enumerate(elems):
            eid = elem.get("objectId", "")
            bbox = get_bbox_pt(elem)

            if "shape" in elem:
                sh = elem["shape"]
                sp = sh.get("shapeProperties", {})
                sbg = sp.get("shapeBackgroundFill", {})
                underlying = resolve_z_bg(slide, idx, bbox)
                eff_bg = underlying
                if sbg.get("propertyState") != "NOT_RENDERED" and "solidFill" in sbg:
                    sf = sbg["solidFill"]
                    oc = sf.get("color", {}).get("rgbColor")
                    if oc is not None:
                        alpha = float(sf.get("alpha", 1.0))
                        eff_bg = blend_rgb(rgb_from_dict(oc), underlying, alpha)

                for te in sh.get("text", {}).get("textElements", []):
                    tr = te.get("textRun")
                    if not tr or not tr.get("content", "").strip():
                        continue
                    shape_runs += 1
                    content = tr["content"].strip()
                    style = tr.get("style", {})
                    fg = style.get("foregroundColor", {})
                    if not fg or "opaqueColor" not in fg or "rgbColor" not in fg["opaqueColor"]:
                        missing_fg.append((s_idx, eid, content[:30]))
                        continue
                    fg_rgb = rgb_from_dict(fg["opaqueColor"]["rgbColor"])
                    ff = style.get("weightedFontFamily", {}).get("fontFamily") or style.get("fontFamily")
                    if ff not in ("Montserrat", "Roboto"):
                        bad_fonts.append((s_idx, eid, ff, content[:25]))
                    fs = style.get("fontSize", {}).get("magnitude")
                    is_bold = bool(style.get("bold", False))
                    is_large = (fs is not None and (fs >= 18.0 or (fs >= 14.0 and is_bold)))
                    req_cr = 3.0 if is_large else 4.5
                    cr = contrast_ratio(fg_rgb, eff_bg)
                    all_crs.append((cr, s_idx, eid, rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, content[:35]))
                    if cr < req_cr:
                        wcag_failures.append((s_idx, eid, round(cr, 2), req_cr, rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, content[:35]))
                    if eid in target_eids:
                        spot_checks[eid] = (s_idx, round(cr, 2), req_cr, rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, ff, content)

            elif "table" in elem:
                underlying = resolve_z_bg(slide, idx, bbox)
                for r_idx, row in enumerate(elem["table"].get("tableRows", [])):
                    for c_idx, cell in enumerate(row.get("tableCells", [])):
                        cbg = cell.get("tableCellProperties", {}).get("tableCellBackgroundFill", {})
                        eff_bg = underlying
                        if cbg.get("propertyState") != "NOT_RENDERED" and "solidFill" in cbg:
                            sf = cbg["solidFill"]
                            oc = sf.get("color", {}).get("rgbColor")
                            if oc is not None:
                                alpha = float(sf.get("alpha", 1.0))
                                eff_bg = blend_rgb(rgb_from_dict(oc), underlying, alpha)

                        for te in cell.get("text", {}).get("textElements", []):
                            tr = te.get("textRun")
                            if not tr or not tr.get("content", "").strip():
                                continue
                            cell_runs += 1
                            content = tr["content"].strip()
                            style = tr.get("style", {})
                            fg = style.get("foregroundColor", {})
                            if not fg or "opaqueColor" not in fg or "rgbColor" not in fg["opaqueColor"]:
                                missing_fg.append((s_idx, f"{eid}[{r_idx},{c_idx}]", content[:30]))
                                continue
                            fg_rgb = rgb_from_dict(fg["opaqueColor"]["rgbColor"])
                            ff = style.get("weightedFontFamily", {}).get("fontFamily") or style.get("fontFamily")
                            if ff not in ("Montserrat", "Roboto"):
                                bad_fonts.append((s_idx, f"{eid}[{r_idx},{c_idx}]", ff, content[:25]))
                            fs = style.get("fontSize", {}).get("magnitude")
                            is_bold = bool(style.get("bold", False))
                            is_large = (fs is not None and (fs >= 18.0 or (fs >= 14.0 and is_bold)))
                            req_cr = 3.0 if is_large else 4.5
                            cr = contrast_ratio(fg_rgb, eff_bg)
                            all_crs.append((cr, s_idx, f"{eid}[{r_idx},{c_idx}]", rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, content[:35]))
                            if cr < req_cr:
                                wcag_failures.append((s_idx, f"{eid}[{r_idx},{c_idx}]", round(cr, 2), req_cr, rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, content[:35]))
                            if s_idx == 15 and (r_idx, c_idx) in target_cells:
                                spot_checks[f"table[{r_idx},{c_idx}]"] = (s_idx, round(cr, 2), req_cr, rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, ff, content)

    total_runs = shape_runs + cell_runs
    min_cr_entry = min(all_crs, key=lambda x: x[0])
    print(f"Total non-whitespace runs audited: {total_runs} (shape={shape_runs}, table-cell={cell_runs})")
    print(f"Missing foregroundColor: {len(missing_fg)}, Non-Montserrat/Roboto fonts: {len(bad_fonts)}")
    print(f"WCAG 2.0 contrast failures: {len(wcag_failures)}")
    for wf in wcag_failures:
        print("  FAIL:", wf)
    print(f"Lowest CR across all {total_runs} runs: {min_cr_entry[0]:.2f}:1 on Slide {min_cr_entry[1]} {min_cr_entry[2]} ({min_cr_entry[3]} on {min_cr_entry[4]}, {min_cr_entry[5]}pt bold={min_cr_entry[6]}, {min_cr_entry[7]!r})")
    print("Targeted spot-checks (previously failing + bumped elements):")
    for k in sorted(spot_checks):
        v = spot_checks[k]
        print(f"  {k}: Slide {v[0]} CR={v[1]}:1 (req {v[2]}:1) {v[3]}->{v[4]} {v[5]}pt bold={v[6]} {v[7]} {v[8]!r}")

    # =========================================================
    # 3. SLIDE 08 & SLIDE 12 LIVE GEOMETRY + DISTORTION CHECK
    # =========================================================
    print("\n=== 3. SLIDE 08 & SLIDE 12 LIVE GEOMETRY & SCALE/DISTORTION ===")
    for slide_num, prefix_ids in [(8, [f"_{n}" for n in range(237, 246)]),
                                  (12, [f"_{n}" for n in range(359, 371)])]:
        s = live_slides[slide_num - 1]
        print(f"Slide {slide_num:02d} targeted elements:")
        for el in s.get("pageElements", []):
            eid = el.get("objectId", "")
            if any(eid.endswith(sfx) for sfx in prefix_ids):
                tr = el.get("transform", {})
                sx = tr.get("scaleX", 1.0)
                sy = tr.get("scaleY", 1.0)
                shx = tr.get("shearX", 0.0)
                shy = tr.get("shearY", 0.0)
                x1, y1, x2, y2 = get_bbox_pt(el)
                txt = extract_text_from_elements(el.get("shape", {}).get("text", {}).get("textElements", [])).strip().replace("\n", " | ")[:45]
                print(f"  {eid}: x={x1:.2f}, y={y1:.2f}, w={x2-x1:.2f}, h={y2-y1:.2f}, y2={y2:.2f} | scaleX={sx:.6f}, scaleY={sy:.6f}, shear=({shx},{shy}) | {txt!r}")

    # Check ALL elements across ALL 16 slides for transform distortion / shear / extreme sizes
    anomalies = []
    image_aspect_checks = []
    for s_idx, slide in enumerate(live_slides, 1):
        for el in slide.get("pageElements", []):
            eid = el.get("objectId", "")
            tr = el.get("transform", {})
            sx = float(tr.get("scaleX", 1.0))
            sy = float(tr.get("scaleY", 1.0))
            shx = float(tr.get("shearX", 0.0))
            shy = float(tr.get("shearY", 0.0))
            x1, y1, x2, y2 = get_bbox_pt(el)
            w, h = x2 - x1, y2 - y1
            if abs(shx) > 1e-6 or abs(shy) > 1e-6 or sx <= 0 or sy <= 0 or w > 725 or h > 410:
                anomalies.append((s_idx, eid, w, h, sx, sy, shx, shy))
            if "image" in el:
                image_aspect_checks.append((s_idx, eid, round(w, 2), round(h, 2), round(w / h, 4), round(sx, 4), round(sy, 4)))
    print(f"Transform/bbox anomalies across all 16 slides: {len(anomalies)} -> {anomalies}")
    print(f"Image bboxes & aspect ratios: {image_aspect_checks}")

    # =========================================================
    # 4. MARGINS, OVERLAPS, PLACEHOLDERS, NOTES, PPTX, PDF, PNG
    # =========================================================
    print("\n=== 4. MARGINS, OVERLAPS, PLACEHOLDERS, SPEAKER NOTES ===")
    placeholder_hits = []
    margin_violations = []
    text_overlaps = []
    image_overlaps = []
    notes_words = []

    for s_idx, slide in enumerate(live_slides, 1):
        np = slide.get("slideProperties", {}).get("notesPage", {})
        nid = np.get("notesProperties", {}).get("speakerNotesObjectId")
        nt = ""
        for ne in np.get("pageElements", []):
            if ne.get("objectId") == nid:
                nt = extract_text_from_elements(ne.get("shape", {}).get("text", {}).get("textElements", []))
        notes_words.append((s_idx, len(nt.strip().split())))

        tbs = []
        imgs = []
        for elem in slide.get("pageElements", []):
            eid = elem.get("objectId", "")
            if re.search(r"(^|_)i[01]$", eid):
                placeholder_hits.append((s_idx, eid, "objectId"))
            x1, y1, x2, y2 = get_bbox_pt(elem)
            w, h = x2 - x1, y2 - y1

            if "shape" in elem:
                sh = elem["shape"]
                if "placeholder" in sh:
                    placeholder_hits.append((s_idx, eid, f"placeholder={sh['placeholder']}"))
                st = sh.get("shapeType", "")
                is_stripe = (abs(x1) < 0.5 and abs(w - 8.0) < 0.5 and abs(y1) < 0.5 and abs(h - 405.0) < 0.5)
                is_bg = (abs(w - 720.0) < 1.0 and abs(h - 405.0) < 1.0)
                if not (is_stripe or is_bg):
                    if x1 < 29.95 or x2 > 690.05 or y1 < 29.95 or y2 > 375.05:
                        margin_violations.append((s_idx, eid, st, round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                stripped = extract_text_from_elements(sh.get("text", {}).get("textElements", [])).strip()
                if stripped:
                    tbs.append({"eid": eid, "bbox": (x1, y1, x2, y2)})
                    for ph in ("Click to add", "TBD"):
                        if ph.lower() in stripped.lower():
                            placeholder_hits.append((s_idx, eid, ph))
                    if stripped in ("Title", "Subtitle"):
                        placeholder_hits.append((s_idx, eid, stripped))
            elif "table" in elem:
                if x1 < 29.95 or x2 > 690.05 or y1 < 29.95 or y2 > 375.05:
                    margin_violations.append((s_idx, eid, "TABLE", round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                tbs.append({"eid": eid, "bbox": (x1, y1, x2, y2)})
            elif "image" in elem:
                if x1 < 29.95 or x2 > 690.05 or y1 < 29.95 or y2 > 375.05:
                    margin_violations.append((s_idx, eid, "IMAGE", round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                imgs.append({"eid": eid, "bbox": (x1, y1, x2, y2)})

        for i in range(len(tbs)):
            for j in range(i + 1, len(tbs)):
                a, b = tbs[i], tbs[j]
                ox = min(a["bbox"][2], b["bbox"][2]) - max(a["bbox"][0], b["bbox"][0])
                oy = min(a["bbox"][3], b["bbox"][3]) - max(a["bbox"][1], b["bbox"][1])
                if ox > 0.5 and oy > 0.5:
                    text_overlaps.append((s_idx, a["eid"], b["eid"], round(ox, 2), round(oy, 2)))
        for im in imgs:
            for tb in tbs:
                ox = min(im["bbox"][2], tb["bbox"][2]) - max(im["bbox"][0], tb["bbox"][0])
                oy = min(im["bbox"][3], tb["bbox"][3]) - max(im["bbox"][1], tb["bbox"][1])
                if ox > 0.5 and oy > 0.5:
                    image_overlaps.append((s_idx, im["eid"], tb["eid"], round(ox, 2), round(oy, 2)))

    print(f"Placeholders: {len(placeholder_hits)} -> {placeholder_hits}")
    print(f"Margin violations: {len(margin_violations)} -> {margin_violations}")
    print(f"Pairwise text/table overlaps: {len(text_overlaps)} -> {text_overlaps}")
    print(f"Image vs text/table overlaps: {len(image_overlaps)} -> {image_overlaps}")
    print(f"Speaker notes word counts (min={min(w for _, w in notes_words)}, max={max(w for _, w in notes_words)}): {notes_words}")

    # =========================================================
    # 5. PPTX, PDF, PNG INTEGRITY + LIVE-TO-PPTX SYNC CHECK
    # =========================================================
    print("\n=== 5. PPTX, PDF & PNG INTEGRITY + LIVE-TO-PPTX SYNC ===")
    ns_p = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    with zipfile.ZipFile(PPTX_PATH, "r") as zf:
        bad = zf.testzip()
        names = set(zf.namelist())
        pres_xml = ET.fromstring(zf.read("ppt/presentation.xml"))
        sld_ids = pres_xml.findall(".//p:sldIdLst/p:sldId", ns_p)
        slide_files = sorted([n for n in names if re.match(r"^ppt/slides/slide\d+\.xml$", n)],
                             key=lambda x: int(re.search(r"(\d+)", x).group(1)))
        notes_files = sorted([n for n in names if re.match(r"^ppt/notesSlides/notesSlide\d+\.xml$", n)],
                             key=lambda x: int(re.search(r"(\d+)", x).group(1)))
        media_files = sorted([n for n in names if n.startswith("ppt/media/")])
        print(f"PPTX: size={PPTX_PATH.stat().st_size}B, testzip={bad}, sldIds={len(sld_ids)}, slideXML={len(slide_files)}, notesXML={len(notes_files)}, media={len(media_files)}")
        for mf in media_files:
            mb = zf.read(mf)
            assert mb[:8] == b"\x89PNG\r\n\x1a\n"
            mw, mh = struct.unpack(">II", mb[16:24])
            print(f"  {mf}: PNG {mw}x{mh}, {len(mb)}B")

        # Verify Slide 13 & Notes 13 & Slide 11 & Slide 08/12 text inside PPTX XML (proves PPTX was re-exported after iter2 fixes!)
        s11_xml = "".join(t.text for t in ET.fromstring(zf.read("ppt/slides/slide11.xml")).findall(".//a:t", ns_p) if t.text)
        s13_xml = "".join(t.text for t in ET.fromstring(zf.read("ppt/slides/slide13.xml")).findall(".//a:t", ns_p) if t.text)
        n13_xml = "".join(t.text for t in ET.fromstring(zf.read("ppt/notesSlides/notesSlide13.xml")).findall(".//a:t", ns_p) if t.text)
        print(f"PPTX Slide 11 has '6% refranchising cap': {'6% refranchising cap' in s11_xml}")
        print(f"PPTX Slide 13 has 'Exact formula 0g / 3% max terminal P/E': {'Exact formula 0g / 3% max terminal P/E' in s13_xml}")
        print(f"PPTX Slide 13 has 'Current Price vs Fair Value vs 0g Floor': {'Current Price vs Fair Value vs 0g Floor' in s13_xml}")
        print(f"PPTX Notes 13 has 'MUV2.DE' and '10.88x': {'MUV2.DE' in n13_xml and '10.88x' in n13_xml}")

        # Verify Slide 5/7/15 colors in PPTX XML match #9A3412 / #92400E / #CADCFC
        s5_raw = zf.read("ppt/slides/slide5.xml").decode("utf-8")
        s7_raw = zf.read("ppt/slides/slide7.xml").decode("utf-8")
        s15_raw = zf.read("ppt/slides/slide15.xml").decode("utf-8")
        print(f"PPTX Slide 5 has 9A3412 (not C2410C): {'9A3412' in s5_raw and 'C2410C' not in s5_raw}")
        print(f"PPTX Slide 7 has CADCFC for '51': {'CADCFC' in s7_raw}")
        print(f"PPTX Slide 15 has 9A3412 & 92400E (not C2410C/B45309): {'9A3412' in s15_raw and '92400E' in s15_raw and 'C2410C' not in s15_raw and 'B45309' not in s15_raw}")

    pdf_bytes = PDF_PATH.read_bytes()
    pages_counts = re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", pdf_bytes, flags=re.S)
    page_objs = re.findall(rb"/Type\s*/Page\b(?!s)", pdf_bytes)
    print(f"PDF: size={len(pdf_bytes)}B, header={pdf_bytes[:5]!r}, eof={b'%%EOF' in pdf_bytes[-1024:]}, /Count={[c.decode() for c in pages_counts]}, /Page objs={len(page_objs)}")

    png_results = []
    for i in range(1, 17):
        p = VERIFY_DIR / f"slide_{i:02d}.png"
        ok, w, h, sz, msg = check_png(p) if p.exists() else (False, 0, 0, 0, "Missing")
        png_results.append((i, ok, w, h, sz))
    all_png_ok = all(ok and w == 1440 and h == 810 for _, ok, w, h, _ in png_results)
    print(f"Slide PNGs 1..16 valid 1440x810: {sum(1 for _, ok, w, h, _ in png_results if ok and w == 1440 and h == 810)}/16 (all_ok={all_png_ok})")


if __name__ == "__main__":
    main()
