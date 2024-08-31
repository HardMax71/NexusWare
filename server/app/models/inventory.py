# /server/app/models/inventory.py
import time

from sqlalchemy import (Column, Integer, String,
                        ForeignKey)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    expiration_date = Column(Integer, default=lambda: int(time.time()))
    quantity = Column(Integer, nullable=False)
    last_updated = Column(Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    product = relationship("Product", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")


class LocationInventory(Base):
    __tablename__ = "location_inventory"

    location_id = Column(Integer, ForeignKey("locations.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    location = relationship("Location")
    product = relationship("Product")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    movement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    from_location_id = Column(Integer, ForeignKey("locations.id"))
    to_location_id = Column(Integer, ForeignKey("locations.id"))
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255))
    timestamp = Column(Integer, default=lambda: int(time.time()))

    product = relationship("Product")
    from_location = relationship("Location", foreign_keys=[from_location_id])
    to_location = relationship("Location", foreign_keys=[to_location_id])


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    quantity_change = Column(Integer, nullable=False)
    reason = Column(String(255))
    timestamp = Column(Integer, default=lambda: int(time.time()))

    product = relationship("Product")
    location = relationship("Location")
