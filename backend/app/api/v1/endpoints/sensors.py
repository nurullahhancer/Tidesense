from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.reading import (
    LatestReadingsResponse,
    LatestStationReading,
    SensorReadingRead,
    SensorReadingsResponse,
    SensorReadingWithStation,
)
from app.schemas.station import StationRead
from app.services.reading_service import latest_readings_by_station, list_recent_readings

router = APIRouter(prefix="/sensors", tags=["sensors"], dependencies=[Depends(get_current_user)])


@router.get(
    "/readings",
    response_model=SensorReadingsResponse,
    summary="Son sensör ölçümlerini listeler",
)
def get_sensor_readings(
    station_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> SensorReadingsResponse:
    rows = list_recent_readings(db, station_id=station_id, limit=limit)
    items = [
        SensorReadingWithStation(
            **SensorReadingRead.model_validate(row).model_dump(),
            station=StationRead.model_validate(row.station),
            risk_level=("KRITIK" if float(row.water_level_cm) >= 150 else "DIKKAT" if float(row.water_level_cm) >= 120 else "NORMAL"),
        )
        for row in rows
    ]
    return SensorReadingsResponse(items=items, total=len(items))


@router.get(
    "/latest",
    response_model=LatestReadingsResponse,
    summary="Her istasyon için en güncel sensör verisini döndürür",
)
def get_latest_readings(db: Session = Depends(get_db)) -> LatestReadingsResponse:
    items = []
    for station, reading, risk in latest_readings_by_station(db):
        items.append(
            LatestStationReading(
                station=StationRead.model_validate(station),
                reading=SensorReadingRead.model_validate(reading) if reading else None,
                risk_level=risk,
            )
        )
    return LatestReadingsResponse(items=items, total=len(items))
