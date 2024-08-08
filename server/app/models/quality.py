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
