# /server/app/models/notification.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String(255), nullable=False)
    timestamp = Column(Integer, nullable=False)
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")
