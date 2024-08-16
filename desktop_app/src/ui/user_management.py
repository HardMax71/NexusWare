from PySide6.QtCore import Signal, Qt, QDateTime
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QStackedWidget, QMessageBox, QComboBox, QListWidgetItem,
                               QDialogButtonBox, QListWidget, QLabel, QCheckBox, QFormLayout)

from desktop_app.src.ui.components import StyledButton
from public_api.api import UsersAPI, APIClient
from public_api.shared_schemas import UserSanitizedWithRole, UserFilter, AllPermissions, UserWithPermissions, \
    UserCreate, UserUpdate, AllRoles


class UserManagementWidget(QWidget):
    user_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.users_api = UsersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for main content
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Main User View
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.textChanged.connect(self.filter_users)
        controls_layout.addWidget(self.search_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["All", "Admin", "User", "Manager"])
        self.role_combo.currentTextChanged.connect(self.refresh_users)
        controls_layout.addWidget(self.role_combo)

        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_users)
        controls_layout.addWidget(self.refresh_button)

        main_layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Status", "Last Login", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.stacked_widget.addWidget(main_widget)

        # Floating Action Button for adding new users
        self.fab = StyledButton("+")
        self.fab.clicked.connect(self.add_user)
        layout.addWidget(self.fab)

        self.refresh_users()

    def refresh_users(self):
        role_filter = self.role_combo.currentText()
        if role_filter == "All":
            role_filter = None

        filter_params = UserFilter(role_name=role_filter)
        users = self.users_api.get_users(filter_params=filter_params)
        self.update_table(users)

    def update_table(self, users: list[UserSanitizedWithRole]):
        self.table.setRowCount(len(users))
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(user.username))
            self.table.setItem(row, 1, QTableWidgetItem(user.email))
            self.table.setItem(row, 2, QTableWidgetItem(user.role.role_name))
            self.table.setItem(row, 3, QTableWidgetItem("Active" if user.is_active else "Inactive"))

            # Convert timestamp to QDateTime
            if user.last_login is not None:
                last_login_dt = QDateTime.fromSecsSinceEpoch(user.last_login)
                last_login_str = last_login_dt.toString("yyyy-MM-dd HH:mm:ss")
            else:
                last_login_str = "Never"
            self.table.setItem(row, 4, QTableWidgetItem(last_login_str))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)  # Reduce spacing between buttons

            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, uid=user.id: self.edit_user(uid))
            permissions_button = StyledButton("Permissions")
            permissions_button.clicked.connect(lambda _, uid=user.id: self.manage_permissions(uid))
            delete_button = StyledButton("Delete")
            delete_button.clicked.connect(lambda _, uid=user.id: self.delete_user(uid))

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(permissions_button)
            actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 5, actions_widget)

            # Color coding based on status
            status_colors = {
                "Active": QColor(200, 255, 200),  # Light green
                "Inactive": QColor(255, 200, 200),  # Light red
            }
            self.table.item(row, 3).setBackground(status_colors.get("Active" if user.is_active else "Inactive"))

    def filter_users(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            row_match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.table.setRowHidden(row, not row_match)

    def add_user(self):
        dialog = UserDialog(self.users_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()
            QMessageBox.information(self, "Success", "User added successfully.")

    def edit_user(self, user_id):
        user = self.users_api.get_user(user_id)
        dialog = UserDialog(self.users_api, user=user, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()
            QMessageBox.information(self, "Success", "User updated successfully.")

    def manage_permissions(self, user_id):
        dialog = PermissionManagementDialog(self.users_api, user_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()
            QMessageBox.information(self, "Success", "User permissions updated successfully.")

    def delete_user(self, user_id):
        confirm = QMessageBox.question(self, 'Delete User',
                                       'Are you sure you want to delete this user?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.users_api.delete_user(user_id)
                self.refresh_users()
                self.user_updated.emit()
                QMessageBox.information(self, "Success", "User deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")


class UserDialog(QDialog):
    def __init__(self, users_api: UsersAPI, user: UserSanitizedWithRole = None, parent=None):
        super().__init__(parent)
        self.users_api = users_api
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add User" if not self.user else "Edit User")
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
        all_roles: AllRoles = self.users_api.get_all_roles()
        for role in all_roles.roles:
            self.role_combo.addItem(role.role_name, role.id)

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


class PermissionManagementDialog(QDialog):
    def __init__(self, users_api: UsersAPI, user_id: int, parent=None):
        super().__init__(parent)
        self.users_api = users_api
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Manage User Permissions")
        layout = QVBoxLayout(self)

        # User info
        user_info = self.users_api.get_user(self.user_id)
        info_label = QLabel(f"User: {user_info.username} (Role: {user_info.role.role_name})")
        layout.addWidget(info_label)

        # Permissions list
        self.permissions_list = QListWidget()
        layout.addWidget(self.permissions_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_permissions)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_permissions()

    def load_permissions(self):
        user_permissions: UserWithPermissions = self.users_api.get_user_permissions(self.user_id)
        all_permissions: AllPermissions = self.users_api.get_all_permissions()

        for permission in all_permissions.permissions:
            item = QListWidgetItem(permission.permission_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if permission in user_permissions.permissions else Qt.Unchecked)
            item.setData(Qt.UserRole, permission.id)
            self.permissions_list.addItem(item)

    def save_permissions(self):
        selected_permissions = []
        for index in range(self.permissions_list.count()):
            item = self.permissions_list.item(index)
            if item.checkState() == Qt.Checked:
                selected_permissions.append(item.data(Qt.UserRole))

        try:
            self.users_api.update_user_permissions(self.user_id, selected_permissions)
            QMessageBox.information(self, "Success", "User permissions updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update user permissions: {str(e)}")
