#!/usr/bin/env python3
"""Release smoke checks for local/staging/production URLs."""

from __future__ import annotations

import json
import os
import sys
import urllib.request


def _get_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=5) as response:  # nosec B310
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def main() -> int:
    base_url = os.getenv("SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
    if len(sys.argv) > 1 and sys.argv[1].strip():
        base_url = sys.argv[1].rstrip("/")

    health = _get_json(f"{base_url}/healthz")
    ready = _get_json(f"{base_url}/readyz")
    if health.get("status") != "ok":
        print("healthz failed")
        return 1
    if ready.get("status") != "ready":
        print("readyz failed")
        return 1
    print(f"release smoke passed for {base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
