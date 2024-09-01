# /server/app/models/pick_list.py
import time

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class PickList(Base):
    __tablename__ = "pick_lists"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    status = Column(String(20))
    created_at = Column(Integer, default=lambda: int(time.time()))
    completed_at = Column(Integer)

    order = relationship("Order")
    pick_list_items = relationship("PickListItem", back_populates="pick_list")


class PickListItem(Base):
    __tablename__ = "pick_list_items"

    pick_list_item_id = Column(Integer, primary_key=True, index=True)
    pick_list_id = Column(Integer, ForeignKey("pick_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    quantity = Column(Integer)
    picked_quantity = Column(Integer, default=0)

    pick_list = relationship("PickList", back_populates="pick_list_items")
    product = relationship("Product")
    location = relationship("Location")
