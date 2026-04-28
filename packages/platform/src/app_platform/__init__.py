"""Platform layer: settings, logging, correlation IDs, minimal HTTP surface (health/readyz, app factory).

Originally lived as `phase0` during the phase-wise build-out (see docs/implementationPlan.md §2);
moved to `packages/platform` and renamed to `app_platform` to avoid shadowing the `platform`
stdlib module while keeping a domain-meaningful folder name on disk.
"""

from __future__ import annotations

__version__ = "0.1.0"

from app_platform.application_factory import create_app

__all__ = ["__version__", "create_app"]
