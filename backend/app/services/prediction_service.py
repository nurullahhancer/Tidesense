from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import MoonPosition, SensorReading, Station, TidePrediction
from app.services.ml_service import FEATURE_COLUMNS, load_model, train_model
from app.services.moon_service import calculate_moon_snapshot
from app.services.station_service import get_station_or_404

PREFERRED_TRAINING_SOURCE = "mqtt"
MIN_SOURCE_ROWS = 30
MAX_STEP_DELTA_CM = 16.0


def _station_readings_frame(db: Session, station_id: int) -> pd.DataFrame:
    rows = db.execute(
        select(
            SensorReading.recorded_at,
            SensorReading.water_level_cm,
            SensorReading.air_pressure_hpa,
            SensorReading.temperature_c,
            SensorReading.data_source,
        )
        .where(SensorReading.station_id == station_id)
        .order_by(SensorReading.recorded_at.asc())
    ).all()
    if not rows:
        return pd.DataFrame(
            columns=[
                "recorded_at",
                "water_level_cm",
                "air_pressure_hpa",
                "temperature_c",
                "data_source",
            ]
        )
    frame = pd.DataFrame(
        rows,
        columns=[
            "recorded_at",
            "water_level_cm",
            "air_pressure_hpa",
            "temperature_c",
            "data_source",
        ],
    )
    live_frame = frame[frame["data_source"] == PREFERRED_TRAINING_SOURCE].copy()
    if len(live_frame) >= MIN_SOURCE_ROWS:
        frame = live_frame
    frame["recorded_at"] = pd.to_datetime(frame["recorded_at"], utc=True)
    frame["water_level_cm"] = frame["water_level_cm"].astype(float)
    frame["air_pressure_hpa"] = frame["air_pressure_hpa"].astype(float)
    frame["temperature_c"] = frame["temperature_c"].astype(float)
    return frame


def _moon_frame(db: Session) -> pd.DataFrame:
    rows = db.execute(
        select(
            MoonPosition.calculated_at,
            MoonPosition.moon_phase,
            MoonPosition.moon_illumination,
            MoonPosition.gravity_factor,
        ).order_by(MoonPosition.calculated_at.asc())
    ).all()
    if not rows:
        return pd.DataFrame(columns=["calculated_at", "moon_phase", "moon_illumination", "gravity_factor"])
    frame = pd.DataFrame(rows, columns=["calculated_at", "moon_phase", "moon_illumination", "gravity_factor"])
    frame["calculated_at"] = pd.to_datetime(frame["calculated_at"], utc=True)
    frame["moon_illumination"] = frame["moon_illumination"].astype(float)
    frame["gravity_factor"] = frame["gravity_factor"].astype(float)
    return frame


def _build_feature_row(
    lag_values: list[float],
    pressure: float,
    temperature: float,
    moon_snapshot: dict,
    prediction_time: datetime,
) -> pd.DataFrame:
    from app.core.constants import MOON_PHASE_MAP

    payload = {
        "lag_1": lag_values[-1],
        "lag_2": lag_values[-2],
        "lag_3": lag_values[-3],
        "air_pressure_hpa": pressure,
        "temperature_c": temperature,
        "moon_phase_numeric": MOON_PHASE_MAP.get(moon_snapshot["moon_phase"], 0),
        "moon_illumination": moon_snapshot["moon_illumination"],
        "gravity_factor": moon_snapshot["gravity_factor"],
        "hour_of_day": prediction_time.hour,
        "day_of_week": prediction_time.weekday(),
    }
    return pd.DataFrame([payload], columns=FEATURE_COLUMNS)


def _fallback_prediction(latest_levels: list[float], moon_snapshot: dict, step_index: int) -> float:
    baseline = sum(latest_levels[-3:]) / min(len(latest_levels), 3)
    drift = (moon_snapshot["gravity_factor"] - 1.0) * 25
    cyclical = (step_index % 6 - 3) * 1.8
    return round(baseline + drift + cyclical, 2)


def _stabilize_prediction(predicted: float, latest_levels: list[float]) -> float:
    anchor = latest_levels[-1]
    lower_bound = anchor - MAX_STEP_DELTA_CM
    upper_bound = anchor + MAX_STEP_DELTA_CM
    return round(min(max(predicted, lower_bound), upper_bound), 2)


def _external_prediction_rows(
    db: Session,
    station_id: int,
    start_time: datetime,
    horizon_hours: int,
) -> list[TidePrediction]:
    end_time = start_time + timedelta(hours=horizon_hours)
    return list(
        db.scalars(
            select(TidePrediction)
            .where(
                TidePrediction.station_id == station_id,
                TidePrediction.prediction_time >= start_time,
                TidePrediction.prediction_time <= end_time,
                TidePrediction.model_version.like("api_tidecheck%"),
            )
            .order_by(TidePrediction.prediction_time.asc())
        ).all()
    )


def _prediction_rows_payload(rows: list[TidePrediction]) -> list[dict]:
    return [
        {
            "prediction_time": row.prediction_time,
            "predicted_water_level_cm": float(row.predicted_water_level_cm),
            "confidence_score": float(row.confidence_score),
            "model_version": row.model_version,
        }
        for row in rows
    ]


