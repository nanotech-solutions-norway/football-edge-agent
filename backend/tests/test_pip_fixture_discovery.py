from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest

import scripts.discover_pip_fixture_registration as discovery_module
from scripts.discover_pip_fixture_registration import (
    FixtureResolutionError,
    _api_sports_league_id,
    _soccerdata_active_season,
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

    with pytest.raises(FixtureResolutionError, match="missing or ambiguous") as captured:
        build_registration_sql_from_documents(odds, leagues, matches, fixture_code="JG8XWK5", now=NOW)
    assert captured.value.metrics == {
        "odds_candidates": 2,
        "soccerdata_events": 2,
        "parseable_dates": 2,
        "date_pairs": 4,
        "home_pairs": 2,
        "full_identity_pairs": 2,
        "ambiguous_candidates": 1,
        "sports_game_odds_available": 0,
        "sports_game_odds_matches": 0,
        "sportsdata_io_available": 0,
        "sportsdata_io_matches": 0,
        "api_sports_available": 0,
        "api_sports_events": 0,
        "api_sports_date_pairs": 0,
        "api_sports_home_pairs": 0,
        "api_sports_full_identity_pairs": 0,
        "api_sports_matches": 0,
    }


def test_resolution_metrics_distinguish_unparseable_provider_dates():
    odds, leagues, matches = documents()
    matches[0]["matches"][0]["date"] = "not-a-date"

    with pytest.raises(FixtureResolutionError) as captured:
        build_registration_sql_from_documents(odds, leagues, matches, fixture_code="JG8XWK5", now=NOW)

    assert captured.value.metrics["soccerdata_events"] == 1
    assert captured.value.metrics["parseable_dates"] == 0
    assert captured.value.metrics["date_pairs"] == 0
    assert captured.value.metrics["home_pairs"] == 0
    assert captured.value.metrics["full_identity_pairs"] == 0


def test_active_soccerdata_season_is_unique_and_optional():
    assert _soccerdata_active_season(
        {"results": [{"year": "2026", "is_active": True}, {"year": "2025", "is_active": False}]}
    ) == "2026"
    assert _soccerdata_active_season({"results": [{"year": "2025", "is_active": False}]}) is None
    with pytest.raises(ValueError, match="active season resolution was ambiguous"):
        _soccerdata_active_season(
            {"results": [{"year": "2026", "is_active": True}, {"year": "2026-2027", "is_active": True}]}
        )


def test_api_sports_league_is_resolved_from_country_catalog_and_requested_season():
    leagues = {
        "response": [
            {
                "league": {"id": 103, "name": "Eliteserien"},
                "country": {"name": "Norway"},
                "seasons": [{"year": 2025}, {"year": 2026}],
            },
            {
                "league": {"id": 104, "name": "1. Division"},
                "country": {"name": "Norway"},
                "seasons": [{"year": 2026}],
            },
        ]
    }

    assert _api_sports_league_id(leagues, 2026) == "103"


def test_discovery_falls_back_to_candidate_dates_when_active_schedule_is_empty(monkeypatch, tmp_path):
    odds, leagues, matches = documents()
    calls: list[str] = []

    def fake_get_json(url, headers=None):
        calls.append(url)
        if "api.the-odds-api.com" in url:
            return odds
        if "/country/" in url:
            return {"results": [{"id": 20, "name": "Norway"}]}
        if "/league/" in url:
            return leagues
        if "/season/" in url:
            return {"results": [{"year": "2026", "is_active": True}]}
        if "/matches/" in url:
            query = parse_qs(urlparse(url).query)
            if "season" in query:
                return []
            return matches if query.get("date") == ["2026-08-15"] else []
        raise AssertionError("unexpected provider URL")

    monkeypatch.setenv("ODDS_API_KEY", "protected-odds-key")
    monkeypatch.setenv("SOCCERDATA_API_KEY", "protected-soccerdata-key")
    monkeypatch.setenv("PIP_VALIDATION_FIXTURE_CODE", "JG8XWK5")
    monkeypatch.delenv("SPORTS_GAME_ODDS_KEY", raising=False)
    monkeypatch.setattr(discovery_module, "_get_json", fake_get_json)
    output = tmp_path / "registration.sql"

    discovery_module.discover(output, now=NOW)

    assert output.exists()
    assert any("/season/" in url for url in calls)
    assert any("season=2026" in url for url in calls)
    assert any("date=2026-08-15" in url for url in calls)
    assert "'odds-api', 'odds-earliest'" in output.read_text(encoding="utf-8")


def test_discovery_falls_back_to_dates_when_season_endpoint_is_unavailable(monkeypatch, tmp_path):
    odds, leagues, matches = documents()

    def fake_get_json(url, headers=None):
        if "api.the-odds-api.com" in url:
            return odds
        if "/country/" in url:
            return {"results": [{"id": 20, "name": "Norway"}]}
        if "/league/" in url:
            return leagues
        if "/season/" in url:
            raise RuntimeError("upstream detail must remain private")
        if "/matches/" in url:
            query = parse_qs(urlparse(url).query)
            return matches if query.get("date") == ["2026-08-15"] else []
        raise AssertionError("unexpected provider URL")

    monkeypatch.setenv("ODDS_API_KEY", "protected-odds-key")
    monkeypatch.setenv("SOCCERDATA_API_KEY", "protected-soccerdata-key")
    monkeypatch.setenv("PIP_VALIDATION_FIXTURE_CODE", "JG8XWK5")
    monkeypatch.delenv("SPORTS_GAME_ODDS_KEY", raising=False)
    monkeypatch.setattr(discovery_module, "_get_json", fake_get_json)
    output = tmp_path / "registration.sql"

    discovery_module.discover(output, now=NOW)

    assert output.exists()
    assert "'soccerdata-api', '531585'" in output.read_text(encoding="utf-8")


def test_discovery_derives_calendar_season_when_season_endpoint_is_unavailable(monkeypatch, tmp_path):
    odds, leagues, matches = documents()
    calls: list[str] = []

    def fake_get_json(url, headers=None):
        calls.append(url)
        if "api.the-odds-api.com" in url:
            return odds
        if "/country/" in url:
            return {"results": [{"id": 20, "name": "Norway"}]}
        if "/league/" in url:
            return leagues
        if "/season/" in url:
            raise RuntimeError("upstream detail must remain private")
        if "/matches/" in url:
            query = parse_qs(urlparse(url).query)
            return matches if query.get("season") == ["2026"] else []
        raise AssertionError("unexpected provider URL")

    monkeypatch.setenv("ODDS_API_KEY", "protected-odds-key")
    monkeypatch.setenv("SOCCERDATA_API_KEY", "protected-soccerdata-key")
    monkeypatch.setenv("PIP_VALIDATION_FIXTURE_CODE", "JG8XWK5")
    monkeypatch.delenv("SPORTS_GAME_ODDS_KEY", raising=False)
    monkeypatch.setattr(discovery_module, "_get_json", fake_get_json)
    output = tmp_path / "registration.sql"

    discovery_module.discover(output, now=NOW)

    assert output.exists()
    assert any("season=2026" in url for url in calls)
    assert not any("date=" in url for url in calls)


def test_date_fallback_continues_after_one_candidate_date_request_fails(monkeypatch, tmp_path):
    odds, leagues, matches = documents()

    def fake_get_json(url, headers=None):
        if "api.the-odds-api.com" in url:
            return odds
        if "/country/" in url:
            return {"results": [{"id": 20, "name": "Norway"}]}
        if "/league/" in url:
            return leagues
        if "/season/" in url:
            raise RuntimeError("upstream detail must remain private")
        if "/matches/" in url:
            query = parse_qs(urlparse(url).query)
            if "season" in query:
                return []
            if query.get("date") == ["2026-08-15"]:
                raise RuntimeError("no matches on candidate date")
            return [
                {
                    "league_id": 777,
                    "matches": [
                        {
                            "id": 531586,
                            "date": "16/08/2026",
                            "teams": {"home": {"name": "Vålerenga"}, "away": {"name": "Rosenborg"}},
                        }
                    ],
                }
            ]
        raise AssertionError("unexpected provider URL")

    monkeypatch.setenv("ODDS_API_KEY", "protected-odds-key")
    monkeypatch.setenv("SOCCERDATA_API_KEY", "protected-soccerdata-key")
    monkeypatch.setenv("PIP_VALIDATION_FIXTURE_CODE", "JG8XWK5")
    monkeypatch.delenv("SPORTS_GAME_ODDS_KEY", raising=False)
    monkeypatch.setattr(discovery_module, "_get_json", fake_get_json)
    output = tmp_path / "registration.sql"

    discovery_module.discover(output, now=NOW)

    assert "'odds-api', 'odds-later'" in output.read_text(encoding="utf-8")


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


def test_sports_game_odds_can_be_the_required_secondary_provider():
    odds, _, _ = documents()
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
        odds,
        None,
        None,
        fixture_code="JG8XWK5",
        now=NOW,
        sports_game_odds_document=sports_game_odds,
    )

    assert "'odds-api', 'odds-earliest'" in sql
    assert "'sports-game-odds', 'sgo-event'" in sql
    assert "'soccerdata-api'" not in sql


