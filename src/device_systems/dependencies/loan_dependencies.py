from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from device_systems.dependencies.database_dependency import get_db
from device_systems.models.loan_model import Loan
from device_systems.services import loan_service


def get_loan_or_404(
    loan_id: int,
    db: Session = Depends(get_db),
) -> Loan:
    # Reutilizar la busqueda y el error 404 en las rutas de prestamos.
    loan = loan_service.get_loan_by_id(db, loan_id)

    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestamo no encontrado",
        )

    return loan
