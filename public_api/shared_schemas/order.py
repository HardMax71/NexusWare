from enum import Enum

from pydantic import BaseModel

from public_api.shared_schemas import Product


class OrderStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class OrderItemBase(BaseModel):
    product: Product = None
    quantity: int
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    id: int | None = None
    product_id: int | None = None
    quantity: int | None = None
    unit_price: float | None = None


class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_id: int
    status: OrderStatus
    total_amount: float
    shipping_name: str | None = None
    shipping_address_line1: str | None = None
    shipping_city: str | None = None
    shipping_state: str | None = None
    shipping_postal_code: str | None = None
    shipping_country: str | None = None
    shipping_phone: str | None = None
    ship_date: int | None = None


class OrderCreate(OrderBase):
    items: list[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_id: int | None = None
    status: OrderStatus | None = None
    total_amount: float | None = None
    shipping_name: str | None = None
    shipping_address_line1: str | None = None
    shipping_city: str | None = None
    shipping_state: str | None = None
    shipping_postal_code: str | None = None
    shipping_country: str | None = None
    shipping_phone: str | None = None
    ship_date: int | None = None
    items: list[OrderItemUpdate] | None = None


class Order(OrderBase):
    id: int
    order_date: int
    order_items: list[OrderItem] = []

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class Customer(CustomerBase):
    id: int

    class Config:
        from_attributes = True


class POItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class POItemCreate(POItemBase):
    pass


class POItemUpdate(BaseModel):
    product_id: int | None = None
    quantity: int | None = None
    unit_price: float | None = None


class POItem(POItemBase):
    id: int
    po_id: int

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    supplier_id: int
    status: OrderStatus
    expected_delivery_date: int | None = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: list[POItemCreate]


class PurchaseOrderUpdate(BaseModel):
    supplier_id: int | None = None
    status: OrderStatus | None = None
    expected_delivery_date: int | None = None
    items: list[POItemUpdate] | None = None


class PurchaseOrder(PurchaseOrderBase):
    id: int
    order_date: int
    po_items: list[POItem] = []

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class Supplier(SupplierBase):
    id: int

    class Config:
        from_attributes = True


class OrderFilter(BaseModel):
    customer_id: int | None = None
    status: OrderStatus | None = None
    order_date_from: int | None = None
    order_date_to: int | None = None
    ship_date_from: int | None = None
    ship_date_to: int | None = None


class OrderSummary(BaseModel):
    total_orders: int
    total_revenue: float
    average_order_value: float


class CustomerFilter(BaseModel):
    name: str | None = None
    email: str | None = None


class PurchaseOrderFilter(BaseModel):
    supplier_id: int | None = None
    status: OrderStatus | None = None
    date_from: int | None = None
    date_to: int | None = None


class SupplierFilter(BaseModel):
    name: str | None = None
    contact_person: str | None = None


class OrderWithDetails(Order):
    customer: Customer
    order_items: list[OrderItem]


class PurchaseOrderWithDetails(PurchaseOrder):
    supplier: Supplier
    po_items: list[POItem]


class ShippingInfo(BaseModel):
    carrier: str
    carrier_id: int
    tracking_number: str


class POItemReceive(BaseModel):
    id: int
    received_quantity: int


class OrderProcessingTimes(BaseModel):
    average_processing_time: float
    min_processing_time: float
    max_processing_time: float
    average_shipping_time: float
    min_shipping_time: float
    max_shipping_time: float


class BulkOrderImportData(BaseModel):
    orders: list[OrderCreate]


class BulkOrderImportResult(BaseModel):
    success_count: int
    failure_count: int
    errors: list[str]
