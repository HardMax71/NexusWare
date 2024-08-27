from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QStackedWidget, QMessageBox, QComboBox,
                               QMainWindow)

from desktop_app.src.ui import BarcodeDesignerWidget
from desktop_app.src.ui.components import StyledButton
from public_api.api import ProductsAPI, APIClient, ProductCategoriesAPI, LocationsAPI, UsersAPI
from public_api.shared_schemas.inventory import (ProductWithCategoryAndInventory, ProductFilter)
from .product_details_dialog import ProductDetailsDialog
from .product_dialog import ProductDialog
from ...icon_path_enum import IconPath


class ProductView(QWidget):
    product_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.products_api = ProductsAPI(api_client)
        self.categories_api = ProductCategoriesAPI(api_client)
        self.locations_api = LocationsAPI(api_client)
        self.users_api = UsersAPI(api_client)
        self.permission_manager = self.users_api.get_current_user_permissions()
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

        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
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
        if self.permission_manager.has_write_permission("products"):
            self.fab = StyledButton("+", icon_path=IconPath.PLUS)
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

    def update_table(self, items: list[ProductWithCategoryAndInventory]):
        self.table.setRowCount(len(items))
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
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

            view_button = StyledButton("View", icon_path=IconPath.VIEW)
            view_button.clicked.connect(lambda _, i=item.id: self.view_product(i))
            actions_layout.addWidget(view_button)

            barcode_button = StyledButton("Barcode", icon_path=IconPath.BARCODE)
            barcode_button.clicked.connect(lambda _, i=item: self.generate_barcode(i))
            actions_layout.addWidget(barcode_button)

            if self.permission_manager.has_write_permission("products"):
                edit_button = StyledButton("Edit", icon_path=IconPath.EDIT)
                edit_button.clicked.connect(lambda _, i=item.id: self.edit_product(i))
                actions_layout.addWidget(edit_button)

            if self.permission_manager.has_delete_permission("products"):
                delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
                delete_button.clicked.connect(lambda _, i=item.id: self.delete_product(i))
                actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 5, actions_widget)

    def generate_barcode(self, product: ProductWithCategoryAndInventory):
        barcode_window = QMainWindow(self)
        barcode_window.setWindowTitle(f"Barcode Designer - {product.name}")

        product_data = {
            "sku": product.sku,
            "name": product.name,
            "price": product.price
        }

        barcode_widget = BarcodeDesignerWidget(self.api_client, product_data)
        barcode_window.setCentralWidget(barcode_widget)

        default_type_index = barcode_widget.barcode_type.findText("Code 128")
        if default_type_index >= 0:
            barcode_widget.barcode_type.setCurrentIndex(default_type_index)

        barcode_widget.generate_barcode()

        barcode_window.resize(400, 350)
        barcode_window.show()

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
