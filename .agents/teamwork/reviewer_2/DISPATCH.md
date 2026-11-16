# DISPATCH: reviewer_2

You are Reviewer 2 (Qualitative Evaluation & Notes Depth).
Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/reviewer_2/
Parent Orchestrator ID: 52860145-8fc7-4969-8b2b-b7788e50408a
Original Request: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md
Project Scope: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT.md

## 2026-11-16T11:51:13Z
You are Reviewer 2 (Qualitative Evaluation & Notes Reviewer).
Your working directory is: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/reviewer_2/
You must read ORIGINAL_REQUEST.md: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md
and PROJECT.md: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT.md

Mandate:
1. Inspect the newly evaluated data in `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv`.
2. Sample companies across multiple sectors to verify `4n` notes depth: ensure they provide meaningful business-model and competitive force justifications rather than boilerplate or generic single-line strings.
3. Check that for every company where any competitive force (`4_ent`, `4_riv`, `4_buy`, `4_sup`, `4_sub`) >= 1, `4n` is non-empty.
4. Check companies with CAP >= 15 to verify they evaluated Gates 5 and 6, and verify that where Gate 5 was 0 without calamity, Gate 6 was correctly scrubbed per Munger waterfall.
5. Check Calamity pass rules and notes in `data/*/inputs.csv`.
6. Verify exact preservation of the 11 reference companies (`SPGI`, `COST`, `ASML.NL`, `ASML`, `MSFT`, `WM`, `RMS.FR`, `CNR.CA`, `HSY`, `CRM`, `NUE`).
7. Write `handoff.md` in your working directory with an explicit verdict (`APPROVE` or `REQUEST_CHANGES`).
8. Send a completion message to your parent (conv ID: 52860145-8fc7-4969-8b2b-b7788e50408a).
