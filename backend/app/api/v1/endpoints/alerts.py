from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.alert import AlertAckRequest, AlertListResponse, AlertLogRead
from app.schemas.station import StationRead
from app.schemas.user import UserRead
from app.services.alert_service import acknowledge_alert, list_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"], dependencies=[Depends(get_current_user)])


@router.get(
    "",
    response_model=AlertListResponse,
    summary="Alarm kayıtlarını listeler",
)
def get_alerts(
    station_id: int | None = None,
    severity: str | None = None,
    only_unacknowledged: bool = False,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> AlertListResponse:
    rows = list_alerts(
        db,
        station_id=station_id,
        severity=severity,
        only_unacknowledged=only_unacknowledged,
        limit=limit,
    )
    items = [
        AlertLogRead(
            id=row.id,
            station=StationRead.model_validate(row.station),
            severity=row.severity,
            message=row.message,
            triggered_at=row.triggered_at,
            is_acknowledged=row.is_acknowledged,
            acknowledged_by=UserRead.model_validate(row.acknowledged_by_user) if row.acknowledged_by_user else None,
            acknowledged_at=row.acknowledged_at,
        )
        for row in rows
    ]
    return AlertListResponse(items=items, total=len(items))


@router.post(
    "/ack",
    response_model=AlertLogRead,
    summary="Alarmı okundu olarak işaretler",
)
def post_alert_ack(
    payload: AlertAckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertLogRead:
    row = acknowledge_alert(db, payload.alert_id, current_user)
    db.refresh(row, attribute_names=["station", "acknowledged_by_user"])
    return AlertLogRead(
        id=row.id,
        station=StationRead.model_validate(row.station),
        severity=row.severity,
        message=row.message,
        triggered_at=row.triggered_at,
        is_acknowledged=row.is_acknowledged,
        acknowledged_by=UserRead.model_validate(current_user),
        acknowledged_at=row.acknowledged_at,
    )
