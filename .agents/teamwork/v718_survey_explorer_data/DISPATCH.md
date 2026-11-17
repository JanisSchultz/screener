# Dispatch — v718_survey_explorer_data

## 2026-11-17T15:33:30Z
Assigned Role: `teamwork_explorer` (Data & 121 Incomplete Moat Franchises Survey)
Parent Orchestrator: `d510ad6d-e687-40ee-9300-d03ba5fff497`
Authoritative Request: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md`
Working Directory: `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data`

Task:
Read `ORIGINAL_REQUEST.md` first, then inspect (read-only) `data/us/`, `data/eu/`, `data/ca/` (`inputs.csv`, `universe.json`, `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv`):
1. Verify exact universe & funnel counts across US, EU, CA:
   - Total companies, Gate 3 reaching (989?), Gate 3 advancing (485 = 483 `3b=="Y"` + `EL` + `APD` on calamity pass?), Gate 3 rejects (504?), Prime Grade (225?), Prime Grade Calamity (13 total / 11 < 3 G6 flags?).
2. Identify EVERY ONE of the 121 incomplete moat franchises (expected: 108 Gate-4 rejects at `CAP = 5Y / 10Y` across 57 US, 51 EU, 0 CA + 13 Gate-5 rejects at `5 = 0` across 9 US, 4 EU, 0 CA).
3. Group all 121 incomplete companies strictly by **GICS Sector / Sub-Industry across US and EU combined** (never split US vs EU!). For each GICS Sector and Sub-Industry, list:
   - The incomplete companies (region, ticker, name, CAP/4, current 5, current 6, calamity, mirror status)
   - How many already-completed moat franchises (out of the 364 completed) exist in the exact same Sub-Industry / Sector for peer benchmarking!
   - Propose an optimal sector-based batching plan across US+EU combined for R2 evaluator agents.
4. Check `CRM` specifically: its current `inputs.csv` row, `CAP`, `note` text (stale `CAP = 10` text?), and mirror status.
5. Check dual-listed mirrors (`ASML`/`ASML.NL`, `FER`/`FER.ES`, and any other mirrors in `universe.json`) — are any in the 121?
6. Document the exact schema & fields available in `financials.csv`, `fundamentals_panel.csv`, `prescreen.csv` (`g6_default`, `g6_checks`, etc.), and `inputs.csv` (`note`, `evidence`, etc.) so evaluators know exact column names and data coverage.
7. Check `"Downstream gates bypassed per waterfall."` occurrences across all `inputs.csv` files (exact strings/variants on the 121 rows vs any other rows).

Deliverables:
Write `analysis.md` and `handoff.md` in your working directory (`/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/v718_survey_explorer_data`), then notify parent `d510ad6d-e687-40ee-9300-d03ba5fff497` via `send_message`.
