# /server/app/models/receipt.py
import time

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    received_date = Column(Integer, default=lambda: int(time.time()))
    status = Column(String(20))

    purchase_order = relationship("PurchaseOrder")
    receipt_items = relationship("ReceiptItem", back_populates="receipt")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity_received = Column(Integer)
    location_id = Column(Integer, ForeignKey("locations.id"))

    receipt = relationship("Receipt", back_populates="receipt_items")
    product = relationship("Product")
    location = relationship("Location")
