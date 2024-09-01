from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Notification
from public_api.shared_schemas import (
    NotificationCreate, NotificationUpdate, Notification as NotificationSchema
)


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):

    def get_user_notifications(self, db: Session,
                               user_id: int, skip: int = 0, limit: int = 100) -> list[NotificationSchema]:
        notifications = db.query(Notification).filter(Notification.user_id == user_id).offset(skip).limit(limit).all()
        return [NotificationSchema.model_validate(notification) for notification in notifications]

    def get_user_unread_notifications(self, db: Session,
                                      user_id: int, skip: int = 0, limit: int = 100) -> list[NotificationSchema]:
        notifications = (db.query(Notification).filter(Notification.user_id == user_id,
                                                       Notification.is_read.isnot(True))
                         .offset(skip)
                         .limit(limit)
                         .all())
        return [NotificationSchema.model_validate(notification) for notification in notifications]

    def mark_notification_as_read(self, db: Session, notification_id: int, user_id: int) -> NotificationSchema | None:
        notification = db.query(Notification).filter(Notification.id == notification_id,
                                                     Notification.user_id == user_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            return NotificationSchema.model_validate(notification)
        return None

    def mark_all_as_read(self, db: Session, user_id: int) -> list[NotificationSchema]:
        notifications = db.query(self.model).filter(self.model.user_id == user_id,
                                                    self.model.is_read.isnot(True)).all()
        for notification in notifications:
            notification.is_read = True
        db.commit()
        for notification in notifications:
            db.refresh(notification)
        return [NotificationSchema.model_validate(notification) for notification in notifications]


notification = CRUDNotification(Notification)
