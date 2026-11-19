# Geometry & In-Place Mutation Spec — `slides_explorer_iter2_2` (Hard Handoff)

**Summary:** Direct pixel/point audit of `slide_08.png` and `slide_12.png` (`1440×810 px` = `2.0 px/pt`) plus `pres_read.json` confirms a `3.5 pt` bottom overflow on Slide 08 Pillar ③ (`y=337.5` vs `y=334.0`) and `0 to −2 pt` bottom-border collision on Slide 12 Cards 1 & 2 (`y=173.5` vs `172.0`; `y=261.0` vs `259.0`). Exact in-place `gslides mutate batch` patches (`resize-element` with explicit `x,y,width,height`, `move-element`, `style-text`, `update-text`) fix all targets on `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` with `>= 8.0 pt` bottom clearance and zero copy loss.

---

## 1. Observation

### 1.1 Slide 08 (`slide_1795014495931926000_219`) — Exact AST & Rendered PNG Measurements
From `output/deck/pres_read.json`, `output/deck/build_batch.py` (lines 338–367), and direct PNG scan of `output/verify/slide_08.png` (`1440×810 px`, `2.0 px/pt`):
- **Outer Gate 6 Card:** `shape_1795014495931941000_232` (`x=365, y=92, w=325, h=258`, bottom `y=350.0`); inner fill `shape_1795014495931941000_233` (`x=366, y=93, w=323, h=256`, inner bottom verified at pixel `y=698..699` → `pt y=349.0..349.5`).
- **Gate 6 Header & Subtitle:** `textbox_1795014495931943000_235` (`y=102, h=22`), `textbox_1795014495931945000_236` (`y=126, h=18`; rendered ink band `y=140.0..147.0`).
- **Left Gate 5 Textbox (symmetry reference):** `textbox_1795014495931940000_231` (`y=152, h=184` → bottom `y=336.0`, `13.0 pt` above inner border `349.0`).
- **Gate 6 Pillars ①–③ (all have `autofitType: NONE`, `base=(236.22×236.22)`):**
  - **Pillar ① (`#E8EEF7`):** `shape_1795014495931947000_237` (`x=379, y=148, w=297, h=57.99` → `148..206`). Title `textbox_1795014495931948000_238` (`x=389, y=152, w=277, h=18`, `13.5 pt` Montserrat Bold; ink `160.0..173.5`). Body `textbox_1795014495931949000_239` (`x=389, y=171, w=277, h=32`, `12.5 pt` Roboto, `lineSpacing=108`; 1 line ink `180.5..193.0`). **Bottom padding inside tint box: `206.0 − 193.0 = 13.0 pt`.**
  - **Pillar ② (`#E8EEF7`):** `shape_1795014495931950000_240` (`x=379, y=212, w=297, h=57.99` → `212..270`). Title `textbox_1795014495931951000_241` (`y=216`, ink `224.0..237.5`). Body `textbox_1795014495931953000_242` (`y=235, h=32`; 1 line ink `244.5..257.0`). **Bottom padding inside tint box: `270.0 − 257.0 = 13.0 pt`.**
  - **Pillar ③ (`#E8EEF7`):** `shape_1795014495931954000_243` (`x=379, y=276, w=297, h=57.99` → `276..334`). Title `textbox_1795014495931955000_244` (`y=280`, ink `288.0..301.5`). Body `textbox_1795014495931956000_245` (`y=299, h=32`; 2 lines `"Net Debt/OE ≤ 4.0y, EBIT/Int > 5.0× (infra &"` / `"Solvency II > 200% contextual)."` — line 1 ink `308.0..321.0`, line 2 ink `324.5..337.5`). **Bottom padding: `334.0 − 337.5 = −3.5 pt` (direct overflow outside tint box).**

### 1.2 Slide 12 (`slide_1795014495932222000_352`) — Exact AST & Rendered PNG Measurements
From `output/deck/pres_read.json`, `output/deck/build_batch.py` (lines 495–505), and direct PNG scan of `output/verify/slide_12.png` (`1440×810 px`, `2.0 px/pt`, measuring `#283582` fill vs `#3949A6` border at card center `x=550 pt` and text ink `max RGB > 180` across `x=422..678 pt`):
- **Left Chart:** `SLIDES_API1805855454_0` at `x=30, y=94, w=365, h=252` (`y=94..346`).
- **Right Card 1 (`ROUND_RECTANGLE`, `cy=92, h=81`):**
  - Border `shape_1795014495932236000_359` (`x=410, y=92, w=280, h=81` → `92..173`); inner fill `shape_1795014495932238000_360` (`x=411, y=93, w=278, h=79`, rendered fill `y=93.0..172.0`).
  - Title `textbox_1795014495932239000_361` (`y=98, h=20`, `14 pt` Montserrat Bold; ink `107.5..118.5`).
  - Body `textbox_1795014495932241000_362` (`y=119, h=48`, `12.5 pt` Roboto, `lineSpacing=110`; 3 lines: `128.5..140.5`, `144.0..157.5`, `160.5..173.5`). **Line 3 `"financials)."` reaches `173.5 pt` vs inner fill bottom `172.0 pt` (`−1.5 pt`, touching border).**
