# AI Travel Planner — Master Document

Single source of truth for leadership, delivery, and next-version execution.

Last updated: 2026-04-28  
Project status: v1 delivered, v2 planned (awaiting explicit approval)


## 1) Executive summary

What this product is:

- A multi-agent travel research and planning platform.
- Users provide a prompt (destination, duration, budget, preferences, avoidances).
- The system returns a structured, day-by-day travel plan with budget and feasibility checks.

What this product is not (v1 and v2):

- Not a booking engine.
- Not a payment processor.
- Not a travel agent of record.

Core product stance:

- We generate suggestions.
- The final decision and booking are always made by the user on external partner sites.


## 2) Current state snapshot (as-built)

v1 delivery status:

- Phases 0–10 delivered.
- Domain-driven monorepo layout in place: `apps/` + `packages/`.
- 94 tests passing across API + packages.
- Mock-mode end-to-end already validated.
- Tiered eval suite (Tier 1/2/3) implemented as pre-production release gate.

Quality status:

- Lint/format clean.
- Reliability envelope integrated (`retry`, `circuit breaker`, latency budget checks, shape validation).
- Edge-case handling implemented and tested across orchestrator, tools, agents, memory, reliability.


## 3) What has been completed (v1 scope)

Goal:

- Build a robust multi-agent planner from prompt to validated itinerary.

Delivered components:

- Orchestrator pipeline with specialized workers.
- Typed domain contracts for every cross-agent payload.
- Tool runtime with reliability wrappers and typed contracts.
- Destination, logistics, budget, synthesis, validator, repair workers.
- API service and web app shell.
- Memory and personalization baseline.
- Hardening and operational reliability layer.
- Tiered evaluation framework.

Exit criteria met:

- Stable end-to-end planning flow in mock mode.
- Deterministic behavior for baseline cases.
- Bounded repair loop (no infinite retries).
- Typed failure envelopes for degraded scenarios.


## 4) Architecture at a glance

High-level flow:

1. User prompt enters API.
2. Request is parsed into `TripBrief`.
3. Orchestrator runs worker graph.
4. Workers call typed tools.
5. Synthesis builds itinerary.
6. Validator checks constraints/quality.
7. Repair loop runs if needed (bounded).
8. Hardened envelope returns safe result or typed failure.

Key technical layers:

- API: FastAPI (`apps/api/`)
- UI: Next.js (`apps/web/`)
- Contracts: `packages/domain_contracts/`
- Orchestrator: `packages/orchestrator/`
- Agents: `packages/agents/*`
- Tools: `packages/tools/`
- Memory: `packages/memory/`
- Reliability: `packages/reliability/`


## 5) Why v2 exists

v1 proves the architecture and quality model.  
v2 expands product usefulness from "itinerary generation" to a full "research concierge" experience:

- Origin-aware planning (from-home context)
- Visa and pre-trip guidance
- Seasonality, crowd, and festival awareness
- Better stay and transport detail
- Entry-fee-aware budgeting
- Map visualization
- PDF export and email delivery
- Gradual personalization and saved trips


## 6) v2 scope (planned)

Goal:

- Deliver a complete decision-support travel research package while preserving the suggestion-only principle.

Planned phases:

- V2.A: origin, dates, traveler profile
- V2.B: real-world tools (flights/visa/seasonality/fees/transport/geo)
- V2.C: new and extended workers (pre-trip, timing, logistics/budget extensions)
- V2.D: maps
- V2.E: PDF + email
- V2.F: auth-backed saved trips + personalization expansion
- V2.G: live trip companion
- V2.H: v2 hardening + eval expansion + observability

v2 MVP launch line:

- V2.A + V2.E + auth + privacy/ToS + sender-domain hygiene (SPF/DKIM/DMARC)


## 7) Recommended execution strategy: phase-wise vs one-go

Decision:

- Execute phase-wise, not one-go.

Reason:

- Lower risk.
- Faster user feedback loop.
- Better cost control for student budget.
- Easier rollback and debugging.
- Cleaner release communication.

