from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QMessageBox, QComboBox, QDialogButtonBox, QCheckBox,
                               QFormLayout)

from public_api.api import UsersAPI, RolesAPI
from public_api.shared_schemas import UserSanitized, UserCreate, UserUpdate


class UserDialog(QDialog):
    def __init__(self, users_api: UsersAPI, roles_api: RolesAPI, user: UserSanitized = None, parent=None):
        super().__init__(parent)
        self.users_api = users_api
        self.roles_api = roles_api
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add User" if not self.user else "Edit User")
        self.setMinimumSize(400, 200)
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        self.is_active_checkbox = QCheckBox()

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Role:", self.role_combo)
        form_layout.addRow("Is Active:", self.is_active_checkbox)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_roles()
        if self.user:
            self.populate_data()

    def load_roles(self):
        all_roles = self.roles_api.get_all_roles()
        for role in all_roles:
            self.role_combo.addItem(role.name, role.id)

    def populate_data(self):
        self.username_input.setText(self.user.username)
        self.email_input.setText(self.user.email)
        self.role_combo.setCurrentIndex(self.role_combo.findData(self.user.role.id))
        self.is_active_checkbox.setChecked(self.user.is_active)
        self.password_input.setPlaceholderText("Leave blank to keep current password")

    def accept(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        role_id = self.role_combo.currentData()
        is_active = self.is_active_checkbox.isChecked()

        try:
            if self.user:
                user_update = UserUpdate(
                    username=username,
                    email=email,
                    role_id=role_id,
                    is_active=is_active
                )
                if password:
                    user_update.password = password
                self.users_api.update_user(self.user.id, user_update)
            else:
                user_create = UserCreate(
                    username=username,
                    email=email,
                    password=password,
                    role_id=role_id,
                    is_active=is_active
                )
                self.users_api.create_user(user_create)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to {'update' if self.user else 'create'} user: {str(e)}")
