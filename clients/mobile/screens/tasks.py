# /clients/mobile/screens/tasks.py

import flet as ft


class TasksScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.task_board = ft.Row(
            [
                self.create_task_column("To Do", ft.colors.BLUE),
                self.create_task_column("In Progress", ft.colors.ORANGE),
                self.create_task_column("Completed", ft.colors.GREEN),
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
        )

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Tasks")),
                self.task_board,
                ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.create_new_task),
            ]
        )

    def create_task_column(self, title, color):
        return ft.Container(
            ft.Column(
                [
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=1, bgcolor=color),
                    ft.ListView(expand=1, spacing=10, padding=20),
                ],
                tight=True,
            ),
            width=300,
            bgcolor=ft.colors.BACKGROUND,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            padding=10,
        )

    async def load_tasks(self):
        response = await self.app.client.get("/tasks")
        if response.status_code == 200:
            task_data = response.json()
            for task in task_data:
                self.add_task_to_column(task)
            self.update()

    def add_task_to_column(self, task):
        column = self.task_board.controls[self.get_column_index(task['status'])]
        column.content.controls[-1].controls.append(self.create_task_card(task))

    def get_column_index(self, status):
        status_map = {"To Do": 0, "In Progress": 1, "Completed": 2}
        return status_map.get(status, 0)

    def create_task_card(self, task):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(task['title']),
                            subtitle=ft.Text(task['description']),
                        ),
                        ft.Text(f"Due: {task['due_date']}"),
                        ft.Container(
                            bgcolor=self.get_priority_color(task['priority']),
                            padding=5,
                            border_radius=5,
                            content=ft.Text(task['priority'], color=ft.colors.WHITE),
                        ),
                    ]
                ),
                padding=10,
            ),
            draggable=True,
        )

    def get_priority_color(self, priority):
        colors = {
            "Low": ft.colors.GREEN,
            "Medium": ft.colors.ORANGE,
            "High": ft.colors.RED,
        }
        return colors.get(priority, ft.colors.GREY)

    def create_new_task(self, e):
        # Implement logic to create a new task
        pass
