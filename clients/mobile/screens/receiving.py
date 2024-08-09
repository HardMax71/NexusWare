import flet as ft

class ReceivingScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.receipt_list = ft.ListView(expand=1, spacing=10, padding=20)

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Receiving")),
                ft.ElevatedButton(
                    "Scan Barcode",
                    icon=ft.icons.QR_CODE_SCANNER,
                    on_click=self.open_barcode_scanner
                ),
                self.receipt_list,
            ]
        )

    async def load_receipts(self):
        response = await self.app.client.get("/warehouse/receipts")
        if response.status_code == 200:
            receipt_data = response.json()
            self.receipt_list.controls = [
                self.create_receipt_item(item) for item in receipt_data
            ]
            self.update()

    def create_receipt_item(self, item):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(f"Receipt #{item['receipt_number']}"),
                            subtitle=ft.Text(f"Supplier: {item['supplier_name']}"),
                            trailing=ft.Text(f"Expected: {item['expected_date']}"),
                        ),
                    ]
                ),
                padding=10,
            ),
            on_click=lambda _: self.open_receipt_details(item['id']),
        )

    def open_barcode_scanner(self, e):
        self.app.barcode_scanner.open_scanner(self.process_scanned_item)

    def process_scanned_item(self, barcode):
        # Implement logic to process scanned item
        pass

    def open_receipt_details(self, receipt_id):
        # Implement logic to open receipt details
        pass