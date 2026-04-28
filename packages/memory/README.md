# travel-planner-memory

Memory and personalization layer for the travel planner.

## What it provides

- `InMemoryRunStateStore` — short-term run-state persistence (correlation-id keyed)
- `InMemoryPlannerResultCache` — TTL + LRU cache over planner results, keyed by trip-brief hash
- `InMemoryUserPreferenceStore` + `UserPreferenceProfile` — long-term preference store
- `apply_profile_to_prompt(profile, base_prompt) -> str` — prompt augmentation helper
- `MemoryAwarePlanner` — composes the three above around an underlying planner

The in-memory implementations satisfy the same interfaces a future Postgres / Redis / Chroma
implementation will satisfy, so swapping is a one-line constructor change.

## Layout

```
src/memory/
  __init__.py        # public surface
  store.py           # full implementation
tests/
  test_memory_store.py
```

## Public API

```python
from memory import (
    InMemoryPlannerResultCache,
    InMemoryRunStateStore,
    InMemoryUserPreferenceStore,
    MemoryAwarePlanner,
    UserPreferenceProfile,
    apply_profile_to_prompt,
)
```

## Verify

```bash
cd ../../apps/api
pytest ../../packages/memory -q
```

## Origin

Originally `phases/phase9/src/phase9/memory_personalization.py` during the phase-wise
build-out (see `docs/implementationPlan.md` Phase 9). Moved here in Pass 4.
