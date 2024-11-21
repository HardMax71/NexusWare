# src/nexusware/screens/tasks/task_details.py
from datetime import datetime

import toga

from mobile_app.src.nexusware.screens.base import BaseScreen
from public_api.api import TasksAPI


class TaskDetailsScreen(BaseScreen):
    def __init__(self, task_id: int):
        super().__init__()
        self.tasks_api = TasksAPI()
        self.task_id = task_id
        self.task = None
        self.comments = []
        self.setup_task_details()

    async def setup_task_details(self):
        try:
            self.task = await self.tasks_api.get_task(self.task_id)
            self.comments = await self.tasks_api.get_task_comments(self.task_id)
            self.render_task_details()
        except Exception as e:
            self.show_error(str(e))

    def render_task_details(self):
        main_box = toga.Box(style=Pack(
            direction=ROW,
            padding=20,
            flex=1
        ))

        # Left section - Task details
        details_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 20, 0, 0),
            flex=1
        ))

        # Header with actions
        header_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 20, 0)
        ))

        title = toga.Label(
            f'Task #{self.task.id}',
            style=Pack(
                font_size=24,
                font_weight='bold',
                flex=1
            )
        )
        header_box.add(title)

        edit_btn = toga.Button(
            'Edit',
            on_press=self.show_edit_dialog,
            style=Pack(padding=5)
        )
        header_box.add(edit_btn)

        delete_btn = toga.Button(
            'Delete',
            on_press=self.confirm_delete,
            style=Pack(
                padding=5,
                background_color=self.theme['error']
            )
        )
        header_box.add(delete_btn)

        details_box.add(header_box)

        # Task details
        fields = [
            ('Type', self.task.task_type.value),
            ('Description', self.task.description),
            ('Priority', self.task.priority.value),
            ('Status', self.task.status.value),
            ('Assigned To', self.task.assigned_user.username if self.task.assigned_user else 'Unassigned'),
            ('Due Date', self.format_date(self.task.due_date)),
            ('Created At', self.format_date(self.task.created_at))
        ]

        for label, value in fields:
            field_box = toga.Box(style=Pack(
                direction=ROW,
                padding=(0, 0, 10, 0)
            ))

            label_widget = toga.Label(
                f'{label}:',
                style=Pack(
                    font_weight='bold',
                    width=100
                )
            )
            field_box.add(label_widget)

            value_widget = toga.Label(str(value))
            field_box.add(value_widget)

            details_box.add(field_box)

        main_box.add(details_box)

        # Right section - Comments
        comments_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 0, 20),
            flex=1
        ))

        comments_title = toga.Label(
            'Comments',
            style=Pack(
                font_size=18,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        comments_box.add(comments_title)

        # Comment list
        self.comments_list = toga.Table(
            headings=['User', 'Comment', 'Date'],
            style=Pack(flex=1)
        )
        self.update_comments_list()
        comments_box.add(self.comments_list)

        # Add comment
        comment_input = toga.TextInput(
            placeholder='Add a comment...',
            style=Pack(padding=(10, 0))
        )
        comments_box.add(comment_input)

        add_comment_btn = toga.Button(
            'Add Comment',
            on_press=lambda w: self.add_comment(comment_input.value),
            style=Pack(
                padding=(10, 0),
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        comments_box.add(add_comment_btn)

        main_box.add(comments_box)
        self.content.add(main_box)

    def update_comments_list(self):
        data = []
        for comment in self.comments:
            data.append([
                comment.user.username,
                comment.comment,
                self.format_date(comment.created_at)
            ])
        self.comments_list.data = data

    async def add_comment(self, comment_text):
        if not comment_text:
            return

        try:
            comment = await self.tasks_api.add_task_comment(
                self.task_id,
                TaskCommentCreate(comment=comment_text)
            )
            self.comments.append(comment)
            self.update_comments_list()
        except Exception as e:
            self.show_error(str(e))

    def show_edit_dialog(self, widget):
        self.window.app.navigate_to(f'/tasks/{self.task_id}/edit')

    async def confirm_delete(self, widget):
        dialog = toga.Dialog(
            title='Confirm Delete',
            content=toga.Label('Are you sure you want to delete this task?'),
            on_result=self.handle_delete_confirmation
        )
        dialog.show()

    async def handle_delete_confirmation(self, dialog, result):
        if result:
            try:
                await self.tasks_api.delete_task(self.task_id)
                self.window.app.navigate_to('/tasks')
            except Exception as e:
                self.show_error(str(e))

    def format_date(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')