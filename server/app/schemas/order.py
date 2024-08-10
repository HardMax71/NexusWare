# /server/app/schemas/order.py
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None


class OrderItem(OrderItemBase):
    order_item_id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_id: int
    status: str
    total_amount: float
    shipping_name: Optional[str] = None
    shipping_address_line1: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: Optional[str] = None
    shipping_phone: Optional[str] = None
    ship_date: Optional[datetime] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None
    shipping_name: Optional[str] = None
    shipping_address_line1: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: Optional[str] = None
    shipping_phone: Optional[str] = None
    ship_date: Optional[datetime] = None
    items: Optional[List[OrderItemUpdate]] = None


class Order(OrderBase):
    order_id: int
    order_date: datetime
    order_items: List[OrderItem] = []

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Customer(CustomerBase):
    customer_id: int

    class Config:
        from_attributes = True


class POItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class POItemCreate(POItemBase):
    pass


class POItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None


class POItem(POItemBase):
    po_item_id: int
    po_id: int

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    supplier_id: int
    status: str
    expected_delivery_date: Optional[datetime] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[POItemCreate]


class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    status: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    items: Optional[List[POItemUpdate]] = None


class PurchaseOrder(PurchaseOrderBase):
    po_id: int
    order_date: datetime
    po_items: List[POItem] = []

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Supplier(SupplierBase):
    supplier_id: int

    class Config:
        from_attributes = True


class OrderFilter(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    order_date_from: Optional[datetime] = None
    order_date_to: Optional[datetime] = None
    ship_date_from: Optional[datetime] = None
    ship_date_to: Optional[datetime] = None


class OrderSummary(BaseModel):
    total_orders: int
    total_revenue: float
    average_order_value: float


class CustomerFilter(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class PurchaseOrderFilter(BaseModel):
    supplier_id: Optional[int] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class SupplierFilter(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None


class OrderWithDetails(Order):
    customer: Customer
    order_items: List[OrderItem]


class PurchaseOrderWithDetails(PurchaseOrder):
    supplier: Supplier
    po_items: List[POItem]


class ShippingInfo(BaseModel):
    carrier: str
    tracking_number: str


class POItemReceive(BaseModel):
    po_item_id: int
    received_quantity: int


class OrderProcessingTimes(BaseModel):
    average_processing_time: float
    min_processing_time: float
    max_processing_time: float
    average_shipping_time: float
    min_shipping_time: float
    max_shipping_time: float


class BulkOrderImportData(BaseModel):
    orders: List[OrderCreate]


class BulkOrderImportResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[str]
