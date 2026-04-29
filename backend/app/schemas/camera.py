from datetime import datetime

from pydantic import BaseModel

from app.schemas.station import StationRead


class CameraFeedRead(BaseModel):
    station: StationRead
    snapshot_url: str
    stream_url: str
    detected_water_level_cm: float | None
    risk_status: str
    resolution: str
    fps: int
    captured_at: datetime | None


class CameraListResponse(BaseModel):
    items: list[CameraFeedRead]
    total: int
