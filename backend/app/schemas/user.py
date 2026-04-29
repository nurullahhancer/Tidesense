from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class UserRead(ORMModel):
    id: int
    username: str
    role: str
    created_at: datetime


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(user|researcher|admin)$")


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(pattern="^(user|researcher|admin)$")


class UserPasswordUpdateRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
