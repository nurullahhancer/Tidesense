from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserCreateRequest, UserRead
from app.services.auth_service import authenticate_user
from app.services.device_service import collect_login_device_info
from app.services.user_service import create_user
from app.core.constants import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=UserRead,
    summary="Yeni kullanıcı kaydı oluşturur",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserRead:
    user_create_payload = UserCreateRequest(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=UserRole.USER,
        email_notifications_enabled=payload.email_notifications_enabled,
    )
    user = create_user(db, user_create_payload)
    return UserRead.model_validate(user)

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
