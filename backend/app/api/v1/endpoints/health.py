from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.constants import UserRole
from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.health_service import collect_health_snapshot

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Sistem sağlık özetini döndürür",
)
def get_health(
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> HealthResponse:
    return HealthResponse(**collect_health_snapshot(db))
