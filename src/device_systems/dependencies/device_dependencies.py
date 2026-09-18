from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from device_systems.dependencies.database_dependency import get_db
from device_systems.models.device_model import Device
from device_systems.services import device_service


def get_device_or_404(
    device_id: int,
    db: Session = Depends(get_db),
) -> Device:
    # Reutilizar la busqueda y el error 404 en todas las rutas por ID.
    device = device_service.get_device_by_id(db, device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )

    return device
