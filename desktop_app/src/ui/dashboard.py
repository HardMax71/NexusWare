import time
from datetime import datetime, timedelta

from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis, \
    QLineSeries, QDateTimeAxis, QHorizontalBarSeries
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QColor
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
        total_quantity = sum(inventory_data.category_quantities.values())

        for category, quantity in inventory_data.category_quantities.items():
            slice = series.append(category, quantity)
            slice.setLabelVisible(True)

            percentage = (quantity / total_quantity) * 100
            slice.setLabel(f"{category}: {quantity} ({percentage:.1f}%)")

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Inventory by Category")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def create_performance_chart(self):
        # Calculate timestamps for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_date_timestamp = int(time.mktime(start_date.timetuple()))
        end_date_timestamp = int(time.mktime(end_date.timetuple()))

        picking_performance = self.pick_lists_api.get_picking_performance(
            start_date=start_date_timestamp, end_date=end_date_timestamp
        )

        set0 = QBarSet("Average Picking Time")
        set1 = QBarSet("Items Picked Per Hour")
        set0.append(picking_performance.average_picking_time)
        set1.append(picking_performance.items_picked_per_hour)

        avg_time_series = QBarSeries()
        avg_time_series.append(set0)
        avg_time_series.setLabelsVisible(True)

        items_picked_series = QBarSeries()
        items_picked_series.append(set1)
        items_picked_series.setLabelsVisible(True)

        chart = QChart()
        chart.addSeries(avg_time_series)
        chart.addSeries(items_picked_series)
        chart.setTitle("Picking Performance (Last 30 Days)")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Set up X-axis
        categories = ["Avg. Picking Time", "Items Picked/Hour"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignBottom)

        # Create and set up left Y-axis (for time)
        axisYLeft = QValueAxis()
        axisYLeft.setRange(0, picking_performance.average_picking_time * 1.1)  # 10% headroom
        axisYLeft.setTitleText("Time (minutes)")
        chart.addAxis(axisYLeft, Qt.AlignLeft)
        avg_time_series.attachAxis(axisYLeft)

        # Create and set up right Y-axis (for items)
        axisYRight = QValueAxis()
        axisYRight.setRange(0, picking_performance.items_picked_per_hour * 1.1)  # 10% headroom
        axisYRight.setTitleText("Items")
        chart.addAxis(axisYRight, Qt.AlignRight)
        items_picked_series.attachAxis(axisYRight)

        # Hide legend
        chart.legend().hide()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    def create_inventory_trend_chart(self):
        days_past = 3
        days_future = 3

        inventory_trend = self.reports_api.get_inventory_trend(
            days_past=days_past,
            days_future=days_future
        )

        real_data_series = QLineSeries()
        prediction_series = QLineSeries()

        real_data_series.setName("Previous days")
        prediction_series.setName("Next days")

        prediction_series.setColor(QColor(255, 0, 0))  # Red color for predictions

        # Process past data
        # More info: https://doc.qt.io/qtforpython-6/overviews/qtcharts-datetimeaxis-example.html
        for item in inventory_trend["past"]:
            moment_in_time = QDateTime.fromSecsSinceEpoch(item.timestamp)
            real_data_series.append(moment_in_time.toMSecsSinceEpoch(), item.quantity)

        # Process predictions
        for item in inventory_trend["predictions"]:
            moment_in_time = QDateTime.fromSecsSinceEpoch(item.timestamp)
            prediction_series.append(moment_in_time.toMSecsSinceEpoch(), item.quantity)

        prediction_series.insert(0, real_data_series.at(
            real_data_series.count() - 1))  # Add last real data point to predictions

        chart = QChart()
        chart.addSeries(real_data_series)
        chart.addSeries(prediction_series)

        chart.setTitle("Inventory Trend")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        axisX = QDateTimeAxis()
        axisX.setFormat("dd.MM")
        axisX.setTitleText("Date")
        axisX.setRange(QDateTime.currentDateTime().addDays(-days_past),
                       QDateTime.currentDateTime().addDays(days_future))

        axisX.setTickCount(days_past + days_future + 1)  # past + future + today
        chart.addAxis(axisX, Qt.AlignBottom)
        real_data_series.attachAxis(axisX)
        prediction_series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setTitleText("Quantity")
        chart.addAxis(axisY, Qt.AlignLeft)
        real_data_series.attachAxis(axisY)
        prediction_series.attachAxis(axisY)

        y_min = axisY.min()
        y_max = axisY.max()
        y_range = y_max - y_min
        axisY.setRange(max(0, y_min - 0.1 * y_range), y_max + 0.1 * y_range)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        return chart_view

    def create_order_statistics_chart(self):
        # Use order summary data to create statistics
        end_date = int(datetime.now().timestamp())
        start_date = int((datetime.now() - timedelta(days=7)).timestamp())
        order_summary = self.reports_api.get_order_summary(start_date, end_date)

        set_total_revenue = QBarSet("Total Revenue")
        set_avg_order_value = QBarSet("Avg Order Value")

        total_revenue = order_summary.summary.total_revenue
        avg_order_value = order_summary.summary.average_order_value

        set_total_revenue.append(total_revenue)
        set_avg_order_value.append(avg_order_value)

        revenue_series = QHorizontalBarSeries()
        revenue_series.append(set_total_revenue)
        avg_order_series = QHorizontalBarSeries()
        avg_order_series.append(set_avg_order_value)

        chart = QChart()
        chart.addSeries(revenue_series)
        chart.addSeries(avg_order_series)
        chart.setTitle("Weekly Order Statistics")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Total Revenue", "Avg Order Value"]
        axisY = QBarCategoryAxis()
        axisY.append(categories)
        chart.addAxis(axisY, Qt.AlignLeft)

        axisXTop = QValueAxis()
        max_money_value = max(total_revenue, avg_order_value)
        axisXTop.setRange(0, max_money_value * 1.1)  # 10% headroom
        axisXTop.setTitleText("Amount ($)")
        chart.addAxis(axisXTop, Qt.AlignTop)
        revenue_series.attachAxis(axisXTop)
        avg_order_series.attachAxis(axisXTop)

        chart.legend().setVisible(False)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view
