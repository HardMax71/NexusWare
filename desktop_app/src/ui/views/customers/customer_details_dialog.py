from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QDialogButtonBox,
                               QMessageBox, QLabel, QWidget, QGroupBox)

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
        self.setMinimumSize(800, 400)
        main_layout = QHBoxLayout(self)

        # Left side - Customer Info and OK button
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Create a group box for customer data
        customer_group = QGroupBox("Customer Data")
        form_layout = QFormLayout(customer_group)
        form_layout.addRow("Name:", QLabel(self.customer.name))
        form_layout.addRow("Email:", QLabel(self.customer.email or "N/A"))
        form_layout.addRow("Phone:", QLabel(self.customer.phone or "N/A"))

        address_label = QLabel(self.customer.address or "N/A")
        address_label.setWordWrap(True)
        form_layout.addRow("Address:", address_label)

        left_layout.addWidget(customer_group)
        left_layout.addStretch(1)

        # OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        left_layout.addWidget(button_box)

        # Right side - Customer Orders Table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        orders_table = QTableWidget()
        orders_table.setColumnCount(4)
        orders_table.setHorizontalHeaderLabels(["Order ID", "Date", "Total Amount", "Status"])
        header = orders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

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

        right_layout.addWidget(QLabel("Customer Orders:"))
        right_layout.addWidget(orders_table)

        # Add left and right widgets to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # Set layout proportions
        main_layout.setStretch(0, 1)  # Left side
        main_layout.setStretch(1, 2)  # Right side