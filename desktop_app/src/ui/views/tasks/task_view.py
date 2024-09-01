from PySide6.QtCharts import QChart, QChartView, QPieSeries, QValueAxis, QBarCategoryAxis, QBarSeries, QBarSet
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QLineEdit, QComboBox, QStackedWidget, QLabel,
                               QMessageBox, QScrollArea)

from public_api.api import APIClient, TasksAPI, UsersAPI
from public_api.shared_schemas import TaskWithAssignee, TaskFilter, TaskStatus, TaskPriority
from public_api.shared_schemas.task import TaskType
from src.ui.components import StyledButton
from src.ui.components.icon_path import IconPath
from src.ui.views.tasks.task_dialog import TaskDialog
from src.ui.views.tasks.tasks_details_dialog import TaskDetailsDialog


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
        self.fab = StyledButton("+", icon_path=IconPath.PLUS)
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
        self.status_combo.addItems(["All"] + [status for status in TaskStatus])
        self.status_combo.currentTextChanged.connect(self.refresh_tasks)
        self.status_combo.setToolTip("Filter by task status")
        filter_layout.addWidget(self.status_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All"] + [priority for priority in TaskPriority])
        self.priority_combo.currentTextChanged.connect(self.refresh_tasks)
        self.priority_combo.setToolTip("Filter by task priority")
        filter_layout.addWidget(self.priority_combo)

        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
        self.refresh_button.clicked.connect(self.refresh_tasks)
        filter_layout.addWidget(self.refresh_button)

        layout.addLayout(filter_layout)

        # Task Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels(
            ["Type", "Description", "Assigned To", "Due Date", "Priority", "Status", "Actions"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.task_table)

        return widget

    def create_task_stats_widget(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Task Statistics
        stats_layout = QHBoxLayout()
        self.total_tasks_label = QLabel("Total Tasks: 0")
        self.completed_tasks_label = QLabel("Completed Tasks: 0")
        self.overdue_tasks_label = QLabel("Overdue Tasks: 0")
        self.high_priority_tasks_label = QLabel("High Priority Tasks: 0")
        stats_layout.addWidget(self.total_tasks_label)
        stats_layout.addWidget(self.completed_tasks_label)
        stats_layout.addWidget(self.overdue_tasks_label)
        stats_layout.addWidget(self.high_priority_tasks_label)
        layout.addLayout(stats_layout)

        # Task Distribution Pie Chart
        layout.addWidget(QLabel("Task Distribution"))
        self.distribution_chart_view = QChartView()
        self.distribution_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.distribution_chart_view.setMinimumHeight(300)
        layout.addWidget(self.distribution_chart_view)

        # Task Type Bar Chart
        layout.addWidget(QLabel("Task Types"))
        self.task_type_chart_view = QChartView()
        self.task_type_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.task_type_chart_view.setMinimumHeight(300)
        layout.addWidget(self.task_type_chart_view)

        # Task Priority Bar Chart
        layout.addWidget(QLabel("Task Priorities"))
        self.task_priority_chart_view = QChartView()
        self.task_priority_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.task_priority_chart_view.setMinimumHeight(300)
        layout.addWidget(self.task_priority_chart_view)

        scroll_area.setWidget(widget)
        return scroll_area

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

    def update_task_table(self, tasks: list[TaskWithAssignee]):
        self.task_table.setRowCount(len(tasks))
        self.task_table.setColumnCount(7)  # Increased column count to 7
        self.task_table.setHorizontalHeaderLabels(
            ["Type", "Description", "Assigned To", "Due Date", "Priority", "Status", "Actions"])

        for row, task in enumerate(tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(task.task_type.value))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.description))
            assigned_user = next((user for user in self.users if user.id == task.assigned_to), None)
            self.task_table.setItem(row, 2,
                                    QTableWidgetItem(assigned_user.username if assigned_user else "No user assigned"))
            self.task_table.setItem(row, 3,
                                    QTableWidgetItem(
                                        QDate.fromJulianDay(task.due_date).toString(Qt.DateFormat.ISODate)))
            self.task_table.setItem(row, 4, QTableWidgetItem(task.priority.value))
            self.task_table.setItem(row, 5, QTableWidgetItem(task.status.value))  # New column for status

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(2)

            view_button = StyledButton("View", icon_path=IconPath.VIEW)
            view_button.clicked.connect(lambda _, t=task: self.view_task(t))
            actions_layout.addWidget(view_button)

            edit_button = StyledButton("Edit", icon_path=IconPath.EDIT)
            edit_button.clicked.connect(lambda _, t=task: self.edit_task(t))
            actions_layout.addWidget(edit_button)

            delete_button = StyledButton("Delete", icon_path=IconPath.DELETE)
            delete_button.clicked.connect(lambda _, t=task: self.delete_task(t))
            actions_layout.addWidget(delete_button)

            self.task_table.setCellWidget(row, 6, actions_widget)

        # Adjust column widths
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Type
        self.task_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Due Date
        self.task_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Priority
        self.task_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        self.task_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Actions

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
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            self.refresh_tasks()
            self.task_updated.emit()

    def edit_task(self, task: TaskWithAssignee):
        dialog = TaskDialog(self.tasks_api, self.users, task_data=task, parent=self)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
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
        self.high_priority_tasks_label.setText(f"High Priority Tasks: {stats.high_priority_tasks}")

        self.tasks_api.get_tasks()
        self.update_distribution_chart()
        self.update_task_type_chart()
        self.update_task_priority_chart()

    def update_distribution_chart(self):
        series = QPieSeries()

        tasks = self.tasks_api.get_tasks()
        status_counts = {status: 0 for status in TaskStatus}
        for task in tasks:
            status_counts[task.status] += 1

        for status, count in status_counts.items():
            series.append(status.value, count)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Task Distribution")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        self.distribution_chart_view.setChart(chart)

    def update_task_type_chart(self):
        tasks = self.tasks_api.get_tasks()
        type_counts = {task_type: 0 for task_type in TaskType}
        for task in tasks:
            type_counts[task.task_type] += 1

        series = QBarSeries()
        bar_set = QBarSet("Task Types")
        for count in type_counts.values():
            bar_set.append(count)
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Task Types")

        axis_x = QBarCategoryAxis()
        axis_x.append([task_type for task_type in TaskType])
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        self.task_type_chart_view.setChart(chart)

    def update_task_priority_chart(self):
        tasks = self.tasks_api.get_tasks()
        priority_counts = {priority: 0 for priority in TaskPriority}
        for task in tasks:
            priority_counts[task.priority] += 1

        series = QBarSeries()
        bar_set = QBarSet("Task Priorities")
        for count in priority_counts.values():
            bar_set.append(count)
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Task Priorities")

        axis_x = QBarCategoryAxis()
        axis_x.append([priority for priority in TaskPriority])
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        self.task_priority_chart_view.setChart(chart)
