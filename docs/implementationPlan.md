AI Travel Planner — Implementation Plan and Delivery Log

Phase-wise build narrative for v1 (delivered) and the v2 concierge expansion (planned).
References: docs/problemStatement.md, docs/architecture.md, docs/projectFileMap.md, docs/conciergeProductPlan.md

Project status

v1 (Phases 0–10) — delivered

- Status:                 End-phase. Phases 0–10 are all delivered.
- Test sweep:             94 tests passing across `apps/api/` + every `packages/*/tests/`
- Lint / format:          ruff clean across `apps/api/` and `packages/`
- Mock mode:              `MOCK_MODE=true` smoke-tested end-to-end (frontend + backend)
- Pre-flight remaining:   one-tool-at-a-time real-API rollout (see "Real-API rollout checklist" further down)

v2 (Phases V2.A–V2.H) — planned

- Status:                 PROPOSED. Awaiting approval per docs/conciergeProductPlan.md.
- Scope:                  origin awareness, real flights / hotels / visa / seasonality / maps, PDF export, email delivery, live trip mode, multi-traveler personalization
- MVP launch line:        V2.A + V2.E + auth + privacy/ToS + DMARC (everything else ships as post-launch feature drops)
- Cost target:            $0/month operating cost on free tiers (Vercel, Render, Supabase, Resend, Cloudflare, Gemini Flash) + ~$10/year domain (or free `.me` via GitHub Student Pack)
- Full detail:            docs/conciergeProductPlan.md (vision, gap analysis, partner ecosystem, GTM, launch plan, 3-day prep)

Note on layout

- The 0–10 phase numbering is the build narrative used during development.
- After delivery the code was reorganised into a domain-driven monorepo (`apps/api/`, `apps/web/`, `packages/*`).
- Each phase below ends with a "Delivered as" line pointing at its home in the new layout.


Delivery summary table

| Phase | Goal | Delivered as | Key tests |
| --- | --- | --- | --- |
| 0 | Project foundation + CI + health | `packages/platform/` (Python module: `app_platform`) | `packages/platform/tests/test_{config,logging,smoke}.py` |
| 1 | Domain contracts + orchestrator skeleton | `packages/domain_contracts/`, `packages/orchestrator/` | `packages/orchestrator/tests/test_{parser,graph}.py`, `…/test_trip_brief.py` |
| 2 | Typed tool layer with retries + cache | `packages/tools/` | `packages/tools/tests/test_{registry,reliability,tool_contracts}.py` |
| 3 | Destination research agent | `packages/agents/destination/` | `packages/agents/destination/tests/test_destination_agent.py` |
| 4 | Logistics agent | `packages/agents/logistics/` | `packages/agents/logistics/tests/test_logistics_agent.py` |
| 5 | Budget agent + itinerary synthesis | `packages/agents/budget/`, `packages/agents/synthesis/` | `…/budget/tests/test_budget_agent.py`, `…/synthesis/tests/test_synthesis_agent.py` |
| 6 | Validator agent (programmatic + LLM) | `packages/agents/validator/` | `packages/agents/validator/tests/test_validator_agent.py` |
| 7 | Bounded repair loop | `packages/agents/repair/` | `packages/agents/repair/tests/test_repair_agent.py` |
| 8 | Trip-planning HTTP API + Next.js UI | `apps/api/app/api/trip_planning.py`, `apps/web/` | `apps/api/tests/test_wiring.py` |
| 9 | Memory + personalization | `packages/memory/` | `packages/memory/tests/test_memory_store.py` |
| 10 | Production hardening + reliability envelope | `packages/reliability/` | `packages/reliability/tests/test_hardening.py` |


Phase 0 — Foundations and project shell

Stand up a reproducible Python project with config, logging, correlation IDs, and CI.

Tasks

- Repo skeleton: domain-driven monorepo with `apps/api/`, `apps/web/`, and `packages/*`
- Tooling: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, root `Makefile`, `apps/api/tasks.py`, pre-commit, GitHub Actions CI
- App shell: FastAPI `create_app()` with `/healthz` and `/readyz`
- Config: Pydantic Settings loaded from `.env`
- Logging: `structlog` JSON output
- Middleware: correlation-ID middleware (`X-Correlation-ID`)

Exit criteria

