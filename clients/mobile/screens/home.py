import flet as ft
import asyncio


class HomeScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.loading = True
        self.stats = None
        self.warehouse_stats = None

    def build(self):
        self.header = self.build_header()
        self.statistics = self.build_statistics()
        self.function_grid = self.build_function_grid()
        self.navigation_bar = self.build_navigation_bar()

        return ft.Column(
            [
                self.header,
                ft.Container(
                    content=ft.Column([
                        self.statistics,
                        self.function_grid
                    ]),
                    expand=True,
                    scroll=ft.ScrollMode.AUTO
                ),
                self.navigation_bar
            ],
            expand=True,
            spacing=0,
        )

    def build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="/assets/logo.png", width=40, height=40),
                    ft.Text("NexusWare", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.icons.SEARCH, on_click=self.search_clicked),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )

    def build_statistics(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Warehouse Statistics", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.create_stat_card("Total Items", "Loading..."),
                            self.create_stat_card("Pending Orders", "Loading..."),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
            ),
            padding=ft.padding.all(20),
            margin=ft.margin.all(10),
            bgcolor=ft.colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.SHADOW),
        )

    def build_function_grid(self):
        return ft.GridView(
            expand=True,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
            padding=20,
            controls=[
                self.create_function_card("Inventory", ft.icons.INVENTORY, lambda _: self.app.page.go("/inventory")),
                self.create_function_card("Picking", ft.icons.LIST, lambda _: self.app.page.go("/picking")),
                self.create_function_card("Receiving", ft.icons.MOVE_TO_INBOX,
                                          lambda _: self.app.page.go("/receiving")),
                self.create_function_card("Shipping", ft.icons.LOCAL_SHIPPING, lambda _: self.app.page.go("/shipping")),
                self.create_function_card("Tasks", ft.icons.ASSIGNMENT, lambda _: self.app.page.go("/tasks")),
                self.create_function_card("Reports", ft.icons.BAR_CHART, lambda _: self.app.page.go("/reports")),
            ]
        )

    def build_navigation_bar(self):
        return ft.Container(
            content=ft.NavigationBar(
                destinations=[
                    ft.NavigationDestination(icon=ft.icons.HOME, label="Home"),
                    ft.NavigationDestination(icon=ft.icons.INVENTORY, label="Inventory"),
                    ft.NavigationDestination(icon=ft.icons.SHOPPING_CART, label="Orders"),
                    ft.NavigationDestination(icon=ft.icons.PERSON, label="Profile"),
                ],
                on_change=self.navigation_change,
                selected_index=0,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )

    def create_function_card(self, title, icon, on_click):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=ft.colors.PRIMARY),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=150,
            height=150,
            bgcolor=ft.colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.SHADOW),
            on_click=on_click,
        )

    def create_stat_card(self, title, value):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=150,
            height=80,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
        )

    async def did_mount_async(self):
        await self.load_data()

    async def load_data(self):
        try:
            stats_task = self.app.client.get("/inventory/report")
            warehouse_stats_task = self.app.client.get("/warehouse/stats")

            stats_response, warehouse_stats_response = await asyncio.gather(stats_task, warehouse_stats_task)

            if stats_response.status_code == 200 and warehouse_stats_response.status_code == 200:
                self.stats = stats_response.json()
                self.warehouse_stats = warehouse_stats_response.json()
                await self.update_statistics()
            else:
                print("Failed to load data")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
        finally:
            self.loading = False
            await self.update_async()

    async def update_statistics(self):
        if self.stats and self.warehouse_stats:
            total_items = self.stats.get("total_items", "N/A")
            pending_orders = self.warehouse_stats.get("pending_orders", "N/A")

            self.statistics.content.controls[1].controls[0].content.controls[1].value = str(total_items)
            self.statistics.content.controls[1].controls[1].content.controls[1].value = str(pending_orders)

            await self.update_async()

    def search_clicked(self, e):
        print("Search clicked")
        # Implement search functionality

    def navigation_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.app.page.go("/")
        elif index == 1:
            self.app.page.go("/inventory")
        elif index == 2:
            self.app.page.go("/orders")
        elif index == 3:
            self.app.page.go("/profile")