from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QMessageBox, QDialogButtonBox, QFormLayout)

from public_api.api import RolesAPI
from public_api.shared_schemas import Permission, PermissionCreate, PermissionUpdate


class PermissionDialog(QDialog):
    def __init__(self, roles_api: RolesAPI, permission: Permission = None, parent=None):
        super().__init__(parent)
        self.roles_api = roles_api
        self.permission = permission
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Permission" if not self.permission else "Edit Permission")
        self.setMinimumSize(300, 150)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.permission:
            self.populate_data()

    def populate_data(self):
        self.name_input.setText(self.permission.name)

    def accept(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a permission name.")
            return

        try:
            if self.permission:
                permission_update = PermissionUpdate(name=name)
                self.roles_api.update_permission(self.permission.id, permission_update)
            else:
                permission_create = PermissionCreate(name=name)
                self.roles_api.create_permission(permission_create)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 f"Failed to {'update' if self.permission else 'create'} permission: {str(e)}")
