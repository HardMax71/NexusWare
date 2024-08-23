# /server/app/shared_schemas/inventory.py

from pydantic import BaseModel, constr, Field


class ProductCategoryBase(BaseModel):
    name: str
    parent_category_id: int | None = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: str | None = None
    parent_category_id: int | None = None


class ProductCategory(ProductCategoryBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: str
    name: str
    description: str | None = None
    category_id: int
    unit_of_measure: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    barcode: str | None = None
    price: float


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    unit_of_measure: str | None = None
    weight: float | None = None
    dimensions: str | None = None
    barcode: str | None = None
    price: float | None = None


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    expiration_date: int | None = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    product_id: int | None = None
    location_id: int | None = None
    quantity: int | None = None
    expiration_date: int | None = None


class Inventory(InventoryBase):
    id: int
    last_updated: int

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    name: str = Field(..., max_length=100)
    zone_id: int | None = None
    aisle: str | None = Field(None, max_length=50)
    rack: str | None = Field(None, max_length=50)
    shelf: str | None = Field(None, max_length=50)
    bin: str | None = Field(None, max_length=50)
    capacity: int = 0


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    zone_id: int | None = None
    aisle: str | None = Field(None, max_length=50)
    rack: str | None = Field(None, max_length=50)
    shelf: str | None = Field(None, max_length=50)
    bin: str | None = Field(None, max_length=50)
    capacity: int | None = 0


class Location(LocationBase):
    id: int

    class Config:
        from_attributes = True


class ZoneBase(BaseModel):
    name: str
    description: str | None = None


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class Zone(ZoneBase):
    id: int

    class Config:
        from_attributes = True


class ProductWithInventory(Product):
    inventory_items: list[Inventory] = []

    class Config:
        from_attributes = True


class LocationWithInventory(Location):
    inventory_items: list[Inventory] = []


class ZoneWithLocations(Zone):
    locations: list[Location] = []


class ProductFilter(BaseModel):
    name: str | None = None
    category_id: int | None = None
    sku: str | None = None
    barcode: str | None = None


class LocationFilter(BaseModel):
    name: str | None = None
    zone_id: int | None = None
    aisle: str | None = None
    rack: str | None = None
    shelf: str | None = None
    bin: str | None = None


class ZoneFilter(BaseModel):
    name: str | None = None


class BarcodeData(BaseModel):
    barcode: constr(min_length=1, max_length=50)


class InventoryTransfer(BaseModel):
    from_location_id: int
    to_location_id: int
    quantity: int


class ProductWithCategoryAndInventory(ProductWithInventory):
    category: ProductCategory | None = None
    pass


class InventoryReport(BaseModel):
    total_products: int
    total_quantity: int
    low_stock_items: list[ProductWithInventory]
    out_of_stock_items: list[Product]


class WarehouseLayout(BaseModel):
    zones: list[ZoneWithLocations]


class InventoryMovement(BaseModel):
    product_id: int
    from_location_id: int
    to_location_id: int
    quantity: int
    reason: str
    timestamp: int


class InventoryAdjustment(BaseModel):
    product_id: int
    location_id: int
    quantity_change: int
    reason: str
    timestamp: int


class StocktakeItem(BaseModel):
    product_id: int
    counted_quantity: int


class StocktakeCreate(BaseModel):
    location_id: int
    items: list[StocktakeItem]


class StocktakeDiscrepancy(BaseModel):
    product_id: int
    expected_quantity: int
    counted_quantity: int
    discrepancy: int


class StocktakeResult(BaseModel):
    location_id: int
    total_items: int
    discrepancies: list[StocktakeDiscrepancy]
    accuracy_percentage: float


class ABCCategory(BaseModel):
    category: str
    products: list[Product]
    value_percentage: float
    item_percentage: float


class ABCAnalysisResult(BaseModel):
    categories: list[ABCCategory]


class InventoryLocationSuggestion(BaseModel):
    product_id: int
    current_location_id: int
    suggested_location_id: int
    reason: str


class BulkImportData(BaseModel):
    items: list[InventoryCreate]


class BulkImportResult(BaseModel):
    success_count: int
    failure_count: int
    errors: list[str]


class StorageUtilization(BaseModel):
    total_capacity: float
    used_capacity: float
    utilization_percentage: float
    zone_utilization: list[dict[str, str | int | float]]


class InventorySummary(BaseModel):
    category_quantities: dict[str, int]
    total_items: int
    total_categories: int

    class Config:
        from_attributes = True


class InventoryWithDetails(Inventory):
    product: Product
    location: Location


class InventoryList(BaseModel):
    items: list[InventoryWithDetails]
    total: int


class InventoryFilter(BaseModel):
    product_id: int | None = None
    location_id: int | None = None
    sku: str | None = None
    name: str | None = None
    quantity_min: int | None = None
    quantity_max: int | None = None


class InventoryTrendItem(BaseModel):
    timestamp: int
    quantity: int
