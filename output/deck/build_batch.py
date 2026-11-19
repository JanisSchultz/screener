#!/usr/bin/env python3
"""Generate and validate output/deck/batch.json for the 16-slide Quality & Moat Screener (v7.19) deck."""

import json
from pathlib import Path

ops = []

# Palette
DARK_BG = "#1E2761"
DARK_CARD = "#283582"
DARK_CARD_ALT = "#232F70"
DARK_BORDER = "#3949A6"
LIGHT_BG = "#F5F7FA"
LIGHT_CARD = "#FFFFFF"
LIGHT_TINT = "#E8EEF7"
LIGHT_BORDER = "#D5DFED"

TXT_DARK_PRIMARY = "#FFFFFF"
TXT_DARK_BODY = "#CADCFC"
TXT_DARK_MUTED = "#A8BCE8"
TXT_LIGHT_TITLE = "#1E2761"
TXT_LIGHT_BODY = "#1F2937"
TXT_LIGHT_MUTED = "#4B5563"

TEAL_DARK = "#2DD4BF"
TEAL_LIGHT = "#0F766E"
AMBER_DARK = "#FBBF24"
AMBER_LIGHT = "#92400E"
CORAL_DARK = "#FB923C"
CORAL_LIGHT = "#9A3412"


def add_rect(slide, x, y, w, h, bg, shape_type="RECTANGLE", alpha=1.0):
    op = {
        "op": "add-shape",
        "slide": slide,
        "shape_type": shape_type,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "background_color": bg,
    }
    if alpha < 1.0:
        op["alpha"] = alpha
    ops.append(op)


def add_bordered_card(slide, x, y, w, h, fill, border, shape_type="ROUND_RECTANGLE"):
    add_rect(slide, x, y, w, h, border, shape_type=shape_type)
    add_rect(slide, x + 1, y + 1, w - 2, h - 2, fill, shape_type=shape_type)


def add_tb(
    slide,
    text,
    x,
    y,
    w,
    h,
    font_size,
    color,
    font_family="Roboto",
    bold=False,
    italic=False,
    alignment="left",
    content_alignment="TOP",
    line_spacing=120,
    background_color=None,
):
    op = {
        "op": "add-textbox",
        "slide": slide,
        "text": text,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "font_size": font_size,
        "color": color,
        "font_family": font_family,
        "alignment": alignment,
        "content_alignment": content_alignment,
        "line_spacing": line_spacing,
    }
    if bold:
        op["bold"] = True
    if italic:
        op["italic"] = True
    if background_color:
        op["background_color"] = background_color
    ops.append(op)


def add_chrome(slide, idx, dark, kicker, title, footer_left):
    bg = DARK_BG if dark else LIGHT_BG
    stripe = TEAL_DARK if dark else TXT_LIGHT_TITLE
    k_col = TEAL_DARK if dark else TEAL_LIGHT
    t_col = TXT_DARK_PRIMARY if dark else TXT_LIGHT_TITLE
    m_col = TXT_DARK_MUTED if dark else TXT_LIGHT_MUTED

    ops.append({"op": "set-background", "slide": slide, "color": bg})
    add_rect(slide, 0, 0, 8, 405, stripe)
    add_tb(slide, kicker, 30, 30, 500, 16, 10, k_col, font_family="Montserrat", bold=True, line_spacing=105)
    add_tb(slide, title, 30, 46, 660, 38, 28, t_col, font_family="Montserrat", bold=True, content_alignment="MIDDLE", line_spacing=105)
    add_tb(slide, footer_left, 30, 360, 540, 15, 10, m_col, font_family="Roboto", line_spacing=105)
    add_tb(slide, f"{idx:02d} / 16", 590, 360, 100, 15, 10, m_col, font_family="Roboto", alignment="right", line_spacing=105)


def set_notes(slide, text):
    ops.append({"op": "set-notes", "slide": slide, "text": text})


# =========================================================================
# SLIDE 1: Title & Core Premise (Dark)
# =========================================================================
ops.append({"op": "delete-element", "element": "i0"})
ops.append({"op": "delete-element", "element": "i1"})
ops.append({"op": "set-background", "slide": "p", "color": DARK_BG})
add_rect("p", 0, 0, 8, 405, TEAL_DARK)

add_tb("p", "INVESTMENT FRAMEWORK WALKTHROUGH  ·  v7.19", 60, 54, 600, 20, 12, TEAL_DARK, font_family="Montserrat", bold=True, alignment="center")
add_tb("p", "Quality & Moat Screener", 45, 92, 630, 54, 40, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center", content_alignment="MIDDLE")
add_tb("p", "How to Find World-Class Compounders — and Never Overpay", 60, 154, 600, 38, 18, TXT_DARK_BODY, font_family="Roboto", alignment="center", content_alignment="MIDDLE")
add_rect("p", 260, 208, 200, 4, TEAL_DARK)

pills = [
    ("1,175", "Global Universe", TXT_DARK_PRIMARY),
    ("6 Gates", "Munger Elimination", AMBER_DARK),
    ("0", "Analyst Overrides", TEAL_DARK),
]
for i, (num, lbl, col) in enumerate(pills):
    px = 45 + i * 220
    add_bordered_card("p", px, 238, 190, 92, DARK_CARD, DARK_BORDER)
    add_tb("p", num, px + 10, 250, 170, 42, 32, col, font_family="Montserrat", bold=True, alignment="center", content_alignment="MIDDLE")
    add_tb("p", lbl, px + 10, 294, 170, 24, 14, TXT_DARK_BODY, font_family="Roboto", alignment="center", content_alignment="MIDDLE")

add_tb("p", "1,175 Developed Stocks  →  225 Prime Grade (19.1%)  →  100% Deterministic Mauboussin-Fade DCF", 30, 358, 660, 17, 11, TXT_DARK_MUTED, font_family="Roboto", alignment="center")
set_notes("p", "Welcome to the Quality and Moat Screener v7.19 walkthrough. The whole system rests on one rule: first decide which businesses deserve a 20-year hold, and only then let pure accounting math tell you what price is fair.")

# =========================================================================
# SLIDE 2: Global Universe & 5 Philosophical Foundations (Light)
# =========================================================================
S2 = "SLIDE_2"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S2})
add_chrome(S2, 2, False, "EXECUTIVE SUMMARY  ·  UNIVERSE & PHILOSOPHY", "Global Universe & 5 Foundations", "Sources: S&P 500 ∪ Nasdaq-100 (US), STOXX Europe 600 (EU), S&P/TSX 60 (CA)")