- `make api-install-dev` and `make api-test` work on a clean checkout
- `/healthz` and `/readyz` return 200 with a correlation ID echoed in headers
- Lint, type-check, and tests run green in CI

Delivered as

- `packages/platform/` (module `app_platform`; the on-disk folder name `platform` is intentional, the module is renamed to avoid shadowing the Python `platform` stdlib module).
- API integration shell: `apps/api/app/main.py` mounts the platform's `create_app()` factory and adds the trip-planning router.


Phase 1 — Data contracts and orchestrator skeleton

Lock down typed contracts and a runnable orchestrator stub before any specialist agent is real.

Tasks

- Schemas: Pydantic models for `TripBrief`, `Recommendations`, `LogisticsPlan`, `BudgetReport`, `Itinerary`, `RevisionRequest`
- Parser: `parse_trip_request(text) -> TripBrief` with regex baseline and LLM hook
- Graph: `build_graph()` `StateGraph` with stub nodes (research, logistics, budget, synthesise, validate, repair)
- Fallback: deterministic linear runner used when `langgraph` is not installed
- `Agent` abstract base contract for every worker
- Tests: parser unit tests + end-to-end stub graph run

Exit criteria

- Canonical Japan request parses into a valid `TripBrief`
- Stub graph runs end-to-end with deterministic outputs
- All schemas validate; no untyped dicts cross node boundaries

Delivered as

- Contracts: `packages/domain_contracts/`
- Orchestrator (parser + graph + Agent base): `packages/orchestrator/`
- The two were extracted as separate packages in Pass 2 of the layout migration so the domain contracts can be reused by every agent without depending on the orchestrator.


Phase 2 — Tool layer (typed wrappers + mocks)

Deterministic, retry-safe tool wrappers used by all specialist agents.

Tasks

- Registry: `ToolRegistry` with typed inputs and outputs and a uniform call signature
- Tools: `web_search`, `vector_search`, `maps_distance`, `hotel_search`, `intercity_transit_search`, `currency_conversion`, `price_estimate`
- Modes: real adapter and mock adapter selectable via `MOCK_MODE`
- Reliability: retries, real-timeout enforcement, cache key strategy with schema-version embedded
- Typed error taxonomy: `ToolTimeoutError`, `ToolUpstreamError`, `ToolSchemaError`, …

Exit criteria

- Every tool has typed I/O and a mock implementation
- Tests cover happy path, retry, cache hit, and the strict-real-mode guard
- Specialist agents in later phases consume only the registry

Delivered as

- `packages/tools/`
- Public surface: `BaseTool`, `ToolRegistry`, plus one module per tool listed above.


Phase 3 — Destination research agent

City-level recommendation catalog.

Tasks

- Sub-query generation: preferences and avoidances → search queries
- Retrieval: `web_search` and `vector_search`; merge and de-duplicate
- Tagging: priority (`must_do` or `nice_to_have`) and `crowd_level` per item
- Output: `Recommendations` grouped per city

Exit criteria

- Canonical run returns neighborhoods, experiences, and food per requested city
- Avoidances are reflected in `crowd_level` and item selection
- Output passes `Recommendations` schema validation

Delivered as

- `packages/agents/destination/` — public surface: `DestinationResearchAgent`, `build_destination_agent`


Phase 4 — Logistics agent

Realistic day-by-day movement and stay plan.

Tasks

- Stay allocation: nights per city based on `duration_days` and `cities`
- Inter-city movement: mode and duration via `maps_distance` and `intercity_transit_search`
- Day sequencing: order activities to reduce backtracking
- Output: `LogisticsPlan` with `stay_plan`, `intercity`, `day_skeleton`

Exit criteria

- `day_skeleton` length equals `TripBrief.duration_days`
- `sum(stay_plan.nights) == duration_days` (guaranteed in constrained scenarios)
- Stay plan covers all requested cities
- Movement legs respect `max_intercity_transfers`

Delivered as

- `packages/agents/logistics/` — public surface: `LogisticsPlanningAgent`, `build_logistics_agent`


Phase 5 — Budget agent and itinerary synthesis

Estimate cost, then merge worker outputs into a coherent day-by-day plan.

Tasks

