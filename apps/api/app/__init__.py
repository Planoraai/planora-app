"""apps/api integration shell: wires the platform package into the ASGI app and exposes its version."""

from __future__ import annotations

from app_platform import __version__

__all__ = ["__version__"]
