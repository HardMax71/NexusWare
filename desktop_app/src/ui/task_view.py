from datetime import datetime
from typing import List, Optional

from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QComboBox, QDateEdit, QStackedWidget, QLabel,
                               QMessageBox, QTextEdit, QDialogButtonBox, QFormLayout, QPushButton, QScrollArea)

from desktop_app.src.ui.components import StyledButton
from public_api.api import APIClient, TasksAPI, UsersAPI
from public_api.shared_schemas import TaskCreate, TaskUpdate, TaskWithAssignee, TaskFilter, UserSanitizedWithRole
from public_api.shared_schemas.task import TaskStatus, TaskPriority


class TaskView(QWidget):
    task_updated = Signal()

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.tasks_api = TasksAPI(api_client)
        self.users_api = UsersAPI(api_client)
        self.users = self.users_api.get_users()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Stacked Widget for different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Task List View
        self.task_list_widget = self.create_task_list_widget()
        self.stacked_widget.addWidget(self.task_list_widget)

        # Task Statistics View
        self.task_stats_widget = self.create_task_stats_widget()
        self.stacked_widget.addWidget(self.task_stats_widget)

        # Switch View Button
        self.switch_view_button = StyledButton("Switch to Statistics")
        self.switch_view_button.clicked.connect(self.toggle_view)
        layout.addWidget(self.switch_view_button)

        # Floating Action Button for adding new tasks
        self.fab = StyledButton("+")
        self.fab.clicked.connect(self.add_task)
        layout.addWidget(self.fab)

        self.refresh_tasks()

    def create_task_list_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Filters
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.textChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.search_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["All"] + [status.value for status in TaskStatus])
        self.status_combo.currentTextChanged.connect(self.refresh_tasks)
        self.status_combo.setToolTip("Filter by task status")
        filter_layout.addWidget(self.status_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All"] + [priority.value for priority in TaskPriority])
        self.priority_combo.currentTextChanged.connect(self.refresh_tasks)
        self.priority_combo.setToolTip("Filter by task priority")
        filter_layout.addWidget(self.priority_combo)

        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_tasks)
        filter_layout.addWidget(self.refresh_button)

        layout.addLayout(filter_layout)

        # Task Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(
            ["Type", "Description", "Assigned To", "Due Date", "Priority", "Actions"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.task_table)

        return widget

    def create_task_stats_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Task Statistics
        stats_layout = QHBoxLayout()
        self.total_tasks_label = QLabel("Total Tasks: 0")
        self.completed_tasks_label = QLabel("Completed Tasks: 0")
        self.overdue_tasks_label = QLabel("Overdue Tasks: 0")
        stats_layout.addWidget(self.total_tasks_label)
        stats_layout.addWidget(self.completed_tasks_label)
        stats_layout.addWidget(self.overdue_tasks_label)
        layout.addLayout(stats_layout)

        # Task Distribution Chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

        return widget

    def toggle_view(self):
        current_index = self.stacked_widget.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.stacked_widget.setCurrentIndex(new_index)
        self.switch_view_button.setText("Switch to List" if new_index == 1 else "Switch to Statistics")
        if new_index == 1:
            self.refresh_statistics()

    def refresh_tasks(self):
        status = self.status_combo.currentText()
        priority = self.priority_combo.currentText()
        filter_params = TaskFilter(
            status=TaskStatus(status) if status != "All" else None,
            priority=TaskPriority(priority) if priority != "All" else None
        )
        tasks = self.tasks_api.get_tasks(filter_params=filter_params)
        self.update_task_table(tasks)

    def update_task_table(self, tasks: List[TaskWithAssignee]):
        self.task_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(task.task_type.value))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.description))
            assigned_user = next((user for user in self.users if user.id == task.assigned_to), None)
            self.task_table.setItem(row, 2,
                                    QTableWidgetItem(assigned_user.username if assigned_user else "No user assigned"))
            self.task_table.setItem(row, 3, QTableWidgetItem(QDate.fromJulianDay(task.due_date).toString(Qt.ISODate)))
            self.task_table.setItem(row, 4, QTableWidgetItem(task.priority.value))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View")
            view_button.clicked.connect(lambda _, t=task: self.view_task(t))
            actions_layout.addWidget(view_button)

            edit_button = StyledButton("Edit")
            edit_button.clicked.connect(lambda _, t=task: self.edit_task(t))
            actions_layout.addWidget(edit_button)

            delete_button = StyledButton("Delete")
            delete_button.clicked.connect(lambda _, t=task: self.delete_task(t))
            actions_layout.addWidget(delete_button)

            self.task_table.setCellWidget(row, 5, actions_widget)

    def view_task(self, task: TaskWithAssignee):
        dialog = TaskDetailsDialog(task, self.users, parent=self)
        dialog.exec_()

    def filter_tasks(self):
        search_text = self.search_input.text().lower()
        for row in range(self.task_table.rowCount()):
            row_match = False
            for col in range(self.task_table.columnCount() - 1):  # Exclude the Actions column
                item = self.task_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_match = True
                    break
            self.task_table.setRowHidden(row, not row_match)

    def add_task(self):
        dialog = TaskDialog(self.tasks_api, self.users, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_tasks()
            self.task_updated.emit()

    def edit_task(self, task: TaskWithAssignee):
        dialog = TaskDialog(self.tasks_api, self.users, task_data=task, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_tasks()
            self.task_updated.emit()

    def delete_task(self, task: TaskWithAssignee):
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete task {task.id}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.tasks_api.delete_task(task.id)
                self.refresh_tasks()
                self.task_updated.emit()
                QMessageBox.information(self, "Success", "Task deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete task: {str(e)}")

    def refresh_statistics(self):
        stats = self.tasks_api.get_task_statistics()
        self.total_tasks_label.setText(f"Total Tasks: {stats.total_tasks}")
        self.completed_tasks_label.setText(f"Completed Tasks: {stats.completed_tasks}")
        self.overdue_tasks_label.setText(f"Overdue Tasks: {stats.overdue_tasks}")

        # Update chart
        series = QPieSeries()
        series.append("Completed", stats.completed_tasks)
        series.append("Overdue", stats.overdue_tasks)
        series.append("Other", stats.total_tasks - stats.completed_tasks - stats.overdue_tasks)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Task Distribution")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.chart_view.setChart(chart)


class TaskDialog(QDialog):
    def __init__(self, tasks_api: TasksAPI, users: List[UserSanitizedWithRole],
                 task_data: Optional[TaskWithAssignee] = None, parent=None):
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


class TaskDetailsDialog(QDialog):
    def __init__(self, task: TaskWithAssignee, users: List[UserSanitizedWithRole], parent=None):
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