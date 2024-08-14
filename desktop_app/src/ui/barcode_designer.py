from io import BytesIO

import qrcode
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QLabel, QFileDialog
from barcode.codex import Code128
from barcode.writer import ImageWriter

from desktop_app.src.ui.components import StyledButton


class BarcodeDesignerWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Input controls
        input_layout = QHBoxLayout()
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Enter barcode data")
        self.barcode_type = QComboBox()
        self.barcode_type.addItems(["Code 128", "QR Code"])
        input_layout.addWidget(self.data_input)
        input_layout.addWidget(self.barcode_type)
        layout.addLayout(input_layout)

        # Generate button
        self.generate_button = StyledButton("Generate Barcode")
        self.generate_button.clicked.connect(self.generate_barcode)
        layout.addWidget(self.generate_button)

        # Barcode display
        self.barcode_label = QLabel()
        self.barcode_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.barcode_label)

        # Save button
        self.save_button = StyledButton("Save Barcode")
        self.save_button.clicked.connect(self.save_barcode)
        layout.addWidget(self.save_button)

    def generate_barcode(self):
        data = self.data_input.text()
        barcode_type = self.barcode_type.currentText()

        # TODO: Add support for more barcode types
        # TODO: Add error handling
        # TODO: check correctness
        if barcode_type == "Code 128":
            barcode = Code128(data, writer=ImageWriter())
            buffer = BytesIO()
            barcode.write(buffer)
            image = QImage.fromData(buffer.getvalue())
        elif barcode_type == "QR Code":
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            image = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image = QImage.fromData(buffer.getvalue())

        pixmap = QPixmap.fromImage(image)
        self.barcode_label.setPixmap(pixmap)

    def save_barcode(self):
        if self.barcode_label.pixmap():
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Barcode", "", "PNG Files (*.png)")
            if file_name:
                self.barcode_label.pixmap().save(file_name, "PNG")
