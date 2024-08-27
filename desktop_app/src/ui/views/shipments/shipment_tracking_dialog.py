from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QDialogButtonBox,
                               QLabel)

from public_api.shared_schemas import ShipmentTracking


class ShipmentTrackingDialog(QDialog):
    def __init__(self, tracking_info: ShipmentTracking, parent=None):
        super().__init__(parent)
        self.tracking_info = tracking_info
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Tracking Information - {self.tracking_info.tracking_number}")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.addRow("Shipment ID:", QLabel(str(self.tracking_info.shipment_id)))
        form_layout.addRow("Tracking Number:", QLabel(self.tracking_info.tracking_number))
        form_layout.addRow("Current Status:", QLabel(self.tracking_info.current_status))
        estimated_delivery = datetime.fromtimestamp(self.tracking_info.estimated_delivery_date).strftime(
            "%Y-%m-%d") if self.tracking_info.estimated_delivery_date else "N/A"
        form_layout.addRow("Estimated Delivery:", QLabel(estimated_delivery))

        layout.addLayout(form_layout)

        # Tracking history table
        history_table = QTableWidget()
        history_table.setColumnCount(3)
        history_table.setHorizontalHeaderLabels(["Date", "Location", "Status"])
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_table.setRowCount(len(self.tracking_info.tracking_history))

        for row, event in enumerate(self.tracking_info.tracking_history):
            history_table.setItem(row, 0, QTableWidgetItem(event.get("timestamp", "")))
            history_table.setItem(row, 1, QTableWidgetItem(event.get("location", "")))
            history_table.setItem(row, 2, QTableWidgetItem(event.get("status", "")))

        layout.addWidget(QLabel("Tracking History:"))
        layout.addWidget(history_table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
