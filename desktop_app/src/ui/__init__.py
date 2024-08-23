from desktop_app.src.ui.settings.system_diagnostics import SystemDiagnosticsWidget
from .audit_log_view import AuditLogView
from .barcode_designer import BarcodeDesignerWidget
from .batch_processor import BatchProcessorWidget
from .customer_view import CustomerView
from .dashboard import DashboardWidget
from .inventory_planning import InventoryPlanningWidget
from .inventory_view import InventoryView
from .login_dialog import LoginDialog
from .main_window import MainWindow
from .notification_center import NotificationCenter
from .offline_mode import OfflineModeWidget
from .order_view import OrderView
from .product_view import ProductView
from .report_generator import ReportGeneratorWidget
from .search_filter import AdvancedSearchDialog
from .shipment_view import ShipmentView
from .simulation_view import SimulationView
from .supplier_view import SupplierView
from .training_mode import TrainingModeManager
from .user_management import UserManagementWidget
from .warehouse_visualization_window import WarehouseVisualizationWindow

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
    "BatchProcessorWidget",
    "BarcodeDesignerWidget",
    "SystemDiagnosticsWidget",
    "SimulationView",
    "AdvancedSearchDialog",
    "TrainingModeManager",
    "OfflineModeWidget",
    "UserManagementWidget",
    "AuditLogView",
    "NotificationCenter",
    "WarehouseVisualizationWindow",
]
