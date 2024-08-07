from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship

from .base import Base


class PickList(Base):
    __tablename__ = "pick_lists"

    pick_list_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    status = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

    order = relationship("Order")
    pick_list_items = relationship("PickListItem", back_populates="pick_list")


class PickListItem(Base):
    __tablename__ = "pick_list_items"

    pick_list_item_id = Column(Integer, primary_key=True, index=True)
    pick_list_id = Column(Integer, ForeignKey("pick_lists.pick_list_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    quantity = Column(Integer)
    picked_quantity = Column(Integer, default=0)

    pick_list = relationship("PickList", back_populates="pick_list_items")
    product = relationship("Product")
    location = relationship("Location")


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


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    carrier_id = Column(Integer, ForeignKey("carriers.carrier_id"))
    tracking_number = Column(String(50))
    ship_date = Column(DateTime)
    status = Column(String(20))

    order = relationship("Order")
    carrier = relationship("Carrier")


class Carrier(Base):
    __tablename__ = "carriers"

    carrier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    contact_info = Column(Text)
