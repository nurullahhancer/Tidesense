from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from random import Random

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models import NOAAData, SensorReading, Station, TidePrediction
from app.services.moon_service import calculate_moon_snapshot

logger = get_logger(__name__)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HOURLY_FIELDS = "temperature_2m,pressure_msl"


@dataclass
class ExternalFetchResult:
    provider: str
    source_label: str
    items: list[dict]
    used_fallback: bool = False
    detail: str | None = None


def _mock_external_payload(station: Station, timestamp: datetime) -> dict:
    seed = int(timestamp.timestamp() // 3600) + station.id * 17
    rng = Random(seed)
    moon = calculate_moon_snapshot(station.latitude, station.longitude, timestamp)
    cycle = math.sin((timestamp.timestamp() / 3600) / 6.2 + station.id)
    water_level = (
        station.latitude % 10
        + 85
        + (cycle * 28)
        + (moon["gravity_factor"] * 15)
        + rng.uniform(-3, 3)
    )
    air_pressure = (
        1008
        + math.cos((timestamp.timestamp() / 3600) / 8.5 + station.id) * 7
        + rng.uniform(-1.5, 1.5)
    )
    temperature = (
        19
        + math.sin((timestamp.timestamp() / 3600) / 12 + station.longitude) * 6
        + rng.uniform(-1.2, 1.2)
    )
    return {
        "recorded_at": timestamp,
        "water_level_cm": round(water_level, 2),
        "air_pressure_hpa": round(air_pressure, 2),
        "temperature_c": round(temperature, 2),
        "raw_payload": {
            "provider": "mock",
            "mode": "mock-fallback",
            "gravity_factor": moon["gravity_factor"],
            "moon_phase": moon["moon_phase"],
        },
    }


def generate_mock_series(
    station: Station,
    start_at: datetime,
    end_at: datetime,
    step_minutes: int = 60,
    weather_rows: dict[datetime, dict] | None = None,
) -> list[dict]:
    current = start_at.astimezone(UTC)
    end_at = end_at.astimezone(UTC)
    rows: list[dict] = []
    while current <= end_at:
        mock_data = _mock_external_payload(station, current)
        if weather_rows:
            weather = _nearest_weather_row(weather_rows, current)
            if weather.get("temperature_c") is not None:
                mock_data["temperature_c"] = weather["temperature_c"]
            if weather.get("air_pressure_hpa") is not None:
                mock_data["air_pressure_hpa"] = weather["air_pressure_hpa"]
        rows.append(mock_data)
        current += timedelta(minutes=step_minutes)
    return rows


def _normalize_rows(
    provider: str,
    merged: dict[datetime, dict],
) -> list[dict]:
    rows: list[dict] = []
    for timestamp in sorted(merged):
        payload = merged[timestamp]
        if payload.get("water_level_cm") is None:
            continue
        rows.append(
            {
                "recorded_at": timestamp,
                "water_level_cm": round(float(payload["water_level_cm"]), 2),
                "air_pressure_hpa": (
                    round(float(payload["air_pressure_hpa"]), 2)
                    if payload.get("air_pressure_hpa") is not None
                    else None
                ),
                "temperature_c": (
                    round(float(payload["temperature_c"]), 2)
                    if payload.get("temperature_c") is not None
                    else None
                ),
                "raw_payload": {
                    "provider": provider,
                    "source": payload.get("source"),
                    "metadata": payload.get("metadata", {}),
                },
            }
        )
    return rows


def _get_http_client() -> httpx.Client:
    return httpx.Client(timeout=settings.request_timeout_seconds)


def _parse_api_datetime(raw_value: str) -> datetime:
    timestamp = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def _fetch_open_meteo_weather(
    client: httpx.Client,
    station: Station,
    start_at: datetime,
    end_at: datetime,
) -> dict[datetime, dict]:
    response = client.get(
        OPEN_METEO_FORECAST_URL,
        params={
            "latitude": station.latitude,
            "longitude": station.longitude,
            "hourly": OPEN_METEO_HOURLY_FIELDS,
            "timezone": "UTC",
            "start_date": start_at.date().isoformat(),
            "end_date": end_at.date().isoformat(),
        },
    )
    response.raise_for_status()
    hourly = response.json().get("hourly", {})
    times = hourly.get("time") or []
    temperatures = hourly.get("temperature_2m") or []
    pressures = hourly.get("pressure_msl") or []

    rows: dict[datetime, dict] = {}
    for index, raw_time in enumerate(times):
        timestamp = _parse_api_datetime(raw_time)
        if timestamp < start_at or timestamp > end_at:
            continue
        rows[timestamp] = {
            "temperature_c": temperatures[index] if index < len(temperatures) else None,
            "air_pressure_hpa": pressures[index] if index < len(pressures) else None,
        }
    return rows


def _nearest_weather_row(weather_rows: dict[datetime, dict], timestamp: datetime) -> dict:
    if not weather_rows:
        return {}
    hour_floor = timestamp.replace(minute=0, second=0, microsecond=0)
    hour_ceil = hour_floor + timedelta(hours=1)
    preferred = hour_ceil if timestamp.minute >= 30 else hour_floor
    return weather_rows.get(preferred) or weather_rows.get(hour_floor) or weather_rows.get(hour_ceil) or {}


def _fetch_noaa_product(
    client: httpx.Client,
    station_external_id: str,
    product: str,
    start_at: datetime,
    end_at: datetime,
    extra_params: dict[str, str] | None = None,
) -> list[dict]:
    params = {
        "station": station_external_id,
        "begin_date": start_at.strftime("%Y%m%d"),
        "end_date": end_at.strftime("%Y%m%d"),
        "time_zone": "gmt",
        "units": "metric",
        "format": "json",
        "product": product,
    }
    params.update(extra_params or {})
    response = client.get(settings.noaa_base_url, params=params)
    response.raise_for_status()
    payload = response.json()
    return payload.get("data", []) or []


def fetch_noaa_series(
    station: Station,
    start_at: datetime,
    end_at: datetime,
) -> ExternalFetchResult:
    station_external_id = settings.noaa_station_map.get(station.code)
    
    weather_rows = None
    try:
        with _get_http_client() as client:
            weather_rows = _fetch_open_meteo_weather(client, station, start_at, end_at)
    except Exception:
        pass

    if not station_external_id:
        return ExternalFetchResult(
            provider="noaa",
            source_label="mock_external",
            items=generate_mock_series(station, start_at, end_at, weather_rows=weather_rows),
            used_fallback=True,
            detail="No NOAA station mapping found; using mock fallback (with real weather).",
        )

    merged: dict[datetime, dict] = defaultdict(dict)
    try:
        with _get_http_client() as client:
            water_rows = _fetch_noaa_product(
                client,
                station_external_id,
                "hourly_height",
                start_at,
                end_at,
                {"datum": "MLLW", "interval": "h"},
            )
            pressure_rows = _fetch_noaa_product(
                client,
                station_external_id,
                "air_pressure",
                start_at,
                end_at,
                {"interval": "h"},
            )
            temperature_rows = _fetch_noaa_product(
                client,
                station_external_id,
                "air_temperature",
                start_at,
                end_at,
                {"interval": "h"},
            )

        for row in water_rows:
            timestamp = datetime.fromisoformat(row["t"]).astimezone(UTC)
            merged[timestamp].update(
                {
                    "water_level_cm": (float(row["v"]) * 100) + 100, # Add 100cm baseline
                    "source": "noaa_hourly_height",
                    "metadata": {"station_external_id": station_external_id},
                }
            )
        for row in pressure_rows:
            timestamp = datetime.fromisoformat(row["t"]).astimezone(UTC)
            merged[timestamp]["air_pressure_hpa"] = float(row["v"])
        for row in temperature_rows:
            timestamp = datetime.fromisoformat(row["t"]).astimezone(UTC)
            merged[timestamp]["temperature_c"] = float(row["v"])

        items = _normalize_rows("noaa", merged)
        if items:
            return ExternalFetchResult(
                provider="noaa",
                source_label="noaa_external",
                items=items,
                used_fallback=False,
                detail=f"Fetched NOAA data for mapped station {station_external_id}.",
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("NOAA fetch failed for %s: %s", station.code, exc)

    return ExternalFetchResult(
        provider="noaa",
        source_label="mock_external",
        items=generate_mock_series(station, start_at, end_at, weather_rows=weather_rows),
        used_fallback=True,
        detail="NOAA fetch failed; using mock fallback (with real weather).",
    )


def _fetch_tidecheck_station(
    client: httpx.Client,
    station: Station,
) -> tuple[str | None, dict | None]:
    headers = {"X-API-Key": settings.tidecheck_api_key}
    response = client.get(
        f"{settings.tidecheck_base_url.rstrip('/')}/api/stations/nearest",
        params={"lat": station.latitude, "lng": station.longitude},
        headers=headers,
    )
    response.raise_for_status()
    payload = response.json()
    
    # Handle both list and dict response formats
    if isinstance(payload, list):
        station_payload = payload[0] if payload else None
    else:
        station_payload = payload.get("data") or payload.get("station") or payload
        if isinstance(station_payload, list):
            station_payload = station_payload[0] if station_payload else None
            
    if not station_payload or not isinstance(station_payload, dict):
        return None, None
        
    station_id = (
        station_payload.get("id")
        or station_payload.get("station_id")
        or station_payload.get("code")
    )
    return str(station_id) if station_id else None, station_payload


def fetch_tidecheck_series(
    station: Station,
    start_at: datetime,
    end_at: datetime,
) -> ExternalFetchResult:
    weather_rows = None
    try:
        with _get_http_client() as client:
            weather_rows = _fetch_open_meteo_weather(client, station, start_at, end_at)
    except Exception:
        pass

    if not settings.tidecheck_api_key:
        return ExternalFetchResult(
            provider="tidecheck",
            source_label="mock_external",
            items=generate_mock_series(station, start_at, end_at, weather_rows=weather_rows),
            used_fallback=True,
            detail="Tidecheck API key is not configured; using mock fallback (with real weather).",
        )

    start_at = start_at.astimezone(UTC)
    end_at = end_at.astimezone(UTC)
    today_utc = datetime.combine(date.today(), datetime.min.time(), tzinfo=UTC)
    request_start = max(start_at, today_utc)
    days = max((end_at.date() - request_start.date()).days + 1, 1)

    try:
        with _get_http_client() as client:
            station_id, station_payload = _fetch_tidecheck_station(client, station)
            if not station_id:
                raise ValueError("No nearest Tidecheck station returned")

            headers = {"X-API-Key": settings.tidecheck_api_key}
            response = client.get(
                f"{settings.tidecheck_base_url.rstrip('/')}/api/station/{station_id}/tides",
                params={
                    "days": days,
                    "datum": settings.tidecheck_datum,
                    "start": request_start.strftime("%Y-%m-%d"),
                },
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()
            if not weather_rows:
                weather_rows = _fetch_open_meteo_weather(client, station, start_at, end_at)

        # Handle both list and dict response formats for series
        if isinstance(payload, list):
            series = payload
        else:
            series = (
                payload.get("data", {}).get("timeseries")
                or payload.get("data", {}).get("timeSeries")
                or payload.get("timeseries")
                or payload.get("timeSeries")
                or []
            )

        merged: dict[datetime, dict] = defaultdict(dict)
        for row in series:
            if not isinstance(row, dict): continue
            raw_time = row.get("time") or row.get("timestamp") or row.get("datetime")
            raw_height = next(
                (row.get(key) for key in ("height", "level", "value") if row.get(key) is not None),
                None,
            )
            if raw_time is None or raw_height is None:
                continue

            timestamp = _parse_api_datetime(raw_time)
            if timestamp < start_at or timestamp > end_at:
                continue
            if timestamp.minute != 0:
                continue

            height_m = float(raw_height)
            weather_row = _nearest_weather_row(weather_rows, timestamp)
            merged[timestamp].update(
                {
                    "water_level_cm": (height_m * 100) + 100, # Add 100cm baseline
                    "air_pressure_hpa": weather_row.get("air_pressure_hpa"),
                    "temperature_c": weather_row.get("temperature_c"),
                    "source": "tidecheck_tides",
                    "metadata": {
                        "station_external_id": station_id,
                        "nearest_station": station_payload,
                        "datum": settings.tidecheck_datum,
                        "weather_provider": "open-meteo",
                    },
                }
            )

        items = _normalize_rows("tidecheck", merged)
        if items:
            return ExternalFetchResult(
                provider="tidecheck",
                source_label="tidecheck_external",
                items=items,
                used_fallback=False,
                detail=f"Fetched Tidecheck data from station {station_id}.",
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Tidecheck fetch failed for %s: %s", station.code, exc)

    fallback_start = start_at if start_at >= today_utc else max(today_utc, end_at - timedelta(hours=24))
    return ExternalFetchResult(
        provider="tidecheck",
        source_label="mock_external",
        items=generate_mock_series(station, fallback_start, end_at, weather_rows=weather_rows),
        used_fallback=True,
        detail="Tidecheck fetch failed or unsupported historical range; using mock fallback (with real weather).",
    )


def fetch_external_series(
    station: Station,
    start_at: datetime,
    end_at: datetime,
    provider: str | None = None,
) -> ExternalFetchResult:
    selected_provider = (provider or settings.external_provider or "mock").lower()
    if selected_provider == "noaa":
        return fetch_noaa_series(station, start_at, end_at)
    if selected_provider == "tidecheck":
        return fetch_tidecheck_series(station, start_at, end_at)
    if selected_provider == "auto":
        tidecheck_result = fetch_tidecheck_series(station, start_at, end_at)
        if not tidecheck_result.used_fallback:
            return tidecheck_result
        noaa_result = fetch_noaa_series(station, start_at, end_at)
        if not noaa_result.used_fallback:
            return noaa_result
        return ExternalFetchResult(
            provider="auto",
            source_label="mock_external",
            items=generate_mock_series(station, start_at, end_at),
            used_fallback=True,
            detail="Auto provider fell back to mock data.",
        )

    weather_rows = None
    try:
        with _get_http_client() as client:
            weather_rows = _fetch_open_meteo_weather(client, station, start_at, end_at)
    except Exception:
        pass

    return ExternalFetchResult(
        provider="mock",
        source_label="mock_external",
        items=generate_mock_series(station, start_at, end_at, weather_rows=weather_rows),
        used_fallback=False,
        detail="Using deterministic mock provider (with real weather).",
    )


def ingest_external_series(
    db: Session,
    station: Station,
    series: list[dict],
    source_label: str = "external",
) -> int:
    if not series:
        return 0

    now = datetime.now(UTC)
    inserted = 0

    for row in series:
        recorded_at = row["recorded_at"]
        
        # Gelecek tahmini ise TidePrediction'a
        if recorded_at > now:
            hours_ahead = (recorded_at - now).total_seconds() / 3600.0
            dynamic_confidence = round(max(0.45, 0.98 - (hours_ahead * 0.012)), 4)
            
            existing_prediction = db.scalar(
                select(TidePrediction).where(
                    TidePrediction.station_id == station.id,
                    TidePrediction.prediction_time == recorded_at,
                )
            )
            if existing_prediction:
                existing_prediction.predicted_water_level_cm = row["water_level_cm"]
                existing_prediction.confidence_score = dynamic_confidence
                existing_prediction.model_version = f"api_{source_label}"
            else:
                db.add(
                    TidePrediction(
                        station_id=station.id,
                        prediction_time=recorded_at,
                        predicted_water_level_cm=row["water_level_cm"],
                        confidence_score=dynamic_confidence,
                        model_version=f"api_{source_label}",
                    )
                )
            inserted += 1
            continue

        # Geçmiş veri ise SensorReading'e
        exists = db.scalar(select(SensorReading.id).where(SensorReading.station_id == station.id, SensorReading.recorded_at == recorded_at))
        if not exists:
            noaa_entry = NOAAData(station_id=station.id, **row)
            reading_entry = SensorReading(station_id=station.id, recorded_at=recorded_at, water_level_cm=row["water_level_cm"], air_pressure_hpa=row["air_pressure_hpa"], temperature_c=row["temperature_c"], data_source=source_label)
            db.add(noaa_entry)
            db.add(reading_entry)
            inserted += 1

    db.commit()
    return inserted


def bootstrap_mock_history(db: Session, history_hours: int = 72) -> int:
    stations = list(db.scalars(select(Station).where(Station.is_active.is_(True))).all())
    total_inserted = 0
    end_at = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    start_at = end_at - timedelta(hours=history_hours)

    for station in stations:
        count = db.scalar(
            select(SensorReading.id).where(SensorReading.station_id == station.id).limit(1)
        )
        if count:
            continue
        result = fetch_external_series(station, start_at=start_at, end_at=end_at, provider="auto")
        total_inserted += ingest_external_series(
            db,
            station,
            result.items,
            source_label="bootstrap" if result.used_fallback else result.source_label,
        )

    return total_inserted


def refresh_recent_external_data(
    db: Session,
    lookback_hours: int = 24,
    forecast_hours: int | None = None,
    provider: str | None = None,
) -> dict:
    stations = list(db.scalars(select(Station).where(Station.is_active.is_(True))).all())
    total_inserted = 0
    details: list[dict] = []
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    start_at = now - timedelta(hours=lookback_hours)
    end_at = now + timedelta(hours=forecast_hours or settings.prediction_horizon_hours)

    for station in stations:
        result = fetch_external_series(
            station,
            start_at=start_at,
            end_at=end_at,
            provider=provider,
        )
        inserted = ingest_external_series(db, station, result.items, source_label=result.source_label)
        total_inserted += inserted
        details.append(
            {
                "station_id": station.id,
                "station_code": station.code,
                "provider": result.provider,
                "inserted": inserted,
                "used_fallback": result.used_fallback,
                "detail": result.detail,
            }
        )

    return {
        "provider_requested": provider or settings.external_provider,
        "inserted_total": total_inserted,
        "details": details,
    }


def latest_external_rows(db: Session, station_id: int | None = None, limit: int = 48) -> list[NOAAData]:
    query = (
        select(NOAAData)
        .join(Station)
        .where(Station.is_active.is_(True))
        .order_by(NOAAData.recorded_at.desc())
        .limit(limit)
    )
    if station_id:
        query = query.where(NOAAData.station_id == station_id)
    return list(db.scalars(query).all())
