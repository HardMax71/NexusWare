from typing import List

from sqlalchemy.orm import Session

from public_api.shared_schemas import (
    NotificationCreate, NotificationUpdate
)
from server.app.models import Notification
from .base import CRUDBase


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):

    def get_user_notifications(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Notification).filter(Notification.user_id == user_id).offset(skip).limit(limit).all()

    def get_user_unread_notifications(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return (db.query(Notification).filter(Notification.user_id == user_id,
                                              Notification.is_read.isnot(True))
                .offset(skip)
                .limit(limit)
                .all())

    def mark_notification_as_read(self, db: Session, notification_id: int, user_id: int):
        notification = db.query(Notification).filter(Notification.id == notification_id,
                                                     Notification.user_id == user_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            return notification
        return None

    def mark_all_as_read(self, db: Session, user_id: int) -> List[Notification]:
        notifications = db.query(self.model).filter(self.model.user_id == user_id,
                                                    self.model.is_read.isnot(True)).all()
        for notification in notifications:
            notification.is_read = True
        db.commit()
        for notification in notifications:
            db.refresh(notification)
        return notifications


notification = CRUDNotification(Notification)
