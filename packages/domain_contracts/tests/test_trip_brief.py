"""TripBrief schema edge-case tests."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from domain_contracts import TripBrief


def test_trip_brief_rejects_past_start_date() -> None:
    with pytest.raises(ValueError, match="start_date cannot be in the past"):
        TripBrief(
            destination_country="Japan",
            cities=["Tokyo"],
            duration_days=5,
            budget_usd=3000,
            start_date=date.today() - timedelta(days=1),
        )


def test_trip_brief_accepts_today_start_date() -> None:
    trip = TripBrief(
        destination_country="Japan",
        cities=["Tokyo"],
        duration_days=5,
        budget_usd=3000,
        start_date=date.today(),
    )
    assert trip.start_date == date.today()
