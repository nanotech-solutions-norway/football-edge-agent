from datetime import datetime, timezone

import pytest

from scripts.discover_pip_fixture_registration import build_registration_sql_from_documents


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
