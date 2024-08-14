from datetime import datetime

from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from desktop_app.src.ui.components import CardWidget
from public_api.api import APIClient, ReportsAPI, InventoryAPI, PickListsAPI


class DashboardWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.reports_api = ReportsAPI(api_client)
        self.pick_lists_api = PickListsAPI(api_client)
        self.inventory_api = InventoryAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Add summary cards
        cards_layout = QHBoxLayout()
        kpi_data = self.reports_api.get_kpi_dashboard()
        for metric in kpi_data.metrics:
            cards_layout.addWidget(self.create_summary_card(metric.name, metric.value))
        layout.addLayout(cards_layout)

        # Add charts
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.create_inventory_chart())
        charts_layout.addWidget(self.create_performance_chart())
        layout.addLayout(charts_layout)

    def create_summary_card(self, title, value):
        content = QLabel(f"{value:.2f}" if isinstance(value, float) else str(value))
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("font-size: 24px; font-weight: bold;")
        return CardWidget(title, content)

    def create_inventory_chart(self):
        inventory_data = self.inventory_api.get_inventory_summary()
        series = QPieSeries()
        for category, quantity in inventory_data.category_quantities.items():
            series.append(category, quantity)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Inventory by Category")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def create_performance_chart(self):
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        picking_performance = self.pick_lists_api.get_picking_performance(start_date=start_date, end_date=end_date)

        set0 = QBarSet("Average Picking Time")
        set1 = QBarSet("Items Picked Per Hour")
        set0.append(picking_performance.average_picking_time)
        set1.append(picking_performance.items_picked_per_hour)

        series = QBarSeries()
        series.append(set0)
        series.append(set1)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Picking Performance")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axisY = QValueAxis()
        axisY.setRange(0, max(set0.at(0), set1.at(0)) * 1.1)  # Set range with 10% headroom
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        categories = ["Avg. Time", "Items/Hour"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view
