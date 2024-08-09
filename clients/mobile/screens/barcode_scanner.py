# /clients/mobile/screens/barcode_scanner.py

import flet as ft


class BarcodeScannerOverlay(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.callback = None

    def build(self):
        self.scanner_view = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Scan Barcode", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        width=300,
                        height=300,
                        border=ft.border.all(2, ft.colors.PRIMARY),
                        border_radius=10,
                        alignment=ft.alignment.center,
                        content=ft.Text("Camera Viewfinder"),
                    ),
                    ft.ElevatedButton("Cancel", on_click=self.close_scanner),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.colors.BLACK54,
            alignment=ft.alignment.center,
        )
        return self.scanner_view

    def open_scanner(self, callback):
        self.callback = callback
        self.scanner_view.visible = True
        self.update()

    def close_scanner(self, e):
        self.scanner_view.visible = False
        self.update()

    def on_barcode_scanned(self, barcode):
        if self.callback:
            self.callback(barcode)
        self.close_scanner(None)
