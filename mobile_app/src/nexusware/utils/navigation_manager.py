# src/nexusware/utils/navigation_manager.py
from typing import Dict, Callable, Any

from toga import App


class NavigationManager:
    def __init__(self, app: App):
        self.app = app
        self.history: list[str] = []
        self.current_screen = None
        self.routes: Dict[str, Callable] = {}
        self.params: Dict[str, Any] = {}

    def register_route(self, route: str, screen_class: Callable):
        """Register a screen with a route"""
        self.routes[route] = screen_class

    def navigate_to(self, route: str, **params):
        """Navigate to a specific route with optional parameters"""
        if route not in self.routes:
            raise ValueError(f"Route {route} not found")

        # Store current route in history
        if self.current_screen:
            self.history.append(self.current_screen)

        # Create new screen instance
        screen_class = self.routes[route]
        screen = screen_class(**params) if params else screen_class()

        # Update current screen
        self.current_screen = route
        self.params[route] = params

        # Set as main content
        self.app.main_window.content = screen

    def go_back(self):
        """Navigate to previous screen"""
        if not self.history:
            return

        previous_route = self.history.pop()
        previous_params = self.params.get(previous_route, {})
        self.navigate_to(previous_route, **previous_params)

    def clear_history(self):
        """Clear navigation history"""
        self.history = []
        self.params = {}

    def get_current_params(self) -> dict:
        """Get parameters for current route"""
        return self.params.get(self.current_screen, {})

    def register_default_routes(self):
        """Register default application routes"""
        from ..screens.auth import LoginScreen, ProfileScreen
        from ..screens.inventory import (
            InventoryListScreen, BarcodeScanner,
            ProductDetailsScreen, StockCountScreen
        )
        from ..screens.tasks import TaskListScreen, TaskDetailsScreen
        from ..screens.picking import PickListScreen, PickingScreen

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
            self.register_route(route, screen)
