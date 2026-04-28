AI Travel Planner — Project File Map (Interview Quick Reference)

Purpose

- One-stop index for "where does X live?" during interviews and code reviews.
- Layout is domain-driven: `apps/` for deployable services, `packages/*` for reusable
  capability layers. The phase-wise build narrative (Phases 0–10) lives in
  `docs/implementationPlan.md`; the running code is organised by domain.

Project status

v1 (delivered)

- All Phase 0–10 capabilities are delivered.
- 94 tests passing across `apps/api/` + every `packages/*/tests/`.
- Lint clean (`ruff check . ../../packages` from `apps/api/`).
- Mock-mode end-to-end works via `MOCK_MODE=true`; see docs/implementationPlan.md "Real-API rollout checklist".

v2 (planned, not yet in code)

- Concierge expansion proposed in docs/conciergeProductPlan.md (vision + GTM + student-budget stack + launch plan + 3-day prep).
- Phase narrative in docs/implementationPlan.md "Roadmap — v2 concierge expansion".
- Architecture impact in docs/architecture.md "17. v2 concierge expansion (planned, not yet built)".
- Section 9 below previews where the new packages, tools, and agents will land once they ship.


## 1. API service shell (FastAPI app)

Primary API entry and integration wiring

- `apps/api/app/main.py` — ASGI entrypoint, app creation, router mounting
- `apps/api/app/api/trip_planning.py` — `POST /api/v1/trips/plan` endpoint, composes `MemoryAwarePlanner` + `HardenedPlannerService`
- `apps/api/app/api/__init__.py` — API router exports

API integration tests and scripts

- `apps/api/tests/test_wiring.py` — verifies app routes, response shape, mock-mode degradation
- `apps/api/tests/conftest.py` — API test setup
- `apps/api/scripts/release_smoke.py` — release smoke checks (`/healthz`, `/readyz`)
- `apps/api/scripts/pytest_backend.py` — pytest helper used by pre-commit
- `apps/api/scripts/mypy_backend.py` — typing helper that walks every `packages/*` (handles PEP-420 namespace packages under `packages/agents/`)
- `apps/api/tasks.py` — local task runner helpers (Windows-friendly)
- `apps/api/Makefile` — Linux/macOS shortcuts (`api-install-dev`, `api-test`, `lint`, `format`)

Environment and configuration

- `apps/api/.env.example` — env template (LLM keys, `MOCK_MODE`, hardening knobs)
- `apps/api/requirements.txt` — pins runtime deps + 12 editable installs of `packages/*`
- `apps/api/requirements-dev.txt` — dev tooling (pytest, mypy, ruff, etc.)
- `apps/api/pyproject.toml` — ruff / mypy / pytest configuration shared with the editable packages

API runtime + endpoint usage (what is running)

- Base dev server: `uvicorn app.main:app --reload` (run from `apps/api/`)
- Health check endpoint: `GET /healthz` — liveness; returns service metadata (`status`, `service`, `version`, `env`)
- Readiness endpoint: `GET /readyz` — startup dependency checks (`config`, `orchestrator`, `tool_registry`), returns `503` if any check fails
- Trip planner endpoint: `POST /api/v1/trips/plan` — main planning flow (`MemoryAwarePlanner` + `HardenedPlannerService`)
- Request contract: `{ "prompt": string>=10 chars, "user_id": string, "opt_in_personalization": bool }`
- Response contract: `{ approved, itinerary, review, run_id, cache_hit, selected_model }`
- Failure contract: `503` with `{ error_type, message }` when hardening cannot produce a safe result

Quick endpoint checks

```bash
curl -s http://127.0.0.1:8000/healthz
curl -s http://127.0.0.1:8000/readyz
curl -s -X POST http://127.0.0.1:8000/api/v1/trips/plan \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Plan a 7 day Japan trip under 2500 USD\",\"user_id\":\"demo\",\"opt_in_personalization\":true}"
```


## 2. Web client (Next.js UI)

Main user-facing app files

- `apps/web/src/app/layout.tsx` — global layout shell
- `apps/web/src/app/page.tsx` — landing/page composition
- `apps/web/src/components/planner-page.tsx` — core planner UI (form, progress, itinerary viewer)
- `apps/web/src/app/globals.css` — global styles
- `apps/web/src/types/planner.ts` — frontend contracts type-aligned to the API payload

