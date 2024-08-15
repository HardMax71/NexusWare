from PySide6.QtCore import Qt, QDate, QDateTime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit, QTextEdit,
                               QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea)
from PySide6.QtGui import QFont

from public_api.api import ReportsAPI, APIClient
from desktop_app.src.ui.components import StyledButton
from public_api.shared_schemas.reports import (InventorySummaryReport, OrderSummaryReport,
                                               WarehousePerformanceReport, KPIDashboard)


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
        self.report_type_combo.addItems(["Inventory Summary", "Order Summary", "Warehouse Performance", "KPI Dashboard"])
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit(QDate.currentDate())
        self.generate_button = StyledButton("Generate Report")
        self.generate_button.clicked.connect(self.generate_report)
        controls_layout.addWidget(QLabel("Report Type:"))
        controls_layout.addWidget(self.report_type_combo)
        controls_layout.addWidget(QLabel("Start Date:"))
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(QLabel("End Date:"))
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(self.generate_button)
        layout.addLayout(controls_layout)

        # Report display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.report_display = QWidget()
        self.report_layout = QVBoxLayout(self.report_display)
        self.scroll_area.setWidget(self.report_display)
        layout.addWidget(self.scroll_area)

    def generate_report(self):
        report_type = self.report_type_combo.currentText()

        # Clear previous report
        for i in reversed(range(self.report_layout.count())):
            self.report_layout.itemAt(i).widget().setParent(None)

        # Convert QDate to Unix timestamp
        start_date = int(self.start_date.dateTime().toSecsSinceEpoch())
        end_date = int(self.end_date.dateTime().toSecsSinceEpoch())

        try:
            if report_type == "Inventory Summary":
                report_data = self.reports_api.get_inventory_summary()
                self.display_inventory_summary(report_data)
            elif report_type == "Order Summary":
                report_data = self.reports_api.get_order_summary(start_date, end_date)
                self.display_order_summary(report_data)
            elif report_type == "Warehouse Performance":
                report_data = self.reports_api.get_warehouse_performance(start_date, end_date)
                self.display_warehouse_performance(report_data)
            elif report_type == "KPI Dashboard":
                report_data = self.reports_api.get_kpi_dashboard()
                self.display_kpi_dashboard(report_data)
        except Exception as e:
            self.display_error(str(e))

    def display_inventory_summary(self, report: InventorySummaryReport):
        title = QLabel("Inventory Summary Report")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        self.report_layout.addWidget(title)

        summary = QLabel(f"Total Items: {report.total_items}\nTotal Value: ${report.total_value:.2f}")
        summary.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(summary)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Product ID", "Product Name", "Quantity", "Value"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(report.items))

        for row, item in enumerate(report.items):
            table.setItem(row, 0, QTableWidgetItem(str(item.product_id)))
            table.setItem(row, 1, QTableWidgetItem(item.product_name))
            table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            table.setItem(row, 3, QTableWidgetItem(f"${item.value:.2f}"))

        self.report_layout.addWidget(table)

    def display_order_summary(self, report: OrderSummaryReport):
        title = QLabel("Order Summary Report")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        self.report_layout.addWidget(title)

        date_range = QLabel(f"From: {QDateTime.fromSecsSinceEpoch(report.start_date).date().toString('yyyy-MM-dd')} "
                            f"To: {QDateTime.fromSecsSinceEpoch(report.end_date).date().toString('yyyy-MM-dd')}")
        date_range.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(date_range)

        summary = QLabel(f"Total Orders: {report.summary.total_orders}\n"
                         f"Total Revenue: ${report.summary.total_revenue:.2f}\n"
                         f"Average Order Value: ${report.summary.average_order_value:.2f}")
        summary.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(summary)

    def display_warehouse_performance(self, report: WarehousePerformanceReport):
        title = QLabel("Warehouse Performance Report")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        self.report_layout.addWidget(title)

        date_range = QLabel(f"From: {QDateTime.fromSecsSinceEpoch(report.start_date).date().toString('yyyy-MM-dd')} "
                            f"To: {QDateTime.fromSecsSinceEpoch(report.end_date).date().toString('yyyy-MM-dd')}")
        date_range.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(date_range)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Metric", "Value", "Unit"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(report.metrics))

        for row, metric in enumerate(report.metrics):
            table.setItem(row, 0, QTableWidgetItem(metric.name))
            table.setItem(row, 1, QTableWidgetItem(f"{metric.value:.2f}"))
            table.setItem(row, 2, QTableWidgetItem(metric.unit))

        self.report_layout.addWidget(table)

    def display_kpi_dashboard(self, report: KPIDashboard):
        title = QLabel("KPI Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        self.report_layout.addWidget(title)

        date = QLabel(f"Date: {QDateTime.fromSecsSinceEpoch(report.date).date().toString('yyyy-MM-dd')}")
        date.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(date)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Metric", "Value", "Trend"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(report.metrics))

        for row, metric in enumerate(report.metrics):
            table.setItem(row, 0, QTableWidgetItem(metric.name))
            table.setItem(row, 1, QTableWidgetItem(f"{metric.value:.2f}"))
            table.setItem(row, 2, QTableWidgetItem(metric.trend))

        self.report_layout.addWidget(table)

    def display_error(self, error_message: str):
        error_label = QLabel(f"Error: {error_message}")
        error_label.setStyleSheet("color: red;")
        self.report_layout.addWidget(error_label)