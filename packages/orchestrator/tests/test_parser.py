"""Phase 1 parser tests using canonical sample requests."""

from __future__ import annotations

from orchestrator.parser import parse_trip_request


def test_parser_japan_request_matches_expected_constraints() -> None:
    request = (
        "Plan a 5-day trip to Japan. Tokyo + Kyoto. "
        "$3,000 budget. Love food and temples, hate crowds."
    )
    trip = parse_trip_request(request)
    assert trip.destination_country == "Japan"
    assert trip.cities == ["Tokyo", "Kyoto"]
    assert trip.duration_days == 5
    assert trip.budget_usd == 3000
    assert trip.preferences == ["food", "temples"]
    assert trip.avoidances == ["crowds"]


def test_parser_italy_request() -> None:
    request = "Plan a 6-day trip to Italy. Rome + Florence. $2,500 budget. Love history and food."
    trip = parse_trip_request(request)
    assert trip.destination_country == "Italy"
    assert trip.cities == ["Rome", "Florence"]
    assert trip.duration_days == 6
    assert trip.budget_usd == 2500
    assert "history" in trip.preferences


def test_parser_thailand_request() -> None:
    request = "Plan a 7 day Thailand trip: Bangkok + Chiang Mai, 2200 USD, love food and nature."
    trip = parse_trip_request(request)
    assert trip.destination_country == "Thailand"
    assert trip.cities == ["Bangkok", "Chiang Mai"]
    assert trip.duration_days == 7
    assert trip.budget_usd == 2200


def test_parser_new_york_request() -> None:
    request = "Plan a 4-day trip to New York, budget 1800 dollars, love museums, hate crowds."
    trip = parse_trip_request(request)
    assert "New York" in trip.cities
    assert trip.duration_days == 4
    assert trip.budget_usd == 1800
    assert "museums" in trip.preferences
    assert "crowds" in trip.avoidances


def test_parser_paris_request() -> None:
    request = "Plan 3-day Paris getaway, $1500 budget, love food and museums."
    trip = parse_trip_request(request)
    assert trip.destination_country == "France"
    assert "Paris" in trip.cities
    assert trip.duration_days == 3
    assert trip.budget_usd == 1500


def test_parser_handles_non_predefined_country_and_cities() -> None:
    request = (
        "Plan a 6-day trip to Spain. Barcelona + Madrid. "
        "2500 USD budget. Love food and museums."
    )
    trip = parse_trip_request(request)
    assert trip.destination_country == "Spain"
    assert trip.cities == ["Barcelona", "Madrid"]
    assert trip.duration_days == 6
    assert trip.budget_usd == 2500
