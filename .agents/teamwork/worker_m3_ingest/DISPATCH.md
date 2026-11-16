# DISPATCH: Worker M3 Ingest & Baseline Update

## Objective
1. Run `python3 screener/bulk_scorer.py --ingest evaluations/completed --apply` to atomically apply all 15 completed evaluation batches into `data/us/inputs.csv`, `data/eu/inputs.csv`, and `data/ca/inputs.csv`.
2. Run `python3 screener/bulk_scorer.py --sync-mirrors --apply` to ensure 100% exact character-for-character parity for dual-listed mirrors (`ASML` <-> `ASML.NL` and `FER` <-> `FER.ES`).
3. Run `python3 screener/bulk_scorer.py --audit` to verify 0 formula discrepancies, 0 missing notes, 0 waterfall violations, and 100% mirror parity.
4. Recalculate the baseline counts for `tests/test_calamity_tier.py`:
   Run:
   `python3 -c "from screener.data import funnel_ids, load_universe; print({k: len(funnel_ids(load_universe(k), include_calamity=False)) for k in ('us', 'eu', 'ca')})"`
   Update line 158 of `tests/test_calamity_tier.py` with the newly verified counts.
5. Run the full unit test suite: `python3 -m unittest discover tests` — all tests must pass cleanly.
6. Run `python3 build.py` to regenerate the screener outputs (`output/screener.html`, `output/index.html`, and `docs/index.html`) — must exit 0.
7. Run the strict E2E test suite: `REQUIRE_ALL_SCORED=1 python3 -m unittest tests/test_bulk_scoring_e2e.py` — all 134 tests must pass cleanly.
8. Document all findings, commands, and outputs in `handoff.md`.
