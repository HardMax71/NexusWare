from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                               QMessageBox, QLabel, QStackedWidget)

from desktop_app.src.ui.components import StyledButton
from public_api.api import CustomersAPI, APIClient, UsersAPI
from public_api.shared_schemas import Customer, CustomerCreate, CustomerUpdate


class CustomerView(QWidget):
    customer_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.customers_api = CustomersAPI(api_client)
        self.users_api = UsersAPI(api_client)
        self.permission_manager = self.users_api.get_current_user_permissions()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main Customer View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        self.search_input.textChanged.connect(self.filter_customers)
        controls_layout.addWidget(self.search_input)

        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_customers)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Address", "Actions"])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.customers_table)

        self.stacked_widget.addWidget(main_widget)

        # Floating Action Button for adding new customers
        if self.permission_manager.has_write_permission("customers"):
            self.fab = StyledButton("+")
            self.fab.clicked.connect(self.add_customer)
            layout.addWidget(self.fab)

        self.refresh_customers()

    def refresh_customers(self):
        customers = self.customers_api.get_customers()
        self.update_table(customers)

    def update_table(self, customers: list[Customer]):
        self.customers_table.setRowCount(len(customers))
        self.customers_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer.name))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer.email or ""))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer.phone or ""))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer.address or ""))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View")
            view_button.clicked.connect(lambda _, c=customer: self.view_customer(c))
            actions_layout.addWidget(view_button)

            if self.permission_manager.has_write_permission("customers"):
                edit_button = StyledButton("Edit")
                edit_button.clicked.connect(lambda _, c=customer: self.edit_customer(c))
                actions_layout.addWidget(edit_button)

            if self.permission_manager.has_delete_permission("customers"):
                delete_button = StyledButton("Delete")
                delete_button.clicked.connect(lambda _, c=customer: self.delete_customer(c))
                actions_layout.addWidget(delete_button)

            self.customers_table.setCellWidget(row, 4, actions_widget)

    def filter_customers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.customers_table.rowCount()):
            row_match = False
            for col in range(self.customers_table.columnCount() - 1):  # Exclude the Actions column
                item = self.customers_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.customers_table.setRowHidden(row, not row_match)

    def add_customer(self):
        dialog = CustomerDialog(self.customers_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_customers()
            self.customer_updated.emit()

    def view_customer(self, customer: Customer):
        dialog = CustomerDetailsDialog(customer, self.customers_api, parent=self)
        dialog.exec_()

    def edit_customer(self, customer: Customer):
        dialog = CustomerDialog(self.customers_api, customer_data=customer, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_customers()
            self.customer_updated.emit()

    def delete_customer(self, customer: Customer):
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete customer {customer.name}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.customers_api.delete_customer(customer.id)
                self.refresh_customers()
                self.customer_updated.emit()
                QMessageBox.information(self, "Success", f"Customer {customer.name} deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customer: {str(e)}")


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
