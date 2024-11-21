# src/nexusware/screens/tasks/task_list.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..base import BaseScreen
from datetime import datetime, timezone


class TaskListScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.tasks_api = TasksAPI()
        self.tasks = []
        self.task_filter = TaskFilter()
        self.setup_task_list()

    def setup_task_list(self):
        main_box = toga.Box(style=Pack(
            direction=ROW,
            padding=20,
            flex=1
        ))

        # Left sidebar - Filters
        filter_box = self.create_filter_box()
        main_box.add(filter_box)

        # Right section - Task list and actions
        content_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 0, 20),
            flex=1
        ))

        # Actions bar
        actions_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0)
        ))

        create_btn = toga.Button(
            'Create Task',
            on_press=self.show_create_dialog,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        actions_box.add(create_btn)

        refresh_btn = toga.Button(
            'Refresh',
            on_press=self.refresh_tasks,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        actions_box.add(refresh_btn)

        content_box.add(actions_box)

        # Task list
        self.task_list = toga.Table(
            headings=['ID', 'Type', 'Description', 'Priority', 'Status', 'Due Date', 'Assignee'],
            style=Pack(flex=1)
        )
        self.task_list.on_select = self.on_task_select
        content_box.add(self.task_list)

        main_box.add(content_box)
        self.content.add(main_box)

        # Initial load
        self.refresh_tasks()

    def create_filter_box(self):
        filter_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 20, 0, 0),
            width=200
        ))

        title = toga.Label(
            'Filters',
            style=Pack(
                font_size=16,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        filter_box.add(title)

        # Type filter
        type_label = toga.Label('Task Type')
        filter_box.add(type_label)
        self.type_selector = toga.Selection(
            items=list(TaskType),
            on_select=self.apply_filters,
            style=Pack(padding=(0, 0, 10, 0))
        )
        filter_box.add(self.type_selector)

        # Priority filter
        priority_label = toga.Label('Priority')
        filter_box.add(priority_label)
        self.priority_selector = toga.Selection(
            items=list(TaskPriority),
            on_select=self.apply_filters,
            style=Pack(padding=(0, 0, 10, 0))
        )
        filter_box.add(self.priority_selector)

        # Status filter
        status_label = toga.Label('Status')
        filter_box.add(status_label)
        self.status_selector = toga.Selection(
            items=list(TaskStatus),
            on_select=self.apply_filters,
            style=Pack(padding=(0, 0, 10, 0))
        )
        filter_box.add(self.status_selector)

        # Due date range
        date_label = toga.Label('Due Date Range')
        filter_box.add(date_label)

        self.date_from = toga.DatePicker(
            on_change=self.apply_filters,
            style=Pack(padding=(0, 0, 5, 0))
        )
        filter_box.add(self.date_from)

        self.date_to = toga.DatePicker(
            on_change=self.apply_filters,
            style=Pack(padding=(0, 0, 10, 0))
        )
        filter_box.add(self.date_to)

        # Reset filters button
        reset_btn = toga.Button(
            'Reset Filters',
            on_press=self.reset_filters,
            style=Pack(padding=5)
        )
        filter_box.add(reset_btn)

        return filter_box

    async def refresh_tasks(self, widget=None):
        try:
            self.tasks = await self.tasks_api.get_tasks(filter_params=self.task_filter)
            self.update_task_list()
        except Exception as e:
            self.show_error(str(e))

    def update_task_list(self):
        data = []
        for task in self.tasks:
            data.append([
                str(task.id),
                task.task_type.value,
                task.description[:50] + '...' if len(task.description) > 50 else task.description,
                task.priority.value,
                task.status.value,
                self.format_date(task.due_date),
                task.assigned_user.username if task.assigned_user else 'Unassigned'
            ])
        self.task_list.data = data

    def apply_filters(self, widget=None):
        self.task_filter = TaskFilter(
            task_type=self.type_selector.value if self.type_selector.value else None,
            priority=self.priority_selector.value if self.priority_selector.value else None,
            status=self.status_selector.value if self.status_selector.value else None,
            due_date_from=int(self.date_from.value.timestamp()) if self.date_from.value else None,
            due_date_to=int(self.date_to.value.timestamp()) if self.date_to.value else None
        )
        self.refresh_tasks()

    def reset_filters(self, widget):
        self.type_selector.value = None
        self.priority_selector.value = None
        self.status_selector.value = None
        self.date_from.value = None
        self.date_to.value = None
        self.task_filter = TaskFilter()
        self.refresh_tasks()

    def show_create_dialog(self, widget):
        self.window.app.navigate_to('/tasks/create')

    def on_task_select(self, widget, row):
        if row is not None:
            task_id = int(self.task_list.data[row][0])
            self.window.app.navigate_to(f'/tasks/{task_id}')

    def format_date(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
