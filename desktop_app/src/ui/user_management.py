from PySide6.QtCore import Signal, Qt, QDateTime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QMessageBox, QComboBox, QListWidgetItem,
                               QDialogButtonBox, QListWidget, QLabel, QCheckBox, QFormLayout, QTabWidget, QPushButton)

from desktop_app.src.ui.components import StyledButton
from public_api.api import UsersAPI, APIClient
from public_api.shared_schemas import UserSanitized, UserFilter, UserCreate, UserUpdate, AllRoles, Role, Permission, \
    RoleCreate, RoleUpdate, PermissionCreate, \
    PermissionUpdate
from public_api.shared_schemas.user import RolePermissionCreate


class UserManagementWidget(QWidget):
    user_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.users_api = UsersAPI(api_client)
        self.roles = self.users_api.get_all_roles().roles
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

        self.refresh_button = StyledButton("Refresh")
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
        if self.permission_manager.has_write_permission("user_management"):
            self.fab = StyledButton("+")
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

            if self.permission_manager.has_write_permission("user_management"):
                edit_button = StyledButton("Edit")
                edit_button.clicked.connect(lambda _, uid=user.id: self.edit_user(uid))
                actions_layout.addWidget(edit_button)

            if self.permission_manager.has_delete_permission("user_management"):
                delete_button = StyledButton("Delete")
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
        dialog = RolePermissionManagementDialog(self.users_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_users()
            self.user_updated.emit()


class RolePermissionManagementDialog(QDialog):
    def __init__(self, users_api: UsersAPI, parent=None):
        super().__init__(parent)
        self.users_api = users_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Manage Roles and Permissions")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)

        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_roles_tab(), "Roles")
        tab_widget.addTab(self.create_permissions_tab(), "Permissions")
        layout.addWidget(tab_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_roles_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.roles_list = QListWidget()
        self.roles_list.itemClicked.connect(self.show_role_permissions)
        layout.addWidget(self.roles_list)

        buttons_layout = QHBoxLayout()
        add_role_button = QPushButton("Add Role")
        add_role_button.clicked.connect(self.add_role)
        buttons_layout.addWidget(add_role_button)

        edit_role_button = QPushButton("Edit Role")
        edit_role_button.clicked.connect(self.edit_role)
        buttons_layout.addWidget(edit_role_button)

        delete_role_button = QPushButton("Delete Role")
        delete_role_button.clicked.connect(self.delete_role)
        buttons_layout.addWidget(delete_role_button)

        layout.addLayout(buttons_layout)

        self.role_permissions_list = QListWidget()
        layout.addWidget(self.role_permissions_list)

        self.load_roles()

        return widget

    def create_permissions_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.permissions_list = QListWidget()
        layout.addWidget(self.permissions_list)

        buttons_layout = QHBoxLayout()
        add_permission_button = QPushButton("Add Permission")
        add_permission_button.clicked.connect(self.add_permission)
        buttons_layout.addWidget(add_permission_button)

        edit_permission_button = QPushButton("Edit Permission")
        edit_permission_button.clicked.connect(self.edit_permission)
        buttons_layout.addWidget(edit_permission_button)

        delete_permission_button = QPushButton("Delete Permission")
        delete_permission_button.clicked.connect(self.delete_permission)
        buttons_layout.addWidget(delete_permission_button)

        layout.addLayout(buttons_layout)

        self.load_permissions()

        return widget

    def load_roles(self):
        self.roles_list.clear()
        roles = self.users_api.get_all_roles().roles
        for role in roles:
            item = QListWidgetItem(role.name)
            item.setData(Qt.UserRole, role)
            self.roles_list.addItem(item)

    def load_permissions(self):
        self.permissions_list.clear()
        permissions = self.users_api.get_all_permissions().permissions
        for permission in permissions:
            item = QListWidgetItem(permission.name)
            item.setData(Qt.UserRole, permission)
            self.permissions_list.addItem(item)

    def show_role_permissions(self, item):
        role = item.data(Qt.UserRole)
        self.role_permissions_list.clear()
        for permission in role.permissions:
            perm_item = QListWidgetItem(
                f"{permission.name}: Read={permission.can_read}, Write={permission.can_write}, Edit={permission.can_edit}, Delete={permission.can_delete}")
            self.role_permissions_list.addItem(perm_item)

    def add_role(self):
        dialog = RoleDialog(self.users_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_roles()

    def edit_role(self):
        selected_items = self.roles_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a role to edit.")
            return
        role = selected_items[0].data(Qt.UserRole)
        dialog = RoleDialog(self.users_api, role_id=role.id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_roles()

    def delete_role(self):
        selected_items = self.roles_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a role to delete.")
            return
        role = selected_items[0].data(Qt.UserRole)
        confirm = QMessageBox.question(self, 'Delete Role',
                                       f'Are you sure you want to delete the role "{role.name}"?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.users_api.delete_role(role.id)
                self.load_roles()
                QMessageBox.information(self, "Success", "Role deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete role: {str(e)}")

    def add_permission(self):
        dialog = PermissionDialog(self.users_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_permissions()

    def edit_permission(self):
        selected_items = self.permissions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a permission to edit.")
            return
        permission = selected_items[0].data(Qt.UserRole)
        dialog = PermissionDialog(self.users_api, permission=permission, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_permissions()

    def delete_permission(self):
        selected_items = self.permissions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a permission to delete.")
            return
        permission = selected_items[0].data(Qt.UserRole)
        confirm = QMessageBox.question(self, 'Delete Permission',
                                       f'Are you sure you want to delete the permission "{permission.name}"?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.users_api.delete_permission(permission.id)
                self.load_permissions()
                QMessageBox.information(self, "Success", "Permission deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete permission: {str(e)}")


class RoleDialog(QDialog):
    def __init__(self, users_api: UsersAPI, role_id: int = None, parent=None):
        super().__init__(parent)
        self.users_api = users_api
        self.role_id = role_id
        self.role = None if role_id is None else self.users_api.get_role(role_id)
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
        self.permissions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.permissions_table)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_data()

    def load_data(self):
        all_permissions = self.users_api.get_all_permissions().permissions
        self.permissions_table.setRowCount(len(all_permissions))

        for row, permission in enumerate(all_permissions):
            self.permissions_table.setItem(row, 0, QTableWidgetItem(permission.name))
            for col in range(1, 5):
                checkbox = QCheckBox()
                self.permissions_table.setCellWidget(row, col, checkbox)
            self.permissions_table.item(row, 0).setData(Qt.UserRole, permission)

        if self.role:
            self.name_input.setText(self.role.name)
            for role_perm in self.role.permissions:
                for row in range(self.permissions_table.rowCount()):
                    if self.permissions_table.item(row, 0).data(Qt.UserRole).id == role_perm.permission_id:
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
                self.users_api.update_role(self.role_id, RoleUpdate(name=name, permissions=permissions))
            else:
                self.users_api.create_role(RoleCreate(name=name, permissions=permissions))
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to {'update' if self.role else 'create'} role: {str(e)}")


class PermissionDialog(QDialog):
    def __init__(self, users_api: UsersAPI, permission: Permission = None, parent=None):
        super().__init__(parent)
        self.users_api = users_api
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
                self.users_api.update_permission(self.permission.id, permission_update)
            else:
                permission_create = PermissionCreate(name=name)
                self.users_api.create_permission(permission_create)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 f"Failed to {'update' if self.permission else 'create'} permission: {str(e)}")

# Update the UserDialog to use the new role structure
class UserDialog(QDialog):
    def __init__(self, users_api: UsersAPI, user: UserSanitized = None, parent=None):
        super().__init__(parent)
        self.users_api = users_api
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
        all_roles: AllRoles = self.users_api.get_all_roles()
        for role in all_roles.roles:
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
