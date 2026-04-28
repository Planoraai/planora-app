AI Travel Planner — Concierge Product Plan (v2 Roadmap)

Owner role:           Principal Product Manager
Status:               PROPOSED. Not yet approved. Awaiting user sign-off.
References:           docs/problemStatement.md, docs/architecture.md, docs/implementationPlan.md, docs/projectFileMap.md
Last updated:         2026-04-28
Covers:               v2 vision, partner ecosystem, phase plan (V2.A–V2.H), GTM strategy, student-budget stack ($0/month), launch plan, 3-day Student Pack prep window
Reading order:        principle → ecosystem → phases → GTM → stack → launch → 3-day prep → approval gate


Why this plan exists

The current system (Phases 0–10) ships a working multi-agent itinerary generator. The next iteration must turn it into a true travel concierge that walks the user from "I want to go to Vietnam for 10 days" all the way to "here is your visa info, your flight option, your day-by-day hotel + transport + entry-fee plan, on a map, and emailed as a PDF". This document captures that vision, the gaps, the scope, and the staged rollout — and is the document you will explicitly approve before code work begins.


Product principle (the stance we will not violate in v1 and v2)

This product is a research-and-planning platform under one roof. We help the user build a complete, decision-ready travel plan; the user implements it on their own.

What that means concretely for v1 and v2:

- We surface options, comparisons, indicative prices, and informed recommendations — all in one place so the user does not have to stitch ten tabs together.
- We never book, reserve, transact, charge, file, or commit on the user's behalf.
- Every external action (book this flight, reserve this hotel, apply for this visa, buy this insurance) is performed by the user on the partner site, via a clearly labelled deep link or copy-pasteable detail.
- Every price, schedule, availability, visa rule, and advisory we show is informational and indicative — the source of truth is the partner / authority at the moment of booking.
- The PDF and email we deliver are personal travel notes for the user; they are not booking confirmations and must never look like one.
- The UI must show, in plain language, that the user is the one who makes the final choice.

A future major release (v3 or later) may extend the platform to support direct booking of flights and hotels from inside our app — see "Future direction (post-v2, not in scope)" below. That work is intentionally not part of this plan and would require a separate product, legal, and compliance review before it is greenlit.

This principle drives the scope, the disclaimers, the legal posture, and the eval suite below.


Partner ecosystem (where we send users to book)

Every option we surface that involves a real-world transaction carries a `partner_link` (or several) to a reputable external site where the user actually books. We do not transact ourselves. The user picks the partner they trust.

The default partner shortlist per category (configurable, region-aware, and replaceable):

- Flights
  - Aggregators: Skyscanner, Google Flights, Kayak, Kiwi.com
  - Direct airline sites: surfaced when the option is a direct flight (e.g. emirates.com, indigo.in, ana.co.jp)
  - User benefit: compare price across aggregators, then book directly with the airline if preferred
- Hotels
  - Aggregators: Booking.com, Agoda (especially strong for APAC: Vietnam, Thailand, Indonesia, Japan), Hotels.com, Expedia
  - Direct hotel sites: surfaced when we have a confident match
  - Niche: Hostelworld for budget / solo traveller persona; Airbnb / VRBO for stays-with-kitchen
- Trains
  - Region-specific: 12Go (SE Asia), Trainline (Europe / UK), IRCTC (India), JR-Pass (Japan), Amtrak (US)
- Buses / coaches
  - Region-specific: 12Go, Redbus (India / SE Asia), FlixBus (Europe)
- Local transport
  - Informational only (Uber, Ola, Grab, Bolt, Didi, local metro apps); no deep linking required
- Tours and tickets
  - GetYourGuide, Viator, Klook (especially strong for APAC)
- Visa
  - Official government / embassy portals only; never a third-party visa-mill
  - Optional: VFS / BLS as authorised application centres where applicable
- Travel insurance
  - SafetyWing, World Nomads, Allianz; localised options where available
- eSIM / connectivity
  - Airalo, Holafly
- Currency
  - Wise, Revolut, XE for FX rates; informational

How the partner shortlist is implemented (engineering note for v2)

- Each tool's response carries an array of `partner_options[]`, each with `name`, `url`, `region`, `affiliate` (true/false), `disclaimer`
- The shortlist is configurable per environment (`partners.yaml` or env-driven), so we can rotate, add a new region, or drop a partner without code changes
- Region-aware ranking: a Vietnam trip prefers Agoda for hotels and 12Go for trains, ahead of EU-centric defaults
- Affiliate flag is honest: if a link is an affiliate link, the UI and PDF show the affiliate disclosure


North star user story

A user lands on the app and types:

    "I live in Mumbai. Plan a 10-day trip to Vietnam in October to see the most famous places. I am a vegetarian. Budget around 2500 USD."

The system should return a concierge-grade set of suggestions that includes:

