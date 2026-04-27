from backend.app.config import get_settings


class AutoBettingInactiveError(PermissionError):
    """Raised whenever execution of auto-betting is attempted during the hard-lock period."""


def get_auto_betting_status() -> dict:
    settings = get_settings()
    hard_locked = bool(settings.auto_betting_hard_lock)
    enabled = bool(settings.auto_betting_enabled) and not hard_locked
    return {
        "enabled": enabled,
        "hard_locked": hard_locked,
        "provider": settings.auto_betting_provider,
        "dry_run": settings.auto_betting_dry_run,
        "legal_review_required": settings.auto_betting_require_legal_review,
        "compliance_review_required": settings.auto_betting_require_compliance_review,
        "risk_review_required": settings.auto_betting_require_risk_review,
        "message": "Auto-betting is inactive and hard-locked. Phase 2 permits architecture only, not execution.",
    }


def assert_auto_betting_allowed() -> None:
    status = get_auto_betting_status()
    if status["hard_locked"] or not status["enabled"]:
        raise AutoBettingInactiveError(status["message"])
