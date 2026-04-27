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
    def __init__(self, name: str, configured: bool, capability: ProviderCapability):
        self.name = name
        self.configured = configured
        self.capability = capability

    async def health_check(self) -> dict:
        return {
            "provider": self.name,
            "configured": self.configured,
            "status": "configured" if self.configured else "missing_api_key",
            "capabilities": self.capability.__dict__,
        }


def get_provider_clients() -> dict[str, ProviderClient]:
    settings = get_settings()
    return {
        "api_football": ProviderClient(
            "api_football",
            settings.api_football_key != "replace_with_api_key",
            ProviderCapability("api_football", True, True, False, False, False, True, True, True, "candidate"),
        ),
        "odds_api": ProviderClient(
            "odds_api",
            settings.odds_api_key != "replace_with_api_key",
            ProviderCapability("odds_api", False, False, True, True, False, False, False, True, "candidate"),
        ),
        "sportmonks": ProviderClient(
            "sportmonks",
            settings.sportmonks_key != "replace_with_api_key",
            ProviderCapability("sportmonks", True, True, True, True, True, True, True, True, "candidate"),
        ),
        "statsbomb": ProviderClient(
            "statsbomb",
            settings.statsbomb_key != "replace_if_available",
            ProviderCapability("statsbomb", True, True, False, False, True, False, False, True, "xg_candidate"),
        ),
    }
