"""Reliability and hardening layer.

Wraps the planner with production-shape guarantees:

  - `ModelTierPolicy` ........ tier selection / graceful downgrade
  - `with_retry` ............. bounded-retry decorator with backoff
  - `CircuitBreaker` ......... per-dependency open/half-open/closed state
  - `HardenedPlannerService` . composes the three above + latency budget +
                               result-shape validation

Originally lived as `phases/phase10/src/phase10/hardening.py` during the phase-wise
build-out (see docs/implementationPlan.md Phase 10). Moved to `packages/reliability/` in Pass 4.
"""

from __future__ import annotations

from reliability.hardening import (
    CircuitBreaker,
    HardenedPlannerService,
    ModelTierPolicy,
    with_retry,
)

__all__ = ["CircuitBreaker", "HardenedPlannerService", "ModelTierPolicy", "with_retry"]
