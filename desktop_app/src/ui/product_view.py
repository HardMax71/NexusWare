from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem

from desktop_app.src.ui.components import StyledButton
from public_api.api import ProductsAPI, APIClient


class ProductView(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.products_api = ProductsAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_products)
        self.add_product_button = StyledButton("Add Product")
        self.add_product_button.clicked.connect(self.add_product)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.add_product_button)
        layout.addLayout(controls_layout)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["SKU", "Name", "Category", "Price", "Total Stock", "Actions"])
        layout.addWidget(self.products_table)

        self.refresh_products()

    def refresh_products(self):
        products = self.products_api.get_products()
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(product.sku))
            self.products_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.products_table.setItem(row, 2, QTableWidgetItem(product.category.name))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"${product.price:.2f}"))

            # Calculate total stock across all inventory items
            total_stock = sum(item.quantity for item in product.inventory_items)
            self.products_table.setItem(row, 4, QTableWidgetItem(str(total_stock)))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, pid=product.id: self.edit_product(pid))
            actions_layout.addWidget(edit_button)
            self.products_table.setCellWidget(row, 5, actions_widget)

    def add_product(self):
        # Implement add product dialog
        pass

    def edit_product(self, product_id):
        # Implement edit product dialog
        pass
