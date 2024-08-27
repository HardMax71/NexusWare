from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QMessageBox, QComboBox,
                               QFormLayout, QDoubleSpinBox, QDialogButtonBox, QTextEdit)

from public_api.api import ProductsAPI, ProductCategoriesAPI
from public_api.shared_schemas import (ProductWithCategoryAndInventory, ProductCreate,
                                       ProductUpdate)


class ProductDialog(QDialog):
    def __init__(self, products_api: ProductsAPI, categories_api: ProductCategoriesAPI,
                 product_data: ProductWithCategoryAndInventory | None = None, parent=None):
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

        self.description_input = QTextEdit()
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
