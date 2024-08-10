# /server/app/crud/receipt.py

from sqlalchemy import func
from sqlalchemy.orm import Session

from server.app.models import (
    Receipt, ReceiptItem
)
from server.app.schemas import (
    Receipt as ReceiptSchema, ReceiptCreate, ReceiptUpdate,
    ReceiptItem as ReceiptItemSchema, ReceiptItemCreate, ReceiptItemUpdate,
    ReceiptFilter, QualityCheckCreate
)
from .base import CRUDBase


class CRUDReceipt(CRUDBase[Receipt, ReceiptCreate, ReceiptUpdate]):
    def create_with_items(self, db: Session, *, obj_in: ReceiptCreate) -> ReceiptSchema:
        db_obj = Receipt(
            po_id=obj_in.po_id,
            status=obj_in.status
        )
        db.add(db_obj)
        db.flush()
        for item in obj_in.items:
            db_item = ReceiptItem(**item.dict(), receipt_id=db_obj.receipt_id)
            db.add(db_item)
        db.commit()
        db.refresh(db_obj)
        return ReceiptSchema.model_validate(db_obj)

    def update_with_items(self, db: Session, *, db_obj: Receipt, obj_in: ReceiptUpdate) -> ReceiptSchema:
        update_data = obj_in.dict(exclude_unset=True)
        if "items" in update_data:
            items = update_data.pop("items")
            for item in db_obj.receipt_items:
                db.delete(item)
            for item in items:
                db_item = ReceiptItem(**item, receipt_id=db_obj.receipt_id)
                db.add(db_item)
        updated_receipt = super().update(db, db_obj=db_obj, obj_in=update_data)
        return ReceiptSchema.model_validate(updated_receipt)

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: ReceiptFilter) -> list[ReceiptSchema]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(Receipt.status == filter_params.status)
        if filter_params.po_id:
            query = query.filter(Receipt.po_id == filter_params.po_id)
        if filter_params.date_from:
            query = query.filter(Receipt.received_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(Receipt.received_date <= filter_params.date_to)
        receipts = query.offset(skip).limit(limit).all()
        return [ReceiptSchema.model_validate(receipt) for receipt in receipts]

    def report_discrepancy(self, db: Session, *, receipt_id: int, item_id: int, discrepancy: int) -> ReceiptItemSchema:
        item = db.query(ReceiptItem).filter(ReceiptItem.receipt_id == receipt_id,
                                            ReceiptItem.receipt_item_id == item_id).first()
        item.quantity_received += discrepancy
        db.commit()
        db.refresh(item)
        return ReceiptItemSchema.model_validate(item)

    def get_expected_today(self, db: Session) -> int:
        return db.query(func.sum(ReceiptItem.quantity_received)).filter(
            func.date(Receipt.received_date) == func.current_date()).scalar()

    def perform_quality_check(self, db: Session, receipt_id: int, quality_check: QualityCheckCreate) -> ReceiptSchema:
        receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
        if not receipt:
            raise ValueError("Receipt not found")

        receipt_item = next((item for item in receipt.receipt_items if item.product_id == quality_check.product_id),
                            None)
        if receipt_item:
            receipt_item.quality_check_result = quality_check.result
            receipt_item.quality_check_notes = quality_check.notes

        receipt.status = "quality_checked"
        db.commit()
        db.refresh(receipt)
        return ReceiptSchema.model_validate(receipt)


class CRUDReceiptItem(CRUDBase[ReceiptItem, ReceiptItemCreate, ReceiptItemUpdate]):
    pass


receipt = CRUDReceipt(Receipt)
receipt_item = CRUDReceiptItem(ReceiptItem)
