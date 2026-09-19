from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from device_systems.dependencies.database_dependency import get_db
from device_systems.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin_or_support,
)
from device_systems.dependencies.device_dependencies import get_device_or_404
from device_systems.dependencies.loan_dependencies import get_loan_or_404
from device_systems.dependencies.user_dependencies import get_user_or_404
from device_systems.models.device_model import Device
from device_systems.models.loan_model import Loan
from device_systems.models.user_model import User
from device_systems.middlewares.request_middleware import limiter
from device_systems.schemas.loan_schema import (
    LoanCreate,
    LoanDetailResponse,
    LoanResponse,
    LoanStatus,
)
from device_systems.services import device_service, loan_service, user_service

router = APIRouter(tags=["Loans"])


@router.get(
    "/loans",
    response_model=list[LoanDetailResponse],
    summary="Listar prestamos",
    description="Consulta prestamos con joins y filtros opcionales.",
    response_description="Lista de prestamos con usuario y dispositivo",
)
def list_loans(
    loan_status: LoanStatus | None = Query(default=None, alias="status"),
    user_email: str | None = None,
    device_type: str | None = None,
    loan_date_from: datetime | None = None,
    loan_date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    if loan_date_from and loan_date_to:
        if loan_date_from > loan_date_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha inicial no puede ser mayor que la fecha final",
            )


    return loan_service.get_loans(
        db,
        loan_status,
        user_email,
        device_type,
        loan_date_from,
        loan_date_to,
    )


@router.get(
    "/loans/details",
    response_model=list[LoanDetailResponse],
    summary="Consultar detalles de prestamos",
    description="Muestra cada prestamo con su usuario y dispositivo relacionados.",
    response_description="Detalles de prestamos",
)
def get_loan_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support),
):
    return loan_service.get_loans(db)


@router.get(
    "/loans/{loan_id}",
    response_model=LoanDetailResponse,
    summary="Consultar prestamo",
    description="Busca un prestamo por su ID.",
    response_description="Prestamo encontrado",
)
def get_loan(loan: Loan = Depends(get_loan_or_404)):
    return loan


@router.post(
    "/loans",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear prestamo",
    description="Asocia un dispositivo disponible con un usuario existente.",
    response_description="Prestamo creado",
)
@limiter.limit("10/minute")
def create_loan(
    request: Request,
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = user_service.get_user_by_id(db, loan_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    device = device_service.get_device_by_id(db, loan_data.device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )
    if not device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El dispositivo no esta disponible",
        )

    return loan_service.create_loan(db, user, device)


@router.patch(
    "/loans/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver dispositivo",
    description="Finaliza un prestamo y vuelve a habilitar el dispositivo.",
    response_description="Devolución exitosa",
)
def return_loan(
    db: Session = Depends(get_db),
    loan: Loan = Depends(get_loan_or_404),
    current_user: User = Depends(require_admin_or_support),
):
    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El equipo ya fue devuelto",
        )
    return loan_service.return_loan(db, loan)


@router.get(
    "/users/{user_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Consultar prestamos de un usuario",
    description="Muestra el historial de prestamos de un usuario.",
    response_description="Prestamos del usuario",
)
def get_user_loans(
    db: Session = Depends(get_db),
    user: User = Depends(get_user_or_404),
):
    return loan_service.get_user_loans(db, user.id)


@router.get(
    "/devices/{device_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Consultar historial de un dispositivo",
    description="Muestra todos los prestamos registrados para un dispositivo.",
    response_description="Prestamos del dispositivo",
)
def get_device_loans(
    db: Session = Depends(get_db),
    device: Device = Depends(get_device_or_404),
):
    return loan_service.get_device_loans(db, device.id)
