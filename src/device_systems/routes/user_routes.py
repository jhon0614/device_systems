from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from device_systems.dependencies.database_dependency import get_db
from device_systems.dependencies.user_dependencies import (
    get_email_validator,
    get_user_or_404,
)
from device_systems.models.user_model import User
from device_systems.schemas.user_schema import (
    UserCreate,
    UserPatch,
    UserResponse,
    UserUpdate,
)
from device_systems.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


def add_headers(response: Response):
    # Agregar las cabeceras comunes del recurso users.
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0"


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Lista, filtra y ordena los usuarios guardados en la base de datos.",
)
def list_users(
    response: Response,
    role: Literal["admin", "support", "user"] | None = None,
    is_active: bool | None = None,
    order_by: Literal["name", "created_at"] = "name",
    db: Session = Depends(get_db),
):
    add_headers(response)
    return user_service.get_users(db, role, is_active, order_by)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario",
    description="Busca un usuario por su ID en la base de datos.",
)
def get_user(
    response: Response,
    user: User = Depends(get_user_or_404),
):
    add_headers(response)
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Guarda un usuario nuevo en la base de datos.",
)
def create_user(
    user_data: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
    validate_email=Depends(get_email_validator),
):
    add_headers(response)
    validate_email(str(user_data.email))
    return user_service.create_user(db, user_data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario completo",
    description="Reemplaza todos los datos de un usuario existente.",
)
def update_user(
    user_data: UserUpdate,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_or_404),
    validate_email=Depends(get_email_validator),
):
    add_headers(response)
    validate_email(str(user_data.email), user.id)
    return user_service.update_user(db, user, user_data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario parcialmente",
    description="Modifica solamente los campos enviados por el cliente.",
)
def patch_user(
    user_data: UserPatch,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_or_404),
    validate_email=Depends(get_email_validator),
):
    add_headers(response)
    # exclude_unset evita modificar campos que no llegaron en el JSON.
    fields_to_update = user_data.model_dump(exclude_unset=True)

    if not fields_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo",
        )

    if any(value is None for value in fields_to_update.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Los campos no pueden ser nulos",
        )

    if "email" in fields_to_update:
        validate_email(str(fields_to_update["email"]), user.id)

    return user_service.patch_user(db, user, fields_to_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario de la base de datos.",
)
def delete_user(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_or_404),
):
    add_headers(response)
    user_service.delete_user(db, user)
