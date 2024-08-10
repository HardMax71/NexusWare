# /server/app/models/audit_log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action_type = Column(String(50))
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_value = Column(Text)
    new_value = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
