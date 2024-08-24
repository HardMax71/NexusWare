import json
from io import BytesIO

import qrcode
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QCursor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox,
                               QLabel, QFileDialog, QMessageBox, QToolTip, QSizePolicy)
from barcode import get_barcode_class
from barcode.writer import ImageWriter

from desktop_app.src.ui.components import StyledButton, StyledLabel


class BarcodeDesignerWidget(QWidget):
    def __init__(self, api_client, product_data=None):
        super().__init__()
        self.api_client = api_client
        self.product_data = product_data
        self.barcode_image = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)

        # Left column
        left_column = QVBoxLayout()
        left_column.setSpacing(10)

        # Barcode type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(StyledLabel("Type:"))
        self.barcode_type = QComboBox()
        self.setup_barcode_types()
        self.barcode_type.setToolTip("Hover for input examples")
        self.barcode_type.view().setMouseTracking(True)
        self.barcode_type.view().entered.connect(self.show_hint)
        type_layout.addWidget(self.barcode_type)
        left_column.addLayout(type_layout)

        # Data input
        data_layout = QVBoxLayout()
        data_layout.addWidget(StyledLabel("Data:"))
        self.data_input = QTextEdit()
        self.data_input.setPlaceholderText("Enter barcode data (JSON format)")
        self.data_input.setMinimumHeight(100)
        data_layout.addWidget(self.data_input)
        left_column.addLayout(data_layout)

        # Generate button
        self.generate_button = StyledButton("Generate Barcode")
        self.generate_button.clicked.connect(self.generate_barcode)
        left_column.addWidget(self.generate_button)

        left_column.addStretch(1)

        # Right column
        right_column = QVBoxLayout()
        right_column.setSpacing(10)

        # Barcode display
        self.barcode_label = QLabel()
        self.barcode_label.setAlignment(Qt.AlignCenter)
        self.barcode_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.barcode_label.setStyleSheet("border: 1px solid #ccc;")
        right_column.addWidget(self.barcode_label, 1)

        # Save button
        self.save_button = StyledButton("Save Barcode")
        self.save_button.clicked.connect(self.save_barcode)
        self.save_button.setEnabled(False)
        right_column.addWidget(self.save_button)

        # Add columns to main layout
        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)

        if self.product_data:
            self.pre_fill_product_data()

        self.setMinimumSize(800, 600)

    def setup_barcode_types(self):
        barcode_types = [
            ("Code 128", "Example: ABC-123"),
            ("QR Code", "Example: https://example.com"),
            ("EAN-13", "Example: 5901234123457"),
            ("UPC-A", "Example: 042100005264"),
            ("ISBN-13", "Example: 978-3-16-148410-0"),
            ("Code 39", "Example: HELLO123")
        ]
        for barcode_type, hint in barcode_types:
            self.barcode_type.addItem(barcode_type, hint)

    def show_hint(self, index):
        hint = self.barcode_type.itemData(index.row())
        QToolTip.showText(QCursor.pos(), hint)

    # if removed - smh aspect ratio of default barcode image will be lost,
    # and the barcode image will be stretched, after "generate" button is clicked -
    # works as expected
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.barcode_image:
            self.update_barcode_label()

    def update_barcode_label(self):
        qimage = QImage.fromData(self.barcode_image)
        pixmap = QPixmap.fromImage(qimage)

        label_size = self.barcode_label.size()
        scaled_pixmap = pixmap.scaled(label_size.width(), label_size.height(),
                                      Qt.KeepAspectRatio)

        self.barcode_label.setPixmap(scaled_pixmap)

    def pre_fill_product_data(self):
        if self.product_data:
            formatted_json = json.dumps(self.product_data, indent=2)
            self.data_input.setPlainText(formatted_json)

    def generate_barcode(self):
        data = self.data_input.toPlainText()
        barcode_type = self.barcode_type.currentText()

        if not data:
            QMessageBox.warning(self, "Input Error", "Please enter barcode data.")
            return

        try:
            # For linear barcodes, use only the SKU
            json_data = json.loads(data)
            sku = json_data.get('sku', '')

            if barcode_type == "QR Code":
                self.generate_qr_code(data)
            else:
                self.generate_linear_barcode(sku, barcode_type)

            self.save_button.setEnabled(True)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid JSON format in the data field.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate barcode: {str(e)}")

    def generate_qr_code(self, data):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        self.barcode_image = buffer.getvalue()
        qimage = QImage.fromData(self.barcode_image)
        pixmap = QPixmap.fromImage(qimage)

        label_size = self.barcode_label.size()
        scaled_pixmap = pixmap.scaled(label_size.width(), label_size.height(),
                                      Qt.KeepAspectRatio)

        self.barcode_label.setPixmap(scaled_pixmap)

    def generate_linear_barcode(self, data, barcode_type):
        barcode_class = get_barcode_class(barcode_type.lower().replace('-', '').replace(' ', ''))
        barcode = barcode_class(data, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer)
        self.barcode_image = buffer.getvalue()
        qimage = QImage.fromData(self.barcode_image)
        pixmap = QPixmap.fromImage(qimage)

        label_size = self.barcode_label.size()
        scaled_pixmap = pixmap.scaled(label_size.width(), label_size.height(),
                                      Qt.KeepAspectRatio)
        self.barcode_label.setPixmap(scaled_pixmap)

    def save_barcode(self):
        if self.barcode_image:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Barcode", "",
                                                       "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)")
            if file_name:
                try:
                    with open(file_name, 'wb') as f:
                        f.write(self.barcode_image)
                    QMessageBox.information(self, "Success", f"Barcode saved as {file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save barcode: {str(e)}")
        else:
            QMessageBox.warning(self, "No Barcode", "Please generate a barcode first.")
