from datetime import UTC, datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AlertLog, SensorReading, Station, TidePrediction, User
from app.scheduler.manager import scheduler_manager
from app.websocket.manager import connection_manager


def collect_health_snapshot(db: Session) -> dict:
    database_status = {"status": "connected", "detail": "Database query succeeded"}
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        database_status = {"status": "disconnected", "detail": str(exc)}

    model_status = "ready"
    if not settings.model_artifacts_dir:
        model_status = "not_configured"

    return {
        "project": settings.project_name,
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.environment,
        "database": database_status,
        "websocket": {
            "status": "ready",
            "active_connections": connection_manager.connection_count,
        },
        "scheduler": scheduler_manager.snapshot(),
        "ml_module": {
            "status": model_status,
            "artifacts_dir": settings.model_artifacts_dir,
        },
        "external_provider": {
            "selected": settings.external_provider,
            "tidecheck_key_configured": bool(settings.tidecheck_api_key),
        },
        "counts": {
            "stations": int(
                db.scalar(
                    select(func.count(Station.id)).where(Station.is_active.is_(True))
                )
                or 0
            ),
            "users": int(db.scalar(select(func.count(User.id))) or 0),
            "sensor_readings": int(
                db.scalar(
                    select(func.count(SensorReading.id))
                    .join(Station)
                    .where(Station.is_active.is_(True))
                )
                or 0
            ),
            "predictions": int(
                db.scalar(
                    select(func.count(TidePrediction.id))
                    .join(Station)
                    .where(Station.is_active.is_(True))
                )
                or 0
            ),
            "alerts": int(
                db.scalar(
                    select(func.count(AlertLog.id))
                    .join(Station)
                    .where(Station.is_active.is_(True))
                )
                or 0
            ),
        },
    }
