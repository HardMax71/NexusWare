from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem

from desktop_app.src.api import InventoryAPI
from desktop_app.src.ui.components import StyledButton


class InventoryView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.inventory_api = InventoryAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = StyledButton("Add Item")
        self.add_button.clicked.connect(self.add_item)
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_inventory)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["SKU", "Name", "Quantity", "Location", "Last Updated"])
        layout.addWidget(self.table)

        self.refresh_inventory()

    def refresh_inventory(self):
        inventory_data = self.inventory_api.get_inventory()
        self.table.setRowCount(len(inventory_data['items']))
        for row, item in enumerate(inventory_data['items']):
            self.table.setItem(row, 0, QTableWidgetItem(item['product']['sku']))
            self.table.setItem(row, 1, QTableWidgetItem(item['product']['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(row, 3, QTableWidgetItem(item['location']['name']))
            self.table.setItem(row, 4, QTableWidgetItem(str(item['last_updated'])))

            actions_layout = QHBoxLayout()
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, i=item['inventory_id']: self.edit_item(i))
            adjust_button = StyledButton("Adjust")
            adjust_button.clicked.connect(lambda _, i=item['inventory_id']: self.adjust_item(i))
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(adjust_button)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 5, actions_widget)

    def add_item(self):
        # Implement add item dialog
        pass

    def edit_item(self, inventory_id):
        # Implement edit item dialog
        pass

    def adjust_item(self, inventory_id):
        # Implement adjust item dialog
        pass
