"""Validator / critic agent implementation for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain_contracts import Itinerary, RevisionRequest, TripBrief


@dataclass(slots=True)
class ItineraryValidatorAgent:
    """Two-layer itinerary validator (programmatic + rubric heuristics)."""

    strict_mode: bool = True

    def validate(self, trip_brief: TripBrief, itinerary: Itinerary) -> RevisionRequest:
        """Return a structured revision request with blocking/advisory items."""
        blocking_issues = self._programmatic_checks(trip_brief, itinerary)
        advisory_issues = self._quality_rubric_checks(trip_brief, itinerary)

        approved = len(blocking_issues) == 0
        requested_changes = self._build_requested_changes(blocking_issues, advisory_issues)
        issues = [*blocking_issues, *advisory_issues]
        return RevisionRequest(
            approved=approved,
            issues=issues,
            requested_changes=requested_changes,
        )

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Phase-compatible async wrapper used by orchestrator graph."""
        trip_brief = state["trip_brief"]
        itinerary = state["itinerary"]
        if not isinstance(trip_brief, TripBrief):
            trip_brief = TripBrief.model_validate(trip_brief)
        if not isinstance(itinerary, Itinerary):
            itinerary = Itinerary.model_validate(itinerary)
        return {"revision_request": self.validate(trip_brief=trip_brief, itinerary=itinerary)}

    def _programmatic_checks(self, trip_brief: TripBrief, itinerary: Itinerary) -> list[str]:
        issues: list[str] = []
        day_count = len(itinerary.day_by_day)
        if day_count != trip_brief.duration_days:
            issues.append(
                f"Blocking: day count mismatch (expected {trip_brief.duration_days}, got {day_count})."
            )

        itinerary_cities = {day.city for day in itinerary.day_by_day}
        missing_cities = [city for city in trip_brief.cities if city not in itinerary_cities]
        if missing_cities:
            issues.append(
                f"Blocking: missing required cities in plan: {', '.join(missing_cities)}."
            )

        if not itinerary.budget_report.within_budget:
            issues.append(
                "Blocking: total estimated spend exceeds budget "
                f"({itinerary.budget_report.total_estimate_usd:.2f} > {trip_brief.budget_usd:.2f})."
            )

        if not itinerary.day_by_day:
            issues.append("Blocking: itinerary has no day-by-day structure.")
            return issues

        empty_highlight_days = [str(day.day) for day in itinerary.day_by_day if not day.highlights]
        if empty_highlight_days:
            issues.append(
                "Blocking: one or more days have no highlights "
                f"(days: {', '.join(empty_highlight_days)})."
            )
        return issues

    def _quality_rubric_checks(self, trip_brief: TripBrief, itinerary: Itinerary) -> list[str]:
        issues: list[str] = []
        corpus = " ".join(
            [day.summary for day in itinerary.day_by_day]
            + [highlight for day in itinerary.day_by_day for highlight in day.highlights]
        ).lower()

        for preference in trip_brief.preferences:
            if preference not in corpus:
                issues.append(
                    f"Advisory: preference '{preference}' is weakly represented in the narrative."
                )

        if any("crowd" in tag for tag in trip_brief.avoidances):
            low_crowd_signal = (
                ("quiet" in corpus) or ("calm" in corpus) or ("less touristy" in corpus)
            )
            if not low_crowd_signal:
                issues.append("Advisory: crowd-avoidance intent is not explicit in activities.")

        if any("travel" in day.summary.lower() for day in itinerary.day_by_day):
            issues.append("Advisory: summaries are transport-heavy; rebalance toward experiences.")

        return issues

    def _build_requested_changes(
        self,
        blocking_issues: list[str],
        advisory_issues: list[str],
    ) -> list[str]:
        changes: list[str] = []
        for issue in blocking_issues:
            if "day count mismatch" in issue:
                changes.append("Regenerate day_skeleton to exactly match TripBrief.duration_days.")
            elif "missing required cities" in issue:
                changes.append("Re-run logistics allocation to include all required cities.")
            elif "exceeds budget" in issue:
                changes.append("Re-run budget + synthesis with lower-cost alternatives.")
            elif "no highlights" in issue:
                changes.append("Populate each itinerary day with at least 2 concrete highlights.")

        if self.strict_mode:
            for issue in advisory_issues:
                if "weakly represented" in issue:
                    changes.append(
                        "Increase coverage of missing preference in destination/logistics output."
                    )
                elif "crowd-avoidance" in issue:
                    changes.append("Prefer low-crowd neighborhoods and early-slot attractions.")

        # Stable unique order
        seen: set[str] = set()
        deduped: list[str] = []
        for change in changes:
            if change in seen:
                continue
            seen.add(change)
            deduped.append(change)
        return deduped


def build_validator_agent() -> ItineraryValidatorAgent:
    """Factory helper used by orchestrator wiring."""
    return ItineraryValidatorAgent()
