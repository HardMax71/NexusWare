# /clients/mobile/screens/product_details.py

import flet as ft

class ProductDetailsScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.product_image = ft.Image(src="", width=300, height=200)
        self.product_name = ft.Text("", size=24, weight=ft.FontWeight.BOLD)
        self.product_sku = ft.Text("", size=16)
        self.product_quantity = ft.Text("", size=18)

        self.adjust_quantity_button = ft.ElevatedButton("Adjust Quantity", on_click=self.adjust_quantity)
        self.move_item_button = ft.ElevatedButton("Move Item", on_click=self.move_item)

        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Details"),
                ft.Tab(text="History"),
                ft.Tab(text="Related Items"),
            ],
        )

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Product Details"), actions=[
                    ft.IconButton(ft.icons.EDIT),
                ]),
                self.product_image,
                self.product_name,
                self.product_sku,
                self.product_quantity,
                ft.Row([self.adjust_quantity_button, self.move_item_button]),
                self.tabs,
            ]
        )

    async def load_product(self, product_id):
        response = await self.app.client.get(f"/inventory/{product_id}")
        if response.status_code == 200:
            product_data = response.json()
            self.product_image.src = product_data["image_url"]
            self.product_name.value = product_data["name"]
            self.product_sku.value = f"SKU: {product_data['sku']}"
            self.product_quantity.value = f"Quantity: {product_data['quantity']}"
        self.update()

    def adjust_quantity(self, e):
        # TODO: Implement adjust quantity logic here
        pass

    def move_item(self, e):
        # TODO: Implement move item logic here
        pass