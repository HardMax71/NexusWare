# /server/app/crud/inventory.py
from server.app.models import (Product, ProductCategory,
                               Inventory, Location, Zone)
from server.app.schemas import (ProductCreate, ProductUpdate,
                                ProductCategoryCreate, ProductCategoryUpdate,
                                InventoryCreate, InventoryUpdate, LocationCreate,
                                LocationUpdate, ZoneCreate, ZoneUpdate)
from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    pass


class CRUDProductCategory(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    pass


class CRUDInventory(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):
    pass


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    pass


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    pass


product = CRUDProduct(Product)
product_category = CRUDProductCategory(ProductCategory)
inventory = CRUDInventory(Inventory)
location = CRUDLocation(Location)
zone = CRUDZone(Zone)
