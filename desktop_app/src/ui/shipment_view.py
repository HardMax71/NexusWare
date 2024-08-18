from datetime import datetime
from typing import List, Optional

from PySide6.QtCore import Signal, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                               QMessageBox, QLabel, QStackedWidget, QComboBox, QDateEdit)

from desktop_app.src.ui.components import StyledButton
from public_api.api import ShipmentsAPI, APIClient, OrdersAPI, CarriersAPI
from public_api.shared_schemas import (Shipment, ShipmentCreate, ShipmentUpdate, ShipmentFilter,
                                       ShipmentTracking, ShipmentWithDetails)
from public_api.shared_schemas.warehouse import ShipmentStatus


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

        self.refresh_button = StyledButton("Refresh")
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
        self.fab = StyledButton("+")
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

    def update_table(self, shipments: List[Shipment]):
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

            view_button = StyledButton("View")
            view_button.clicked.connect(lambda _, s=shipment: self.view_shipment(s))
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, s=shipment: self.edit_shipment(s))
            track_button = StyledButton("Track")
            track_button.clicked.connect(lambda _, s=shipment: self.track_shipment(s))
            label_button = StyledButton("Label")
            label_button.clicked.connect(lambda _, s=shipment: self.generate_label(s))
            delete_button = StyledButton("Delete")
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
        try:
            tracking_info = self.shipments_api.track_shipment(shipment.id)
            dialog = ShipmentTrackingDialog(tracking_info, parent=self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to track shipment: {str(e)}")

    def generate_label(self, shipment: Shipment):
        try:
            label = self.shipments_api.generate_shipping_label(shipment.id)
            QMessageBox.information(self, "Success",
                                    f"Shipping label generated successfully. Download URL: {label.label_download_url}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate shipping label: {str(e)}")


class ShipmentDialog(QDialog):
    def __init__(self, shipments_api: ShipmentsAPI, orders_api: OrdersAPI,
                 carriers_api: CarriersAPI, shipment_data: Optional[Shipment] = None, parent=None):
        super().__init__(parent)
        self.shipments_api = shipments_api
        self.orders_api = orders_api
        self.carriers_api = carriers_api
        self.shipment_data = shipment_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Shipment" if not self.shipment_data else "Edit Shipment")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.order_combo = QComboBox()
        self.load_orders()
        form_layout.addRow("Order:", self.order_combo)

        self.carrier_combo = QComboBox()
        self.load_carriers()
        form_layout.addRow("Carrier:", self.carrier_combo)

        self.tracking_number_input = QLineEdit()
        form_layout.addRow("Tracking Number:", self.tracking_number_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems([item.value for item in ShipmentStatus])
        form_layout.addRow("Status:", self.status_combo)

        self.ship_date_edit = QDateEdit()
        self.ship_date_edit.setCalendarPopup(True)
        self.ship_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Ship Date:", self.ship_date_edit)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.shipment_data:
            self.populate_data()

    def load_orders(self):
        try:
            orders = self.orders_api.get_orders()
            for order in orders:
                self.order_combo.addItem(f"{order.id}: {order.customer_id}", order.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load orders: {str(e)}")

    def load_carriers(self):
        try:
            carriers = self.carriers_api.get_carriers()
            for carrier in carriers:
                self.carrier_combo.addItem(carrier.name, carrier.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load carriers: {str(e)}")

    def populate_data(self):
        order_index = self.order_combo.findData(self.shipment_data.order_id)
        self.order_combo.setCurrentIndex(order_index)

        carrier_index = self.carrier_combo.findData(self.shipment_data.carrier_id)
        self.carrier_combo.setCurrentIndex(carrier_index)

        self.tracking_number_input.setText(self.shipment_data.tracking_number or "")
        self.status_combo.setCurrentText(self.shipment_data.status)

        if self.shipment_data.ship_date:
            self.ship_date_edit.setDate(QDate.fromString(
                datetime.fromtimestamp(self.shipment_data.ship_date).strftime("%Y-%m-%d"),
                "yyyy-MM-dd"))

    def accept(self):
        order_id = self.order_combo.currentData()
        carrier_id = self.carrier_combo.currentData()
        tracking_number = self.tracking_number_input.text()
        status = self.status_combo.currentText()
        ship_date = int(self.ship_date_edit.dateTime().toPython().timestamp())

        try:
            if self.shipment_data:
                shipment_update = ShipmentUpdate(
                    order_id=order_id,
                    carrier_id=carrier_id,
                    tracking_number=tracking_number,
                    status=status,
                    ship_date=ship_date
                )
                self.shipments_api.update_shipment(self.shipment_data.id, shipment_update)
                QMessageBox.information(self, "Success", f"Shipment {self.shipment_data.id} updated successfully.")
            else:
                shipment_create = ShipmentCreate(
                    order_id=order_id,
                    carrier_id=carrier_id,
                    tracking_number=tracking_number,
                    status=status,
                    ship_date=ship_date
                )
                new_shipment = self.shipments_api.create_shipment(shipment_create)
                QMessageBox.information(self, "Success", f"Shipment {new_shipment.id} created successfully.")

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


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
