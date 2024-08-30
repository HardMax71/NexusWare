from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QDialogButtonBox, QLabel, QWidget, QGroupBox)

from public_api.api import LocationsAPI
from public_api.shared_schemas import ProductWithCategoryAndInventory


class ProductDetailsDialog(QDialog):
    def __init__(self, product: ProductWithCategoryAndInventory, locations_api: LocationsAPI, parent=None):
        super().__init__(parent)
        self.product = product
        self.locations_api = locations_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Product Details - {self.product.name}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        main_layout = QHBoxLayout(self)

        # Left side - Product Info and OK button
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Create a group box for product data
        product_group = QGroupBox("Product Data")
        info_layout = QFormLayout(product_group)
        info_layout.addRow("SKU:", QLabel(self.product.sku))
        info_layout.addRow("Name:", QLabel(self.product.name))
        info_layout.addRow("Category:", QLabel(self.product.category.name if self.product.category else "N/A"))
        info_layout.addRow("Price:", QLabel(f"${self.product.price:.2f}"))

        description_label = QLabel(self.product.description or "N/A")
        description_label.setWordWrap(True)
        info_layout.addRow("Description:", description_label)

        left_layout.addWidget(product_group)
        left_layout.addStretch(1)

        # OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        left_layout.addWidget(button_box)

        # Right side - Available Locations Table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        inventory_table = QTableWidget()
        inventory_table.setColumnCount(3)
        inventory_table.setHorizontalHeaderLabels(["Location", "Quantity", "Last Updated"])
        inventory_table.setRowCount(len(self.product.inventory_items))
        inventory_table.setSortingEnabled(True)

        header = inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        for row, item in enumerate(self.product.inventory_items):
            location = self.locations_api.get_location(item.location_id)
            location_name = location.name if location else f"Unknown (ID: {item.location_id})"

            inventory_table.setItem(row, 0, QTableWidgetItem(location_name))
            inventory_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            inventory_table.setItem(row, 2, QTableWidgetItem(
                datetime.fromtimestamp(item.last_updated).strftime("%Y-%m-%d %H:%M:%S")))

        right_layout.addWidget(QLabel("Available Locations"))
        right_layout.addWidget(inventory_table)

        # Add left and right widgets to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # Set layout proportions
        main_layout.setStretch(0, 1)  # Left side
        main_layout.setStretch(1, 2)  # Right side
