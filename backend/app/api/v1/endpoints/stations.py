from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.core.constants import UserRole
from app.models import Station, CameraSnapshot, User
from app.schemas.station import StationDetailResponse, StationListResponse, StationRead, StationCreate
from app.services.station_service import get_station_or_404, list_stations

router = APIRouter(prefix="/stations", tags=["stations"], dependencies=[Depends(get_current_user)])


@router.get(
    "",
    response_model=StationListResponse,
    summary="İstasyon listesini döndürür",
)
def get_stations(
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> StationListResponse:
    items = [StationRead.model_validate(station) for station in list_stations(db, active_only=active_only)]
    return StationListResponse(items=items, total=len(items))


@router.get(
    "/{station_id}",
    response_model=StationDetailResponse,
    summary="Tek istasyon detayını döndürür",
)
def get_station(station_id: int, db: Session = Depends(get_db)) -> StationDetailResponse:
    return StationDetailResponse(station=StationRead.model_validate(get_station_or_404(db, station_id)))


@router.post(
    "",
    response_model=StationDetailResponse,
    summary="Yeni istasyon ve kamera (isteğe bağlı) ekler",
)
def create_station(
    payload: StationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> StationDetailResponse:
    existing = db.query(Station).filter(Station.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Station code already exists")

    station = Station(
        name=payload.name,
        code=payload.code,
        latitude=payload.latitude,
        longitude=payload.longitude,
        city=payload.city,
        is_active=True,
    )
    db.add(station)
    db.commit()
    db.refresh(station)

    if payload.snapshot_url:
        snap = CameraSnapshot(
            station_id=station.id,
            snapshot_url=payload.snapshot_url,
            detected_water_level_cm=100.0,
            risk_status="NORMAL",
            captured_at=datetime.now(UTC),
        )
        db.add(snap)
        db.commit()

    return StationDetailResponse(station=StationRead.model_validate(station))
