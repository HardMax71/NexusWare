# /server/app/crud/pick_list.py
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from server.app.models import (
    PickList, PickListItem
)
from public_api.shared_schemas import (
    PickList as PickListSchema, PickListCreate, PickListUpdate,
    PickListItem as PickListItemSchema, PickListItemCreate, PickListItemUpdate,
    PickListFilter, PickingPerformance, OptimizedPickingRoute
)
from .base import CRUDBase


class CRUDPickList(CRUDBase[PickList, PickListCreate, PickListUpdate]):
    def create_with_items(self, db: Session, *, obj_in: PickListCreate) -> PickListSchema:
        db_obj = PickList(
            order_id=obj_in.order_id,
            status=obj_in.status
        )
        db.add(db_obj)
        db.flush()
        for item in obj_in.items:
            db_item = PickListItem(**item.model_dump(), pick_list_id=db_obj.pick_list_id)
            db.add(db_item)
        db.commit()
        db.refresh(db_obj)
        return PickListSchema.model_validate(db_obj)

    def update_with_items(self, db: Session, *, db_obj: PickList, obj_in: PickListUpdate) -> PickListSchema:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "items" in update_data:
            items = update_data.pop("items")
            for item in db_obj.pick_list_items:
                db.delete(item)
            for item in items:
                db_item = PickListItem(**item, pick_list_id=db_obj.pick_list_id)
                db.add(db_item)
        updated_pick_list = super().update(db, db_obj=db_obj, obj_in=update_data)
        return PickListSchema.model_validate(updated_pick_list)

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100,
                              filter_params: PickListFilter) -> list[PickListSchema]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(PickList.status == filter_params.status)
        if filter_params.order_id:
            query = query.filter(PickList.order_id == filter_params.order_id)
        if filter_params.date_from:
            query = query.filter(PickList.created_at >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(PickList.created_at <= filter_params.date_to)
        pick_lists = query.offset(skip).limit(limit).all()
        return [PickListSchema.model_validate(pl) for pl in pick_lists]

    def get_performance(self, db: Session, start_date: datetime, end_date: datetime) -> PickingPerformance:
        completed_pick_lists = db.query(PickList).filter(
            PickList.status == "completed",
            PickList.completed_at.between(start_date, end_date)
        ).all()

        total_time = sum((pl.completed_at - pl.created_at).total_seconds() for pl in completed_pick_lists)
        total_items = sum(sum(item.picked_quantity for item in pl.pick_list_items) for pl in completed_pick_lists)

        if len(completed_pick_lists) > 0:
            average_picking_time = total_time / len(completed_pick_lists) / 60  # in minutes
            items_picked_per_hour = (total_items / (total_time / 3600)) if total_time > 0 else 0
            accuracy_rate = sum(1 for pl in completed_pick_lists for item in pl.pick_list_items if
                                item.quantity == item.picked_quantity) / total_items if total_items > 0 else 1
        else:
            average_picking_time = 0
            items_picked_per_hour = 0
            accuracy_rate = 1

        return PickingPerformance(
            average_picking_time=average_picking_time,
            items_picked_per_hour=items_picked_per_hour,
            accuracy_rate=accuracy_rate
        )

    def optimize_route(self, db: Session, pick_list_id: int) -> OptimizedPickingRoute:
        pick_list = db.query(PickList).filter(PickList.pick_list_id == pick_list_id).first()
        if not pick_list:
            raise ValueError("Pick list not found")

        optimized_items = sorted(pick_list.pick_list_items, key=lambda x: (
            x.location.zone_id, x.location.aisle, x.location.rack, x.location.shelf, x.location.bin))

        return OptimizedPickingRoute(
            pick_list_id=pick_list_id,
            optimized_route=[PickListItemSchema.model_validate(item) for item in optimized_items]
        )

    def start(self, db: Session, *, pick_list_id: int, user_id: int) -> PickListSchema:
        current_pick_list = db.query(PickList).filter(PickList.pick_list_id == pick_list_id).first()
        current_pick_list.status = "in_progress"
        db.commit()
        db.refresh(current_pick_list)
        return PickListSchema.model_validate(current_pick_list)

    def complete(self, db: Session, *, pick_list_id: int, user_id: int) -> PickListSchema:
        current_pick_list = db.query(PickList).filter(PickList.pick_list_id == pick_list_id).first()
        current_pick_list.status = "completed"
        current_pick_list.completed_at = func.now()
        db.commit()
        db.refresh(current_pick_list)
        return PickListSchema.model_validate(current_pick_list)


class CRUDPickListItem(CRUDBase[PickListItem, PickListItemCreate, PickListItemUpdate]):
    pass


pick_list = CRUDPickList(PickList)
pick_list_item = CRUDPickListItem(PickListItem)
