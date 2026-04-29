from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.constants import RiskSeverity
from app.models import AlertLog, SensorReading, Station, TidePrediction, User
from app.websocket.manager import connection_manager


def compute_risk_level(water_level_cm: float) -> str:
    if water_level_cm >= settings.alert_critical_threshold_cm:
        return RiskSeverity.CRITICAL.value
    if water_level_cm >= settings.alert_warning_threshold_cm:
        return RiskSeverity.WARNING.value
    return RiskSeverity.NORMAL.value


def evaluate_station_risk(db: Session, station: Station) -> AlertLog | None:
    latest_reading = db.scalar(
        select(SensorReading)
        .where(SensorReading.station_id == station.id)
        .order_by(SensorReading.recorded_at.desc())
        .limit(1)
    )
    if latest_reading is None:
        return None

    predicted_peak = db.scalar(
        select(TidePrediction.predicted_water_level_cm)
        .where(TidePrediction.station_id == station.id)
        .order_by(TidePrediction.prediction_time.asc())
        .limit(1)
    )
    evaluated_level = max(
        float(latest_reading.water_level_cm),
        float(predicted_peak) if predicted_peak is not None else float(latest_reading.water_level_cm),
    )
    severity = compute_risk_level(evaluated_level)
    if severity == RiskSeverity.NORMAL.value:
        return None

    recent_duplicate = db.scalar(
        select(AlertLog)
        .where(
            AlertLog.station_id == station.id,
            AlertLog.severity == severity,
            AlertLog.triggered_at >= datetime.now(UTC) - timedelta(hours=1),
        )
        .order_by(AlertLog.triggered_at.desc())
        .limit(1)
    )
    if recent_duplicate:
        return recent_duplicate

    message = (
        f"{station.name} istasyonunda su seviyesi {evaluated_level:.1f} cm olarak değerlendirildi. "
        f"Risk seviyesi: {severity}."
    )
    alert = AlertLog(
        station_id=station.id,
        severity=severity,
        message=message,
        triggered_at=datetime.now(UTC),
        is_acknowledged=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    connection_manager.emit(
        {
            "type": "alert",
            "payload": {
                "station_id": station.id,
                "severity": severity,
                "message": message,
                "triggered_at": alert.triggered_at.isoformat(),
            },
        }
    )
    return alert


def evaluate_all_stations(db: Session) -> list[AlertLog]:
    stations = list(db.scalars(select(Station).where(Station.is_active.is_(True))).all())
    return [alert for station in stations if (alert := evaluate_station_risk(db, station)) is not None]


def list_alerts(
    db: Session,
    station_id: int | None = None,
    severity: str | None = None,
    only_unacknowledged: bool = False,
    limit: int = 100,
) -> list[AlertLog]:
    query = (
        select(AlertLog)
        .join(Station)
        .options(
            selectinload(AlertLog.station),
            selectinload(AlertLog.acknowledged_by_user),
        )
        .where(Station.is_active.is_(True))
        .order_by(AlertLog.triggered_at.desc())
        .limit(limit)
    )
    if station_id:
        query = query.where(AlertLog.station_id == station_id)
    if severity:
        query = query.where(AlertLog.severity == severity)
    if only_unacknowledged:
        query = query.where(AlertLog.is_acknowledged.is_(False))
    return list(db.scalars(query).all())


def acknowledge_alert(db: Session, alert_id: int, user: User) -> AlertLog:
    alert = db.get(AlertLog, alert_id)
    if alert is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_acknowledged = True
    alert.acknowledged_by = user.id
    alert.acknowledged_at = datetime.now(UTC)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
