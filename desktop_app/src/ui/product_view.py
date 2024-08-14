from datetime import datetime
from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QStackedWidget, QMessageBox, QComboBox,
                               QFormLayout, QDoubleSpinBox, QDialogButtonBox, QLabel)

from desktop_app.src.ui.components import StyledButton
from public_api.api import ProductsAPI, APIClient, ProductCategoriesAPI, LocationsAPI
from public_api.shared_schemas.inventory import (ProductWithCategoryAndInventory, ProductFilter, ProductCreate,
                                                 ProductUpdate)


class ProductView(QWidget):
    product_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.products_api = ProductsAPI(api_client)
        self.categories_api = ProductCategoriesAPI(api_client)
        self.locations_api = LocationsAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content and product details
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main Product View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.filter_products)
        controls_layout.addWidget(self.search_input)

        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.load_categories()
        self.category_combo.currentIndexChanged.connect(self.refresh_products)
        controls_layout.addWidget(self.category_combo)

        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_products)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["SKU", "Name", "Category", "Price", "Total Stock", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.stacked_widget.addWidget(main_widget)

        # Floating Action Button for adding new products
        self.fab = StyledButton("+")
        self.fab.clicked.connect(self.create_new_product)
        layout.addWidget(self.fab)

        self.refresh_products()

    def load_categories(self):
        categories = self.categories_api.get_categories()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)

    def refresh_products(self):
        category_id = self.category_combo.currentData()
        filter_params = ProductFilter(category_id=category_id) if category_id else None
        products = self.products_api.get_products(product_filter=filter_params)
        self.update_table(products)

    def update_table(self, items: List[ProductWithCategoryAndInventory]):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item.sku))
            self.table.setItem(row, 1, QTableWidgetItem(item.name))
            self.table.setItem(row, 2, QTableWidgetItem(item.category.name if item.category else ""))
            self.table.setItem(row, 3, QTableWidgetItem(f"${item.price:.2f}"))

            total_stock = sum(inv.quantity for inv in item.inventory_items)
            self.table.setItem(row, 4, QTableWidgetItem(str(total_stock)))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View")
            view_button.clicked.connect(lambda _, i=item.id: self.view_product(i))
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, i=item.id: self.edit_product(i))
            delete_button = StyledButton("Delete")
            delete_button.clicked.connect(lambda _, i=item.id: self.delete_product(i))

            actions_layout.addWidget(view_button)
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 5, actions_widget)

            # Color coding based on stock level
            if total_stock == 0:
                self.table.item(row, 4).setBackground(QColor(255, 200, 200))  # Light red for out of stock
            elif total_stock < 10:
                self.table.item(row, 4).setBackground(QColor(255, 255, 200))  # Light yellow for low stock

    def filter_products(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            row_match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.table.setRowHidden(row, not row_match)

    def create_new_product(self):
        dialog = ProductDialog(self.products_api, self.categories_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_products()
            self.product_updated.emit()

    def view_product(self, product_id):
        product = self.products_api.get_product(product_id)
        dialog = ProductDetailsDialog(product, self.locations_api, parent=self)
        dialog.exec_()

    def edit_product(self, product_id):
        product = self.products_api.get_product(product_id)
        dialog = ProductDialog(self.products_api, self.categories_api, product_data=product, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_products()
            self.product_updated.emit()

    def delete_product(self, product_id):
        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete this product?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.products_api.delete_product(product_id)
                self.refresh_products()
                self.product_updated.emit()
                QMessageBox.information(self, "Success", "Product deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")


class ProductDialog(QDialog):
    def __init__(self, products_api: ProductsAPI, categories_api: ProductCategoriesAPI,
                 product_data: Optional[ProductWithCategoryAndInventory] = None, parent=None):
        super().__init__(parent)
        self.products_api = products_api
        self.categories_api = categories_api
        self.product_data = product_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Product" if not self.product_data else "Edit Product")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.sku_input = QLineEdit()
        form_layout.addRow("SKU:", self.sku_input)

        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Category:", self.category_combo)

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(1000000)
        self.price_input.setPrefix("$")
        form_layout.addRow("Price:", self.price_input)

        self.description_input = QLineEdit()
        form_layout.addRow("Description:", self.description_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.product_data:
            self.populate_data()

    def load_categories(self):
        categories = self.categories_api.get_categories()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)

    def populate_data(self):
        self.sku_input.setText(self.product_data.sku)
        self.name_input.setText(self.product_data.name)
        self.price_input.setValue(self.product_data.price)
        self.description_input.setText(self.product_data.description or "")
        if self.product_data.category:
            index = self.category_combo.findData(self.product_data.category.id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def accept(self):
        sku = self.sku_input.text()
        name = self.name_input.text()
        category_id = self.category_combo.currentData()
        price = self.price_input.value()
        description = self.description_input.text()

        try:
            if self.product_data:
                product_update = ProductUpdate(
                    sku=sku,
                    name=name,
                    category_id=category_id,
                    price=price,
                    description=description
                )
                self.products_api.update_product(self.product_data.id, product_update)
                QMessageBox.information(self, "Success", f"Product {self.product_data.id} updated successfully.")
            else:
                product_create = ProductCreate(
                    sku=sku,
                    name=name,
                    category_id=category_id,
                    price=price,
                    description=description
                )
                new_product = self.products_api.create_product(product_create)
                QMessageBox.information(self, "Success", f"Product {new_product.id} created successfully.")

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class ProductDetailsDialog(QDialog):
    def __init__(self, product: ProductWithCategoryAndInventory, locations_api: LocationsAPI, parent=None):
        super().__init__(parent)
        self.product = product
        self.locations_api = locations_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Product Details - {self.product.name}")
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

        for row, item in enumerate(self.product.inventory_items):
            location = self.locations_api.get_location(item.location_id)
            location_name = location.name if location else f"Unknown (ID: {item.location_id})"

            inventory_table.setItem(row, 0, QTableWidgetItem(location_name))
            inventory_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            inventory_table.setItem(row, 2, QTableWidgetItem(
                datetime.fromtimestamp(item.last_updated).strftime("%Y-%m-%d %H:%M:%S")))

        inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(inventory_table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
