from datetime import datetime

from pydantic import BaseModel


class MoonPositionRead(BaseModel):
    calculated_at: datetime
    moon_phase: str
    moon_illumination: float
    gravity_factor: float
    altitude: float
    azimuth: float
    station_id: int | None = None
    station_name: str | None = None
