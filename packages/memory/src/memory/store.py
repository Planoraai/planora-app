"""Phase 9 memory and personalization services."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any, Protocol

from domain_contracts import TripBrief
from orchestrator.graph import OrchestratorState, run_orchestrator


class PlannerRunner(Protocol):
    """Callable protocol for planner execution."""

    def __call__(self, request_text: str) -> OrchestratorState: ...


@dataclass(slots=True)
class RunStateRecord:
    """Short-term state for one planning run."""

    run_id: str
    user_id: str
    prompt: str
    created_at: float
    status: str = "completed"
    approved: bool | None = None
    issues: list[str] = field(default_factory=list)


@dataclass(slots=True)
class UserPreferenceProfile:
    """Long-term user preference profile."""

    user_id: str
    preferences: list[str] = field(default_factory=list)
    avoidances: list[str] = field(default_factory=list)
    updated_at: float = field(default_factory=time)


class InMemoryRunStateStore:
    """In-memory short-term run state storage."""

    def __init__(self) -> None:
        self._runs: dict[str, RunStateRecord] = {}
        self._counter = 0

    def create(self, *, user_id: str, prompt: str) -> RunStateRecord:
        self._counter += 1
        run_id = f"run-{self._counter:06d}"
        record = RunStateRecord(
            run_id=run_id,
            user_id=user_id,
            prompt=prompt,
            created_at=time(),
        )
        self._runs[run_id] = record
        return record

    def complete(self, run_id: str, *, approved: bool, issues: list[str]) -> None:
        if run_id not in self._runs:
            return
        rec = self._runs[run_id]
        rec.approved = approved
        rec.issues = issues
        rec.status = "completed"

    def get(self, run_id: str) -> RunStateRecord | None:
        return self._runs.get(run_id)


class InMemoryUserPreferenceStore:
    """In-memory long-term preference store keyed by user."""

    def __init__(self) -> None:
        self._profiles: dict[str, UserPreferenceProfile] = {}

    def get(self, user_id: str) -> UserPreferenceProfile | None:
        return self._profiles.get(user_id)

    def upsert_from_trip_brief(self, user_id: str, trip_brief: TripBrief) -> UserPreferenceProfile:
        existing = self._profiles.get(user_id)
        if existing is None:
            existing = UserPreferenceProfile(user_id=user_id)
        prefs = sorted({*existing.preferences, *trip_brief.preferences})
        avoids = sorted({*existing.avoidances, *trip_brief.avoidances})
        profile = UserPreferenceProfile(
            user_id=user_id,
            preferences=prefs,
            avoidances=avoids,
            updated_at=time(),
        )
        self._profiles[user_id] = profile
        return profile


class InMemoryPlannerResultCache:
    """Simple cache for full planner outputs."""

    def __init__(self, *, ttl_seconds: float = 300.0, max_entries: int = 256) -> None:
        self._values: dict[str, tuple[float, OrchestratorState]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.hits = 0
        self.misses = 0

    def _key(self, *, user_id: str, prompt: str, opt_in: bool) -> str:
        return f"{user_id}|{opt_in}|{prompt.strip().lower()}"

    def get(self, *, user_id: str, prompt: str, opt_in: bool) -> OrchestratorState | None:
        key = self._key(user_id=user_id, prompt=prompt, opt_in=opt_in)
        entry = self._values.get(key)
        if entry is None:
            self.misses += 1
            return None
        expires_at, value = entry
        if expires_at <= time():
            del self._values[key]
            self.misses += 1
            return None
        self.hits += 1
        # Move to end for a lightweight LRU-like eviction order.
        self._values.pop(key)
        self._values[key] = (expires_at, value)
        return value

    def set(self, *, user_id: str, prompt: str, opt_in: bool, value: OrchestratorState) -> None:
        key = self._key(user_id=user_id, prompt=prompt, opt_in=opt_in)
        expires_at = time() + self.ttl_seconds
        if key in self._values:
            self._values.pop(key)
        self._values[key] = (expires_at, value)
        while len(self._values) > self.max_entries:
            oldest_key = next(iter(self._values))
            del self._values[oldest_key]


def apply_profile_to_prompt(
    *,
    prompt: str,
    profile: UserPreferenceProfile | None,
    opt_in: bool,
) -> str:
    """Inject long-term profile hints into prompt when user opts in."""
    if not opt_in or profile is None:
        return prompt
    if not profile.preferences and not profile.avoidances:
        return prompt
    parts: list[str] = []
    if profile.preferences:
        parts.append(f"Known preferences: {', '.join(profile.preferences)}.")
    if profile.avoidances:
        parts.append(f"Known avoidances: {', '.join(profile.avoidances)}.")
    suffix = " ".join(parts)
    return f"{prompt.strip()} {suffix}".strip()


class MemoryAwarePlanner:
    """Planning orchestrator wrapper with run state, profile, and cache."""

    def __init__(
        self,
        *,
        runner: PlannerRunner = run_orchestrator,
        run_state_store: InMemoryRunStateStore | None = None,
        preference_store: InMemoryUserPreferenceStore | None = None,
        result_cache: InMemoryPlannerResultCache | None = None,
    ) -> None:
        self.runner = runner
        self.run_state_store = run_state_store or InMemoryRunStateStore()
        self.preference_store = preference_store or InMemoryUserPreferenceStore()
        self.result_cache = result_cache or InMemoryPlannerResultCache()

    def run(
        self,
        *,
        prompt: str,
        user_id: str,
        opt_in_personalization: bool = True,
    ) -> tuple[OrchestratorState, dict[str, Any]]:
        profile = self.preference_store.get(user_id)
        enriched_prompt = apply_profile_to_prompt(
            prompt=prompt,
            profile=profile,
            opt_in=opt_in_personalization,
        )

        cached = self.result_cache.get(
            user_id=user_id,
            prompt=prompt,
            opt_in=opt_in_personalization,
        )
        if cached is not None:
            metadata = {
                "cache_hit": True,
                "run_id": "cached",
                "personalization_applied": profile is not None,
            }
            return cached, metadata

        run_record = self.run_state_store.create(user_id=user_id, prompt=enriched_prompt)
        state = self.runner(enriched_prompt)
        review = state["revision_request"]
        self.run_state_store.complete(
            run_record.run_id,
            approved=review.approved,
            issues=review.issues,
        )
        self.preference_store.upsert_from_trip_brief(
            user_id=user_id, trip_brief=state["trip_brief"]
        )
        self.result_cache.set(
            user_id=user_id,
            prompt=prompt,
            opt_in=opt_in_personalization,
            value=state,
        )
        metadata = {
            "cache_hit": False,
            "run_id": run_record.run_id,
            "personalization_applied": profile is not None and opt_in_personalization,
        }
        return state, metadata
