import json
from datetime import datetime, time

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
                               QDialog, QLabel, QCheckBox, QDoubleSpinBox, QDateEdit,
                               QGroupBox, QGridLayout, QWidget)

from desktop_app.src.ui.components import StyledButton
from desktop_app.src.ui.components.icon_path import IconPath
from public_api.api import APIClient, SearchAPI
from public_api.shared_schemas.order import OrderStatus


class AdvancedSearchDialog(QDialog):
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.search_api = SearchAPI(api_client)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Advanced Search")
        self.setMinimumSize(1200, 800)

        main_layout = QHBoxLayout(self)

        # Left side - Search options
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.search_type = QComboBox()
        self.search_type.addItems(["Products", "Orders"])
        self.search_type.currentTextChanged.connect(self.update_search_options)
        left_layout.addWidget(QLabel("Search Type:"))
        left_layout.addWidget(self.search_type)

        self.search_options_widget = QWidget()
        self.search_options_layout = QVBoxLayout(self.search_options_widget)
        left_layout.addWidget(self.search_options_widget)

        self.search_button = StyledButton("Search", icon_path=IconPath.SEARCH)
        self.search_button.clicked.connect(self.perform_search)
        left_layout.addWidget(self.search_button)

        left_layout.addStretch()

        # Right side - Results table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.results_table = QTableWidget()
        self.results_table.setSortingEnabled(True)
        self.results_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        right_layout.addWidget(self.results_table)

        # Add left and right widgets to main layout
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 3)

        self.update_search_options()

    def update_search_options(self):
        # Clear existing widgets in the layout
        for i in reversed(range(self.search_options_layout.count())):
            self.search_options_layout.itemAt(i).widget().setParent(None)

        if self.search_type.currentText() == "Products":
            self.setup_product_search_options()
        else:
            self.setup_order_search_options()

    def setup_product_search_options(self):
        group_box = QGroupBox("Product Search Options")
        layout = QGridLayout()

        self.product_search_term = QLineEdit()
        self.product_category = QComboBox()
        self.product_category.addItem("All Categories")
        self.min_price = QDoubleSpinBox()
        self.max_price = QDoubleSpinBox()
        self.in_stock = QCheckBox("In Stock Only")

        layout.addWidget(QLabel("Search Term:"), 0, 0)
        layout.addWidget(self.product_search_term, 0, 1)
        layout.addWidget(QLabel("Category:"), 1, 0)
        layout.addWidget(self.product_category, 1, 1)
        layout.addWidget(QLabel("Min Price:"), 2, 0)
        layout.addWidget(self.min_price, 2, 1)
        layout.addWidget(QLabel("Max Price:"), 3, 0)
        layout.addWidget(self.max_price, 3, 1)
        layout.addWidget(self.in_stock, 4, 0, 1, 2)

        group_box.setLayout(layout)
        self.search_options_layout.addWidget(group_box)

    def setup_order_search_options(self):
        group_box = QGroupBox("Order Search Options")
        layout = QGridLayout()

        self.order_search_term = QLineEdit()
        self.order_status = QComboBox()
        self.order_status.addItems(["All"] + [status.value for status in OrderStatus])
        self.min_total = QDoubleSpinBox()
        self.max_total = QDoubleSpinBox()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())

        layout.addWidget(QLabel("Search Term:"), 0, 0)
        layout.addWidget(self.order_search_term, 0, 1)
        layout.addWidget(QLabel("Status:"), 1, 0)
        layout.addWidget(self.order_status, 1, 1)
        layout.addWidget(QLabel("Min Total:"), 2, 0)
        layout.addWidget(self.min_total, 2, 1)
        layout.addWidget(QLabel("Max Total:"), 3, 0)
        layout.addWidget(self.max_total, 3, 1)
        layout.addWidget(QLabel("Start Date:"), 4, 0)
        layout.addWidget(self.start_date, 4, 1)
        layout.addWidget(QLabel("End Date:"), 5, 0)
        layout.addWidget(self.end_date, 5, 1)

        group_box.setLayout(layout)
        self.search_options_layout.addWidget(group_box)

    def perform_search(self):
        if self.search_type.currentText() == "Products":
            results = self.search_products()
        else:
            results = self.search_orders()

        self.display_results(results)

    def search_products(self):
        return self.search_api.search_products(
            q=self.product_search_term.text(),
            category_id=self.product_category.currentIndex() if self.product_category.currentIndex() > 0 else None,
            min_price=self.min_price.value() if self.min_price.value() > 0 else None,
            max_price=self.max_price.value() if self.max_price.value() > 0 else None,
            in_stock=self.in_stock.isChecked()
        )

    def search_orders(self):
        start_date = datetime.combine(self.start_date.date().toPython(), time.min)
        end_date = datetime.combine(self.end_date.date().toPython(), time.max)

        return self.search_api.search_orders(
            q=self.order_search_term.text(),
            status=self.order_status.currentText() if self.order_status.currentText() != "All" else None,
            min_total=self.min_total.value() if self.min_total.value() > 0 else None,
            max_total=self.max_total.value() if self.max_total.value() > 0 else None,
            start_date=int(start_date.timestamp()),
            end_date=int(end_date.timestamp())
        )

    def display_results(self, results):
        self.results_table.clear()
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return

        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(results[0].model_dump()))
        self.results_table.setHorizontalHeaderLabels(results[0].model_dump().keys())

        for row, item in enumerate(results):
            for col, (key, value) in enumerate(item.model_dump().items()):
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, indent=2)
                elif isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                self.results_table.setItem(row, col, QTableWidgetItem(str(value)))

        self.results_table.resizeColumnsToContents()

    def on_header_clicked(self, logical_index):
        if self.results_table.horizontalHeader().sortIndicatorSection() == logical_index:
            if self.results_table.horizontalHeader().sortIndicatorOrder() == Qt.AscendingOrder:
                self.results_table.sortItems(logical_index, Qt.DescendingOrder)
            else:
                self.results_table.sortItems(logical_index, Qt.AscendingOrder)
        else:
            self.results_table.sortItems(logical_index, Qt.AscendingOrder)

