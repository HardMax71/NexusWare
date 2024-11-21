# src/nexusware/app.py

import asyncio
from datetime import datetime

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from mobile_app.src.nexusware.utils.cache_manager import CacheManager
from mobile_app.src.nexusware.utils.navigation_manager import NavigationManager
from mobile_app.src.nexusware.utils.network_manager import NetworkManager
from mobile_app.src.nexusware.utils.theme_manager import ThemeManager
from public_api.api.client import APIClient
from public_api.api.users import UsersAPI


class NexusWareMobile(toga.App):
    def __init__(self):
        super().__init__(
            formal_name='NexusWare Mobile',
            app_id='com.nexusware.mobile',
            app_name='NexusWare Mobile',
            icon='resources/app_icon.png'
        )

        # Initialize API client
        self.api_client = APIClient(base_url="http://127.0.0.1:8000/api/v1")
        self.users_api = UsersAPI(self.api_client)

        # Initialize managers
        self.theme_manager = ThemeManager()
        self.navigation_manager = NavigationManager(self)
        self.network_manager = NetworkManager()
        self.cache_manager = CacheManager()

        # Initialize state
        self.current_screen = None
        self.is_authenticated = False

    def startup(self):
        """
        Initialize the application
        """
        # Create main window
        self.main_window = toga.MainWindow(
            title='NexusWare Mobile',
            size=(800, 600)
        )

        # Add initial content - can be a temporary loading message
        self.main_window.content = toga.Box(
            style=Pack(direction=COLUMN, padding=20),
            children=[
                toga.Label('Loading NexusWare Mobile...', style=Pack(padding=10))
            ]
        )

        # Register routes
        self.register_routes()

        # Show the window first
        self.main_window.show()

        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run async startup in the event loop
        loop.run_until_complete(self.async_startup())

    async def async_startup(self):
        """
        Async initialization tasks
        """
        try:
            # Check authentication status
            await self.check_auth()
        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Startup error: {str(e)}"
            )
            await self.main_window.dialog(error_dialog)
            # Ensure we show login screen on error
            self.navigate_to('login')

    def register_routes(self):
        """
        Register all application routes
        """
        from mobile_app.src.nexusware.screens.auth import LoginScreen, ProfileScreen
        from mobile_app.src.nexusware.screens.inventory import (
            InventoryListScreen, BarcodeScanner,
            ProductDetailsScreen, StockCountScreen
        )
        from mobile_app.src.nexusware.screens.tasks import TaskListScreen, TaskDetailsScreen
        from mobile_app.src.nexusware.screens.picking import PickListScreen, PickingScreen

        # Register routes with navigation manager
        routes = {
            'login': LoginScreen,
            'profile': ProfileScreen,
            'inventory': InventoryListScreen,
            'barcode_scanner': BarcodeScanner,
            'product_details': ProductDetailsScreen,
            'stock_count': StockCountScreen,
            'tasks': TaskListScreen,
            'task_details': TaskDetailsScreen,
            'pick_lists': PickListScreen,
            'picking': PickingScreen
        }

        for route, screen in routes.items():
            self.navigation_manager.register_route(route, screen)

    async def check_auth(self):
        """
        Check authentication status and redirect accordingly
        """
        try:
            # Try to get cached token
            token_data = self.cache_manager.get('auth_token')
            if token_data:
                self.api_client.set_tokens(
                    token_data['access_token'],
                    token_data['refresh_token'],
                    token_data['expires_in']
                )
                # Verify token is still valid
                user = await asyncio.to_thread(self.users_api.get_current_user)
                if user:
                    self.is_authenticated = True
                    self.navigate_to('inventory')
                    return

        except Exception as e:
            print(f"Auth check error: {str(e)}")
            pass

        # If not authenticated, show login screen
        self.navigate_to('login')

    def navigate_to(self, route: str, **params):
        """
        Navigate to a screen
        """
        try:
            # Clear previous screen
            if self.current_screen:
                self.current_screen.cleanup()

            # Create new screen
            screen_class = self.navigation_manager.routes[route]
            self.current_screen = screen_class(**params) if params else screen_class()

            # Set as main content
            self.main_window.content = self.current_screen.main_box

        except Exception as e:
            self.show_error(f"Navigation error: {str(e)}")

    def show_error(self, message: str):
        """
        Show error dialog
        """
        self.main_window.error_dialog('Error', message)

    def show_info(self, title: str, message: str):
        """
        Show info dialog
        """
        self.main_window.info_dialog(title, message)

    async def logout(self):
        """
        Handle logout
        """
        try:
            self.is_authenticated = False
            self.api_client.set_tokens("", "", 0)
            self.cache_manager.clear()
            self.navigate_to('login')
        except Exception as e:
            self.show_error(f"Logout error: {str(e)}")

    def on_exit(self, widget, **kwargs):
        """
        Handle application exit
        """
        try:
            # Cleanup
            if self.current_screen:
                self.current_screen.cleanup()

            # Clear sensitive cache
            self.cache_manager.clear()

        except Exception as e:
            print(f"Exit error: {str(e)}")

        return False  # Allow exit

    async def refresh_token(self):
        """
        Refresh authentication token
        """
        try:
            success = await asyncio.to_thread(self.api_client.refresh_access_token)
            if success:
                token_data = {
                    'access_token': self.api_client.access_token,
                    'refresh_token': self.api_client.refresh_token,
                    'expires_in': int((self.api_client.token_expiry - datetime.utcnow()).total_seconds())
                }
                self.cache_manager.set('auth_token', token_data)
            else:
                await self.logout()
        except Exception:
            await self.logout()


def main():
    """
    Application entry point
    """
    return NexusWareMobile()


if __name__ == '__main__':
    app = main()
    app.main_loop()