- Pre-trip: visa requirements + processing time, vaccinations, travel insurance hint, currency, language phrasebook, packing notes
- Travel-from-home: flight options (date, airline, layovers, indicative price, deep link to the partner site) and arrival airport — the user picks and books
- Best time / crowd / festivals: what October looks like in Vietnam — crowd_level, weather, festivals during user's window
- City-by-city plan: which famous places, ordered to reduce backtracking — the user is free to drop, swap, or reorder
- Stays: 1–2 hotel options per city with view, rating, indicative price, area, and deep link — the user picks and books
- Local transport per city: typical mode (cab, metro, scooter), indicative cost
- Inter-city movement: flight / train / bus options with duration and indicative price
- Entry fees per attraction included in the budget breakdown
- Map view: every leg and every attraction plotted with markers + polylines
- Export: ability to email a PDF copy of these suggestions to the user
- Disclaimers: every section is labelled as a suggestion; visa info is informational, not legal advice; prices are indicative; the user is the decision-maker


Current state vs target state

| Capability                         | v1 (today)                                | v2 (target)                                                       |
|------------------------------------|-------------------------------------------|-------------------------------------------------------------------|
| Origin awareness                   | none                                      | `origin_city` + `origin_country` + `start_date` aware             |
| Flight from home                   | none                                      | `flight_search` tool + dedicated logistics agent leg              |
| Visa info                          | none                                      | `visa_requirements` tool + Pre-Trip agent                         |
| Best month / crowd / festivals     | implicit only                             | `seasonality_calendar` + Pre-Trip agent + per-day signals          |
| Hotel detail                       | basic name + area                         | view, rating, amenities, indicative price                         |
| Local in-city transport            | implicit                                  | `local_transport_guide` + per-city section in itinerary           |
| Entry fees                         | rolled into `price_estimate`              | typed line items in budget breakdown                              |
| Map view                           | none                                      | provider-backed map in `apps/web` with markers + routes           |
| PDF export                         | none                                      | `POST /api/v1/trips/export/pdf`                                   |
| Email delivery                     | none                                      | `POST /api/v1/trips/email` (Gmail or SendGrid/Mailgun)            |
| Personalization memory             | basic preference profile                  | trip history, saved trips, repeat-traveler signals                |
| Multi-traveler / group             | single traveler only                      | `travelers[]`, dietary, accessibility per traveler                |
| Live trip updates                  | none                                      | weather + flight status + re-route on delay                       |
| Compliance / disclaimers           | none                                      | visa, health, advisory disclaimers in payload + UI                |


User personas (driving feature priority)

- The Solo Explorer (backpacker): cheapest, flexible dates, hostels, public transit
- The Couple Getaway: comfort, balanced budget, well-known spots, good views
- The Family Trip (with kids or seniors): low pace, accessibility, kid-friendly food, safety
- The Business Add-on Leisure: short windows, premium stays, airport-proximity hotels
- The First-time International Traveler: heavy hand-holding on visa, currency, safety

Each phase below is annotated with which persona it most benefits.


Capability gap analysis

What the user explicitly requested

- Step-by-step suggestion path from home to destination
- Airline suggestions with indicative price and a deep link to book externally (we do not handle bookings)
- Visa process information (informational, not legal advice)
- Best month / crowd level / festival timings
- Hotel suggestions including a "with view" option
- Local transport guidance (cab, bus, train, flight) per leg
- Entry fees surfaced in the budget breakdown
- Map view of suggested locations
- Email of the suggestion PDF

What the user did not explicitly mention but the PM strongly recommends including

Pre-trip preparation
- Travel insurance recommendation (third-party links only, never selling insurance ourselves)
- SIM / eSIM / data roaming guidance
- Health and vaccination advice (sourced from CDC / WHO with disclaimer)
- Power-adapter / packing checklist tailored to destination
- Embassy and local emergency numbers
- Currency conversion + average tipping guidance
- Local payment methods (UPI in India, Alipay/WeChat in China, etc.)

Trust, safety, compliance
- Travel advisory feed (US State Dept / UK FCDO / India MEA where available)
- Common scam warnings per destination
- Visa info disclaimer (informational, not legal advice)
- "Indicative price / availability — confirm on the partner site" disclaimer wherever a price or seat appears
- GDPR-friendly handling of email + saved trips
- PII redaction in logs (already partially in v1)

Personalization & profile
- Travel style: luxury / mid-range / budget / backpacker
- Group composition: solo / couple / family-kids / family-seniors
- Dietary restrictions: veg / vegan / halal / kosher / allergies
- Accessibility needs: wheelchair, mobility, sensory
- Pace preference: relaxed / standard / packed
- Save past trips and learn cross-trip preferences

Multi-traveler and collaboration
- Multiple travelers per trip plan (with per-traveler profile fields)
- Cost split per traveler in budget summary
- Share-link to suggestion plan (read-only token)

Live trip mode (during the trip)
- Real-time weather alerts for upcoming day
- Optional flight status check-in (user pastes flight number; we read public status, we never hold their booking)
- Suggestion to re-shuffle remaining days on disruption — the user accepts, edits, or ignores

Communication channels
- PDF (mandatory, requested by user)
- Email (mandatory, requested by user)
- Calendar invite as `.ics` (low-cost win)
- Optional WhatsApp / Telegram delivery (later phase)

Trip management
- Dashboard with upcoming / past / saved trips
- Duplicate, edit, cancel a trip
- Compare two itinerary variants side-by-side (e.g. budget vs comfort)

Analytics & feedback
- Per-trip rating after completion
- "Did the user actually do this day?" (optional check-in)
- Funnel metrics (request → planned → exported → emailed)

