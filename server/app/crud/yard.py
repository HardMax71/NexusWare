# /server/app/crud/yard.py
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from server.app.models import YardLocation, DockAppointment, Carrier
from server.app.schemas import (
    YardLocation as YardLocationSchema,
    DockAppointment as DockAppointmentSchema,
    YardLocationCreate, YardLocationUpdate,
    DockAppointmentCreate, DockAppointmentUpdate,
    YardLocationFilter, DockAppointmentFilter,
    YardStats, AppointmentConflict, YardUtilizationReport,
    CarrierPerformance, YardLocationCapacity,
    YardLocationWithAppointments
)
from .base import CRUDBase


class CRUDYardLocation(CRUDBase[YardLocation, YardLocationCreate, YardLocationUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100,
                              filter_params: YardLocationFilter) -> List[YardLocationSchema]:
        query = db.query(self.model)
        if filter_params.name:
            query = query.filter(YardLocation.name.ilike(f"%{filter_params.name}%"))
        if filter_params.type:
            query = query.filter(YardLocation.type == filter_params.type)
        if filter_params.status:
            query = query.filter(YardLocation.status == filter_params.status)
        locations = query.offset(skip).limit(limit).all()
        return [YardLocationSchema.model_validate(location) for location in locations]

    def get_with_appointments(self, db: Session, id: int) -> Optional[YardLocationWithAppointments]:
        location = (db.query(self.model)
                    .filter(self.model.yard_location_id == id)
                    .options(selectinload(YardLocation.appointments))
                    .first())
        return YardLocationWithAppointments.model_validate(location) if location else None


class CRUDDockAppointment(CRUDBase[DockAppointment, DockAppointmentCreate, DockAppointmentUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100,
                              filter_params: DockAppointmentFilter) -> List[DockAppointmentSchema]:
        query = db.query(self.model)
        if filter_params.yard_location_id:
            query = query.filter(DockAppointment.yard_location_id == filter_params.yard_location_id)
        if filter_params.carrier_id:
            query = query.filter(DockAppointment.carrier_id == filter_params.carrier_id)
        if filter_params.type:
            query = query.filter(DockAppointment.type == filter_params.type)
        if filter_params.status:
            query = query.filter(DockAppointment.status == filter_params.status)
        if filter_params.date_from:
            query = query.filter(DockAppointment.appointment_time >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(DockAppointment.appointment_time <= filter_params.date_to)
        appointments = query.offset(skip).limit(limit).all()
        return [DockAppointmentSchema.model_validate(appointment) for appointment in appointments]

    def check_conflicts(self, db: Session,
                        appointment: DockAppointmentCreate,
                        exclude_id: Optional[int] = None) -> List[AppointmentConflict]:
        conflicts = []
        appointment_duration = timedelta(hours=1)  # Assume 1-hour appointments
        query = db.query(DockAppointment).filter(
            DockAppointment.yard_location_id == appointment.yard_location_id,
            DockAppointment.appointment_time.between(
                appointment.appointment_time - appointment_duration,
                appointment.appointment_time + appointment_duration
            )
        )
        if exclude_id:
            query = query.filter(DockAppointment.appointment_id != exclude_id)

        for existing_appointment in query.all():
            conflicts.append(AppointmentConflict(
                conflicting_appointment=DockAppointmentSchema.model_validate(existing_appointment),
                conflict_reason="Time overlap with existing appointment"
            ))
        return conflicts


class CRUDYard:
    def get_stats(self, db: Session) -> YardStats:
        total_locations = db.query(func.count(YardLocation.yard_location_id)).scalar()
        occupied_locations = db.query(func.count(YardLocation.yard_location_id)).filter(
            YardLocation.status == "occupied").scalar()
        total_appointments = db.query(func.count(DockAppointment.appointment_id)).scalar()
        upcoming_appointments = db.query(func.count(DockAppointment.appointment_id)).filter(
            DockAppointment.appointment_time > datetime.now(),
            DockAppointment.status == "scheduled"
        ).scalar()

        return YardStats(
            total_locations=total_locations,
            occupied_locations=occupied_locations,
            total_appointments=total_appointments,
            upcoming_appointments=upcoming_appointments
        )

    def get_utilization_report(self, db: Session, date: datetime) -> YardUtilizationReport:
        locations = db.query(YardLocation).all()
        total_capacity = sum(location.capacity for location in locations)
        total_utilization = db.query(func.count(DockAppointment.appointment_id)).filter(
            func.date(DockAppointment.appointment_time) == date.date()
        ).scalar()

        location_breakdown = []
        for location in locations:
            occupancy = db.query(func.count(DockAppointment.appointment_id)).filter(
                DockAppointment.yard_location_id == location.yard_location_id,
                func.date(DockAppointment.appointment_time) == date.date()
            ).scalar()
            location_breakdown.append(YardLocationCapacity(
                yard_location_id=location.yard_location_id,
                name=location.name,
                capacity=location.capacity,
                current_occupancy=occupancy
            ))

        return YardUtilizationReport(
            date=date,
            total_capacity=total_capacity,
            total_utilization=total_utilization,
            utilization_percentage=(total_utilization / total_capacity) * 100 if total_capacity > 0 else 0,
            location_breakdown=location_breakdown
        )

    def get_carrier_performance(self, db: Session,
                                start_date: datetime, end_date: datetime) -> List[CarrierPerformance]:
        carriers = db.query(Carrier).all()
        performance_data = []

        for carrier in carriers:
            appointments = db.query(DockAppointment).filter(
                DockAppointment.carrier_id == carrier.carrier_id,
                DockAppointment.appointment_time.between(start_date, end_date)
            ).all()

            total_appointments = len(appointments)
            on_time_appointments = sum(
                1 for a in appointments if a.status == "completed" and a.actual_arrival_time <= a.appointment_time)
            late_appointments = sum(
                1 for a in appointments if a.status == "completed" and a.actual_arrival_time > a.appointment_time)
            missed_appointments = sum(1 for a in appointments if a.status == "missed")

            dwell_times = [
                (a.actual_departure_time - a.actual_arrival_time).total_seconds() / 60
                for a in appointments
                if a.status == "completed" and a.actual_arrival_time and a.actual_departure_time
            ]
            average_dwell_time = sum(dwell_times) / len(dwell_times) if dwell_times else 0

            performance_data.append(CarrierPerformance(
                carrier_id=carrier.carrier_id,
                carrier_name=carrier.name,
                total_appointments=total_appointments,
                on_time_appointments=on_time_appointments,
                late_appointments=late_appointments,
                missed_appointments=missed_appointments,
                average_dwell_time=average_dwell_time
            ))

        return performance_data


yard_location = CRUDYardLocation(YardLocation)
dock_appointment = CRUDDockAppointment(DockAppointment)
yard = CRUDYard()
