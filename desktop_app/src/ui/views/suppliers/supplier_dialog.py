from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                               QMessageBox)

from public_api.api import SuppliersAPI
from public_api.shared_schemas import Supplier, SupplierCreate, SupplierUpdate


class SupplierDialog(QDialog):
    def __init__(self, suppliers_api: SuppliersAPI, supplier_data: Supplier | None = None, parent=None):
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
