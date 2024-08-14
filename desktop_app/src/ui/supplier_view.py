from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                               QMessageBox, QLabel, QStackedWidget)

from desktop_app.src.ui.components import StyledButton
from public_api.api import SuppliersAPI, APIClient
from public_api.shared_schemas import Supplier, SupplierCreate, SupplierUpdate


class SupplierView(QWidget):
    supplier_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.suppliers_api = SuppliersAPI(api_client)
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

        self.refresh_button = StyledButton("Refresh")
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
        self.fab = StyledButton("+")
        self.fab.clicked.connect(self.add_supplier)
        layout.addWidget(self.fab)

        self.refresh_suppliers()

    def refresh_suppliers(self):
        suppliers = self.suppliers_api.get_suppliers()
        self.update_table(suppliers)

    def update_table(self, suppliers: List[Supplier]):
        self.suppliers_table.setRowCount(len(suppliers))
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

            view_button = StyledButton("View")
            view_button.clicked.connect(lambda _, s=supplier: self.view_supplier(s))
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, s=supplier: self.edit_supplier(s))
            delete_button = StyledButton("Delete")
            delete_button.clicked.connect(lambda _, s=supplier: self.delete_supplier(s))

            actions_layout.addWidget(view_button)
            actions_layout.addWidget(edit_button)
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


class SupplierDialog(QDialog):
    def __init__(self, suppliers_api: SuppliersAPI, supplier_data: Optional[Supplier] = None, parent=None):
        super().__init__(parent)
        self.suppliers_api = suppliers_api
        self.supplier_data = supplier_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Supplier" if not self.supplier_data else "Edit Supplier")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

        self.contact_person_input = QLineEdit()
        form_layout.addRow("Contact Person:", self.contact_person_input)

        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)

        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)

        self.address_input = QLineEdit()
        form_layout.addRow("Address:", self.address_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.supplier_data:
            self.populate_data()

    def populate_data(self):
        self.name_input.setText(self.supplier_data.name)
        self.contact_person_input.setText(self.supplier_data.contact_person or "")
        self.email_input.setText(self.supplier_data.email or "")
        self.phone_input.setText(self.supplier_data.phone or "")
        self.address_input.setText(self.supplier_data.address or "")

    def accept(self):
        name = self.name_input.text()
        contact_person = self.contact_person_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()

        try:
            if self.supplier_data:
                supplier_update = SupplierUpdate(
                    name=name,
                    contact_person=contact_person,
                    email=email,
                    phone=phone,
                    address=address
                )
                self.suppliers_api.update_supplier(self.supplier_data.id, supplier_update)
                QMessageBox.information(self, "Success", f"Supplier {name} updated successfully.")
            else:
                supplier_create = SupplierCreate(
                    name=name,
                    contact_person=contact_person,
                    email=email,
                    phone=phone,
                    address=address
                )
                new_supplier = self.suppliers_api.create_supplier(supplier_create)
                QMessageBox.information(self, "Success", f"Supplier {new_supplier.name} created successfully.")

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class SupplierDetailsDialog(QDialog):
    def __init__(self, supplier: Supplier, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Supplier Details - {self.supplier.name}")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.addRow("Name:", QLabel(self.supplier.name))
        form_layout.addRow("Contact Person:", QLabel(self.supplier.contact_person or "N/A"))
        form_layout.addRow("Email:", QLabel(self.supplier.email or "N/A"))
        form_layout.addRow("Phone:", QLabel(self.supplier.phone or "N/A"))
        form_layout.addRow("Address:", QLabel(self.supplier.address or "N/A"))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
