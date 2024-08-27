from PySide6.QtWidgets import (QVBoxLayout, QDialog, QFormLayout, QDialogButtonBox,
                               QLabel)

from public_api.shared_schemas import Supplier


class SupplierDetailsDialog(QDialog):
    def __init__(self, supplier: Supplier, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Supplier Details - {self.supplier.name}")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.addRow("Name:", QLabel(self.supplier.name))
        form_layout.addRow("Contact Person:", QLabel(self.supplier.contact_person or "N/A"))
        form_layout.addRow("Email:", QLabel(self.supplier.email or "N/A"))
        form_layout.addRow("Phone:", QLabel(self.supplier.phone or "N/A"))
        form_layout.addRow("Address:", QLabel(self.supplier.address or "N/A"))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
