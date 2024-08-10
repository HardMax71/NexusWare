# /server/app/models/yard_location.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class YardLocation(Base):
    __tablename__ = "yard_locations"

    yard_location_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20))
    status = Column(String(20))
    capacity = Column(Integer, default=1)

    appointments = relationship("DockAppointment", back_populates="yard_location")
