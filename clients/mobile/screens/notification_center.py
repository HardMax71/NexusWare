import flet as ft

class NotificationCenter(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.notification_list = ft.ListView(expand=1, spacing=10, padding=20)

        return ft.Column(
            [
                ft.AppBar(
                    title=ft.Text("Notifications"),
                    actions=[
                        ft.IconButton(ft.icons.FILTER_LIST, on_click=self.filter_notifications),
                    ],
                ),
                self.notification_list,
            ]
        )

    async def load_notifications(self):
        response = await self.app.client.get("/users/me/notifications")
        if response.status_code == 200:
            notification_data = response.json()
            self.notification_list.controls = [
                self.create_notification_item(item) for item in notification_data
            ]
            self.update()

    def create_notification_item(self, item):
        return ft.Dismissible(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(self.get_notification_icon(item['type'])),
                                title=ft.Text(item['title']),
                                subtitle=ft.Text(item['description']),
                            ),
                            ft.Text(item['timestamp'], size=12, color=ft.colors.GREY),
                        ]
                    ),
                    padding=10,
                )
            ),
            dismiss_direction=ft.DismissDirection.END_TO_START,
            background=ft.Container(
                content=ft.Icon(ft.icons.DELETE, color=ft.colors.RED),
                alignment=ft.alignment.center_right,
                padding=15,
            ),
            on_dismiss=lambda _: self.dismiss_notification(item['id']),
        )

    def get_notification_icon(self, notification_type):
        icons = {
            "info": ft.icons.INFO,
            "warning": ft.icons.WARNING,
            "error": ft.icons.ERROR,
            "success": ft.icons.CHECK_CIRCLE,
        }
        return icons.get(notification_type, ft.icons.NOTIFICATIONS)

    async def dismiss_notification(self, notification_id):
        response = await self.app.client.put(f"/users/me/notifications/{notification_id}", json={"dismissed": True})
        if response.status_code == 200:
            # Notification dismissed successfully
            pass

    def filter_notifications(self, e):
        # Implement notification filtering logic
        pass
    