- Budget agent
  - Categorize spend across stay, transport, food, activities, buffer
  - Estimate cost: combine baselines, FX, and tool data into category totals
  - Compare to budget: set `within_budget` and emit `BudgetFlag` items when over
  - Sanity flags: zero-cost outputs, dominant-category outliers, unrealistic daily spend
- Synthesis agent
  - Receive `Recommendations`, `LogisticsPlan`, `BudgetReport` for the same `TripBrief`
  - Resolve "what vs when vs cost" conflicts and link day slots to recommendation IDs
  - Embed budget summary; surface caveats and assumptions
  - Output: `Itinerary` ready for the validator

Exit criteria

- End-to-end run produces a coherent `Itinerary`
- `Itinerary.day_by_day` length equals `TripBrief.duration_days`
- Total category spend reconciles with `BudgetReport.total_estimate_usd`

Delivered as

- Budget:    `packages/agents/budget/`     — `BudgetPlanningAgent`, `build_budget_agent`
- Synthesis: `packages/agents/synthesis/`  — `ItinerarySynthesisAgent`, `build_synthesis_agent`
- During Pass 3 of the layout migration the original combined test file was split into per-package tests so each capability can be exercised in isolation.


Phase 6 — Validator agent (programmatic + LLM)

Quality gate before user delivery.

Tasks

- Layer 1 — Programmatic: `duration_days` matches day count
- Layer 1 — Programmatic: all required cities appear
- Layer 1 — Programmatic: total estimated spend ≤ `TripBrief.budget_usd` (using `BudgetReport` numbers)
- Layer 2 — LLM rubric: preference alignment, crowd-avoidance effort, narrative coherence, logistics realism
- Layer 2 — LLM output: `RevisionRequest` with blocking vs advisory severity
- If Layer 1 fails, return structured errors; optionally skip or shorten Layer 2

Exit criteria

- Known-bad drafts (wrong city, over budget, wrong day count) fail programmatic checks
- Good demo draft passes with a documented checklist on the `RevisionRequest`

Delivered as

- `packages/agents/validator/` — public surface: `ItineraryValidatorAgent`, `build_validator_agent`


Phase 7 — Repair loop and final user-facing plan

Convert validator feedback into targeted fixes and finalize the user-facing itinerary.

Tasks

- Repair routing: map `RevisionRequest` items to specific workers (destination / logistics / budget / synthesis)
- Bounded retries: cap repair loop iterations; record reasons per attempt
- Non-convergence detection: stop early if the same revision signature repeats
- Finalization: `Itinerary` with summary, day-by-day blocks, and budget rollup

Exit criteria

- A failing draft is fixed within `max_retries` or returns a structured error
- Final `Itinerary` passes the validator and matches `TripBrief`
- No infinite loops under any input

Delivered as

- `packages/agents/repair/` — public surface: `RepairLoopAgent`, `build_repair_loop_agent`


Phase 8 — Trip-planning API and Next.js UI

Expose the orchestrator over HTTP and wrap it in a usable UI.

Tasks

- API: `POST /api/v1/trips/plan` returning `{approved, itinerary, review, run_id, cache_hit, selected_model}`
- API: graceful failure handling (`503` with typed error envelope on hardening trips)
- UI: Next.js 14 + Tailwind under `apps/web/`
- UI pages: request form, run progress, itinerary viewer
- UI states: loading, partial results, validation failure, final success
- Wiring: UI calls API via `NEXT_PUBLIC_API_BASE_URL`; correlation-ID surfaced for support

Exit criteria

- A user can submit the canonical Japan request and see the final `Itinerary`
- All UI states are reachable from real API responses
- API integration test (`apps/api/tests/test_wiring.py`) covers the happy path and a mock-mode degraded response

Delivered as

- API route:           `apps/api/app/api/trip_planning.py` (composes `MemoryAwarePlanner` and `HardenedPlannerService`)
- UI:                  `apps/web/` (Next.js + Tailwind, type-aligned to the API payload via `apps/web/src/types/planner.ts`)


Phase 9 — Memory and personalization

Add long-term memory and a planner-result cache around the orchestrator.

Tasks