add_bordered_card(S2, 30, 94, 220, 74, TXT_LIGHT_TITLE, TXT_LIGHT_TITLE)
add_tb(S2, "1,175", 44, 100, 192, 38, 32, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center")
add_tb(S2, "Developed Large & Mid-Caps", 44, 138, 192, 22, 12, TXT_DARK_BODY, font_family="Roboto", alignment="center")

regions = [
    ("EU · 602 (51%)", "STOXX Europe 600", "#3B82F6"),
    ("US · 515 (44%)", "S&P 500 ∪ Nasdaq-100", TEAL_LIGHT),
    ("CA · 58 (5%)", "S&P/TSX 60", AMBER_LIGHT),
]
for i, (r_title, r_sub, bar_col) in enumerate(regions):
    ry = 178 + i * 58
    add_bordered_card(S2, 30, ry, 220, 50, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
    add_rect(S2, 30, ry, 6, 50, bar_col)
    add_tb(S2, r_title, 44, ry + 6, 196, 20, 14, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
    add_tb(S2, r_sub, 44, ry + 26, 196, 18, 12, TXT_LIGHT_MUTED, font_family="Roboto")

foundations = [
    ("①", "Munger Inversion: Sequential rejection; hunt fatal flaws."),
    ("②", "Buffett Owner Earnings: Cash moats; no \"kindness of strangers.\""),
    ("③", "Sleep & Thorndike (Outsiders): Scale economies shared + allocation."),
    ("④", "Mauboussin CAP & Fade: 5–30Y runway + base-rate fade."),
    ("⑤", "Zero Analyst Overrides: Gates (gates.py) separate from DCF."),
]
for i, (badge, body) in enumerate(foundations):
    fy = 94 + i * 52
    add_bordered_card(S2, 268, fy, 422, 44, LIGHT_CARD, LIGHT_BORDER)
    add_tb(S2, badge, 276, fy + 8, 28, 28, 16, TEAL_LIGHT, font_family="Montserrat", bold=True, alignment="center", content_alignment="MIDDLE")
    add_tb(S2, body, 306, fy + 8, 376, 28, 14, TXT_LIGHT_BODY, font_family="Roboto", content_alignment="MIDDLE", line_spacing=110)

set_notes(S2, "Our 1,175-stock universe covers Europe, the US, and Canada. Five investing masters shape the rules: Munger's inversion, Buffett's Owner Earnings and solvency, Nick Sleep and Will Thorndike on capital allocation, Mauboussin on competitive advantage duration, and zero manual DCF overrides.")

# =========================================================================
# SLIDE 3: Pre-Screen Layer & Two-Stage Waterfall (Light)
# =========================================================================
S3 = "SLIDE_3"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S3})
add_chrome(S3, 3, False, "ARCHITECTURE  ·  PRE-SCREEN & WATERFALL", "Pre-Screen & Two-Stage Waterfall", "Blank Gate Rule: 0 unreviewed gates across all 1,175 companies (100% evaluated)")

# Top 2 Pre-screen cards
add_bordered_card(S3, 30, 92, 320, 110, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S3, 30, 92, 320, 5, CORAL_LIGHT)
add_tb(S3, "in_market → Feeds Gate 2", 44, 102, 292, 22, 15, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S3, "• Y: Western rule-of-law (US, CA, UK, CH, Nordics, W. Europe).\n• N: Greece & Poland → auto-fail Gate 2.", 44, 126, 292, 70, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

add_bordered_card(S3, 370, 92, 320, 110, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S3, 370, 92, 320, 5, CORAL_LIGHT)
add_tb(S3, "g6_default → Feeds Gate 6", 384, 102, 292, 22, 15, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S3, "• Deposit Banks (10–15× lev., duration mismatch) → G6 = N.\n• Utilities (6–8% ROIC, dilution) → G6 = N.", 384, 126, 292, 70, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

# Bottom Two-Stage Waterfall
add_bordered_card(S3, 30, 214, 294, 138, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S3, 30, 214, 294, 5, AMBER_LIGHT)
add_tb(S3, "Stage 1: Early Stop (G1–G3)", 44, 224, 266, 22, 15, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S3, "• Fail at G1, G2, or G3 stops immediately.\n• Gates 4–6 stay blank.\n• Blank Rule: 0 unreviewed (100% scored).", 44, 248, 266, 94, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

add_tb(S3, "→", 326, 268, 26, 30, 22, TEAL_LIGHT, font_family="Montserrat", bold=True, alignment="center", content_alignment="MIDDLE")

add_bordered_card(S3, 354, 214, 336, 138, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S3, 354, 214, 336, 5, TEAL_LIGHT)
add_tb(S3, "Stage 2: Full Diagnostic (G4–G6)", 368, 224, 308, 22, 15, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S3, "• All 483 G3-passers get full G4–G6 scores.\n• Scored even if failed at G4 (<15Y) or G5 (0).\n• Prevents hidden blind spots.", 368, 248, 308, 94, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

set_notes(S3, "Before Gate 1 even begins, pre-screens flag weak property-rights markets like Greece or Poland for Gate 2, and structurally leveraged deposit banks and capped utilities for Gate 6. Early rejects stop at Gates 1 to 3, while all 483 moat franchises receive full diagnostic scores across Gates 4 to 6.")

# =========================================================================
# SLIDE 4: Global Funnel Attrition (Dark + PNG Chart Slot)
# =========================================================================
S4 = "SLIDE_4"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S4})
add_chrome(S4, 4, True, "PART I · QUALITATIVE WATERFALL", "Global Funnel Attrition (1,175 → 225)", "Live v7.19 attrition: 1,175 → 1,145 → 989 → 483 → 375 → 359 → 225 Prime Grade")

# Right sidebar stat cards (Left 30..495, y=94..346 reserved for funnel_waterfall.png)
add_bordered_card(S4, 510, 94, 180, 118, DARK_CARD, DARK_BORDER)
add_tb(S4, "19.1%", 520, 104, 160, 44, 34, TEAL_DARK, font_family="Montserrat", bold=True, alignment="center")
add_tb(S4, "Prime Survival", 520, 150, 160, 22, 14, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center")
add_tb(S4, "225 of 1,175 clear all 6 Munger gates", 520, 174, 160, 32, 12, TXT_DARK_BODY, font_family="Roboto", alignment="center", line_spacing=115)

add_bordered_card(S4, 510, 228, 180, 118, DARK_CARD, DARK_BORDER)
add_tb(S4, "−43.1%", 520, 238, 160, 44, 34, AMBER_DARK, font_family="Montserrat", bold=True, alignment="center")
add_tb(S4, "Gate 3 Choke Point", 520, 284, 160, 22, 14, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center")
add_tb(S4, "506 firms lack moat or real pricing power", 520, 308, 160, 32, 12, TXT_DARK_BODY, font_family="Roboto", alignment="center", line_spacing=115)

set_notes(S4, "Look at how brutal Charlie Munger's inversion is in practice: 81 percent of the world's largest companies are eliminated. Gate 3 is the biggest choke point, cutting 506 businesses—43.1 percent of the starting universe—because they lack an enduring moat or pricing power above inflation.")

# =========================================================================
# SLIDE 5: Stage 1 Filters: Gates 1 & 2 (Light)
# =========================================================================
S5 = "SLIDE_5"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S5})
add_chrome(S5, 5, False, "PART I · STAGE 1 FILTERS", "Stage 1 Filters: Gates 1 & 2", "Stage 1 rejects 186 firms (−15.8%): 1,175 → 1,145 (G1) → 989 (G2)")

# Gate 1 Card
add_bordered_card(S5, 30, 92, 320, 258, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_tb(S5, "Gate 1 · Simple to Understand", 44, 100, 292, 22, 16, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S5, "Score: Y/N  |  −30 firms (−2.6%) → 1,145 remain", 44, 122, 292, 18, 12, TXT_LIGHT_MUTED, font_family="Roboto", bold=True)
add_rect(S5, 44, 146, 292, 90, LIGHT_TINT, shape_type="RECTANGLE")
add_tb(S5, "✓ PASS STANDARD", 54, 152, 272, 18, 12, TEAL_LIGHT, font_family="Montserrat", bold=True)
add_tb(S5, "Multi-cycle track record & verifiable statements (incl. clean banks, insurers, holdcos).", 54, 172, 272, 58, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)
add_rect(S5, 44, 244, 292, 96, LIGHT_TINT, shape_type="RECTANGLE")
add_tb(S5, "✗ REJECT STANDARD", 54, 250, 272, 18, 12, CORAL_LIGHT, font_family="Montserrat", bold=True)
add_tb(S5, "Pre-profit/unproven models & opaque B/S (prop trading, crypto treasuries, binary biotech).", 54, 270, 272, 64, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

# Gate 2 Card
add_bordered_card(S5, 370, 92, 320, 258, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_tb(S5, "Gate 2 · Essential Need & Habits", 384, 100, 292, 22, 16, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S5, "Score: Y/N + 2r  |  −156 (−13.3%) → 989 remain", 384, 122, 292, 18, 12, TXT_LIGHT_MUTED, font_family="Roboto", bold=True)
add_rect(S5, 384, 146, 292, 90, LIGHT_TINT, shape_type="RECTANGLE")
add_tb(S5, "✓ PASS STANDARD (in_market = Y)", 394, 152, 272, 18, 12, TEAL_LIGHT, font_family="Montserrat", bold=True)
add_tb(S5, "Functional needs + Buffett \"likely to spend\" habits & Lindy luxury; low legislative risk.", 394, 172, 272, 58, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)
add_rect(S5, 384, 244, 292, 96, LIGHT_TINT, shape_type="RECTANGLE")
add_tb(S5, "✗ REJECT STANDARD (Logs reason 2r)", 394, 250, 272, 18, 12, CORAL_LIGHT, font_family="Montserrat", bold=True)
add_tb(S5, "Deferrable cyclicals (cruises, airlines, builders), commodity explorers, pariah, tobacco/CFD.", 394, 270, 272, 64, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

set_notes(S5, "Gate 1 enforces circle of competence and financial verifiability, cutting binary biotech and opaque prop trading. Gate 2 applies Buffett and Munger's likely-to-spend test: it keeps necessities, daily rituals, and Lindy luxury while rejecting deferrable cyclicals, commodity explorers, pariah states, and predatory models.")

# =========================================================================
# SLIDE 6: Gate 3: 4 Moat Archetypes & Proof of Moat (Light)
# =========================================================================
S6 = "SLIDE_6"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S6})
add_chrome(S6, 6, False, "PART I · GATE 3 MOAT PROFILE", "Gate 3: 4 Moats & Empirical Proof", "Scores: 3_tb, 3_ia, 3_se, 3_rd ∈ {0,1,2} + primary 3a + 3b  |  −506 (−43.1%) → 483 remain")

archetypes = [
    ("124", "55% of Prime", "Toll Booth & Switching", "MSFT, SPGI\nLock-in & fees", TEAL_LIGHT),
    ("71", "32% of Prime", "Irreplaceable Infra", "WM, RMS.FR\nScarce assets/brand", TXT_LIGHT_TITLE),
    ("17", "8% of Prime", "Scale Econ. Shared", "COST, PGR\nStrictly Nick Sleep", AMBER_LIGHT),
    ("13", "6% of Prime", "R&D Leadership", "ASML.NL\nPatented edge", TEAL_LIGHT),
]
for i, (cnt, pct, name, ex, col) in enumerate(archetypes):
    cx = 30 + i * 169
    add_bordered_card(S6, cx, 92, 153, 162, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
    add_rect(S6, cx, 92, 153, 5, col)
    add_tb(S6, cnt, cx + 10, 102, 133, 38, 30, col, font_family="Montserrat", bold=True, alignment="center")
    add_tb(S6, pct, cx + 10, 140, 133, 16, 11, TXT_LIGHT_MUTED, font_family="Roboto", bold=True, alignment="center")
    add_tb(S6, name, cx + 10, 160, 133, 38, 14, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True, alignment="center", line_spacing=110)
    add_tb(S6, ex, cx + 10, 202, 133, 44, 12.5, TXT_LIGHT_BODY, font_family="Roboto", alignment="center", line_spacing=115)

add_bordered_card(S6, 30, 266, 660, 84, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S6, 30, 266, 8, 84, TEAL_LIGHT)
add_tb(S6, "✓ Gate 3b Empirical Proof-of-Moat Hurdle (3b = Y required alongside 3a ≠ None)", 48, 274, 630, 22, 14, TEAL_LIGHT, font_family="Montserrat", bold=True)
add_tb(S6, "5Y Median GAAP ROIC ≥ 12% (or Tangible ROIC ≥ 15%) AND Incremental ROIIC ≥ 12% + Real Pricing Power ≥ Inflation.", 48, 300, 630, 42, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

set_notes(S6, "Every surviving franchise must score on at least one of four moat archetypes: Toll Booths, Irreplaceable Infrastructure, strictly Nick Sleep's Scale Economies Shared—like Costco passing savings to shoppers—or R&D Leadership. Gate 3b also requires hard proof via 12 percent ROIC, 12 percent incremental ROIIC, and inflation-beating pricing power.")

# =========================================================================
# SLIDE 7: Gate 4: Two-Step Deterministic CAP Engine (Dark)
# =========================================================================
S7 = "SLIDE_7"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S7})
add_chrome(S7, 7, True, "PART I · GATE 4 RUNWAY ENGINE (CAP ≥ 15Y)", "Gate 4: Deterministic CAP Engine", "−108 rejected at Gate 4 (−9.2%)  |  375 firms clear CAP ≥ 15Y  |  Zero manual CAP overrides")

# Step 1 box
add_bordered_card(S7, 30, 92, 435, 78, DARK_CARD, DARK_BORDER)
add_tb(S7, "STEP 1 · Initial CAP from Gate 3 (m_max, m_sum)", 44, 98, 407, 20, 14, TEAL_DARK, font_family="Montserrat", bold=True)
add_tb(S7, "0Y (m_max=0)  |  15Y (1,1)  |  20Y (1,≥2 or 2,2)  |  25Y (2,3)  |  30Y (2,≥4)", 44, 122, 407, 42, 14, TXT_DARK_PRIMARY, font_family="Roboto", line_spacing=115)

# Step 2 box
add_bordered_card(S7, 30, 178, 435, 110, DARK_CARD, DARK_BORDER)
add_tb(S7, "STEP 2 · Porter's 5 Forces × 5 Macrotrends", 44, 184, 407, 20, 14, AMBER_DARK, font_family="Montserrat", bold=True)
add_tb(S7, "• 4_ent, 4_riv, 4_buy, 4_sup, 4_sub ∈ {0,1,2} vs AI, Demo, Geopolitics, Energy, Inflation & Clock Speed (fast tech/pharma 4_sub ≥ 1).\n• Haircut h(c1): 0→0Y, 1–2→−5Y, 3–4→−10Y, 5→−15Y.\n• ⚠ Fatal Flaw (any Force=2): CAP ≤ 10Y → Reject.", 44, 208, 407, 74, 12, TXT_DARK_BODY, font_family="Roboto", line_spacing=112)

# Right Prime CAP Distribution Native Bar Chart
add_bordered_card(S7, 480, 92, 210, 196, DARK_CARD, DARK_BORDER)
add_tb(S7, "Prime CAP Dist. (225)", 492, 100, 186, 22, 14, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center")
cap_dist = [
    ("15Y", 51, 40, "#5B7CFA"),
    ("20Y", 114, 88, TEAL_DARK),
    ("25Y", 57, 44, AMBER_DARK),
    ("30Y", 3, 6, TXT_DARK_PRIMARY),
]
for i, (lbl, cnt, bw, col) in enumerate(cap_dist):
    by = 132 + i * 37
    txt_col = TXT_DARK_BODY if col == "#5B7CFA" else col
    add_tb(S7, lbl, 490, by, 46, 22, 13, TXT_DARK_BODY, font_family="Roboto", bold=True, content_alignment="MIDDLE")
    add_rect(S7, 538, by + 3, bw, 16, col, shape_type="ROUND_RECTANGLE")
    add_tb(S7, str(cnt), 544 + bw, by, 40, 22, 13, txt_col, font_family="Montserrat", bold=True, content_alignment="MIDDLE")

# Bottom Anti-Drift Rules Strip
add_bordered_card(S7, 30, 296, 660, 54, DARK_CARD_ALT, DARK_BORDER)
add_tb(S7, "3 Anti-Drift Rules:  (1) Sub-Industry Peer Benchmarking  ·  (2) UI Seat Layer (2) vs Proprietary Data/Statutory Engine (1)  ·  (3) Gate Orthogonality (zero G5/G6 bleed into G4)", 44, 302, 632, 42, 13, TXT_DARK_BODY, font_family="Roboto", content_alignment="MIDDLE", line_spacing=115)

set_notes(S7, "Gate 4 separates how strong a moat is today from how fast disruption is moving. Step 1 sets initial CAP from 15 to 30 years using Gate 3 scores. Step 2 stress-tests Porter's 5 Forces against 5 macrotrends and Mauboussin's Clock Speed: moderate forces shave 5 to 15 years, while any fatal flaw rated 2 caps runway at 10 years or less.")

# =========================================================================
# SLIDE 8: Stage 2 Stewardship & Solvency (Gates 5 & 6) (Light)
# =========================================================================
S8 = "SLIDE_8"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S8})
add_chrome(S8, 8, False, "PART I · STAGE 2 DIAGNOSTICS", "Stage 2: Stewardship & Solvency", "−16 fail Gate 5 (−1.4%) → 359  |  −134 fail Gate 6 (−11.4%) → 225 Prime Grade (19.1%)")

# Left: Gate 5
add_bordered_card(S8, 30, 92, 315, 258, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S8, 30, 92, 315, 5, AMBER_LIGHT)
add_tb(S8, "Gate 5 · Stewardship (0–2, pass ≥ 1)", 44, 102, 287, 22, 14.5, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S8, "5 Superinvestor Vectors (−16 rejected):", 44, 126, 287, 18, 12, TXT_LIGHT_MUTED, font_family="Roboto", bold=True)
vectors = [
    "1. Integrity & Candor (Fisher / Buffett)",
    "2. Rational Capital Alloc. (Murphy / Thorndike)",
    "3. Customer Surplus (Bezos / Sleep)",
    "4. Product-Led Execution",
    "5. Anti-Bureaucracy (Wallenberg / Drucker)",
]
add_tb(S8, "\n".join(vectors), 44, 152, 287, 184, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=140)

# Right: Gate 6
add_bordered_card(S8, 365, 92, 325, 258, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S8, 365, 92, 325, 5, TEAL_LIGHT)
add_tb(S8, "Gate 6 · Cash & Solvency (Y/N)", 379, 102, 297, 22, 14.5, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S8, "3 Financial Pillars (<3 flags, −134 rejected):", 379, 126, 297, 18, 12, TXT_LIGHT_MUTED, font_family="Roboto", bold=True)

pillars = [
    ("① Peak-to-Peak Owner EPS", "Compound to new highs across cycles."),
    ("② Cash Conversion ≥ 80%", "Multi-year Owner FCF ÷ GAAP NI ≥ 80%."),
    ("③ Peace-of-Mind Fortress B/S", "Net Debt/OE ≤ 4.0y, EBIT/Int > 5.0× (infra & Solvency II > 200% contextual)."),
]
pillar_geom = [(148, 53, 28), (207, 53, 28), (266, 70, 45)]
for (pt, pb), (py, ph, bh) in zip(pillars, pillar_geom):
    add_rect(S8, 379, py, 297, ph, LIGHT_TINT, shape_type="RECTANGLE")
    add_tb(S8, pt, 389, py + 4, 277, 18, 13.5, TEAL_LIGHT, font_family="Montserrat", bold=True)
    add_tb(S8, pb, 389, py + 23, 277, bh, 12.5, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=108)

set_notes(S8, "Even a great moat fails if management wastes capital or loads up on debt. Gate 5 grades 5 superinvestor stewardship vectors and eliminates 16 companies. Gate 6 eliminates 134 more because of shrinking cycle peaks, weak cash conversion below 80 percent, or leverage exceeding 4 years of Owner Earnings.")

# =========================================================================
# SLIDE 9: Part II: Slump-Cannibal & Sanitized Owner EPS (Dark)
# =========================================================================
S9 = "SLIDE_9"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S9})
add_chrome(S9, 9, True, "PART II · QUANTITATIVE VALUATION (STEP 1)", "Part II: Sanitized Owner EPS", "Slump-Cannibal Compounder Doctrine: 100% deterministic from audited statements — zero overrides")

# Formula Strip
add_bordered_card(S9, 30, 90, 660, 40, DARK_CARD_ALT, TEAL_DARK)
add_tb(S9, "Owner EPS = (NI + max(0, min(clean_DA, max(0, OCF − NI)) − CapEx − 0.20 × AvgLease)) / Shares", 40, 96, 640, 28, 12.5, TEAL_DARK, font_family="Roboto", bold=True, alignment="center", content_alignment="MIDDLE")

# 2x2 Accounting Guards
guards = [
    ("① Cash-Flow Backing", "OCF − NI caps non-cash D&A; no fake accruals."),
    ("② 1.5× Impairment Cap", "clean_DA trims transient impairment spikes."),
    ("③ 20% IFRS-16 Lease Ded.", "Deducts 20% AvgLease depr. (US-GAAP exempt)."),
    ("④ Spike & Pre-IPO Strip", "Purges one-off windfalls & pre-IPO noise."),
]
for i, (gt, gb) in enumerate(guards):
    col = i % 2
    row = i // 2
    gx = 30 + col * 340
    gy = 138 + row * 68
    add_bordered_card(S9, gx, gy, 320, 62, DARK_CARD, DARK_BORDER)
    add_tb(S9, gt, gx + 12, gy + 5, 296, 20, 14, AMBER_DARK, font_family="Montserrat", bold=True)
    add_tb(S9, gb, gx + 12, gy + 25, 296, 34, 12.5, TXT_DARK_BODY, font_family="Roboto", line_spacing=108)

# Bottom Slump-Cannibal & Age-Weighted Reversion
add_bordered_card(S9, 30, 278, 660, 74, DARK_CARD, DARK_BORDER, shape_type="RECTANGLE")
add_rect(S9, 30, 278, 8, 74, TEAL_DARK)
add_tb(S9, "Slump-Cannibal & Age-Weighted Mid-Cycle Reversion", 48, 284, 630, 20, 14, TEAL_DARK, font_family="Montserrat", bold=True)
add_tb(S9, "Looks through 1Y sales_1y slumps using multi-cycle growth. When cur_eps < peak, blend weight decays linearly: w = 50% (peak ≤ 1y old) → 33% (2y) → 17% (3y) → 0% (≥ 4y).", 48, 306, 630, 42, 13, TXT_DARK_BODY, font_family="Roboto", line_spacing=112)

set_notes(S9, "Accounting Net Income can be distorted by non-cash charges or stale boom years, so Owner EPS measures true cash earnings. Part II computes intrinsic value purely from audited statements with zero analyst overrides: Owner EPS caps depreciation add-backs by operating cash flow minus net income, strips 1.5x impairment spikes and pre-IPO noise, deducts 20 percent of IFRS-16 leases, and decays stale earnings peaks to zero over four years.")

# =========================================================================
# SLIDE 10: Capital Base & M&A-Matched RONIC₀ (Light)
# =========================================================================
S10 = "SLIDE_10"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S10})
add_chrome(S10, 10, False, "PART II · QUANTITATIVE VALUATION (STEP 2)", "Capital Base & M&A-Matched RONIC₀", "RONIC₀ bounded to [5.0%, 50.0%]  |  Prevents serial cash-acquirer ROIC inflation")

