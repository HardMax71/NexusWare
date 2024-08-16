from datetime import datetime

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox,
                               QPushButton, QHBoxLayout, QMessageBox, QDateEdit)

from public_api.api import InventoryAPI, LocationsAPI, ProductsAPI
from public_api.shared_schemas import Inventory, InventoryUpdate, InventoryCreate, InventoryAdjustment


class InventoryDialog(QDialog):
    def __init__(self, inventory_api: InventoryAPI, locations_api: LocationsAPI,
                 products_api: ProductsAPI, item_data: Inventory = None,
                 parent=None):
        super().__init__(parent)
        self.inventory_api = inventory_api
        self.locations_api = locations_api
        self.products_api = products_api
        self.item_data = item_data
        self.product_data = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Inventory Item" if not self.item_data else "Edit Inventory Item")
        layout = QFormLayout(self)

        self.product_input = QComboBox()
        self.sku_input = QLineEdit()
        self.sku_input.setReadOnly(True)
        self.name_input = QLineEdit()
        self.name_input.setReadOnly(True)
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1000000)
        self.location_input = QComboBox()
        self.expiration_date_input = QDateEdit()
        self.expiration_date_input.setCalendarPopup(True)

        layout.addRow("Product:", self.product_input)
        layout.addRow("SKU:", self.sku_input)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Location:", self.location_input)
        layout.addRow("Expiration Date:", self.expiration_date_input)

        self.load_products()
        self.load_locations()

        if self.item_data:
            self.set_existing_item_data()
        else:
            self.quantity_input.setValue(0)
            self.expiration_date_input.setDate(datetime.now().date())

        self.product_input.currentIndexChanged.connect(self.update_product_details)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_item)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

    def load_products(self):
        try:
            products = self.products_api.get_products()
            for product in products:
                self.product_input.addItem(f"{product.sku} - {product.name}", product.id)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load products: {str(e)}")

    def load_locations(self):
        try:
            locations = self.locations_api.get_locations()
            for location in locations:
                self.location_input.addItem(location.name, location.id)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load locations: {str(e)}")

    def set_existing_item_data(self):
        if self.item_data:
            self.product_data = self.products_api.get_product(self.item_data.product_id)
            index = self.product_input.findData(self.item_data.product_id)
            if index >= 0:
                self.product_input.setCurrentIndex(index)
            self.quantity_input.setValue(self.item_data.quantity)
            if self.item_data.location_id:
                index = self.location_input.findData(self.item_data.location_id)
                if index >= 0:
                    self.location_input.setCurrentIndex(index)
            if self.item_data.expiration_date:
                self.expiration_date_input.setDate(QDateTime.fromSecsSinceEpoch(self.item_data.expiration_date).date())
            self.update_product_details()

    def update_product_details(self):
        product_id = self.product_input.currentData()
        if product_id:
            product = self.products_api.get_product(product_id)
            self.sku_input.setText(product.sku)
            self.name_input.setText(product.name)

    def save_item(self):
        try:
            product_id = self.product_input.currentData()
            expiration_date = int(self.expiration_date_input.dateTime().toSecsSinceEpoch())  # Convert to timestamp

            if self.item_data:
                # Update existing item
                inventory_update = InventoryUpdate(
                    product_id=product_id,
                    quantity=self.quantity_input.value(),
                    location_id=self.location_input.currentData(),
                    expiration_date=expiration_date
                )
                self.inventory_api.update_inventory(self.item_data.id, inventory_update)
            else:
                # Create new item
                inventory_create = InventoryCreate(
                    product_id=product_id,
                    quantity=self.quantity_input.value(),
                    location_id=self.location_input.currentData(),
                    expiration_date=expiration_date  # Pass timestamp
                )
                self.inventory_api.create_inventory(inventory_create)

            QMessageBox.information(self, "Success", "Item saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save item: {str(e)}")


class AdjustmentDialog(QDialog):
    def __init__(self, inventory_api: InventoryAPI, id: int, parent=None):
        super().__init__(parent)
        self.inventory_api = inventory_api
        self.id = id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Adjust Inventory")
        layout = QFormLayout(self)

        self.adjustment_input = QSpinBox()
        self.adjustment_input.setRange(-1000000, 1000000)
        self.reason_input = QLineEdit()

        layout.addRow("Adjustment:", self.adjustment_input)
        layout.addRow("Reason:", self.reason_input)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_adjustment)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

    def save_adjustment(self):
        try:
            adjustment_data = InventoryAdjustment(
                product_id=self.id,
                location_id=self.id,
                quantity_change=self.adjustment_input.value(),
                reason=self.reason_input.text(),
                timestamp=int(datetime.now().timestamp())  # Pass timestamp
            )
            self.inventory_api.adjust_inventory(self.id, adjustment_data)
            QMessageBox.information(self, "Success", "Adjustment saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save adjustment: {str(e)}")
