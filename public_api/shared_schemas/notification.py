# /public_api/shared_schemas/notification.py
from typing import Optional

from pydantic import BaseModel


class NotificationBase(BaseModel):
    message: str
    timestamp: int


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool

    class Config:
        from_attributes = True
