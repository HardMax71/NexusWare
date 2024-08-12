from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem

from desktop_app.src.api import CustomersAPI
from desktop_app.src.ui.components import StyledButton


class CustomerView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.customers_api = CustomersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_customers)
        self.add_customer_button = StyledButton("Add Customer")
        self.add_customer_button.clicked.connect(self.add_customer)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.add_customer_button)
        layout.addLayout(controls_layout)

        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Address", "Actions"])
        layout.addWidget(self.customers_table)

        self.refresh_customers()

    def refresh_customers(self):
        customers = self.customers_api.get_customers()
        self.customers_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer['name']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer['email']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer['phone']))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer['address']))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, cid=customer['customer_id']: self.edit_customer(cid))
            actions_layout.addWidget(edit_button)
            self.customers_table.setCellWidget(row, 4, actions_widget)

    def add_customer(self):
        # Implement add customer dialog
        pass

    def edit_customer(self, customer_id):
        # Implement edit customer dialog
        pass
