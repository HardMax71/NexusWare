from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class YardLocationStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


class YardLocationType(str, Enum):
    LOADING = "loading"
    UNLOADING = "unloading"
    PARKING = "parking"


class YardLocationBase(BaseModel):
    name: str
    type: YardLocationType
    status: YardLocationStatus
    capacity: int = 1


class YardLocationCreate(YardLocationBase):
    pass


class YardLocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[YardLocationType] = None
    status: Optional[YardLocationStatus] = None
    capacity: Optional[int] = None


class YardLocation(YardLocationBase):
    yard_location_id: int

    class Config:
        from_attributes = True


class DockAppointmentBase(BaseModel):
    yard_location_id: int
    appointment_time: int
    carrier_id: int
    type: YardLocationType
    status: YardLocationStatus
    actual_arrival_time: Optional[int] = None
    actual_departure_time: Optional[int] = None


class DockAppointmentCreate(DockAppointmentBase):
    pass


class DockAppointmentUpdate(BaseModel):
    yard_location_id: Optional[int] = None
    appointment_time: Optional[int] = None
    carrier_id: Optional[int] = None
    type: Optional[YardLocationType] = None
    status: Optional[YardLocationStatus] = None
    actual_arrival_time: Optional[int] = None
    actual_departure_time: Optional[int] = None


class DockAppointment(DockAppointmentBase):
    appointment_id: int

    class Config:
        from_attributes = True


class YardLocationWithAppointments(YardLocation):
    appointments: List[DockAppointment] = []


class YardLocationFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[YardLocationType] = None
    status: Optional[YardLocationStatus] = None


class DockAppointmentFilter(BaseModel):
    yard_location_id: Optional[int] = None
    carrier_id: Optional[int] = None
    type: Optional[YardLocationType] = None
    status: Optional[YardLocationStatus] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None


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
    date: int
    total_capacity: int
    total_utilization: int
    utilization_percentage: float
    location_breakdown: List[YardLocationCapacity]


class CarrierPerformance(BaseModel):
    carrier_id: int
    carrier_name: str
    total_appointments: int
    on_time_appointments: int
    late_appointments: int
    missed_appointments: int
    average_dwell_time: float  # in minutes


class YardLocationOccupancy(BaseModel):
    yard_location_id: int
    name: str
    occupied: bool
    current_appointment: Optional[DockAppointment] = None


class YardOverview(BaseModel):
    total_locations: int
    occupied_locations: int
    available_locations: int
    utilization_percentage: float
    locations: List[YardLocationOccupancy]


class AppointmentScheduleConflict(BaseModel):
    conflicting_appointments: List[DockAppointment]
    suggested_time_slots: List[int]


class CarrierSchedule(BaseModel):
    carrier_id: int
    carrier_name: str
    appointments: List[DockAppointment]


class YardLocationTypeDistribution(BaseModel):
    type: YardLocationType
    count: int
    percentage: float


class YardAnalytics(BaseModel):
    total_locations: int
    average_utilization: float
    peak_hours: List[int]
    type_distribution: List[YardLocationTypeDistribution]
    carrier_performance: List[CarrierPerformance]


class BulkAppointmentCreate(BaseModel):
    appointments: List[DockAppointmentCreate]


class BulkAppointmentCreateResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[str]
