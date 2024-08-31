# /server/app/shared_schemas/__init__.py

# Asset shared_schemas
from .asset import (
    AssetBase, AssetCreate, AssetUpdate, Asset, AssetMaintenanceBase,
    AssetMaintenanceCreate, AssetMaintenanceUpdate,
    AssetMaintenance, AssetWithMaintenance,
    AssetFilter, AssetMaintenanceFilter, AssetWithMaintenanceList,
    AssetTransfer, AssetLocation
)
# Audit shared_schemas
from .audit import (AuditLogBase, AuditLogCreate,
                    AuditLog, AuditLogWithUser, AuditLogFilter,
                    AuditSummary, UserActivitySummary, AuditLogExport)
# Inventory shared_schemas
from .inventory import (
    ProductCategoryBase, ProductCategoryCreate, ProductCategoryUpdate, ProductCategory,
    ProductBase, ProductCreate, ProductUpdate, Product,
    InventoryBase, InventoryCreate, InventoryUpdate, Inventory,
    ZoneBase, ZoneCreate, ZoneUpdate, Zone,
    ProductWithInventory, LocationWithInventory, ZoneWithLocations,
    ProductFilter, InventoryFilter, ZoneFilter,
    InventoryAdjustment, BarcodeData, InventoryTransfer,
    ProductWithCategoryAndInventory, InventoryReport,
    WarehouseLayout, InventoryMovement, StocktakeItem, StocktakeCreate,
    StocktakeDiscrepancy, StocktakeResult, ABCCategory, ABCAnalysisResult,
    InventoryLocationSuggestion, BulkImportData, BulkImportResult,
    StorageUtilization, LocationBase, LocationCreate, LocationUpdate, Location,
    LocationFilter, InventorySummary, InventoryList, InventoryWithDetails,
    InventoryTrendItem,
)
# Notification shared_schemas
from .notification import (
    NotificationBase, NotificationCreate, NotificationUpdate, Notification
)
# Order shared_schemas
from .order import (
    OrderItemBase, OrderItemCreate, OrderItemUpdate, OrderItem,
    OrderBase, OrderCreate, OrderUpdate, Order,
    CustomerBase, CustomerCreate, CustomerUpdate, Customer,
    POItemBase, POItemCreate, POItemUpdate, POItem,
    PurchaseOrderBase, PurchaseOrderCreate,
    PurchaseOrderUpdate, PurchaseOrder,
    SupplierBase, SupplierCreate, SupplierUpdate, Supplier,
    OrderFilter, OrderSummary, CustomerFilter, PurchaseOrderFilter,
    SupplierFilter, OrderWithDetails, PurchaseOrderWithDetails,
    ShippingInfo, POItemReceive, OrderProcessingTimes,
    BulkOrderImportData, BulkOrderImportResult, OrderStatus
)
# Quality shared_schemas
from .quality import (QualityCheckBase, QualityCheckCreate,
                      QualityCheckUpdate, QualityCheck,
                      QualityCheckWithProduct, QualityCheckFilter,
                      QualityMetrics, QualityStandard,
                      QualityStandardCreate, QualityStandardUpdate,
                      QualityAlert, QualityAlertCreate,
                      QualityAlertUpdate, QualityCheckComment,
                      QualityCheckCommentCreate, ProductDefectRate)
# Report shared_schemas
from .reports import (
    InventoryItem, InventorySummaryReport,
    OrderSummaryReport, WarehousePerformanceMetric, WarehousePerformanceReport,
    KPIMetric, KPIDashboard
)
# Task shared_schemas
from .task import (TaskBase, TaskCreate, TaskUpdate, Task,
                   TaskWithAssignee, TaskFilter, TaskComment, TaskCommentCreate,
                   TaskStatistics, UserTaskSummary, TaskWithComments,
                   TaskPriorityUpdate, TaskAssignmentUpdate, TaskStatusUpdate,
                   TaskDueDateUpdate, TaskProgressUpdate, TaskDependency,
                   TaskDependencyCreate, TaskTimeline, TaskAnalytics,
                   BulkTaskCreate, BulkTaskCreateResult, TaskPriority, TaskStatus)
# User shared_schemas
from .user import (
    PermissionBase, PermissionCreate, PermissionUpdate, Permission,
    RoleBase, RoleCreate, RoleUpdate, Role, UserBase, UserUpdate, UserSanitized,
    UserInDB, TwoFactorLogin, Token, Message, UserFilter, UserWithPermissions,
    AllRoles, AllPermissions, UserPermissionUpdate, UserCreate, RefreshTokenRequest,
    RolePermission, RolePermissionCreate, RolePermissionUpdate, UserPermission,
    UserSearchResult
)
# Warehouse shared_schemas
from .warehouse import (
    PickListItemBase, PickListItemCreate, PickListItemUpdate, PickListItem,
    PickListBase, PickListCreate, PickListUpdate, PickList,
    ReceiptItemBase, ReceiptItemCreate, ReceiptItemUpdate, ReceiptItem,
    ReceiptBase, ReceiptCreate, ReceiptUpdate, Receipt,
    ShipmentBase, ShipmentCreate, ShipmentUpdate, Shipment,
    CarrierBase, CarrierCreate, CarrierUpdate, Carrier,
    PickListFilter, ReceiptFilter, ShipmentFilter, WarehouseStats, LocationInventory,
    LocationInventoryUpdate, OptimizedPickingRoute, PickingPerformance,
    ReceiptDiscrepancy, ShippingLabel, CarrierRate, ShipmentTracking,
    InventoryMovementCreate, InventoryAdjustmentCreate,
    ShipmentWithDetails, ShipmentStatus
)
# Yard shared_schemas
from .yard import (
    YardLocationBase, YardLocationCreate,
    YardLocationUpdate, YardLocation,
    DockAppointmentBase, DockAppointmentCreate,
    DockAppointmentUpdate, DockAppointment,
    YardLocationWithAppointments, YardLocationFilter,
    DockAppointmentFilter, YardUtilizationReport, CarrierPerformance,
    YardLocationOccupancy, YardOverview, AppointmentScheduleConflict,
    CarrierSchedule, YardLocationTypeDistribution, YardAnalytics,
    BulkAppointmentCreate, BulkAppointmentCreateResult,
    YardStats, AppointmentConflict, YardLocationCapacity
)
