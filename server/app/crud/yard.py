# /server/app/crud/yard.py
from server.app.models import YardLocation, DockAppointment
from server.app.schemas import (YardLocationCreate, YardLocationUpdate,
                                DockAppointmentCreate, DockAppointmentUpdate)

from .base import CRUDBase


class CRUDYardLocation(CRUDBase[YardLocation, YardLocationCreate, YardLocationUpdate]):
    pass


class CRUDDockAppointment(CRUDBase[DockAppointment, DockAppointmentCreate, DockAppointmentUpdate]):
    pass


yard_location = CRUDYardLocation(YardLocation)
dock_appointment = CRUDDockAppointment(DockAppointment)
