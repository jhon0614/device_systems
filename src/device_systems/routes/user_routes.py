from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status

from device_systems.dependencies.user_dependencies import (
    get_email_validator,
    get_user_or_404,
)
from device_systems.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from device_systems.services.user_service import (
    create_user,
    delete_user,
    get_all_users,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


def add_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0"


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Retorna todos los usuarios y permite filtrar por rol o estado.",
    response_description="Lista de usuarios",
)
async def list_users(
    response: Response,
    role: Optional[Literal["admin", "support", "user"]] = None,
    is_active: Optional[bool] = None,
):
    add_headers(response)
    users = get_all_users()

    if role is not None:
        users = [user for user in users if user["role"] == role]
    if is_active is not None:
        users = [user for user in users if user["is_active"] == is_active]

    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario",
    description="Busca un usuario por su ID.",
    response_description="Usuario encontrado",
)
async def get_user(response: Response, user=Depends(get_user_or_404)):
    add_headers(response)
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Registra un usuario nuevo y evita correos duplicados.",
    response_description="Usuario creado",
)
async def post_user(
    user_data: UserCreate,
    response: Response,
    validate_email=Depends(get_email_validator),
):
    add_headers(response)
    validate_email(str(user_data.email))
    return create_user(user_data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario completo",
    description="Reemplaza todos los datos de un usuario existente.",
    response_description="Usuario actualizado",
)
async def put_user(
    user_data: UserCreate,
    response: Response,
    user=Depends(get_user_or_404),
    validate_email=Depends(get_email_validator),
):
    add_headers(response)
    validate_email(str(user_data.email), user["id"])
    return update_user(user, user_data.model_dump())


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario parcialmente",
    description="Modifica solamente los campos enviados por el cliente.",
    response_description="Usuario actualizado",
)
async def patch_user(
    user_data: UserUpdate,
    response: Response,
    user=Depends(get_user_or_404),
    validate_email=Depends(get_email_validator),
):
    add_headers(response)
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

    if user_data.email is not None:
        validate_email(str(user_data.email), user["id"])

    return update_user(user, fields_to_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente.",
    response_description="Usuario eliminado",
)
async def remove_user(response: Response, user=Depends(get_user_or_404)):
    add_headers(response)
    delete_user(user)
