# /clients/mobile/screens/reports.py

import flet as ft

class ReportsScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.report_grid = ft.GridView(
            expand=1,
            runs_count=2,
            max_extent=200,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
        )

        return ft.Column(
            [
                ft.AppBar(
                    title=ft.Text("Reports"),
                    actions=[
                        ft.IconButton(ft.icons.CALENDAR_TODAY, on_click=self.show_date_picker),
                    ],
                ),
                self.report_grid,
            ]
        )

    async def load_reports(self):
        report_types = [
            ("Inventory", ft.icons.INVENTORY, self.show_inventory_report),
            ("Orders", ft.icons.SHOPPING_CART, self.show_order_report),
            ("Performance", ft.icons.TRENDING_UP, self.show_performance_report),
            ("KPI Dashboard", ft.icons.DASHBOARD, self.show_kpi_dashboard),
        ]

        self.report_grid.controls = [
            self.create_report_card(title, icon, on_click) for title, icon, on_click in report_types
        ]
        self.update()

    def create_report_card(self, title, icon, on_click):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=50),
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            ),
            on_click=on_click,
        )

    def show_date_picker(self, e):
        # Implement date picker logic
        pass

    async def show_inventory_report(self, e):
        response = await self.app.client.get("/reports/inventory-summary")
        if response.status_code == 200:
            report_data = response.json()
            # Implement logic to display inventory report
            pass

    async def show_order_report(self, e):
        response = await self.app.client.get("/reports/order-summary")
        if response.status_code == 200:
            report_data = response.json()
            # Implement logic to display order report
            pass

    async def show_performance_report(self, e):
        response = await self.app.client.get("/reports/warehouse-performance")
        if response.status_code == 200:
            report_data = response.json()
            # Implement logic to display performance report
            pass

    async def show_kpi_dashboard(self, e):
        response = await self.app.client.get("/reports/kpi-dashboard")
        if response.status_code == 200:
            report_data = response.json()
            # Implement logic to display KPI dashboard
            pass