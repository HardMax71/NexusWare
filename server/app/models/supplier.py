# /server/app/models/supplier.py
from sqlalchemy import (Column, Integer, String, Text)
from sqlalchemy.orm import relationship

from .base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)

    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
