from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from device_systems.dependencies.database_dependency import get_db
from device_systems.models.user_model import User
from device_systems.services import user_service


def get_user_or_404(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    # Esta busqueda se reutiliza en GET, PUT, PATCH y DELETE.
    user = user_service.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return user


def get_email_validator(db: Session = Depends(get_db)):
    # Retorna una sola funcion para validar correos en varias rutas.
    def validate_email(email: str, ignored_user_id: int = None):
        user = user_service.get_user_by_email(db, email)

        # En PUT y PATCH se permite conservar el correo del mismo usuario.
        if user and user.id != ignored_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya esta registrado",
            )

    return validate_email
