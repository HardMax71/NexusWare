from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(50))
    asset_name = Column(String(100))
    serial_number = Column(String(50))
    purchase_date = Column(Date)
    status = Column(String(20))

    maintenance_records = relationship("AssetMaintenance", back_populates="asset")


class AssetMaintenance(Base):
    __tablename__ = "asset_maintenance"

    maintenance_id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"))
    maintenance_type = Column(String(50))
    scheduled_date = Column(Date)
    completed_date = Column(Date)
    performed_by = Column(Integer, ForeignKey("users.user_id"))
    notes = Column(Text)

    asset = relationship("Asset", back_populates="maintenance_records")
    user = relationship("User")
