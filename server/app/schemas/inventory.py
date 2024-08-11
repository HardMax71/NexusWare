# /server/app/schemas/inventory.py
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, constr, Field


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
    price: float


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
    price: Optional[float] = None


class Product(ProductBase):
    product_id: int

    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    expiration_date: Optional[datetime] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    product_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity: Optional[int] = None
    expiration_date: Optional[datetime] = None


class Inventory(InventoryBase):
    inventory_id: int
    last_updated: datetime
    product: Product

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    name: str = Field(..., max_length=100)
    zone_id: Optional[int] = None
    aisle: Optional[str] = Field(None, max_length=50)
    rack: Optional[str] = Field(None, max_length=50)
    shelf: Optional[str] = Field(None, max_length=50)
    bin: Optional[str] = Field(None, max_length=50)


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    zone_id: Optional[int] = None
    aisle: Optional[str] = Field(None, max_length=50)
    rack: Optional[str] = Field(None, max_length=50)
    shelf: Optional[str] = Field(None, max_length=50)
    bin: Optional[str] = Field(None, max_length=50)


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
    inventory_items: List[Inventory] = []


class LocationWithInventory(Location):
    inventory_items: List[Inventory] = []


class ZoneWithLocations(Zone):
    locations: List[Location] = []


class ProductFilter(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None


class InventoryFilter(BaseModel):
    product_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity_min: Optional[int] = None
    quantity_max: Optional[int] = None


class LocationFilter(BaseModel):
    name: Optional[str] = None
    zone_id: Optional[int] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None


class ZoneFilter(BaseModel):
    name: Optional[str] = None


class BarcodeData(BaseModel):
    barcode: constr(min_length=1, max_length=50)


class InventoryTransfer(BaseModel):
    from_location_id: int
    to_location_id: int
    quantity: int


class ProductWithCategoryAndInventory(ProductWithInventory):
    category: ProductCategory


class InventoryReport(BaseModel):
    total_products: int
    total_quantity: int
    low_stock_items: List[ProductWithInventory]
    out_of_stock_items: List[Product]


class WarehouseLayout(BaseModel):
    zones: List[ZoneWithLocations]


class InventoryMovement(BaseModel):
    product_id: int
    from_location_id: int
    to_location_id: int
    quantity: int
    reason: str
    timestamp: datetime


class InventoryAdjustment(BaseModel):
    product_id: int
    location_id: int
    quantity_change: int
    reason: str
    timestamp: datetime


class StocktakeItem(BaseModel):
    product_id: int
    counted_quantity: int


class StocktakeCreate(BaseModel):
    location_id: int
    items: List[StocktakeItem]


class StocktakeDiscrepancy(BaseModel):
    product_id: int
    expected_quantity: int
    counted_quantity: int
    discrepancy: int


class StocktakeResult(BaseModel):
    location_id: int
    total_items: int
    discrepancies: List[StocktakeDiscrepancy]
    accuracy_percentage: float


class ABCCategory(BaseModel):
    category: str
    products: List[Product]
    value_percentage: float
    item_percentage: float


class ABCAnalysisResult(BaseModel):
    categories: List[ABCCategory]


class InventoryLocationSuggestion(BaseModel):
    product_id: int
    current_location_id: int
    suggested_location_id: int
    reason: str


class BulkImportData(BaseModel):
    items: List[InventoryCreate]


class BulkImportResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[str]


class StorageUtilization(BaseModel):
    total_capacity: float
    used_capacity: float
    utilization_percentage: float
