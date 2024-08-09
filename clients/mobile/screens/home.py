import flet as ft

class HomeScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        # GridView configuration
        self.grid = ft.GridView(
            expand=True,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
            padding=20,
        )

        # Build the home screen layout
        layout = ft.Column(
            [
                self.build_header(),
                self.build_statistics(),
                self.build_navigation_bar(),
            ],
            expand=True,
            spacing=0,
        )

        return layout

    def build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="/assets/logo.png", width=40, height=40),
                    ft.Text("NexusWare", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.icons.SEARCH),
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
                            self.create_stat_card("Total Items", "1000"),
                            self.create_stat_card("Pending Orders", "50"),
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

    def build_navigation_bar(self):
        return ft.Container(
            content=ft.NavigationBar(
                destinations=[
                    ft.NavigationDestination(icon=ft.icons.HOME, label="Home"),
                    ft.NavigationDestination(icon=ft.icons.INVENTORY, label="Inventory"),
                    ft.NavigationDestination(icon=ft.icons.SHOPPING_CART, label="Orders"),
                    ft.NavigationDestination(icon=ft.icons.PERSON, label="Profile"),
                ],
                height=56,
            ),
            margin=ft.margin.all(0),
            padding=ft.padding.all(0),
        )

    async def did_mount_async(self):
        await self.load_data()

    async def load_data(self):
        try:
            response = await self.app.client.get("/warehouse/stats")
            if response.status_code == 200:
                stats = response.json()
                self.grid.controls = [
                    self.create_function_card("Inventory", ft.icons.INVENTORY, lambda _: self.app.page.go("/inventory")),
                    self.create_function_card("Picking", ft.icons.LIST, lambda _: self.app.page.go("/picking")),
                    self.create_function_card("Receiving", ft.icons.MOVE_TO_INBOX, lambda _: self.app.page.go("/receiving")),
                    self.create_function_card("Shipping", ft.icons.LOCAL_SHIPPING, lambda _: self.app.page.go("/shipping")),
                    self.create_function_card("Tasks", ft.icons.ASSIGNMENT, lambda _: self.app.page.go("/tasks")),
                    self.create_function_card("Reports", ft.icons.BAR_CHART, lambda _: self.app.page.go("/reports")),
                ]
            else:
                self.grid.controls = [ft.Text("Failed to load data", color=ft.colors.RED)]
        except Exception as e:
            self.grid.controls = [ft.Text(f"Error: {str(e)}", color=ft.colors.RED)]
        finally:
            await self.update_async()

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
