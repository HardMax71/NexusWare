# /server/app/models/receipt.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base


class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.po_id"))
    received_date = Column(DateTime, server_default=func.now())
    status = Column(String(20))

    purchase_order = relationship("PurchaseOrder")
    receipt_items = relationship("ReceiptItem", back_populates="receipt")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    receipt_item_id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.receipt_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity_received = Column(Integer)
    location_id = Column(Integer, ForeignKey("locations.location_id"))

    receipt = relationship("Receipt", back_populates="receipt_items")
    product = relationship("Product")
    location = relationship("Location")