T10 = "TABLE_S10"
ops.append({"op": "add-table", "slide": S10, "rows": 4, "cols": 4, "id": T10, "x": 30, "y": 92, "width": 660, "height": 134})
col_widths_10 = [135, 145, 225, 155]
for idx, cw in enumerate(col_widths_10):
    ops.append({
        "op": "updateTableColumnProperties",
        "updateTableColumnProperties": {
            "objectId": T10,
            "columnIndices": [idx],
            "tableColumnProperties": {"columnWidth": {"magnitude": cw, "unit": "PT"}},
            "fields": "columnWidth",
        },
    })

t10_rows = [
    ["Capital Regime", "Eligible Industries", "Return Formula", "Why It Matters"],
    ["Tangible Op. ROIC", "Operating & Fee Fin.", "NOPAT ÷ max(IC − GW − Intang, 1/3 IC)", "Strips legacy M&A goodwill"],
    ["5Y Median ROE", "BS Fin. & IC≤0 (≥2/5y)", "5Y Consolidated ROE (r=10.25% / 8.5%)", "Deposits/float make IC ≤ 0"],
    ["GAAP ROIC", "IFRIC-12 Concessions", "NOPAT ÷ IC_GAAP", "Concession asset base"],
]
for r_idx, row in enumerate(t10_rows):
    for c_idx, val in enumerate(row):
        is_hdr = r_idx == 0
        bg = TXT_LIGHT_TITLE if is_hdr else (LIGHT_CARD if r_idx % 2 == 1 else LIGHT_TINT)
        fg = TXT_DARK_PRIMARY if is_hdr else (TXT_LIGHT_TITLE if c_idx == 0 else TXT_LIGHT_BODY)
        ops.append({
            "op": "set-table-cell",
            "table": T10,
            "row": r_idx,
            "col": c_idx,
            "text": val,
            "color": fg,
            "bold": is_hdr or c_idx == 0,
            "font_size": 12 if is_hdr else 11.5,
            "font_family": "Roboto",
            "background_color": bg,
        })

