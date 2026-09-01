from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Response

from device_systems.schemas.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

# Base de datos simulada con una lista.
users = []


def add_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"


@router.get("", response_model=list[UserResponse])
async def list_users(
    response: Response,
    role: Optional[Literal["admin", "support", "user"]] = None,
    is_active: Optional[bool] = None,
):
    add_headers(response)
    result = users

    if role is not None:
        result = [user for user in result if user["role"] == role]

    if is_active is not None:
        result = [user for user in result if user["is_active"] == is_active]

    return result


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(user_id: int, response: Response):
    add_headers(response)

    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
)
async def create_user(user_data: UserCreate, response: Response):
    add_headers(response)

    for user in users:
        if user["email"].lower() == str(user_data.email).lower():
            raise HTTPException(status_code=409, detail="El correo ya esta registrado")

    new_user = {
        "id": len(users) + 1,
        "name": user_data.name,
        "email": user_data.email,
        "role": user_data.role,
        "is_active": user_data.is_active,
    }
    users.append(new_user)
    return new_user
