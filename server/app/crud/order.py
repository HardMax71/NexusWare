# /server/app/crud/order.py
from datetime import datetime
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from server.app.models import Order, OrderItem, Customer, PurchaseOrder, POItem, Supplier
from server.app.schemas import (OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate,
                                CustomerCreate, CustomerUpdate, PurchaseOrderCreate, PurchaseOrderUpdate,
                                POItemCreate, POItemUpdate, SupplierCreate, SupplierUpdate,
                                OrderFilter, CustomerFilter, PurchaseOrderFilter, SupplierFilter,
                                OrderSummary, POItemReceive, ShippingInfo)
from .base import CRUDBase


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create(self, db: Session, *, obj_in: OrderCreate) -> Order:
        obj_in_data = jsonable_encoder(obj_in)
        items = obj_in_data.pop("items")
        db_obj = self.model(**obj_in_data)
        for item in items:
            db_obj.order_items.append(OrderItem(**item))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_with_details(self, db: Session, *,
                               skip: int = 0, limit: int = 100,
                               filter_params: OrderFilter) -> List[Order]:
        query = db.query(self.model).options(
            joinedload(Order.customer),
            joinedload(Order.order_items).joinedload(OrderItem.product)
        )
        if filter_params.customer_id:
            query = query.filter(Order.customer_id == filter_params.customer_id)
        if filter_params.status:
            query = query.filter(Order.status == filter_params.status)
        if filter_params.date_from:
            query = query.filter(Order.order_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(Order.order_date <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, id: int) -> Optional[Order]:
        return db.query(self.model).options(
            joinedload(Order.customer),
            joinedload(Order.order_items).joinedload(OrderItem.product)
        ).filter(self.model.order_id == id).first()

    def get_summary(self, db: Session, date_from: Optional[datetime], date_to: Optional[datetime]) -> OrderSummary:
        query = db.query(func.count(Order.order_id).label("total_orders"),
                         func.sum(Order.total_amount).label("total_revenue"))
        if date_from:
            query = query.filter(Order.order_date >= date_from)
        if date_to:
            query = query.filter(Order.order_date <= date_to)
        result = query.first()
        return OrderSummary(
            total_orders=result.total_orders,
            total_revenue=result.total_revenue,
            average_order_value=result.total_revenue / result.total_orders if result.total_orders > 0 else 0
        )

    def cancel(self, db: Session, *, db_obj: Order) -> Order:
        db_obj.status = "cancelled"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def ship(self, db: Session, *, db_obj: Order, shipping_info: ShippingInfo) -> Order:
        db_obj.status = "shipped"
        db_obj.shipping_carrier = shipping_info.carrier
        db_obj.tracking_number = shipping_info.tracking_number
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_customer(self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(self.model).filter(Order.customer_id == customer_id).offset(skip).limit(limit).all()


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemCreate, OrderItemUpdate]):
    pass


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100, filter_params: CustomerFilter) -> \
            List[Customer]:
        query = db.query(self.model)
        if filter_params.name:
            query = query.filter(Customer.name.ilike(f"%{filter_params.name}%"))
        if filter_params.email:
            query = query.filter(Customer.email == filter_params.email)
        return query.offset(skip).limit(limit).all()


class CRUDPurchaseOrder(CRUDBase[PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate]):
    def create(self, db: Session, *, obj_in: PurchaseOrderCreate) -> PurchaseOrder:
        obj_in_data = jsonable_encoder(obj_in)
        items = obj_in_data.pop("items")
        db_obj = self.model(**obj_in_data)
        for item in items:
            db_obj.po_items.append(POItem(**item))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_with_details(self, db: Session, *, skip: int = 0, limit: int = 100,
                               filter_params: PurchaseOrderFilter) -> List[PurchaseOrder]:
        query = db.query(self.model).join(Supplier)
        if filter_params.supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == filter_params.supplier_id)
        if filter_params.status:
            query = query.filter(PurchaseOrder.status == filter_params.status)
        if filter_params.date_from:
            query = query.filter(PurchaseOrder.order_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(PurchaseOrder.order_date <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, id: int) -> Optional[PurchaseOrder]:
        return db.query(self.model).filter(self.model.po_id == id).join(Supplier).first()

    def receive(self, db: Session, *, db_obj: PurchaseOrder, received_items: List[POItemReceive]) -> PurchaseOrder:
        for item in received_items:
            po_item = next((i for i in db_obj.po_items if i.po_item_id == item.po_item_id), None)
            if po_item:
                po_item.received_quantity = item.received_quantity
        db_obj.status = "received"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_supplier(self, db: Session, *, supplier_id: int, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        return db.query(self.model).filter(PurchaseOrder.supplier_id == supplier_id).offset(skip).limit(limit).all()


class CRUDPOItem(CRUDBase[POItem, POItemCreate, POItemUpdate]):
    def get_by_product(self, db: Session, *, product_id: int, skip: int = 0, limit: int = 100) -> List[POItem]:
        return db.query(self.model).filter(POItem.product_id == product_id).offset(skip).limit(limit).all()

    def get_pending_receipt(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[POItem]:
        return db.query(self.model).join(PurchaseOrder).filter(
            PurchaseOrder.status.in_(["open", "partial"]),
            POItem.quantity > POItem.received_quantity
        ).offset(skip).limit(limit).all()


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100, filter_params: SupplierFilter) -> \
            List[Supplier]:
        query = db.query(self.model)
        if filter_params.name:
            query = query.filter(Supplier.name.ilike(f"%{filter_params.name}%"))
        if filter_params.contact_person:
            query = query.filter(Supplier.contact_person.ilike(f"%{filter_params.contact_person}%"))
        return query.offset(skip).limit(limit).all()


order = CRUDOrder(Order)
order_item = CRUDOrderItem(OrderItem)
customer = CRUDCustomer(Customer)
purchase_order = CRUDPurchaseOrder(PurchaseOrder)
po_item = CRUDPOItem(POItem)
supplier = CRUDSupplier(Supplier)
