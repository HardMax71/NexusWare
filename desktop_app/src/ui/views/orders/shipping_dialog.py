from PySide6.QtWidgets import (QVBoxLayout, QDialog, QComboBox,
                               QFormLayout, QDialogButtonBox, QLineEdit, QMessageBox)

from public_api.api import ShipmentsAPI, CarriersAPI
from public_api.shared_schemas import ShippingInfo


class ShippingDialog(QDialog):
    def __init__(self, shipments_api: ShipmentsAPI, carriers_api: CarriersAPI, parent=None):
        super().__init__(parent)
        self.shipments_api = shipments_api
        self.carriers_api = carriers_api
        self.carriers = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ship Order")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.carrier_combo = QComboBox()
        self.load_carriers()
        form_layout.addRow("Carrier:", self.carrier_combo)

        self.tracking_input = QLineEdit()
        form_layout.addRow("Tracking Number:", self.tracking_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_carriers(self):
        try:
            self.carriers = self.carriers_api.get_carriers()
            self.carrier_combo.clear()
            self.carrier_combo.addItems([carrier.name for carrier in self.carriers])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load carriers: {str(e)}")

    def get_shipping_info(self) -> ShippingInfo:
        selected_carrier = self.carriers[self.carrier_combo.currentIndex()]
        return ShippingInfo(
            carrier=selected_carrier.name,
            carrier_id=selected_carrier.id,
            tracking_number=self.tracking_input.text()
        )
