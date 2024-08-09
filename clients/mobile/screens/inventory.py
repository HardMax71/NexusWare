# /clients/mobile/screens/inventory.py

import flet as ft

class InventoryScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.search_bar = ft.TextField(
            label="Search inventory",
            prefix_icon=ft.icons.SEARCH,
            on_change=self.search_inventory
        )
        self.inventory_list = ft.ListView(expand=1, spacing=10, padding=20)

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Inventory"), actions=[
                    ft.IconButton(ft.icons.FILTER_LIST),
                    ft.IconButton(ft.icons.SORT),
                ]),
                self.search_bar,
                self.inventory_list,
                ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_inventory_item),
            ]
        )

    async def load_inventory(self):
        response = await self.app.client.get("/inventory")
        if response.status_code == 200:
            inventory_data = response.json()
            self.inventory_list.controls = [
                self.create_inventory_item(item) for item in inventory_data
            ]
            self.update()

    def create_inventory_item(self, item):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Image(src=item["image_url"], width=40, height=40),
                            title=ft.Text(item["name"]),
                            subtitle=ft.Text(f"SKU: {item['sku']}"),
                            trailing=ft.Text(f"Qty: {item['quantity']}"),
                        ),
                    ]
                ),
                padding=10,
            ),
            on_click=lambda _: self.app.page.go(f"/product/{item['id']}"),
        )

    def search_inventory(self, e):
        # Implement inventory search logic here
        pass

    def add_inventory_item(self, e):
        # Implement add new inventory item logic here
        pass