Monetization (informational, not committing)
- Affiliate / partner deep links per the Partner ecosystem section (e.g. Skyscanner / airline sites for flights, Booking.com / Agoda for hotels, GetYourGuide / Viator / Klook for tickets, 12Go / Trainline / Redbus for ground transport) — clicking takes the user to the partner site where they decide and transact
- Affiliate disclosure shown in the UI and in the PDF footer; `affiliate: true` flag travels through the API payload too, so the UI cannot accidentally hide it
- Premium tier (PDF + email + multi-itinerary compare) — explicit gate

Internationalization
- UI multi-language (start with EN; HI, JA later)
- Multi-currency display in budget block

Performance & cost
- Real-API tier costs are non-trivial (flight + hotel + maps). Need cost-per-request budget and caching strategy.
- Latency budget will rise; we already have `HardenedPlannerService` to enforce a max time.

Open questions the PM is parking for the user

- Will we charge users? If yes, where is the paywall?
- Deep-link-only is now the default per the product principle. Open question: do we want any partner that requires us to pre-fill a booking form on their side, or strictly "open partner site, user takes it from there"?
- Are we comfortable storing user emails for delivery?
- Which map provider (Google vs Mapbox) — cost vs DX trade-off?
- Which flight provider (Amadeus self-service vs Kiwi affiliate vs SerpAPI Google Flights) — cost vs reliability trade-off? Note: any choice must support read-only quote retrieval; we do not need a "create booking" endpoint from any of them.
- Do we need authentication (login) before "save trip" / "email me"? Recommended: yes.


Phase plan (proposed rollout order)

Each phase is sized so it can ship independently with green tests, mock-mode parity, and a clear acceptance demo.


Phase V2.A — Origin awareness, traveler profile, and trip dates

Goal

Make the trip plan aware of where the user is travelling from, when, and with whom.

Tasks

- Extend `TripBrief` schema (`packages/domain_contracts`) with: `origin_city`, `origin_country`, `travel_dates` (start_date, end_date), `travelers[]` (count, dietary, accessibility), `travel_style`, `pace`
- Update parser (`packages/orchestrator/parser.py`) to recognize "I live in X", "from X to Y", explicit dates, and traveler hints
- Update orchestrator graph state to carry origin and traveler profile through every node
- Update API request schema in `apps/api/app/api/trip_planning.py` (backward-compatible: existing `prompt` keeps working)
- Update Tier 1 evals to include origin, dates, traveler profile fidelity
- Frontend: add an optional "About your trip" pre-form that pre-fills these fields without being mandatory

Exit criteria

- A request mentioning home + dates parses correctly into typed fields
- All existing tests + new origin-awareness tests pass
- Existing API contract still works for clients that send only `prompt`


Phase V2.B — Real-world tool integrations

Goal

Add the new tools the concierge needs, all wrapped in the existing `BaseTool` runtime (typed I/O, retries, real-timeout, cache, mock fallback).

Tasks

- New tools under `packages/tools/src/tools/`. Every tool is read-only (quote, lookup, or info). None of them perform booking, payment, or stateful writes on partner systems. Tools that surface a real-world option must populate `partner_options[]` per the Partner ecosystem section.
  - `flight_search` (Amadeus / Kiwi / SerpAPI Google Flights, mock-first) — returns options + indicative price + `partner_options` (Skyscanner, Google Flights, Kayak, direct airline site)
  - `visa_requirements` (Sherpa or curated KB + LLM verification) — informational, with mandatory disclaimer; `partner_options` are official embassy / government portals only
  - `seasonality_calendar` (climate + crowd + festivals; combine `web_search` + curated KB)
  - `attraction_fees` (or extend `price_estimate` with a `category=entry_fee` channel) — indicative only; `partner_options` may include GetYourGuide, Viator, Klook for ticketed attractions
  - `local_transport_guide` (per-city typical modes + indicative cost) — informational, no booking handoff required
  - `hotel_search` enrichment (view, amenities, rating fields added to schema) — returns options + `partner_options` (Booking.com, Agoda, Hotels.com, Expedia; Hostelworld for budget; Airbnb / VRBO for stays-with-kitchen); never a reservation
  - `intercity_transport` (new): trains and buses with region-aware partner mapping (12Go, Trainline, IRCTC, JR-Pass, Amtrak, Redbus, FlixBus)
  - `geocoding` (reverse + forward) and `directions` (provider TBD)
- Tool-contract tests for every new tool (schema, retries, mock vs real)
- Per-tool TTL + cache key strategy (especially for flight_search which is expensive)
- Update `ToolRegistry` and `apps/api/requirements.txt`

Exit criteria

- All new tools have typed schemas, mock implementations, and contract tests
- Real-mode adapters return data within the latency budget for at least one provider per tool
- No tool change breaks the existing 95-test regression


Phase V2.C — New / extended worker agents

Goal

Translate the new tool data into typed plan output usable by the synthesis agent.

Tasks

- New agent: `packages/agents/pre_trip/` — produces `PreTripBriefing` (visa, vaccinations, sim, packing, embassy, advisories)
- New agent: `packages/agents/timing/` — produces `TimingReport` (best-month, crowd_level per month, festivals during travel window)
- Extend `agents/destination/` to incorporate `TimingReport` so recommendations reflect crowd/festival reality
- Extend `agents/logistics/` to:
  - Add `from_home` flight leg using `flight_search`
  - Attach `local_transport_guide` to each city block
  - Attach geocoding to every city / POI
