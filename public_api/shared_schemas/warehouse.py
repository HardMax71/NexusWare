# /server/app/shared_schemas/warehouse.py
from typing import Optional, List

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
    items: List[PickListItemCreate]


class PickListUpdate(BaseModel):
    order_id: Optional[int] = None
    status: Optional[str] = None
    items: Optional[List[PickListItemUpdate]] = None


class PickList(PickListBase):
    pick_list_id: int
    created_at: int
    completed_at: Optional[int] = None
    items: List[PickListItem] = []

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
    items: List[ReceiptItemCreate]


class ReceiptUpdate(BaseModel):
    po_id: Optional[int] = None
    status: Optional[str] = None
    items: Optional[List[ReceiptItemUpdate]] = None


class Receipt(ReceiptBase):
    receipt_id: int
    received_date: int
    items: List[ReceiptItem] = []

    class Config:
        from_attributes = True


class ShipmentBase(BaseModel):
    order_id: int
    carrier_id: int
    tracking_number: Optional[str] = None
    status: str
    label_id: Optional[str] = None
    label_download_url: Optional[str] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    order_id: Optional[int] = None
    carrier_id: Optional[int] = None
    tracking_number: Optional[str] = None
    status: Optional[str] = None
    ship_date: Optional[int] = None
    label_id: Optional[str] = None
    label_download_url: Optional[str] = None


class Shipment(ShipmentBase):
    shipment_id: int
    ship_date: Optional[int] = None

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
    date_from: Optional[int] = None
    date_to: Optional[int] = None


class ReceiptFilter(BaseModel):
    status: Optional[str] = None
    po_id: Optional[int] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None


class ShipmentFilter(BaseModel):
    status: Optional[str] = None
    order_id: Optional[int] = None
    carrier_id: Optional[int] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None


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
    optimized_route: List[PickListItem]


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
    estimated_delivery_date: Optional[int]
    tracking_history: List[dict]


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
    timestamp: int

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
    timestamp: int

    class Config:
        from_attributes = True


class YardLocationBase(BaseModel):
    name: str
    type: str
    status: str
    capacity: int = 1


class YardLocationCreate(YardLocationBase):
    pass


class YardLocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    capacity: Optional[int] = None


class YardLocation(YardLocationBase):
    yard_location_id: int

    class Config:
        from_attributes = True


class DockAppointmentBase(BaseModel):
    yard_location_id: int
    appointment_time: int
    carrier_id: int
    type: str
    status: str


class DockAppointmentCreate(DockAppointmentBase):
    pass


class DockAppointmentUpdate(BaseModel):
    yard_location_id: Optional[int] = None
    appointment_time: Optional[int] = None
    carrier_id: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None
    actual_arrival_time: Optional[int] = None
    actual_departure_time: Optional[int] = None


class DockAppointment(DockAppointmentBase):
    appointment_id: int
    actual_arrival_time: Optional[int] = None
    actual_departure_time: Optional[int] = None

    class Config:
        from_attributes = True


class YardLocationFilter(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None


class DockAppointmentFilter(BaseModel):
    yard_location_id: Optional[int] = None
    carrier_id: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None


class YardManagementStats(BaseModel):
    total_yard_locations: int
    occupied_yard_locations: int
    total_appointments: int
    on_time_appointments: int
    delayed_appointments: int
