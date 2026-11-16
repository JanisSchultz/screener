# Dispatch for survey_explorer_engine
Target: Investigate evaluation engine, build scripts, and test suite.

## 2026-11-16T10:35:02Z
You are an Engine and Test Explorer.
Working directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_explorer_engine/
Workspace directory: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener
Original request path: /Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/ORIGINAL_REQUEST.md
Parent conversation ID: 52860145-8fc7-4969-8b2b-b7788e50408a

TASK:
Investigate the evaluation engine, build process, and test suite:
1. Analyze `screener/apply_evaluation.py` and any related scripts in `screener/`:
   - How does `screener/apply_evaluation.py` execute? What arguments does it accept?
   - How does it apply the sequential Munger reject waterfall? Which fields are cleared downstream on gate rejection?
   - How does it calculate deterministic CAP (`4`) and primary moat (`3a`)?
   - How does it synchronize mirror tickers?
   - How does it handle Calamity pass rules?
2. Analyze `build.py`:
   - What does `python3 build.py` do? What inputs does it read, what outputs does it generate (`output/screener.html`, `output/index.html`, `docs/index.html`)?
3. Analyze the test suite in `tests/`:
   - What tests exist?
   - Specifically inspect `tests/test_calamity_tier.py`: what baseline universe count assertions exist? How are counts validated? What counts will need to be updated when scoring shifts companies between quality/calamity pass and rejected states?
   - Run the test suite (`python3 -m unittest discover tests`) to observe the current baseline pass/fail status and output.

OUTPUT:
Write a comprehensive report to `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_explorer_engine/handoff.md`.
Keep progress updated in `/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener/.agents/teamwork/survey_explorer_engine/progress.md`.
When finished, send a message to the orchestrator (conversation ID: 52860145-8fc7-4969-8b2b-b7788e50408a) using send_message.
