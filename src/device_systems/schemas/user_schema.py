from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=3, examples=["Ana Torres"])
    email: EmailStr = Field(examples=["ana@example.com"])
    role: Literal["admin", "support", "user"]
    is_active: bool


class UserResponse(UserCreate):
    id: int
