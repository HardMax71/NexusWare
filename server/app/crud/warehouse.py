# /server/app/crud/warehouse.py
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from server.app.models import (PickList, PickListItem,
                               Receipt, ReceiptItem, Shipment, Carrier)
from server.app.schemas import (PickListCreate, PickListUpdate,
                                PickListItemCreate, PickListItemUpdate, ReceiptCreate,
                                ReceiptUpdate, ReceiptItemCreate, ReceiptItemUpdate,
                                ShipmentCreate, ShipmentUpdate,
                                CarrierCreate, CarrierUpdate, PickListFilter, InventoryAdjustment, LocationInventory,
                                InventoryMovement, WarehouseStats, ShipmentFilter, ReceiptFilter)
from .base import CRUDBase


class CRUDPickList(CRUDBase[PickList, PickListCreate, PickListUpdate]):
    def create_with_items(self, db: Session, *, obj_in: PickListCreate) -> PickList:
        db_obj = PickList(
            order_id=obj_in.order_id,
            status=obj_in.status
        )
        db.add(db_obj)
        db.flush()
        for item in obj_in.items:
            db_item = PickListItem(**item.dict(), pick_list_id=db_obj.pick_list_id)
            db.add(db_item)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_items(self, db: Session, *, db_obj: PickList, obj_in: PickListUpdate) -> PickList:
        update_data = obj_in.dict(exclude_unset=True)
        if "items" in update_data:
            items = update_data.pop("items")
            for item in db_obj.pick_list_items:
                db.delete(item)
            for item in items:
                db_item = PickListItem(**item, pick_list_id=db_obj.pick_list_id)
                db.add(db_item)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100,
                              filter_params: PickListFilter) -> list[PickList]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(PickList.status == filter_params.status)
        if filter_params.order_id:
            query = query.filter(PickList.order_id == filter_params.order_id)
        if filter_params.date_from:
            query = query.filter(PickList.created_at >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(PickList.created_at <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()


class CRUDPickListItem(CRUDBase[PickListItem, PickListItemCreate, PickListItemUpdate]):
    pass


class CRUDReceipt(CRUDBase[Receipt, ReceiptCreate, ReceiptUpdate]):
    def create_with_items(self, db: Session, *, obj_in: ReceiptCreate) -> Receipt:
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
        return db_obj

    def update_with_items(self, db: Session, *, db_obj: Receipt, obj_in: ReceiptUpdate) -> Receipt:
        update_data = obj_in.dict(exclude_unset=True)
        if "items" in update_data:
            items = update_data.pop("items")
            for item in db_obj.receipt_items:
                db.delete(item)
            for item in items:
                db_item = ReceiptItem(**item, receipt_id=db_obj.receipt_id)
                db.add(db_item)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: ReceiptFilter) -> list[Receipt]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(Receipt.status == filter_params.status)
        if filter_params.po_id:
            query = query.filter(Receipt.po_id == filter_params.po_id)
        if filter_params.date_from:
            query = query.filter(Receipt.received_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(Receipt.received_date <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()


class CRUDReceiptItem(CRUDBase[ReceiptItem, ReceiptItemCreate, ReceiptItemUpdate]):
    pass


class CRUDShipment(CRUDBase[Shipment, ShipmentCreate, ShipmentUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: ShipmentFilter) -> list[Shipment]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(Shipment.status == filter_params.status)
        if filter_params.order_id:
            query = query.filter(Shipment.order_id == filter_params.order_id)
        if filter_params.carrier_id:
            query = query.filter(Shipment.carrier_id == filter_params.carrier_id)
        if filter_params.date_from:
            query = query.filter(Shipment.ship_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(Shipment.ship_date <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()


class CRUDCarrier(CRUDBase[Carrier, CarrierCreate, CarrierUpdate]):
    pass


class CRUDWarehouse:
    def get_stats(self, db: Session) -> WarehouseStats:
        total_pick_lists = db.query(func.count(PickList.pick_list_id)).scalar()
        completed_pick_lists = db.query(func.count(PickList.pick_list_id)).filter(
            PickList.status == "completed").scalar()
        total_receipts = db.query(func.count(Receipt.receipt_id)).scalar()
        completed_receipts = db.query(func.count(Receipt.receipt_id)).filter(Receipt.status == "completed").scalar()
        total_shipments = db.query(func.count(Shipment.shipment_id)).scalar()
        completed_shipments = db.query(func.count(Shipment.shipment_id)).filter(Shipment.status == "completed").scalar()

        return WarehouseStats(
            total_pick_lists=total_pick_lists,
            completed_pick_lists=completed_pick_lists,
            total_receipts=total_receipts,
            completed_receipts=completed_receipts,
            total_shipments=total_shipments,
            completed_shipments=completed_shipments
        )

    def get_location_inventory(self, db: Session, *, location_id: int) -> list[LocationInventory]:
        return db.query(LocationInventory).filter(LocationInventory.location_id == location_id).all()

    def update_location_inventory(self, db: Session, *, location_id: int, product_id: int,
                                  quantity: int) -> LocationInventory:
        inventory = db.query(LocationInventory).filter(
            and_(
                LocationInventory.location_id == location_id,
                LocationInventory.product_id == product_id
            )
        ).first()
        if not inventory:
            inventory = LocationInventory(location_id=location_id, product_id=product_id, quantity=quantity)
            db.add(inventory)
        else:
            inventory.quantity = quantity
        db.commit()
        db.refresh(inventory)
        return inventory

    def move_inventory(self, db: Session, *, movement: InventoryMovement) -> InventoryMovement:
        # Decrease quantity in the source location
        self.update_location_inventory(
            db,
            location_id=movement.from_location_id,
            product_id=movement.product_id,
            quantity=LocationInventory.quantity - movement.quantity
        )

        # Increase quantity in the destination location
        self.update_location_inventory(
            db,
            location_id=movement.to_location_id,
            product_id=movement.product_id,
            quantity=LocationInventory.quantity + movement.quantity
        )

        # Record the movement
        db_movement = InventoryMovement(**movement.dict())
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        return db_movement

    def adjust_inventory(self, db: Session, *, adjustment: InventoryAdjustment) -> InventoryAdjustment:
        self.update_location_inventory(
            db,
            location_id=adjustment.location_id,
            product_id=adjustment.product_id,
            quantity=LocationInventory.quantity + adjustment.quantity_change
        )

        # Record the adjustment
        db_adjustment = InventoryAdjustment(**adjustment.dict())
        db.add(db_adjustment)
        db.commit()
        db.refresh(db_adjustment)
        return db_adjustment


pick_list = CRUDPickList(PickList)
receipt = CRUDReceipt(Receipt)
shipment = CRUDShipment(Shipment)
carrier = CRUDCarrier(Carrier)
warehouse = CRUDWarehouse()
pick_list_item = CRUDPickListItem(PickListItem)
receipt_item = CRUDReceiptItem(ReceiptItem)
