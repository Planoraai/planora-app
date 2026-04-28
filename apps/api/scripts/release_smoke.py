#!/usr/bin/env python3
"""Basic release smoke checks for Phase 10."""

from __future__ import annotations

import json
import urllib.request


def _get_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=5) as response:  # nosec B310
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def main() -> int:
    health = _get_json("http://localhost:8000/healthz")
    ready = _get_json("http://localhost:8000/readyz")
    if health.get("status") != "ok":
        print("healthz failed")
        return 1
    if ready.get("status") != "ready":
        print("readyz failed")
        return 1
    print("release smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
