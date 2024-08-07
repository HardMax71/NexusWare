from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    order_date = Column(DateTime, server_default=func.now())
    status = Column(String(20))
    total_amount = Column(Numeric(10, 2))

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)

    orders = relationship("Order", back_populates="customer")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    order_date = Column(DateTime, server_default=func.now())
    status = Column(String(20))
    expected_delivery_date = Column(DateTime)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    po_items = relationship("POItem", back_populates="purchase_order")


class POItem(Base):
    __tablename__ = "po_items"

    po_item_id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.po_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))

    purchase_order = relationship("PurchaseOrder", back_populates="po_items")
    product = relationship("Product")


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)

    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