- Extend `agents/budget/` to add explicit line items for: flights, entry fees, local transport, optional insurance
- New domain contracts (`packages/domain_contracts`):
  - `PreTripBriefing`, `TimingReport`, `FlightLeg`, `LocalTransportTip`, `EntryFee`
  - Extend `Itinerary` to embed these and `geo` markers per city / POI

Exit criteria

- Synthesis produces an `Itinerary` that includes pre-trip, timing, flights, local transport, entry fees, and geo
- Validator updated with rules for flight + entry-fee feasibility
- Repair loop covers new failure modes (e.g. visa data missing, festival conflict)


Phase V2.D — Maps feature (frontend + backend wiring)

Goal

Make every recommendation visible on a real map.

Tasks

- Decide provider (recommendation: Mapbox if cost-sensitive; Google if data quality matters most)
- Backend: ensure every itinerary entity has `lat/lng` (Phase V2.C populates them)
- Frontend (`apps/web`):
  - New `MapPanel` component
  - V1 view: city markers + intercity polylines
  - V2 view: per-day route + POI markers with popovers (price, hours, fee)
  - Provider key configured via `NEXT_PUBLIC_MAPS_*`
- Tests:
  - Tool-level: geocoding + directions contract tests
  - Frontend: render test for MapPanel (markers count, polyline count)

Exit criteria

- Map renders for any successfully planned trip
- Map degrades gracefully if geocoding fails (text-only fallback)


Phase V2.E — PDF export and email delivery

Goal

Let users walk away with a real artifact: a PDF of their personal travel suggestions, delivered by email. The PDF is explicitly labelled as suggestions, not a booking confirmation.

Tasks

- PDF service:
  - Library: `weasyprint` (HTML → PDF) for layout flexibility, or `reportlab` for pure-Python
  - HTML template stored under `apps/api/app/templates/itinerary_pdf.html`
  - Header banner: "Travel suggestions for <user>. Not a booking confirmation."
  - Footer disclaimers: indicative price, visa-info informational, affiliate disclosure if applicable
  - Tests render a sample itinerary to PDF and verify file size, header banner text, and presence of key sections
- Email delivery:
  - Provider choice (recommend SendGrid or Mailgun for transactional simplicity; Gmail OAuth2 for "send-as user" only if necessary)
  - Tokenized download link as fallback
  - Rate limiting and abuse prevention
- New endpoints:
  - `POST /api/v1/trips/export/pdf` → returns PDF bytes
  - `POST /api/v1/trips/email`     → triggers email send
- Compliance: explicit user opt-in, GDPR-style data minimization, no marketing emails

Exit criteria

- A planned trip can be exported as PDF and emailed to the requested address
- Failure cases (bad email, provider outage) return typed `503` with structured error envelope (matches existing pattern)
- Rate limiting prevents abuse


Phase V2.F — Personalization, multi-traveler, and saved trips

Goal

Let users come back, save trips, and have the system remember them.

Tasks

- Persistence: introduce a real datastore (Postgres recommended) for users, saved trips, preferences
  - The existing `packages/memory/` interfaces are designed to allow this swap; this phase implements the real backends
- Auth: minimal email-link or OAuth (Google) login (open question for user)
- Multi-traveler: cost split, per-traveler dietary / accessibility flags
- Compare two variants: budget vs comfort vs adventure
- Trip dashboard in `apps/web`: upcoming, past, saved, duplicate, share

Exit criteria

- A logged-in user can save, retrieve, edit, and delete a trip
- The same user gets progressively personalized recommendations across sessions


Phase V2.G — Live trip mode (in-trip companion)

Goal

Become useful during the trip, not just before. Still suggestion-only — we never assume control of the user's bookings or schedule.

Tasks

- Per-day notification windows (push or email) with weather + (optional) flight status the user has pasted in
- Suggestion to re-shuffle remaining days on disruption, surfaced as a proposed change the user must accept, edit, or dismiss
- Optional opt-in: "ping me if rain forecast above 60%"
- Explicit copy in every notification: "This is a suggestion. Your bookings are with the partner site."

Exit criteria

- A trip in progress receives at most one informational ping per day, with opt-out always available
- Re-route suggestion arrives within 10 minutes of detected disruption and is presented as a proposal, never auto-applied


Phase V2.H — Hardening, evals, observability for v2

Goal

Make v2 release-grade, with the same rigor as v1.

Tasks

- New evals (extend `apps/api/tests/test_eval_tiers.py`):
  - Origin-aware fidelity eval
  - Visa-correctness eval (against a curated test matrix per top 30 destinations)
  - Festival-accuracy eval
  - Entry-fee-presence eval
  - Map-payload geo-validity eval (every city has `lat/lng`)
  - PDF export eval (file generated within latency budget)
  - Email-delivery eval (sandbox provider in CI)
  - Suggestion-stance eval: every flight / hotel / visa / insurance / intercity-transport / ticketed-attraction block in the response includes a `source: "suggestion"` flag, a non-empty `partner_options[]` (each with `name`, `url`, `region`, `affiliate`, `disclaimer`) for transactable categories, and a disclaimer string; PDF and email payloads carry the "suggestions, not booking confirmation" header
  - Partner-routing eval: a Vietnam trip surfaces Agoda for hotels and 12Go for trains ahead of EU-centric defaults; a Europe trip surfaces Booking.com and Trainline; a US trip surfaces Hotels.com / Expedia and Amtrak — confirms region-aware ranking is wired
