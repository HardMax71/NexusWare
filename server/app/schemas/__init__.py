# /server/app/schemas/__init__.py

# Asset schemas
from .asset import (
    AssetBase, AssetCreate, AssetUpdate, Asset, AssetMaintenanceBase,
    AssetMaintenanceCreate, AssetMaintenanceUpdate,
    AssetMaintenance, AssetWithMaintenance
)

# Audit schemas
from .audit import AuditLogBase, AuditLogCreate, AuditLog

# Inventory schemas
from .inventory import (
    ProductCategoryBase, ProductCategoryCreate, ProductCategoryUpdate, ProductCategory,
    ProductBase, ProductCreate, ProductUpdate, Product,
    InventoryBase, InventoryCreate, InventoryUpdate, Inventory,
    LocationBase, LocationCreate, LocationUpdate, Location,
    ZoneBase, ZoneCreate, ZoneUpdate, Zone,
    ProductWithInventory, LocationWithInventory, ZoneWithLocations
)

# Order schemas
from .order import (
    OrderItemBase, OrderItemCreate, OrderItemUpdate, OrderItem,
    OrderBase, OrderCreate, OrderUpdate, Order,
    CustomerBase, CustomerCreate, CustomerUpdate, Customer,
    POItemBase, POItemCreate, POItemUpdate, POItem,
    PurchaseOrderBase, PurchaseOrderCreate,
    PurchaseOrderUpdate, PurchaseOrder,
    SupplierBase, SupplierCreate, SupplierUpdate, Supplier
)

# Quality schemas
from .quality import (QualityCheckBase, QualityCheckCreate,
                      QualityCheckUpdate, QualityCheck)

# Task schemas
from .task import TaskBase, TaskCreate, TaskUpdate, Task

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
    CarrierBase, CarrierCreate, CarrierUpdate, Carrier
)

# Yard schemas
from .yard import (
    YardLocationBase, YardLocationCreate,
    YardLocationUpdate, YardLocation,
    DockAppointmentBase, DockAppointmentCreate,
    DockAppointmentUpdate, DockAppointment
)
