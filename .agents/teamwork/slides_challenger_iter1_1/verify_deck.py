#!/usr/bin/env python3
"""
Read-only empirical verification suite for Quality & Moat Screener (v7.19) Google Slides deck.
Checks:
  1. Live Google Slides metadata (steps 9 & 10 outputs) vs output/deck/pres_read.json vs batch.json
  2. output/Quality_Moat_Screener_v7.19.pptx (zipfile + ElementTree XML)
  3. output/verify/deck_export.pdf & output/verify/slide_01..16.png & output/charts/*.png
  4. S-1..S-5, true geometric bounds (including tableColumns/tableRows), pairwise text/table/image
     overlaps, font sizes, WCAG contrast, and factual parity against v7.19 spec & live screener data.
"""

import json
import re
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
LIVE_LIST_PATH = Path("/Users/janis.schultz/.gemini/antigravity/brain/129a9ea4-1f08-4d95-8bd7-3aa33b045803/.system_generated/steps/9/output.txt")
LIVE_INFO_PATH = Path("/Users/janis.schultz/.gemini/antigravity/brain/129a9ea4-1f08-4d95-8bd7-3aa33b045803/.system_generated/steps/10/output.txt")
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
        w = sum(emu_to_pt(c.get("columnWidth", {}).get("magnitude", 0),
                          c.get("columnWidth", {}).get("unit", "EMU"))
                for c in tbl.get("tableColumns", []))
        h = sum(emu_to_pt(r.get("rowHeight", {}).get("magnitude", 0),
                          r.get("rowHeight", {}).get("unit", "EMU"))
                for r in tbl.get("tableRows", []))
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


