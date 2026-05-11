from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.camera import CameraFeedRead, CameraListResponse
from app.schemas.station import StationRead
from app.services.camera_service import ensure_camera_snapshots, list_camera_feeds

router = APIRouter(prefix="/cameras", tags=["cameras"], dependencies=[Depends(get_current_user)])


@router.get(
    "",
    response_model=CameraListResponse,
    summary="İstasyon kamera akışlarını ve overlay bilgilerini döndürür",
)
def get_cameras(
    station_id: int | None = None,
    db: Session = Depends(get_db),
) -> CameraListResponse:
    ensure_camera_snapshots(db)
    items = [
        CameraFeedRead(
            station=StationRead.model_validate(item["station"]),
            snapshot_url=item["snapshot_url"],
            stream_url=item["stream_url"],
            detected_water_level_cm=item["detected_water_level_cm"],
            risk_status=item["risk_status"],
            resolution=item["resolution"],
            fps=item["fps"],
            captured_at=item["captured_at"],
        )
        for item in list_camera_feeds(db, station_id=station_id)
    ]
    return CameraListResponse(items=items, total=len(items))
