# Changelog

All notable changes to AI Travel Planner. Versions follow [Semantic Versioning](https://semver.org/).

## Unreleased — 0.12.0-proposed (v2 concierge expansion plan)

Documentation-only release. No runtime code changed. Captures the v2 product plan, GTM strategy, student-budget stack, launch plan, and prep checklist before v2 implementation begins. Awaiting user approval per the "Approval gate" section in `docs/conciergeProductPlan.md`.

Product plan added

- New file `docs/conciergeProductPlan.md` (PROPOSED) — owner: Principal Product Manager. Covers:
  - Product principle: research-and-planning platform under one roof; user always implements externally; suggestion-only stance encoded as `source: "suggestion"` flag + `partner_options[]` + disclaimer on every transactable option
  - Partner ecosystem (configurable, region-aware): Skyscanner / Google Flights / Kayak / direct airline for flights; Booking.com / Agoda / Hotels.com / Expedia / Hostelworld / Airbnb for stays; 12Go / Trainline / IRCTC / JR-Pass / Amtrak / Redbus / FlixBus for ground transport; GetYourGuide / Viator / Klook for tickets; embassy / government portals for visa
  - Phase plan V2.A through V2.H with Goal / Tasks / Exit-criteria
  - Future direction (post-v2): in-app booking with explicit prerequisites (travel-agency licensing, PCI-DSS, KYC, customer support)

GTM and launch plan added

- Auth-gated signup as the email-capture mechanism (replaces a separate "waitlist" page)
- Two-checkbox consent UX, region-aware defaults (EU + UK + India unchecked; US + others checked + visible) — GDPR / DPDP / CAN-SPAM compliant
- Drip cadence: one marketing email per feature drop, max one per 3 weeks, one-click List-Unsubscribe header, suppression list enforced at DB layer
- MVP launch line defined: V2.A + V2.E + auth + privacy/ToS + DMARC

Student-budget stack ($0/month) documented

- Vercel + Render + Supabase + Resend + Cloudflare + Gemini 1.5 Flash + OpenFreeMap/Nominatim + OpenWeatherMap + PostHog + Sentry + UptimeRobot — total monthly cost $0
- GitHub Student Developer Pack perks mapped (free `.me` domain, Cloudflare Pro, Sentry, DigitalOcean credit, JetBrains)
- LLM cost containment rules (default Gemini Flash, per-user rate limit, daily hard-cap with alert email)

Launch plan and timeline added

- Launch ladder: private alpha (week 5–6) → soft launch (week 7–8) → public launch (week 10–12)
- Week-by-week timeline (10–15 hrs/week of student-effort)
- Anti-patterns to avoid (no "coming soon" page, no waiting for V2.B/C, no skipping privacy/ToS/DMARC, no skipping private alpha)

3-day Student Pack prep window documented

- Day 1: accounts (Supabase, Vercel, Render, Resend, Cloudflare, PostHog, UptimeRobot) + initial deployment
- Day 2: Supabase Auth + Privacy Policy + ToS draft via Termly + email infra schema
- Day 3: V2.A + V2.E coding checklists finalized
- Day 4 (Pack unlocks): claim free `.me` + DNS + SPF/DKIM/DMARC + Cloudflare Pro + Sentry, then start coding V2.A

Existing docs updated to be forward-consistent with the v2 plan

- `docs/architecture.md` — top status block now mentions v2 status; new section "17. v2 concierge expansion (planned, not yet built)" summarises architectural impact and points at the product plan
- `docs/implementationPlan.md` — top status block split into v1 (delivered) and v2 (planned); new section "Roadmap — v2 concierge expansion (planned)" lists V2.A through V2.H in the same Goal / Tasks / Exit-criteria style as v1
- `docs/projectFileMap.md` — top status block split into v1 / v2; new section "9. v2 expansion preview" lists the new contracts, tools, agents, endpoints, frontend views, persistence schema, and free-tier infra
- `docs/problemStatement.md` — added a forward-pointer noting that the v2 scope is described in `docs/conciergeProductPlan.md`

No code changed

- v1 still ships 94 passing tests across `apps/api/` + every `packages/*/tests/`
- v2 implementation does not begin until the product plan is explicitly approved

## 0.11.1 — End-phase documentation refresh

Documentation pass after the layout migration; no runtime code changes.

- `docs/architecture.md`: rewrote with as-built schema names (`TripBrief`, `Recommendations`, `LogisticsPlan`, `BudgetReport`, `Itinerary`, `RevisionRequest`); replaced the design-time `TravelConstraints` / `ActivityCatalog` / `LodgingPlan` / `MovementPlan` / `BudgetBreakdown` / `DraftItinerary` / `ReviewReport` placeholders.
- `docs/architecture.md`: added an "Implementation status" header and an "As implemented" footer to every numbered section, pointing at the exact `packages/<...>/` or `apps/api/<...>` file that owns it.
- `docs/architecture.md`: added a Synthesis section (8) and split the repair loop into 9.1 to match the worker layout under `packages/agents/`; added a Reliability envelope subsection (11.1) describing `HardenedPlannerService`.
- `docs/architecture.md`: refreshed the agent-flow, data-flow, and tool/memory-wiring Mermaid diagrams to use the as-built schema names and tool names (`hotel_search`, `intercity_transit_search`, `currency_conversion`).
- `docs/architecture.md`: rewrote the edge-case section to point at the concrete test files that prove each guarantee.
- `docs/implementationPlan.md`: reframed as a delivery log; added a project-status block, a phase-by-phase delivery summary table, and a "Delivered as" footer for every phase. Added a "Real-API rollout checklist" replacing the "Before switching to real APIs" stub.
- `docs/projectFileMap.md`: added a project-status block, a "Verify everything locally" section with copy-pasteable commands, and an "End-to-end mental model" section that walks a request through the codebase.
- `docs/CHANGELOG.md`: this entry; tightened the `0.11.0` formatting with sub-headings per migration pass.

## 0.11.0 — Domain-driven monorepo migration

Reorganised the repo into a domain-driven monorepo (`apps/api/`, `apps/web/`, `packages/*`); the `phases/` folder is gone. Delivered in four passes.

Layout changes

- Pass 1 — Apps and platform: `backend/` → `apps/api/`, `frontend/` → `apps/web/`, `phases/phase0` → `packages/platform/` (Python module renamed to `app_platform` to avoid shadowing the stdlib `platform` module).
- Pass 2 — Contracts, orchestrator, tools: extracted `packages/domain_contracts/`, `packages/orchestrator/` (with the `Agent` base contract), and `packages/tools/` from Phase 1 / Phase 2.
- Pass 3 — Worker agents: collapsed Phases 3–7 into one package per capability under `packages/agents/{destination, logistics, budget, synthesis, validator, repair}/` using a PEP-420 namespace package; split the combined Phase 5 test file into `test_budget_agent.py` and `test_synthesis_agent.py`.
- Pass 4 — Memory and reliability: extracted `packages/memory/` (run-state store, TTL/LRU planner-result cache, user-preference profile, `MemoryAwarePlanner`) and `packages/reliability/` (`ModelTierPolicy`, `with_retry`, `CircuitBreaker`, `HardenedPlannerService`); rewired `apps/api/app/api/trip_planning.py` accordingly.

Build, CI, and tooling

- Updated editable installs in `apps/api/requirements.txt`, pytest paths in `apps/api/pyproject.toml`, ruff scope in `apps/api/Makefile` + `apps/api/tasks.py`, pre-commit hook globs, and the GitHub Actions workflow to follow the new layout.
- Reworked `apps/api/scripts/mypy_backend.py` to recursively walk `packages/` and correctly emit dotted module names for PEP-420 namespace packages such as `agents.destination`.
- Added `packages/README.md` (layer map + dependency-direction diagram) and `packages/agents/README.md` (capability index + onboarding guide).

Cleanup

- Removed the now-empty `phases/` tree and its build/dist artefacts from `.gitignore`.
- Removed the legacy `frontend/` directory after terminating an orphaned `next dev` process that was holding a lock on `next-swc.win32-x64-msvc.node`.

Test sweep

- 82 tests passing (was 81 before the Phase 5 worker test split).

## 0.10.1 — Edge-case hardening

System-side hardening implemented across phases.

- Phase 2: typed tool failure classes, strict real-mode behavior, real-timeout enforcement, expanded reliability/contract test coverage.
- Phase 4: city/night allocation guarantees so `sum(stay_plan.nights) == duration_days` in constrained scenarios.
- Phase 5: budget sanity flags for all-zero outputs, dominant-category outliers, and unrealistic daily spend.
- Phase 7: repair-loop non-convergence detection for repeated revision signatures.
- Phase 9: planner-result cache TTL and bounded eviction policy with dedicated tests.
- Phase 10: latency budget guard and planner result-shape validation.
- Phase 0 / Phase 1: readiness checks expanded and `start_date` past-date validation added.

## 0.10.0 — Phase 10 hardening primitives

- Added Phase 10 hardening primitives: `with_retry`, `CircuitBreaker`, `ModelTierPolicy`.
- Hardened the trip-planning API route with graceful failure handling.
- Added Phase 10 test coverage and integrated it into the backend test matrix.
