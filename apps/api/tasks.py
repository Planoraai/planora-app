"""Cross-platform task runner (Windows-friendly Makefile alternative).

Usage:
    invoke install-dev
    invoke dev
    invoke test
    invoke check

Run `invoke --list` to see all available tasks.
"""

from __future__ import annotations

from invoke.context import Context
from invoke.tasks import task


@task
def install(c: Context) -> None:
    """Install runtime dependencies."""
    c.run("python -m pip install -r requirements.txt")


@task
def install_dev(c: Context) -> None:
    """Install runtime + dev dependencies and pre-commit hooks."""
    c.run("python -m pip install -r requirements-dev.txt")
    c.run("pre-commit install")


@task
def run(c: Context) -> None:
    """Run the API server."""
    c.run("uvicorn app.main:app --host 0.0.0.0 --port 8000")


@task
def dev(c: Context) -> None:
    """Run the API server with auto-reload."""
    c.run("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")


@task
def test(c: Context) -> None:
    """Run the test suite."""
    c.run("pytest")


@task
def test_cov(c: Context) -> None:
    """Run tests with coverage."""
    c.run("pytest --cov=app --cov-report=term-missing --cov-report=html")


@task
def lint(c: Context) -> None:
    """Run the linter."""
    c.run("ruff check . ../../packages")


@task
def format_(c: Context) -> None:
    """Auto-format the code."""
    c.run("ruff format . ../../packages")
    c.run("ruff check --fix . ../../packages")


@task(name="type")
def type_check(c: Context) -> None:
    """Run static type checking."""
    c.run("mypy app")


@task
def precommit(c: Context) -> None:
    """Run all pre-commit hooks (expects repo root; run from apps/api/: cd ../.. first)."""
    c.run("cd ../.. && pre-commit run --all-files")


@task(pre=[lint, type_check, test])
def check(c: Context) -> None:
    """Lint + type-check + test (used by CI)."""


@task
def clean(c: Context) -> None:
    """Remove caches and build artefacts."""
    import shutil
    from pathlib import Path

    targets = [
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
        "build",
        "dist",
    ]
    for t in targets:
        p = Path(t)
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.is_file():
            p.unlink(missing_ok=True)
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
