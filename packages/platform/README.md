# `packages/platform/` — Platform layer

The cross-cutting foundation every other package and the API service depend on:
typed configuration, structured logging, correlation-ID middleware, the FastAPI
application factory, and `/healthz` + `/readyz` routes.

Originally implemented as `phases/phase0` (see `docs/implementationPlan.md` §2). Moved
to `packages/platform/` during the domain-driven reorganisation. The on-disk folder is
named `platform/` for navigability; the actual Python package is **`app_platform`** to
avoid shadowing the `platform` stdlib module.

## Layout

| Path | Purpose |
|---|---|
| `src/app_platform/application_factory.py` | `create_app()` — builds the FastAPI app (lifespan, CORS, middlewares, health routes) |
| `src/app_platform/application_settings.py` | `Settings` (Pydantic) — typed env / `.env` loader, `get_settings()` cache |
| `src/app_platform/structured_logging.py` | `configure_logging`, `get_logger` (structlog with correlation-ID processor) |
| `src/app_platform/request_correlation.py` | `CorrelationIdMiddleware`, `get_correlation_id`, `new_correlation_id` |
| `src/app_platform/health_routes.py` | `/healthz` (liveness) and `/readyz` (real readiness probe) |
| `tests/` | Smoke + config + logging + readiness tests |
| `.env.example` | Environment-variable template (copy to `apps/api/.env` when running uvicorn from `apps/api/`) |

The runnable ASGI app lives in `apps/api/app/main.py`, which imports `create_app` from this package.

## Verify

```bash
cd apps/api
pip install -e ../../packages/platform
pytest ../../packages/platform/tests -q
uvicorn app.main:app --reload
```
