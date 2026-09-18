from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from device_systems.models.device_model import Device
from device_systems.models.loan_model import Loan
from device_systems.models.user_model import User


def create_loan(db: Session, user: User, device: Device):
    loan = Loan(user_id=user.id, device_id=device.id, status="active")
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def get_loans(
    db: Session,
    status_filter: str = None,
    user_email: str = None,
    device_type: str = None,
    loan_date_from: datetime = None,
    loan_date_to: datetime = None,
):
    # Los joins permiten filtrar usando datos de usuarios y dispositivos.
    query = db.query(Loan).join(User).join(Device)
    filters = []

    if status_filter is not None:
        filters.append(Loan.status == status_filter)
    if user_email is not None:
        filters.append(User.email.ilike(f"%{user_email}%"))
    if device_type is not None:
        filters.append(Device.device_type == device_type)
    if loan_date_from is not None:
        filters.append(Loan.loan_date >= loan_date_from)
    if loan_date_to is not None:
        filters.append(Loan.loan_date <= loan_date_to)

    if filters:
        query = query.where(and_(*filters))

    return query.order_by(Loan.loan_date.desc()).all()


def get_loan_by_id(db: Session, loan_id: int):
    return db.query(Loan).filter(Loan.id == loan_id).first()


def get_user_loans(db: Session, user_id: int):
    return (
        db.query(Loan)
        .join(User)
        .join(Device)
        .where(User.id == user_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )


def get_device_loans(db: Session, device_id: int):
    return (
        db.query(Loan)
        .join(User)
        .join(Device)
        .where(Device.id == device_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )


def return_loan(db: Session, loan: Loan):
    loan.status = "returned"
    loan.return_date = datetime.utcnow()
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan
