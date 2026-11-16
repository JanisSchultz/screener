# Progress — worker_m3_ingest

Last visited: 2026-11-16T11:49:15Z

## Status: COMPLETE
- Step 1: Ingested 15 evaluated batch dossiers (978 companies) via `screener/bulk_scorer.py --ingest evaluations/completed --apply`. [PASSED]
- Step 2: Synchronized dual-listed mirrors (`ASML` <-> `ASML.NL`, `FER` <-> `FER.ES`) via `screener/bulk_scorer.py --sync-mirrors --apply`. [PASSED - 100% parity]
- Step 3: Ran comprehensive dataset audit via `screener/bulk_scorer.py --audit`. [PASSED - 0 formula discrepancies, 0 missing notes, 0 waterfall violations, 100% mirror parity]
- Step 4: Checked and verified baseline counts in `tests/test_calamity_tier.py` line 158 ({'us': 109, 'eu': 103, 'ca': 11}). [PASSED]
- Step 5: Ran unit tests via `python3 -m unittest discover tests`. [PASSED - 303 tests]
- Step 6: Ran cockpit build via `python3 build.py`. [PASSED - exit code 0, HTMLs regenerated]
- Step 7: Ran strict E2E test suite via `REQUIRE_ALL_SCORED=1 python3 -m unittest tests/test_bulk_scoring_e2e.py`. [PASSED - 134 tests]
- Step 8: Documented all commands, outputs, and findings in `handoff.md`.
