from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar, QMessageBox

from desktop_app.src.utils import ConfigManager
from public_api.api import APIClient
from public_api.permission_manager import PermissionManager
from .components.dialogs import UserManualDialog, AboutDialog
from .customer_view import CustomerView
from .dashboard import DashboardWidget
from .inventory_view import InventoryView
from .notification_center import NotificationCenter
from .order_view import OrderView
from .product_view import ProductView
from .report_generator import ReportGeneratorWidget
from .search_filter import AdvancedSearchDialog
from .settings.settings_dialog import SettingsDialog
from .shipment_view import ShipmentView
from .supplier_view import SupplierView
from .task_view import TaskView
from .user_management import UserManagementWidget


class MainWindow(QMainWindow):
    def __init__(self, api_client: APIClient, config_manager: ConfigManager,
                 permission_manager: PermissionManager):
        super().__init__()
        self.api_client = api_client
        self.config_manager = config_manager
        self.permission_manager = permission_manager
        self.init_ui()

        # TODO : Implement training mode, now it overlaps with the main window
        # self.training_manager = TrainingModeManager(self, self.config_manager)
        # QApplication.instance().processEvents()  # Ensure UI is fully loaded
        # self.training_manager.start_training()

    def init_ui(self):
        self.setWindowTitle("NexusWare WMS")
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        self.setMinimumSize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.add_tabs_based_on_permissions()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.notification_center = NotificationCenter(self.api_client)
        self.addDockWidget(Qt.RightDockWidgetArea, self.notification_center)
        self.notification_center.hide()

        self.create_menu_bar()

    def add_tabs_based_on_permissions(self):
        tab_permissions = {
            "Dashboard": "dashboard",
            "Inventory": "inventory",
            "Orders": "orders",
            "Products": "products",
            "Suppliers": "suppliers",
            "Customers": "customers",
            "Shipments": "shipments",
            "Reports": "reports",
            "User Management": "user_management",
            "Tasks Management": "tasks_management",
        }

        tab_classes = {
            "Dashboard": DashboardWidget,
            "Inventory": InventoryView,
            "Orders": OrderView,
            "Products": ProductView,
            "Suppliers": SupplierView,
            "Customers": CustomerView,
            "Shipments": ShipmentView,
            "Reports": ReportGeneratorWidget,
            "User Management": UserManagementWidget,
            "Tasks Management": TaskView,
        }

        for tab_name, permission_name in tab_permissions.items():
            if self.permission_manager.has_read_permission(permission_name):
                tab_widget = tab_classes[tab_name](self.api_client)
                self.tab_widget.addTab(tab_widget, tab_name)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        if self.permission_manager.has_read_permission("settings"):
            file_menu.addAction("Settings", self.open_settings)
        file_menu.addAction("Exit", self.close)

        view_menu = menu_bar.addMenu("View")
        if self.permission_manager.has_read_permission("notifications"):
            view_menu.addAction("Toggle Notification Center", self.toggle_notification_center)

        if self.permission_manager.has_read_permission("adv_search"):
            view_menu.addAction("Advanced Search", self.open_advanced_search)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("User Manual", self.open_user_manual)
        help_menu.addAction("About", self.show_about_dialog)

    def open_advanced_search(self):
        search_dialog = AdvancedSearchDialog(self.api_client, self)
        search_dialog.exec()

    def open_settings(self):
        settings_dialog = SettingsDialog(self.config_manager, self, api_client=self.api_client)
        settings_dialog.exec_()

    def toggle_notification_center(self):
        self.notification_center.setVisible(not self.notification_center.isVisible())

    def open_user_manual(self):
        try:
            with open("docs/user_manual.md", "r") as manual_file:
                manual_content = manual_file.read()

            manual_dialog = UserManualDialog(manual_content, self)
            manual_dialog.exec_()

        except FileNotFoundError:
            QMessageBox.warning(self, "User Manual", "The user manual file could not be found.", QMessageBox.Ok)

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()
