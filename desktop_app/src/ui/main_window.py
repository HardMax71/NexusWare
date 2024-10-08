from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar, QMessageBox, QToolButton

from public_api.api import APIClient
from public_api.permissions import PermissionName, PermissionManager
from src.ui import AuditLogView
from src.ui.advanced_search import AdvancedSearchDialog
from src.ui.components import IconPath
from src.ui.components.dialogs import UserManualDialog, AboutDialog
from src.ui.dashboard import DashboardWidget
from src.ui.qtutorial import QTutorialManager
from src.ui.report_generator import ReportGeneratorWidget
from src.ui.settings import SettingsDialog
from src.ui.views.customers import CustomerView
from src.ui.views.inventory import InventoryView
from src.ui.views.notifications import NotificationCenter
from src.ui.views.orders import OrderView
from src.ui.views.products import ProductView
from src.ui.views.shipments import ShipmentView
from src.ui.views.suppliers import SupplierView
from src.ui.views.tasks import TaskView
from src.ui.views.user_mgmt import UserManagementWidget
from src.utils import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self, api_client: APIClient, config_manager: ConfigManager,
                 permission_manager: PermissionManager):
        super().__init__()
        self.api_client = api_client
        self.config_manager = config_manager
        self.permission_manager = permission_manager
        self.chat_base_url = self.config_manager.get("chat_base_url",
                                                     "http://127.0.0.1:8001/chat/v1")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("NexusWare WMS")
        self.setWindowIcon(QIcon(IconPath.APP_ICON))
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

        self.create_menu_bar()

        if self.config_manager.get("start_tutorial", True):
            self.initialize_tutorial_manager()

    def initialize_tutorial_manager(self):
        tutorial_steps = [
            (self.tab_widget, "This is the main window where you can navigate between different tabs."),
            (self.tab_widget.tabBar(), "Click on a tab to view the content."),
            (self.status_bar, "This is the status bar where you can see notifications and other messages."),
            (self.menuBar(), "Use the menu bar to access different features."),
            (self.notification_center, "Click on the bell icon to view notifications."),
        ]

        self.tutorial_manager = QTutorialManager(self, tutorial_steps, show_step_number=True)
        self.tutorial_manager.start_tutorial()

    def add_tabs_based_on_permissions(self):
        tab_classes = {
            PermissionName.DASHBOARD: DashboardWidget,
            PermissionName.AUDIT_LOGS: AuditLogView,
            PermissionName.INVENTORY: InventoryView,
            PermissionName.ORDERS: OrderView,
            PermissionName.PRODUCTS: ProductView,
            PermissionName.SUPPLIERS: SupplierView,
            PermissionName.CUSTOMERS: CustomerView,
            PermissionName.SHIPMENTS: ShipmentView,
            PermissionName.REPORTS: ReportGeneratorWidget,
            PermissionName.USER_MANAGEMENT: UserManagementWidget,
            PermissionName.TASKS_MANAGEMENT: TaskView,
        }

        for tab_name, tab_class in tab_classes.items():
            if self.permission_manager.has_read_permission(tab_name):
                tab_widget = tab_class(self.api_client)
                self.tab_widget.addTab(tab_widget, tab_name.value)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        if self.permission_manager.has_read_permission(PermissionName.SETTINGS):
            file_menu.addAction("Settings", self.open_settings)
        file_menu.addAction("Exit", self.close)

        view_menu = menu_bar.addMenu("View")
        if self.permission_manager.has_read_permission(PermissionName.ADVANCED_SEARCH):
            view_menu.addAction("Advanced Search", self.open_advanced_search)

        chat_menu = menu_bar.addMenu("Chat")
        chat_menu.addAction("Open Chat", self.open_chat_window)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("User Manual", self.open_user_manual)
        help_menu.addAction("About", self.show_about_dialog)

        self.add_notification_button(menu_bar)

    def open_chat_window(self):
        from src.ui.chat_window import ChatDialog
        chat_dialog = ChatDialog(self.api_client, self)
        chat_dialog.exec()

    def add_notification_button(self, menu_bar):
        notification_button = QToolButton(self)
        notification_button.setIcon(QIcon(IconPath.BELL))
        notification_button.setIconSize(QSize(24, 24))
        notification_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        notification_button.clicked.connect(self.toggle_notification_center)

        menu_bar.setCornerWidget(notification_button, Qt.TopRightCorner)

        self.update_notification_icon(notification_button)

    def update_notification_icon(self, button):
        unread_notifications = len(self.notification_center.notifications_api.get_unread_notifications())
        if unread_notifications > 0:
            button.setIcon(QIcon(IconPath.BELL_UNREAD))
        else:
            button.setIcon(QIcon(IconPath.BELL))

    def toggle_notification_center(self):
        if not self.notification_center.isVisible():
            self.notification_center.show()
        else:
            self.notification_center.hide()

    def open_advanced_search(self):
        search_dialog = AdvancedSearchDialog(self.api_client, self)
        search_dialog.exec()

    def open_settings(self):
        settings_dialog = SettingsDialog(self.config_manager, self, api_client=self.api_client)
        settings_dialog.exec_()

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
