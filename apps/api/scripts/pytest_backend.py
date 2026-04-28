#!/usr/bin/env python3
"""Run pytest from apps/api/ (invoked by pre-commit from repo root)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    return subprocess.call(
        [sys.executable, "-m", "pytest", "-q", "--no-header", *sys.argv[1:]],
        cwd=API_DIR,
    )


if __name__ == "__main__":
    raise SystemExit(main())
