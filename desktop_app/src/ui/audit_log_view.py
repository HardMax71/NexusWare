from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QDateEdit, QLabel

from desktop_app.src.api import APIClient, AuditAPI
from desktop_app.src.ui.components import StyledButton


class AuditLogView(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.audit_log_api = AuditAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.start_date = QDateEdit(QDate.currentDate().addDays(-7))
        self.end_date = QDateEdit(QDate.currentDate())
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_logs)
        controls_layout.addWidget(QLabel("Start Date:"))
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(QLabel("End Date:"))
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(self.refresh_button)
        layout.addLayout(controls_layout)

        # Audit log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "User", "Action", "Table", "Record ID", "Details"])
        layout.addWidget(self.log_table)

        self.refresh_logs()

    def refresh_logs(self):
        start_date = self.start_date.date().toString(Qt.ISODate)
        end_date = self.end_date.date().toString(Qt.ISODate)
        logs = self.audit_log_api.get_audit_summary(start_date, end_date)

        self.log_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.log_table.setItem(row, 0, QTableWidgetItem(log['timestamp']))
            self.log_table.setItem(row, 1, QTableWidgetItem(log['username']))
            self.log_table.setItem(row, 2, QTableWidgetItem(log['action']))
            self.log_table.setItem(row, 3, QTableWidgetItem(log['table_name']))
            self.log_table.setItem(row, 4, QTableWidgetItem(str(log['record_id'])))
            self.log_table.setItem(row, 5, QTableWidgetItem(log['details']))

        self.log_table.resizeColumnsToContents()
