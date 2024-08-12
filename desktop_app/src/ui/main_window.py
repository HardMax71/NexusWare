from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from .components.dialogs import UserManualDialog, AboutDialog
from .dashboard import DashboardWidget
from .inventory_view import InventoryView
from .order_view import OrderView
from .product_view import ProductView
from .settings.settings_dialog import SettingsDialog
from .supplier_view import SupplierView
from .customer_view import CustomerView
from .shipment_view import ShipmentView
from .report_generator import ReportGeneratorWidget
from .user_management import UserManagementWidget
from .notification_center import NotificationCenter

class MainWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("NexusWare WMS")
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        self.setMinimumSize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(DashboardWidget(self.api_client), "Dashboard")
        self.tab_widget.addTab(InventoryView(self.api_client), "Inventory")
        self.tab_widget.addTab(OrderView(self.api_client), "Orders")
        self.tab_widget.addTab(ProductView(self.api_client), "Products")
        self.tab_widget.addTab(SupplierView(self.api_client), "Suppliers")
        self.tab_widget.addTab(CustomerView(self.api_client), "Customers")
        self.tab_widget.addTab(ShipmentView(self.api_client), "Shipments")
        self.tab_widget.addTab(ReportGeneratorWidget(self.api_client), "Reports")
        self.tab_widget.addTab(UserManagementWidget(self.api_client), "User Management")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.notification_center = NotificationCenter(self.api_client)
        self.addDockWidget(Qt.RightDockWidgetArea, self.notification_center)
        self.notification_center.hide()

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Settings", self.open_settings)
        file_menu.addAction("Exit", self.close)

        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Toggle Notification Center", self.toggle_notification_center)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("User Manual", self.open_user_manual)
        help_menu.addAction("About", self.show_about_dialog)

    def open_settings(self):
        settings_dialog = SettingsDialog(self.api_client, self)
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