# Bottom Harmonic M&A Blend Card
add_bordered_card(S10, 30, 244, 660, 106, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
add_rect(S10, 30, 244, 8, 106, AMBER_LIGHT)
add_tb(S10, "M&A-Matched Harmonic Blend (Trigger: r_tang > 1.25 × r_GAAP)", 48, 252, 630, 22, 15, AMBER_LIGHT, font_family="Montserrat", bold=True)
add_tb(S10, "• Cash Acquirers (ma_reinvest > 0): harmonic blend of r_tang & r_GAAP via w = clip(ma_reinvest × r_GAAP / g₀, 0, 1).\n• Stock Deals: penalized via Share Index S_t. RONIC₀ bounded to [5%, 50%].", 48, 278, 630, 64, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=114)

set_notes(S10, "To measure return on new capital fairly, the model picks the right capital base by sector: tangible operating ROIC with a one-third invested-capital floor for operating firms, 5-year ROE for banks, insurers, and negative-capital clearinghouses, and GAAP ROIC for concessions. Serial cash acquirers get harmonically blended down toward GAAP ROIC.")

# =========================================================================
# SLIDE 11: 4-Pillar Statistical Organic Growth (Light)
# =========================================================================
S11 = "SLIDE_11"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S11})
add_chrome(S11, 11, False, "PART II · QUANTITATIVE VALUATION (STEP 3)", "4-Pillar Statistical Growth (g₀ ≤ 13%)", "10Y audited history  |  Outlier-resistant non-parametric statistics  |  Pure organic firm growth")

