from enum import Enum

from pydantic import BaseModel

from public_api.shared_schemas import Order


class ShipmentStatus(str, Enum):
    PENDING = "Pending"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"


class PickListItemBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    picked_quantity: int = 0


class PickListItemCreate(PickListItemBase):
    pass


class PickListItemUpdate(BaseModel):
    product_id: int | None = None
    location_id: int | None = None
    quantity: int | None = None
    picked_quantity: int | None = None


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
    order_id: int | None = None
    status: str | None = None
    items: list[PickListItemUpdate] | None = None


class PickList(PickListBase):
    pick_list_id: int
    created_at: int
    completed_at: int | None = None
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
    product_id: int | None = None
    quantity_received: int | None = None
    location_id: int | None = None


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
    po_id: int | None = None
    status: str | None = None
    items: list[ReceiptItemUpdate] | None = None


class Receipt(ReceiptBase):
    receipt_id: int
    received_date: int
    items: list[ReceiptItem] = []

    class Config:
        from_attributes = True


class ShipmentBase(BaseModel):
    order_id: int
    carrier_id: int
    tracking_number: str | None = None
    status: ShipmentStatus
    label_id: str | None = None
    label_download_url: str | None = None


class ShipmentCreate(ShipmentBase):
    ship_date: int | None = None


class ShipmentUpdate(BaseModel):
    order_id: int | None = None
    carrier_id: int | None = None
    tracking_number: str | None = None
    status: ShipmentStatus | None = None
    ship_date: int | None = None
    label_id: str | None = None
    label_download_url: str | None = None


class Shipment(ShipmentBase):
    id: int
    ship_date: int | None = None

    class Config:
        from_attributes = True


class CarrierBase(BaseModel):
    name: str
    contact_info: str | None = None


class CarrierCreate(CarrierBase):
    pass


class CarrierUpdate(BaseModel):
    name: str | None = None
    contact_info: str | None = None


class Carrier(CarrierBase):
    id: int

    class Config:
        from_attributes = True


class PickListFilter(BaseModel):
    status: str | None = None
    order_id: int | None = None
    date_from: int | None = None
    date_to: int | None = None


class ReceiptFilter(BaseModel):
    status: str | None = None
    po_id: int | None = None
    date_from: int | None = None
    date_to: int | None = None


class ShipmentFilter(BaseModel):
    status: ShipmentStatus | None = None
    order_id: int | None = None
    carrier_id: int | None = None
    date_from: int | None = None
    date_to: int | None = None


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

    class Config:
        from_attributes = True


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
    notes: str | None = None


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
    estimated_delivery_date: int | None
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
    name: str | None = None
    type: str | None = None
    status: str | None = None
    capacity: int | None = None


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
    yard_location_id: int | None = None
    appointment_time: int | None = None
    carrier_id: int | None = None
    type: str | None = None
    status: str | None = None
    actual_arrival_time: int | None = None
    actual_departure_time: int | None = None


class DockAppointment(DockAppointmentBase):
    appointment_id: int
    actual_arrival_time: int | None = None
    actual_departure_time: int | None = None

    class Config:
        from_attributes = True


class YardLocationFilter(BaseModel):
    type: str | None = None
    status: str | None = None


class DockAppointmentFilter(BaseModel):
    yard_location_id: int | None = None
    carrier_id: int | None = None
    type: str | None = None
    status: str | None = None
    date_from: int | None = None
    date_to: int | None = None


class YardManagementStats(BaseModel):
    total_yard_locations: int
    occupied_yard_locations: int
    total_appointments: int
    on_time_appointments: int
    delayed_appointments: int


class ShipmentWithDetails(Shipment):
    order: Order | None = None
    carrier: Carrier | None = None
