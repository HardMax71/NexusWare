# /server/app/models/shipment.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    tracking_number = Column(String(50))
    ship_date = Column(Integer)
    status = Column(String(20))
    label_id = Column(String(100))
    label_download_url = Column(String(255))

    order = relationship("Order")
    carrier = relationship("Carrier")
