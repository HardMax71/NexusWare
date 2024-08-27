from datetime import datetime

from PySide6.QtWidgets import (QVBoxLayout, QDialog, QFormLayout, QDialogButtonBox,
                               QLabel)

from public_api.api import ShipmentsAPI
from public_api.shared_schemas import (ShipmentWithDetails)


class ShipmentDetailsDialog(QDialog):
    def __init__(self, shipment: ShipmentWithDetails, shipments_api: ShipmentsAPI, parent=None):
        super().__init__(parent)
        self.shipment = shipment
        self.shipments_api = shipments_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Shipment Details - {self.shipment.id}")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.addRow("Shipment ID:", QLabel(str(self.shipment.id)))

        order_text = f"{self.shipment.order.id}: {self.shipment.order.customer_id}" if self.shipment.order else "N/A"
        form_layout.addRow("Order:", QLabel(order_text))

        carrier_text = self.shipment.carrier.name if self.shipment.carrier else "N/A"
        form_layout.addRow("Carrier:", QLabel(carrier_text))

        form_layout.addRow("Status:", QLabel(self.shipment.status))
        form_layout.addRow("Tracking Number:", QLabel(self.shipment.tracking_number or "N/A"))
        ship_date = datetime.fromtimestamp(self.shipment.ship_date).strftime(
            "%Y-%m-%d") if self.shipment.ship_date else "N/A"
        form_layout.addRow("Ship Date:", QLabel(ship_date))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
