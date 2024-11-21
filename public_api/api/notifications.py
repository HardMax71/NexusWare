# /public_api/api/notifications.py
from typing import List

from public_api.shared_schemas import Notification, NotificationCreate, NotificationUpdate
from public_api.api.client import APIClient


class NotificationsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_notifications(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        response = self.client.get("/notifications/", params={"skip": skip, "limit": limit})
        return [Notification.model_validate(item) for item in response]

    def get_unread_notifications(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        response = self.client.get("/notifications/unread", params={"skip": skip, "limit": limit})
        return [Notification.model_validate(item) for item in response]

    def create_notification(self, notification: NotificationCreate) -> Notification:
        response = self.client.post("/notifications/", json=notification.model_dump())
        return Notification.model_validate(response)

    def get_notification(self, notification_id: int) -> Notification:
        response = self.client.get(f"/notifications/{notification_id}")
        return Notification.model_validate(response)

    def update_notification(self, notification_id: int, notification_update: NotificationUpdate) -> Notification:
        response = self.client.put(f"/notifications/{notification_id}", json=notification_update.model_dump())
        return Notification.model_validate(response)

    def delete_notification(self, notification_id: int) -> None:
        self.client.delete(f"/notifications/{notification_id}")

    def mark_as_read(self, notification_id: int) -> Notification:
        response = self.client.put(f"/notifications/{notification_id}/read")
        return Notification.model_validate(response)

    def mark_all_as_read(self) -> List[Notification]:
        response = self.client.put("/notifications/read-all")
        return [Notification.model_validate(item) for item in response]
