from PySide6.QtCore import Signal, QDateTime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QMessageBox, QComboBox)

from desktop_app.src.ui.components import StyledButton
from public_api.api import UsersAPI, APIClient, RolesAPI
from public_api.permissions import PermissionName
from public_api.shared_schemas import UserSanitized, UserFilter
from .role_permission_mgmt_dialog import RolePermissionManagementDialog
from .user_dialog import UserDialog
from ...icon_path_enum import IconPath


class UserManagementWidget(QWidget):
    user_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.users_api = UsersAPI(api_client)
        self.roles_api = RolesAPI(api_client)
        self.roles = self.roles_api.get_all_roles()
        self.role_name_to_id = {role.name: role.id for role in self.roles}
        self.permission_manager = self.users_api.get_current_user_permissions()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.textChanged.connect(self.filter_users)
        controls_layout.addWidget(self.search_input)

        self.role_combo = QComboBox()
        self.role_combo.addItem("All", None)
        for role in self.roles:
            self.role_combo.addItem(role.name, role.id)
        self.role_combo.currentTextChanged.connect(self.filter_users)
        controls_layout.addWidget(self.role_combo)

        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
        self.refresh_button.clicked.connect(self.refresh_users)
        controls_layout.addWidget(self.refresh_button)

        self.manage_roles_permissions_button = StyledButton("Manage Roles")
        self.manage_roles_permissions_button.clicked.connect(self.open_role_permission_management)
        controls_layout.addWidget(self.manage_roles_permissions_button)

        layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Status", "Last Login", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Floating Action Button for adding new users
        if self.permission_manager.has_write_permission(PermissionName.USER_MANAGEMENT):
            self.fab = StyledButton("+", icon_path=IconPath.PLUS)
            self.fab.clicked.connect(self.add_user)
            layout.addWidget(self.fab)

        self.refresh_users()

    def refresh_users(self):
        role_id = self.role_combo.currentData()
        filter_params = UserFilter(role_id=role_id)
        users = self.users_api.get_users(filter_params=filter_params)
        self.update_table(users)

    def update_table(self, users: list[UserSanitized]):
        self.table.setRowCount(len(users))
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(user.username))
            self.table.setItem(row, 1, QTableWidgetItem(user.email))
            self.table.setItem(row, 2, QTableWidgetItem(user.role.name))
            self.table.setItem(row, 3, QTableWidgetItem("Active" if user.is_active else "Inactive"))

            if user.last_login is not None:
                last_login_dt = QDateTime.fromSecsSinceEpoch(user.last_login)
                last_login_str = last_login_dt.toString("yyyy-MM-dd HH:mm:ss")
            else:
                last_login_str = "Never"
            self.table.setItem(row, 4, QTableWidgetItem(last_login_str))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            if self.permission_manager.has_write_permission(PermissionName.USER_MANAGEMENT):
                edit_button = StyledButton("Edit", icon_path=IconPath.EDIT)
                edit_button.clicked.connect(lambda _, uid=user.id: self.edit_user(uid))
                actions_layout.addWidget(edit_button)

            if self.permission_manager.has_delete_permission(PermissionName.USER_MANAGEMENT):
                delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
                delete_button.clicked.connect(lambda _, uid=user.id: self.delete_user(uid))
                actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 5, actions_widget)

    def filter_users(self):
        search_text = self.search_input.text().lower()
        selected_role_id = self.role_combo.currentData()

        for row in range(self.table.rowCount()):
            row_match = True

            if search_text:
                row_match = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_match = True
                        break

            if selected_role_id is not None and row_match:
                role_item = self.table.item(row, 2)
                if role_item:
                    role_name = role_item.text()
                    role_id = self.role_name_to_id.get(role_name)
                    if role_id != selected_role_id:
                        row_match = False

            self.table.setRowHidden(row, not row_match)

    def add_user(self):
        dialog = UserDialog(users_api=self.users_api,
                            roles_api=self.roles_api,
                            parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()
            QMessageBox.information(self, "Success", "User added successfully.")

    def edit_user(self, user_id):
        user = self.users_api.get_user(user_id)
        dialog = UserDialog(users_api=self.users_api,
                            roles_api=self.roles_api,
                            user=user, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()
            QMessageBox.information(self, "Success", "User updated successfully.")

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

    def open_role_permission_management(self):
        dialog = RolePermissionManagementDialog(self.roles_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()
