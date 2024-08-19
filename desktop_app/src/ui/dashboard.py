import time
from datetime import datetime, timedelta

from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis, \
    QLineSeries, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
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

        # Add new charts
        new_charts_layout = QHBoxLayout()
        new_charts_layout.addWidget(self.create_inventory_trend_chart())
        new_charts_layout.addWidget(self.create_order_statistics_chart())
        layout.addLayout(new_charts_layout)

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
        chart.legend().setAlignment(Qt.AlignRight)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def create_performance_chart(self):
        # Convert datetime objects to Unix timestamps
        start_date_timestamp = int(time.mktime(datetime(2023, 1, 1).timetuple()))
        end_date_timestamp = int(time.mktime(datetime(2024, 12, 31).timetuple()))

        picking_performance = self.pick_lists_api.get_picking_performance(
            start_date=start_date_timestamp, end_date=end_date_timestamp
        )

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
        chart.legend().setAlignment(Qt.AlignRight)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def create_inventory_trend_chart(self):
        # Use inventory summary data to create a trend
        inventory_summary = self.reports_api.get_inventory_summary()

        series = QLineSeries()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=len(inventory_summary.items))

        for i, item in enumerate(inventory_summary.items):
            date = start_date + timedelta(days=i)
            series.append(QDateTime(date).toMSecsSinceEpoch(), item.quantity)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Inventory Trend by Product")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axisX = QDateTimeAxis()
        axisX.setFormat("dd MMM")
        axisX.setTitleText("Date")
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setTitleText("Quantity")
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        chart.legend().setVisible(False)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def create_order_statistics_chart(self):
        # Use order summary data to create statistics
        end_date = int(datetime.now().timestamp())
        start_date = int((datetime.now() - timedelta(days=7)).timestamp())
        order_summary = self.reports_api.get_order_summary(start_date, end_date)

        set_total_orders = QBarSet("Total Orders")
        set_total_revenue = QBarSet("Total Revenue")

        set_total_orders.append([order_summary.summary.total_orders])
        set_total_revenue.append([order_summary.summary.total_revenue])

        series = QBarSeries()
        series.append(set_total_orders)
        series.append(set_total_revenue)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Weekly Order Statistics")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axisX = QBarCategoryAxis()
        axisX.append(["Last 7 Days"])
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view