def test_sportsdata_io_can_be_the_required_secondary_provider():
    odds, _, _ = documents()
    sportsdata_schedule = [
        {
            "Games": [
                {
                    "GameId": 812345,
                    "DateTime": "2026-08-15T18:00:00",
                    "HomeTeamName": "Bodø/Glimt",
                    "AwayTeamName": "Vålerenga",
                }
            ]
        }
    ]

    sql = build_registration_sql_from_documents(
        odds,
        None,
        None,
        fixture_code="JG8XWK5",
        now=NOW,
        sportsdata_io_document=sportsdata_schedule,
    )

    assert "'odds-api', 'odds-earliest'" in sql
    assert "'sportsdata-io', '812345'" in sql
    assert "'soccerdata-api'" not in sql


def test_sportsdata_io_ambiguous_identity_fails_closed():
    odds, _, _ = documents()
    duplicated_game = {
        "DateTime": "2026-08-15T18:00:00",
        "HomeTeamName": "Bodø/Glimt",
        "AwayTeamName": "Vålerenga",
    }
    sportsdata_schedule = [
        {"Games": [{**duplicated_game, "GameId": 812345}, {**duplicated_game, "GameId": 812346}]}
    ]

    with pytest.raises(FixtureResolutionError):
        build_registration_sql_from_documents(
            odds,
            None,
            None,
            fixture_code="JG8XWK5",
            now=NOW,
            sportsdata_io_document=sportsdata_schedule,
        )


