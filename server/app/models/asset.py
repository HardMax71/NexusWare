# /server/app/models/asset.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(50))
    asset_name = Column(String(100))
    serial_number = Column(String(50))
    purchase_date = Column(Integer)
    status = Column(String(20))
    location_id = Column(Integer, ForeignKey("locations.id"))

    maintenance_records = relationship("AssetMaintenance", back_populates="asset")
    location = relationship("Location", back_populates="assets")


class AssetMaintenance(Base):
    __tablename__ = "asset_maintenance"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    maintenance_type = Column(String(50))
    scheduled_date = Column(Integer)
    completed_date = Column(Integer)
    performed_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)

    asset = relationship("Asset", back_populates="maintenance_records")
    user = relationship("User")