pillars_11 = [
    ("①", "Dilution Index S_t", "Penalizes SBC & stock M&A share growth in exact year (10Y).", TEAL_LIGHT),
    ("②", "Cycle Theil–Sen", "Log-slopes Δt ≥ 5y; outputs P50 median & conservative P25.", TXT_LIGHT_TITLE),
    ("③", "3-Driver Triang.", "Balances Rev, NOPAT & Owner EPS (6% refranchising cap).", AMBER_LIGHT),
    ("④", "EB & tanh Cap", "Shrinks (τ₀=6%) toward 3.0%; smooth tanh cap at 13.0%.", TEAL_LIGHT),
]
for i, (num, p_title, p_desc, col) in enumerate(pillars_11):
    px = 30 + i * 170
    add_bordered_card(S11, px, 92, 150, 174, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
    add_rect(S11, px, 92, 150, 5, col)
    add_tb(S11, num, px + 10, 100, 130, 26, 20, col, font_family="Montserrat", bold=True, alignment="center")
    add_tb(S11, p_title, px + 8, 128, 134, 34, 13.5, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True, alignment="center", line_spacing=108)
    add_tb(S11, p_desc, px + 10, 166, 130, 92, 12.5, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)
    if i < 3:
        add_tb(S11, "→", px + 150, 162, 20, 26, 18, TEAL_LIGHT, font_family="Montserrat", bold=True, alignment="center")

add_bordered_card(S11, 30, 276, 660, 76, LIGHT_TINT, LIGHT_BORDER, shape_type="RECTANGLE")
add_tb(S11, "Buyback Discipline (Kept Strictly Outside Firm-Level DCF)", 44, 284, 632, 20, 14, TXT_LIGHT_TITLE, font_family="Montserrat", bold=True)
add_tb(S11, "Net buyback yield (bb_eff) is clamped to [−3.0%, +3.5%] and excluded from DCF growth g₀, preventing leverage-driven financial engineering from inflating fair value.", 44, 306, 632, 42, 13, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=112)

set_notes(S11, "Rather than trusting noisy short-term surges, the model extracts durable organic growth and gently pulls extreme outliers back toward normal. Growth g0 comes from a four-pillar statistical pipeline over 10 years of statements: a dilution-only share index, cycle-spanning Theil-Sen slopes over 5-plus-year spans to ignore 1-year COVID flukes, three-driver triangulation across revenue, NOPAT, and Owner EPS, and Empirical Bayes shrinkage toward 3 percent inflation capped smoothly at 13 percent.")

# =========================================================================
# SLIDE 12: Explicit N-Year Mauboussin-Fade DCF (Dark + PNG Chart Slot)
# =========================================================================
S12 = "SLIDE_12"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S12})
add_chrome(S12, 12, True, "PART II · QUANTITATIVE VALUATION (STEP 4)", "Explicit N-Year Mauboussin-Fade DCF", "Stage 1 explicit fade (t = 1..CAP) + Stage 2 McKinsey terminal value at 3.0% inflation")

