from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session

from app.models import Station, Port


def list_stations(db: Session, active_only: bool = False) -> list[Station]:
    query = select(Station).order_by(Station.name.asc())
    if active_only:
        # Join with Port to check Port.is_active.
        # If a station has no port, we still show it if it's active.
        # If a station has a port, both must be active.
        query = query.outerjoin(Port).where(
            Station.is_active.is_(True),
            or_(Port.id.is_(None), Port.is_active.is_(True))
        )
    return list(db.scalars(query).all())


def get_station_or_404(db: Session, station_id: int) -> Station:
    station = db.get(Station, station_id)
    if station is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Station not found")
    return station