- **Right Card 2 (`ROUND_RECTANGLE`, `cy=179, h=81`):**
  - Border `shape_1795014495932242000_363` (`x=410, y=179, w=280, h=81` → `179..260`); inner fill `shape_1795014495932244000_364` (rendered fill `y=180.0..259.0`).
  - Title `textbox_1795014495932246000_365` (`y=185, h=20`; ink `194.5..208.0` due to `g` descender).
  - Body `textbox_1795014495932248000_366` (`y=206, h=48`, `12.5 pt` Roboto; 3 lines: `214.5..228.0`, `231.0..244.5`, `247.5..261.0`). **Line 3 `"E_t(1−g_t/RONIC_t)."` reaches `261.0 pt` vs inner fill bottom `259.0 pt` (`−2.0 pt`, subscript `t`/parens overlap border).**
- **Right Card 3 (`ROUND_RECTANGLE`, `cy=266, h=81`):**
  - Border `shape_1795014495932250000_367` (`y=266..347`), inner fill `shape_1795014495932251000_368` (`y=267.0..346.0`).
  - Title `textbox_1795014495932252000_369` (`y=272`, ink `281.0..295.5`); Body `textbox_1795014495932256000_370` (`y=293`, 2 lines: `302.5..314.5`, `318.0..331.5`). **Inner bottom clearance: `346.0 − 331.5 = 14.5 pt`.**

### 1.3 `gslides mutate` In-Place Capability Audit (`gslides-986250228`)
Verified via `gslides mutate --help`, subcommand `--help`, `SKILL.md:260-276`, `output/deck/patch_3_slides.json`, and binary inspection of `~/.gemini/antigravity/plugin_data/gslides/bin/gslides-986250228`:

| Operation | Standalone CLI (`gslides mutate ...`) | Batch JSON (`gslides mutate batch`) | Critical Caveats / Verified Evidence |
|---|---|---|---|
| `resize-element` | **Yes** (`[presID] [elemID] --width --height`) | **Yes** (`element, width, height, x, y`) | Standalone CLI lacks `--x`/`--y` and defaults `--width 100 --height 100`. Binary uses `UpdatePageElementTransform` (`ABSOLUTE` mode). **Always pass `x, y, width, height` via `batch`** so `translateX`/`translateY` are preserved. |
| `move-element` | **Yes** (`[presID] [elemID] --x --y`) | **Yes** (`element, x, y`) | Verified in `gslides mutate move-element --help` and `SKILL.md:273`. |
| `style-text` | **No** (no CLI subcommand) | **Yes** (`element, color, bold, italic, underline, strikethrough, font_size, font_family, link, start, end`) | Batch-only per `SKILL.md:268`; binary contains `UpdateTextStyle` and `buildTextStyle`. Short `<=16B` batch op literals (`style-text`, `add-shape`, `skip-slide`) are compiled as ARM64 immediates rather than `.rodata` strings (`add-shape` already proven across 100+ ops in `batch.json`). |
| `update-text` | **Yes** (`[presID] --element --text`) | **Yes** (`element, text`) | Already executed in-place on `1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ` via `output/deck/patch_3_slides.json`. |

---

## 2. Logic Chain