- Cost-per-request observability dashboards (LLM tokens + each external API)
- Real-API rate limiting + circuit-breaker tuning
- Compliance: visa / advisory disclaimers in every itinerary payload and PDF
- Risk register sign-off

Exit criteria

- All new evals pass in CI
- Cost-per-request stays within target budget on a representative test set
- All disclaimers present in API and PDF


Cross-cutting concerns (apply across phases)

Compliance and legal

- Suggestion stance is the foundational disclaimer: every response, PDF, and email is labelled "Travel suggestions. The user is the decision-maker. Confirm details on the partner site before booking."
- Visa data is informational; mandatory disclaimer in payload + PDF
- Health / vaccination data sourced from CDC/WHO with disclaimer
- Affiliate links must be disclosed if used
- GDPR: explicit consent before storing email / saving trips

Trust and safety

- Travel advisories visible in pre-trip section, color-coded
- Common scam warnings per destination
- Disclaimer that prices are indicative, not guaranteed
- No partner content is presented as "confirmed", "reserved", "booked", or "paid"

Performance and cost

- Latency budget for v2 happy path: 12s (current v1 budget is 5–8s)
- Cost-per-request budget per tier (mock / standard / premium); track in observability
- Caching: every external API call is cache-keyed; agent-level results cache for repeat users (already in `packages/memory`)

Internationalization

- Phase 0 of i18n: English-only with translatable string layer ready
- Phase 1 of i18n: Add HI and JA (covers India and Japan)

Analytics

- Funnel events: prompt → planned → exported → emailed
- Per-trip post-trip rating
- Aggregate: which destinations are most-requested?

Personalization

- Already-implemented `UserPreferenceProfile` extended in V2.F to include trip_history
- Re-rank destinations using prior preferences and avoidances

Architecture impact summary

- Every new capability fits the current domain-driven monorepo with no rewrites:
  - New tools land in `packages/tools/`
  - New agents land in `packages/agents/<capability>/`
  - New domain contracts land in `packages/domain_contracts/`
  - New API endpoints land in `apps/api/app/api/`
  - New frontend views land in `apps/web/src/components/`


Risks and mitigations

- External-API cost spikes:    enforce per-tool TTL + circuit breaker + cost dashboard
- Visa info correctness:       curated KB + disclaimer + version-pin per source
- LLM hallucination on flights: never claim a flight exists without a tool quote; enforce schema strictness
- Email abuse:                 strict rate-limit + opt-in + sender-domain authentication
- Latency budget breach:       tiered model fallback + degraded "best-effort" response (already supported by `HardenedPlannerService`)
- Vendor lock-in:              every tool is behind `BaseTool` interface; we can swap providers


What is explicitly out of scope for v2

The product principle ("research + plan with us, transact on the partner site") makes the following explicit non-goals. None of these will be added in v2 without a separate product review:

- Real-time live booking, ticketing, or payment processing — we suggest, the user transacts on the partner site
- Holding or storing the user's payment methods or partner credentials
- Insurance underwriting or selling — we link to providers
- Visa application filing or document submission — we inform only
- Currency exchange or money movement — we estimate only
- Loyalty program management or mileage redemption
- Auto-applying changes to the user's plan during the trip — every change is a suggestion the user accepts
- Acting as a travel agent of record for any partner


Future direction (post-v2, not in scope for this plan)

The natural next step, once the research-and-planning experience is solid, is to let the user complete the booking inside our platform instead of being handed off to a partner site. This is not a v2 commitment — it is captured here so the v2 architecture stays compatible with it.

What that future could look like

- In-app booking for flights and hotels (and possibly tours, transfers, insurance)
- Stored bookings tied to the saved trip (so live trip mode in V2.G can reason about them without the user pasting flight numbers)
- Confirmation emails clearly distinct from suggestion emails
- Refund / change flows handled in coordination with the partner

What we are deliberately doing in v2 to keep this future open

- Every external option already carries a `partner_link` and a clean source of truth — adding a "book with us" button later is additive
- The data contracts (`FlightLeg`, hotel option, etc.) are designed to be the same shape whether the source is "suggestion" or, later, "confirmed booking via partner API"
- Memory and saved-trips persistence (V2.F) introduces the data model that a future booking record would attach to

What that future would require before greenlit (not blocking v2)

- Travel-agency licensing or partner reseller agreements, region by region
- PCI-DSS compliance for payment handling, or full delegation to a payments provider
- KYC / fraud / abuse controls
- Customer support pathway for change / refund / dispute
- A separate product, legal, and compliance review
- Distinct contractual stance: we become a transacting party, not just an informational tool, which changes the risk profile entirely

This future is recorded so we never lose sight of it; it is not part of v2 and will not be touched until v2 ships and we explicitly decide to greenlight it.


Go-to-market and rollout strategy

