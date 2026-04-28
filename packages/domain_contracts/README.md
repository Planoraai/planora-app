# `packages/domain_contracts/` — Domain contracts

The single source of truth for every Pydantic schema that crosses agent boundaries.

If two layers (orchestrator, tools, agents, memory, reliability) need to agree on the
shape of a value, that value is defined here.

## Contracts

| Module | Type | Purpose |
|---|---|---|
| `trip_brief.py` | `TripBrief`, `TripConstraints` | Parsed user request (origin, cities, dates, budget, prefs) |
| `recommendations.py` | `RecommendationItem`, `CityRecommendations`, `Recommendations` | Output of the destination-research agent |
| `logistics.py` | `StayAllocation`, `IntercityLeg`, `DayBlock`, `DaySkeleton`, `LogisticsPlan` | Output of the logistics-planning agent |
| `budget.py` | `BudgetCategoryBreakdown`, `BudgetFlag`, `BudgetReport` | Output of the budget agent |
| `itinerary.py` | `ItineraryDay`, `Itinerary` | Final synthesised plan |
| `revision.py` | `RevisionRequest` | Feedback the validator/critic and repair loop pass around |

## Verify

```bash
cd apps/api
pytest ../../packages/domain_contracts/tests -q
```

Originally lived as `phases/phase1/src/phase1/schemas/`.
