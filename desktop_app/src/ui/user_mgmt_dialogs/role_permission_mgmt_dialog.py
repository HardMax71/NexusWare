from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QMessageBox, QListWidgetItem,
                               QListWidget, QTabWidget, QPushButton)

from desktop_app.src.ui.user_mgmt_dialogs import RoleDialog, PermissionDialog
from public_api.api import RolesAPI


class RolePermissionManagementDialog(QDialog):
    def __init__(self, roles_api: RolesAPI, parent=None):
        super().__init__(parent)
        self.roles_api = roles_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Manage Roles and Permissions")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_roles_tab(), "Roles")
        self.tab_widget.addTab(self.create_permissions_tab(), "Permissions")
        layout.addWidget(self.tab_widget)

    def create_roles_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left panel: Roles list and buttons
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.roles_list = QListWidget()
        self.roles_list.itemClicked.connect(self.show_role_permissions)
        left_layout.addWidget(self.roles_list)

        roles_buttons = QHBoxLayout()
        add_role_button = QPushButton("Add")
        add_role_button.clicked.connect(self.add_role)
        edit_role_button = QPushButton("Edit")
        edit_role_button.clicked.connect(self.edit_role)
        delete_role_button = QPushButton("Delete")
        delete_role_button.clicked.connect(self.delete_role)
        roles_buttons.addWidget(add_role_button)
        roles_buttons.addWidget(edit_role_button)
        roles_buttons.addWidget(delete_role_button)
        left_layout.addLayout(roles_buttons)

        # Set a minimum width for the left panel
        left_panel.setMinimumWidth(200)

        # Right panel: Role permissions table
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.role_permissions_table = QTableWidget()
        self.role_permissions_table.setColumnCount(5)
        self.role_permissions_table.setHorizontalHeaderLabels(["Permission", "Read", "Write", "Edit", "Delete"])
        self.role_permissions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.role_permissions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.role_permissions_table.verticalHeader().setVisible(False)
        right_layout.addWidget(self.role_permissions_table)

        # Add panels to main layout
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 3)

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
        edit_permission_button = QPushButton("Edit Permission")
        edit_permission_button.clicked.connect(self.edit_permission)
        delete_permission_button = QPushButton("Delete Permission")
        delete_permission_button.clicked.connect(self.delete_permission)
        buttons_layout.addWidget(add_permission_button)
        buttons_layout.addWidget(edit_permission_button)
        buttons_layout.addWidget(delete_permission_button)
        layout.addLayout(buttons_layout)

        self.load_permissions()

        return widget

    def load_roles(self):
        self.roles_list.clear()
        roles = self.roles_api.get_all_roles()
        for role in roles:
            item = QListWidgetItem(role.name)
            item.setData(Qt.UserRole, role)
            self.roles_list.addItem(item)

        if self.roles_list.count() > 0:
            self.roles_list.setCurrentRow(0)
            self.show_role_permissions(self.roles_list.item(0))

    def load_permissions(self):
        self.permissions_list.clear()
        permissions = self.roles_api.get_all_permissions()
        for permission in permissions:
            item = QListWidgetItem(permission.name)
            item.setData(Qt.UserRole, permission)
            self.permissions_list.addItem(item)

    def show_role_permissions(self, item):
        if item is None:
            self.role_permissions_table.setRowCount(0)
            return

        role = item.data(Qt.UserRole)
        self.role_permissions_table.setRowCount(len(role.role_permissions))
        for row, role_permission in enumerate(role.role_permissions):
            self.role_permissions_table.setItem(row, 0, QTableWidgetItem(role_permission.permission.name))
            self.role_permissions_table.setItem(row, 1, QTableWidgetItem("✓" if role_permission.can_read else ""))
            self.role_permissions_table.setItem(row, 2, QTableWidgetItem("✓" if role_permission.can_write else ""))
            self.role_permissions_table.setItem(row, 3, QTableWidgetItem("✓" if role_permission.can_edit else ""))
            self.role_permissions_table.setItem(row, 4, QTableWidgetItem("✓" if role_permission.can_delete else ""))

        self.role_permissions_table.resizeColumnsToContents()

    def add_role(self):
        dialog = RoleDialog(self.roles_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_roles()

    def edit_role(self):
        selected_items = self.roles_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a role to edit.")
            return
        role = selected_items[0].data(Qt.UserRole)
        dialog = RoleDialog(self.roles_api, role_id=role.id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_roles()
            # Update the permissions table for the edited role
            for i in range(self.roles_list.count()):
                item = self.roles_list.item(i)
                if item.data(Qt.UserRole).id == role.id:
                    self.roles_list.setCurrentItem(item)
                    self.show_role_permissions(item)
                    break

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
                self.roles_api.delete_role(role.id)
                self.load_roles()
                QMessageBox.information(self, "Success", "Role deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete role: {str(e)}")

    def add_permission(self):
        dialog = PermissionDialog(self.roles_api, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_permissions()
            # Refresh the roles to show the new permission
            self.load_roles()

    def edit_permission(self):
        selected_items = self.permissions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a permission to edit.")
            return
        permission = selected_items[0].data(Qt.UserRole)
        dialog = PermissionDialog(self.roles_api, permission=permission, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_permissions()
            # Refresh the roles to show the updated permission
            self.load_roles()

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
                self.roles_api.delete_permission(permission.id)
                self.load_permissions()
                # Refresh the roles to remove the deleted permission
                self.load_roles()
                QMessageBox.information(self, "Success", "Permission deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete permission: {str(e)}")
