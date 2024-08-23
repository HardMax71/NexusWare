from enum import Enum

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
    name: str | None = None
    type: YardLocationType | None = None
    status: YardLocationStatus | None = None
    capacity: int | None = None


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
    actual_arrival_time: int | None = None
    actual_departure_time: int | None = None


class DockAppointmentCreate(DockAppointmentBase):
    pass


class DockAppointmentUpdate(BaseModel):
    yard_location_id: int | None = None
    appointment_time: int | None = None
    carrier_id: int | None = None
    type: YardLocationType | None = None
    status: YardLocationStatus | None = None
    actual_arrival_time: int | None = None
    actual_departure_time: int | None = None


class DockAppointment(DockAppointmentBase):
    appointment_id: int

    class Config:
        from_attributes = True


class YardLocationWithAppointments(YardLocation):
    appointments: list[DockAppointment] = []


class YardLocationFilter(BaseModel):
    name: str | None = None
    type: YardLocationType | None = None
    status: YardLocationStatus | None = None


class DockAppointmentFilter(BaseModel):
    yard_location_id: int | None = None
    carrier_id: int | None = None
    type: YardLocationType | None = None
    status: YardLocationStatus | None = None
    date_from: int | None = None
    date_to: int | None = None


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
    location_breakdown: list[YardLocationCapacity]


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
    current_appointment: DockAppointment | None = None


class YardOverview(BaseModel):
    total_locations: int
    occupied_locations: int
    available_locations: int
    utilization_percentage: float
    locations: list[YardLocationOccupancy]


class AppointmentScheduleConflict(BaseModel):
    conflicting_appointments: list[DockAppointment]
    suggested_time_slots: list[int]


class CarrierSchedule(BaseModel):
    carrier_id: int
    carrier_name: str
    appointments: list[DockAppointment]


class YardLocationTypeDistribution(BaseModel):
    type: YardLocationType
    count: int
    percentage: float


class YardAnalytics(BaseModel):
    total_locations: int
    average_utilization: float
    peak_hours: list[int]
    type_distribution: list[YardLocationTypeDistribution]
    carrier_performance: list[CarrierPerformance]


class BulkAppointmentCreate(BaseModel):
    appointments: list[DockAppointmentCreate]


class BulkAppointmentCreateResult(BaseModel):
    success_count: int
    failure_count: int
    errors: list[str]
