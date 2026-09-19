from sqlalchemy import func
from sqlalchemy.orm import Session

from device_systems.models.user_model import User
from device_systems.auth.security import get_password_hash


def create_user(db: Session, user_data):
    # Convertir el schema Pydantic en un registro SQLAlchemy.
    user_fields = user_data.model_dump(exclude={"password"})
    user = User(
        **user_fields,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(
    db: Session,
    role: str = None,
    is_active: bool = None,
    order_by: str = "name",
):
    # Construir la consulta antes de aplicar filtros y ordenamiento.
    query = db.query(User)

    # Aplicar únicamente los filtros enviados por el cliente.
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if order_by == "created_at":
        query = query.order_by(User.created_at)
    else:
        query = query.order_by(User.name)

    return query.all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    # Comparar sin distinguir mayúsculas para evitar correos duplicados.
    return db.query(User).filter(func.lower(User.email) == email.lower()).first()


def update_user(db: Session, user: User, user_data):
    # PUT reemplaza todos los campos editables del usuario.
    for field, value in user_data.model_dump().items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def patch_user(db: Session, user: User, fields_to_update: dict):
    # PATCH modifica únicamente los campos enviados por el cliente.
    for field, value in fields_to_update.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User):
    # Confirmar la transacción para eliminar el registro definitivamente.
    db.delete(user)
    db.commit()


