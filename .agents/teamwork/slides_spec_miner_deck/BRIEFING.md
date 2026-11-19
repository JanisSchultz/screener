# BRIEFING — 2026-11-18T13:29:00Z

## Mission
Specify the complete pedagogical slide architecture, visual design system, chart specifications, and verification rubric for explaining the Quality & Moat Screener (v7.19) to the user's brother.

## 🔒 My Identity
- Archetype: `teamwork_spec_miner` (`slides_spec_miner_deck`)
- Roles: Specification Miner — Presentation Architecture, Visual Design & Verification Rubric
- Working directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_spec_miner_deck`
- Original parent: `628d3c94-387f-425c-b1c2-0f102895e566`
- Milestone: Slide Architecture & Verification Rubric Specification

## 🔒 Key Constraints
- Read-only on repository and Google Slides — do NOT create slides or edit repo files.
- Write only to `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_spec_miner_deck/`.
- Follow `gslides/SKILL.md` and `gslides/references/styling.md` strictly (720×405 pt canvas, >=30pt margins, >=14pt body, max 5–6 bullets, varied layouts, visual element on every slide, WCAG >=4.5:1 contrast, zero red-green pitfalls).
- Cover 100% of R2 requirements from `ORIGINAL_REQUEST.md` without overcrowding.

## Current Parent
- Conversation ID: `628d3c94-387f-425c-b1c2-0f102895e566`
- Updated: 2026-11-18T13:29:00Z

## Task Summary
- **What to build**: Complete specification in `handoff.md` covering pacing/slide count analysis, 16-slide blueprint, visual design system, PNG/native chart specs, and explicit visual & factual verification rubric.
- **Success criteria**: Every R2 item mapped to slides with zero overcrowding; concrete 720×405pt coordinates/motifs/colors; verifiable rubric for Reviewers & Challengers.
- **Interface contracts**: `.agents/teamwork/ORIGINAL_REQUEST.md`, `gslides/SKILL.md`, `gslides/references/styling.md`

## Key Decisions Made
- **16-slide architecture** (splitting overloaded Draft Slides 2, 4, 8, and 12 into 2 slides each) for 100% R2 parity without violating 14pt body / 5-6 bullet / 30pt margin rules.
- **Midnight Executive (`#1E2761`) + Ice Slate (`#F5F7FA`)** sandwich palette with colorblind-safe Teal (`#0F766E`/`#2DD4BF`), Coral (`#C2410C`/`#FB923C`), and Amber (`#B45309`/`#FBBF24`) accents + `Montserrat` Bold / `Roboto` pairing.
- **Chart strategy**: Note that `matplotlib`/`PIL` are not installed in `/usr/bin/python3`; recommend `swiftc` CoreGraphics 3× Retina PNGs in `output/charts/` for Slides 4, 12, and 15 + native `gslides` shapes/tables/connectors elsewhere.

## Artifact Index
- `.agents/teamwork/slides_spec_miner_deck/DISPATCH.md` — Dispatch log
- `.agents/teamwork/slides_spec_miner_deck/progress.md` — Liveness heartbeat
- `.agents/teamwork/slides_spec_miner_deck/handoff.md` — Final specification (complete)
