# /server/app/crud/order.py
from server.app.models import (Order, OrderItem, Customer,
                               PurchaseOrder, POItem, Supplier)
from server.app.schemas import (OrderCreate, OrderUpdate, OrderItemCreate,
                                OrderItemUpdate, CustomerCreate,
                                CustomerUpdate, PurchaseOrderCreate,
                                PurchaseOrderUpdate,
                                POItemCreate, POItemUpdate,
                                SupplierCreate, SupplierUpdate)
from .base import CRUDBase


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    pass


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemCreate, OrderItemUpdate]):
    pass


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    pass


class CRUDPurchaseOrder(CRUDBase[PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate]):
    pass


class CRUDPOItem(CRUDBase[POItem, POItemCreate, POItemUpdate]):
    pass


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    pass


order = CRUDOrder(Order)
order_item = CRUDOrderItem(OrderItem)
customer = CRUDCustomer(Customer)
purchase_order = CRUDPurchaseOrder(PurchaseOrder)
po_item = CRUDPOItem(POItem)
supplier = CRUDSupplier(Supplier)
