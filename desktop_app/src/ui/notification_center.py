from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel


class NotificationCenter(QDockWidget):
    def __init__(self, api_client):
        super().__init__("Notifications")
        self.api_client = api_client
        self.init_ui()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.fetch_notifications)
        self.update_timer.start(60000)  # Fetch notifications every minute

    def init_ui(self):
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        self.setMinimumWidth(250)

        content = QWidget()
        layout = QVBoxLayout(content)

        title_label = QLabel("Notifications")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.notification_list = QListWidget()
        layout.addWidget(self.notification_list)

        self.setWidget(content)

        self.fetch_notifications()


    # TODO: notifications api doesnt exist yet, so this is just a placeholder
    def fetch_notifications(self):
        self.notification_list.clear()
        for i in range(5):
            notification = {
                "timestamp": "2021-08-01 12:00:00",
                "message": f"<not implemented> Notification {i}"
            }
            item = QListWidgetItem(f"{notification['timestamp']} - {notification['message']}")
            self.notification_list.addItem(item)

        # notifications = self.api_client.notifications.get_notifications()
        # self.notification_list.clear()
        # for notification in notifications:
        #     item = QListWidgetItem(f"{notification['timestamp']} - {notification['message']}")
        #     item.setData(Qt.UserRole, notification['id'])
        #     self.notification_list.addItem(item)

    def mark_as_read(self, notification_id):
        pass
        # self.api_client.notifications.mark_as_read(notification_id)
        # self.fetch_notifications()
