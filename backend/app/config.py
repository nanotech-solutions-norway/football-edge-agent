from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "Football Edge Agent Backend"
    app_env: str = "development"
    app_version: str = "0.2.0"
    timezone: str = "Europe/Oslo"
    api_base_url: str = "http://localhost:8000"
    public_backend_domain: str = "api.your-domain.no"
    public_backend_url: str = "https://api.your-domain.no"
    domain_registrar: str = "domeneshop.no"

    internal_api_key: str = "replace_with_secure_internal_key"
    gpt_action_api_key: str = "replace_with_future_gpt_action_key"

    database_url: str = "postgresql://football_edge_user:replace_with_password@db:5432/football_edge"

    auto_betting_enabled: bool = False
    auto_betting_hard_lock: bool = True
    auto_betting_provider: str = "none"
    auto_betting_dry_run: bool = True
    auto_betting_require_legal_review: bool = True
    auto_betting_require_compliance_review: bool = True
    auto_betting_require_risk_review: bool = True

    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_key: str = "replace_with_api_key"
    odds_api_base_url: str = "https://api.the-odds-api.com"
    odds_api_key: str = "replace_with_api_key"
    sportsdata_io_base_url: str = "https://api.sportsdata.io/v4/soccer"
    sportsdata_io_key: str = "replace_with_api_key"
    soccerdata_api_base_url: str = "https://api.soccerdataapi.com"
    soccerdata_api_key: str = "replace_with_api_key"
    sports_game_odds_base_url: str = "https://api.sportsgameodds.com/v2"
    sports_game_odds_key: str = "replace_with_api_key"
    sharpapi_base_url: str = "https://api.sharpapi.io/api/v1"
    sharpapi_key: str = "replace_with_api_key"
    statsbomb_base_url: str = "replace_if_available"
    statsbomb_key: str = "replace_if_available"

    max_odds_age_minutes: int = 30
    max_fixture_age_hours: int = 24
    max_injury_age_hours: int = 24
    max_xg_age_days: int = 7
    max_team_stats_age_days: int = 7
    lineup_recheck_window_minutes: int = 90

    supported_competitions: str = "EPL,LALIGA,BUNDESLIGA,SERIE_A,LIGUE_1,UCL,UEL,NOR_ELITESERIEN"
    supported_markets: str = "1X2,OVER_UNDER_2_5,BTTS"
    log_level: str = "INFO"

    @property
    def supported_competition_list(self) -> List[str]:
        return [item.strip() for item in self.supported_competitions.split(",") if item.strip()]

    @property
    def supported_market_list(self) -> List[str]:
        return [item.strip() for item in self.supported_markets.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
