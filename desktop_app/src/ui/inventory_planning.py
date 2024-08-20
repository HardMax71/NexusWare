from PySide6 import QtGui, QtCore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, \
    QHeaderView

from desktop_app.src.ui.components import StyledButton
from desktop_app.src.ui.warehouse_visualization_window import WarehouseVisualizationWindow
from public_api.api import ProductsAPI, InventoryAPI, APIClient


class InventoryPlanningWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.products_api = ProductsAPI(api_client)
        self.inventory_api = InventoryAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.update_forecast)
        self.forecast_button = StyledButton("Generate Forecast")
        self.forecast_button.clicked.connect(self.generate_forecast)
        controls_layout.addWidget(self.product_combo)
        controls_layout.addWidget(self.forecast_button)
        layout.addLayout(controls_layout)

        # Forecast chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

        # Reorder suggestions table
        self.reorder_table = QTableWidget()
        self.reorder_table.setColumnCount(4)
        self.reorder_table.setHorizontalHeaderLabels(["SKU", "Name", "Current Stock", "Suggested Reorder"])
        self.reorder_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.reorder_table)

        self.visualization_button = QPushButton("3D Warehouse Visualization")
        self.visualization_button.clicked.connect(self.open_3d_visualization)
        layout.addWidget(self.visualization_button)

        self.load_products()

    def load_products(self):
        products = self.products_api.get_products()
        self.product_combo.clear()
        for product in products:
            self.product_combo.addItem(product.name, product.id)

    def open_3d_visualization(self):
        self.visualization_window = WarehouseVisualizationWindow(self.api_client)
        self.visualization_window.show()

    def update_forecast(self):
        product_id = self.product_combo.currentData()
        if product_id:
            forecast_data = self.inventory_api.get_inventory_forecast(product_id)
            self.update_chart(forecast_data)

    def generate_forecast(self):
        product_id = self.product_combo.currentData()
        if product_id:
            forecast_data = self.inventory_api.get_inventory_forecast(product_id)
            self.update_chart(forecast_data)
            self.update_reorder_suggestions()

    def update_chart(self, forecast_data: dict):
        series = QLineSeries()
        series.setName("Projected quantity")
        series.setPen(QtGui.QPen(QtGui.QColor("blue"), 2))

        for point in forecast_data['forecast']:
            date_in_ms = point['date'] * 1000
            series.append(date_in_ms, point['quantity'])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Inventory Forecast")

        axis_x = QDateTimeAxis()
        axis_x.setTickCount(5)
        axis_x.setFormat("dd-MM-yyyy")
        axis_x.setTitleText("Date")

        min_date = int(series.pointsVector()[0].x())
        max_date = int(series.pointsVector()[-1].x())
        axis_x.setRange(QtCore.QDateTime.fromMSecsSinceEpoch(min_date), QtCore.QDateTime.fromMSecsSinceEpoch(max_date))

        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        axis_y.setTitleText("Quantity")

        min_quantity = min(point['quantity'] for point in forecast_data['forecast'])
        max_quantity = max(point['quantity'] for point in forecast_data['forecast'])
        axis_y.setRange(min_quantity - 5, max_quantity + 5)

        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)

    def update_reorder_suggestions(self):
        suggestions = self.inventory_api.get_reorder_suggestions()
        self.reorder_table.setRowCount(len(suggestions))
        for row, item in enumerate(suggestions):
            self.reorder_table.setItem(row, 0, QTableWidgetItem(item['sku']))
            self.reorder_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.reorder_table.setItem(row, 2, QTableWidgetItem(str(item['current_stock'])))
            self.reorder_table.setItem(row, 3, QTableWidgetItem(str(item['suggested_reorder'])))
