# v7.19 Documentation & Specification Survey Analysis

## 1. Repository Documentation Inventory (Excluding `.agents/`)

All markdown, text, and specification/changelog sources discovered in the repository:

1. `QUALITATIVE_EVALUATION_SPEC.md` (350 lines) — Standalone qualitative evaluation spec (currently labeled `v7.18`).
2. `COMPANY_EVALUATION_SPEC.md` (661 lines) — Unified full-lifecycle evaluation spec (currently labeled `v7.18`).
3. `QUANTITATIVE_EVALUATION_SPEC.md` (234 lines) — Standalone quantitative DCF valuation spec (currently labeled `v7.7`).
4. `README.md` (396 lines) — Repository overview, inline release-notes block (currently headed `v7.7`, top block `v7.16`), layout map, workflows, deployment notes.
5. `evaluations/completed/README.md` (3 lines) — Note on completed batch JSON directory (no version/calamity/tab references; unaffected).
6. `data/{us,eu,ca}/universe.json` — Universe metadata & historical `how_produced` notes (no version/calamity/tab references; unaffected).
7. **Note on `CHANGELOG`**: There is **no** `CHANGELOG.md` or `CHANGELOG` file at repo root. As documented in `README.md:368` (`Add a CHANGELOG entry in screener/config.py when you change the framework.`), the authoritative `CHANGELOG` is the Python dictionary `CHANGELOG` in `screener/config.py:330–816`, paired with `SCREENER_VERSION = "7.18"` at `screener/config.py:328` and embedded in the dashboard HTML (`screener/dashboard.py:273`).
8. **Note on `.claude/` / prompts / `SKILL.md`**: No `SKILL.md`, prompt templates, or `.github/workflows/` markdown files exist in the repo (only `.claude/settings.local.json`, unaffected). However, `screener/dashboard.py:2048–2139` embeds the in-app **`📖 Framework`** reference tab HTML, and `screener/bulk_scorer.py:1–26, 1160` contains module/CLI documentation headers with `v7.18` and `989` Gate 3 counts.

---

