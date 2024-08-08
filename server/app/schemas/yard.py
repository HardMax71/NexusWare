# /server/app/schemas/yard.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class YardLocationBase(BaseModel):
    name: str
    type: str
    status: str


class YardLocationCreate(YardLocationBase):
    pass


class YardLocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None


class YardLocation(YardLocationBase):
    yard_location_id: int

    class Config:
        from_attributes = True


class DockAppointmentBase(BaseModel):
    yard_location_id: int
    appointment_time: datetime
    carrier_id: int
    type: str
    status: str


class DockAppointmentCreate(DockAppointmentBase):
    pass


class DockAppointmentUpdate(BaseModel):
    yard_location_id: Optional[int] = None
    appointment_time: Optional[datetime] = None
    carrier_id: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None


class DockAppointment(DockAppointmentBase):
    appointment_id: int

    class Config:
        from_attributes = True
