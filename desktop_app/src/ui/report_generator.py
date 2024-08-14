from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit, QTextEdit

from public_api.api import ReportsAPI, APIClient
from desktop_app.src.ui.components import StyledButton


# TODO: implement missing functions
class ReportGeneratorWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.reports_api = ReportsAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Inventory Summary", "Order Summary", "Warehouse Performance"])
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit(QDate.currentDate())
        self.generate_button = StyledButton("Generate Report")
        self.generate_button.clicked.connect(self.generate_report)
        controls_layout.addWidget(self.report_type_combo)
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(self.generate_button)
        layout.addLayout(controls_layout)

        # Report display
        self.report_display = QTextEdit()
        self.report_display.setReadOnly(True)
        layout.addWidget(self.report_display)

    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date.date().toString(Qt.ISODate)
        end_date = self.end_date.date().toString(Qt.ISODate)

        if report_type == "Inventory Summary":
            report_data = self.reports_api.get_inventory_summary()
        elif report_type == "Order Summary":
            report_data = self.reports_api.get_order_summary(start_date, end_date)
        elif report_type == "Warehouse Performance":
            report_data = self.reports_api.get_warehouse_performance(start_date, end_date)

        self.display_report(report_data)

    def display_report(self, report_data):
        # Format and display the report data in self.report_display
        self.report_display.setPlainText(str(report_data))  # Replace with proper formatting
