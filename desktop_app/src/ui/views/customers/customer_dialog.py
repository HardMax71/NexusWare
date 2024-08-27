from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                               QMessageBox)

from public_api.api import CustomersAPI
from public_api.shared_schemas import Customer, CustomerCreate, CustomerUpdate


class CustomerDialog(QDialog):
    def __init__(self, customers_api: CustomersAPI, customer_data: Customer | None = None, parent=None):
        super().__init__(parent)
        self.customers_api = customers_api
        self.customer_data = customer_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Customer" if not self.customer_data else "Edit Customer")
        self.setMinimumSize(300, 200)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

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

        if self.customer_data:
            self.populate_data()

    def populate_data(self):
        self.name_input.setText(self.customer_data.name)
        self.email_input.setText(self.customer_data.email or "")
        self.phone_input.setText(self.customer_data.phone or "")
        self.address_input.setText(self.customer_data.address or "")

    def accept(self):
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()

        try:
            if self.customer_data:
                customer_update = CustomerUpdate(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                self.customers_api.update_customer(self.customer_data.id, customer_update)
                QMessageBox.information(self, "Success", f"Customer {name} updated successfully.")
            else:
                customer_create = CustomerCreate(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                new_customer = self.customers_api.create_customer(customer_create)
                QMessageBox.information(self, "Success", f"Customer {new_customer.name} created successfully.")

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