The product principle says "research + plan with us, transact on the partner site". The GTM principle is the matching one: ship a tight MVP, capture every active user's email at the moment they get value, drip features to that list as we ship them, never run a "secret marketing" play.

MVP cut (the launch line)

The MVP is the smallest version of v2 that gives the user a real "wow" plus gives us a first-class email list. Concretely:

- v1 planner core (already built) running on a free LLM (Gemini Flash by default)
- Phase V2.A: origin awareness, dates, traveler profile (so the plan feels personalized)
- Phase V2.E: PDF export + email-the-itinerary (the perceived-value moment)
- Auth-gated signup (email captured during signup, not as a separate "waitlist" page)
- Privacy Policy + Terms of Service live, linked from footer
- Sender-domain hygiene: SPF + DKIM + DMARC configured day one

Notably NOT in MVP — explicitly delayed to keep cost and timeline tight:

- Real flight search, real hotel search, visa, seasonality, maps (V2.B / V2.C / V2.D)
- Live trip mode (V2.G)
- Personalization datastore beyond what V2.E + V2.F minimally need

Critical cost-cheat: instead of paid flight / hotel APIs at launch, we generate deep-links to partner search URLs (Skyscanner, Agoda, Booking.com) with the user's parameters pre-filled in the query string. Zero API cost, looks like a feature, and stays consistent with the suggestion-only stance.

Auth-gated signup as the email-capture mechanism

We do not run a separate "waitlist" page. The product itself is the hook; signup is the unlock for "save trip", "email me my plan", and "more than one trip per session".

Signup flow (one screen)

- Auth options: Google OAuth (primary, one-click) and email + password (fallback)
- Mandatory checkbox: "I agree to the Terms and Privacy Policy."
- Optional checkbox: "Email me when we launch new features (about once a month, unsubscribe anytime)."
  - Default unchecked in EU + UK + India (GDPR / DPDP-compliant)
  - Default checked + clearly visible in US + AU + NZ + everywhere else
- Microcopy under the form: "We email you about your account and your saved trips. Marketing emails are opt-in only and easy to unsubscribe from."
- Consent log written to DB: which boxes ticked, timestamp, IP, region — this is our legal proof

Drip cadence (one email per feature drop)

- Welcome email immediately on signup (transactional)
- "Your trip is ready" email immediately on first trip save (transactional)
- One marketing email per feature drop:
  - V2.E ships → "Get your trip as a PDF, sent to your inbox"
  - V2.B + V2.C ship → "Your plan now includes real flights, hotels, visa info"
  - V2.D ships → "See your trip on a map" + screenshot
  - V2.F ships → "Personalized to you. All your trips in one place."
  - V2.G ships → "We will check in with you during your trip"
- Maximum: one marketing email per 3 weeks. Beyond that, complaint rates spike.
- Every marketing email carries a one-click List-Unsubscribe header
- Suppression list enforced at DB layer — cannot be bypassed by a forgetful operator

Why not run a "secret" marketing play

For the record: capturing an email through auth and then quietly emailing the user about new features without a disclosed opt-in is a textbook GDPR / DPDP / CAN-SPAM violation. It also performs worse than the disclosed version because un-consented sends get spam-reported, killing sender reputation. The disclosed two-checkbox flow above gives the same email list, with consent, with no downside.


Student-budget stack ($0/month)

Constraint acknowledged: this is a student build with no funds. The stack below runs the entire MVP at $0/month operating cost, with one $10/year domain that is also obtainable for free via the GitHub Student Developer Pack.

Free-tier infrastructure matrix

| Layer            | Recommended free option                              | Free-tier headroom                              |
|------------------|------------------------------------------------------|-------------------------------------------------|
| Frontend hosting | Vercel free                                          | 100 GB bandwidth/month                          |
| Backend hosting  | Render free (or Fly.io / Hugging Face Spaces)         | sleeps after idle; fine for early-stage         |
| Database + auth  | Supabase free                                        | 500 MB Postgres, Google + email + magic-link auth, 50 K MAU |
| Email sending    | Resend free (transactional + marketing)              | 3 000 emails/month, 100/day                     |
| DNS + SSL        | Cloudflare free                                      | DNS, SSL, DMARC tooling, DDoS protection        |
| Domain           | Free `.me` via GitHub Student Pack (Namecheap)       | 1 year free; or $10/year `.com` from Cloudflare/Porkbun |
| LLM              | Gemini 1.5 Flash free tier (or Groq Llama 3 / Mixtral) | 1 500 req/day on Gemini Flash                   |
| Maps             | OpenFreeMap or Mapbox free                           | 50 K loads/month on Mapbox                      |
| Geocoding        | Nominatim (OpenStreetMap)                            | rate-limited; respect their fair-use policy     |
| Weather          | OpenWeatherMap free                                  | 60 calls/min, 1 M calls/month                   |
| Analytics        | PostHog Cloud free                                   | 1 M events/month                                |
| Error monitoring | Sentry developer plan (free via Student Pack)        | 5 K errors/month                                |
| Uptime           | UptimeRobot free                                     | 50 monitors, 5-min interval                     |
| Privacy / ToS    | Termly free generator                                | covers GDPR / CCPA / DPDP basics; free for small sites |

