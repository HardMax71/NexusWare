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
    actual_arrival_time: Optional[datetime] = None
    actual_departure_time: Optional[datetime] = None


class DockAppointmentCreate(DockAppointmentBase):
    pass


class DockAppointmentUpdate(BaseModel):
    yard_location_id: Optional[int] = None
    appointment_time: Optional[datetime] = None
    carrier_id: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None
    actual_arrival_time: Optional[datetime] = None
    actual_departure_time: Optional[datetime] = None


class DockAppointment(DockAppointmentBase):
    appointment_id: int

    class Config:
        from_attributes = True


class YardLocationWithAppointments(YardLocation):
    appointments: list[DockAppointment] = []


class YardLocationFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None


class DockAppointmentFilter(BaseModel):
    yard_location_id: Optional[int] = None
    carrier_id: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class YardStats(BaseModel):
    total_locations: int
    occupied_locations: int
    total_appointments: int
    upcoming_appointments: int


class AppointmentConflict(BaseModel):
    conflicting_appointment: DockAppointment
    conflict_reason: str


class YardLocationCapacity(BaseModel):
    yard_location_id: int
    name: str
    capacity: int
    current_occupancy: int


class YardUtilizationReport(BaseModel):
    date: datetime
    total_capacity: int
    total_utilization: int
    utilization_percentage: float
    location_breakdown: list[YardLocationCapacity]


class CarrierPerformance(BaseModel):
    carrier_id: int
    carrier_name: str
    total_appointments: int
    on_time_appointments: int
    late_appointments: int
    missed_appointments: int
    average_dwell_time: float  # in minutes
