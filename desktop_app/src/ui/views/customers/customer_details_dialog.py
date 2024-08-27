from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QDialogButtonBox,
                               QMessageBox, QLabel)

from public_api.api import CustomersAPI
from public_api.shared_schemas import Customer


class CustomerDetailsDialog(QDialog):
    def __init__(self, customer: Customer, customers_api: CustomersAPI, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.customers_api = customers_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Customer Details - {self.customer.name}")
        self.setMinimumSize(550, 400)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.addRow("Name:", QLabel(self.customer.name))
        form_layout.addRow("Email:", QLabel(self.customer.email or "N/A"))
        form_layout.addRow("Phone:", QLabel(self.customer.phone or "N/A"))
        form_layout.addRow("Address:", QLabel(self.customer.address or "N/A"))

        layout.addLayout(form_layout)

        # Customer Orders
        orders_table = QTableWidget()
        orders_table.setColumnCount(4)
        orders_table.setHorizontalHeaderLabels(["Order ID", "Date", "Total Amount", "Status"])
        header = orders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        # header.setSectionResizeMode(0, QHeaderView.Stretch)

        try:
            orders = self.customers_api.get_customer_orders(self.customer.id)
            orders_table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                orders_table.setItem(row, 0, QTableWidgetItem(str(order.id)))
                orders_table.setItem(row, 1,
                                     QTableWidgetItem(datetime.fromtimestamp(order.order_date).strftime("%Y-%m-%d")))
                orders_table.setItem(row, 2, QTableWidgetItem(f"${order.total_amount:.2f}"))
                orders_table.setItem(row, 3, QTableWidgetItem(order.status))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load customer orders: {str(e)}")

        layout.addWidget(QLabel("Customer Orders:"))
        layout.addWidget(orders_table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
