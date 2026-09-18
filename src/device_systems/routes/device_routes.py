from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from device_systems.dependencies.database_dependency import get_db
from device_systems.dependencies.device_dependencies import get_device_or_404
from device_systems.models.device_model import Device
from device_systems.schemas.device_schema import (
    DeviceCreate,
    DevicePatch,
    DeviceResponse,
    DeviceUpdate,
)
from device_systems.services import device_service

router = APIRouter(prefix="/devices", tags=["Devices"])


def validate_serial(db: Session, serial_number: str, current_device_id: int = None):
    device = device_service.get_device_by_serial(db, serial_number)
    if device and device.id != current_device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El numero de serie ya esta registrado",
        )


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description="Lista dispositivos y aplica filtros opcionales.",
    response_description="Lista de dispositivos",
)
def list_devices(
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return device_service.get_devices(db, device_type, is_available, brand, search)


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar dispositivo",
    description="Busca un dispositivo por su ID.",
    response_description="Dispositivo encontrado",
)
def get_device(device: Device = Depends(get_device_or_404)):
    return device


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dispositivo",
    description="Registra un dispositivo con numero de serie unico.",
    response_description="Dispositivo creado",
)
def create_device(device_data: DeviceCreate, db: Session = Depends(get_db)):
    validate_serial(db, device_data.serial_number)
    return device_service.create_device(db, device_data)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo",
    description="Reemplaza todos los datos de un dispositivo.",
    response_description="Dispositivo actualizado",
)
def update_device(
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
    device: Device = Depends(get_device_or_404),
):
    validate_serial(db, device_data.serial_number, device.id)
    return device_service.update_device(db, device, device_data)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcialmente",
    description="Modifica solamente los campos enviados.",
    response_description="Dispositivo actualizado",
)
def patch_device(
    device_data: DevicePatch,
    db: Session = Depends(get_db),
    device: Device = Depends(get_device_or_404),
):
    fields_to_update = device_data.model_dump(exclude_unset=True)

    if not fields_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo",
        )
    if any(
        value is None and field != "brand"
        for field, value in fields_to_update.items()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Los campos obligatorios no pueden ser nulos",
        )
    if "serial_number" in fields_to_update:
        validate_serial(db, fields_to_update["serial_number"], device.id)

    return device_service.patch_device(db, device, fields_to_update)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dispositivo",
    description="Elimina un dispositivo sin historial de prestamos.",
)
def delete_device(
    response: Response,
    db: Session = Depends(get_db),
    device: Device = Depends(get_device_or_404),
):
    if device.loans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un dispositivo con prestamos registrados",
        )

    device_service.delete_device(db, device)
