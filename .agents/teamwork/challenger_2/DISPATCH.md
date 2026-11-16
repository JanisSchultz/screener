## 2026-11-16T11:51:16Z
You are Challenger 2 (Boundary, Mirror Parity & Mutation Stress Challenger).
Your working directory is: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/challenger_2/
You must read ORIGINAL_REQUEST.md: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md
and PROJECT.md: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/PROJECT.md

Mandate:
1. Write and execute stress tests on dual-listed mirrors (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`):
   - Test that every qualitative field, note, and evidence field matches 100% character-for-character.
   - Test mutation sensitivity: verify that if a field differed, `screener/bulk_scorer.py --audit` or tests would catch it.
2. Stress test the cockpit HTML files:
   - Verify `output/screener.html`, `output/index.html`, and `docs/index.html` contain the newly scored companies, the correct number of prime companies (223 prime, 11 calamity prime), and valid non-corrupted tables.
3. Check for boundary conditions across universes (`us`, `eu`, `ca`).
4. Write `handoff.md` in your working directory with an explicit verdict (`APPROVE` or `REQUEST_CHANGES`).
5. Send a completion message to your parent (conv ID: 52860145-8fc7-4969-8b2b-b7788e50408a).
