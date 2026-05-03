from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.constants import UserRole
from app.db.session import get_db
from app.models import User
from app.schemas.reading import ReadingHistoryResponse, ReadingStatsResponse, SensorReadingRead
from app.schemas.station import StationRead
from app.services.external_data_service import latest_external_rows, refresh_recent_external_data
from app.services.reading_service import reading_history, reading_stats, render_history_csv

router = APIRouter(prefix="/readings", tags=["readings"], dependencies=[Depends(get_current_user)])


@router.get(
    "/history",
    response_model=ReadingHistoryResponse,
    summary="Tarihsel sensör verisini getirir",
)
def get_reading_history(
    station_id: int,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = Query(default=500, le=2000),
    export_format: str = Query(default="json", pattern="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReadingHistoryResponse | PlainTextResponse:
    station, rows = reading_history(db, station_id=station_id, start_at=start_at, end_at=end_at, limit=limit)
    if export_format == "csv":
        if current_user.role not in {UserRole.RESEARCHER.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value}:
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="CSV export requires researcher or admin role")
        csv_payload = render_history_csv(station, rows)
        return PlainTextResponse(
            content=csv_payload,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={station.code.lower()}_history.csv"},
        )
    return ReadingHistoryResponse(
        station=StationRead.model_validate(station),
        items=[SensorReadingRead.model_validate(row) for row in rows],
        total=len(rows),
    )


@router.get(
    "/stats",
    response_model=ReadingStatsResponse,
    summary="Özet istatistikleri döndürür",
)
def get_reading_stats(
    station_id: int,
    period_hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> ReadingStatsResponse:
    station, stats = reading_stats(db, station_id=station_id, period_hours=period_hours)
    return ReadingStatsResponse(
        station=StationRead.model_validate(station),
        period_hours=period_hours,
        **stats,
    )


@router.get(
    "/noaa",
    summary="Veritabanındaki dış kaynak ölçümlerini döndürür",
)
def get_noaa_readings(
    station_id: int | None = None,
    limit: int = Query(default=48, le=500),
    refresh: bool = False,
    provider: str | None = Query(default=None, pattern="^(mock|noaa|tidecheck|auto)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    refresh_result = None
    if refresh:
        if current_user.role not in {UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value}:
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="Refresh requires admin role")
        refresh_result = refresh_recent_external_data(db, provider=provider)

    rows = latest_external_rows(db, station_id=station_id, limit=limit)
    return {
        "provider": "db_cached_external_data",
        "provider_requested": provider,
        "refresh_result": refresh_result,
        "items": [
            {
                "station_id": row.station_id,
                "recorded_at": row.recorded_at.isoformat(),
                "water_level_cm": float(row.water_level_cm) if row.water_level_cm is not None else None,
                "air_pressure_hpa": float(row.air_pressure_hpa) if row.air_pressure_hpa is not None else None,
                "temperature_c": float(row.temperature_c) if row.temperature_c is not None else None,
                "raw_payload": row.raw_payload,
            }
            for row in rows
        ],
        "total": len(rows),
    }
