from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QDialogButtonBox, QLabel)

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
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        info_layout = QFormLayout()
        info_layout.addRow("SKU:", QLabel(self.product.sku))
        info_layout.addRow("Name:", QLabel(self.product.name))
        info_layout.addRow("Category:", QLabel(self.product.category.name if self.product.category else "N/A"))
        info_layout.addRow("Price:", QLabel(f"${self.product.price:.2f}"))
        info_layout.addRow("Description:", QLabel(self.product.description or "N/A"))

        layout.addLayout(info_layout)

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

        layout.addWidget(inventory_table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
