# /server/app/models/order.py
from sqlalchemy import (Column, Integer, String, ForeignKey,
                        Numeric)
from sqlalchemy.orm import relationship
import time

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(Integer, default=lambda: int(time.time()))
    ship_date = Column(Integer)
    status = Column(String(20))
    total_amount = Column(Numeric(10, 2))
    shipping_name = Column(String(100))
    shipping_address_line1 = Column(String(255))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_postal_code = Column(String(20))
    shipping_country = Column(String(100))
    shipping_phone = Column(String(20))

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    order_date = Column(Integer, default=lambda: int(time.time()))
    status = Column(String(20))
    expected_delivery_date = Column(Integer)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    po_items = relationship("POItem", back_populates="purchase_order")


class POItem(Base):
    __tablename__ = "po_items"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))

    purchase_order = relationship("PurchaseOrder", back_populates="po_items")
    product = relationship("Product")
