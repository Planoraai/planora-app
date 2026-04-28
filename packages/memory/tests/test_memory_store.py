"""Phase 9 memory and personalization tests."""

from __future__ import annotations

from unittest.mock import patch

from memory import MemoryAwarePlanner
from memory.store import InMemoryPlannerResultCache, apply_profile_to_prompt
from orchestrator.graph import run_orchestrator


def test_profile_enrichment_appends_known_preferences() -> None:
    planner = MemoryAwarePlanner(runner=run_orchestrator)
    # seed profile by running once with explicit preferences
    planner.run(
        prompt="Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget. Love food and temples.",
        user_id="user-a",
        opt_in_personalization=True,
    )
    profile = planner.preference_store.get("user-a")
    assert profile is not None
    enriched = apply_profile_to_prompt(
        prompt="Plan another 5-day trip to Japan. Tokyo + Kyoto. $3000 budget.",
        profile=profile,
        opt_in=True,
    )
    assert "Known preferences" in enriched
    assert "food" in enriched


def test_cache_hits_on_repeated_prompt_for_same_user() -> None:
    calls = {"count": 0}

    def fake_runner(prompt: str):
        calls["count"] += 1
        return run_orchestrator(prompt)

    planner = MemoryAwarePlanner(runner=fake_runner)
    planner.run(
        prompt="Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget. Love food and temples.",
        user_id="user-cache",
    )
    _, metadata = planner.run(
        prompt="Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget. Love food and temples.",
        user_id="user-cache",
    )
    assert calls["count"] == 1
    assert metadata["cache_hit"] is True


def test_second_run_reuses_learned_preferences_when_opted_in() -> None:
    planner = MemoryAwarePlanner(runner=run_orchestrator)
    planner.run(
        prompt="Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget. Love food and temples.",
        user_id="user-memory",
        opt_in_personalization=True,
    )
    state, _ = planner.run(
        prompt="Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget.",
        user_id="user-memory",
        opt_in_personalization=True,
    )
    assert "food" in state["trip_brief"].preferences


def test_cache_entry_expires_after_ttl() -> None:
    cache = InMemoryPlannerResultCache(ttl_seconds=1.0, max_entries=10)
    state = run_orchestrator("Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget.")
    with patch("memory.store.time", return_value=100.0):
        cache.set(user_id="user-ttl", prompt="same prompt", opt_in=True, value=state)
    with patch("memory.store.time", return_value=100.5):
        assert cache.get(user_id="user-ttl", prompt="same prompt", opt_in=True) is not None
    with patch("memory.store.time", return_value=101.5):
        assert cache.get(user_id="user-ttl", prompt="same prompt", opt_in=True) is None


def test_cache_evicts_oldest_entry_when_capacity_exceeded() -> None:
    cache = InMemoryPlannerResultCache(ttl_seconds=100.0, max_entries=1)
    first_state = run_orchestrator("Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget.")
    second_state = run_orchestrator("Plan a 6-day trip to Italy. Rome + Florence. $2500 budget.")
    cache.set(user_id="user-cap", prompt="first", opt_in=True, value=first_state)
    cache.set(user_id="user-cap", prompt="second", opt_in=True, value=second_state)
    assert cache.get(user_id="user-cap", prompt="first", opt_in=True) is None
    assert cache.get(user_id="user-cap", prompt="second", opt_in=True) is not None
