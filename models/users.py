from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    """Роли стенда юзер < менеджер < админ"""

    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = " ADMIN"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=100)
    phone: str | None = None
    invite_code: str | None = None

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72)

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: str | None
    role: Role
    is_active: bool
    created_at: datetime


class RegisteredUser(BaseModel):
    registration: RegisterRequest
    profile: UserResponse

    @property
    def credentials(self) -> tuple[str, str]:
        return self.registration.email, self.registration.password


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
