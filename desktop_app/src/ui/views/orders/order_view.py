from datetime import datetime
from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QStackedWidget, QMessageBox, QComboBox)

from desktop_app.src.ui.components import StyledButton
from public_api.api import OrdersAPI, APIClient, CustomersAPI, ProductsAPI, ShipmentsAPI, CarriersAPI, UsersAPI
from public_api.shared_schemas import OrderWithDetails, OrderFilter, OrderStatus
from .order_details_dialog import OrderDetailsDialog
from .order_dialog import OrderDialog
from .shipping_dialog import ShippingDialog
from ...icon_path_enum import IconPath


class OrderView(QWidget):
    order_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.orders_api = OrdersAPI(api_client)
        self.customers_api = CustomersAPI(api_client)
        self.products_api = ProductsAPI(api_client)
        self.shipments_api = ShipmentsAPI(api_client)
        self.carriers_api = CarriersAPI(api_client)
        self.users_api = UsersAPI(api_client)
        self.permission_manager = self.users_api.get_current_user_permissions()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content and order details
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main Order View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search orders...")
        self.search_input.textChanged.connect(self.filter_orders)
        controls_layout.addWidget(self.search_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["All"] + [status.value for status in OrderStatus])
        self.status_combo.currentTextChanged.connect(self.refresh_orders)
        controls_layout.addWidget(self.status_combo)

        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
        self.refresh_button.clicked.connect(self.refresh_orders)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Customer", "Date", "Total", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)

        self.stacked_widget.addWidget(main_widget)

        # Floating Action Button for adding new orders
        if self.permission_manager.has_write_permission("orders"):
            self.fab = StyledButton("+", icon_path=IconPath.PLUS)
            self.fab.clicked.connect(self.create_new_order)
            layout.addWidget(self.fab)

        self.refresh_orders()

    def refresh_orders(self):
        status_filter = self.status_combo.currentText()
        if status_filter == "All":
            status_filter = None
        else:
            status_filter = OrderStatus(status_filter)

        filter = OrderFilter(status=status_filter)
        orders = self.orders_api.get_orders(filter_params=filter)
        self.update_table(orders)

    def update_table(self, items: List[OrderWithDetails]):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item.customer.name))
            self.table.setItem(row, 1, QTableWidgetItem(datetime.fromtimestamp(item.order_date).strftime("%Y-%m-%d")))
            self.table.setItem(row, 2, QTableWidgetItem(f"${item.total_amount:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(item.status.value))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View", icon_path=IconPath.VIEW)
            view_button.clicked.connect(lambda _, i=item.id: self.view_order(i))
            actions_layout.addWidget(view_button)

            if self.permission_manager.has_write_permission("orders"):
                edit_button = StyledButton("Edit", icon_path=IconPath.EDIT)
                edit_button.clicked.connect(lambda _, i=item.id: self.edit_order(i))
                actions_layout.addWidget(edit_button)

                ship_button = StyledButton("Ship", icon_path=IconPath.SHIP)
                ship_button.clicked.connect(lambda _, i=item.id: self.ship_order(i))
                actions_layout.addWidget(ship_button)

                # Disable Ship button for "Shipped" or "Delivered" orders
                if item.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                    ship_button.setEnabled(False)
                    ship_button.setToolTip("Order already shipped")

            if self.permission_manager.has_delete_permission("orders"):
                delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
                delete_button.clicked.connect(lambda _, i=item.id: self.delete_order(i))
                actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 4, actions_widget)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_orders(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            row_match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.table.setRowHidden(row, not row_match)

    def create_new_order(self):
        dialog = OrderDialog(self.orders_api, self.customers_api, self.products_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_orders()
            self.order_updated.emit()

    def view_order(self, order_id):
        order = self.orders_api.get_order(order_id)
        dialog = OrderDetailsDialog(order, parent=self)
        dialog.exec_()

    def edit_order(self, order_id):
        order = self.orders_api.get_order(order_id)
        dialog = OrderDialog(self.orders_api, self.customers_api, self.products_api, order_data=order, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_orders()
            self.order_updated.emit()

    def ship_order(self, order_id):
        dialog = ShippingDialog(self.shipments_api, self.carriers_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            shipping_info = dialog.get_shipping_info()
            try:
                self.orders_api.ship_order(order_id, shipping_info)
                QMessageBox.information(self, "Success", "Order shipped successfully.")
                self.refresh_orders()
                self.order_updated.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to ship order: {str(e)}")

    def delete_order(self, order_id):
        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete this order?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.orders_api.delete_order(order_id)
                self.refresh_orders()
                self.order_updated.emit()
                QMessageBox.information(self, "Success", "Order deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete order: {str(e)}")
