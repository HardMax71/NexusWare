from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem

from desktop_app.src.api import APIClient
from desktop_app.src.ui.components import StyledButton


# TODO: Fix api search call (now nonexistent)

class SearchFilterWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search controls
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term")
        self.search_type = QComboBox()
        self.search_type.addItems(["Products", "Orders", "Customers"])
        self.search_button = StyledButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Results table
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)

    def perform_search(self):
        search_term = self.search_input.text()
        search_type = self.search_type.currentText()

        results = self.api_client.search(search_type, search_term)
        self.display_results(results)

    def display_results(self, results):
        self.results_table.clear()
        if not results:
            return

        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(results[0]))
        self.results_table.setHorizontalHeaderLabels(results[0].keys())

        for row, item in enumerate(results):
            for col, (key, value) in enumerate(item.items()):
                self.results_table.setItem(row, col, QTableWidgetItem(str(value)))

        self.results_table.resizeColumnsToContents()
