# /server/app/crud/dock_appointment.py
from datetime import timedelta
from typing import Optional, List

from sqlalchemy.orm import Session

from server.app.models import DockAppointment
from public_api.shared_schemas import (
    DockAppointment as DockAppointmentSchema,
    DockAppointmentCreate, DockAppointmentUpdate,
    DockAppointmentFilter,
    AppointmentConflict
)
from .base import CRUDBase


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


dock_appointment = CRUDDockAppointment(DockAppointment)
