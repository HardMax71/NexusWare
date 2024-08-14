# /server/app/models/task.py
import time

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50))
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    due_date = Column(Integer)
    priority = Column(String(20))
    status = Column(String(20))
    created_at = Column(Integer, default=lambda: int(time.time()))

    assigned_user = relationship("User")
    comments = relationship("TaskComment", back_populates="task")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment = Column(Text)
    created_at = Column(Integer, default=lambda: int(time.time()))

    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")