## 2. Features Discovered (Spec & Documentation Surface)

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | Version References | Spec header & mandate version (`v7.18` -> `v7.19`) | Both qualitative & unified specs declare `(v7.18)` in H1 title and Section 1 overview | `QUALITATIVE_EVALUATION_SPEC.md:1,8`; `COMPANY_EVALUATION_SPEC.md:1,8` | Must display `v7.19` | Stale `v7.18` version mismatch with `SCREENER_VERSION` | `view_file`, `grep_search` |
| 2 | Version References | `README.md` header & release block (`v7.7` / `v7.16`) | H1 title says `v7.7`, layout line 299 says `v7.7`, release block starts with `v7.16` (missing `v7.17`, `v7.18`, `v7.19`) | `README.md:1,20–23,299` | Update H1 (if bumping to `v7.19`) and add `v7.19` (or note `v7.17–v7.19`) summary | Stale version / missing recent changelog in README | `view_file` |
| 3 | Version References | `QUANTITATIVE_EVALUATION_SPEC.md` version (`v7.7`) | H1, overview, and Steps 1–5 say `v7.7`; line 15 references `Calamity pass` | `QUANTITATIVE_EVALUATION_SPEC.md:1,8,15,56,60,99,122,145,166` | Remove `Calamity pass` from line 15; keep/update version as appropriate | Leaving `Calamity pass` on line 15 contradicts R2 retirement | `view_file`, `grep_search` |
| 4 | Version References | `COMPANY_EVALUATION_SPEC.md` Stage 2 Note (`v7.18`) | Example 4 (`CRM`) has `> **v7.18 Stage 2 Note**: ...` | `COMPANY_EVALUATION_SPEC.md:547` | Keep historical rationale or update phrasing cleanly without calamity | N/A (factual Stage 2 diagnostic note) | `view_file` |
| 5 | Version References | `SCREENER_VERSION` & `CHANGELOG` in `screener/config.py` | `SCREENER_VERSION = "7.18"` and `CHANGELOG` dict keyed by `"7.18"`, `"7.17"`, `"7.16"`, etc. | `screener/config.py:328,330,708–718` | Bump `SCREENER_VERSION = "7.19"` and add `"7.19": [...]` entry matching existing tone/format | `test_v718_two_stage_waterfall.py:491` asserts `CHANGELOG["7.18"]`; `7.19` test should mirror | `view_file`, `grep_search` |
| 6 | Calamity Retirement | Two-Stage Waterfall Calamity Tier & Exception Bullet | Section 1 Mandate Principle 2 defines `(with Conditional Calamity Tier on Gates 3b, 5 & 6 Only)`, `calamity_flag="Y"`, `calamity_note`, `unwaived`, `Anchor Gates`, `Calamity pass`, and dedicated Buffett Calamity Exception bullet | `QUALITATIVE_EVALUATION_SPEC.md:15–18`; `COMPANY_EVALUATION_SPEC.md:15–18` | Remove all Calamity Tier/exception bullets, `unwaived`, `calamity_flag`, `calamity_note`, Anchor Gate calamity-clearing rules; preserve clean Stage 1 (G1–G3 early stop) vs. Stage 2 (G4–G6 full diagnostic scorecard) | Leaving any waiver/calamity text violates R2 zero-reference acceptance criterion | `view_file`, `grep_search` |
| 7 | Calamity Retirement | ASCII Waterfall Diagram & Gate Actions | Diagram shows `Pass: Y (or Calamity-waived 3b with 3a != None)`, `Gate 4 ... Non-Waivable Anchor`, `Score = 0 (unwaived)`; Gate 3/4/5/6 Waterfall Actions reference `(unwaived)` and `clear calamity_flag / calamity_note` | `QUALITATIVE_EVALUATION_SPEC.md:49,60,63,67,147,186,207`; `COMPANY_EVALUATION_SPEC.md:52,63,66,70,144,172,193` | Simplify Gate 3b pass to `[Pass: Y]`, remove `(unwaived)` & `Non-Waivable Anchor`, remove calamity clearing on Gate 4 reject | Contradicts retired calamity mechanism | `view_file`, `grep_search` |
| 8 | Calamity Retirement | Quantitative Prerequisite References | Section 5 (`COMPANY_EVALUATION_SPEC.md:256`) and Section 1 (`QUANTITATIVE_EVALUATION_SPEC.md:15`) state quantitative valuation runs on `Quality pass` and `Calamity pass` | `COMPANY_EVALUATION_SPEC.md:256`; `QUANTITATIVE_EVALUATION_SPEC.md:15` | Restrict prerequisite wording to `Quality pass` (and note Quality Grade cohort valuation if applicable; remove `Calamity pass` completely) | Leaving `QUANTITATIVE_EVALUATION_SPEC.md:15` unedited leaves stale `Calamity pass` docs | `view_file`, `grep_search` |
| 9 | Calamity Retirement | JSON Schema Example & Field Mapping Table | Sample JSON includes `"calamity_flag": null`, `"calamity_note": null`; Mapping tables include `calamity`/`calamity_note` rows, `unwaived 3b="N"`, `unwaived Gate 3 fails`, and `for both Quality pass and Calamity pass` | `QUALITATIVE_EVALUATION_SPEC.md:299–300,327–338`; `COMPANY_EVALUATION_SPEC.md:365–366,393–404` | Remove `calamity_flag` and `calamity_note` keys from JSON examples and table rows; remove `unwaived` and `Calamity pass` from `note` & nullable rules | `apply_evaluation.py` validation & schema docs diverge if left | `view_file` |
| 10 | Calamity Retirement | Ingestion & Handoff Protocol Sections | `QUALITATIVE_EVALUATION_SPEC.md:349` and `COMPANY_EVALUATION_SPEC.md:647,653,660` reference `unwaived 3b="N"`, `clearing calamity if Gate 4 fails`, `inputs.csv` columns `calamity, calamity_note`, and `⚠️ Calamity Watchlist` tab | `QUALITATIVE_EVALUATION_SPEC.md:349`; `COMPANY_EVALUATION_SPEC.md:647,653,660` | Remove `unwaived`, `calamity`, `calamity_note`, and `⚠️ Calamity Watchlist`; update tab names in `COMPANY_EVALUATION_SPEC.md:660` | Misleads evaluator/coordinator agents on CSV schema and dashboard tabs | `view_file` |
| 11 | Calamity Retirement | `README.md` Overview, Layout & Release Notes | Line 17 describes `"Calamity pass"` and `Calamity Watchlist`; line 307 (`inputs.csv` layout) lists `calamity flag/note`; lines 63 & 133–136 are historical `v7.1` and `v6.25` changelog bullets | `README.md:17,63,133–136,307` | Remove calamity from lines 17 and 307; **clarify R2 treatment of historical release bullets** (lines 63, 133–136) vs. active spec text | Zero-grep check on `README.md` for `calamity` would still hit lines 63 & 133–136 unless intentionally handled/removed | `view_file`, `grep_search` |
| 12 | Dashboard UX & Tiers | `COMPANY_EVALUATION_SPEC.md` Tab List (`660`) | Currently cites obsolete v7.7 tab names: `🛡️ Quality Pass Funnel`, `⚠️ Calamity Watchlist`, `🔍 Full Universe & Waterfall` | `COMPANY_EVALUATION_SPEC.md:660` | Update to v7.19 tabs: `🛡️ Prime Grade`, `💎 Growth at ~0g`, `🏰 Quality Grade`, `🔍 Full Universe` (plus `📖 Framework`) | Stale tab names in spec | `view_file` |
| 13 | Dashboard UX & Tiers | `screener/dashboard.py` `📖 Framework` Tab HTML | Lines 2081–2084 define `Prime Grade Calamity`; lines 2085–2093 (`Dashboard Views & Quality Tiers`) list `Prime Grade`, `Prime Grade Calamity`, `Quality Grade`, `Full Universe` | `screener/dashboard.py:2048–2139` (specifically 2081–2093) | Remove `Prime Grade Calamity` box; add `💎 Growth at ~0g` tier description (`passes_quality_grade` + `val_status == 'Valued'` + `g_market_flag in ('ok', 'saturated_low')` + `g_market < 5.0%` + `g_org_exp >= 5.0%`) | In-app Framework documentation out of sync with UI tabs | `view_file` |
| 14 | Dashboard UX & Tiers | Top-bar KPIs, Tab Bar & `#filter-gate` | KPI chip `Prime Grade Calamity` (`1882`); Tab `⚠️ Prime Grade Calamity` (`1899–1903`); `#filter-gate` hidden on non-Quality/Universe tabs (`1979–1991`) and includes `Calamity pass` option (`1984`) | `screener/dashboard.py:1872–1918,1979–1991` | Replace KPI chip with `Growth at ~0g` (`25`); replace tab #2 with `💎 Growth at ~0g` (`💎 ~0g Growth` mobile); enable `#filter-gate` on `💎 Growth at ~0g`; remove `Calamity pass` option | Spec/UI mismatch | `view_file` |
| 15 | `~0g` / `Growth at ~0g` Concept | Absence from Existing Docs | Zero occurrences of `~0g`, `Growth at ~0g`, or `passes_growth_0g` exist in any `.md` or `.py` file currently | All `.md` and `.py` files | Must document `💎 Growth at ~0g` (`passes_growth_0g` predicate, slot #2, KPI chip, default `g_org_exp` desc sort, `#filter-gate`, columns) in `README.md`, `COMPANY_EVALUATION_SPEC.md`, `screener/dashboard.py` Framework tab, and `CHANGELOG["7.19"]` | Undocumented new v7.19 tier | `grep_search` |
| 16 | Funnel Counts & Metrics | Live Counts vs. Documented Counts | Live v7.18 counts: `1175` total, `989` Gate 3 (`485` Stage-2 advancing + `504` Gate-3 rejects), `225` Prime Grade, `13` Calamity (`11` passing `<3` G6 flags). Under v7.19: `2` `3b=N` calamity names (`APD`, `EL`) scrub to G3 rejects -> `483` Stage-2 advancing + `506` G3 rejects = `989`; `11` `3b=Y` retain G4–G6 (`10` in `Quality Grade`); `Prime Grade` = `225`; `Growth at ~0g` = `25` (`9` Prime Grade, `6` CAP >= 15Y G6=N, `10` CAP 5–10Y) | `screener/config.py:711–714` (`v7.18` changelog cites `485`, `225`, `11/13`); `screener/bulk_scorer.py:3,7` (`989`) | Preserve historical `7.18` counts in `CHANGELOG["7.18"]`; record new v7.19 counts (`483` advancing / `506` G3 rejects / `989` G3 total, `225` Prime Grade, `25` Growth at ~0g) in `CHANGELOG["7.19"]` and `README.md` | Mutating `CHANGELOG["7.18"]` falsifies historical release notes | `run_command`, `view_file` |

---

## 3. Exact Line-by-Line Change Map per Documentation File

### A. `QUALITATIVE_EVALUATION_SPEC.md` (350 lines)
- **Lines 1, 8**: `v7.18` → `v7.19`.
- **Line 15**: Remove `(with Conditional Calamity Tier on Gates 3b, 5 & 6 Only)`.
- **Line 16**: `or unwaived Gate 3 (3a="None" or unwaived 3b="N")` → `or Gate 3 (3a="None" or 3b="N")`.
- **Line 17**: Remove `or calamity_flag="Y"`, `without calamity`, `unwaived`, and `Gate 4 (4 >= 15) remains a strictly non-waivable Anchor Gate (any 4 < 15 clears calamity_flag / calamity_note and rejects at Gate 4 while preserving diagnostic 5 and 6)` → replace cleanly with Gate 4 rejection preserving diagnostic `5` and `6`.
- **Line 18**: Delete entire `- **Exception (Buffett Temporary Fixable Calamities)**: ...` bullet.
- **Line 49**: Remove `unwaived` before `failing gate`.
- **Line 60**: `│ [Pass: Y (or Calamity-waived 3b with 3a != None)]` → `│ [Pass: Y]`.
- **Line 63**: Remove `; Non-Waivable Anchor`.
- **Line 67**: Remove `(unwaived)` from `Score = 0 (unwaived)`.
- **Line 147**: Remove `(unwaived)` before `3b == "N"`.
- **Line 186**: Remove `, clear calamity_flag / calamity_note if set (Gate 4 is a non-waivable Anchor Gate)`.
- **Line 207**: Remove `unwaived` before `5 < 1`.
- **Lines 299–300**: Remove `"calamity_flag": null,` and `"calamity_note": null,` from JSON example.
- **Lines 327–335**: Remove `unwaived` in Nullable Rules column (9 rows).
- **Lines 336–337**: Delete `calamity` and `calamity_note` table rows.
- **Line 338**: `for both Quality pass and Calamity pass` → `for Quality pass`.
- **Line 349**: Remove `unwaived` and `while clearing calamity if Gate 4 (4 < 15) fails`.

### B. `COMPANY_EVALUATION_SPEC.md` (661 lines)
- **Lines 1, 8**: `v7.18` → `v7.19`.
- **Line 15**: Remove `(with Conditional Calamity Tier on Gates 3b, 5 & 6 Only)`.
- **Line 16**: Remove `unwaived` (2 occurrences).
- **Line 17**: Remove `or calamity_flag="Y"`, `without calamity`, `unwaived`, and `Gate 4 (4 >= 15) remains a non-waivable Anchor Gate (any 4 < 15 clears calamity_flag / calamity_note and rejects at Gate 4 while preserving diagnostic 5 and 6)` → keep Stage 2 diagnostic `5` and `6` preservation on `4 < 15`.
- **Line 18**: Delete entire `- **Buffett Calamity Exception**: ...` bullet.
- **Line 52**: Remove `unwaived`.
- **Line 63**: `│ [Pass: Y (or Calamity-waived 3b with 3a != None)]` → `│ [Pass: Y]`.
- **Line 66**: Remove `; Non-Waivable Anchor`.
- **Line 70**: Remove `(unwaived)`.
- **Line 144**: Remove `(unwaived)`.
- **Line 172**: Remove `, clear calamity_flag / calamity_note if set (Gate 4 is a non-waivable Anchor Gate)`.
- **Line 193**: Remove `unwaived`.
- **Line 256**: Remove `, as well as Calamity pass candidates (conditional waiver on Gates 3b, 5, and/or 6)`.
- **Lines 365–366**: Remove `"calamity_flag": null,` and `"calamity_note": null,` from JSON example.
- **Lines 393–401**: Remove `unwaived` in Nullable Rules column (9 rows).
- **Lines 402–403**: Delete `calamity` and `calamity_note` table rows.
- **Line 404**: `for Quality pass and Calamity pass` → `for Quality pass`.
- **Line 547**: `> **v7.18 Stage 2 Note**: ...` — note: either retain as historical v7.18 note or update label to Stage 2 Note (`v7.18+`).
- **Line 647**: Remove `unwaived` and `while clearing calamity if Gate 4 (4 < 15) fails`.
- **Line 653**: Remove `` `calamity`, `calamity_note`, `` from `inputs.csv` column list.
- **Line 660**: Replace obsolete tab names (`🛡️ Quality Pass Funnel`, `⚠️ Calamity Watchlist`, and `🔍 Full Universe & Waterfall`) with `🛡️ Prime Grade`, `💎 Growth at ~0g`, `🏰 Quality Grade`, and `🔍 Full Universe`.
- *Optional/Recommended*: Add a brief description of dashboard tiers (`Prime Grade`, `💎 Growth at ~0g`, `Quality Grade`) in Section 5 or Section 8 Step 3.

### C. `QUANTITATIVE_EVALUATION_SPEC.md` (234 lines)
- **Line 15**: Contains TWO occurrences of `Calamity pass`:
  - `companies that achieve Quality pass across the 6 qualitative gates or Calamity pass (conditional override on Gates 3b, 5, and/or 6). For Calamity pass businesses, check whether normalized earning power or forward growth still reflects pre-calamity peaks.`
  - Must be cleaned up to remove `Calamity pass` (keep `Quality pass` and `Since v7.6 there are no analyst overrides...`).
- **Lines 1, 8, 56, 60, 99, 122, 145, 166**: Still stamped `v7.7` (model math unchanged since v7.7; note to orchestrator whether to leave `v7.7` or align).

### D. `README.md` (396 lines)
- **Line 1**: Currently `# Quality & Moat Screener (v7.7 — ...)`; consider updating to `v7.19` (or updating the top summary).
- **Line 17**: Currently: `-> "Quality pass" and conditional "Calamity pass" (temporary fixable calamities on Gates 3b, 5, or 6 only, while Gates 1, 2, 3a, and 4 pass) enter the Quantitative sheet (...), separated into clean Shortlists vs. the Calamity Watchlist.` → Rewrite to remove `Calamity pass`, calamity waiver rule, and `Calamity Watchlist`, and describe `Prime Grade` (`Quality pass`) + `💎 Growth at ~0g` (`Quality Grade` companies with `Mkt Implied g < 5.0%` and organic `Model g >= 5.0%`) + `Quality Grade`.
- **Lines 20–23**: Currently latest entry in inline release notes is `v7.16`; add `v7.19` summary block (and optionally `v7.17`–`v7.18` or note `screener/config.py` `CHANGELOG`).
- **Line 63** (`v7.1` historical note) & **Lines 133–136** (`v6.25` historical note): Contain `calamity` / `Calamity pass` / `Calamity Watchlist`!
  - **Caveat for R2**: `ORIGINAL_REQUEST.md` Acceptance Criteria states: *"Zero references to `calamity`, `calamity_note`, `RES_CALAMITY`, or calamity-waiver logic remain across ... `README.md`"*. If an automated `grep -i calamity README.md` check is run, lines 63 and 133–136 will match unless either (a) those historical notes in `README.md` are purged/redacted or (b) the zero-reference check excludes historical `v6.25` / `v7.1` changelog blocks. Recommend flagging this explicitly to the orchestrator!
- **Line 307 (`## Layout`)**: `inputs.csv Phase 1–3 inputs per company (Y/N gates, 0/1/2 scores, CAP years, calamity flag/note, notes, evidence)` → remove `calamity flag/note, `.

### E. `screener/config.py` (`CHANGELOG` & `SCREENER_VERSION`)
- **Line 328**: `SCREENER_VERSION = "7.18"` → `"7.19"`.
- **Lines 708–718**: Existing `"7.18"` entry in `CHANGELOG` (placed right after `"7.0"` and before `"7.17"`, i.e., reverse chronological `7.18`, `7.17`, `7.16`, ...).
  - Format convention: Key is string `"7.19"` (no `"v"` prefix); value is a `list[str]` containing 1+ paragraphs, typically starting with a title line ending in `:` followed by numbered `(1)`, `(2)`, `(3)` items with concrete numbers, file names, and ticker/metric details.
  - Suggested placement: Insert `"7.19": [...]` immediately before `"7.18": [` at line 708 (preserving `"7.18"` and earlier historical entries intact).
- **Lines 239–245, 313–314, 317, 323, 326**: `CALAMITY_GATES`, `CALAMITY_FLAG_DEF`, `RES_CALAMITY`, `FUNNEL_RESULTS`, `Q_RESULTS`, `V_CALAMITY`, `LIST_CAPACITY` — all must be removed/updated per R2.

### F. `screener/dashboard.py` (Embedded `📖 Framework` Tab & UI Docs)
- **Lines 1881–1884**: `Prime Grade Calamity` KPI chip → `Growth at ~0g` KPI chip (`25` total).
- **Lines 1893–1918**: Tab bar order → `🛡️ Prime Grade` (`🛡️ Prime`) → `💎 Growth at ~0g` (`💎 ~0g Growth`) → `🏰 Quality Grade` (`🏰 Quality`) → `🔍 Full Universe` (`🔍 All`) → `📖 Framework`.
- **Lines 1979–1991**: `#filter-gate` comment & options → enable for `growth_0g` tab too, remove `Calamity pass` option.
- **Lines 2048–2095**: `📖 Framework` HTML section:
  - Delete `Prime Grade Calamity (Conditional Pass — Gates 3b, 5, 6 Only)` card (lines 2081–2084).
  - Update `Dashboard Views & Quality Tiers` card (lines 2085–2093): replace `⚠️ Prime Grade Calamity` bullet with `💎 Growth at ~0g` bullet describing the `passes_quality_grade` + `val_status == 'Valued'` + `g_market_flag in ('ok', 'saturated_low')` + `g_market < 5.0%` + `g_org_exp >= 5.0%` selection.

---

## 4. Edge Cases Discovered

| # | Feature | Input / File | Observed Behavior |
|---|---|---|---|
| 1 | `CHANGELOG` location | Repo root vs. `screener/config.py` | There is no `CHANGELOG.md` file; `CHANGELOG` is a Python dict in `screener/config.py:330`, referenced by `README.md:368` and `screener/dashboard.py:273`. |
| 2 | `README.md` historical changelog vs. zero-reference grep | `README.md:63,133–136` | Historical `v7.1` and `v6.25` release bullets in `README.md` mention `calamity`, `Calamity pass`, and `Calamity Watchlist`. A naive `grep -i calamity README.md` will fail R2 unless historical bullets are edited or exempted. |
| 3 | `QUANTITATIVE_EVALUATION_SPEC.md` omitted from R2 list | `QUANTITATIVE_EVALUATION_SPEC.md:15` | R2 explicitly named `QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `README.md`, omitting `QUANTITATIVE_EVALUATION_SPEC.md` — yet line 15 has two `Calamity pass` references. |
| 4 | `COMPANY_EVALUATION_SPEC.md` stale tab names | `COMPANY_EVALUATION_SPEC.md:660` | Still uses pre-v7.8 tab names (`🛡️ Quality Pass Funnel`, `⚠️ Calamity Watchlist`, `🔍 Full Universe & Waterfall`) instead of v7.19 names. |
| 5 | Historical `CHANGELOG` entries in `screener/config.py` | `screener/config.py:577–588,708–718,741–746,759–765` | Historical entries `"6.25"`, `"7.8"`, `"7.9"`, `"7.14"`, `"7.15"`, `"7.18"` mention `Calamity` / `calamity_pass`. Note R2 acceptance criterion explicitly scopes zero-calamity-references to `screener/gates.py`, `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/config.py`, `screener/data.py`, `screener/fetch/sqlite_db.py`, `screener/dashboard.py`, `data/{us,eu,ca}/inputs.csv`, tests, and spec docs — meaning `screener/config.py` historical `CHANGELOG` strings would also trip a literal `grep -i calamity screener/config.py` unless carefully handled or exempted! |
| 6 | Live Gate-3 / Calamity counts check | `data/{us,eu,ca}/inputs.csv` via `collect_screener_data` | Current v7.18 live state: `1175` total (`us=515, eu=602, ca=58`), `989` Gate 3 companies, `485` Stage-2 advancing, `504` Gate-3 rejects, `225` Prime Grade, `13` `Calamity pass` (`11` passing `<3` G6 flags; `11` have `3b=Y`, `2` (`APD`, `EL`) have `3b!=Y`). Matches `ORIGINAL_REQUEST.md` arithmetic (`485 - 2 = 483` advancing, `504 + 2 = 506` G3 rejects, `483 + 506 = 989`). |
