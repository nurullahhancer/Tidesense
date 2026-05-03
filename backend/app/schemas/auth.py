from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    device_platform: str | None = Field(default=None, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {"username": "marine_researcher", "password": "Research123!"}
        }
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
