## 2026-11-18T15:41:51Z
You are `slides_challenger_iter2_1` (`teamwork_challenger`).
Your working directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_challenger_iter2_1`
Your parent conversation ID: `628d3c94-387f-425c-b1c2-0f102895e566`

MANDATORY READS:
1. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
2. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_challenger_iter1_1/handoff.md`
3. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_explorer_iter2_1/handoff.md`
4. `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/slides_worker_iter2/handoff.md`

CRITICAL `gslides` COMMAND RULES:
- Any `run_command` calling `gslides` MUST start literally with `gslides readonly ...` with `BypassSandbox: false` (NO `&&`, `;`, `||`, `|`, `>`, vars, subshells, `env`, or `python3 subprocess`). Read-only only — NEVER mutate!

OBJECTIVE (Iteration 2 AST, Geometry, PPTX/PDF/PNG & All-302-Run WCAG Challenge):
1. Query live Google Slides metadata via `gslides readonly list-slides 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --json` and `gslides readonly info 1c92WOeak6IUvuTVjxrXn5tsB3IHv7_9Nv7mzl8dM2oQ --json` (standalone commands, `BypassSandbox: false`).
2. Write and run a read-only Python verification script inside `slides_challenger_iter2_1/` (NEVER touch `output/` or repo files!) that verifies:
   - Exact live AST parity (`list-slides` == `output/deck/pres_read.json` == `output/deck/batch.json` `276` text strings & `16` speaker notes).
   - **ALL 302 text runs (251 shape runs + 51 table-cell runs)** in `pres_read.json` pass WCAG 2.0 contrast (`>= 4.50:1` normal, `>= 3.00:1` large) against their true z-ordered background shape/cell/slide fill — specifically confirming all 7 previously failing runs (Slide 5 `_131`/`_141`, Slide 7 `_205`, Slide 15 table `[4,3]`, `[6,0]`, `[6,3]`, `[6,4]`, plus `[3,3]`/`[5,3]`) now pass!
   - Exact Slide 08 (`_237.._245`: `h=53, 53, 70`, bottom `<=336`) and Slide 12 (`_359.._370`: `h=87, 87, 72`, bottom `<=348`) live geometry with zero `scaleX`/`scaleY` distortion.
   - Zero margin violations (`[30,690]×[30,375]`), zero pairwise text/table/image overlaps, zero placeholders, `100%` explicit colors & `Montserrat`/`Roboto` fonts.
   - Updated `output/Quality_Moat_Screener_v7.19.pptx` (`testzip() == None`, 16 slides, 16 notesSlides, 3 embedded media PNGs), `output/verify/deck_export.pdf` (16 pages), and `output/verify/slide_01..16.png` (`1440×810`).

Maintain `progress.md` (`Last visited: [timestamp]`), write full script output & explicit **`APPROVE`** or **`REQUEST_CHANGES`** verdict to `handoff.md`, and send summary via `send_message` to `628d3c94-387f-425c-b1c2-0f102895e566`.