- Run-state store: typed short-term state shared across graph nodes (`InMemoryRunStateStore`)
- Planner-result cache: TTL + LRU eviction keyed on a hash of the `TripBrief` (`InMemoryPlannerResultCache`)
- Long-term store: opt-in user preferences and trip history (`InMemoryUserPreferenceStore`, `UserPreferenceProfile`)
- Prompt augmentation: `apply_profile_to_prompt(profile, base_prompt)`
- Composition: `MemoryAwarePlanner` wraps the orchestrator runner with all of the above

Exit criteria

- Repeat runs for the same user produce more personalized catalogs
- Cache hits measurably reduce orchestrator invocations in tests
- TTL + capacity eviction are unit-tested

Delivered as

- `packages/memory/`
- The in-memory implementations satisfy the same interfaces a future Postgres / Redis / Chroma implementation would, so swapping is a one-line constructor change.


Phase 10 — Hardening, observability, and release

Make the system production-ready and traceable.

Tasks

- Reliability primitives: `ModelTierPolicy`, `with_retry`, `CircuitBreaker`
- Composed envelope: `HardenedPlannerService` adds latency budget enforcement and result-shape validation against `domain_contracts`
- Observability: structured logs at every node, per-run trace IDs (correlation ID), optional LangSmith / Langfuse hooks
- Cost control: model tiering, prompt caching, bounded repair loops
- Release: versioning (`docs/CHANGELOG.md`), smoke checks (`apps/api/scripts/release_smoke.py`)

Exit criteria

- A single run can be fully traced from request to `Itinerary`
- Failures degrade gracefully with structured errors
- Latency budget breaches surface as a typed error and are recorded
- Release pipeline ships a versioned build with passing smoke tests

Delivered as

- `packages/reliability/` (`HardenedPlannerService`, `CircuitBreaker`, `ModelTierPolicy`, `with_retry`)
- Wired in at `apps/api/app/api/trip_planning.py`:

  ```python
  planner = MemoryAwarePlanner(runner=run_orchestrator)
  hardening = HardenedPlannerService(planner_callable=planner.run, retry_attempts=2)
  ```


Edge-case coverage delivered

Edge cases were treated as first-class acceptance criteria, not post-hoc bug fixes.

Input and contract integrity

- Missing fields, malformed values, contradictory constraints handled in `domain_contracts` + `orchestrator/parser.py`
- Past `start_date` rejected at the schema layer
- Tests: `packages/orchestrator/tests/test_parser.py`, `packages/domain_contracts/tests/test_trip_brief.py`

Retrieval and recommendation robustness

- Sparse / noisy / duplicate search results handled in `tools/` (retries + de-dup) and `agents/destination/` (low-confidence fallback)
- Tests: `packages/tools/tests/test_reliability.py`, `packages/agents/destination/tests/test_destination_agent.py`

Logistics feasibility under constraints

- Impossible transfers and over-packed days handled by reallocation + buffer insertion
- `sum(stay_plan.nights) == duration_days` invariant guaranteed in constrained scenarios
- Tests: `packages/agents/logistics/tests/test_logistics_agent.py`

Budget uncertainty and drift

- Mixed-confidence prices, FX snapshot per run, sanity flags for zero-cost / outlier-share / unrealistic spend
- Tests: `packages/agents/budget/tests/test_budget_agent.py`

Validation and repair-loop failure modes

- Programmatic checks remain blocking even if LLM rubric is favorable
- Repeated repair failures terminate safely with non-convergence detection
- Tests: `packages/agents/validator/tests/test_validator_agent.py`, `packages/agents/repair/tests/test_repair_agent.py`

Memory, cache, and concurrency

- Versioned cache keys, TTL, capacity eviction, opt-in personalization
- Run isolation by correlation ID
- Tests: `packages/memory/tests/test_memory_store.py`

Operational hardening and release gates

- Tool outages handled by retry + circuit breaker; latency budget guard catches slow runs
- Result-shape validation blocks malformed planner outputs
- Tests: `packages/reliability/tests/test_hardening.py`, `packages/platform/tests/test_smoke.py`

Definition of done for edge cases

- Every phase ships at least one explicit failure-path acceptance test
- docs/architecture.md edge-case contracts and this plan are kept synchronized
- No phase is marked complete if only happy-path tests pass


Tiered evaluation coverage delivered

The project now includes a dedicated eval layer for pre-production confidence.

Tier 1 (must-have before real APIs)

