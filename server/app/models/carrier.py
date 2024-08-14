# /server/app/models/carrier.py
from sqlalchemy import Column, Integer, String, Text

from .base import Base


class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    contact_info = Column(Text)
