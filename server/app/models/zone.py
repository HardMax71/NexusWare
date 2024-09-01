# /server/app/models/zone.py
from sqlalchemy import (Column, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)

    locations = relationship("Location", back_populates="zone")
