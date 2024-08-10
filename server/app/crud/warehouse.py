# /server/app/crud/warehouse.py

from fastapi import HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from server.app.models import (
    PickList, Receipt, Shipment, LocationInventory, InventoryMovement, InventoryAdjustment
)
from server.app.schemas import (
    InventoryMovement as InventoryMovementSchema,
    InventoryAdjustment as InventoryAdjustmentSchema,
    InventoryAdjustmentCreate,
    LocationInventory as LocationInventorySchema, InventoryMovementCreate, WarehouseStats
)


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

    def get_location_inventory(self, db: Session, *, location_id: int) -> list[LocationInventorySchema]:
        location_inventory = (db.query(LocationInventory)
                              .filter(LocationInventory.location_id == location_id)
                              .all())
        return [LocationInventorySchema.model_validate(inv) for inv in location_inventory]

    def update_location_inventory(self, db: Session, *, location_id: int, product_id: int,
                                  quantity: int) -> LocationInventorySchema:
        inventory = db.query(LocationInventory).filter(
            and_(LocationInventory.location_id == location_id, LocationInventory.product_id == product_id)).first()
        if not inventory:
            inventory = LocationInventory(location_id=location_id, product_id=product_id, quantity=quantity)
            db.add(inventory)
        else:
            inventory.quantity = quantity
        db.commit()
        db.refresh(inventory)
        return LocationInventorySchema.model_validate(inventory)

    def move_inventory(self, db: Session, *, movement: InventoryMovementCreate) -> InventoryMovementSchema:
        # Update the from_location inventory
        from_location_inventory = db.query(LocationInventory).filter(
            LocationInventory.location_id == movement.from_location_id,
            LocationInventory.product_id == movement.product_id
        ).first()
        if from_location_inventory:
            from_location_inventory.quantity -= movement.quantity
        else:
            raise HTTPException(status_code=400, detail="Insufficient inventory in the from location")

        # Update the to_location inventory
        to_location_inventory = db.query(LocationInventory).filter(
            LocationInventory.location_id == movement.to_location_id,
            LocationInventory.product_id == movement.product_id
        ).first()
        if to_location_inventory:
            to_location_inventory.quantity += movement.quantity
        else:
            to_location_inventory = LocationInventory(
                location_id=movement.to_location_id,
                product_id=movement.product_id,
                quantity=movement.quantity
            )
            db.add(to_location_inventory)

        db_movement = InventoryMovement(**movement.dict())
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        return InventoryMovementSchema.model_validate(db_movement)

    def adjust_inventory(self, db: Session, *, adjustment: InventoryAdjustmentCreate) -> InventoryAdjustmentSchema:
        # Update the inventory for the specified location
        location_inventory = db.query(LocationInventory).filter(
            LocationInventory.location_id == adjustment.location_id,
            LocationInventory.product_id == adjustment.product_id
        ).first()
        if location_inventory:
            location_inventory.quantity += adjustment.quantity_change
        else:
            location_inventory = LocationInventory(
                location_id=adjustment.location_id,
                product_id=adjustment.product_id,
                quantity=adjustment.quantity_change
            )
            db.add(location_inventory)

        db_adjustment = InventoryAdjustment(**adjustment.dict())
        db.add(db_adjustment)
        db.commit()
        db.refresh(db_adjustment)
        return InventoryAdjustmentSchema.model_validate(db_adjustment)


whole_warehouse = CRUDWarehouse()
