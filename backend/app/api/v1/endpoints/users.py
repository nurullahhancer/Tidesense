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

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead], summary="Admin kullanıcı listesini döndürür")
def get_users(
    _: object = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    return [UserRead.model_validate(user) for user in list_users(db)]


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı oluşturur",
)
def post_user(
    payload: UserCreateRequest,
    _: object = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserRead:
    return UserRead.model_validate(create_user(db, payload))


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Kullanıcı rolünü günceller",
)
def patch_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    _: object = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserRead:
    target_user = db.query(User).filter(User.id == user_id).first()
    if target_user and target_user.username == "tidesense" and current_user.username != "tidesense":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Ana admin yetkisi değiştirilemez")
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
    _: object = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserRead:
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.username == "tidesense" and current_user.username != "tidesense":
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
    _: object = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> Response:
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Current admin user cannot be deleted")
        
    target_user = db.query(User).filter(User.id == user_id).first()
    if target_user and target_user.username == "tidesense" and current_user.username != "tidesense":
        raise HTTPException(status_code=403, detail="Ana admin silinemez")
        
    delete_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
