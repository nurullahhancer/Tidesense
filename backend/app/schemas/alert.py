from datetime import datetime

from pydantic import BaseModel

from app.schemas.station import StationRead
from app.schemas.user import UserRead


class AlertLogRead(BaseModel):
    id: int
    station: StationRead
    severity: str
    message: str
    triggered_at: datetime
    is_acknowledged: bool
    acknowledged_by: UserRead | None = None
    acknowledged_at: datetime | None = None


class AlertListResponse(BaseModel):
    items: list[AlertLogRead]
    total: int


class AlertAckRequest(BaseModel):
    alert_id: int