1. **Slide 08 Vertical Ink Model:** From Observation §1.1, Google Slides' default internal top inset shifts title ink `+8.0 pt` below `title_y` (`py+4 → py+12.0..25.5`) and body ink `+9.5 pt` below `body_y` (`py+23 → py+32.5..45.0` for 1 line; `py+61.5` for 2 lines at `12.5 pt` Roboto, `lineSpacing=108`).
2. **Slide 08 Exact Fix:** Keeping `title_y = py + 4` and `body_y = py + 23`, shrinking 1-line Pillars ① & ② from `h=58` to `h=53` leaves `53.0 − 45.0 = 8.0 pt` bottom padding. Shifting Pillar ② up `5 pt` (`y=212 → 207`) and Pillar ③ up `10 pt` (`y=276 → 266`, maintaining uniform `6 pt` inter-pillar gaps) while expanding Pillar ③ from `h=58` to `h=70` places Pillar ③'s bottom at `y=336.0` (`8.5 pt` bottom padding below `327.5 pt` line 2 ink, `13.0 pt` above Gate 6 inner border `349.0`, `<= 350.0`, and aligned to the exact `y=336.0` bottom of Gate 5 on the left). Body textbox heights also tighten/expand (`32 → 28` on ①/②, `32 → 45` on ③) so no textbox bounding box is smaller than its ink.
3. **Slide 12 Vertical Ink Model:** From Observation §1.2, inside `h=81` cards (`inner fill = 79 pt`), `title_y = cy + 6` leaves `9.5 pt` empty space above title ink (`cy + 15.5`) and `6.5–10.0 pt` below title ink to `body_y = cy + 27`, pushing 3-line bodies to `cy + 81.5..82.0` (colliding with `cy + 80.0` inner bottom). Meanwhile Card 3 (2 lines) has `14.5 pt` unused bottom padding.
4. **Slide 12 Exact Fix (Geometry + Text-Y, Zero Copy Loss):** Shifting `title_y = cy + 3` (`-3 pt`) and `body_y = cy + 23` (`-4 pt` on Cards 1–2; adjusts delta to `20 pt` so Card 2 `g` descender keeps `5.5 pt` clearance above body line 1), and redistributing card heights to `h1=87, h2=87, h3=72` with `5 pt` gaps (`cy = 92, 184, 276`, ending `y=348.0`, matching left chart `y=346.0`) yields inner bottom clearances of **`8.5 pt`** (Card 1), **`8.0 pt`** (Card 2), and **`9.5 pt`** (Card 3) with zero abbreviation of `"financials)."` or `"E_t(1−g_t/RONIC_t)."`.
5. **In-Place Patch Execution:** From Observation §1.3, `gslides mutate batch 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ -f <patch.json> --json` supports all 4 operations (`resize-element` with `x,y,width,height`, `move-element`, `style-text`, `update-text`) directly on the canonical deck, eliminating any need for a 3rd presentation.

---

## 3. Caveats

- Because `gslides` uses `UpdatePageElementTransform` (`ABSOLUTE`) and all target elements on Slides 08 and 12 currently have `base = (236.22 × 236.22)` scaled by `scaleX/scaleY`, every `resize-element` op in the batch JSON MUST explicitly include `x`, `y`, `width`, and `height` (never omit `x,y`) and should be verified immediately afterward via `gslides readonly read` + PDF/PNG re-render.
- **Secondary Optional Variant (Slide 12 Card 1 Copy Tightening):** If a 2-line Card 1 is also desired later, replacing `"Discount rate r = 8.50% (operating) or 10.25% (BS financials)."` with `"Hurdle r = 8.50% (operating) or 10.25% (BS fin.)."` fits 2 lines (`~14.5 pt` clearance), but is unnecessary given the geometry + text-y fix already provides `8.5 pt` clearance with full verbatim copy.
- Slide 05 (`#C2410C → #9A3412` via `style-text`) and Slides 07/10/13/14 font bumps (`style-text`) are outside this explorer's geometry scope (handled by sibling explorer / worker), though confirmed compatible with `gslides mutate batch`.

---

## 4. Conclusion — Exact Patch Specifications

### 4.1 Exact `gslides mutate batch` JSON Ops (Slides 08 & 12)

```json
[
  {"op": "resize-element", "element": "shape_1795014495931947000_237", "x": 379, "y": 148, "width": 297, "height": 53},
  {"op": "resize-element", "element": "textbox_1795014495931949000_239", "x": 389, "y": 171, "width": 277, "height": 28},

  {"op": "resize-element", "element": "shape_1795014495931950000_240", "x": 379, "y": 207, "width": 297, "height": 53},
  {"op": "move-element",   "element": "textbox_1795014495931951000_241", "x": 389, "y": 211},
  {"op": "resize-element", "element": "textbox_1795014495931953000_242", "x": 389, "y": 230, "width": 277, "height": 28},

  {"op": "resize-element", "element": "shape_1795014495931954000_243", "x": 379, "y": 266, "width": 297, "height": 70},
  {"op": "move-element",   "element": "textbox_1795014495931955000_244", "x": 389, "y": 270},
  {"op": "resize-element", "element": "textbox_1795014495931956000_245", "x": 389, "y": 289, "width": 277, "height": 45},

  {"op": "resize-element", "element": "shape_1795014495932236000_359",   "x": 410, "y": 92,  "width": 280, "height": 87},
  {"op": "resize-element", "element": "shape_1795014495932238000_360",   "x": 411, "y": 93,  "width": 278, "height": 85},
  {"op": "move-element",   "element": "textbox_1795014495932239000_361", "x": 422, "y": 95},
  {"op": "resize-element", "element": "textbox_1795014495932241000_362", "x": 422, "y": 115, "width": 256, "height": 56},

  {"op": "resize-element", "element": "shape_1795014495932242000_363",   "x": 410, "y": 184, "width": 280, "height": 87},
  {"op": "resize-element", "element": "shape_1795014495932244000_364",   "x": 411, "y": 185, "width": 278, "height": 85},
  {"op": "move-element",   "element": "textbox_1795014495932246000_365", "x": 422, "y": 187},
  {"op": "resize-element", "element": "textbox_1795014495932248000_366", "x": 422, "y": 207, "width": 256, "height": 56},

  {"op": "resize-element", "element": "shape_1795014495932250000_367",   "x": 410, "y": 276, "width": 280, "height": 72},
  {"op": "resize-element", "element": "shape_1795014495932251000_368",   "x": 411, "y": 277, "width": 278, "height": 70},
  {"op": "move-element",   "element": "textbox_1795014495932252000_369", "x": 422, "y": 279},
  {"op": "resize-element", "element": "textbox_1795014495932256000_370", "x": 422, "y": 299, "width": 256, "height": 44}
]
```

