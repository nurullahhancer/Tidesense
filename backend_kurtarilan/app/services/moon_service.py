from datetime import UTC, datetime
from math import degrees

import ephem
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MoonPosition, Station


def _phase_label(illumination: float) -> str:
    if illumination < 2:
        return "New Moon"
    if illumination < 25:
        return "Waxing Crescent"
    if illumination < 50:
        return "First Quarter"
    if illumination < 75:
        return "Waxing Gibbous"
    if illumination < 98:
        return "Full Moon"
    return "Full Moon"


def _phase_by_longitude(elong: float) -> str:
    degree = elong % 360
    if degree < 45:
        return "Waxing Crescent"
    if degree < 90:
        return "First Quarter"
    if degree < 135:
        return "Waxing Gibbous"
    if degree < 180:
        return "Full Moon"
    if degree < 225:
        return "Waning Gibbous"
    if degree < 270:
        return "Last Quarter"
    if degree < 315:
        return "Waning Crescent"
    return "New Moon"


def calculate_moon_snapshot(latitude: float, longitude: float, at_time: datetime | None = None) -> dict:
    timestamp = at_time or datetime.now(UTC)
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = timestamp
    moon = ephem.Moon(observer)

    illumination = float(moon.phase) / 100.0
    altitude = degrees(float(moon.alt))
    azimuth = degrees(float(moon.az))
    distance = float(moon.earth_distance)
    average_distance = 0.00257
    gravity_factor = round((average_distance / distance) ** 2, 6)
    phase_name = _phase_by_longitude(degrees(float(moon.elong)))
    if phase_name == "New Moon" and illumination > 0.97:
        phase_name = "Full Moon"

    return {
        "calculated_at": timestamp,
        "moon_phase": phase_name if illumination > 0.01 else "New Moon",
        "moon_illumination": round(illumination, 4),
        "gravity_factor": gravity_factor,
        "altitude": round(altitude, 4),
        "azimuth": round(azimuth, 4),
    }


def record_moon_snapshot(db: Session, station: Station | None = None, at_time: datetime | None = None) -> MoonPosition:
    if station is None:
        station = db.scalar(select(Station).order_by(Station.id.asc()))
        if station is None:
            raise ValueError("No station found for moon snapshot")

    payload = calculate_moon_snapshot(station.latitude, station.longitude, at_time=at_time)
    moon_position = MoonPosition(**payload)
    db.add(moon_position)
    db.commit()
    db.refresh(moon_position)
    return moon_position


def get_latest_moon_position(db: Session) -> MoonPosition | None:
    return db.scalar(select(MoonPosition).order_by(MoonPosition.calculated_at.desc()))
