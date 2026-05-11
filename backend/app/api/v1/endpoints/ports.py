import random
from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.constants import UserRole
from app.db.session import get_db
from app.models import Port, User, Station, CameraSnapshot, SensorReading
from app.schemas.port import PortCreate, PortDetailResponse, PortListResponse, PortRead, PortUpdate

from app.routers.weather import get_weather

router = APIRouter(prefix="/ports", tags=["ports"], dependencies=[Depends(get_current_user)])


@router.get(
    "",
    response_model=PortListResponse,
    summary="Liman listesini döndürür",
)
def get_ports(
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> PortListResponse:
    query = db.query(Port)
    if active_only:
        query = query.filter(Port.is_active == True)
    ports = query.order_by(Port.name).all()
    items = [PortRead.model_validate(p) for p in ports]
    return PortListResponse(items=items, total=len(items))


@router.get(
    "/{port_id}",
    response_model=PortDetailResponse,
    summary="Tek liman detayını döndürür",
)
def get_port(port_id: int, db: Session = Depends(get_db)) -> PortDetailResponse:
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Liman bulunamadı")
    return PortDetailResponse(port=PortRead.model_validate(port))


@router.post(
    "",
    response_model=PortDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni liman ekler",
)
async def create_port(
    payload: PortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
) -> PortDetailResponse:
    print(f"DEBUG: Creating port: {payload.name}")
    port = Port(
        name=payload.name,
        city=payload.city,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
        description=payload.description,
        is_active=True,
    )
    db.add(port)
    db.flush() # ID alabilmek için
    print(f"DEBUG: Port created with ID: {port.id}")
    
    # Yeni liman için otomatik bir istasyon oluştur
    station_code = f"{payload.city.upper()}_{port.id}_{int(datetime.now().timestamp())}"
    print(f"DEBUG: Creating station with code: {station_code}")
    station = Station(
        name=f"{payload.name} İstasyonu",
        code=station_code,
        latitude=payload.latitude,
        longitude=payload.longitude,
        city=payload.city,
        port_id=port.id,
        is_active=True
    )
    db.add(station)
    db.flush()
    print(f"DEBUG: Station created with ID: {station.id}")
    
    # Kamera kısmında gözükmesi için bir snapshot ekle
    snap = CameraSnapshot(
        station_id=station.id,
        snapshot_url="https://images.unsplash.com/photo-1551244072-5d12893278ab?auto=format&fit=crop&w=960&h=540",
        detected_water_level_cm=100.0,
        risk_status="NORMAL",
        captured_at=datetime.now(UTC),
    )
    db.add(snap)

    # Hava durumunu koordinatlara göre GERÇEK olarak çek
    now = datetime.now(UTC)
    temp = 20.0
    press = 1010.0
    try:
        print(f"DEBUG: Fetching weather for {payload.latitude}, {payload.longitude}")
        weather = await get_weather(lat=payload.latitude, lon=payload.longitude)
        temp = weather.get("temperature_c", 20.0)
        press = weather.get("air_pressure_hpa", 1010.0)
        print(f"DEBUG: Weather fetched: {temp}C, {press}hPa")
    except Exception as e:
        print(f"DEBUG: Weather fetch failed: {e}")
        seed = int(abs(payload.latitude) * 100 + abs(payload.longitude) * 100) + now.hour
        random.seed(seed)
        temp = 15 + random.random() * 10
        press = 1005 + random.random() * 15

    reading = SensorReading(
        station_id=station.id,
        recorded_at=now,
        water_level_cm=100.0 + (random.random() * 10 - 5),
        air_pressure_hpa=press,
        temperature_c=temp,
        data_source="initial_setup"
    )
    db.add(reading)
    
    db.commit()
    print(f"DEBUG: Transaction committed.")
    db.refresh(port)
    return PortDetailResponse(port=PortRead.model_validate(port))


@router.patch(
    "/{port_id}",
    response_model=PortDetailResponse,
    summary="Liman bilgilerini günceller",
)
def update_port(
    port_id: int,
    payload: PortUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
) -> PortDetailResponse:
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Liman bulunamadı")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(port, field, value)

    db.commit()
    db.refresh(port)
    return PortDetailResponse(port=PortRead.model_validate(port))


@router.delete(
    "/{port_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Limanı veritabanından kalıcı olarak siler",
)
def delete_port(
    port_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
) -> Response:
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Liman bulunamadı")
    
    db.delete(port)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
