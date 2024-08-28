from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QLabel

from .components import StyledButton
from .icon_path_enum import IconPath


class OfflineModeWidget(QWidget):
    def __init__(self, api_client, offline_manager):
        super().__init__()
        self.api_client = api_client
        self.offline_manager = offline_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Status and controls
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Offline Mode: Inactive")
        self.toggle_button = StyledButton("Enable Offline Mode", icon_path=IconPath.OFFLINE)
        self.toggle_button.clicked.connect(self.toggle_offline_mode)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        layout.addLayout(status_layout)

        # Pending actions list
        self.pending_actions = QListWidget()
        layout.addWidget(self.pending_actions)

        # Sync button
        self.sync_button = StyledButton("Sync with Server", icon_path=IconPath.SYNC)
        self.sync_button.clicked.connect(self.sync_with_server)
        layout.addWidget(self.sync_button)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        self.update_ui()

    def toggle_offline_mode(self):
        self.offline_manager.toggle_offline_mode()
        self.update_ui()

    def update_ui(self):
        is_offline = self.offline_manager.is_offline_mode()
        self.status_label.setText(f"Offline Mode: {'Active' if is_offline else 'Inactive'}")
        self.toggle_button.setText("Disable Offline Mode" if is_offline else "Enable Offline Mode")
        self.sync_button.setEnabled(is_offline)
        self.update_pending_actions()

    def update_pending_actions(self):
        self.pending_actions.clear()
        actions = self.offline_manager.get_pending_actions()
        for action in actions:
            self.pending_actions.addItem(f"{action['type']} - {action['description']}")

    def sync_with_server(self):
        self.log_display.clear()
        self.log_display.append("Starting sync with server...")

        try:
            sync_results = self.offline_manager.sync_with_server()
            for result in sync_results:
                self.log_display.append(
                    f"Synced: {result['description']} - {'Success' if result['success'] else 'Failed'}")
        except Exception as e:
            self.log_display.append(f"Sync failed: {str(e)}")

        self.log_display.append("Sync completed.")
        self.update_pending_actions()
