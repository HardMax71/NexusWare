# /server/app/models/location.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="")
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    aisle = Column(String(50), nullable=True)
    rack = Column(String(50), nullable=True)
    shelf = Column(String(50), nullable=True)
    bin = Column(String(50), nullable=True)
    capacity = Column(Integer, nullable=False, default=0)

    assets = relationship("Asset", back_populates="location")
    inventory_items = relationship("Inventory", back_populates="location")
    location_inventory = relationship("LocationInventory", back_populates="location")
    pick_list_items = relationship("PickListItem", back_populates="location")
    receipt_items = relationship("ReceiptItem", back_populates="location")
    inventory_movements_from = relationship("InventoryMovement",
                                            foreign_keys="[InventoryMovement.from_location_id]",
                                            back_populates="from_location")
    inventory_movements_to = relationship("InventoryMovement",
                                          foreign_keys="[InventoryMovement.to_location_id]",
                                          back_populates="to_location")
    inventory_adjustments = relationship("InventoryAdjustment", back_populates="location")
    zone = relationship("Zone", back_populates="locations")
