# /server/app/schemas/inventory.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProductCategoryBase(BaseModel):
    name: str
    parent_category_id: Optional[int] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_category_id: Optional[int] = None


class ProductCategory(ProductCategoryBase):
    category_id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: int
    unit_of_measure: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    barcode: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_of_measure: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    barcode: Optional[str] = None


class Product(ProductBase):
    product_id: int

    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    product_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity: Optional[int] = None


class Inventory(InventoryBase):
    inventory_id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    zone_id: int
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    zone_id: Optional[int] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None


class Location(LocationBase):
    location_id: int

    class Config:
        from_attributes = True


class ZoneBase(BaseModel):
    name: str
    description: Optional[str] = None


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Zone(ZoneBase):
    zone_id: int

    class Config:
        from_attributes = True


class ProductWithInventory(Product):
    inventory_items: list[Inventory] = []


class LocationWithInventory(Location):
    inventory_items: list[Inventory] = []


class ZoneWithLocations(Zone):
    locations: list[Location] = []
