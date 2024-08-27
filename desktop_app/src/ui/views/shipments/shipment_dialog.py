from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                               QMessageBox, QComboBox, QDateEdit)

from public_api.api import ShipmentsAPI, OrdersAPI, CarriersAPI
from public_api.shared_schemas import Shipment, ShipmentCreate, ShipmentUpdate, ShipmentStatus


class ShipmentDialog(QDialog):
    def __init__(self, shipments_api: ShipmentsAPI, orders_api: OrdersAPI,
                 carriers_api: CarriersAPI, shipment_data: Shipment | None = None, parent=None):
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
