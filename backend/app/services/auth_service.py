from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead


def authenticate_user(
    db: Session,
    credentials: LoginRequest,
    device_info: dict | None = None,
) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == credentials.username))
    
    if user:
        if user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hesabınız bloke edilmiştir. Lütfen yönetici ile iletişime geçin.",
            )
        
        now = datetime.now(timezone.utc)
        if user.lockout_until and now < user.lockout_until:
            wait_seconds = int((user.lockout_until - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Çok fazla hatalı giriş denemesi. Lütfen {wait_seconds} saniye bekleyin.",
            )

    if user is None or not verify_password(credentials.password, user.password_hash):
        if user:
            user.failed_attempts += 1
            
            # 5 failed -> 10 seconds
            if user.failed_attempts == 5:
                user.lockout_until = datetime.now(timezone.utc) + timedelta(seconds=10)
            # 10 failed -> 10 minutes
            elif user.failed_attempts == 10:
                user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=10)
            # 15 failed -> 1 hour
            elif user.failed_attempts == 15:
                user.lockout_until = datetime.now(timezone.utc) + timedelta(hours=1)
            # > 15 -> Blocked
            elif user.failed_attempts > 15:
                user.is_blocked = True
            
            db.commit()
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
        )

    # Success
    user.failed_attempts = 0
    user.lockout_until = None
    if device_info:
        for field, value in device_info.items():
            setattr(user, field, value)
    db.commit()
    db.refresh(user)

    expires_in = settings.access_token_expire_minutes * 60
    access_token = create_access_token(
        subject=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )
