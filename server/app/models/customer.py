# /server/app/models/customer.py
from sqlalchemy import (Column, Integer, String, Text)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)

    orders = relationship("Order", back_populates="customer")