Web env / config touchpoints

- `apps/web/.env.local.example` — env template (`NEXT_PUBLIC_API_BASE_URL`)
- `apps/web/README.md` — run and usage notes


## 3. Reusable Python packages (capability layers)

Every `packages/<name>/` is a self-contained Python project with its own `pyproject.toml`, `src/`, `tests/`, and `README.md`. Top-level index lives at `packages/README.md`; the agent capability index lives at `packages/agents/README.md`.

Platform foundation (Phase 0) — `packages/platform/`

- `packages/platform/src/app_platform/application_factory.py` — FastAPI app factory
- `packages/platform/src/app_platform/application_settings.py` — typed settings
- `packages/platform/src/app_platform/structured_logging.py` — JSON logs
- `packages/platform/src/app_platform/request_correlation.py` — correlation-id middleware
- `packages/platform/src/app_platform/health_routes.py` — `/healthz`, `/readyz` (checks include orchestrator import + tool registry boot)

Domain contracts (Phase 1) — `packages/domain_contracts/`

- `packages/domain_contracts/src/domain_contracts/__init__.py` — public re-exports
- Pydantic models: `TripBrief`, `Recommendations`, `LogisticsPlan`, `BudgetReport`, `Itinerary`, `RevisionRequest`

Orchestrator (Phase 1) — `packages/orchestrator/`

- `packages/orchestrator/src/orchestrator/parser.py` — prompt → `TripBrief` parser
- `packages/orchestrator/src/orchestrator/graph.py` — LangGraph `StateGraph` + deterministic linear fallback runner
- `packages/orchestrator/src/orchestrator/agents/base.py` — `Agent` abstract base contract
- `packages/orchestrator/src/orchestrator/prompts/` — prompt namespace

Tool layer (Phase 2) — `packages/tools/`

- `packages/tools/src/tools/tool_runtime.py` — `BaseTool`, retries, real-timeout, cache, typed error taxonomy
- `packages/tools/src/tools/registry.py` — `ToolRegistry`
- `packages/tools/src/tools/web_search.py`
- `packages/tools/src/tools/vector_search.py`
- `packages/tools/src/tools/maps_distance.py`
- `packages/tools/src/tools/hotel_search.py`
- `packages/tools/src/tools/intercity_transit_search.py`
- `packages/tools/src/tools/currency_conversion.py`
- `packages/tools/src/tools/price_estimate.py`

Worker agents (Phases 3–7) — `packages/agents/<capability>/`

- `packages/agents/destination/src/agents/destination/agent.py` — destination research
- `packages/agents/logistics/src/agents/logistics/agent.py` — stay + transit planner
- `packages/agents/budget/src/agents/budget/agent.py` — per-category cost estimator
- `packages/agents/synthesis/src/agents/synthesis/agent.py` — day-by-day itinerary stitcher
- `packages/agents/validator/src/agents/validator/agent.py` — hard-rule validator + `RevisionRequest` emitter
- `packages/agents/repair/src/agents/repair/agent.py` — bounded revision loop dispatcher
- `agents/` is a PEP-420 namespace package; there is no top-level `agents/__init__.py`. Each capability is installed editably as its own distribution.

Memory and personalization (Phase 9) — `packages/memory/`

- `packages/memory/src/memory/store.py` — `InMemoryRunStateStore`, `InMemoryPlannerResultCache` (TTL/LRU), `InMemoryUserPreferenceStore`, `UserPreferenceProfile`, `MemoryAwarePlanner`, `apply_profile_to_prompt`

Reliability and hardening (Phase 10) — `packages/reliability/`

- `packages/reliability/src/reliability/hardening.py` — `ModelTierPolicy`, `with_retry`, `CircuitBreaker`, `HardenedPlannerService`


## 4. LangGraph, LangChain, and prompts mapping

LangGraph state graph

- `packages/orchestrator/src/orchestrator/graph.py` — `build_graph()`, node functions, fallback linear runner

Prompt and prompt-shaping files

- `packages/orchestrator/src/orchestrator/parser.py` — request-text → `TripBrief` prompt + regex fallback
- `packages/orchestrator/src/orchestrator/prompts/__init__.py` — prompt namespace
- `packages/memory/src/memory/store.py` — `apply_profile_to_prompt(profile, base_prompt)` for personalization

LangChain usage status

