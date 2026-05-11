from datetime import datetime

from pydantic import BaseModel

from app.schemas.station import StationRead


class TidePredictionRead(BaseModel):
    prediction_time: datetime
    predicted_water_level_cm: float
    confidence_score: float
    model_version: str


class PredictionSeries(BaseModel):
    station: StationRead
    items: list[TidePredictionRead]
    total: int
    rmse: float | None = None
    fallback_used: bool = False


class PredictionListResponse(BaseModel):
    items: list[PredictionSeries]
    total: int
