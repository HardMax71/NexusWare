# /server/app/schemas/__init__.py

# Asset schemas
from .asset import (
    AssetBase, AssetCreate, AssetUpdate, Asset, AssetMaintenanceBase,
    AssetMaintenanceCreate, AssetMaintenanceUpdate,
    AssetMaintenance, AssetWithMaintenance,
    AssetFilter, AssetMaintenanceFilter, AssetWithMaintenanceList
)
# Audit schemas
from .audit import (AuditLogBase, AuditLogCreate,
                    AuditLog, AuditLogWithUser, AuditLogFilter,
                    AuditSummary, UserActivitySummary, AuditLogExport)
# Inventory schemas
from .inventory import (
    ProductCategoryBase, ProductCategoryCreate, ProductCategoryUpdate, ProductCategory,
    ProductBase, ProductCreate, ProductUpdate, Product,
    InventoryBase, InventoryCreate, InventoryUpdate, Inventory,
    LocationBase, LocationCreate, LocationUpdate, Location,
    ZoneBase, ZoneCreate, ZoneUpdate, Zone,
    ProductWithInventory, LocationWithInventory, ZoneWithLocations,
    ProductFilter, InventoryFilter, LocationFilter, ZoneFilter,
    InventoryAdjustment, BarcodeData, InventoryTransfer,
    ProductWithCategoryAndInventory, InventoryReport,
    WarehouseLayout, InventoryMovement, StocktakeItem, StocktakeCreate,
    StocktakeDiscrepancy, StocktakeResult, ABCCategory, ABCAnalysisResult,
    InventoryLocationSuggestion
)
# Order schemas
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
    ShippingInfo, POItemReceive
)
# Quality schemas
from .quality import (QualityCheckBase, QualityCheckCreate,
                      QualityCheckUpdate, QualityCheck,
                      QualityCheckWithProduct, QualityCheckFilter,
                      QualityMetrics, QualityStandard,
                      QualityStandardCreate, QualityStandardUpdate,
                      QualityAlert, QualityAlertCreate,
                      QualityAlertUpdate, QualityCheckComment,
                      QualityCheckCommentCreate, ProductDefectRate)
# Report schemas
from .reports import (
    InventoryItem, InventorySummaryReport,
    OrderSummaryReport, WarehousePerformanceMetric, WarehousePerformanceReport,
    KPIMetric, KPIDashboard
)
# Task schemas
from .task import (TaskBase, TaskCreate, TaskUpdate, Task,
                   TaskWithAssignee, TaskFilter, TaskComment, TaskCommentCreate,
                   TaskStatistics, UserTaskSummary)
# User schemas
from .user import (
    PermissionBase, PermissionCreate, PermissionUpdate, Permission,
    RoleBase, RoleCreate, RoleUpdate, Role,
    UserBase, UserCreate, UserUpdate, User, UserInDB, Token, TokenData
)
# Warehouse schemas
from .warehouse import (
    PickListItemBase, PickListItemCreate, PickListItemUpdate, PickListItem,
    PickListBase, PickListCreate, PickListUpdate, PickList,
    ReceiptItemBase, ReceiptItemCreate, ReceiptItemUpdate, ReceiptItem,
    ReceiptBase, ReceiptCreate, ReceiptUpdate, Receipt,
    ShipmentBase, ShipmentCreate, ShipmentUpdate, Shipment,
    CarrierBase, CarrierCreate, CarrierUpdate, Carrier,
    PickListFilter, ReceiptFilter, ShipmentFilter, WarehouseStats, LocationInventory,
    LocationInventoryUpdate
)
# Yard schemas
from .yard import (
    YardLocationBase, YardLocationCreate,
    YardLocationUpdate, YardLocation,
    DockAppointmentBase, DockAppointmentCreate,
    DockAppointmentUpdate, DockAppointment,
    YardLocationWithAppointments, YardLocationFilter,
    YardStats, AppointmentConflict, YardUtilizationReport,
    YardLocationCapacity, CarrierPerformance,
    DockAppointmentFilter
)
