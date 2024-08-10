# /clients/mobile/main.py

import flet as ft
import httpx
from flet import Page

from screens.barcode_scanner import BarcodeScannerOverlay
from screens.forgot_password import ForgotPasswordScreen
from screens.home import HomeScreen
from screens.inventory import InventoryScreen
from screens.login import LoginScreen
from screens.notification_center import NotificationCenter
from screens.picking import PickingScreen
from screens.product_details import ProductDetailsScreen
from screens.profile import ProfileScreen
from screens.receiving import ReceivingScreen
from screens.reports import ReportsScreen
from screens.shipping import ShippingScreen
from screens.tasks import TasksScreen
from utils.api_helper import api_call

API_BASE_URL = "http://127.0.0.1:8000/api/v1"


class NexusWareApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "NexusWare"
        self.page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.client = httpx.AsyncClient(base_url=API_BASE_URL)
        self.token = None
        self.user = None

        self.init_screens()
        self.setup_routes()

    def init_screens(self):
        self.login_screen = LoginScreen(self)
        self.home_screen = HomeScreen(self)
        self.inventory_screen = InventoryScreen(self)
        self.product_details_screen = ProductDetailsScreen(self)
        self.picking_screen = PickingScreen(self)
        self.receiving_screen = ReceivingScreen(self)
        self.shipping_screen = ShippingScreen(self)
        self.tasks_screen = TasksScreen(self)
        self.reports_screen = ReportsScreen(self)
        self.profile_screen = ProfileScreen(self)
        self.barcode_scanner = BarcodeScannerOverlay(self)
        self.notification_center = NotificationCenter(self)
        self.forgot_password_screen = ForgotPasswordScreen(self)

    def setup_routes(self):
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

    def route_change(self, route):
        self.page.views.clear()
        new_view = ft.View(route.route)

        routes = {
            "/login": self.login_screen,
            "/": self.home_screen,
            "/inventory": self.inventory_screen,
            "/picking": self.picking_screen,
            "/receiving": self.receiving_screen,
            "/shipping": self.shipping_screen,
            "/tasks": self.tasks_screen,
            "/reports": self.reports_screen,
            "/profile": self.profile_screen,
            "/forgot-password": self.forgot_password_screen,
        }

        if route.route in routes:
            new_view.controls.append(routes[route.route])
        elif route.route.startswith("/product/"):
            product_id = int(route.route.split("/")[-1])
            self.page.run_task(self.product_details_screen.load_product(product_id))
            new_view.controls.append(self.product_details_screen)
        else:
            new_view.controls.append(ft.Text(f"404 - Page not found: {route.route}"))

        self.page.views.append(new_view)
        self.page.update()

    def view_pop(self, view):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    async def login(self, email, password):
        login_data = {
            "username": email,
            "password": password
        }
        response = await api_call(self, self.client.post, "/users/login", data=login_data)
        if response and "access_token" in response:
            self.token = response["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            await self.load_user_data()
            return True
        return False

    async def load_user_data(self):
        response = await api_call(self, self.client.get, "/users/me")
        if response:
            self.user = response
            # Update user-related UI elements if needed

    def logout(self):
        self.token = None
        self.user = None
        self.client.headers.pop("Authorization", None)
        self.page.go("/login")

    def check_auth(self):
        if not self.token:
            self.page.go("/login")


def main(page: Page):
    app = NexusWareApp(page)
    page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)
