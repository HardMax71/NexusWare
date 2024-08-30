from desktop_app.src.ui.views.notifications.notification_center import NotificationCenter
from desktop_app.src.ui.views.audit_logs.audit_log_view import AuditLogView
from .barcode_designer import BarcodeDesignerWidget
from .dashboard import DashboardWidget
from .main_window import MainWindow
from .report_generator import ReportGeneratorWidget
from .advanced_search import AdvancedSearchDialog
from .settings.system_diagnostics import SystemDiagnosticsWidget
from .views.auth import LoginDialog
from .views.customers import CustomerDialog, CustomerDetailsDialog, CustomerView
from .views.inventory.inventory_planning import InventoryPlanningWidget
from .views.inventory.inventory_view import InventoryView
from .views.inventory.warehouse_visualization_window import WarehouseVisualizationWindow
from .views.orders import OrderView
from .views.products import ProductView
from .views.shipments import ShipmentView
from .views.suppliers import SupplierView
from .views.user_mgmt.user_mgmt_widget import UserManagementWidget

__all__ = [
    "MainWindow",
    "LoginDialog",
    "DashboardWidget",
    "InventoryView",
    "InventoryPlanningWidget",
    "OrderView",
    "ProductView",
    "SupplierView",
    "CustomerView",
    "ShipmentView",
    "ReportGeneratorWidget",
    "BarcodeDesignerWidget",
    "SystemDiagnosticsWidget",
    "AdvancedSearchDialog",
    "UserManagementWidget",
    "AuditLogView",
    "NotificationCenter",
    "WarehouseVisualizationWindow",
]
