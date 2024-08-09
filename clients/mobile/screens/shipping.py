# /clients/mobile/screens/shipping.py

import flet as ft

class ShippingScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.shipment_list = ft.ListView(expand=1, spacing=10, padding=20)

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Shipping")),
                self.shipment_list,
            ]
        )

    async def load_shipments(self):
        response = await self.app.client.get("/warehouse/shipments")
        if response.status_code == 200:
            shipment_data = response.json()
            self.shipment_list.controls = [
                self.create_shipment_item(item) for item in shipment_data
            ]
            self.update()

    def create_shipment_item(self, item):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(f"Order #{item['order_number']}"),
                            subtitle=ft.Text(f"Customer: {item['customer_name']}"),
                            trailing=ft.Text(item['shipping_method']),
                        ),
                        ft.ElevatedButton(
                            "Generate Shipping Label",
                            on_click=lambda _: self.generate_shipping_label(item['id'])
                        ),
                    ]
                ),
                padding=10,
            ),
        )

    def generate_shipping_label(self, shipment_id):
        # Implement logic to generate shipping label
        pass