# /server/app/models/dock_appointment.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class DockAppointment(Base):
    __tablename__ = "dock_appointments"

    id = Column(Integer, primary_key=True, index=True)
    yard_location_id = Column(Integer, ForeignKey("yard_locations.id"))
    appointment_time = Column(Integer)
    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    type = Column(String(20))
    status = Column(String(20))
    actual_arrival_time = Column(Integer)
    actual_departure_time = Column(Integer)

    yard_location = relationship("YardLocation", back_populates="appointments")
    carrier = relationship("Carrier")
