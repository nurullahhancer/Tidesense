from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import User
from app.schemas.user import UserCreateRequest


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="User not found")
    return user


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.asc())).all())


def create_user(db: Session, payload: UserCreateRequest) -> User:
    from fastapi import HTTPException

    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    if payload.email:
        existing_email = db.scalar(select(User).where(User.email == payload.email))
        if existing_email:
            raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        email_notifications_enabled=payload.email_notifications_enabled,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_role(db: Session, user_id: int, role: str) -> User:
    user = get_user_or_404(db, user_id)
    user.role = role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, password: str) -> User:
    user = get_user_or_404(db, user_id)
    user.password_hash = get_password_hash(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
