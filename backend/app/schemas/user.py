from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class UserRead(ORMModel):
    id: int
    username: str
    email: str | None = None
    role: str
    is_active: bool = False
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    last_login_user_agent: str | None = None
    last_login_device: str | None = None
    last_login_os: str | None = None
    last_login_browser: str | None = None
    email_notifications_enabled: bool = False
    created_at: datetime


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: str = Field(..., max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(pattern="^(user|researcher|admin|super_admin)$")
    email_notifications_enabled: bool = False


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(pattern="^(user|researcher|admin|super_admin)$")


class UserPasswordUpdateRequest(BaseModel):
    password: str = Field(min_length=6, max_length=128)