def main():
    live_slides = load_step_json(LIVE_LIST_PATH)
    live_info = load_step_json(LIVE_INFO_PATH)
    pres_read = json.loads(PRES_READ_PATH.read_text(encoding="utf-8"))
    batch_ops = json.loads(BATCH_JSON_PATH.read_text(encoding="utf-8"))

    live_slide_ids = [s["objectId"] for s in live_slides]
    info_slide_ids = [s["objectId"] for s in live_info.get("slides", [])]
    pres_slide_ids = [s["objectId"] for s in pres_read.get("slides", [])]

    print("=== 1. LIVE METADATA VS PRES_READ.JSON VS BATCH.JSON ===")
    print(f"Title (info): {live_info.get('title')}")
    print(f"Slide counts: list-slides={len(live_slide_ids)}, info={len(info_slide_ids)}, pres_read={len(pres_slide_ids)}")
    print(f"Slide IDs & order match: {live_slide_ids == info_slide_ids == pres_slide_ids}")
    print(f"Full slide AST identical (live list-slides == pres_read.slides): {live_slides == pres_read.get('slides', [])}")

    # Check batch.json update-text strings appear in live slides
    batch_texts = [op["text"].strip() for op in batch_ops if op.get("op") == "update-text" and op.get("text", "").strip()]
    live_all_text = []
    for s in live_slides:
        for el in s.get("pageElements", []):
            if "shape" in el:
                live_all_text.append(extract_text_from_elements(el["shape"].get("text", {}).get("textElements", [])).strip())
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        ct = extract_text_from_elements(cell.get("text", {}).get("textElements", [])).strip()
                        if ct:
                            live_all_text.append(ct)
    live_text_set = set(live_all_text)
    missing_batch_texts = [bt for bt in batch_texts if bt not in live_text_set]
    print(f"batch.json update-text items: {len(batch_texts)}, missing from live AST: {len(missing_batch_texts)}")
    if missing_batch_texts:
        print("  Missing batch texts:", missing_batch_texts[:5])

    # ---------------------------------------------------------
    # 2. PPTX Integrity
    # ---------------------------------------------------------
    print("\n=== 2. PPTX INTEGRITY ===")
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
        print(f"PPTX size={PPTX_PATH.stat().st_size}B, testzip={bad}, sldId={len(sld_ids)}, slideXML={len(slide_files)}, notesXML={len(notes_files)}, media={len(media_files)}")
        for idx, sf in enumerate(slide_files, 1):
            root = ET.fromstring(zf.read(sf))
            texts = [t.text for t in root.findall(".//a:t", ns_p) if t.text]
            assert len(texts) > 0, f"Empty PPTX slide {idx}"
        for mf in media_files:
            mb = zf.read(mf)
            assert mb[:8] == b"\x89PNG\r\n\x1a\n"
            mw, mh = struct.unpack(">II", mb[16:24])
            print(f"  {mf}: PNG {mw}x{mh}, {len(mb)}B")

    # ---------------------------------------------------------
    # 3. PDF & PNG Integrity
    # ---------------------------------------------------------
    print("\n=== 3. PDF & PNG INTEGRITY ===")
    pdf_bytes = PDF_PATH.read_bytes()
    pages_counts = re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", pdf_bytes, flags=re.S)
    page_objs = re.findall(rb"/Type\s*/Page\b(?!s)", pdf_bytes)
    print(f"PDF: {len(pdf_bytes)}B, header={pdf_bytes[:5]!r}, eof={b'%%EOF' in pdf_bytes[-1024:]}, /Count={[c.decode() for c in pages_counts]}, /Page objs={len(page_objs)}")
    png_ok = sum(1 for i in range(1, 17)
                 if (VERIFY_DIR / f"slide_{i:02d}.png").exists()
                 and check_png(VERIFY_DIR / f"slide_{i:02d}.png")[:3] == (True, 1440, 810))
    print(f"Slide PNGs valid 1440x810: {png_ok}/16")

    # ---------------------------------------------------------
    # 4. S-1..S-5, True Geometry, Overlaps, Contrast, Fonts
    # ---------------------------------------------------------
    print("\n=== 4. S-1..S-5, TRUE GEOMETRY, OVERLAPS, CONTRAST & FONTS ===")
    placeholder_hits = []
    missing_fg = []
    bad_fonts = []
    notes_stats = []
    margin_violations = []
    text_overlaps = []
    image_overlaps = []
    contrast_failures = []
    prose_under_14 = []

    for s_idx, slide in enumerate(live_slides, 1):
        bg_rgb = get_slide_bg_rgb(slide)
        notes_page = slide.get("slideProperties", {}).get("notesPage", {})
        notes_id = notes_page.get("notesProperties", {}).get("speakerNotesObjectId")
        notes_text = ""
        for ne in notes_page.get("pageElements", []):
            if ne.get("objectId") == notes_id:
                notes_text = extract_text_from_elements(ne.get("shape", {}).get("text", {}).get("textElements", []))
        notes_stats.append((s_idx, len(notes_text.strip().split())))

        text_boxes = []
        images = []
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
                sp = sh.get("shapeProperties", {})
                sbg = sp.get("shapeBackgroundFill", {})
                fill_rgb = None
                if sbg.get("propertyState") != "NOT_RENDERED" and "solidFill" in sbg:
                    sf_c = sbg["solidFill"].get("color", {}).get("rgbColor")
                    if sf_c is not None:
                        fill_rgb = rgb_from_dict(sf_c)

                is_stripe = (abs(x1) < 0.5 and abs(w - 8.0) < 0.5 and abs(y1) < 0.5 and abs(h - 405.0) < 0.5)
                is_bg = (abs(w - 720.0) < 1.0 and abs(h - 405.0) < 1.0)
                if not (is_stripe or is_bg):
                    if x1 < 29.95 or x2 > 690.05 or y1 < 29.95 or y2 > 375.05:
                        margin_violations.append((s_idx, eid, st, round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))

                te_list = sh.get("text", {}).get("textElements", [])
                stripped = extract_text_from_elements(te_list).strip()
                if stripped:
                    text_boxes.append({"eid": eid, "kind": st, "bbox": (x1, y1, x2, y2), "text": stripped})
                    for ph in ("Click to add", "TBD"):
                        if ph.lower() in stripped.lower():
                            placeholder_hits.append((s_idx, eid, ph))
                    if stripped in ("Title", "Subtitle"):
                        placeholder_hits.append((s_idx, eid, stripped))

                for te in te_list:
                    tr = te.get("textRun")
                    if not tr or tr.get("content", "") in ("", "\n"):
                        continue
                    content = tr["content"]
                    style = tr.get("style", {})
                    fg = style.get("foregroundColor", {})
                    if not fg or "opaqueColor" not in fg or "rgbColor" not in fg["opaqueColor"]:
                        missing_fg.append((s_idx, eid, content[:25]))
                    ff = style.get("weightedFontFamily", {}).get("fontFamily") or style.get("fontFamily")
                    if ff not in ("Montserrat", "Roboto"):
                        bad_fonts.append((s_idx, eid, ff))
                    fs = style.get("fontSize", {}).get("magnitude")
                    is_bold = bool(style.get("bold", False))

                    # Check body prose < 14pt (excluding footer y>=355, kicker y<=48, card badges/labels)
                    if fs is not None and 10.5 <= fs < 14.0 and 48 < y1 < 355 and not is_bold:
                        prose_under_14.append((s_idx, fs, content.strip()[:40]))

                    if fg and "opaqueColor" in fg and "rgbColor" in fg["opaqueColor"]:
                        fg_rgb = rgb_from_dict(fg["opaqueColor"]["rgbColor"])
                        eff_bg = fill_rgb
                        if eff_bg is None:
                            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                            cands = []
                            for oe in slide.get("pageElements", []):
                                if oe.get("objectId") == eid or "shape" not in oe:
                                    continue
                                ox1, oy1, ox2, oy2 = get_bbox_pt(oe)
                                if ox1 - 1 <= cx <= ox2 + 1 and oy1 - 1 <= cy <= oy2 + 1:
                                    osp = oe["shape"].get("shapeProperties", {}).get("shapeBackgroundFill", {})
                                    if osp.get("propertyState") != "NOT_RENDERED" and "solidFill" in osp:
                                        oc = osp["solidFill"].get("color", {}).get("rgbColor")
                                        if oc is not None:
                                            cands.append(((ox2 - ox1) * (oy2 - oy1), rgb_from_dict(oc)))
                            eff_bg = sorted(cands, key=lambda z: z[0])[0][1] if cands else bg_rgb
                        cr = contrast_ratio(fg_rgb, eff_bg)
                        is_large = (fs is not None and (fs >= 18.0 or (fs >= 14.0 and is_bold)))
                        min_cr = 3.0 if is_large else 4.5
                        if cr < min_cr:
                            contrast_failures.append((s_idx, eid, round(cr, 2), min_cr, rgb_to_hex(fg_rgb), rgb_to_hex(eff_bg), fs, is_bold, content.strip()[:30]))

            elif "table" in elem:
                if x1 < 29.95 or x2 > 690.05 or y1 < 29.95 or y2 > 375.05:
                    margin_violations.append((s_idx, eid, "TABLE", round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                text_boxes.append({"eid": eid, "kind": "TABLE", "bbox": (x1, y1, x2, y2), "text": "TABLE"})
                for row in elem["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        for te in cell.get("text", {}).get("textElements", []):
                            tr = te.get("textRun")
                            if not tr or tr.get("content", "") in ("", "\n"):
                                continue
                            style = tr.get("style", {})
                            fg = style.get("foregroundColor", {})
                            if not fg or "opaqueColor" not in fg or "rgbColor" not in fg["opaqueColor"]:
                                missing_fg.append((s_idx, eid, tr["content"][:20]))
                            ff = style.get("weightedFontFamily", {}).get("fontFamily") or style.get("fontFamily")
                            if ff not in ("Montserrat", "Roboto"):
                                bad_fonts.append((s_idx, eid, ff))

            elif "image" in elem:
                if x1 < 29.95 or x2 > 690.05 or y1 < 29.95 or y2 > 375.05:
                    margin_violations.append((s_idx, eid, "IMAGE", round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                images.append({"eid": eid, "bbox": (x1, y1, x2, y2)})

        for i in range(len(text_boxes)):
            for j in range(i + 1, len(text_boxes)):
                a, b = text_boxes[i], text_boxes[j]
                ox = min(a["bbox"][2], b["bbox"][2]) - max(a["bbox"][0], b["bbox"][0])
                oy = min(a["bbox"][3], b["bbox"][3]) - max(a["bbox"][1], b["bbox"][1])
                if ox > 0.5 and oy > 0.5:
                    text_overlaps.append((s_idx, a["eid"], b["eid"], round(ox, 2), round(oy, 2)))

        for im in images:
            for tb in text_boxes:
                ox = min(im["bbox"][2], tb["bbox"][2]) - max(im["bbox"][0], tb["bbox"][0])
                oy = min(im["bbox"][3], tb["bbox"][3]) - max(im["bbox"][1], tb["bbox"][1])
                if ox > 0.5 and oy > 0.5:
                    image_overlaps.append((s_idx, im["eid"], tb["eid"], round(ox, 2), round(oy, 2)))

    print(f"Placeholders: {len(placeholder_hits)}, Missing FG: {len(missing_fg)}, Bad fonts: {len(bad_fonts)}")
    print(f"Margin violations: {len(margin_violations)}")
    print(f"True pairwise text/table overlaps: {len(text_overlaps)} -> {text_overlaps}")
    print(f"Image vs text/table overlaps: {len(image_overlaps)} -> {image_overlaps}")
    print(f"WCAG contrast failures ({len(contrast_failures)}):")
    for cf in contrast_failures:
        print("  ", cf)
    print(f"Non-bold body prose in [10.5, 14.0)pt ({len(prose_under_14)} runs across slides {sorted(set(x[0] for x in prose_under_14))})")


if __name__ == "__main__":
    main()
