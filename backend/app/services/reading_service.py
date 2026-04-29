from __future__ import annotations

import csv
import io
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import SensorReading, Station
from app.services.alert_service import compute_risk_level
from app.services.station_service import get_station_or_404


def list_recent_readings(db: Session, station_id: int | None = None, limit: int = 50) -> list[SensorReading]:
    query = (
        select(SensorReading)
        .join(Station)
        .options(selectinload(SensorReading.station))
        .where(Station.is_active.is_(True))
        .order_by(SensorReading.recorded_at.desc())
        .limit(limit)
    )
    if station_id:
        query = query.where(SensorReading.station_id == station_id)
    return list(db.scalars(query).all())


def latest_readings_by_station(db: Session) -> list[tuple[Station, SensorReading | None, str]]:
    stations = list(
        db.scalars(
            select(Station)
            .where(Station.is_active.is_(True))
            .order_by(Station.name.asc())
        ).all()
    )
    items: list[tuple[Station, SensorReading | None, str]] = []
    for station in stations:
        reading = db.scalar(
            select(SensorReading)
            .where(SensorReading.station_id == station.id)
            .order_by(SensorReading.recorded_at.desc())
            .limit(1)
        )
        risk = compute_risk_level(float(reading.water_level_cm)) if reading else "NORMAL"
        items.append((station, reading, risk))
    return items


def reading_history(
    db: Session,
    station_id: int,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 500,
) -> tuple[Station, list[SensorReading]]:
    station = get_station_or_404(db, station_id)
    start_at = (start_at or datetime.now(UTC) - timedelta(hours=48)).astimezone(UTC)
    end_at = (end_at or datetime.now(UTC)).astimezone(UTC)
    if start_at > end_at:
        raise HTTPException(status_code=400, detail="start_at must be before end_at")

    readings = list(
        db.scalars(
            select(SensorReading)
            .where(
                SensorReading.station_id == station_id,
                SensorReading.recorded_at >= start_at,
                SensorReading.recorded_at <= end_at,
            )
            .order_by(SensorReading.recorded_at.desc())
            .limit(limit)
        ).all()
    )
    readings.reverse()
    return station, readings


def reading_stats(db: Session, station_id: int, period_hours: int = 24) -> tuple[Station, dict]:
    station = get_station_or_404(db, station_id)
    start_at = datetime.now(UTC) - timedelta(hours=period_hours)
    result = db.execute(
        select(
            func.count(SensorReading.id),
            func.min(SensorReading.water_level_cm),
            func.max(SensorReading.water_level_cm),
            func.avg(SensorReading.water_level_cm),
            func.avg(SensorReading.air_pressure_hpa),
            func.avg(SensorReading.temperature_c),
        ).where(
            SensorReading.station_id == station_id,
            SensorReading.recorded_at >= start_at,
        )
    ).one()

    return station, {
        "reading_count": int(result[0] or 0),
        "min_water_level_cm": float(result[1]) if result[1] is not None else None,
        "max_water_level_cm": float(result[2]) if result[2] is not None else None,
        "avg_water_level_cm": float(result[3]) if result[3] is not None else None,
        "avg_air_pressure_hpa": float(result[4]) if result[4] is not None else None,
        "avg_temperature_c": float(result[5]) if result[5] is not None else None,
    }


def render_history_csv(station: Station, readings: list[SensorReading]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "station_code",
            "station_name",
            "recorded_at",
            "water_level_cm",
            "air_pressure_hpa",
            "temperature_c",
            "data_source",
        ]
    )
    for reading in readings:
        writer.writerow(
            [
                station.code,
                station.name,
                reading.recorded_at.isoformat(),
                float(reading.water_level_cm),
                float(reading.air_pressure_hpa) if reading.air_pressure_hpa is not None else "",
                float(reading.temperature_c) if reading.temperature_c is not None else "",
                reading.data_source,
            ]
        )
    return buffer.getvalue()
