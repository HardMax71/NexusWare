# /server/app/models/audit_log.py
import time

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(50))
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_value = Column(Text)
    new_value = Column(Text)
    timestamp = Column(Integer, default=lambda: int(time.time()))

    user = relationship("User", back_populates="audit_logs")