- Constraint fidelity eval: validates city coverage, day count, budget compliance
- Consistency/determinism eval: repeats identical prompts and checks variance bounds
- Prompt perturbation eval: rephrased/typo variants still satisfy core constraints
- Repair-loop safety eval: verifies bounded completion and non-hanging behavior

Tier 2 (high-value)

- Tool failure/degradation eval: simulated outage returns typed `503` error envelope
- Multi-turn update eval: second-turn revised constraints update resulting plan
- Schema strictness eval: response keys remain stable (`approved`, `itinerary`, `review`, `run_id`, `cache_hit`, `selected_model`)

Tier 3 (hardening)

- Adversarial prompt eval: prompt-injection style text does not expose secrets/system internals
- Semantic stability eval: similar prompts produce similar itinerary signal
- A/B minimal-change eval: one-word phrasing shifts do not cause disproportionate drift

Implemented as

- `apps/api/tests/test_eval_tiers.py` (12 tests total)
- Included in regular regression command (`pytest -q` from `apps/api/`)


Real-API rollout checklist

The system runs end-to-end in `MOCK_MODE=true` today. To switch to real APIs:

- Run the full regression suite (includes tiered evals): `cd apps/api && pytest -q`
- Provision real API keys in `apps/api/.env` (use `apps/api/.env.example` as template)
- Flip `MOCK_MODE=false` in `apps/api/.env`
- Enable one real tool at a time and compare its outputs against mock-contract expectations
- Watch the circuit-breaker dashboards (logs filtered by `event="circuit_open"`) during the first hours of traffic
- Keep a `MOCK_MODE=true` fallback path available for offline development and CI


Roadmap — v2 concierge expansion (planned)

The phases below are PROPOSED and not yet built. Full vision, gap analysis, GTM strategy, partner ecosystem, student-budget stack, launch plan, and 3-day prep checklist live in docs/conciergeProductPlan.md. Architecture impact is summarized in docs/architecture.md "17. v2 concierge expansion (planned, not yet built)". This section lists the phases in the same Goal / Tasks / Exit-criteria style used by Phases 0–10 above.

v2 phase summary table

| Phase | Goal | Will land in |
| --- | --- | --- |
| V2.A | Origin awareness, traveler profile, trip dates | `packages/domain_contracts/`, `packages/orchestrator/`, `apps/api/`, `apps/web/` |
| V2.B | Real-world tool integrations | `packages/tools/` (`flight_search`, `visa_requirements`, `seasonality_calendar`, `attraction_fees`, `local_transport_guide`, `intercity_transport`, `geocoding`, `directions`) |
| V2.C | New / extended worker agents | `packages/agents/pre_trip/`, `packages/agents/timing/`, extensions to `agents/{destination, logistics, budget}/` |
| V2.D | Maps feature (frontend + backend wiring) | `apps/web/src/components/MapPanel/`, geocoding/directions tool calls |
| V2.E | PDF export and email delivery | `apps/api/app/api/`, `apps/api/app/templates/itinerary_pdf.html`, Resend integration |
| V2.F | Personalization, multi-traveler, saved trips | Supabase Auth + Postgres, `users` / saved-trips tables, `apps/web` dashboard |
| V2.G | Live trip mode (in-trip companion) | New `packages/agents/live_trip/`, notification provider integration |
| V2.H | Hardening, evals, observability for v2 | New evals in `apps/api/tests/test_eval_tiers.py`, cost dashboards, compliance disclaimers |

Phase V2.A — Origin awareness, traveler profile, trip dates

Goal

Make every plan aware of where the user is travelling from, when, and with whom.

Tasks

- Extend `TripBrief` schema in `packages/domain_contracts/` with `origin_city`, `origin_country`, `travel_dates` (start_date, end_date), `travelers[]` (count, dietary, accessibility), `travel_style`, `pace`
- Update `parse_trip_request` in `packages/orchestrator/src/orchestrator/parser.py` to recognize "I live in X", "from X to Y", explicit dates, and traveler hints
- Update orchestrator graph state to carry origin and traveler profile through every node
- Update API request schema in `apps/api/app/api/trip_planning.py` (backward-compatible: existing `prompt`-only clients keep working)
- Add Tier-1 eval cases for origin / dates / traveler profile fidelity in `apps/api/tests/test_eval_tiers.py`
- Frontend: optional "About your trip" pre-form in `apps/web` that pre-fills these fields

