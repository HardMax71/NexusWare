from typing import List

from PySide6.QtCore import QDate, QDateTime
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit, QLabel, QTableWidget,
                               QTableWidgetItem, QHeaderView, QScrollArea, QFileDialog, QMessageBox)

from desktop_app.src.services.document_management.report_exporter import ReportExporter, format_report_data
from desktop_app.src.ui.components import StyledButton
from public_api.api import ReportsAPI, APIClient
from public_api.shared_schemas.reports import (InventorySummaryReport, OrderSummaryReport,
                                               WarehousePerformanceReport, KPIDashboard)


class ReportGeneratorWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.reports_api = ReportsAPI(api_client)
        self.report_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addLayout(self.create_controls())
        layout.addWidget(self.create_report_display())
        layout.addLayout(self.create_export_buttons())

    def create_controls(self):
        controls_layout = QHBoxLayout()
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Inventory Summary", "Order Summary", "Warehouse Performance", "KPI Dashboard"
        ])
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
        return controls_layout

    def create_report_display(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.report_display = QWidget()
        self.report_layout = QVBoxLayout(self.report_display)
        self.scroll_area.setWidget(self.report_display)
        return self.scroll_area

    def create_export_buttons(self):
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.export_docx_button = StyledButton("Export to MS Word")
        self.export_docx_button.clicked.connect(lambda: self.export_report('docx'))
        self.export_excel_button = StyledButton("Export to MS Excel")
        self.export_excel_button.clicked.connect(lambda: self.export_report('excel'))

        export_layout.addWidget(self.export_docx_button)
        export_layout.addWidget(self.export_excel_button)
        export_layout.addStretch()

        return export_layout

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
                self.report_data = self.reports_api.get_inventory_summary()
                self.display_inventory_summary(self.report_data)
            elif report_type == "Order Summary":
                self.report_data = self.reports_api.get_order_summary(start_date, end_date)
                self.display_order_summary(self.report_data)
            elif report_type == "Warehouse Performance":
                self.report_data = self.reports_api.get_warehouse_performance(start_date, end_date)
                self.display_warehouse_performance(self.report_data)
            elif report_type == "KPI Dashboard":
                self.report_data = self.reports_api.get_kpi_dashboard()
                self.display_kpi_dashboard(self.report_data)
        except Exception as e:
            self.display_error(str(e))

    def display_inventory_summary(self, report: InventorySummaryReport):
        self._add_title("Inventory Summary Report")
        self._add_summary(f"Total Items: {report.total_items}\nTotal Value: ${report.total_value:.2f}")
        self._add_table(["Product ID", "Product Name", "Quantity", "Value"],
                        [[str(item.product_id), item.product_name, str(item.quantity), f"${item.value:.2f}"]
                         for item in report.items])

    def display_order_summary(self, report: OrderSummaryReport):
        self._add_title("Order Summary Report")
        self._add_date_range(report.start_date, report.end_date)
        self._add_summary(f"Total Orders: {report.summary.total_orders}\n"
                          f"Total Revenue: ${report.summary.total_revenue:.2f}\n"
                          f"Average Order Value: ${report.summary.average_order_value:.2f}")

    def display_warehouse_performance(self, report: WarehousePerformanceReport):
        self._add_title("Warehouse Performance Report")
        self._add_date_range(report.start_date, report.end_date)
        self._add_table(["Metric", "Value", "Unit"],
                        [[metric.name, f"{metric.value:.2f}", metric.unit] for metric in report.metrics])

    def display_kpi_dashboard(self, report: KPIDashboard):
        self._add_title("KPI Dashboard")
        self._add_date(report.date)
        self._add_table(["Metric", "Value", "Trend"],
                        [[metric.name, f"{metric.value:.2f}", metric.trend] for metric in report.metrics])

    def _add_title(self, title: str):
        label = QLabel(title)
        label.setFont(QFont("Arial", 16, QFont.Bold))
        self.report_layout.addWidget(label)

    def _add_summary(self, summary: str):
        label = QLabel(summary)
        label.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(label)

    def _add_date(self, date: int):
        label = QLabel(f"Date: {QDateTime.fromSecsSinceEpoch(date).date().toString('yyyy-MM-dd')}")
        label.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(label)

    def _add_date_range(self, start_date: int, end_date: int):
        label = QLabel(f"From: {QDateTime.fromSecsSinceEpoch(start_date).date().toString('yyyy-MM-dd')} "
                       f"To: {QDateTime.fromSecsSinceEpoch(end_date).date().toString('yyyy-MM-dd')}")
        label.setFont(QFont("Arial", 12))
        self.report_layout.addWidget(label)

    def _add_table(self, headers: List[str], data: List[List[str]]):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(data))

        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                table.setItem(row, col, QTableWidgetItem(cell_data))

        self.report_layout.addWidget(table)

    def display_error(self, error_message: str):
        error_label = QLabel(f"Error: {error_message}")
        error_label.setStyleSheet("color: red;")
        self.report_layout.addWidget(error_label)

    def export_report(self, format: str):
        if not self.report_data:
            QMessageBox.warning(self, "Export Error", "No report data available. Generate a report first.")
            return

        file_filter = "Word Document (*.docx)" if format == 'docx' else "Excel Workbook (*.xlsx)"
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report", "", file_filter)

        if file_name:
            try:
                template_dir = "./resources/templates"

                formatted_data = format_report_data(self.report_data)
                exporter = ReportExporter(formatted_data, format, template_dir)
                exporter.export(file_name)

                QMessageBox.information(self, "Export Successful", f"Report exported successfully to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")
