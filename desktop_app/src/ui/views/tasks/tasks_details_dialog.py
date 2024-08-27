from datetime import datetime

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QLabel,
                               QTextEdit, QFormLayout, QPushButton, QScrollArea)

from public_api.shared_schemas import TaskWithAssignee, UserSanitized


class TaskDetailsDialog(QDialog):
    def __init__(self, task: TaskWithAssignee, users: list[UserSanitized], parent=None):
        super().__init__(parent)
        self.task = task
        self.users = users
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Task Details | Task #{self.task.id}")
        main_layout = QVBoxLayout(self)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        form_layout = QFormLayout()

        # Task Type
        task_type_edit = QTextEdit()
        task_type_edit.setPlainText(self.task.task_type)
        task_type_edit.setReadOnly(True)
        task_type_edit.setMaximumHeight(100)
        form_layout.addRow("Task Type:", task_type_edit)

        # Description
        description_edit = QTextEdit()
        description_edit.setPlainText(self.task.description)
        description_edit.setReadOnly(True)
        description_edit.setMaximumHeight(150)
        form_layout.addRow("Description:", description_edit)

        # Assigned To
        assigned_user = next((user for user in self.users if user.id == self.task.assigned_to), None)
        form_layout.addRow("Assigned To:", QLabel(assigned_user.username if assigned_user else "No user assigned"))
        form_layout.addRow("Due Date:", QLabel(QDate.fromJulianDay(self.task.due_date).toString(Qt.ISODate)))
        form_layout.addRow("Priority:", QLabel(self.task.priority))
        form_layout.addRow("Status:", QLabel(self.task.status))
        form_layout.addRow("Created At:",
                           QLabel(datetime.fromtimestamp(self.task.created_at).strftime("%Y-%m-%d %H:%M:%S")))

        scroll_layout.addLayout(form_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)
