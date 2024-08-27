from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QDialog, QComboBox,
                               QFormLayout, QDateEdit, QDoubleSpinBox, QSpinBox, QDialogButtonBox, QGroupBox,
                               QMessageBox, QHeaderView, QHBoxLayout, QWidget)

from desktop_app.src.ui.components import StyledButton
from desktop_app.src.ui.icon_path_enum import IconPath
from public_api.api import OrdersAPI, CustomersAPI, ProductsAPI
from public_api.shared_schemas import (OrderWithDetails, OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate,
                                       OrderStatus)


class OrderDialog(QDialog):
    def __init__(self, orders_api: OrdersAPI, customers_api: CustomersAPI, products_api: ProductsAPI,
                 order_data: OrderWithDetails | None = None, parent=None):
        super().__init__(parent)
        self.orders_api = orders_api
        self.customers_api = customers_api
        self.products_api = products_api
        self.order_data = order_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Order" if not self.order_data else "Edit Order")
        self.setMinimumWidth(850)
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Left side: Order Information
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        info_group = QGroupBox("Order Information")
        form_layout = QFormLayout()

        self.customer_combo = QComboBox()
        self.load_customers()
        form_layout.addRow("Customer:", self.customer_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems([status.value for status in OrderStatus])
        form_layout.addRow("Status:", self.status_combo)

        self.order_date = QDateEdit()
        self.order_date.setCalendarPopup(True)
        self.order_date.setDate(datetime.now().date())
        form_layout.addRow("Order Date:", self.order_date)

        self.total_amount = QDoubleSpinBox()
        self.total_amount.setMaximum(1000000)
        self.total_amount.setPrefix("$")
        form_layout.addRow("Total Amount:", self.total_amount)

        info_group.setLayout(form_layout)
        left_layout.addWidget(info_group)
        left_layout.addStretch(1)
        content_layout.addWidget(left_widget)

        # Right side: Order Items Table
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Actions"])

        # Set column widths
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Stretch the product column
        items_layout.addWidget(self.items_table)

        add_item_button = StyledButton("Add Item", icon_path=IconPath.PLUS)
        add_item_button.clicked.connect(self.add_item)
        items_layout.addWidget(add_item_button)

        items_group.setLayout(items_layout)
        content_layout.addWidget(items_group, 1)  # Give the table more stretch

        main_layout.addLayout(content_layout)

        # OK and Cancel buttons at the bottom
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        if self.order_data:
            self.populate_data()

    def load_customers(self):
        customers = self.customers_api.get_customers()
        self.customer_combo.addItems([c.name for c in customers])

    def populate_data(self):
        self.customer_combo.setCurrentText(self.order_data.customer.name)
        self.status_combo.setCurrentText(self.order_data.status)
        self.order_date.setDate(datetime.fromtimestamp(self.order_data.order_date).date())
        self.total_amount.setValue(self.order_data.total_amount)

        for item in self.order_data.order_items:
            self.add_item(item)

    def add_item(self, item_data=None):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        product_combo = QComboBox()
        products = self.products_api.get_products()
        product_combo.addItems([p.name for p in products])

        quantity_spin = QSpinBox()
        quantity_spin.setMinimum(1)
        quantity_spin.setMaximum(1000)

        price_spin = QDoubleSpinBox()
        price_spin.setMaximum(100000)
        price_spin.setPrefix("$")

        delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
        delete_button.clicked.connect(lambda: self.delete_item(row))

        self.items_table.setCellWidget(row, 0, product_combo)
        self.items_table.setCellWidget(row, 1, quantity_spin)
        self.items_table.setCellWidget(row, 2, price_spin)
        self.items_table.setCellWidget(row, 3, delete_button)

        if item_data:
            product_combo.setCurrentText(item_data.product.name)
            quantity_spin.setValue(item_data.quantity)
            price_spin.setValue(item_data.unit_price)

    def delete_item(self, row):
        self.items_table.removeRow(row)

    def accept(self):
        if self.items_table.rowCount() == 0:
            QMessageBox.critical(self, "Error",
                                 "Cannot create an order without any items. Please add at least one item.")
            return

        customer = self.customers_api.get_customers()[self.customer_combo.currentIndex()]
        status = self.status_combo.currentText()
        order_date = int(self.order_date.dateTime().toPython().timestamp())
        total_amount = self.total_amount.value()

        items = []
        all_products = self.products_api.get_products()
        for row in range(self.items_table.rowCount()):
            product_combo: QComboBox = self.items_table.cellWidget(row, 0)
            product = all_products[product_combo.currentIndex()]
            quantity = self.items_table.cellWidget(row, 1).value()
            unit_price = self.items_table.cellWidget(row, 2).value()

            if self.order_data:
                items.append(OrderItemUpdate(
                    id=self.order_data.order_items[row].id if row < len(self.order_data.order_items) else None,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price
                ))
            else:
                items.append(OrderItemCreate(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price
                ))

        try:
            if self.order_data:
                order_update = OrderUpdate(
                    customer_id=customer.id,
                    status=status,
                    total_amount=total_amount,
                    items=items
                )
                self.orders_api.update_order(self.order_data.id, order_update)
                QMessageBox.information(self, "Success", f"Order {self.order_data.id} updated successfully.")
            else:
                order_create = OrderCreate(
                    customer_id=customer.id,
                    status=status,
                    order_date=order_date,
                    total_amount=total_amount,
                    items=items
                )
                new_order = self.orders_api.create_order(order_create)
                QMessageBox.information(self, "Success", f"Order {new_order.id} created successfully.")

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
