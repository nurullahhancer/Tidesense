from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.moon import MoonPositionRead
from app.services.moon_service import calculate_moon_snapshot
from app.services.station_service import get_station_or_404, list_stations

router = APIRouter(prefix="/moon", tags=["moon"], dependencies=[Depends(get_current_user)])


@router.get(
    "/current",
    response_model=MoonPositionRead,
    summary="Anlık ay konumu ve çekim verisini döndürür",
)
def get_current_moon(
    station_id: int | None = None,
    db: Session = Depends(get_db),
) -> MoonPositionRead:
    if station_id is not None:
        station = get_station_or_404(db, station_id)
        snapshot = calculate_moon_snapshot(station.latitude, station.longitude)
        return MoonPositionRead(**snapshot, station_id=station.id, station_name=station.name)

    station = list_stations(db, active_only=True)[0]
    snapshot = calculate_moon_snapshot(station.latitude, station.longitude)
    return MoonPositionRead(**snapshot, station_id=station.id, station_name=station.name)
