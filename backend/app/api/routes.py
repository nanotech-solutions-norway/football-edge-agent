from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from backend.app.api.phase3 import router as phase3_router
from backend.app.config import get_settings
from backend.app.providers.clients import get_provider_clients
from backend.app.services.auto_betting_service import AutoBettingInactiveError, assert_auto_betting_allowed, get_auto_betting_status
from backend.app.services.data_quality_service import build_fixture_quality_placeholder

router = APIRouter()
settings = get_settings()


def require_fixture_code(
    fixture_code: Annotated[str, Path(pattern=r"^[0-9A-HJ-KM-NP-TV-Z]{7}$")],
) -> str:
    if not any(character.isdigit() for character in fixture_code) or not any(
        character.isalpha() for character in fixture_code
    ):
        raise HTTPException(status_code=422, detail="fixture_code must include a letter and digit")
    return fixture_code


FixtureCode = Annotated[str, Depends(require_fixture_code)]


@router.get("/health")
async def health_check():
    return {
        "status": "success",
        "data": {
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "default_recommendation": "NO BET",
        },
    }


@router.get("/providers/status")
async def provider_status():
    clients = get_provider_clients()
    return {"status": "success", "data": {name: await client.health_check() for name, client in clients.items()}}


@router.get("/fixtures/upcoming")
async def upcoming_fixtures(competition: str | None = None, date_from: str | None = None, date_to: str | None = None):
    return {
        "status": "success",
        "data": [],
        "metadata": {
            "competition": competition,
            "date_from": date_from,
            "date_to": date_to,
            "supported_competitions": settings.supported_competition_list,
            "note": "Provider ingestion is intentionally placeholder-only in Phase 2.",
        },
    }


@router.get("/fixtures/{fixture_code}")
async def fixture_detail(fixture_code: FixtureCode):
    return {"status": "success", "data": {"fixture_code": fixture_code, "status": "placeholder"}}


@router.get("/odds/current/{fixture_code}")
async def current_odds(fixture_code: FixtureCode):
    return {
        "status": "success",
        "data": {"fixture_code": fixture_code, "odds": [], "mandatory": True, "status": "pending_provider_integration"},
    }


@router.get("/odds/history/{fixture_code}")
async def historical_odds(fixture_code: FixtureCode):
    return {
        "status": "success",
        "data": {"fixture_code": fixture_code, "historical_odds": [], "mandatory": True, "status": "pending_provider_integration"},
    }


@router.get("/xg/{fixture_code}")
async def fixture_xg(fixture_code: FixtureCode):
    return {
        "status": "success",
        "data": {"fixture_code": fixture_code, "xg": [], "mandatory": True, "status": "pending_provider_integration"},
    }


@router.get("/lineups/{fixture_code}")
async def fixture_lineups(fixture_code: FixtureCode):
    return {"status": "success", "data": {"fixture_code": fixture_code, "lineups": [], "confirmed": False}}


@router.get("/injuries/{fixture_code}")
async def fixture_injuries(fixture_code: FixtureCode):
    return {"status": "success", "data": {"fixture_code": fixture_code, "injuries_suspensions": []}}


@router.get("/data-quality/{fixture_code}")
async def data_quality(fixture_code: FixtureCode):
    return {"status": "success", "data": build_fixture_quality_placeholder(fixture_code)}


@router.get("/audit/fixture/{fixture_code}")
async def fixture_audit(fixture_code: FixtureCode):
    return {"status": "success", "data": {"fixture_code": fixture_code, "events": [], "status": "placeholder"}}


@router.get("/auto-betting/status")
async def auto_betting_status():
    return {"status": "success", "data": get_auto_betting_status()}


@router.post("/auto-betting/execute")
async def execute_auto_bet():
    try:
        assert_auto_betting_allowed()
    except AutoBettingInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return {"status": "blocked", "data": {"message": "Auto-betting execution is not implemented in Phase 2."}}


router.include_router(phase3_router)
