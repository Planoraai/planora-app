# travel-planner-agent-validator

Itinerary Validator worker: applies hard rules (budget delta, geography, time/pace) against
the proposed `Itinerary` and emits a typed `RevisionRequest` enumerating issues for the
repair loop to act on.

## Layout

```
src/agents/validator/
  __init__.py        # public surface: ItineraryValidatorAgent, build_validator_agent
  agent.py           # rule checks + RevisionRequest emission
tests/
  test_validator_agent.py
```

## Public API

```python
from agents.validator import ItineraryValidatorAgent, build_validator_agent
```

## Verify

```bash
cd ../../../apps/api
.venv\Scripts\Activate.ps1
pytest ../../packages/agents/validator -q
```

## Origin

Originally `phases/phase6/src/phase6/validator.py` (see `docs/implementationPlan.md` Phase 6).
Moved here in Pass 3.
