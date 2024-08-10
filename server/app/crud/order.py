# /server/app/crud/order.py
from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from server.app.models import Order, OrderItem
from server.app.schemas import (
    Order as OrderSchema,
    OrderWithDetails as OrderWithDetailsSchema,
    OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate,
    OrderFilter, OrderSummary, ShippingInfo, BulkOrderImportData,
    BulkOrderImportResult, OrderProcessingTimes
)
from .base import CRUDBase


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create(self, db: Session, *, obj_in: OrderCreate) -> OrderSchema:
        obj_in_data = jsonable_encoder(obj_in)
        items = obj_in_data.pop("items")
        db_obj = self.model(**obj_in_data)
        for item in items:
            db_obj.order_items.append(OrderItem(**item))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return OrderSchema.model_validate(db_obj)

    def get_multi_with_details(self, db: Session, *,
                               skip: int = 0, limit: int = 100,
                               filter_params: OrderFilter) -> list[OrderWithDetailsSchema]:
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

        orders = query.offset(skip).limit(limit).all()
        return [OrderWithDetailsSchema.model_validate(x) for x in orders]

    def get_with_details(self, db: Session, id: int) -> Optional[OrderWithDetailsSchema]:
        current_order = db.query(self.model).options(
            joinedload(Order.customer),
            joinedload(Order.order_items).joinedload(OrderItem.product)
        ).filter(self.model.order_id == id).first()
        return OrderWithDetailsSchema.model_validate(current_order) if current_order else None

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

    def cancel(self, db: Session, *, db_obj: Order) -> OrderSchema:
        db_obj.status = "cancelled"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return OrderSchema.model_validate(db_obj)

    def ship(self, db: Session, *, db_obj: Order, shipping_info: ShippingInfo) -> OrderSchema:
        db_obj.status = "shipped"
        db_obj.shipping_carrier = shipping_info.carrier
        db_obj.tracking_number = shipping_info.tracking_number
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return OrderSchema.model_validate(db_obj)

    def get_by_customer(self, db: Session, *,
                        customer_id: int, skip: int = 0, limit: int = 100) -> list[OrderSchema]:
        orders = (db.query(self.model)
                  .filter(Order.customer_id == customer_id)
                  .offset(skip).limit(limit)
                  .all())
        return [OrderSchema.model_validate(x) for x in orders]

    def cancel_item(self, db: Session, *, order_id: int, item_id: int) -> OrderSchema:
        order = db.query(self.model).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        item = next((item for item in order.order_items if item.order_item_id == item_id), None)
        if not item:
            raise ValueError("Order item not found")

        order.total_amount -= item.quantity * item.unit_price
        db.delete(item)

        if not order.order_items:
            order.status = "cancelled"

        db.add(order)
        db.commit()
        db.refresh(order)
        return OrderSchema.model_validate(order)

    def add_item(self, db: Session, *, order_id: int, item: OrderItemCreate) -> OrderSchema:
        order = db.query(self.model).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        new_item = OrderItem(**item.dict(), order_id=order_id)
        order.order_items.append(new_item)
        order.total_amount += item.quantity * item.unit_price

        db.add(order)
        db.commit()
        db.refresh(order)
        return OrderSchema.model_validate(order)

    def get_backorders(self, db: Session) -> list[OrderSchema]:
        backorders = db.query(self.model).filter(Order.status == "backorder").all()
        return [OrderSchema.model_validate(order) for order in backorders]

    def bulk_import(self, db: Session, *, import_data: BulkOrderImportData) -> BulkOrderImportResult:
        success_count = 0
        failure_count = 0
        errors = []

        for order_data in import_data.orders:
            try:
                self.create(db, obj_in=order_data)
                success_count += 1
            except Exception as e:
                failure_count += 1
                errors.append(f"Error importing order: {str(e)}")

        return BulkOrderImportResult(
            success_count=success_count,
            failure_count=failure_count,
            errors=errors
        )

    def get_processing_times(self, db: Session, *, start_date: datetime, end_date: datetime) -> OrderProcessingTimes:
        processing_times = db.query(
            func.avg(Order.ship_date - Order.order_date).label('avg_time'),
            func.min(Order.ship_date - Order.order_date).label('min_time'),
            func.max(Order.ship_date - Order.order_date).label('max_time')
        ).filter(
            Order.order_date.between(start_date, end_date),
            Order.status == 'shipped'
        ).first()

        return OrderProcessingTimes(
            average_processing_time=processing_times.avg_time.total_seconds() / 3600
            if processing_times.avg_time else 0,
            min_processing_time=processing_times.min_time.total_seconds() / 3600
            if processing_times.min_time else 0,
            max_processing_time=processing_times.max_time.total_seconds() / 3600
            if processing_times.max_time else 0
        )


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemCreate, OrderItemUpdate]):
    pass


order = CRUDOrder(Order)
order_item = CRUDOrderItem(OrderItem)
