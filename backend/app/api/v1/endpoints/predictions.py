from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.constants import UserRole
from app.db.session import get_db
from app.schemas.prediction import PredictionListResponse, PredictionSeries, TidePredictionRead
from app.schemas.station import StationRead
from app.services.prediction_service import generate_predictions_for_all_stations, generate_predictions_for_station, get_prediction_series

from app.models import User

router = APIRouter(prefix="/predictions", tags=["predictions"], dependencies=[Depends(get_current_user)])


@router.get(
    "",
    response_model=PredictionListResponse,
    summary="İstasyon bazlı gelgit tahminlerini döndürür",
)
def get_predictions(
    station_id: int | None = None,
    refresh: bool = False,
    force_retrain: bool = False,
    horizon_hours: int = Query(default=24, ge=1, le=72),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PredictionListResponse:
    if refresh or force_retrain:
        if current_user.role not in {UserRole.RESEARCHER.value, UserRole.ADMIN.value}:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Refresh/retrain requires researcher or admin role")
        if station_id:
            generate_predictions_for_station(
                db,
                station_id=station_id,
                horizon_hours=horizon_hours,
                force_retrain=force_retrain,
                persist=True,
            )
        else:
            generate_predictions_for_all_stations(db, force_retrain=force_retrain)

    series = get_prediction_series(db, station_id=station_id)
    items = [
        PredictionSeries(
            station=StationRead.model_validate(item["station"]),
            items=[TidePredictionRead(**prediction) for prediction in item["items"]],
            total=item["total"],
            rmse=item["rmse"],
            fallback_used=item["fallback_used"],
        )
        for item in series
    ]
    return PredictionListResponse(items=items, total=len(items))