- Orchestration is centred on the LangGraph `StateGraph` plus typed tool adapters under `packages/tools/`.
- There is no large standalone `langchain` chains directory — agent flow logic lives in each `packages/agents/*/agent.py` file and is composed via the orchestrator graph.
- `langchain-core` is used only for model and tool abstractions; primary control flow is LangGraph.


## 5. Test map by responsibility

Foundation and app readiness

- `packages/platform/tests/test_config.py`
- `packages/platform/tests/test_logging.py`
- `packages/platform/tests/test_smoke.py`

Contracts and orchestration

- `packages/orchestrator/tests/test_parser.py`
- `packages/orchestrator/tests/test_graph.py`
- `packages/domain_contracts/tests/test_trip_brief.py`

Tool runtime and contracts

- `packages/tools/tests/test_registry.py`
- `packages/tools/tests/test_reliability.py` — typed errors, real-mode strict guard, timeout enforcement
- `packages/tools/tests/test_tool_contracts.py`

Worker agents

- `packages/agents/destination/tests/test_destination_agent.py`
- `packages/agents/logistics/tests/test_logistics_agent.py` — stay-plan invariant
- `packages/agents/budget/tests/test_budget_agent.py` — over-budget, sanity flags
- `packages/agents/synthesis/tests/test_synthesis_agent.py`
- `packages/agents/validator/tests/test_validator_agent.py`
- `packages/agents/repair/tests/test_repair_agent.py` — bounded retries, non-convergence

Memory and reliability

- `packages/memory/tests/test_memory_store.py` — TTL eviction, capacity eviction, profile prompt
- `packages/reliability/tests/test_hardening.py` — latency budget, invalid-result, circuit-breaker states

API integration

- `apps/api/tests/test_wiring.py`

Tiered evaluation suite (Tier 1/2/3)

- `apps/api/tests/test_eval_tiers.py` — 12 behavior-level eval tests spanning:
  - Tier 1: constraint fidelity, determinism, prompt perturbation, repair-loop safety
  - Tier 2: tool-failure degradation, multi-turn update behavior, schema strictness
  - Tier 3: adversarial prompt resilience, semantic stability, A/B minimal-change sensitivity


## 6. Interview speaking flow (fast navigation order)

Use this order when walking an interviewer through the project:

- Problem and scope:                    `docs/problemStatement.md`
- Architecture and data flow:           `docs/architecture.md` (start with sections 1, 2, 2.1, 2.2)
- Build narrative + delivery log:       `docs/implementationPlan.md`
- API entrypoint:                       `apps/api/app/main.py`, `apps/api/app/api/trip_planning.py`
- Schemas (single source of truth):     `packages/domain_contracts/src/domain_contracts/`
- Orchestrator + graph:                 `packages/orchestrator/src/orchestrator/graph.py`
- One worker agent (any):               `packages/agents/destination/src/agents/destination/agent.py`
- Tool layer reliability story:         `packages/tools/src/tools/tool_runtime.py`
- Memory and caching:                   `packages/memory/src/memory/store.py`
- Hardening envelope:                   `packages/reliability/src/reliability/hardening.py`
- Test evidence:                        per-package `tests/` folders + `apps/api/tests/test_wiring.py`
- Release history:                      `docs/CHANGELOG.md`
- v2 vision + GTM + launch plan:        `docs/conciergeProductPlan.md` (use this when asked "what is next?")


## 7. Verify everything locally

