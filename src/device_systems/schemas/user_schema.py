from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from device_systems.schemas.auth_schema import validate_secure_password


class UserCreate(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["admin", "support", "user"]
    is_active: bool = True

    _validate_password = field_validator("password")(validate_secure_password)


class UserUpdate(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool


class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=3)
    email: EmailStr | None = None
    role: Literal["admin", "support", "user"] | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    # Permite convertir un objeto SQLAlchemy en una respuesta Pydantic.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool
    created_at: datetime