# Right 3 Stacked Formula Cards (Left 30..395, y=94..346 reserved for mauboussin_fade_dcf.png)
dcf_cards = [
    ("Conservative Base & Hurdle", "E₁ = 1.0 × Active EPS. Discount rate r = 8.50% (operating) or 10.25% (BS financials).", TEAL_DARK),
    ("Stage 1 & 2 Linear Fade", "g_t → min(g₀, 3.0%); RONIC_t → min(RONIC₀, 20%, r+0.5(RONIC₀−r)); FCF_t = E_t(1−g_t/RONIC_t).", AMBER_DARK),
    ("Miller–Modigliani Invariance", "Exact math guarantee: when RONIC = r, Fair P/E ≡ 1 / r (11.76× op / 9.76× fin) for any g₀.", TXT_DARK_PRIMARY),
]
card_geom = [(92, 87, 56), (184, 87, 56), (276, 72, 44)]
for (ct, cb, col), (cy, ch, bh) in zip(dcf_cards, card_geom):
    add_bordered_card(S12, 410, cy, 280, ch, DARK_CARD, DARK_BORDER)
    add_tb(S12, ct, 422, cy + 3, 256, 20, 14, col, font_family="Montserrat", bold=True)
    add_tb(S12, cb, 422, cy + 23, 256, bh, 12.5, TXT_DARK_BODY, font_family="Roboto", line_spacing=110)

set_notes(S12, "In Step 4, excess growth and returns fade linearly over the Gate 4 Competitive Advantage Period. High returns only create value when RONIC exceeds the hurdle rate: if a business only earns 8.5 percent, growing faster adds zero extra value and its Fair P/E stays locked at 1 divided by 8.5 percent, or 11.76 times.")

# =========================================================================
# SLIDE 13: 3-Price Anchor, Bellman 5Y IRR, Reverse-DCF (Light)
# =========================================================================
S13 = "SLIDE_13"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S13})
add_chrome(S13, 13, False, "PART II · QUANTITATIVE VALUATION (STEP 5)", "3-Price Anchor, 5Y IRR & Reverse-DCF", "Exact formula 0g / 3% max terminal P/E: 15.45× operating  |  11.72× BS financials")