def generate_predictions_for_station(
    db: Session,
    station_id: int,
    horizon_hours: int | None = None,
    force_retrain: bool = False,
    persist: bool = True,
) -> dict:
    station = get_station_or_404(db, station_id)
    horizon_hours = horizon_hours or settings.prediction_horizon_hours
    start_time = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)

    if not force_retrain:
        external_rows = _external_prediction_rows(db, station_id, start_time, horizon_hours)
        if external_rows:
            model_bundle = load_model(station_id)
            return {
                "station": station,
                "items": _prediction_rows_payload(external_rows),
                "total": len(external_rows),
                "rmse": model_bundle.rmse if model_bundle else None,
                "fallback_used": False,
            }

    readings_frame = _station_readings_frame(db, station_id)
    moon_frame = _moon_frame(db)
    bundle = None if force_retrain else load_model(station_id)
    if bundle is None:
        bundle = train_model(readings_frame, moon_frame, station_id)

    if readings_frame.empty:
        return {
            "station": station,
            "items": [],
            "total": 0,
            "rmse": bundle.rmse,
            "fallback_used": True,
        }

    latest_levels = readings_frame["water_level_cm"].tail(3).tolist()
    while len(latest_levels) < 3:
        latest_levels.insert(0, latest_levels[0])

    pressure_series = readings_frame["air_pressure_hpa"].dropna()
    temperature_series = readings_frame["temperature_c"].dropna()
    latest_pressure = float(pressure_series.iloc[-1]) if not pressure_series.empty else 1013.25
    latest_temperature = float(temperature_series.iloc[-1]) if not temperature_series.empty else 20.0

    generated_items: list[dict] = []
    for step in range(1, horizon_hours + 1):
        prediction_time = start_time + timedelta(hours=step)
        moon_snapshot = calculate_moon_snapshot(station.latitude, station.longitude, prediction_time)
        if bundle.model is not None:
            feature_row = _build_feature_row(
                lag_values=latest_levels,
                pressure=latest_pressure,
                temperature=latest_temperature,
                moon_snapshot=moon_snapshot,
                prediction_time=prediction_time,
            )
            predicted = float(bundle.model.predict(feature_row)[0])
        else:
            predicted = _fallback_prediction(latest_levels, moon_snapshot, step)

        predicted = _stabilize_prediction(predicted, latest_levels)
        latest_levels.append(predicted)
        latest_levels = latest_levels[-3:]
        confidence = 0.62 if bundle.fallback_used else max(
            0.45,
            1 - ((bundle.rmse or 12) / 100) - (step * 0.012),
        )
        generated_items.append(
            {
                "prediction_time": prediction_time,
                "predicted_water_level_cm": round(predicted, 2),
                "confidence_score": round(confidence, 4),
                "model_version": bundle.version,
            }
        )

    if persist:
        db.execute(
            delete(TidePrediction).where(
                TidePrediction.station_id == station_id,
                TidePrediction.prediction_time >= start_time,
            )
        )
        db.add_all(
            TidePrediction(station_id=station_id, **item) for item in generated_items
        )
        db.commit()

    return {
        "station": station,
        "items": generated_items,
        "total": len(generated_items),
        "rmse": bundle.rmse,
        "fallback_used": bundle.fallback_used,
    }


def generate_predictions_for_all_stations(db: Session, force_retrain: bool = False) -> list[dict]:
    stations = list(db.scalars(select(Station).where(Station.is_active.is_(True))).all())
    return [
        generate_predictions_for_station(
            db,
            station.id,
            force_retrain=force_retrain,
            persist=True,
        )
        for station in stations
    ]


def train_models_for_all_stations(db: Session) -> list[dict]:
    stations = list(db.scalars(select(Station).where(Station.is_active.is_(True))).all())
    results: list[dict] = []
    moon_frame = _moon_frame(db)
    for station in stations:
        bundle = train_model(_station_readings_frame(db, station.id), moon_frame, station.id)
        results.append(
            {
                "station": station,
                "version": bundle.version,
                "rmse": bundle.rmse,
                "fallback_used": bundle.fallback_used,
            }
        )
    return results


def get_prediction_series(db: Session, station_id: int | None = None) -> list[dict]:
    stations = list(
        db.scalars(
            select(Station)
            .where(Station.is_active.is_(True))
            .order_by(Station.name.asc())
        ).all()
    )
    if station_id:
        stations = [station for station in stations if station.id == station_id]

    items = []
    for station in stations:
        rows = list(
            db.scalars(
                select(TidePrediction)
                .where(TidePrediction.station_id == station.id)
                .where(TidePrediction.prediction_time >= datetime.now(UTC).replace(minute=0, second=0, microsecond=0))
                .order_by(TidePrediction.prediction_time.asc())
            ).all()
        )
        model_bundle = load_model(station.id)
        rmse = model_bundle.rmse if model_bundle else None
        items.append(
            {
                "station": station,
                "items": [
                    {
                        "prediction_time": row.prediction_time,
                        "predicted_water_level_cm": float(row.predicted_water_level_cm),
                        "confidence_score": float(row.confidence_score),
                        "model_version": row.model_version,
                    }
                    for row in rows
                ],
                "total": len(rows),
                "rmse": rmse,
                "fallback_used": False if rows else True,
            }
        )
    return items
