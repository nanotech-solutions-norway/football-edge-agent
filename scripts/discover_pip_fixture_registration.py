#!/usr/bin/env python3
"""Discover and render one protected PIP fixture registration transaction.

Provider credentials are read only from the runner environment. Raw responses,
fixture identifiers, team names, and the generated SQL are never printed.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


FIXTURE_CODE_PATTERN = re.compile(r"^(?=.*[0-9])(?=.*[A-HJ-KM-NP-TV-Z])[0-9A-HJ-KM-NP-TV-Z]{7}$")
CLUB_DESIGNATORS = frozenset({"afc", "bk", "fc", "ff", "fk", "fotball", "fotballklubb", "football", "if", "il", "sk"})

SAFE_FAILURE_CODES = {
    "canonical key normalization failed": "canonical_key_invalid",
    "provider kickoff is missing timezone": "kickoff_invalid",
    "Odds API response must be an array": "odds_response_shape",
    "Soccerdata Eliteserien league resolution was missing or ambiguous": "soccerdata_league_resolution",
    "Soccerdata Norway country resolution was missing or ambiguous": "soccerdata_country_resolution",
    "Soccerdata event match was missing or ambiguous": "soccerdata_event_resolution",
    "Soccerdata active season resolution was ambiguous": "soccerdata_season_resolution",
    "Soccerdata date schedule request failed": "soccerdata_date_schedule_request",
    "secondary provider event match was missing or ambiguous": "secondary_provider_resolution",
    "protected fixture code is invalid": "fixture_code_invalid",
    "no upcoming Eliteserien event with odds was available": "odds_event_unavailable",
    "provider returned non-200 response": "provider_http_status",
    "provider response size gate failed": "provider_response_size",
    "decompressed provider response size gate failed": "provider_decompressed_size",
    "required protected discovery secret is missing": "required_secret_missing",
}


class FixtureResolutionError(ValueError):
    def __init__(self, metrics: dict[str, int]):
        super().__init__("secondary provider event match was missing or ambiguous")
        self.metrics = metrics


def safe_failure_code(error: Exception) -> str:
    """Return a stable diagnostic without exposing provider data or credentials."""
    return SAFE_FAILURE_CODES.get(str(error), "unexpected_provider_response")


def normalize_key(value: str) -> str:
    translated = value.strip().casefold().translate(
        str.maketrans({"æ": "ae", "ø": "o", "å": "a", "ð": "d", "þ": "th"})
    )
    ascii_value = unicodedata.normalize("NFKD", translated).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    if not normalized:
        raise ValueError("canonical key normalization failed")
    return normalized


def _team_identity_tokens(value: str) -> tuple[str, ...]:
    tokens = tuple(token for token in normalize_key(value).split("-") if token not in CLUB_DESIGNATORS)
    return tokens or tuple(normalize_key(value).split("-"))


def _is_acronym_label(value: str) -> bool:
    compact = re.sub(r"[^A-Za-z0-9]", "", value)
    return 3 <= len(compact) <= 8 and compact.isupper()


def team_names_equivalent(left: str, right: str) -> bool:
    left_key = normalize_key(left)
    right_key = normalize_key(right)
    if left_key == right_key or left_key.replace("-", "") == right_key.replace("-", ""):
        return True
    left_tokens = _team_identity_tokens(left)
    right_tokens = _team_identity_tokens(right)
    if left_tokens == right_tokens:
        return True
    if len(left_tokens) == 1 and len(right_tokens) == 2 and left_tokens[0] in right_tokens:
        return _is_acronym_label(left)
    if len(right_tokens) == 1 and len(left_tokens) == 2 and right_tokens[0] in left_tokens:
        return _is_acronym_label(right)
    return False


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("provider kickoff is missing timezone")
    return parsed.astimezone(timezone.utc)


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def canonical_event_key(competition: str, kickoff: datetime, home: str, away: str) -> str:
    identity = "|".join(
        (
            normalize_key(competition),
            kickoff.isoformat().replace("+00:00", "Z"),
            normalize_key(home),
            normalize_key(away),
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _odds_candidates(document: Any, now: datetime) -> list[dict[str, Any]]:
    if not isinstance(document, list):
        raise ValueError("Odds API response must be an array")
    candidates = []
    for event in document:
        if not isinstance(event, dict):
            continue
        kickoff = parse_utc(str(event.get("commence_time", "")))
        if kickoff <= now:
            continue
        if not event.get("bookmakers"):
            continue
        if not all(isinstance(event.get(field), str) and event[field].strip() for field in ("id", "home_team", "away_team")):
            continue
        candidates.append({**event, "_kickoff": kickoff})
    return sorted(candidates, key=lambda event: event["_kickoff"])


def _soccerdata_league_id(document: Any) -> str:
    items = document.get("results", []) if isinstance(document, dict) else []
    matches = []
    for league in items:
        if not isinstance(league, dict):
            continue
        country = league.get("country", {})
        country_name = country.get("name", "") if isinstance(country, dict) else ""
        league_name = str(league.get("name", "")).strip()
        country_name = str(country_name).strip()
        if not league_name or not country_name:
            continue
        if normalize_key(league_name) == "eliteserien" and normalize_key(country_name) == "norway":
            matches.append(str(league.get("id", "")).strip())
    matches = [value for value in matches if value]
    if len(matches) != 1:
        raise ValueError("Soccerdata Eliteserien league resolution was missing or ambiguous")
    return matches[0]


def _soccerdata_country_id(document: Any) -> str:
    items = document.get("results", []) if isinstance(document, dict) else []
    matches = [
        str(country.get("id", "")).strip()
        for country in items
        if isinstance(country, dict)
        and str(country.get("name", "")).strip()
        and normalize_key(str(country["name"])) == "norway"
    ]
    matches = [value for value in matches if value]
    if len(matches) != 1:
        raise ValueError("Soccerdata Norway country resolution was missing or ambiguous")
    return matches[0]


def _soccerdata_active_season(document: Any) -> str | None:
    items = document.get("results", []) if isinstance(document, dict) else []
    active = [
        str(season.get("year", "")).strip()
        for season in items
        if isinstance(season, dict) and season.get("is_active") is True
    ]
    active = list(dict.fromkeys(value for value in active if value))
    if len(active) > 1:
        raise ValueError("Soccerdata active season resolution was ambiguous")
    return active[0] if active else None


def _flatten_soccerdata_matches(document: Any) -> list[dict[str, Any]]:
    if isinstance(document, dict):
        document = document.get("results", document)
    roots = document if isinstance(document, list) else [document]
    flattened: list[dict[str, Any]] = []
    for root in roots:
        if not isinstance(root, dict):
            continue
        nested = root.get("matches")
        if isinstance(nested, list):
            flattened.extend(item for item in nested if isinstance(item, dict))
        elif "id" in root:
            flattened.append(root)
    return flattened


def _merge_soccerdata_match_documents(documents: list[Any]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for document in documents:
        for event in _flatten_soccerdata_matches(document):
            event_id = str(event.get("id", "")).strip()
            if not event_id or event_id in seen_ids:
                continue
            seen_ids.add(event_id)
            merged.append(event)
    return [{"matches": merged}]


def _soccerdata_event_date(event: dict[str, Any]):
    raw_date = str(event.get("date", "")).strip()
    if not raw_date:
        return None
    try:
        return datetime.strptime(raw_date.replace("-", "/"), "%d/%m/%Y").date()
    except ValueError:
        return None


def _soccerdata_candidate_metrics(
    events: list[dict[str, Any]], odds_event: dict[str, Any]
) -> tuple[list[str], dict[str, int]]:
    kickoff_date = odds_event["_kickoff"].date()
    matches: list[str] = []
    metrics = {"date_pairs": 0, "home_pairs": 0, "full_identity_pairs": 0}
    for event in events:
        event_date = _soccerdata_event_date(event)
        if event_date is None or abs((event_date - kickoff_date).days) > 1:
            continue
        metrics["date_pairs"] += 1
        teams = event.get("teams", {})
        if not isinstance(teams, dict):
            continue
        home = teams.get("home", {})
        away = teams.get("away", {})
        if not isinstance(home, dict) or not isinstance(away, dict):
            continue
        home_name = str(home.get("name", "")).strip()
        away_name = str(away.get("name", "")).strip()
        if not home_name or not away_name:
            continue
        if not team_names_equivalent(home_name, odds_event["home_team"]):
            continue
        metrics["home_pairs"] += 1
        if not team_names_equivalent(away_name, odds_event["away_team"]):
            continue
        metrics["full_identity_pairs"] += 1
        event_id = str(event.get("id", "")).strip()
        if event_id:
            matches.append(event_id)
    return list(dict.fromkeys(matches)), metrics


def _match_soccerdata_event(document: Any, odds_event: dict[str, Any]) -> str:
    matches, _ = _soccerdata_candidate_metrics(_flatten_soccerdata_matches(document), odds_event)
    if len(matches) != 1:
        raise ValueError("Soccerdata event match was missing or ambiguous")
    return matches[0]


def _optional_sports_game_odds_event(document: Any, odds_event: dict[str, Any]) -> str | None:
    items = document.get("data", []) if isinstance(document, dict) else []
    matches: list[str] = []
    for event in items:
        if not isinstance(event, dict):
            continue
        teams = event.get("teams", {})
        if not isinstance(teams, dict):
            continue
        home = teams.get("home", {})
        away = teams.get("away", {})
        if not isinstance(home, dict) or not isinstance(away, dict):
            continue
        home_names = home.get("names", {})
        away_names = away.get("names", {})
        if not isinstance(home_names, dict) or not isinstance(away_names, dict):
            continue
        home_candidates = {
            str(name)
            for name in home_names.values()
            if isinstance(name, str) and name.strip()
        }
        away_candidates = {
            str(name)
            for name in away_names.values()
            if isinstance(name, str) and name.strip()
        }
        event_id = str(event.get("eventID", "")).strip()
        home_match = any(team_names_equivalent(name, odds_event["home_team"]) for name in home_candidates)
        away_match = any(team_names_equivalent(name, odds_event["away_team"]) for name in away_candidates)
        if home_match and away_match and event_id:
            matches.append(event_id)
    unique = list(dict.fromkeys(matches))
    return unique[0] if len(unique) == 1 else None


def build_registration_sql_from_documents(
    odds_document: Any,
    soccerdata_leagues: Any | None,
    soccerdata_matches: Any | None,
    *,
    fixture_code: str,
    now: datetime,
    sports_game_odds_document: Any | None = None,
) -> str:
    if FIXTURE_CODE_PATTERN.fullmatch(fixture_code) is None:
        raise ValueError("protected fixture code is invalid")
    candidates = _odds_candidates(odds_document, now)
    if not candidates:
        raise ValueError("no upcoming Eliteserien event with odds was available")
    soccerdata_available = soccerdata_leagues is not None and soccerdata_matches is not None
    if soccerdata_available:
        _soccerdata_league_id(soccerdata_leagues)
    soccerdata_events = _flatten_soccerdata_matches(soccerdata_matches) if soccerdata_available else []
    resolution_metrics = {
        "odds_candidates": len(candidates),
        "soccerdata_events": len(soccerdata_events),
        "parseable_dates": sum(_soccerdata_event_date(event) is not None for event in soccerdata_events),
        "date_pairs": 0,
        "home_pairs": 0,
        "full_identity_pairs": 0,
        "ambiguous_candidates": 0,
        "sports_game_odds_available": int(sports_game_odds_document is not None),
        "sports_game_odds_matches": 0,
    }
    matched_fixture: tuple[dict[str, Any], list[tuple[str, str]]] | None = None
    for candidate in candidates:
        provider_mappings: list[tuple[str, str]] = []
        matches, candidate_metrics = _soccerdata_candidate_metrics(soccerdata_events, candidate)
        for key in ("date_pairs", "home_pairs", "full_identity_pairs"):
            resolution_metrics[key] += candidate_metrics[key]
        if len(matches) > 1:
            resolution_metrics["ambiguous_candidates"] += 1
        elif len(matches) == 1:
            provider_mappings.append(("soccerdata-api", matches[0]))
        sports_game_odds_event_id = (
            _optional_sports_game_odds_event(sports_game_odds_document, candidate)
            if sports_game_odds_document is not None
            else None
        )
        if sports_game_odds_event_id is not None:
            resolution_metrics["sports_game_odds_matches"] += 1
            provider_mappings.append(("sports-game-odds", sports_game_odds_event_id))
        if not provider_mappings:
            continue
        matched_fixture = (candidate, provider_mappings)
        break
    if matched_fixture is None:
        raise FixtureResolutionError(resolution_metrics)
    odds_event, secondary_provider_mappings = matched_fixture

    competition = "nor-eliteserien"
    kickoff = odds_event["_kickoff"]
    home = normalize_key(odds_event["home_team"])
    away = normalize_key(odds_event["away_team"])
    event_key = canonical_event_key(competition, kickoff, home, away)
    kickoff_sql = kickoff.strftime("%Y-%m-%d %H:%M:%S.%f")
    lines = [
        "-- Protected automatic discovery from at least two authenticated providers.",
        "START TRANSACTION;",
        "INSERT INTO pip_fixtures (",
        "    fixture_code, canonical_event_key, competition_key, kickoff_at,",
        "    home_team_key, away_team_key, status",
        ") VALUES (",
        f"    {sql_literal(fixture_code)}, {sql_literal(event_key)}, {sql_literal(competition)},",
        f"    {sql_literal(kickoff_sql)}, {sql_literal(home)}, {sql_literal(away)}, 'scheduled'",
        ");",
        "SET @pip_fixture_id = LAST_INSERT_ID();",
        "INSERT INTO pip_provider_fixture_mappings (provider, provider_fixture_id, fixture_id, provider_updated_at)",
        f"VALUES ('odds-api', {sql_literal(str(odds_event['id']))}, @pip_fixture_id, NULL);",
    ]
    for provider, provider_fixture_id in secondary_provider_mappings:
        lines.extend(
            [
                "INSERT INTO pip_provider_fixture_mappings (provider, provider_fixture_id, fixture_id, provider_updated_at)",
                f"VALUES ({sql_literal(provider)}, {sql_literal(provider_fixture_id)}, @pip_fixture_id, NULL);",
            ]
        )
    lines.extend(
        [
        "SELECT fixture_id, fixture_code, competition_key, kickoff_at, home_team_key, away_team_key",
        "FROM pip_fixtures WHERE fixture_id = @pip_fixture_id;",
        "SELECT provider, provider_fixture_id FROM pip_provider_fixture_mappings",
        "WHERE fixture_id = @pip_fixture_id ORDER BY provider;",
        "COMMIT;",
        ]
    )
    return "\n".join(lines) + "\n"


def _get_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request = urllib.request.Request(url, headers=headers or {"Accept": "application/json"}, method="GET")
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError("provider returned non-200 response")
        body = response.read(5_000_001)
        if not body or len(body) > 5_000_000:
            raise ValueError("provider response size gate failed")
        if response.headers.get("Content-Encoding", "").lower() == "gzip":
            body = gzip.decompress(body)
            if len(body) > 5_000_000:
                raise ValueError("decompressed provider response size gate failed")
        return json.loads(body.decode("utf-8"))


def discover(output: Path, *, now: datetime | None = None) -> None:
    odds_key = os.environ.get("ODDS_API_KEY", "")
    soccerdata_key = os.environ.get("SOCCERDATA_API_KEY", "")
    sports_game_odds_key = os.environ.get("SPORTS_GAME_ODDS_KEY", "")
    fixture_code = os.environ.get("PIP_VALIDATION_FIXTURE_CODE", "")
    if not odds_key or not fixture_code or not (soccerdata_key or sports_game_odds_key):
        raise ValueError("required protected discovery secret is missing")
    reference_time = now or datetime.now(timezone.utc)

    odds_query = urllib.parse.urlencode(
        {"apiKey": odds_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal", "dateFormat": "iso"}
    )
    odds_document = _get_json(
        f"https://api.the-odds-api.com/v4/sports/soccer_norway_eliteserien/odds?{odds_query}"
    )
    odds_candidates = _odds_candidates(odds_document, reference_time)
    soccerdata_leagues = None
    soccerdata_matches = None
    if soccerdata_key:
        try:
            soccer_headers = {"Accept": "application/json", "Accept-Encoding": "gzip"}
            country_query = urllib.parse.urlencode({"auth_token": soccerdata_key})
            soccerdata_countries = _get_json(f"https://api.soccerdataapi.com/country/?{country_query}", soccer_headers)
            country_id = _soccerdata_country_id(soccerdata_countries)
            league_query = urllib.parse.urlencode({"country_id": country_id, "auth_token": soccerdata_key})
            soccerdata_leagues = _get_json(f"https://api.soccerdataapi.com/league/?{league_query}", soccer_headers)
            league_id = _soccerdata_league_id(soccerdata_leagues)
            season_query = urllib.parse.urlencode({"league_id": league_id, "auth_token": soccerdata_key})
            try:
                soccerdata_seasons = _get_json(f"https://api.soccerdataapi.com/season/?{season_query}", soccer_headers)
                active_season = _soccerdata_active_season(soccerdata_seasons)
            except Exception:
                active_season = None
            match_documents: list[Any] = []
            candidate_seasons = [active_season] if active_season else sorted(
                {str(event["_kickoff"].year) for event in odds_candidates}
            )[:2]
            for candidate_season in candidate_seasons:
                matches_query = urllib.parse.urlencode(
                    {"league_id": league_id, "season": candidate_season, "auth_token": soccerdata_key}
                )
                try:
                    match_documents.append(
                        _get_json(f"https://api.soccerdataapi.com/matches/?{matches_query}", soccer_headers)
                    )
                except Exception:
                    continue
            if not _merge_soccerdata_match_documents(match_documents)[0]["matches"]:
                candidate_dates = sorted({event["_kickoff"].date().isoformat() for event in odds_candidates})[:14]
                for candidate_date in candidate_dates:
                    date_query = urllib.parse.urlencode(
                        {"league_id": league_id, "date": candidate_date, "auth_token": soccerdata_key}
                    )
                    try:
                        match_documents.append(
                            _get_json(f"https://api.soccerdataapi.com/matches/?{date_query}", soccer_headers)
                        )
                    except Exception:
                        continue
            soccerdata_matches = _merge_soccerdata_match_documents(match_documents)
        except Exception:
            soccerdata_leagues = None
            soccerdata_matches = None

    sports_game_odds_document = None
    if sports_game_odds_key:
        optional_query = urllib.parse.urlencode(
            {
                "sportID": "SOCCER",
                "oddsAvailable": "true",
                "startsAfter": reference_time.isoformat().replace("+00:00", "Z"),
                "startsBefore": (max(event["_kickoff"] for event in odds_candidates) + timedelta(days=2))
                .isoformat()
                .replace("+00:00", "Z"),
                "limit": "100",
            }
        )
        try:
            sports_game_odds_document = _get_json(
                f"https://api.sportsgameodds.com/v2/events?{optional_query}",
                {"Accept": "application/json", "x-api-key": sports_game_odds_key},
            )
        except Exception:
            sports_game_odds_document = None

    rendered = build_registration_sql_from_documents(
        odds_document,
        soccerdata_leagues,
        soccerdata_matches,
        fixture_code=fixture_code,
        now=reference_time,
        sports_game_odds_document=sports_game_odds_document,
    )
    output.write_text(rendered, encoding="utf-8")
    output.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        discover(args.output)
    except Exception as error:
        print(f"discovery_status=review error_code={safe_failure_code(error)}")
        if isinstance(error, FixtureResolutionError):
            metric_order = (
                "odds_candidates",
                "soccerdata_events",
                "parseable_dates",
                "date_pairs",
                "home_pairs",
                "full_identity_pairs",
                "ambiguous_candidates",
                "sports_game_odds_available",
                "sports_game_odds_matches",
            )
            print("resolution_counts=" + ",".join(f"{key}:{error.metrics.get(key, 0)}" for key in metric_order))
        print("credentials_logged=false payload_logged=false provider_ids_logged=false")
        return 2
    print("discovery_status=pass required_providers_matched=2 optional_provider_match_evaluated=true")
    print("credentials_logged=false payload_logged=false provider_ids_logged=false")
    print("fixture_code_logged=false sql_logged=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
