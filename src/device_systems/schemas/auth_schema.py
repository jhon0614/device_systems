from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def validate_secure_password(password: str):
    """Validar las reglas mínimas de seguridad de la contraseña."""
    if any(character.isspace() for character in password):
        raise ValueError("La contraseña no puede contener espacios")
    if not any(character.isupper() for character in password):
        raise ValueError("La contraseña debe incluir una mayúscula")
    if not any(character.islower() for character in password):
        raise ValueError("La contraseña debe incluir una minúscula")
    if not any(character.isdigit() for character in password):
        raise ValueError("La contraseña debe incluir un número")
    return password


class UserRegister(BaseModel):
    name: str = Field(min_length=3, description="Nombre del usuario")
    email: EmailStr
    password: str = Field(min_length=8, description="Contraseña segura")
    role: Literal["admin", "support", "user"] = "user"
    is_active: bool = True

    _validate_password = field_validator("password")(validate_secure_password)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    # Permite validar los datos recuperados del token JWT.
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr | None = None
