from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LoanStatus = Literal["active", "returned", "overdue"]


class LoanCreate(BaseModel):
    user_id: int = Field(gt=0, examples=[1])
    device_id: int = Field(gt=0, examples=[1])


class LoanUpdate(BaseModel):
    status: LoanStatus
    return_date: datetime | None = None


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: datetime | None
    status: str


class LoanUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class LoanDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: str


class LoanDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # El modelo SQLAlchemy usa id, pero la guia solicita loan_id en la respuesta.
    loan_id: int = Field(validation_alias="id")
    status: str
    user: LoanUserResponse
    device: LoanDeviceResponse