quads = [
    ("① 3-Price Anchor", "Current Price vs Fair Value vs 0g Floor (3% inflation, max 15.45× op / 11.72× BS fin; zero-spread 11.76× / 9.76×).", TEAL_LIGHT),
    ("② Bellman-Consistent 5Y IRR", "Solves exact IRR across FCF₁..FCF₅ + Year-5 DCF continuation V₅. Guaranteed lock: IRR == r iff Price == Fair Value.", TXT_LIGHT_TITLE),
    ("③ Reverse-DCF (g_market)", "Scans [−20%, +50%] grid + bisection to invert market-implied growth g_market & Market-Implied CAP from today's quote.", AMBER_LIGHT),
    ("④ Special Physics & Breakers", "• 1.0× BVPS: MTM HoldCo anchor.\n• No value: Fair Value ≤ 0.\n• No data: BLOCKING_AUTO_NOTES.", CORAL_LIGHT),
]
for i, (qt, qb, col) in enumerate(quads):
    col_i = i % 2
    row_i = i // 2
    qx = 30 + col_i * 340
    qy = 94 + row_i * 134
    add_bordered_card(S13, qx, qy, 320, 120, LIGHT_CARD, LIGHT_BORDER, shape_type="RECTANGLE")
    add_rect(S13, qx, qy, 320, 5, col)
    add_tb(S13, qt, qx + 14, qy + 10, 292, 22, 15, col, font_family="Montserrat", bold=True)
    add_tb(S13, qb, qx + 14, qy + 36, 292, 76, 14, TXT_LIGHT_BODY, font_family="Roboto", line_spacing=116)

set_notes(S13, "Step 5 turns Fair Value into three practical decision anchors. Notice the 0g floor ceiling: at 3 percent inflation and a 20 percent terminal RONIC cap, operating companies cap at (1 - 3%/20%)/(8.5% - 3%) = 15.45x, while Balance-Sheet Financials at a 10.25% hurdle cap at the exact formula ceiling (1 - 3%/20%)/(10.25% - 3%) = 11.72x (superseding the earlier 10.89x draft ref)—individual insurers like MUV2.DE at 18.2% RONIC0 sit at 10.88x and HNR1.DE at 19.0% RONIC0 sit at 10.97x. Reverse-DCF flips the model to ask what growth today's price already assumes.")

# =========================================================================
# SLIDE 14: Part III: Actionable Decision Cohorts (Dark)
# =========================================================================
S14 = "SLIDE_14"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S14})
add_chrome(S14, 14, True, "PART III · ACTIONABLE COHORTS", "Part III: Actionable Decision Cohorts", "Price date 2026-11-17  |  Prime Grade median excess 5Y IRR vs hurdle: −11.7pp")

cohorts = [
    ("225", "🛡️ Prime Grade", "Clears all 6 Munger gates (< 3 G6 flags).\n\n• 110 US | 104 EU | 11 CA\n• 220 Valued (5 No data, 0 No value)\n• Core long-term compounder A-list.", TEAL_DARK),
    ("25", "💎 Growth at ~0g", "Quality Grade, Valued, g₀ ≥ 5.0%, g_mkt < 5.0% (9 Prime, 6 G6-fail, 10 CAP 5–10Y).\n\n• ZTS: +22.4% IRR ($83 vs $146 FV / $94 0g)\n• PGHN.CH: +16.5% | PGR: +18.3%", AMBER_DARK),
    ("443", "🏰 Quality Grade", "Structural moat cohort passing G1, G2 & G3 (< 3 G6 flags).\n\n• 221 US | 204 EU | 18 CA\n• Full watchlist for deep cycle pullbacks.", TXT_DARK_BODY),
]
for i, (num, cname, cdesc, col) in enumerate(cohorts):
    cx = 30 + i * 227
    add_bordered_card(S14, cx, 94, 206, 254, DARK_CARD, DARK_BORDER, shape_type="RECTANGLE")
    add_rect(S14, cx, 94, 206, 5, col)
    add_tb(S14, num, cx + 12, 104, 182, 48, 40, col, font_family="Montserrat", bold=True, alignment="center")
    add_tb(S14, cname, cx + 12, 152, 182, 24, 15, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center")
    add_tb(S14, cdesc, cx + 12, 182, 182, 158, 13, TXT_DARK_BODY, font_family="Roboto", line_spacing=116)

set_notes(S14, "Surviving companies organize into three actionable cohorts. Prime Grade holds the 225 top-tier compounders. Quality Grade tracks all 443 structural moats for pullback watchlists. Growth at ~0g spots 25 mispriced compounders growing at least 5 percent organically while priced below 5 percent—such as Zoetis at +22.4 percent IRR, Partners Group at +16.5 percent, and Progressive at +18.3 percent.")

# =========================================================================
# SLIDE 15: Live Case Studies: Quality vs. Price (Light + PNG Chart Slot)
# =========================================================================
S15 = "SLIDE_15"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S15})
add_chrome(S15, 15, False, "PART III · LIVE EXAMPLES (2026-11-17)", "Live Case Studies: Quality vs. Price", "Great businesses can be expensive stocks (COST, ASML.NL, WM)  |  CRM blocked by Gate 4 AI Fatal Flaw")

T15 = "TABLE_S15"
ops.append({"op": "add-table", "slide": S15, "rows": 7, "cols": 5, "id": T15, "x": 30, "y": 96, "width": 416, "height": 236})
col_widths_15 = [88, 84, 92, 54, 98]
for idx, cw in enumerate(col_widths_15):
    ops.append({
        "op": "updateTableColumnProperties",
        "updateTableColumnProperties": {
            "objectId": T15,
            "columnIndices": [idx],
            "tableColumnProperties": {"columnWidth": {"magnitude": cw, "unit": "PT"}},
            "fields": "columnWidth",
        },
    })

t15_rows = [
    ["Ticker (CAP)", "Cur/Fair P/E", "g₀ → g_mkt", "5Y IRR", "Verdict"],
    ["MSFT (25Y)", "28.2×/30.5×", "11.5%→10.5%", "+10.3%", "✓ Prime −7.5%"],
    ["SPGI (30Y)", "25.4×/20.3×", "7.0%→9.9%", "+3.5%", "Prime +24.8%"],
    ["ASML.NL (25Y)", "49.8×/32.5×", "12.3%→17.5%", "−0.7%", "Prime +53.3%"],
    ["COST (30Y)", "53.5×/28.9×", "10.0%→16.5%", "−4.6%", "Prime +84.9%"],
    ["WM (25Y)", "36.0×/14.4×", "5.6%→23.5%", "−10.5%", "Prime +148.9%"],
    ["CRM (5Y)", "17.8×/15.1×", "11.6%→26.6%", "Reject", "✗ G4 (4_sub=2)"],
]
for r_idx, row in enumerate(t15_rows):
    for c_idx, val in enumerate(row):
        is_hdr = r_idx == 0
        bg = TXT_LIGHT_TITLE if is_hdr else (LIGHT_CARD if r_idx % 2 == 1 else LIGHT_TINT)
        if is_hdr:
            fg = TXT_DARK_PRIMARY
        elif r_idx == 1 and c_idx in (3, 4):
            fg = TEAL_LIGHT
        elif r_idx == 6 and c_idx in (0, 3, 4):
            fg = AMBER_LIGHT
        elif r_idx in (3, 4, 5) and c_idx == 3:
            fg = CORAL_LIGHT
        else:
            fg = TXT_LIGHT_TITLE if c_idx == 0 else TXT_LIGHT_BODY
        ops.append({
            "op": "set-table-cell",
            "table": T15,
            "row": r_idx,
            "col": c_idx,
            "text": val,
            "color": fg,
            "bold": is_hdr or c_idx == 0 or (r_idx in (1, 6) and c_idx in (3, 4)),
            "font_size": 12 if is_hdr else 11.5,
            "font_family": "Roboto",
            "background_color": bg,
        })