### 4.2 Corresponding `output/deck/build_batch.py` Sync Snippets

1. **Slide 08 (`output/deck/build_batch.py:358-367`):**
   - Replace loop:
     ```python
     # Before:
     for i, (pt, pb) in enumerate(pillars):
         py = 148 + i * 64
         add_rect(S8, 379, py, 297, 58, LIGHT_TINT, shape_type="RECTANGLE")
         add_tb(S8, pt, 389, py + 4, 277, 18, 13.5, TEAL_LIGHT, font_family="Montserrat", bold=True)
         add_tb(S8, pb, 389, py + 23, 277, 32, 12.5, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=108)

     # After:
     pillar_geom = [(148, 53, 28), (207, 53, 28), (266, 70, 45)]
     for (pt, pb), (py, ph, bh) in zip(pillars, pillar_geom):
         add_rect(S8, 379, py, 297, ph, LIGHT_TINT, shape_type="RECTANGLE")
         add_tb(S8, pt, 389, py + 4, 277, 18, 13.5, TEAL_LIGHT, font_family="Montserrat", bold=True)
         add_tb(S8, pb, 389, py + 23, 277, bh, 12.5, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=108)
     ```
2. **Slide 12 (`output/deck/build_batch.py:501-505`):**
   - Replace loop:
     ```python
     # Before:
     for i, (ct, cb, col) in enumerate(dcf_cards):
         cy = 92 + i * 87
         add_bordered_card(S12, 410, cy, 280, 81, DARK_CARD, DARK_BORDER)
         add_tb(S12, ct, 422, cy + 6, 256, 20, 14, col, font_family="Montserrat", bold=True)
         add_tb(S12, cb, 422, cy + 27, 256, 48, 12.5, TXT_DARK_BODY, font_family="Roboto", line_spacing=110)

     # After:
     card_geom = [(92, 87, 56), (184, 87, 56), (276, 72, 44)]
     for (ct, cb, col), (cy, ch, bh) in zip(dcf_cards, card_geom):
         add_bordered_card(S12, 410, cy, 280, ch, DARK_CARD, DARK_BORDER)
         add_tb(S12, ct, 422, cy + 3, 256, 20, 14, col, font_family="Montserrat", bold=True)
         add_tb(S12, cb, 422, cy + 23, 256, bh, 12.5, TXT_DARK_BODY, font_family="Roboto", line_spacing=110)
     ```

---

## 5. Verification Method

1. **Apply & Sync:** Execute the patch JSON via `gslides mutate batch 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ -f <patch.json> --json`, sync `output/deck/build_batch.py`, and run `python3 output/deck/build_batch.py` (confirming `Validation OK: 16 slides`).
2. **AST Transform Check:** Run `gslides readonly read 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --json > output/deck/pres_read.json` and verify exact `x, y, w, h` for Slide 08 (`_237.._245`) and Slide 12 (`_359.._370`).
3. **Visual Export Check:** Re-export `output/verify/deck_export.pdf` and `output/Quality_Moat_Screener_v7.19.pptx`, re-render `slide_08.png` and `slide_12.png`, inspect visually via `view_file`, and confirm:
   - Slide 08: All 3 Pillar ink bands terminate `>= 8.0 pt` above their `#E8EEF7` box bottoms (`201`, `260`, `336`), with Pillar ③ ending `13 pt` inside Gate 6 (`y=349`).
   - Slide 12: Cards 1, 2, 3 bottom lines (`"financials)."`, `"E_t(1−g_t/RONIC_t)."`, `"for any g₀."`) have `8.5 pt`, `8.0 pt`, `9.5 pt` clearance above `#283582` inner bottoms (`178`, `270`, `347`).
4. **Invalidation Condition:** Any change to font size, `line_spacing`, or `text` inside Slide 08 Gate 6 or Slide 12 right cards invalidates the pixel-derived clearance guarantees above.
