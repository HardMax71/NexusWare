from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QMessageBox, QStackedWidget)

from desktop_app.src.ui.components import StyledButton
from public_api.api import SuppliersAPI, APIClient, UsersAPI
from public_api.shared_schemas import Supplier
from .supplier_details_dialog import SupplierDetailsDialog
from .supplier_dialog import SupplierDialog
from ...icon_path_enum import IconPath


class SupplierView(QWidget):
    supplier_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.suppliers_api = SuppliersAPI(api_client)
        self.users_api = UsersAPI(api_client)
        self.permission_manager = self.users_api.get_current_user_permissions()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main Supplier View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search suppliers...")
        self.search_input.textChanged.connect(self.filter_suppliers)
        controls_layout.addWidget(self.search_input)

        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
        self.refresh_button.clicked.connect(self.refresh_suppliers)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(6)
        self.suppliers_table.setHorizontalHeaderLabels(["Name", "Contact", "Email", "Phone", "Address", "Actions"])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.suppliers_table)

        self.stacked_widget.addWidget(main_widget)

        # Floating Action Button for adding new suppliers
        if self.permission_manager.has_write_permission("suppliers"):
            self.fab = StyledButton("+", icon_path=IconPath.PLUS)
            self.fab.clicked.connect(self.add_supplier)
            layout.addWidget(self.fab)

        self.refresh_suppliers()

    def refresh_suppliers(self):
        suppliers = self.suppliers_api.get_suppliers()
        self.update_table(suppliers)

    def update_table(self, suppliers: list[Supplier]):
        self.suppliers_table.setRowCount(len(suppliers))
        self.suppliers_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(supplier.name))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier.contact_person or ""))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.email or ""))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier.phone or ""))
            self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier.address or ""))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View", icon_path=IconPath.VIEW)
            view_button.clicked.connect(lambda _, s=supplier: self.view_supplier(s))
            actions_layout.addWidget(view_button)

            if self.permission_manager.has_write_permission("suppliers"):
                edit_button = StyledButton("Edit", icon_path=IconPath.EDIT)
                edit_button.clicked.connect(lambda _, s=supplier: self.edit_supplier(s))
                actions_layout.addWidget(edit_button)

            if self.permission_manager.has_delete_permission("suppliers"):
                delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
                delete_button.clicked.connect(lambda _, s=supplier: self.delete_supplier(s))
                actions_layout.addWidget(delete_button)

            self.suppliers_table.setCellWidget(row, 5, actions_widget)

    def filter_suppliers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.suppliers_table.rowCount()):
            row_match = False
            for col in range(self.suppliers_table.columnCount() - 1):  # Exclude the Actions column
                item = self.suppliers_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.suppliers_table.setRowHidden(row, not row_match)

    def add_supplier(self):
        dialog = SupplierDialog(self.suppliers_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_suppliers()
            self.supplier_updated.emit()

    def view_supplier(self, supplier: Supplier):
        dialog = SupplierDetailsDialog(supplier, parent=self)
        dialog.exec_()

    def edit_supplier(self, supplier: Supplier):
        dialog = SupplierDialog(self.suppliers_api, supplier_data=supplier, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_suppliers()
            self.supplier_updated.emit()

    def delete_supplier(self, supplier: Supplier):
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete supplier {supplier.name}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.suppliers_api.delete_supplier(supplier.id)
                self.refresh_suppliers()
                self.supplier_updated.emit()
                QMessageBox.information(self, "Success", f"Supplier {supplier.name} deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete supplier: {str(e)}")