# Right slot x=454..690 (w=236), y=96..325 (h=229) reserved for case_study_irr_pe.png

set_notes(S15, "These six real companies prove why quality and price must be judged separately. Costco, ASML, and Waste Management are wonderful 25-to-30-year moats, yet their stock prices assume 16 to 24 percent growth and yield negative 5-year IRRs. Salesforce looks cheap at 17.8x earnings until Gate 4 flags AI seat-compression as a fatal flaw. Only Microsoft passes all gates and clears the 8.5 percent hurdle at +10.3 percent IRR.")

# =========================================================================
# SLIDE 16: Brother's 4-Step Decision Playbook (Dark)
# =========================================================================
S16 = "SLIDE_16"
ops.append({"op": "add-slide", "layout": "BLANK", "id": S16})
add_chrome(S16, 16, True, "CLOSING  ·  PRACTICAL WORKFLOW", "Your 4-Step Decision Playbook", "Quality & Moat Screener (v7.19)  ·  Open output/screener.html to explore all 1,175 dossiers")

steps = [
    ("①", "Screen First", "Start inside Prime Grade (225) or Growth at ~0g (25). Never override a failed gate.", TEAL_DARK),
    ("②", "Invert g_mkt", "Compare Model g₀ vs Market Implied g_mkt. Seek positive growth cushion.", TEAL_DARK),
    ("③", "3-Price Anchor", "Check Current Price vs DCF Fair Value & 0g Terminal Floor.", AMBER_DARK),
    ("④", "Demand IRR", "Require Bellman 5Y IRR > 8.50% (10.25% BS fin) before buying.", AMBER_DARK),
]
for i, (num, stitle, sdesc, col) in enumerate(steps):
    sx = 30 + i * 169
    add_bordered_card(S16, sx, 92, 153, 168, DARK_CARD, DARK_BORDER, shape_type="RECTANGLE")
    add_rect(S16, sx, 92, 153, 5, col)
    add_tb(S16, num, sx + 10, 102, 133, 28, 22, col, font_family="Montserrat", bold=True, alignment="center")
    add_tb(S16, stitle, sx + 10, 132, 133, 24, 15, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, alignment="center")
    add_tb(S16, sdesc, sx + 10, 160, 133, 92, 13, TXT_DARK_BODY, font_family="Roboto", line_spacing=114)

add_bordered_card(S16, 30, 272, 660, 78, DARK_CARD_ALT, DARK_BORDER, shape_type="RECTANGLE")
add_rect(S16, 260, 272, 200, 3, TEAL_DARK)
add_tb(S16, "“Tell me where I am going to die, so I never go there.” — Charlie Munger", 46, 280, 628, 24, 15, TXT_DARK_PRIMARY, font_family="Montserrat", bold=True, italic=True, alignment="center")
add_tb(S16, "Patience pays: wait inside the 225 Prime Grade & 25 Growth-at-0g names until Mr. Market hands you a double-digit 5Y IRR.", 46, 308, 628, 36, 12.5, TXT_DARK_BODY, font_family="Roboto", alignment="center", line_spacing=112)

set_notes(S16, "To use the screener every week, just follow four steps: start inside the 225 Prime Grade or 25 Growth at ~0g cohorts, invert market-implied growth against g0, anchor to Fair Value and the 0g floor, and wait patiently until 5-year IRR clears your hurdle rate.")


def validate_batch():
    slides = ["p"] + [op["id"] for op in ops if op["op"] == "add-slide"]
    assert len(slides) == 16, f"Expected 16 slides, got {len(slides)}"
    assert ops[0] == {"op": "delete-element", "element": "i0"}
    assert ops[1] == {"op": "delete-element", "element": "i1"}

    notes_by_slide = {}
    for idx, op in enumerate(ops):
        kind = op["op"]
        if kind == "add-textbox":
            assert op.get("color"), f"Missing color on textbox {idx}"
            assert op.get("font_family") in ("Montserrat", "Roboto"), f"Invalid font on textbox {idx}"
            x, y, w, h = op["x"], op["y"], op["width"], op["height"]
            assert 30 <= x and x + w <= 690, f"X margin violation on {op['slide']}: x={x}, w={w}"
            assert 30 <= y and y + h <= 375, f"Y margin violation on {op['slide']}: y={y}, h={h}"
        elif kind == "add-shape":
            x, y, w, h = op["x"], op["y"], op["width"], op["height"]
            if not (x == 0 and y == 0 and w == 8 and h == 405):
                assert 30 <= x and x + w <= 690, f"Shape X margin violation on {op['slide']}: x={x}, w={w}"
                assert 30 <= y and y + h <= 375, f"Shape Y margin violation on {op['slide']}: y={y}, h={h}"
        elif kind == "add-table":
            x, y, w, h = op["x"], op["y"], op["width"], op["height"]
            assert 30 <= x and x + w <= 690
            assert 30 <= y and y + h <= 375
        elif kind == "set-table-cell":
            assert op.get("color"), f"Missing color on table cell {op}"
            assert op.get("font_family") in ("Montserrat", "Roboto")
        elif kind == "set-notes":
            wc = len(op["text"].split())
            assert wc >= 15, f"Speaker notes too short ({wc} words) on {op['slide']}"
            notes_by_slide[op["slide"]] = wc

    assert len(notes_by_slide) == 16, f"Expected 16 notes, got {len(notes_by_slide)}"
    print(f"Validation OK: {len(slides)} slides, {len(ops)} batch ops, {len(notes_by_slide)} speaker notes.")


if __name__ == "__main__":
    validate_batch()
    out = Path("output/deck/batch.json")
    out.write_text(json.dumps(ops, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
