import flet as ft
from flet import (
    Column,
    Container,
    Row,
    Text,
    Icon,
    IconButton,
    Card,
    GridView,
    AppBar,
    colors,
    icons,
    padding,
    border_radius,
)
from flet_core import Image

from clients.mobile.utils.api_helper import api_call


class HomeScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        self.app_bar = AppBar(
            leading=Image(src="logo.png", width=40, height=40),
            leading_width=40,
            title=Text("NexusWare", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=colors.BLUE_600,
            actions=[
                IconButton(icon=icons.SEARCH, icon_color=colors.WHITE),
            ],
        )

        self.stats_row = Row(
            controls=[
                self.create_stat_card("Total Items", "0"),
                self.create_stat_card("Pending Orders", "0"),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.function_grid = GridView(
            expand=True,
            runs_count=2,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
        )

        self.bottom_nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=icons.HOME, label="Home"),
                ft.NavigationDestination(icon=icons.INVENTORY_2, label="Inventory"),
                ft.NavigationDestination(icon=icons.SHOPPING_CART, label="Orders"),
                ft.NavigationDestination(icon=icons.PERSON, label="Profile"),
            ],
            on_change=self.bottom_nav_change,
        )

    def build(self):
        return Column(
            controls=[
                self.app_bar,
                Container(
                    expand=True,
                    bgcolor=colors.BLUE_50,
                    content=Column(
                        controls=[
                            Container(
                                padding=padding.all(20),
                                content=Column(
                                    controls=[
                                        self.stats_row,
                                        Container(height=20),
                                        self.function_grid,
                                    ],
                                    expand=True,
                                ),
                            ),
                        ],
                        expand=True,
                    ),
                ),
                self.bottom_nav_bar,
            ],
            expand=True,
        )

    def did_mount(self):
        self.load_function_cards()
        self.app.page.run_task(self.fetch_warehouse_stats)
        self.update()

    async def fetch_warehouse_stats(self):
        response = await api_call(self.app, self.app.client.get, "/warehouse/stats")
        if response:
            self.stats_row.controls[0].content.content.controls[1].value = str(response.get("total_items", 0))
            self.stats_row.controls[1].content.content.controls[1].value = str(response.get("pending_orders", 0))
        self.update()

    def create_stat_card(self, title, value):
        return Card(
            content=Container(
                padding=10,
                content=Column(
                    controls=[
                        Text(title, size=14, color=colors.BLUE_600),
                        Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            width=self.app.page.width * 0.4,  # 40% of screen width
            height=100,
        )

    def create_function_card(self, icon, title, gradient_colors):
        return ft.GestureDetector(
            content=Card(
                content=Container(
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=gradient_colors,
                    ),
                    border_radius=border_radius.all(12),
                    padding=15,
                    content=Column(
                        controls=[
                            Icon(icon, size=40, color=colors.WHITE),
                            Container(height=10),
                            Text(title, color=colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ),
            on_tap=lambda _: self.navigate_to_function(title),
        )

    def load_function_cards(self):
        functions = [
            ("Inventory", icons.INVENTORY_2, [ft.colors.BLUE_400, ft.colors.BLUE_700]),
            ("Picking", icons.LIST_ALT, [ft.colors.GREEN_400, ft.colors.GREEN_700]),
            ("Receiving", icons.MOVE_TO_INBOX, [ft.colors.AMBER_400, ft.colors.AMBER_700]),
            ("Shipping", icons.LOCAL_SHIPPING, [ft.colors.PURPLE_400, ft.colors.PURPLE_700]),
            ("Tasks", icons.ASSIGNMENT, [ft.colors.RED_400, ft.colors.RED_700]),
            ("Reports", icons.BAR_CHART, [ft.colors.CYAN_400, ft.colors.CYAN_700]),
        ]

        for title, icon, colors in functions:
            self.function_grid.controls.append(self.create_function_card(icon, title, colors))

        self.update()

    def navigate_to_function(self, function_name):
        function_routes = {
            "Inventory": "/inventory",
            "Picking": "/picking",
            "Receiving": "/receiving",
            "Shipping": "/shipping",
            "Tasks": "/tasks",
            "Reports": "/reports",
        }
        if function_name in function_routes:
            self.app.page.go(function_routes[function_name])

    def bottom_nav_change(self, e):
        index = e.control.selected_index
        if index == 0:  # Home
            pass  # Already on home screen
        elif index == 1:  # Inventory
            self.app.page.go("/inventory")
        elif index == 2:  # Orders
            self.app.page.go("/orders")
        elif index == 3:  # Profile
            self.app.page.go("/profile")
