from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QDialog, QComboBox,
                               QFormLayout, QDateEdit, QDoubleSpinBox, QSpinBox, QDialogButtonBox, QLabel, QGroupBox,
                               QLineEdit, QMessageBox)

from desktop_app.src.ui.components import StyledButton
from public_api.api import OrdersAPI, CustomersAPI, ProductsAPI, ShipmentsAPI, CarriersAPI
from public_api.shared_schemas import (OrderWithDetails, OrderCreate, OrderUpdate, OrderItemCreate, ShippingInfo,
                                       OrderItemUpdate)
from public_api.shared_schemas.order import OrderStatus


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
        layout = QVBoxLayout(self)

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

        layout.addLayout(form_layout)

        # Order Items
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Actions"])
        layout.addWidget(self.items_table)

        add_item_button = StyledButton("Add Item")
        add_item_button.clicked.connect(self.add_item)
        layout.addWidget(add_item_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

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

        delete_button = StyledButton("Delete")
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
        customer = self.customers_api.get_customers()[self.customer_combo.currentIndex()]
        status = self.status_combo.currentText()
        order_date = int(self.order_date.dateTime().toPython().timestamp())
        total_amount = self.total_amount.value()

        items = []
        for row in range(self.items_table.rowCount()):
            product = self.products_api.get_products()[self.items_table.cellWidget(row, 0).currentIndex()]
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


class OrderDetailsDialog(QDialog):
    def __init__(self, order: OrderWithDetails, parent=None):
        super().__init__(parent)
        self.order = order
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Order Details - #{self.order.id}")
        layout = QVBoxLayout(self)

        info_layout = QFormLayout()
        info_layout.addRow("Order ID:", QLabel(str(self.order.id)))
        info_layout.addRow("Customer:", QLabel(self.order.customer.name))
        info_layout.addRow("Status:", QLabel(self.order.status))
        info_layout.addRow("Order Date:", QLabel(datetime.fromtimestamp(self.order.order_date).strftime("%Y-%m-%d")))
        info_layout.addRow("Total Amount:", QLabel(f"${self.order.total_amount:.2f}"))

        layout.addLayout(info_layout)

        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Total"])
        items_table.setRowCount(len(self.order.order_items))

        for row, item in enumerate(self.order.order_items):
            items_table.setItem(row, 0, QTableWidgetItem(item.product.name))
            items_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            items_table.setItem(row, 2, QTableWidgetItem(f"${item.unit_price:.2f}"))
            items_table.setItem(row, 3, QTableWidgetItem(f"${item.quantity * item.unit_price:.2f}"))

        items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Total"])
        items_table.setRowCount(len(self.order.order_items))

        layout.addWidget(items_table)

        if self.order.shipping_address_line1:
            shipping_group = QGroupBox("Shipping Information")
            shipping_layout = QFormLayout()
            shipping_layout.addRow("Name:", QLabel(self.order.shipping_name))
            shipping_layout.addRow("Address:", QLabel(self.order.shipping_address_line1))
            shipping_layout.addRow("City:", QLabel(self.order.shipping_city))
            shipping_layout.addRow("State:", QLabel(self.order.shipping_state))
            shipping_layout.addRow("Postal Code:", QLabel(self.order.shipping_postal_code))
            shipping_layout.addRow("Country:", QLabel(self.order.shipping_country))
            shipping_layout.addRow("Phone:", QLabel(self.order.shipping_phone))
            shipping_group.setLayout(shipping_layout)
            layout.addWidget(shipping_group)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.adjustSize()


class ShippingDialog(QDialog):
    def __init__(self, shipments_api: ShipmentsAPI, carriers_api: CarriersAPI, parent=None):
        super().__init__(parent)
        self.shipments_api = shipments_api
        self.carriers_api = carriers_api
        self.carriers = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ship Order")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.carrier_combo = QComboBox()
        self.load_carriers()
        form_layout.addRow("Carrier:", self.carrier_combo)

        self.tracking_input = QLineEdit()
        form_layout.addRow("Tracking Number:", self.tracking_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_carriers(self):
        try:
            self.carriers = self.carriers_api.get_carriers()
            self.carrier_combo.clear()
            self.carrier_combo.addItems([carrier.name for carrier in self.carriers])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load carriers: {str(e)}")

    def get_shipping_info(self) -> ShippingInfo:
        selected_carrier = self.carriers[self.carrier_combo.currentIndex()]
        return ShippingInfo(
            carrier=selected_carrier.name,
            carrier_id=selected_carrier.id,
            tracking_number=self.tracking_input.text()
        )
