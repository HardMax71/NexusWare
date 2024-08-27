from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QDialog, QFormLayout, QDialogButtonBox, QLabel, QGroupBox,
                               QHeaderView, QHBoxLayout, QWidget)

from public_api.shared_schemas import OrderWithDetails


class OrderDetailsDialog(QDialog):
    def __init__(self, order: OrderWithDetails, parent=None):
        super().__init__(parent)
        self.order = order
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Order Details - #{self.order.id}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        main_layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Order Information
        info_group = QGroupBox("Order Information")
        info_layout = QFormLayout()
        info_layout.addRow("Order ID:", QLabel(str(self.order.id)))
        info_layout.addRow("Customer:", QLabel(self.order.customer.name))
        info_layout.addRow("Status:", QLabel(self.order.status))
        info_layout.addRow("Order Date:", QLabel(datetime.fromtimestamp(self.order.order_date).strftime("%Y-%m-%d")))
        info_layout.addRow("Total Amount:", QLabel(f"${self.order.total_amount:.2f}"))
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)

        # Shipping Information
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
            left_layout.addWidget(shipping_group)

        left_layout.addStretch(1)  # Add stretch to push groups to the top
        content_layout.addWidget(left_widget)

        # Right side: Order Items Table
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Total"])
        items_table.setRowCount(len(self.order.order_items))

        for row, item in enumerate(self.order.order_items):
            items_table.setItem(row, 0, QTableWidgetItem(item.product.name))
            items_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            items_table.setItem(row, 2, QTableWidgetItem(f"${item.unit_price:.2f}"))
            items_table.setItem(row, 3, QTableWidgetItem(f"${item.quantity * item.unit_price:.2f}"))

        # Set column widths
        header = items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        items_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        items_layout.addWidget(items_table)
        items_group.setLayout(items_layout)
        content_layout.addWidget(items_group, 1)  # Give the table more stretch

        main_layout.addLayout(content_layout)

        # OK button at the bottom
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)

        self.adjustSize()
