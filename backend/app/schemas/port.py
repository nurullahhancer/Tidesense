from datetime import datetime
from pydantic import BaseModel

from app.schemas.common import ORMModel


class PortRead(ORMModel):
    id: int
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    description: str | None
    is_active: bool
    created_at: datetime


class PortCreate(BaseModel):
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    description: str | None = None


class PortUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    is_active: bool | None = None


class PortListResponse(BaseModel):
    items: list[PortRead]
    total: int


class PortDetailResponse(BaseModel):
    port: PortRead
