from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit

from desktop_app.src.api import ReportsAPI
from desktop_app.src.ui.components import StyledButton


class DataAnalysisWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.reports_api = ReportsAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Sales Trend", "Inventory Turnover", "Order Fulfillment Time"])
        self.start_date = QDateEdit(QDateTime.currentDateTime().addDays(-30).date())
        self.end_date = QDateEdit(QDateTime.currentDateTime().date())
        self.analyze_button = StyledButton("Analyze")
        self.analyze_button.clicked.connect(self.perform_analysis)
        controls_layout.addWidget(self.analysis_type_combo)
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(self.analyze_button)
        layout.addLayout(controls_layout)

        # Chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

    def perform_analysis(self):
        analysis_type = self.analysis_type_combo.currentText()
        start_date = self.start_date.date().toString(Qt.ISODate)
        end_date = self.end_date.date().toString(Qt.ISODate)

        # TODO: implement functions for reports api
        if analysis_type == "Sales Trend":
            data = self.reports_api.get_sales_trend(start_date, end_date)
        elif analysis_type == "Inventory Turnover":
            data = self.reports_api.get_inventory_turnover(start_date, end_date)
        elif analysis_type == "Order Fulfillment Time":
            data = self.reports_api.get_order_fulfillment_time(start_date, end_date)

        self.update_chart(analysis_type, data)

    def update_chart(self, analysis_type, data):
        series = QLineSeries()
        for point in data:
            series.append(QDateTime.fromString(point['date'], Qt.ISODate).toMSecsSinceEpoch(), point['value'])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(analysis_type)

        date_axis = QDateTimeAxis()
        date_axis.setFormat("dd-MM-yyyy")
        date_axis.setTitleText("Date")
        chart.addAxis(date_axis, Qt.AlignBottom)
        series.attachAxis(date_axis)

        value_axis = QValueAxis()
        value_axis.setTitleText("Value")
        chart.addAxis(value_axis, Qt.AlignLeft)
        series.attachAxis(value_axis)

        self.chart_view.setChart(chart)
