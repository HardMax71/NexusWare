# /clients/mobile/screens/picking.py

import flet as ft

class PickingScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.pick_list = ft.ListView(expand=1, spacing=10, padding=20)

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Picking")),
                self.pick_list,
            ]
        )

    async def load_pick_lists(self):
        response = await self.app.client.get("/warehouse/pick-lists")
        if response.status_code == 200:
            pick_list_data = response.json()
            self.pick_list.controls = [
                self.create_pick_list_item(item) for item in pick_list_data
            ]
            self.update()

    def create_pick_list_item(self, item):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(f"Order #{item['order_number']}"),
                            subtitle=ft.Text(f"Items: {item['item_count']}"),
                            trailing=ft.Text(item['status'], color=self.get_status_color(item['status'])),
                        ),
                        ft.LinearProgressIndicator(value=item['completion_percentage'] / 100),
                    ]
                ),
                padding=10,
            ),
            on_click=lambda _: self.start_picking(item['id']),
        )

    def get_status_color(self, status):
        colors = {
            "Not Started": ft.colors.GREY,
            "In Progress": ft.colors.BLUE,
            "Completed": ft.colors.GREEN,
        }
        return colors.get(status, ft.colors.GREY)

    def start_picking(self, pick_list_id):
        # Implement start picking logic here
        pass