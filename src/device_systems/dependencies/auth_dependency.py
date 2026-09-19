from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from device_systems.auth.security import decode_access_token
from device_systems.dependencies.database_dependency import get_db
from device_systems.models.user_model import User
from device_systems.schemas.auth_schema import TokenData
from device_systems.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    token_data = TokenData(email=payload.get("sub"))
    if token_data.email is None:
        raise credentials_exception

    user = user_service.get_user_by_email(db, str(token_data.email))
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(user: User = Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )
    return user


def require_admin(user: User = Depends(get_current_active_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol admin",
        )
    return user


def require_admin_or_support(user: User = Depends(get_current_active_user)):
    if user.role not in ("admin", "support"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol admin o support",
        )
    return user
