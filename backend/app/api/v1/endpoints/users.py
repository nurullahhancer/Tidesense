from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.constants import UserRole
from app.db.session import get_db
from app.models import User
from app.schemas.user import (
    UserCreateRequest,
    UserPasswordUpdateRequest,
    UserRead,
    UserRoleUpdateRequest,
)
from app.services.user_service import (
    create_user,
    delete_user,
    list_users,
    update_user_password,
    update_user_role,
)

from app.websocket.manager import connection_manager

router = APIRouter(prefix="/users", tags=["users"])


def ensure_admin_can_manage_target(current_user: User, target_user: User) -> None:
    if current_user.role == UserRole.ADMIN and target_user.role not in [
        UserRole.USER,
        UserRole.RESEARCHER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Adminler sadece User ve Researcher hesaplarını yönetebilir",
        )


@router.get("", response_model=list[UserRead], summary="Admin kullanıcı listesini döndürür")
def get_users(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    active_user_ids = connection_manager.active_user_ids
    users = []
    for user in list_users(db):
        user_read = UserRead.model_validate(user)
        if user.id in active_user_ids:
            user_read.is_active = True
        if current_user.role != UserRole.SUPER_ADMIN:
            user_read.last_login_at = None
            user_read.last_login_ip = None
            user_read.last_login_user_agent = None
            user_read.last_login_device = None
            user_read.last_login_os = None
            user_read.last_login_browser = None
        users.append(user_read)
    return users


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı oluşturur",
)
def post_user(
    payload: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    if current_user.role == UserRole.SUPER_ADMIN:
        if payload.role == UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Yeni Ana Admin oluşturulamaz",
            )
        return UserRead.model_validate(create_user(db, payload))

    if current_user.role == UserRole.ADMIN:
        # Normal adminler sadece user ve researcher oluşturabilir
        if payload.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Adminler sadece User ve Researcher oluşturabilir",
            )
        return UserRead.model_validate(create_user(db, payload))

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Bu işlem için yetkiniz yok",
    )


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Kullanıcı rolünü günceller",
)
def patch_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Yetersiz yetki")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    ensure_admin_can_manage_target(current_user, target_user)

    # Ana adminin yetkisi değiştirilemez (sadece kendisi belki ama genellikle kilitlenir)
    if target_user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Ana admin yetkisi değiştirilemez")

    if payload.role == UserRole.SUPER_ADMIN and target_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Yeni Ana Admin oluşturulamaz")

    # Normal admin birini admin yapamaz
    if current_user.role == UserRole.ADMIN and payload.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Adminler yetki yükseltemez")

    return UserRead.model_validate(update_user_role(db, user_id, payload.role))


@router.patch(
    "/{user_id}/password",
    response_model=UserRead,
    summary="Kullanıcı şifresini sıfırlar",
)
def patch_user_password(
    user_id: int,
    payload: UserPasswordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Yetersiz yetki")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    ensure_admin_can_manage_target(current_user, target_user)

    if target_user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Ana admin şifresi değiştirilemez")

    return UserRead.model_validate(update_user_password(db, user_id, payload.password))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kullanıcıyı siler",
)
def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Yetersiz yetki")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Current admin user cannot be deleted")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    ensure_admin_can_manage_target(current_user, target_user)

    if target_user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Ana admin silinemez")

    delete_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
