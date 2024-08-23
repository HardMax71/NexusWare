from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                               QPushButton, QHeaderView, QAbstractItemView)

from public_api.api import APIClient, NotificationsAPI


class NotificationCenter(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.notifications_api = NotificationsAPI(api_client)
        self.init_ui()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.fetch_notifications)
        self.update_timer.start(60000)  # Fetch notifications every minute
        self.setMinimumSize(600, 400)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.notification_table = QTableWidget(0, 3)
        self.notification_table.setHorizontalHeaderLabels(["Date", "Description", "Action"])
        self.notification_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.notification_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.notification_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.notification_table.verticalHeader().setVisible(False)
        self.notification_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.notification_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.notification_table.setColumnWidth(0, 100)  # Fixed width for date column
        self.notification_table.setColumnWidth(2, 150)  # Fixed width for action column
        self.notification_table.setShowGrid(False)
        self.notification_table.setStyleSheet("""
            QTableWidget::item { border-bottom: 1px solid #d0d0d0; }
            QTableWidget::item:selected { background-color: #e6f3ff; color: black; }
        """)
        layout.addWidget(self.notification_table)

        mark_all_read_button = QPushButton("Mark All as Read")
        mark_all_read_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px;")
        mark_all_read_button.clicked.connect(self.mark_all_as_read)
        layout.addWidget(mark_all_read_button)

        self.fetch_notifications()

    def fetch_notifications(self):
        notifications = self.notifications_api.get_notifications()
        self.notification_table.setRowCount(0)

        for notification in notifications:
            row_position = self.notification_table.rowCount()
            self.notification_table.insertRow(row_position)

            timestamp = QDateTime.fromSecsSinceEpoch(notification.timestamp).toString("yyyy-MM-dd")
            date_item = QTableWidgetItem(timestamp)
            date_item.setTextAlignment(Qt.AlignCenter)

            description_item = QTableWidgetItem(notification.message)
            description_item.setToolTip(notification.message)  # Show full message on hover

            if notification.is_read:
                color = QColor(180, 180, 180)  # Lighter grey for read notifications
            else:
                color = QColor(0, 0, 0)  # Black for unread notifications

            date_item.setForeground(QBrush(color))
            description_item.setForeground(QBrush(color))

            self.notification_table.setItem(row_position, 0, date_item)
            self.notification_table.setItem(row_position, 1, description_item)

            mark_as_read_button = QPushButton("Mark as Read")
            mark_as_read_button.setStyleSheet("background-color: #28a745; color: white; padding: 5px;")
            mark_as_read_button.clicked.connect(lambda _, nid=notification.id: self.mark_as_read(nid))
            if notification.is_read:
                mark_as_read_button.setEnabled(False)
                mark_as_read_button.setStyleSheet("background-color: #a0a0a0; color: white; padding: 5px;")

            self.notification_table.setCellWidget(row_position, 2, mark_as_read_button)

        self.notification_table.resizeRowsToContents()

    def mark_as_read(self, notification_id):
        self.notifications_api.mark_as_read(notification_id)
        self.fetch_notifications()

    def mark_all_as_read(self):
        self.notifications_api.mark_all_as_read()
        self.fetch_notifications()
