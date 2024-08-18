from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QStackedWidget, QMessageBox)

from desktop_app.src.ui.components import StyledButton, AdjustmentDialog, InventoryDialog
from public_api.api import InventoryAPI, APIClient, LocationsAPI, ProductsAPI, UsersAPI
from public_api.shared_schemas import InventoryWithDetails, Inventory
from .inventory_planning import InventoryPlanningWidget


class InventoryView(QWidget):
    inventory_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.inventory_api = InventoryAPI(api_client)
        self.locations_api = LocationsAPI(api_client)
        self.products_api = ProductsAPI(api_client)
        self.users_api = UsersAPI(api_client)
        self.permission_manager = self.users_api.get_current_user_permissions()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content and planning
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main Inventory View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search inventory...")
        self.search_input.textChanged.connect(self.filter_inventory)
        controls_layout.addWidget(self.search_input)

        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_inventory)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["SKU", "Name", "Quantity", "Location", "Last Updated", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)

        self.stacked_widget.addWidget(main_widget)

        # Inventory Planning Widget
        self.planning_widget = InventoryPlanningWidget(self.api_client)
        self.stacked_widget.addWidget(self.planning_widget)

        # Floating Action Button for adding new items
        if self.permission_manager.has_write_permission("inventory"):
            self.fab = StyledButton("+")
            self.fab.clicked.connect(self.add_item)
            layout.addWidget(self.fab)

        # Planning toggle button
        self.planning_button = StyledButton("Inventory Planning")
        self.planning_button.clicked.connect(self.toggle_planning_view)
        layout.addWidget(self.planning_button)

        self.refresh_inventory()

    def refresh_inventory(self):
        inventory_data = self.inventory_api.get_inventory()
        self.update_table(inventory_data.items)

    def update_table(self, items: list[InventoryWithDetails]):
        self.table.setRowCount(len(items))
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item.product.sku))
            self.table.setItem(row, 1, QTableWidgetItem(item.product.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            self.table.setItem(row, 3, QTableWidgetItem(item.location.name))
            self.table.setItem(row, 4,
                               QTableWidgetItem(
                                   datetime.fromtimestamp(item.last_updated).strftime("%Y-%m-%d %H:%M:%S")))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            if self.permission_manager.has_write_permission("inventory"):
                edit_button = StyledButton("Edit")
                edit_button.clicked.connect(lambda _, i=item.id: self.edit_item(i))
                actions_layout.addWidget(edit_button)

                adjust_button = StyledButton("Adjust")
                adjust_button.clicked.connect(lambda _, i=item.id: self.adjust_item(i))
                actions_layout.addWidget(adjust_button)

            if self.permission_manager.has_delete_permission("inventory"):
                delete_button = StyledButton("Delete")
                delete_button.clicked.connect(lambda _, i=item.id: self.delete_item(i))
                actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 5, actions_widget)

    def filter_inventory(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            row_match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.table.setRowHidden(row, not row_match)

    def add_item(self):
        dialog = InventoryDialog(self.inventory_api, locations_api=self.locations_api, products_api=self.products_api,
                                 parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_inventory()
            self.inventory_updated.emit()

    def edit_item(self, id):
        item_data: Inventory = self.inventory_api.get_inventory_item(id)
        dialog = InventoryDialog(self.inventory_api, self.locations_api, self.products_api, item_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_inventory()
            self.inventory_updated.emit()

    def adjust_item(self, id):
        dialog = AdjustmentDialog(self.inventory_api, id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_inventory()
            self.inventory_updated.emit()

    def delete_item(self, id):
        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete this item?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.inventory_api.delete_inventory_item(id)
                self.refresh_inventory()
                self.inventory_updated.emit()
                QMessageBox.information(self, "Success", "Item deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

    def toggle_planning_view(self):
        current_index = self.stacked_widget.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.stacked_widget.setCurrentIndex(new_index)
        self.planning_button.setText("Inventory List" if new_index == 1 else "Inventory Planning")