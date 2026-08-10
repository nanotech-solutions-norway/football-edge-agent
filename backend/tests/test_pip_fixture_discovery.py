from datetime import datetime, timezone

import pytest

from scripts.discover_pip_fixture_registration import (
    build_registration_sql_from_documents,
    safe_failure_code,
    team_names_equivalent,
)


NOW = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)


def documents():
    odds = [
        {
            "id": "odds-later",
            "commence_time": "2026-08-16T18:00:00Z",
            "home_team": "Vålerenga",
            "away_team": "Rosenborg",
            "bookmakers": [{"key": "book-a"}],
        },
        {
            "id": "odds-earliest",
            "commence_time": "2026-08-15T18:00:00Z",
            "home_team": "Bodø/Glimt",
            "away_team": "Vålerenga",
            "bookmakers": [{"key": "book-a"}],
        },
    ]
    leagues = {"results": [{"id": 777, "name": "Eliteserien", "country": {"name": "Norway"}}]}
    matches = [
        {
            "league_id": 777,
            "matches": [
                {
                    "id": 531585,
                    "date": "15/08/2026",
                    "teams": {"home": {"name": "Bodø/Glimt"}, "away": {"name": "Vålerenga"}},
                }
            ],
        }
    ]
    return odds, leagues, matches


def test_discovers_earliest_cross_provider_fixture_without_credentials():
    sql = build_registration_sql_from_documents(*documents(), fixture_code="JG8XWK5", now=NOW)
    assert "'JG8XWK5'" in sql
    assert "'bodo-glimt'" in sql
    assert "'valerenga'" in sql
    assert "'odds-api', 'odds-earliest'" in sql
    assert "'soccerdata-api', '531585'" in sql
    assert "2026-08-15 18:00:00.000000" in sql
    assert "apiKey" not in sql
    assert "auth_token" not in sql


def test_discovery_fails_closed_without_cross_provider_match():
    odds, leagues, matches = documents()
    matches[0]["matches"][0]["teams"]["away"]["name"] = "Different Team"
    with pytest.raises(ValueError, match="missing or ambiguous"):
        build_registration_sql_from_documents(odds, leagues, matches, fixture_code="JG8XWK5", now=NOW)


def test_skips_earlier_odds_only_event_and_selects_first_cross_provider_match():
    odds, leagues, matches = documents()
    matches[0]["matches"] = [
        {
            "id": 531586,
            "date": "16/08/2026",
            "teams": {"home": {"name": "Vålerenga"}, "away": {"name": "Rosenborg"}},
        }
    ]

    sql = build_registration_sql_from_documents(odds, leagues, matches, fixture_code="JG8XWK5", now=NOW)

    assert "'odds-api', 'odds-later'" in sql
    assert "'soccerdata-api', '531586'" in sql
    assert "2026-08-16 18:00:00.000000" in sql


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("SK Brann", "Brann"),
        ("Molde FK", "Molde"),
        ("Tromsø IL", "Tromso"),
        ("Sarpsborg 08 FF", "Sarpsborg 08"),
        ("Ham-Kam", "HamKam"),
        ("KFUM", "KFUM Oslo"),
    ],
)
def test_conservative_provider_team_identity_equivalence(left, right):
    assert team_names_equivalent(left, right)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("City", "Manchester City"),
        ("United", "Manchester United"),
        ("Viking", "Vikingur"),
        ("Brann", "Bryne"),
    ],
)
def test_provider_team_identity_rejects_unsafe_containment(left, right):
    assert not team_names_equivalent(left, right)


def test_club_designators_still_require_a_unique_home_away_date_match():
    odds, leagues, matches = documents()
    matches[0]["matches"] = [
        {
            "id": 531585,
            "date": "15/08/2026",
            "teams": {"home": {"name": "Bodø/Glimt FK"}, "away": {"name": "Vålerenga IF"}},
        },
        {
            "id": 531586,
            "date": "15/08/2026",
            "teams": {"home": {"name": "Bodø/Glimt BK"}, "away": {"name": "Vålerenga IL"}},
        },
    ]

    with pytest.raises(ValueError, match="missing or ambiguous"):
        build_registration_sql_from_documents(odds, leagues, matches, fixture_code="JG8XWK5", now=NOW)


def test_adds_unambiguous_optional_sports_game_odds_mapping():
    sports_game_odds = {
        "data": [
            {
                "eventID": "sgo-event",
                "teams": {
                    "home": {"names": {"long": "Bodø/Glimt"}},
                    "away": {"names": {"long": "Vålerenga"}},
                },
            }
        ]
    }
    sql = build_registration_sql_from_documents(
        *documents(),
        fixture_code="JG8XWK5",
        now=NOW,
        sports_game_odds_document=sports_game_odds,
    )
    assert "'sports-game-odds', 'sgo-event'" in sql


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Soccerdata Norway country resolution was missing or ambiguous", "soccerdata_country_resolution"),
        ("Soccerdata Eliteserien league resolution was missing or ambiguous", "soccerdata_league_resolution"),
        ("Soccerdata event match was missing or ambiguous", "soccerdata_event_resolution"),
        ("no upcoming Eliteserien event with odds was available", "odds_event_unavailable"),
        ("protected fixture code is invalid", "fixture_code_invalid"),
    ],
)
def test_safe_failure_codes_do_not_include_provider_payload(message, expected):
    assert safe_failure_code(ValueError(message)) == expected


def test_unknown_provider_failures_use_a_stable_sanitized_code():
    assert safe_failure_code(RuntimeError("sensitive upstream detail")) == "unexpected_provider_response"
