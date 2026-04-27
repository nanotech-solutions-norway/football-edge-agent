from fastapi import APIRouter, HTTPException, status

from backend.app.api.phase3 import router as phase3_router
from backend.app.config import get_settings
from backend.app.providers.clients import get_provider_clients
from backend.app.services.auto_betting_service import AutoBettingInactiveError, assert_auto_betting_allowed, get_auto_betting_status
from backend.app.services.data_quality_service import build_fixture_quality_placeholder

router = APIRouter()
settings = get_settings()


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


@router.get("/fixtures/{fixture_id}")
async def fixture_detail(fixture_id: int):
    return {"status": "success", "data": {"fixture_id": fixture_id, "status": "placeholder"}}


@router.get("/odds/current/{fixture_id}")
async def current_odds(fixture_id: int):
    return {
        "status": "success",
        "data": {"fixture_id": fixture_id, "odds": [], "mandatory": True, "status": "pending_provider_integration"},
    }


@router.get("/odds/history/{fixture_id}")
async def historical_odds(fixture_id: int):
    return {
        "status": "success",
        "data": {"fixture_id": fixture_id, "historical_odds": [], "mandatory": True, "status": "pending_provider_integration"},
    }


@router.get("/xg/{fixture_id}")
async def fixture_xg(fixture_id: int):
    return {
        "status": "success",
        "data": {"fixture_id": fixture_id, "xg": [], "mandatory": True, "status": "pending_provider_integration"},
    }


@router.get("/lineups/{fixture_id}")
async def fixture_lineups(fixture_id: int):
    return {"status": "success", "data": {"fixture_id": fixture_id, "lineups": [], "confirmed": False}}


@router.get("/injuries/{fixture_id}")
async def fixture_injuries(fixture_id: int):
    return {"status": "success", "data": {"fixture_id": fixture_id, "injuries_suspensions": []}}


@router.get("/data-quality/{fixture_id}")
async def data_quality(fixture_id: int):
    return {"status": "success", "data": build_fixture_quality_placeholder(fixture_id)}


@router.get("/audit/fixture/{fixture_id}")
async def fixture_audit(fixture_id: int):
    return {"status": "success", "data": {"fixture_id": fixture_id, "events": [], "status": "placeholder"}}


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
