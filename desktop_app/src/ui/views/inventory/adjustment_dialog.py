from datetime import datetime

from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QPushButton, QHBoxLayout, QMessageBox, QTextEdit)

from public_api.api import InventoryAPI
from public_api.shared_schemas import InventoryAdjustment


class AdjustmentDialog(QDialog):
    def __init__(self, inventory_api: InventoryAPI, id: int, parent=None):
        super().__init__(parent)
        self.inventory_api = inventory_api
        self.id = id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Adjust Inventory")
        layout = QFormLayout(self)

        self.adjustment_input = QSpinBox()
        self.adjustment_input.setRange(-1000000, 1000000)
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Enter reason for adjustment...")

        layout.addRow("Adjustment:", self.adjustment_input)
        layout.addRow("Reason:", self.reason_input)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_adjustment)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

    def save_adjustment(self):
        try:
            adjustment_data = InventoryAdjustment(
                product_id=self.id,
                location_id=self.id,
                quantity_change=self.adjustment_input.value(),
                reason=self.reason_input.toPlainText(),
                timestamp=int(datetime.now().timestamp())  # Pass timestamp
            )
            self.inventory_api.adjust_inventory(self.id, adjustment_data)
            QMessageBox.information(self, "Success", "Adjustment saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save adjustment: {str(e)}")