From the repo root, on Windows PowerShell or Linux/macOS shell:

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\Activate.ps1        # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r requirements.txt    # editable installs of every packages/*
pytest -q                          # 94 tests pass (includes tiered eval suite)
ruff check . ../../packages
```

Run only the parts you care about:

- One package:        `pytest ../../packages/agents/destination -q`
- One layer:          `pytest ../../packages/tools -q`
- API only:           `pytest tests/ -q`
- Mock-mode app:      `uvicorn app.main:app --reload` after setting `MOCK_MODE=true` in `apps/api/.env`


## 8. End-to-end mental model

When in doubt, follow the request through these files in order:

- HTTP arrives:                         `apps/api/app/api/trip_planning.py`
- Wrapped by reliability:               `packages/reliability/src/reliability/hardening.py` (`HardenedPlannerService`)
- Wrapped by memory:                    `packages/memory/src/memory/store.py` (`MemoryAwarePlanner`)
- Parses request:                       `packages/orchestrator/src/orchestrator/parser.py`
- Walks the graph:                      `packages/orchestrator/src/orchestrator/graph.py`
- Calls workers in parallel:            `packages/agents/{destination, logistics, budget}/`
- Stitches them:                        `packages/agents/synthesis/`
- Validates the result:                 `packages/agents/validator/`
- Loops on failure:                     `packages/agents/repair/`
- Each worker calls registered tools:   `packages/tools/`
- All payloads conform to:              `packages/domain_contracts/`


## 9. v2 expansion preview (planned, not yet in code)

Where the new packages, tools, and agents will land once the v2 phases ship. Nothing in this section exists in the codebase today — it is here so the file map is forward-consistent with docs/conciergeProductPlan.md and docs/implementationPlan.md "Roadmap — v2 concierge expansion".

New / extended domain contracts (`packages/domain_contracts/`)

- `TripBrief` extended with `origin_city`, `origin_country`, `travel_dates`, `travelers[]`, `travel_style`, `pace`
- New: `PreTripBriefing`, `TimingReport`, `FlightLeg`, `LocalTransportTip`, `EntryFee`
- `Itinerary` extended with `geo` markers per city / POI and `partner_options[]` per transactable option

New tools (`packages/tools/src/tools/`)

- `flight_search` — Amadeus / Kiwi / SerpAPI; `partner_options`: Skyscanner, Google Flights, Kayak, direct airline
- `visa_requirements` — Sherpa or curated KB; `partner_options`: official embassy / government portals only
- `seasonality_calendar` — climate + crowd + festivals
- `attraction_fees` — entry-fee channel; `partner_options`: GetYourGuide / Viator / Klook for ticketed attractions
- `local_transport_guide` — per-city typical modes + cost (informational only)
- `intercity_transport` — region-aware partner mapping (12Go, Trainline, IRCTC, JR-Pass, Amtrak, Redbus, FlixBus)
- `geocoding` and `directions` — Mapbox free / Nominatim for low-volume launch

New worker agents (`packages/agents/`)

- `pre_trip/` — produces `PreTripBriefing` (visa, vaccinations, sim, packing, embassy, advisories)
- `timing/` — produces `TimingReport` (best-month, crowd_level, festivals during window)
- Extensions to `destination/`, `logistics/`, `budget/`, `synthesis/`

New API endpoints (`apps/api/app/api/`)

- `POST /api/v1/trips/export/pdf`
- `POST /api/v1/trips/email`
- Auth-gated user routes wired to Supabase Auth (signup, sessions, manage preferences, suppression list)

New frontend views (`apps/web/`)

- "About your trip" pre-form (origin, dates, travelers)
- `MapPanel` component (markers + polylines + per-day route)
- Signup screen with two-checkbox consent (region-aware defaults)
- Manage-preferences page
- Trip dashboard (upcoming, past, saved, duplicate, share)

New persistence (Supabase Postgres, lands in V2.F)

- `users` (with `marketing_consent`, `marketing_consent_ts`, `marketing_consent_ip`, `unsubscribed_at`, `region`)
- `email_log` (campaign_id, template, sent_at, opened_at, clicked_at, bounced_at, complained_at)
- `unsubscribe_tokens`
- `saved_trips`

New evals (extending `apps/api/tests/test_eval_tiers.py` in V2.H)

- Origin-aware fidelity / visa-correctness / festival-accuracy / entry-fee-presence / map-payload geo-validity
- PDF export / email-delivery
- Suggestion-stance eval: every transactable block carries `source: "suggestion"` + non-empty `partner_options[]` + disclaimer
- Partner-routing eval: region-aware partner ranking (Vietnam → Agoda + 12Go, Europe → Booking.com + Trainline, US → Hotels.com / Expedia + Amtrak)

Free-tier infrastructure used at launch

- Frontend host: Vercel free
- Backend host: Render free
- DB + Auth: Supabase free
- Email: Resend free (3 K/month)
- DNS + SSL: Cloudflare free
- Domain: free `.me` via GitHub Student Pack (or `$10/year` `.com`)
- LLM: Gemini 1.5 Flash free tier
- Maps: Mapbox free / OpenFreeMap
- Analytics: PostHog Cloud free
- Error monitoring: Sentry developer plan (free via Student Pack)