Execution model:

- Ship one phase at a time.
- Each phase has Goal / Tasks / Exit criteria.
- Each phase must pass tests + eval gates before marking complete.
- Each phase should be releasable independently when possible.

When one-go is acceptable:

- Only for small, documentation-only edits or tiny low-risk internal refactors.
- Not for multi-provider integration or user-facing capability jumps.


## 8) Student-budget operating model

Constraint:

- Minimize spend to near zero until clear user traction.

Approach:

- Use free tiers first.
- Delay paid API integrations until demand proves value.
- Use deep-links to partner search pages before expensive direct integrations.
- Guard LLM spend with limits, caching, and fallback models.

Baseline stack:

- Frontend: Vercel free
- Backend: Render free
- Auth/DB: Supabase free
- Email: Resend free
- DNS/SSL: Cloudflare free
- LLM: Gemini Flash free tier (default)
- Maps/geo: OpenStreetMap ecosystem / free map tiers


## 9) Launch strategy

Goal:

- Launch fast enough to gather real signal, but not so early that trust breaks.

Recommended launch ladder:

- Stage 1: private alpha (friends/known users)
- Stage 2: soft launch (communities)
- Stage 3: public launch (broader channels)

Minimum launch readiness:

- Auth + consent flow working
- PDF/email flow working
- Mobile usable
- Error monitoring active
- Legal pages live
- Unsubscribe and suppression logic enforced


## 10) Edge cases and evals (must remain release gates)

Edge-case categories:

- Parser ambiguity and malformed inputs
- Tool outages and slow upstreams
- Budget and day-count inconsistencies
- Non-converging repair paths
- Cache correctness and eviction behavior
- Contract/schema drift
- Prompt injection and unsafe response leakage

Eval tiers:

- Tier 1 (blocker): constraint fidelity, determinism, perturbation, repair safety
- Tier 2 (high value): tool degradation, multi-turn updates, schema strictness
- Tier 3 (hardening): adversarial resilience, semantic stability, A/B drift sensitivity

v2 adds:

- Suggestion-stance evals (`source: suggestion`, partner options + disclaimers)
- Partner-routing evals (region-aware link priorities)
- PDF/email quality gates
- Geo validity checks for map payloads


## 11) Governance model (how decisions are made)

Change policy:

- v1 delivered behavior is baseline.
- v2 plan changes are proposed in docs first, then approved, then implemented.
- No silent scope expansion.

Definition of done per phase:

- Implementation complete
- Tests green
- Relevant evals green
- Docs updated (`architecture`, `implementationPlan`, `projectFileMap`, `CHANGELOG`)

Release policy:

- No release if Tier 1 evals fail.
- Tier 2/3 failures require explicit risk acceptance.


## 12) Immediate next steps (what to do now)

1. Approve v2 phase order and MVP launch line.
2. Start V2.A implementation.
3. In parallel, complete auth + consent + policy pages.
4. Implement V2.E (PDF/email) as the first high-value launch hook.
5. Run private alpha before soft launch.


## 13) Document map (where details live)

- Problem framing (v1 baseline): `docs/problemStatement.md`
- Full architecture (v1 + v2 impact): `docs/architecture.md`
- Detailed phase delivery log and v2 roadmap: `docs/implementationPlan.md`
- File-level code map: `docs/projectFileMap.md`
- Release history: `docs/CHANGELOG.md`
- Full v2 product plan and GTM: `docs/conciergeProductPlan.md`


## 14) Employer/interviewer one-minute pitch

This system is a production-minded multi-agent travel planner.  
v1 is fully delivered with typed contracts, reliability wrappers, repair-loop safety, memory, and a tiered eval gate.  
v2 is intentionally planned as a phased concierge expansion with strict product boundaries: we provide decision-ready research, users execute bookings externally.  
Execution is phase-wise for control, speed, and cost discipline, using a student-budget stack until traction justifies paid upgrades.

