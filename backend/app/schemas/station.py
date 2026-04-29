from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class StationRead(ORMModel):
    id: int
    name: str
    code: str
    latitude: float
    longitude: float
    city: str
    is_active: bool
    created_at: datetime


class StationCreate(BaseModel):
    name: str
    code: str
    latitude: float
    longitude: float
    city: str
    snapshot_url: str | None = None


class StationListResponse(BaseModel):
    items: list[StationRead]
    total: int


class StationDetailResponse(BaseModel):
    station: StationRead
