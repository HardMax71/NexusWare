# /server/app/models/shipment.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    carrier_id = Column(Integer, ForeignKey("carriers.carrier_id"))
    tracking_number = Column(String(50))
    ship_date = Column(DateTime)
    status = Column(String(20))
    label_id = Column(String(100))
    label_download_url = Column(String(255))

    order = relationship("Order")
    carrier = relationship("Carrier")