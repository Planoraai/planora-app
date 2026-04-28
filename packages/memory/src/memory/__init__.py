"""Memory and personalization layer.

Three-tier memory model (see docs/architecture.md §4.7):

  - short-term run state ........ `InMemoryRunStateStore`
  - planner result cache (TTL/LRU) `InMemoryPlannerResultCache`
  - long-term user preferences .. `InMemoryUserPreferenceStore` + `UserPreferenceProfile`

The composed `MemoryAwarePlanner` wraps an underlying planner with cache lookup,
preference-aware prompt augmentation (`apply_profile_to_prompt`), and run-state persistence.

Originally lived as `phases/phase9/src/phase9/memory_personalization.py` during the phase-wise
build-out (see docs/implementationPlan.md Phase 9). Moved to `packages/memory/` in Pass 4.
"""

from __future__ import annotations

from memory.store import (
    InMemoryPlannerResultCache,
    InMemoryRunStateStore,
    InMemoryUserPreferenceStore,
    MemoryAwarePlanner,
    RunStateRecord,
    UserPreferenceProfile,
    apply_profile_to_prompt,
)

__all__ = [
    "InMemoryPlannerResultCache",
    "InMemoryRunStateStore",
    "InMemoryUserPreferenceStore",
    "MemoryAwarePlanner",
    "RunStateRecord",
    "UserPreferenceProfile",
    "apply_profile_to_prompt",
]
