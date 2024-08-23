import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit,
                               QComboBox, QTableWidget, QTableWidgetItem,
                               QDialog, QPushButton, QLabel)

from desktop_app.src.ui.components import StyledButton
from public_api.api import APIClient, SearchAPI


class AdvancedSearchDialog(QDialog):
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.search_api = SearchAPI(api_client)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Advanced Search")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Search controls
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term")
        self.search_type = QComboBox()
        self.search_type.addItems(["Products", "Orders"])
        self.search_button = StyledButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Type:"))
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Results table
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)

    def perform_search(self):
        search_term: str = self.search_input.text()
        search_type = self.search_type.currentText()

        if search_type == "Products":
            results = self.search_api.search_products(q=search_term)
        elif search_type == "Orders":
            results = self.search_api.search_orders(q=search_term)
        else:
            results = []

        self.display_results(results)

    def display_results(self, results):
        self.results_table.clear()
        if not results:
            return

        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(results[0].model_dump()))
        self.results_table.setHorizontalHeaderLabels(results[0].model_dump().keys())

        for row, item in enumerate(results):
            for col, (key, value) in enumerate(item.model_dump().items()):
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                self.results_table.setItem(row, col, QTableWidgetItem(str(value)))

        self.results_table.resizeColumnsToContents()
