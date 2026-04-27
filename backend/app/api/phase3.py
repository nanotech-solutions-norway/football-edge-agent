"""Phase 3 API routes for the baseline probability engine."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.models.phase3_probability_engine import (
    ALLOWED_RECOMMENDATIONS,
    MODEL_NAME,
    MODEL_VERSION,
    SUPPORTED_MARKETS,
    build_recommendation_payload,
    calibration_summary,
    generate_market_probabilities,
    glicko_placeholder_rating,
)

router = APIRouter(tags=["Phase 3 Model Engine"])


class ProbabilityRequest(BaseModel):
    market: str = Field(..., examples=["1X2", "OVER_UNDER_2_5", "BTTS"])
    odds_by_selection: dict[str, float]
    home_expected_goals: float = Field(..., ge=0)
    away_expected_goals: float = Field(..., ge=0)
    home_elo_rating: float = 1500.0
    away_elo_rating: float = 1500.0
    xg_available: bool = True
    historical_odds_available: bool = True


class RecommendationRequest(BaseModel):
    fixture_id: int = Field(..., ge=1)
    market: str
    selection: str
    decimal_odds: float = Field(..., gt=1.0)
    model_probability: float = Field(..., ge=0, le=1)
    bookie_probability: float = Field(..., ge=0, le=1)
    data_quality_score: int = Field(..., ge=0, le=100)
    xg_available: bool = True
    historical_odds_available: bool = True
    odds_fresh: bool = True
    auto_betting_enabled: bool = False


class CalibrationRow(BaseModel):
    predicted_probability: float = Field(..., ge=0, le=1)
    actual_outcome: int = Field(..., ge=0, le=1)


class BacktestSummaryRequest(BaseModel):
    rows: list[CalibrationRow]


@router.get("/model/status")
def model_status() -> dict[str, Any]:
    return {
        "status": "success",
        "data": {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "phase": 3,
            "supported_markets": list(SUPPORTED_MARKETS.keys()),
            "supported_recommendations": sorted(ALLOWED_RECOMMENDATIONS),
            "mandatory_inputs": [
                "current_odds",
                "historical_odds",
                "xG",
                "fixtures",
                "results",
                "timestamps",
                "provider_audit_trail",
            ],
            "glicko_scaffold": glicko_placeholder_rating(),
            "default_recommendation": "NO BET",
            "auto_betting_enabled": False,
            "auto_betting_hard_locked": True,
            "real_money_status": "not_approved",
        },
    }


@router.post("/probabilities/calculate")
def calculate_probabilities(request: ProbabilityRequest) -> dict[str, Any]:
    try:
        outputs = generate_market_probabilities(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"status": "success", "data": outputs}


@router.post("/recommendations/fixture/direct")
def create_direct_recommendation(request: RecommendationRequest) -> dict[str, Any]:
    try:
        payload = build_recommendation_payload(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"status": "success", "data": payload}


@router.post("/backtests/summary")
def summarize_backtest(request: BacktestSummaryRequest) -> dict[str, Any]:
    rows = [row.model_dump() for row in request.rows]
    return {"status": "success", "data": calibration_summary(rows)}
