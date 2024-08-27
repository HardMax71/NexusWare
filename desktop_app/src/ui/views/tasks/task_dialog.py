from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QVBoxLayout, QDialog, QLineEdit, QComboBox, QDateEdit, QMessageBox, QTextEdit,
                               QDialogButtonBox, QFormLayout)

from public_api.api import TasksAPI
from public_api.shared_schemas import TaskCreate, TaskUpdate, TaskWithAssignee, UserSanitized, TaskPriority, TaskStatus


class TaskDialog(QDialog):
    def __init__(self, tasks_api: TasksAPI, users: list[UserSanitized],
                 task_data: TaskWithAssignee | None = None, parent=None):
        super().__init__(parent)
        self.tasks_api = tasks_api
        self.users = users
        self.task_data = task_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Task" if not self.task_data else "Edit Task")
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.task_type_input = QLineEdit()
        form_layout.addRow("Task Type:", self.task_type_input)

        self.description_input = QTextEdit()
        form_layout.addRow("Description:", self.description_input)

        self.assigned_to_input = QComboBox()
        for user in self.users:
            self.assigned_to_input.addItem(f"{user.username} ({user.email})", user.id)
        form_layout.addRow("Assigned To:", self.assigned_to_input)

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        form_layout.addRow("Due Date:", self.due_date_input)

        self.priority_input = QComboBox()
        self.priority_input.addItems([priority.value for priority in TaskPriority])
        form_layout.addRow("Priority:", self.priority_input)

        self.status_input = QComboBox()
        self.status_input.addItems([status.value for status in TaskStatus])
        form_layout.addRow("Status:", self.status_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        if self.task_data:
            self.populate_data()

    def populate_data(self):
        self.task_type_input.setText(self.task_data.task_type)
        self.description_input.setText(self.task_data.description)
        index = self.assigned_to_input.findData(self.task_data.assigned_to)
        if index >= 0:
            self.assigned_to_input.setCurrentIndex(index)
        self.due_date_input.setDate(QDate.fromJulianDay(self.task_data.due_date))
        self.priority_input.setCurrentText(self.task_data.priority.value)
        self.status_input.setCurrentText(self.task_data.status.value)

    def accept(self):
        task_type = self.task_type_input.text()
        description = self.description_input.toPlainText()
        assigned_to = self.assigned_to_input.currentData()
        due_date = self.due_date_input.date().toJulianDay()
        priority = self.priority_input.currentText()
        status = self.status_input.currentText()

        try:
            if self.task_data:
                task_update = TaskUpdate(
                    task_type=task_type,
                    description=description,
                    assigned_to=assigned_to,
                    due_date=due_date,
                    priority=priority,
                    status=status
                )
                updated_task = self.tasks_api.update_task(self.task_data.id, task_update)
                QMessageBox.information(self, "Success", f"Task {updated_task.id} updated successfully.")
            else:
                task_create = TaskCreate(
                    task_type=task_type,
                    description=description,
                    assigned_to=assigned_to,
                    due_date=due_date,
                    priority=priority,
                    status=status
                )
                new_task = self.tasks_api.create_task(task_create)
                QMessageBox.information(self, "Success", f"Task {new_task.id} created successfully.")

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
