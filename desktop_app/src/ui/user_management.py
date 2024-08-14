from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem

from desktop_app.src.ui.components import StyledButton
from public_api.api import UsersAPI, APIClient


# TODO: Implement missing functions
class UserManagementWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.users_api = UsersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.add_user_button = StyledButton("Add User")
        self.add_user_button.clicked.connect(self.add_user)
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_users)
        controls_layout.addWidget(self.add_user_button)
        controls_layout.addWidget(self.refresh_button)
        layout.addLayout(controls_layout)

        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Status", "Actions"])
        layout.addWidget(self.users_table)

        self.refresh_users()

    def refresh_users(self):
        users = self.users_api.get_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.email))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.role.role_name))
            self.users_table.setItem(row, 3, QTableWidgetItem("Active" if user.is_active else "Inactive"))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, uid=user.user_id: self.edit_user(uid))
            delete_button = StyledButton("Delete")
            delete_button.clicked.connect(lambda _, uid=user.user_id: self.delete_user(uid))
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            self.users_table.setCellWidget(row, 4, actions_widget)

    def add_user(self):
        # Implement add user dialog
        pass

    def edit_user(self, user_id):
        # Implement edit user dialog
        pass

    def delete_user(self, user_id):
        # Implement user deletion with confirmation
        pass
