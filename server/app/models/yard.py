# /server/app/models/yard.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class YardLocation(Base):
    __tablename__ = "yard_locations"

    yard_location_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20))
    status = Column(String(20))

    appointments = relationship("DockAppointment", back_populates="yard_location")


class DockAppointment(Base):
    __tablename__ = "dock_appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    yard_location_id = Column(Integer, ForeignKey("yard_locations.yard_location_id"))
    appointment_time = Column(DateTime)
    carrier_id = Column(Integer, ForeignKey("carriers.carrier_id"))
    type = Column(String(20))
    status = Column(String(20))

    yard_location = relationship("YardLocation", back_populates="appointments")
    carrier = relationship("Carrier")
