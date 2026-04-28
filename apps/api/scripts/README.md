# scripts/

Operational helpers and one-off utilities (run from **`backend/`** unless noted).

| Script | Phase | Purpose |
|---|---|---|
| `ingest_kb.py` | 3 | Load curated travel docs from `data/kb/` into the vector DB |
| `replay_run.py` | 7 | Re-run a saved trip from its `run_id` for debugging |
| `seed_fixtures.py` | 2 | Refresh test fixtures from a real API run |
| `mypy_backend.py` | 0 | Invoked by root **pre-commit** to run `mypy app` with `cwd=backend/` |
| `pytest_backend.py` | 0 | Invoked by root **pre-commit** (pre-push) to run pytest from `backend/` |

Phase 0 ships the pre-commit helper scripts and this README; ingest/replay/seed arrive in later phases.
