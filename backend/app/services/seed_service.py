from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import DEFAULT_STATIONS, DEMO_USERS
from app.core.security import get_password_hash
from app.models import MoonPosition, Station, User
from app.services.camera_service import ensure_camera_snapshots
from app.services.external_data_service import bootstrap_mock_history
from app.services.moon_service import record_moon_snapshot


def seed_stations(db: Session) -> None:
    default_codes = {station_payload["code"] for station_payload in DEFAULT_STATIONS}
    existing_by_code = {
        station.code: station
        for station in db.scalars(select(Station)).all()
    }

    for station in existing_by_code.values():
        station.is_active = station.code in default_codes

    for station_payload in DEFAULT_STATIONS:
        station = existing_by_code.get(station_payload["code"])
        if station is None:
            db.add(
                Station(
                    name=station_payload["name"],
                    code=station_payload["code"],
                    latitude=station_payload["latitude"],
                    longitude=station_payload["longitude"],
                    city=station_payload["city"],
                    is_active=True,
                )
            )
            continue

        station.name = station_payload["name"]
        station.latitude = station_payload["latitude"]
        station.longitude = station_payload["longitude"]
        station.city = station_payload["city"]
        station.is_active = True

    db.commit()


def seed_users(db: Session) -> None:
    existing_users = {user.username: user for user in db.scalars(select(User)).all()}
    for user_payload in DEMO_USERS:
        user = existing_users.get(user_payload["username"])
        if user is None:
            db.add(
                User(
                    username=user_payload["username"],
                    password_hash=get_password_hash(user_payload["password"]),
                    role=user_payload["role"],
                    failed_attempts=0,
                    is_blocked=False
                )
            )
        else:
            # Update password and role if needed
            user.password_hash = get_password_hash(user_payload["password"])
            user.role = user_payload["role"]
            # Ensure new fields are set for existing users
            if user.failed_attempts is None:
                user.failed_attempts = 0
            if user.is_blocked is None:
                user.is_blocked = False
            
    db.commit()


def seed_moon_history(db: Session, hours: int = 72) -> None:
    already_exists = db.scalar(select(MoonPosition.id).limit(1))
    if already_exists:
        return
    station = db.scalar(
        select(Station)
        .where(Station.is_active.is_(True))
        .order_by(Station.id.asc())
    )
    if station is None:
        return
    end_at = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    start_at = end_at - timedelta(hours=hours)
    current = start_at
    while current <= end_at:
        record_moon_snapshot(db, station=station, at_time=current)
        current += timedelta(hours=1)


def bootstrap_initial_data(db: Session) -> None:
    seed_stations(db)
    seed_users(db)
    seed_moon_history(db, settings.bootstrap_history_hours)
    bootstrap_mock_history(db, settings.bootstrap_history_hours)
    ensure_camera_snapshots(db)
