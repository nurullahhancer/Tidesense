from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import authenticate_user
from app.services.device_service import collect_login_device_info

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="JWT erişim anahtarı üretir",
    description="Kullanıcı adı ve şifreyle giriş yapar, rol bilgisini token içine ekler.",
)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return authenticate_user(
        db,
        payload,
        collect_login_device_info(
            request,
            platform_hint=payload.device_platform,
        ),
    )


@router.get(
    "/me",
    response_model=UserRead,
    summary="Aktif kullanıcı profilini döndürür",
)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
