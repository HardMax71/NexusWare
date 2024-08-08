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


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None
    items: Optional[List[OrderItemUpdate]] = None


class Order(OrderBase):
    order_id: int
    order_date: datetime
    items: List[OrderItem] = []

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
    items: List[POItem] = []

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
