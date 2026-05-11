from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel
from app.schemas.station import StationRead


class SensorReadingRead(ORMModel):
    id: int
    station_id: int
    recorded_at: datetime
    water_level_cm: float
    air_pressure_hpa: float | None
    temperature_c: float | None
    data_source: str


class SensorReadingWithStation(SensorReadingRead):
    station: StationRead
    risk_level: str


class SensorReadingsResponse(BaseModel):
    items: list[SensorReadingWithStation]
    total: int


class LatestStationReading(BaseModel):
    station: StationRead
    reading: SensorReadingRead | None
    risk_level: str


class LatestReadingsResponse(BaseModel):
    items: list[LatestStationReading]
    total: int


class ReadingHistoryResponse(BaseModel):
    station: StationRead
    items: list[SensorReadingRead]
    total: int


class ReadingStatsResponse(BaseModel):
    station: StationRead
    period_hours: int
    reading_count: int
    min_water_level_cm: float | None
    max_water_level_cm: float | None
    avg_water_level_cm: float | None
    avg_air_pressure_hpa: float | None
    avg_temperature_c: float | None
