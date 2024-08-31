# /server/app/models/quality.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
import time

from app.models.base import Base


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    check_date = Column(Integer, default=lambda: int(time.time()))
    performed_by = Column(Integer, ForeignKey("users.id"))
    result = Column(String(20))
    notes = Column(Text)

    product = relationship("Product")
    user = relationship("User")


class QualityStandard(Base):
    __tablename__ = "quality_standards"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    criteria = Column(String(100), nullable=False)
    acceptable_range = Column(String(100), nullable=False)

    product = relationship("Product")


class QualityAlert(Base):
    __tablename__ = "quality_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    alert_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(Integer, default=lambda: int(time.time()))
    resolved_at = Column(Integer, nullable=True)

    product = relationship("Product")
