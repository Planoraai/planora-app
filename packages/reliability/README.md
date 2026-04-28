# travel-planner-reliability

Reliability and hardening layer for the travel planner.

## What it provides

- `ModelTierPolicy` — selects (and gracefully downgrades) the LLM tier per call
- `with_retry(fn, ...)` — bounded-retry decorator with exponential backoff
- `CircuitBreaker` — per-dependency open / half-open / closed state machine
- `HardenedPlannerService` — composes the three above around an underlying planner and adds:
  - latency budget enforcement
  - result-shape validation against domain contracts
  - graceful degradation paths when individual workers fail

## Layout

```
src/reliability/
  __init__.py        # public surface
  hardening.py       # full implementation
tests/
  test_hardening.py
```

## Public API

```python
from reliability import CircuitBreaker, HardenedPlannerService, ModelTierPolicy, with_retry
```

## Verify

```bash
cd ../../apps/api
pytest ../../packages/reliability -q
```

## Origin

Originally `phases/phase10/src/phase10/hardening.py` during the phase-wise build-out
(see `docs/implementationPlan.md` Phase 10). Moved here in Pass 4.