def test_api_sports_can_be_the_required_secondary_provider():
    odds, _, _ = documents()
    api_sports = {
        "response": [
            {
                "fixture": {"id": 991122, "date": "2026-08-15T18:00:00+00:00"},
                "teams": {"home": {"name": "Bodø/Glimt"}, "away": {"name": "Vålerenga"}},
            }
        ]
    }

    sql = build_registration_sql_from_documents(
        odds,
        None,
        None,
        fixture_code="JG8XWK5",
        now=NOW,
        api_sports_document=api_sports,
    )

    assert "'odds-api', 'odds-earliest'" in sql
    assert "'api-sports', '991122'" in sql
    assert "'soccerdata-api'" not in sql


def test_discovery_falls_back_to_api_sports_full_season_schedule(monkeypatch, tmp_path):
    odds, _, _ = documents()
    calls: list[str] = []

    def fake_get_json(url, headers=None):
        calls.append(url)
        if "api.the-odds-api.com" in url:
            return odds
        if "/leagues?" in url:
            return {
                "response": [
                    {
                        "league": {"id": 103, "name": "Eliteserien"},
                        "country": {"name": "Norway"},
                        "seasons": [{"year": 2026}],
                    }
                ]
            }
        if "/fixtures?" in url:
            query = parse_qs(urlparse(url).query)
            if "from" in query:
                return {"response": []}
            return {
                "response": [
                    {
                        "fixture": {"id": 991122, "date": "2026-08-15T18:00:00+00:00"},
                        "teams": {"home": {"name": "Bodø/Glimt"}, "away": {"name": "Vålerenga"}},
                    }
                ]
            }
        raise AssertionError("unexpected provider URL")

    monkeypatch.setenv("ODDS_API_KEY", "protected-odds-key")
    monkeypatch.setenv("API_SPORTS_KEY", "protected-api-sports-key")
    monkeypatch.setenv("PIP_VALIDATION_FIXTURE_CODE", "JG8XWK5")
    for name in ("SOCCERDATA_API_KEY", "SPORTS_GAME_ODDS_KEY", "SPORTSDATA_IO_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(discovery_module, "_get_json", fake_get_json)
    output = tmp_path / "registration.sql"

    discovery_module.discover(output, now=NOW)

    assert any("from=" in url and "to=" in url for url in calls if "/fixtures?" in url)
    assert any("season=2026" in url and "from=" not in url for url in calls if "/fixtures?" in url)
    assert "'api-sports', '991122'" in output.read_text(encoding="utf-8")


def test_discovery_continues_to_sports_game_odds_when_soccerdata_schedule_fails(monkeypatch, tmp_path):
    odds, leagues, _ = documents()

    def fake_get_json(url, headers=None):
        if "api.the-odds-api.com" in url:
            return odds
        if "/country/" in url:
            return {"results": [{"id": 20, "name": "Norway"}]}
        if "/league/" in url:
            return leagues
        if "api.sportsgameodds.com" in url:
            return {
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
        raise RuntimeError("upstream detail must remain private")

    monkeypatch.setenv("ODDS_API_KEY", "protected-odds-key")
    monkeypatch.setenv("SOCCERDATA_API_KEY", "protected-soccerdata-key")
    monkeypatch.setenv("SPORTS_GAME_ODDS_KEY", "protected-sgo-key")
    monkeypatch.setenv("PIP_VALIDATION_FIXTURE_CODE", "JG8XWK5")
    monkeypatch.setattr(discovery_module, "_get_json", fake_get_json)
    output = tmp_path / "registration.sql"

    discovery_module.discover(output, now=NOW)

    rendered = output.read_text(encoding="utf-8")
    assert "'sports-game-odds', 'sgo-event'" in rendered
    assert "'soccerdata-api'" not in rendered


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Soccerdata Norway country resolution was missing or ambiguous", "soccerdata_country_resolution"),
        ("Soccerdata Eliteserien league resolution was missing or ambiguous", "soccerdata_league_resolution"),
        ("Soccerdata event match was missing or ambiguous", "soccerdata_event_resolution"),
        ("secondary provider event match was missing or ambiguous", "secondary_provider_resolution"),
        ("API-Sports authentication or competition access failed", "api_sports_auth_or_access"),
        ("API-Sports request quota was exceeded", "api_sports_quota"),
        ("API-Sports league request failed", "api_sports_league_request"),
        ("API-Sports league response could not resolve Eliteserien", "api_sports_league_resolution"),
        ("API-Sports fixture request failed", "api_sports_fixture_request"),
        ("no upcoming Eliteserien event with odds was available", "odds_event_unavailable"),
        ("protected fixture code is invalid", "fixture_code_invalid"),
    ],
)
def test_safe_failure_codes_do_not_include_provider_payload(message, expected):
    assert safe_failure_code(ValueError(message)) == expected


def test_unknown_provider_failures_use_a_stable_sanitized_code():
    assert safe_failure_code(RuntimeError("sensitive upstream detail")) == "unexpected_provider_response"
