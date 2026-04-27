from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Football Edge Agent Backend",
    description=(
        "Phase 2 backend foundation for a probability-calibrated football analysis agent. "
        "Default posture is NO BET. Auto-betting is inactive and hard-locked."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "status": "success",
        "data": {
            "service": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "default_recommendation": "NO BET",
            "auto_betting": "inactive_hard_locked",
        },
    }