Exit criteria

- A request mentioning home + dates parses correctly into typed fields
- All existing tests + new origin-awareness tests pass
- Existing API contract still works for clients that send only `prompt`

Phase V2.B — Real-world tool integrations

Goal

Add the new tools the concierge needs, all wrapped in the existing `BaseTool` runtime (typed I/O, retries, real-timeout, cache, mock-first). Every tool is read-only — no booking, payment, or stateful writes.

Tasks

- New tools under `packages/tools/src/tools/`:
  - `flight_search` — Amadeus / Kiwi / SerpAPI Google Flights (mock-first); returns options + indicative price + `partner_options[]` (Skyscanner, Google Flights, Kayak, direct airline site)
  - `visa_requirements` — Sherpa or curated KB + LLM verification; informational, mandatory disclaimer; `partner_options` are official embassy / government portals only
  - `seasonality_calendar` — climate + crowd + festivals; combines `web_search` + curated KB
  - `attraction_fees` — or extend `price_estimate` with a `category=entry_fee` channel; `partner_options` may include GetYourGuide / Viator / Klook for ticketed attractions
  - `local_transport_guide` — per-city typical modes + indicative cost; informational only
  - `hotel_search` enrichment — view, amenities, rating fields added; `partner_options` include Booking.com, Agoda, Hotels.com, Expedia (Hostelworld for budget; Airbnb / VRBO for stays-with-kitchen)
  - `intercity_transport` — region-aware partner mapping (12Go, Trainline, IRCTC, JR-Pass, Amtrak, Redbus, FlixBus)
  - `geocoding` and `directions` — provider TBD (Mapbox / Nominatim free for low-volume launch)
- Tool-contract tests for every new tool (schema, retries, mock vs real)
- Per-tool TTL + cache key strategy (especially flight_search, which is expensive per call)
- Update `ToolRegistry` and `apps/api/requirements.txt`

Exit criteria

- All new tools have typed schemas, mock implementations, and contract tests
- Real-mode adapters return data within the latency budget for at least one provider per tool
- No tool change breaks the existing 94-test regression

Phase V2.C — New / extended worker agents

Goal

Translate the new tool data into typed plan output usable by the synthesis agent.

Tasks

- New agent `packages/agents/pre_trip/` — produces `PreTripBriefing` (visa, vaccinations, sim, packing, embassy, advisories)
- New agent `packages/agents/timing/` — produces `TimingReport` (best-month, crowd_level per month, festivals during travel window)
- Extend `agents/destination/` to incorporate `TimingReport`
- Extend `agents/logistics/` to add `from_home` flight leg via `flight_search`, attach `local_transport_guide` per city, attach geocoding to every city / POI
- Extend `agents/budget/` with explicit line items for flights, entry fees, local transport, optional insurance
- New domain contracts: `PreTripBriefing`, `TimingReport`, `FlightLeg`, `LocalTransportTip`, `EntryFee`; extend `Itinerary` with `geo` markers and `partner_options[]` per option

Exit criteria

- Synthesis produces an `Itinerary` that includes pre-trip, timing, flights, local transport, entry fees, and geo
- Validator updated with rules for flight + entry-fee feasibility
- Repair loop covers new failure modes (visa data missing, festival conflict)

Phase V2.D — Maps feature (frontend + backend wiring)

Goal

Make every recommendation visible on a real map.

Tasks

- Decide provider (recommendation: Mapbox free tier or OpenFreeMap for fully-free)
- Backend: ensure every itinerary entity has `lat/lng` (V2.C populates them)
- Frontend `apps/web`: new `MapPanel` component — V1 shows city markers + intercity polylines; V2 shows per-day route + POI markers with popovers (price, hours, fee)
- Provider key configured via `NEXT_PUBLIC_MAPS_*`
- Tests: tool-level geocoding/directions contract tests; frontend render test for `MapPanel` (markers count, polyline count)

Exit criteria

- Map renders for any successfully planned trip
- Map degrades gracefully if geocoding fails (text-only fallback)

Phase V2.E — PDF export and email delivery (the MVP-launch hook)

Goal

Let users walk away with a real artifact: a PDF of their travel suggestions, delivered by email. Explicitly labelled as suggestions, not a booking confirmation.

Tasks

