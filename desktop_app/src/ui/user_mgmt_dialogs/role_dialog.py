from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QMessageBox, QDialogButtonBox, QLabel, QCheckBox)

from public_api.api import RolesAPI
from public_api.shared_schemas import RoleCreate, RoleUpdate
from public_api.shared_schemas.user import RolePermissionCreate


class RoleDialog(QDialog):
    def __init__(self, roles_api: RolesAPI, role_id: int = None, parent=None):
        super().__init__(parent)
        self.roles_api = roles_api
        self.role_id = role_id
        self.role = None if role_id is None else self.roles_api.get_role(role_id)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Role" if self.role is None else "Edit Role")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(5)
        self.permissions_table.setHorizontalHeaderLabels(["Permission", "Read", "Write", "Edit", "Delete"])
        self.permissions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.permissions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.permissions_table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_data()

    def load_data(self):
        all_permissions = self.roles_api.get_all_permissions()
        self.permissions_table.setRowCount(len(all_permissions))

        for row, permission in enumerate(all_permissions):
            self.permissions_table.setItem(row, 0, QTableWidgetItem(permission.name))
            for col in range(1, 5):
                checkbox = QCheckBox()
                self.permissions_table.setCellWidget(row, col, checkbox)
            self.permissions_table.item(row, 0).setData(Qt.UserRole, permission)

        if self.role:
            self.name_input.setText(self.role.name)
            for role_perm in self.role.role_permissions:
                for row in range(self.permissions_table.rowCount()):
                    permission_item = self.permissions_table.item(row, 0)
                    permission_data = permission_item.data(Qt.UserRole)

                    if permission_data.id == role_perm.permission_id:
                        self.permissions_table.cellWidget(row, 1).setChecked(role_perm.can_read)
                        self.permissions_table.cellWidget(row, 2).setChecked(role_perm.can_write)
                        self.permissions_table.cellWidget(row, 3).setChecked(role_perm.can_edit)
                        self.permissions_table.cellWidget(row, 4).setChecked(role_perm.can_delete)
                        break

    def accept(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a role name.")
            return

        permissions = [
            RolePermissionCreate(
                permission_id=self.permissions_table.item(row, 0).data(Qt.UserRole).id,
                can_read=self.permissions_table.cellWidget(row, 1).isChecked(),
                can_write=self.permissions_table.cellWidget(row, 2).isChecked(),
                can_edit=self.permissions_table.cellWidget(row, 3).isChecked(),
                can_delete=self.permissions_table.cellWidget(row, 4).isChecked()
            )
            for row in range(self.permissions_table.rowCount())
            if any(self.permissions_table.cellWidget(row, col).isChecked() for col in range(1, 5))
        ]

        try:
            if self.role:
                # Update existing role
                self.roles_api.update_role(self.role_id, RoleUpdate(name=name, permissions=permissions))
            else:
                # Create new role
                self.roles_api.create_role(RoleCreate(name=name, permissions=permissions))
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 f"Failed to {'update' if self.role else 'create'} role: {str(e)}")
