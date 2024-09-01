from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QMessageBox, QStackedWidget, QComboBox)

from public_api.api import ShipmentsAPI, APIClient, OrdersAPI, CarriersAPI
from public_api.shared_schemas import Shipment, ShipmentFilter, ShipmentStatus
from src.ui.components import StyledButton
from src.ui.components.icon_path import IconPath
from src.ui.views.shipments.shipment_details_dialog import ShipmentDetailsDialog
from src.ui.views.shipments.shipment_dialog import ShipmentDialog
from src.ui.views.shipments.shipment_tracking_dialog import ShipmentTrackingDialog


class ShipmentView(QWidget):
    shipment_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.shipments_api = ShipmentsAPI(api_client)
        self.orders_api = OrdersAPI(api_client)
        self.carriers_api = CarriersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main Shipment View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All"] + [status.value for status in ShipmentStatus])
        self.status_combo.currentIndexChanged.connect(self.refresh_shipments)
        controls_layout.addWidget(self.status_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search shipments...")
        self.search_input.textChanged.connect(self.filter_shipments)
        controls_layout.addWidget(self.search_input)

        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
        self.refresh_button.clicked.connect(self.refresh_shipments)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Shipments table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Order ID", "Carrier", "Status", "Tracking", "Ship Date", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)

        self.stacked_widget.addWidget(main_widget)

        # Floating Action Button for adding new shipments
        self.fab = StyledButton("+", icon_path=IconPath.PLUS)
        self.fab.clicked.connect(self.create_shipment)
        layout.addWidget(self.fab)

        self.refresh_shipments()

    def refresh_shipments(self):
        status_filter = self.status_combo.currentText()
        if status_filter == "All":
            status_filter = None

        filter_params = ShipmentFilter(status=status_filter)
        shipments = self.shipments_api.get_shipments(filter_params=filter_params)
        self.update_table(shipments)

    def update_table(self, shipments: list[Shipment]):
        self.table.setRowCount(len(shipments))
        for row, shipment in enumerate(shipments):
            shipment_details = self.shipments_api.get_shipment_with_details(shipment.id)

            order_text = (
                f"Order #{shipment_details.order.id} - "
                f"{datetime.fromtimestamp(shipment_details.order.order_date).strftime('%Y-%m-%d')} "
                f"(${shipment_details.order.total_amount:.2f})") if shipment_details.order \
                else f"Order #{shipment.order_id}"
            carrier_text = shipment_details.carrier.name if shipment_details.carrier else str(shipment.carrier_id)

            self.table.setItem(row, 0, QTableWidgetItem(order_text))
            self.table.setItem(row, 1, QTableWidgetItem(carrier_text))
            self.table.setItem(row, 2, QTableWidgetItem(shipment.status))
            self.table.setItem(row, 3, QTableWidgetItem(shipment.tracking_number or ""))
            ship_date = datetime.fromtimestamp(shipment.ship_date).strftime("%Y-%m-%d") if shipment.ship_date else ""
            self.table.setItem(row, 4, QTableWidgetItem(ship_date))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View", icon_path=IconPath.VIEW)
            view_button.clicked.connect(lambda _, s=shipment: self.view_shipment(s))
            edit_button = StyledButton("Edit", icon_path=IconPath.EDIT)
            edit_button.clicked.connect(lambda _, s=shipment: self.edit_shipment(s))
            track_button = StyledButton("Track", icon_path=IconPath.TRACK)
            track_button.clicked.connect(lambda _, s=shipment: self.track_shipment(s))
            label_button = StyledButton("Label", icon_path=IconPath.LABEL)
            label_button.clicked.connect(lambda _, s=shipment: self.generate_label(s))
            delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
            delete_button.clicked.connect(lambda _, s=shipment: self.delete_shipment(s))

            actions_layout.addWidget(view_button)
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(track_button)
            actions_layout.addWidget(label_button)
            actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 5, actions_widget)

    def filter_shipments(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            row_match = False
            for col in range(self.table.columnCount() - 1):  # Exclude the Actions column
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.table.setRowHidden(row, not row_match)

    def create_shipment(self):
        dialog = ShipmentDialog(self.shipments_api, self.orders_api, self.carriers_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_shipments()
            self.shipment_updated.emit()

    def edit_shipment(self, shipment: Shipment):
        dialog = ShipmentDialog(self.shipments_api, self.orders_api, self.carriers_api, shipment_data=shipment,
                                parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_shipments()
            self.shipment_updated.emit()

    def view_shipment(self, shipment: Shipment):
        shipment_details = self.shipments_api.get_shipment_with_details(shipment.id)
        dialog = ShipmentDetailsDialog(shipment_details, self.shipments_api, parent=self)
        dialog.exec_()

    def delete_shipment(self, shipment: Shipment):
        reply = QMessageBox.question(self, 'Delete Shipment',
                                     f"Are you sure you want to delete shipment {shipment.id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.shipments_api.delete_shipment(shipment.id)
                QMessageBox.information(self, "Success", f"Shipment {shipment.id} deleted successfully.")
                self.refresh_shipments()
                self.shipment_updated.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete shipment: {str(e)}")

    def track_shipment(self, shipment: Shipment):
        tracking_info = self.shipments_api.track_shipment(shipment.id)
        dialog = ShipmentTrackingDialog(tracking_info, parent=self)
        dialog.exec_()

    def generate_label(self, shipment: Shipment):
        label = self.shipments_api.generate_shipping_label(shipment.id)
        QMessageBox.information(self, "Success",
                                f"Shipping label generated successfully. Download URL: {label.label_download_url}")
