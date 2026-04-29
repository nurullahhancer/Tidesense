from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Station


def list_stations(db: Session, active_only: bool = False) -> list[Station]:
    query = select(Station).order_by(Station.name.asc())
    if active_only:
        query = query.where(Station.is_active.is_(True))
    return list(db.scalars(query).all())


def get_station_or_404(db: Session, station_id: int) -> Station:
    station = db.get(Station, station_id)
    if station is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Station not found")
    return station
