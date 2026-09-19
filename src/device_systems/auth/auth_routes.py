from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from device_systems.auth import auth_service
from device_systems.auth.security import create_access_token
from device_systems.dependencies.auth_dependency import get_current_active_user
from device_systems.dependencies.database_dependency import get_db
from device_systems.dependencies.user_dependencies import get_email_validator
from device_systems.middlewares.request_middleware import limiter
from device_systems.models.user_model import User
from device_systems.schemas.auth_schema import Token, UserRegister
from device_systems.schemas.user_schema import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Crea un usuario y almacena su contraseña como hash.",
)
@limiter.limit("3/minute")
def register_user(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db),
    validate_email=Depends(get_email_validator),
):
    # Reutilizar la misma dependencia de correo único empleada por /users.
    validate_email(str(user_data.email))
    return auth_service.register_user(db, user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Valida las credenciales y genera un token JWT.",
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2 usa el campo username; en esta API contiene el correo.
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Consultar usuario autenticado",
    description="Retorna los datos del usuario asociado al token.",
)
def get_me(user: User = Depends(get_current_active_user)):
    return user
