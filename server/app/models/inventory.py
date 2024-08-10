# /server/app/models/inventory.py
from sqlalchemy import (Column, Integer, String,
                        ForeignKey, DateTime, func)
from sqlalchemy.orm import relationship

from .base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    expiration_date = Column(DateTime, server_default=func.now())
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")


class LocationInventory(Base):
    __tablename__ = "location_inventory"

    location_id = Column(Integer, ForeignKey("locations.location_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    location = relationship("Location")
    product = relationship("Product")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    movement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    from_location_id = Column(Integer, ForeignKey("locations.location_id"))
    to_location_id = Column(Integer, ForeignKey("locations.location_id"))
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255))
    timestamp = Column(DateTime, server_default=func.now())

    product = relationship("Product")
    from_location = relationship("Location", foreign_keys=[from_location_id])
    to_location = relationship("Location", foreign_keys=[to_location_id])


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    adjustment_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    quantity_change = Column(Integer, nullable=False)
    reason = Column(String(255))
    timestamp = Column(DateTime, server_default=func.now())

    product = relationship("Product")
    location = relationship("Location")
