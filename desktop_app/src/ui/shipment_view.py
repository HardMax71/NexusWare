from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox

from desktop_app.src.ui.components import StyledButton
from public_api.api import ShipmentsAPI
from public_api.shared_schemas import ShipmentFilter


# TODO: Implement shipment tracking dialog
class ShipmentView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.shipments_api = ShipmentsAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "In Transit", "Delivered"])
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_shipments)
        controls_layout.addWidget(self.status_combo)
        controls_layout.addWidget(self.refresh_button)
        layout.addLayout(controls_layout)

        # Shipments table
        self.shipments_table = QTableWidget()
        self.shipments_table.setColumnCount(6)
        self.shipments_table.setHorizontalHeaderLabels(
            ["Shipment ID", "Order ID", "Customer", "Status", "Tracking", "Actions"])
        layout.addWidget(self.shipments_table)

        self.refresh_shipments()

    def refresh_shipments(self):
        status_filter = self.status_combo.currentText()
        if status_filter == "All":
            status_filter = None

        filter = ShipmentFilter(status=status_filter)
        shipments = self.shipments_api.get_shipments(filter_params=filter)
        self.shipments_table.setRowCount(len(shipments))
        for row, shipment in enumerate(shipments):
            self.shipments_table.setItem(row, 0, QTableWidgetItem(str(shipment.id)))
            self.shipments_table.setItem(row, 1, QTableWidgetItem(str(shipment.order_id)))
            self.shipments_table.setItem(row, 2, QTableWidgetItem(shipment.label_id))
            self.shipments_table.setItem(row, 3, QTableWidgetItem(shipment.status))
            self.shipments_table.setItem(row, 4, QTableWidgetItem(shipment.tracking_number))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            track_button = StyledButton("Track")
            track_button.clicked.connect(lambda _, sid=shipment.id: self.track_shipment(sid))
            actions_layout.addWidget(track_button)
            self.shipments_table.setCellWidget(row, 5, actions_widget)

    def track_shipment(self, shipment_id):
        tracking_info = self.shipments_api.track_shipment(shipment_id)
        # Implement a dialog to display tracking information
        print(f"Tracking info for shipment {shipment_id}: {tracking_info}")
