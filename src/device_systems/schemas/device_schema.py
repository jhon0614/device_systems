from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    name: str = Field(min_length=3, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(min_length=3, examples=["LEN-2026-001"])
    device_type: str = Field(min_length=3)
    brand: str | None = None
    is_available: bool = True


class DeviceUpdate(BaseModel):
    name: str = Field(min_length=3)
    serial_number: str = Field(min_length=3)
    device_type: str = Field(min_length=3)
    brand: str | None = None
    is_available: bool


class DevicePatch(BaseModel):
    name: str | None = Field(default=None, min_length=3)
    serial_number: str | None = Field(default=None, min_length=3)
    device_type: str | None = Field(default=None, min_length=3)
    brand: str | None = None
    is_available: bool | None = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: str
    brand: str | None
    is_available: bool
    created_at: datetime
