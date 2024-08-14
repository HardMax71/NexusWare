# /server/app/crud/purchase_order.py
from typing import Optional

from sqlalchemy.orm import Session

from public_api.shared_schemas import (
    PurchaseOrder as PurchaseOrderSchema,
    PurchaseOrderWithDetails as PurchaseOrderWithDetailsSchema,
    POItem as POItemSchema,
    POItemCreate, POItemUpdate,
    PurchaseOrderFilter, POItemReceive, PurchaseOrderCreate, PurchaseOrderUpdate
)
from server.app.models import PurchaseOrder, POItem, Supplier
from .base import CRUDBase


class CRUDPurchaseOrder(CRUDBase[PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate]):
    def create(self, db: Session, *, obj_in: PurchaseOrderCreate) -> PurchaseOrderSchema:
        obj_in_data = obj_in.model_dump()
        items = obj_in_data.pop("items")
        db_obj = self.model(**obj_in_data)
        for item in items:
            db_obj.po_items.append(POItem(**item))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return PurchaseOrderSchema.model_validate(db_obj)

    def get_multi_with_details(self, db: Session, *, skip: int = 0, limit: int = 100,
                               filter_params: PurchaseOrderFilter) -> list[PurchaseOrderWithDetailsSchema]:
        query = db.query(self.model).join(Supplier)
        if filter_params.supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == filter_params.supplier_id)
        if filter_params.status:
            query = query.filter(PurchaseOrder.status == filter_params.status)
        if filter_params.date_from:
            query = query.filter(PurchaseOrder.order_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(PurchaseOrder.order_date <= filter_params.date_to)

        purchase_orders = query.offset(skip).limit(limit).all()
        return [PurchaseOrderWithDetailsSchema.model_validate(po) for po in purchase_orders]

    def get_with_details(self, db: Session, id: int) -> Optional[PurchaseOrderWithDetailsSchema]:
        purchase_order = (db.query(self.model)
                          .filter(self.model.id == id)
                          .join(Supplier)
                          .first())
        return PurchaseOrderWithDetailsSchema.model_validate(purchase_order) if purchase_order else None

    def receive(self, db: Session, *, db_obj: PurchaseOrder,
                received_items: list[POItemReceive]) -> PurchaseOrderSchema:
        for item in received_items:
            cur_po_item = next((i for i in db_obj.po_items if i.id == item.id), None)
            if cur_po_item:
                cur_po_item.received_quantity = item.received_quantity
        db_obj.status = "received"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return PurchaseOrderSchema.model_validate(db_obj)

    def get_by_supplier(self, db: Session, *,
                        supplier_id: int, skip: int = 0, limit: int = 100) -> list[PurchaseOrderSchema]:
        purchase_orders = (db.query(self.model)
                           .filter(PurchaseOrder.supplier_id == supplier_id)
                           .offset(skip).limit(limit)
                           .all())
        return [PurchaseOrderSchema.model_validate(po) for po in purchase_orders]


class CRUDPOItem(CRUDBase[POItem, POItemCreate, POItemUpdate]):
    def get_by_product(self, db: Session, *, product_id: int, skip: int = 0, limit: int = 100) -> list[POItemSchema]:
        po_items = (db.query(self.model)
                    .filter(POItem.product_id == product_id)
                    .offset(skip).limit(limit)
                    .all())
        return [POItemSchema.model_validate(item) for item in po_items]

    def get_pending_receipt(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[POItemSchema]:
        po_items = db.query(self.model).join(PurchaseOrder).filter(
            PurchaseOrder.status.in_(["open", "partial"])
        ).offset(skip).limit(limit).all()
        return [POItemSchema.model_validate(item) for item in po_items]


purchase_order = CRUDPurchaseOrder(PurchaseOrder)
po_item = CRUDPOItem(POItem)
