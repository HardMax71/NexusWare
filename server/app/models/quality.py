# /server/app/models/quality.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    check_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    check_date = Column(DateTime, server_default=func.now())
    performed_by = Column(Integer, ForeignKey("users.user_id"))
    result = Column(String(20))
    notes = Column(Text)

    product = relationship("Product")
    user = relationship("User")


class QualityStandard(Base):
    __tablename__ = "quality_standards"

    standard_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    criteria = Column(String(100), nullable=False)
    acceptable_range = Column(String(100), nullable=False)

    product = relationship("Product")


class QualityAlert(Base):
    __tablename__ = "quality_alerts"

    alert_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    alert_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    product = relationship("Product")
