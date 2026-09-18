from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from device_systems.models.device_model import Device


def create_device(db: Session, device_data):
    device = Device(**device_data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_devices(
    db: Session,
    device_type: str = None,
    is_available: bool = None,
    brand: str = None,
    search: str = None,
):
    query = db.query(Device)
    filters = []

    # Cada filtro es opcional y se combina con los demas mediante and_.
    if device_type is not None:
        filters.append(Device.device_type == device_type)
    if is_available is not None:
        filters.append(Device.is_available == is_available)
    if brand is not None:
        filters.append(Device.brand.ilike(f"%{brand}%"))
    if search is not None:
        filters.append(
            or_(
                Device.name.ilike(f"%{search}%"),
                Device.serial_number.ilike(f"%{search}%"),
            )
        )

    if filters:
        query = query.where(and_(*filters))

    return query.order_by(Device.name).all()


def get_device_by_id(db: Session, device_id: int):
    return db.query(Device).filter(Device.id == device_id).first()


def get_device_by_serial(db: Session, serial_number: str):
    return (
        db.query(Device)
        .filter(Device.serial_number.ilike(serial_number))
        .first()
    )


def update_device(db: Session, device: Device, device_data):
    for field, value in device_data.model_dump().items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


def patch_device(db: Session, device: Device, fields_to_update: dict):
    for field, value in fields_to_update.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device):
    db.delete(device)
    db.commit()