- PDF service:
  - Library: `weasyprint` (HTML → PDF) or `reportlab`; HTML template at `apps/api/app/templates/itinerary_pdf.html`
  - Header banner: "Travel suggestions for <user>. Not a booking confirmation."
  - Footer: indicative-price disclaimer, visa-info informational disclaimer, affiliate disclosure if applicable
- Email delivery:
  - Provider: Resend (free tier 3 K/month) for both transactional and marketing
  - Tokenized download link as fallback
  - Rate limiting and abuse prevention
- New endpoints in `apps/api/app/api/`:
  - `POST /api/v1/trips/export/pdf` → returns PDF bytes
  - `POST /api/v1/trips/email`     → triggers email send via Resend
- Compliance: explicit user opt-in, GDPR-style data minimization, no marketing-by-default

Exit criteria

- A planned trip can be exported as PDF and emailed to the requested address
- Failure cases return typed `503` with structured error envelope (matches existing pattern)
- Rate limiting prevents abuse
- Header / footer disclaimers present in every PDF

Phase V2.F — Personalization, multi-traveler, saved trips

Goal

Let users come back, save trips, and have the system remember them.

Tasks

- Persistence: introduce real datastore (Supabase Postgres) for users, saved trips, preferences, consent log
- Auth: Supabase Auth (Google OAuth + email + magic-link); two-checkbox consent UI in `apps/web` signup screen (region-aware defaults)
- `users`, `email_log`, `unsubscribe_tokens`, `saved_trips` schema in Supabase
- Multi-traveler: cost split, per-traveler dietary / accessibility flags
- Compare two variants (budget vs comfort vs adventure)
- Trip dashboard in `apps/web`: upcoming, past, saved, duplicate, share

Exit criteria

- A logged-in user can save, retrieve, edit, and delete a trip
- Same user gets progressively personalized recommendations across sessions
- Suppression list enforced at DB layer; unsubscribed users filtered out of every campaign send

Phase V2.G — Live trip mode (in-trip companion)

Goal

Become useful during the trip, not just before. Still suggestion-only.

Tasks

- Per-day notification windows (push or email) with weather + (optional) flight status the user has pasted in
- Suggestion to re-shuffle remaining days on disruption, surfaced as a proposed change the user must accept
- Optional opt-in: "ping me if rain forecast above 60%"
- Explicit copy on every notification: "This is a suggestion. Your bookings are with the partner site."

Exit criteria

- A trip in progress receives at most one informational ping per day, opt-out always available
- Re-route suggestion arrives within 10 minutes of detected disruption and is presented as a proposal, never auto-applied

Phase V2.H — Hardening, evals, observability for v2

Goal

Make v2 release-grade with the same rigor as v1.

Tasks

- New evals (extend `apps/api/tests/test_eval_tiers.py`):
  - Origin-aware fidelity eval
  - Visa-correctness eval (curated test matrix per top 30 destinations)
  - Festival-accuracy eval
  - Entry-fee-presence eval
  - Map-payload geo-validity eval (every city has `lat/lng`)
  - PDF export eval (file generated within latency budget; header banner present)
  - Email-delivery eval (sandbox provider in CI)
  - Suggestion-stance eval: every flight / hotel / visa / insurance / intercity-transport / ticketed-attraction block carries `source: "suggestion"` + non-empty `partner_options[]` + disclaimer
  - Partner-routing eval: Vietnam trip surfaces Agoda + 12Go ahead of EU defaults; Europe trip surfaces Booking.com + Trainline; US trip surfaces Hotels.com / Expedia + Amtrak
- Cost-per-request observability dashboards (LLM tokens + each external API)
- Real-API rate limiting + circuit-breaker tuning
- Compliance: visa / advisory disclaimers in every itinerary payload and PDF
- Risk register sign-off

Exit criteria

- All new evals pass in CI
- Cost-per-request stays within target budget on a representative test set
- All disclaimers present in API and PDF


Where to go next

- Architecture deep dive:       docs/architecture.md
- File-by-file map:             docs/projectFileMap.md
- Release history:              docs/CHANGELOG.md
- v2 product plan + GTM:        docs/conciergeProductPlan.md
- Per-package quick-starts:     `packages/<name>/README.md`
- Capability index:             `packages/agents/README.md`
