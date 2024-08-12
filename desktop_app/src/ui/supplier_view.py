from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem

from desktop_app.src.api import SuppliersAPI
from desktop_app.src.ui.components import StyledButton


# TODO: Implement Supplier functions

class SupplierView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.suppliers_api = SuppliersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_suppliers)
        self.add_supplier_button = StyledButton("Add Supplier")
        self.add_supplier_button.clicked.connect(self.add_supplier)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.add_supplier_button)
        layout.addLayout(controls_layout)

        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(5)
        self.suppliers_table.setHorizontalHeaderLabels(["Name", "Contact", "Email", "Phone", "Actions"])
        layout.addWidget(self.suppliers_table)

        self.refresh_suppliers()

    def refresh_suppliers(self):
        suppliers = self.suppliers_api.get_suppliers()
        self.suppliers_table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(supplier['name']))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier['contact_person']))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier['email']))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier['phone']))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, sid=supplier['supplier_id']: self.edit_supplier(sid))
            actions_layout.addWidget(edit_button)
            self.suppliers_table.setCellWidget(row, 4, actions_widget)

    def add_supplier(self):
        # Implement add supplier dialog
        pass

    def edit_supplier(self, supplier_id):
        # Implement edit supplier dialog
        pass