Total monthly cost: $0. Total yearly cost: $0–10 (just the domain if not using the free `.me`).

GitHub Student Developer Pack callouts (claim the moment it activates)

The Pack approval triggers a 72-hour activation cooldown before partner perks unlock. Useful claims, in priority order:

1. Namecheap free `.me` domain (1 year)
2. Cloudflare Pro free (1 year) — image optimization + better caching
3. Sentry developer plan — error monitoring on both frontend and backend
4. DigitalOcean $200 credit (12 months) — kept as fallback if Render free becomes painful
5. JetBrains Pack — PyCharm Pro / WebStorm (optional)
6. Skip: Heroku, MongoDB Atlas — not needed; Supabase covers DB

LLM cost containment (the only variable bill)

This is where most student AI products quietly bleed money. Day-one rules:

- Default model: Gemini 1.5 Flash; fallback: Groq Llama 3 / Mixtral
- Reserve GPT-4 / Claude only for the synthesis step that runs once per request, never inside loops
- Cache every request keyed on prompt hash (already implemented in `packages/memory`)
- Per-user rate limit: 5 trip plans/day on free
- Hard daily cap: alert email if daily LLM spend exceeds $1; stop sending if it exceeds $3
- Realistic envelope: ~$0.01–0.05 per planned trip on Gemini Flash; 100 users × 3 trips/month ≈ $9/month total

Outgrowing the free tier — what to upgrade first

Each paid tier kicks in only when usage justifies it:

- Vercel bandwidth cap → real users; either monetise or take freelance work to fund it
- Supabase 500 MB cap → tens of thousands of saved trips; consider $25/month Pro
- Resend 3 K/month cap → real engagement; switch to Brevo (300/day free) or Resend $20/month
- LLM cost > $50/month → introduce free tier (3 plans/day) + $5/month unlimited tier; 10 paying users covers it


Launch plan and timeline

Launch line (the must-be-true list before we go public)

Must-have (blockers — cannot launch without these)

- Auth-gated signup with two-checkbox consent live
- Phase V2.A landed: parser handles origin, dates, travelers; trip plan reflects them
- Phase V2.E landed: PDF export + email-the-itinerary work end-to-end
- Privacy Policy + Terms of Service published, linked from footer
- SPF + DKIM + DMARC configured on the sender domain
- A real domain (free `.me` from Student Pack, or paid `.com`)
- LLM hard-cap configured with daily quota alert
- Sentry error monitoring on both frontend and backend
- One-click unsubscribe on every email
- Mobile-responsive layout (most travel research happens on phones)
- Suppression list enforced at DB layer

Should-have (do not block launch)

- Curated visa info JSON for top 30 destinations (zero API cost, big perceived value)
- Real geocoding via Nominatim (free with attribution)
- Real weather via OpenWeatherMap free
- PostHog analytics wired

Nice-to-have (explicitly skipped at launch)

- Real flight search → mock + Skyscanner deep-links
- Real hotel search → mock + Booking.com / Agoda deep-links
- Maps (V2.D) → ship 2 weeks after launch as the first feature drop
- Live trip mode (V2.G) → 2 months post-launch minimum

Launch ladder (do not skip stages)

- Stage 1 — Private alpha (week 5–6): 10–20 personal contacts, WhatsApp / Telegram, catch obvious bugs, fix top 5 issues
- Stage 2 — Soft launch (week 7–8): Reddit (r/solotravel, r/travel, r/IndiaTravel, r/digitalnomad), Indie Hackers, university travel groups, Twitter/X. Honest pitch, not hype. Target 100–500 signups.
- Stage 3 — Public launch (week 10–12): Product Hunt, Hacker News (Show HN), travel blogs. Ship V2.D maps as the launch hook so there is a "what's new" angle. Target 1 000+ signups in launch week.

Each stage exists to surface a different class of failure before the audience gets bigger. Skipping stages is how products die in public.

Week-by-week timeline (10–15 hrs/week of student-effort)

| Week | Milestones                                                                              |
|------|------------------------------------------------------------------------------------------|
| 1    | Domain + Cloudflare DNS + Vercel + Render + Supabase + Resend account setup              |
| 2    | Auth UI + two-checkbox consent + welcome email + Privacy Policy + ToS + suppression list |
| 3    | Phase V2.A: schema + parser + frontend pre-form + Tier-1 evals updated                   |
| 4    | Phase V2.E: WeasyPrint PDF + email endpoint wired to Resend + sandbox testing            |
| 5    | Mobile pass + Sentry + LLM hard-cap + private alpha (10–20 invites)                       |
| 6–7  | Iterate on alpha feedback + curated visa JSON + Skyscanner/Agoda deep-links + soft launch on Reddit |
| 8–10 | Phase V2.D maps + public launch on Product Hunt / HN with maps as launch hook            |

Total time to first signup: ~5 weeks. Total time to soft launch: ~7 weeks. Total time to public launch: ~10 weeks.

Anti-patterns to avoid

- Do not launch a "coming soon" page with email-only capture. Conversion is bad and you learn nothing.
- Do not wait for V2.B / V2.C real flights and hotels before launch. Deep-links cover 80% of the perceived value at 0% of the cost.
- Do not ship without privacy policy + ToS + unsubscribe + DMARC. One spam complaint in week one will kill your sender domain for months.
- Do not optimize for Product Hunt #1. Optimize for retention and email-list growth.
- Do not skip the private alpha. It is 5 hours of work that saves 50 hours of public embarrassment.


