from sqlalchemy.orm import Session

from device_systems.auth.security import get_password_hash, verify_password
from device_systems.models.user_model import User
from device_systems.services import user_service


def register_user(db: Session, user_data):
    # Convertir la contraseña en hash antes de crear el registro.
    user = User(
        name=user_data.name,
        email=str(user_data.email),
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = user_service.get_user_by_email(db, email)
    # Los usuarios creados antes de esta migración todavía no tienen un hash válido.
    if (
        user is None
        or not user.hashed_password
        or not verify_password(password, user.hashed_password)
    ):
        return None
    return user
