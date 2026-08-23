from dataclasses import dataclass

from backend.app.config import get_settings


@dataclass(frozen=True)
class ProviderCapability:
    name: str
    fixtures: bool
    results: bool
    current_odds: bool
    historical_odds: bool
    xg: bool
    lineups: bool
    injuries_suspensions: bool
    audit_trail: bool
    status: str


class ProviderClient:
    def __init__(self, name: str, configured: bool, capability: ProviderCapability, *, enabled: bool = True):
        self.name = name
        self.configured = configured
        self.capability = capability
        self.enabled = enabled

    async def health_check(self) -> dict:
        return {
            "provider": self.name,
            "configured": self.configured,
            "status": "disabled_policy" if not self.enabled else ("configured" if self.configured else "missing_api_key"),
            "capabilities": self.capability.__dict__,
        }


def get_provider_clients() -> dict[str, ProviderClient]:
    settings = get_settings()
    return {
        "api_football": ProviderClient(
            "api_football",
            settings.api_football_enabled and settings.api_football_key != "replace_with_api_key",
            ProviderCapability(
                "api_football", True, True, True, False, False, True, True, True, "disabled_current_tier"
            ),
            enabled=settings.api_football_enabled,
        ),
        "odds_api": ProviderClient(
            "odds_api",
            settings.odds_api_key != "replace_with_api_key",
            ProviderCapability("odds_api", False, False, True, True, False, False, False, True, "candidate"),
        ),
        "sportsdata_io": ProviderClient(
            "sportsdata_io",
            settings.sportsdata_io_enabled and settings.sportsdata_io_key != "replace_with_api_key",
            ProviderCapability(
                "sportsdata_io", True, True, True, True, False, True, True, True, "disabled_current_tier"
            ),
            enabled=settings.sportsdata_io_enabled,
        ),
        "soccerdata_api": ProviderClient(
            "soccerdata_api",
            settings.soccerdata_api_key != "replace_with_api_key",
            ProviderCapability("soccerdata_api", True, True, True, False, False, True, True, True, "candidate"),
        ),
        "sports_game_odds": ProviderClient(
            "sports_game_odds",
            settings.sports_game_odds_enabled and settings.sports_game_odds_key != "replace_with_api_key",
            ProviderCapability(
                "sports_game_odds", True, True, True, False, False, True, False, True, "disabled_by_policy"
            ),
            enabled=settings.sports_game_odds_enabled,
        ),
        "sharpapi": ProviderClient(
            "sharpapi",
            settings.sharpapi_key != "replace_with_api_key",
            ProviderCapability("sharpapi", True, False, True, False, False, False, False, True, "candidate"),
        ),
        "statsbomb": ProviderClient(
            "statsbomb",
            settings.statsbomb_key != "replace_if_available",
            ProviderCapability("statsbomb", True, True, False, False, True, False, False, True, "xg_candidate"),
        ),
    }
