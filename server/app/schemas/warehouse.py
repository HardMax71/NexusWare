# /server/app/schemas/warehouse.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PickListItemBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    picked_quantity: int = 0


class PickListItemCreate(PickListItemBase):
    pass


class PickListItemUpdate(BaseModel):
    product_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity: Optional[int] = None
    picked_quantity: Optional[int] = None


class PickListItem(PickListItemBase):
    pick_list_item_id: int
    pick_list_id: int

    class Config:
        from_attributes = True


class PickListBase(BaseModel):
    order_id: int
    status: str


class PickListCreate(PickListBase):
    items: list[PickListItemCreate]


class PickListUpdate(BaseModel):
    order_id: Optional[int] = None
    status: Optional[str] = None
    items: Optional[list[PickListItemUpdate]] = None


class PickList(PickListBase):
    pick_list_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    items: list[PickListItem] = []

    class Config:
        from_attributes = True


class ReceiptItemBase(BaseModel):
    product_id: int
    quantity_received: int
    location_id: int


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity_received: Optional[int] = None
    location_id: Optional[int] = None


class ReceiptItem(ReceiptItemBase):
    receipt_item_id: int
    receipt_id: int

    class Config:
        from_attributes = True


class ReceiptBase(BaseModel):
    po_id: int
    status: str


class ReceiptCreate(ReceiptBase):
    items: list[ReceiptItemCreate]


class ReceiptUpdate(BaseModel):
    po_id: Optional[int] = None
    status: Optional[str] = None
    items: Optional[list[ReceiptItemUpdate]] = None


class Receipt(ReceiptBase):
    receipt_id: int
    received_date: datetime
    items: list[ReceiptItem] = []

    class Config:
        from_attributes = True


class ShipmentBase(BaseModel):
    order_id: int
    carrier_id: int
    tracking_number: Optional[str] = None
    status: str


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    order_id: Optional[int] = None
    carrier_id: Optional[int] = None
    tracking_number: Optional[str] = None
    status: Optional[str] = None
    ship_date: Optional[datetime] = None


class Shipment(ShipmentBase):
    shipment_id: int
    ship_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarrierBase(BaseModel):
    name: str
    contact_info: Optional[str] = None


class CarrierCreate(CarrierBase):
    pass


class CarrierUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None


class Carrier(CarrierBase):
    carrier_id: int

    class Config:
        from_attributes = True


class PickListFilter(BaseModel):
    status: Optional[str] = None
    order_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ReceiptFilter(BaseModel):
    status: Optional[str] = None
    po_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ShipmentFilter(BaseModel):
    status: Optional[str] = None
    order_id: Optional[int] = None
    carrier_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class WarehouseStats(BaseModel):
    total_pick_lists: int
    completed_pick_lists: int
    total_receipts: int
    completed_receipts: int
    total_shipments: int
    completed_shipments: int


class LocationInventory(BaseModel):
    location_id: int
    product_id: int
    quantity: int


class LocationInventoryUpdate(BaseModel):
    quantity: int


class OptimizedPickingRoute(BaseModel):
    pick_list_id: int
    optimized_route: list[PickListItem]


class PickingPerformance(BaseModel):
    average_picking_time: float
    items_picked_per_hour: float
    accuracy_rate: float


class QualityCheckCreate(BaseModel):
    product_id: int
    result: str
    notes: Optional[str] = None


class ReceiptDiscrepancy(BaseModel):
    product_id: int
    expected_quantity: int
    received_quantity: int
    discrepancy: int


class ShippingLabel(BaseModel):
    shipment_id: int
    tracking_number: str
    label_id: str
    label_download_url: str


class CarrierRate(BaseModel):
    carrier_id: int
    carrier_name: str
    rate: float
    estimated_delivery_time: str


class ShipmentTracking(BaseModel):
    shipment_id: int
    tracking_number: str
    current_status: str
    estimated_delivery_date: Optional[datetime]
    tracking_history: list[dict]


class InventoryMovementBase(BaseModel):
    product_id: int
    from_location_id: int
    to_location_id: int
    quantity: int
    reason: str


class InventoryMovementCreate(InventoryMovementBase):
    pass


class InventoryMovement(InventoryMovementBase):
    movement_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class InventoryAdjustmentBase(BaseModel):
    product_id: int
    location_id: int
    quantity_change: int
    reason: str


class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    pass


class InventoryAdjustment(InventoryAdjustmentBase):
    adjustment_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
