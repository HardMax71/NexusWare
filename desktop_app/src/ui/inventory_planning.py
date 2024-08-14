from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QPainter, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox

from public_api.api import ProductsAPI, InventoryAPI, APIClient
from desktop_app.src.ui.components import StyledButton


# TODO: Implement all missing inventory api methods

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
        layout.addWidget(self.reorder_table)

        self.load_products()

    def load_products(self):
        products = self.products_api.get_products()
        self.product_combo.clear()
        for product in products:
            self.product_combo.addItem(product.name, product.product_id)

    def update_forecast(self):
        product_id = self.product_combo.currentData()
        if product_id:
            forecast_data = self.inventory_api.get_inventory_forecast(product_id)
            self.update_chart(forecast_data)

    def generate_forecast(self):
        product_id = self.product_combo.currentData()
        if product_id:
            forecast_data = self.inventory_api.generate_inventory_forecast(product_id)
            self.update_chart(forecast_data)
            self.update_reorder_suggestions()

    def update_chart(self, forecast_data):
        series = QLineSeries()
        for point in forecast_data['forecast']:
            date = QDateTime.fromString(point['date'], Qt.ISODate)
            x = date.toMSecsSinceEpoch()  # Convert date to milliseconds
            y = float(point['quantity'])  # Convert quantity to float
            series.append(x, y)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Inventory Forecast")

        # Create X axis
        axis_x = QDateTimeAxis()
        axis_x.setTickCount(5)
        axis_x.setFormat("dd-MM-yyyy")
        axis_x.setTitleText("Date")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Create Y axis
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        axis_y.setTitleText("Quantity")
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
