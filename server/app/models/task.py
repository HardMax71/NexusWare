# /server/app/models/task.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50))
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.user_id"))
    due_date = Column(DateTime)
    priority = Column(String(20))
    status = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    assigned_user = relationship("User")
