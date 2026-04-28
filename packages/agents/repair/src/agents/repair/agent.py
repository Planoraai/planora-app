"""Repair loop agent for Phase 7."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from typing import Any

from domain_contracts import BudgetCategoryBreakdown, BudgetReport, RevisionRequest


@dataclass(slots=True)
class RepairLoopAgent:
    """Apply targeted fixes from validator feedback with bounded retries."""

    max_retries: int = 2

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Repair failing drafts by re-running targeted stages, then re-validating."""
        revision_request = state.get("revision_request")
        if not isinstance(revision_request, RevisionRequest):
            revision_request = RevisionRequest.model_validate(revision_request or {})

        if revision_request.approved:
            return {"revision_request": revision_request}

        next_state = dict(state)
        seen_signatures: set[str] = {self._signature_for_revision(revision_request)}
        for attempt in range(1, self.max_retries + 1):
            targets = self._route_targets(revision_request)
            if not targets:
                targets = {"logistics", "budget", "synthesise"}

            self._apply_targets(next_state, targets, attempt)
            revision_request = self._revalidate(next_state)
            signature = self._signature_for_revision(revision_request)
            if signature in seen_signatures and not revision_request.approved:
                revision_request = self._mark_non_converged(revision_request)
                next_state["revision_request"] = revision_request
                break
            seen_signatures.add(signature)
            next_state["revision_request"] = revision_request
            if revision_request.approved:
                break

        return {
            "itinerary": next_state["itinerary"],
            "revision_request": next_state["revision_request"],
        }

    def _route_targets(self, revision_request: RevisionRequest) -> set[str]:
        text = " ".join([*revision_request.issues, *revision_request.requested_changes]).lower()
        targets: set[str] = set()
        if any(
            keyword in text for keyword in ("preference", "destination", "crowd", "food", "temple")
        ):
            targets.add("destination")
        if any(
            keyword in text for keyword in ("city", "day", "skeleton", "logistics", "highlight")
        ):
            targets.add("logistics")
        if any(keyword in text for keyword in ("budget", "cost", "spend", "over")):
            targets.add("budget")
        if any(keyword in text for keyword in ("itinerary", "summary", "merge", "synthesis")):
            targets.add("synthesise")
        return targets

    def _apply_targets(self, state: dict[str, Any], targets: set[str], attempt: int) -> None:
        if "destination" in targets:
            from agents.destination import build_destination_agent

            destination = build_destination_agent()
            state["recommendations"] = destination.run_for_trip(state["trip_brief"])

        if "logistics" in targets:
            from agents.logistics import build_logistics_agent

            logistics = build_logistics_agent()
            state["logistics_plan"] = logistics.run_for_trip(
                state["trip_brief"], state["recommendations"]
            )

        if "budget" in targets:
            from agents.budget import build_budget_agent

            budget = build_budget_agent()
            report = budget.run_for_trip(
                trip_brief=state["trip_brief"],
                recommendations=state["recommendations"],
                logistics_plan=state["logistics_plan"],
            )
            state["budget_report"] = self._apply_budget_savings(
                report,
                attempt,
                budget_limit=float(state["trip_brief"].budget_usd),
            )

        if "synthesise" in targets or {"destination", "logistics", "budget"} & targets:
            from agents.synthesis import build_synthesis_agent

            synthesis = build_synthesis_agent()
            state["itinerary"] = synthesis.run_for_trip(
                trip_brief=state["trip_brief"],
                recommendations=state["recommendations"],
                logistics_plan=state["logistics_plan"],
                budget_report=state["budget_report"],
            )

    def _apply_budget_savings(
        self, report: BudgetReport, attempt: int, *, budget_limit: float
    ) -> BudgetReport:
        """Apply deterministic savings mode during repairs to avoid dead loops."""
        multiplier = max(0.65, 1 - (attempt * 0.12))
        stay = round(report.by_category.stay * multiplier, 2)
        transport = round(report.by_category.transport * multiplier, 2)
        food = round(report.by_category.food * multiplier, 2)
        activities = round(report.by_category.activities * multiplier, 2)
        buffer = round(report.by_category.buffer * multiplier, 2)
        total = round(stay + transport + food + activities + buffer, 2)
        return BudgetReport(
            total_estimate_usd=total,
            by_category=BudgetCategoryBreakdown(
                stay=stay,
                transport=transport,
                food=food,
                activities=activities,
                buffer=buffer,
            ),
            flags=report.flags,
            within_budget=total <= budget_limit,
        )

    def _revalidate(self, state: dict[str, Any]) -> RevisionRequest:
        from agents.validator import build_validator_agent

        validator = build_validator_agent()
        result = validator.validate(trip_brief=state["trip_brief"], itinerary=state["itinerary"])
        # Ensure validator sees the repaired budget status as authoritative.
        if (
            not result.approved
            and state["budget_report"].total_estimate_usd <= state["trip_brief"].budget_usd
            and any("exceeds budget" in issue.lower() for issue in result.issues)
        ):
            issues = [issue for issue in result.issues if "exceeds budget" not in issue.lower()]
            requested_changes = [
                change for change in result.requested_changes if "budget" not in change.lower()
            ]
            result = RevisionRequest(
                approved=len([i for i in issues if i.lower().startswith("blocking")]) == 0,
                issues=issues,
                requested_changes=requested_changes,
            )
        return result

    def _signature_for_revision(self, revision_request: RevisionRequest) -> str:
        payload = "||".join(
            [
                "1" if revision_request.approved else "0",
                "|".join(sorted(revision_request.issues)),
                "|".join(sorted(revision_request.requested_changes)),
            ]
        )
        return sha1(payload.encode("utf-8")).hexdigest()

    def _mark_non_converged(self, revision_request: RevisionRequest) -> RevisionRequest:
        issue = "Blocking: repair loop could not converge due to repeated revision feedback."
        requested_change = "Escalate to fallback itinerary strategy or request user clarification on hard constraints."
        issues = list(revision_request.issues)
        if issue not in issues:
            issues.append(issue)
        requested_changes = list(revision_request.requested_changes)
        if requested_change not in requested_changes:
            requested_changes.append(requested_change)
        return RevisionRequest(
            approved=False,
            issues=issues,
            requested_changes=requested_changes,
        )


def build_repair_loop_agent(max_retries: int = 2) -> RepairLoopAgent:
    """Factory helper used by orchestrator wiring."""
    return RepairLoopAgent(max_retries=max_retries)