3-day prep checklist (Student Pack 72-hour activation window)

When the GitHub Education approval lands, partner perks unlock 72 hours later. These three days are not idle time — they cover Week 1 of the launch timeline using only zero-card free tiers.

Day 1 — accounts and deployment rails (2–4 hrs)

- Create accounts: Supabase, Vercel, Render, Resend, Cloudflare, PostHog, UptimeRobot
- Deploy current `apps/web` to Vercel (free) and `apps/api` to Render (free)
- Verify both URLs are reachable from a phone browser too
- Output: 2 live URLs (web + api) on free tiers

Day 2 — auth + policy + email infrastructure (3–5 hrs)

- Provision Supabase Auth: enable Google OAuth + email + magic-link
- Draft Privacy Policy + ToS via Termly free generator (fill placeholders later for company-name / domain)
- Sketch the `users` + `email_log` + `unsubscribe_tokens` tables in Supabase schema
- Output: auth provider configured, policy drafts ready to paste

Day 3 — V2.A + V2.E build prep (3–5 hrs)

- Finalize V2.A coding checklist: `TripBrief` new fields (origin, dates, travelers), parser cases, API backward compatibility, frontend pre-form
- Finalize V2.E coding checklist: PDF template sections, email endpoint behaviour, Resend SDK plan
- Finalize test plan: parser unit tests, API contract tests, one E2E happy path
- Output: zero-ambiguity coding backlog ready for Day 4

Day 4 (Pack unlocks) — first 60 minutes

- Claim free `.me` domain on Namecheap (or buy `.com` if preferred)
- Point DNS to Cloudflare; configure SPF, DKIM, DMARC records
- Verify sender domain in Resend
- Claim Cloudflare Pro + Sentry developer plan (Pack perks)
- Then: start coding V2.A

What NOT to do during the 72 hours

- Do not integrate paid flight / hotel APIs
- Do not over-design the landing page
- Do not chase pixel-perfect UI polish
- Do not wait idly for the Pack — every Day-1 / Day-2 / Day-3 task is unblocked already


Approval gate

To move from PROPOSED → APPROVED, the user must sign off on:

- The scope above (Phase V2.A through V2.H)
- The list of "PM additions" they accept and the ones they reject
- The listed Open questions (especially monetization and provider choice)
- The priority order of phases (default order proposed, can be reshuffled)
- The release-grade exit criteria (Phase V2.H)

Once approved, this document becomes the v2 contract. Work order will be opened phase by phase, with each phase landing as its own set of PRs and a CHANGELOG entry.


How this maps onto existing docs

This document is the v2 contract. The other docs reference it from their v2-related sections so there is a single source of truth.

- docs/problemStatement.md       → carries a forward-pointer noting that this document supersedes for v2 scope
- docs/architecture.md           → has a new section "17. v2 concierge expansion (planned)" pointing here for full detail
- docs/implementationPlan.md     → has a new section "Roadmap — v2 concierge expansion (planned)" listing V2.A–V2.H in the same Goal / Tasks / Exit-criteria style as v1
- docs/projectFileMap.md         → has a new section "9. v2 expansion preview" showing where the new packages, tools, and agents will land once they ship
- docs/CHANGELOG.md              → has an `Unreleased — 0.12.0-proposed` entry capturing the v2 product plan; subsequent shipping phases each get their own entry (`0.12.0` for V2.A, `0.13.0` for V2.B, etc.)


Glossary

- Concierge plan       → the v2 set of suggestions covering pre-trip, flights, local transport, fees, map, PDF — always advisory, never a booking
- Suggestion stance    → the product principle that we surface options and the user makes the final call; encoded as a flag + disclaimer on every external option
- Partner link         → outbound deep link to a booking site (Skyscanner / airline site for flights, Booking.com / Agoda for hotels, GetYourGuide / Viator / Klook for tickets, 12Go / Trainline / Redbus for ground transport, etc.); the user transacts there, not with us
- Partner ecosystem    → the configurable, region-aware shortlist of external sites we route the user to per category; see "Partner ecosystem" section
- Pre-trip briefing    → visa, vaccinations, advisories, packing, embassy, currency (informational only)
- Timing report        → climate + crowd + festival info for the chosen window
- Live trip mode       → in-trip companion features (V2.G); informational pings + suggested changes the user must accept
- Real-API mode        → `MOCK_MODE=false`; all tools call live providers in read-only / quote-only mode
- Tier 1/2/3 evals     → existing release-gate evals (`apps/api/tests/test_eval_tiers.py`)
- Launch line          → the must-be-true checklist before public launch; defined in "Launch plan and timeline"
- MVP cut              → V2.A + V2.E + auth + privacy/ToS + DMARC; the smallest version that earns a real email list
- Drip cadence         → one marketing email per feature drop, max one per 3 weeks, opt-in only
- Suppression list     → DB-enforced filter that removes unsubscribed users from every campaign
- GitHub Student Pack  → free perks bundle (domain, Cloudflare Pro, Sentry, JetBrains, DigitalOcean credit) used to keep operating cost at $0/month
