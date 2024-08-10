# /server/app/models/pick_list.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
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
