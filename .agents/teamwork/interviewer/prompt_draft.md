Build an implementation plan first, then carry out the v7.19 changes to retire the `Calamity` tier end-to-end across the Quality & Moat Screener and add the `💎 Growth at ~0g` tab showing Quality Grade companies trading near their 0g price (`Mkt Implied g < 5.0%` and organic `Model g >= 5.0%`).

Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Integrity mode: development

## Requirements

### R1. Implementation Plan
- Produce a concrete implementation plan covering the `Calamity` retirement, `💎 Growth at ~0g` tab, data transitions, test updates, spec updates, and build/verification steps before making edits, then execute the plan end-to-end.

### R2. Full Retirement of `Calamity` End-to-End
- Remove `calamity`, `calamity_note`, `RES_CALAMITY` (`Calamity pass`), and calamity-waiver logic across `screener/gates.py`, `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/config.py`, `screener/data.py`, `screener/fetch/sqlite_db.py`, `screener/dashboard.py`, `data/{us,eu,ca}/inputs.csv`, tests, and spec docs (`QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `README.md`).
- Preserve `Prime Grade` at `225`, retain full Gate 4–6 scores and notes for the `11` former calamity companies with `3b = Y` (`DGE.GB`, `NESN.CH`, `RTO.GB`, `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN`; `10` remaining in `🏰 Quality Grade`), and apply Stage-1 waterfall scrubbing to `APD` and `EL` (`3b = N`) so they become standard Gate 3 rejects (`483` Stage-2 advancing + `506` Gate-3 rejects = `989` Gate-3 companies).

### R3. New Tab: `💎 Growth at ~0g` (Mobile: `💎 ~0g Growth`)
- Add predicate `passes_growth_0g` matching companies that satisfy `passes_quality_grade` (`G1 = Y`, `G2 = Y`, `3a != None`, `3b = Y`, `< 3` Gate 6 numeric flags), `val_status == 'Valued'`, `g_market_flag in ('ok', 'saturated_low')` with `g_market < 0.05` (`Mkt Implied g < 5.0%`), and `g_org_exp >= 0.05` (organic `Model g >= 5.0%`), yielding `25` companies today (`9` Prime Grade, `6` `CAP >= 15Y` failing `G6 = N`, `10` `CAP = 5–10Y`).
- Place `💎 Growth at ~0g` in slot #2 of the tab bar (`🛡️ Prime Grade` default landing tab → `💎 Growth at ~0g` → `🏰 Quality Grade` → `🔍 Full Universe` → `📖 Framework`), replace the top-bar `Prime Grade Calamity` KPI chip with `Growth at ~0g` (`25`), default-sort by `Model g ↓` (`g_org_exp` descending), enable `#filter-gate` on `💎 Growth at ~0g` (for 1-click filtering to `Prime Grade Only` or specific failing gates), and surface `G5 Mgmt`, `G6 B/S`, `Gate Status`, and `Failing Gate` alongside the core valuation columns.

### R4. Version Bump, Build & Verification
- Bump version to `v7.19` and update `CHANGELOG`, run `screener/bulk_scorer.py --audit`, run the full `unittest` suite, and regenerate `output/screener.html`, `output/index.html`, and `docs/index.html` via `build.py`.

## Verification Resources
- `screener/bulk_scorer.py --audit`
- Full `unittest` test suite (`python3 -m unittest discover -s tests`)
- `build.py`

## Acceptance Criteria

### Implementation Plan & Calamity Retirement
- [ ] An implementation plan covering the `Calamity` retirement, `💎 Growth at ~0g` tab, data transitions, test updates, spec updates, and build verification is produced before making implementation changes.
- [ ] Zero references to `calamity`, `calamity_note`, `RES_CALAMITY`, or calamity-waiver logic remain across `screener/gates.py`, `screener/apply_evaluation.py`, `screener/bulk_scorer.py`, `screener/config.py`, `screener/data.py`, `screener/fetch/sqlite_db.py`, `screener/dashboard.py`, `data/{us,eu,ca}/inputs.csv`, tests, and spec docs (`QUALITATIVE_EVALUATION_SPEC.md`, `COMPANY_EVALUATION_SPEC.md`, `README.md`).
- [ ] `Prime Grade` remains `225`; the `11` former calamity companies with `3b = Y` (`DGE.GB`, `NESN.CH`, `RTO.GB`, `GOOGL`, `NDAQ`, `HONA`, `NOC`, `RTX`, `EFX`, `SNPS`, `TXN`) retain their Gate 4–6 scores and notes (`10` in `🏰 Quality Grade`); `APD` and `EL` follow Stage-1 waterfall scrubbing and become standard Gate 3 rejects (`483` Stage-2 advancing + `506` Gate-3 rejects = `989` Gate-3 companies).

### `💎 Growth at ~0g` Tab & Dashboard
- [ ] `passes_growth_0g` selects the `25` matching companies (`9` Prime Grade, `6` `CAP >= 15Y` failing `G6 = N`, `10` `CAP = 5–10Y`) where `passes_quality_grade` is true, `val_status == 'Valued'`, `g_market_flag in ('ok', 'saturated_low')` and `g_market < 0.05`, and `g_org_exp >= 0.05`.
- [ ] The dashboard orders tabs `🛡️ Prime Grade` (default landing tab) → `💎 Growth at ~0g` (mobile `💎 ~0g Growth`) → `🏰 Quality Grade` → `🔍 Full Universe` → `📖 Framework`, replaces the `Prime Grade Calamity` KPI chip with `Growth at ~0g` (`25`), default-sorts the new tab by `g_org_exp` descending, enables `#filter-gate`, and displays `G5 Mgmt`, `G6 B/S`, `Gate Status`, and `Failing Gate` alongside the core valuation columns.

### Version, Audit, Tests & Build
- [ ] Version is bumped to `v7.19` with `CHANGELOG` updated.
- [ ] `python3 screener/bulk_scorer.py --audit` passes with zero errors or discrepancies.
- [ ] `python3 -m unittest discover -s tests` passes 100%.
- [ ] `python3 build.py` completes cleanly and regenerates `output/screener.html`, `output/index.html`, and `docs/index.html`.
