# /server/app/api/v1/endpoints/warehouse.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.get("/layout", response_model=schemas.WarehouseLayout)
def get_warehouse_layout(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.get_warehouse_layout(db)

@router.get("/stats", response_model=schemas.WarehouseStats)
def get_warehouse_stats(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.get_stats(db)


@router.get("/inventory/{location_id}", response_model=List[schemas.LocationInventory])
def get_location_inventory(
        location_id: int = Path(..., title="The ID of the location to get inventory for"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.get_location_inventory(db, location_id=location_id)


@router.put("/inventory/{location_id}/{product_id}", response_model=schemas.LocationInventory)
def update_location_inventory(
        location_id: int = Path(..., title="The ID of the location"),
        product_id: int = Path(..., title="The ID of the product"),
        inventory_update: schemas.LocationInventoryUpdate = Body(..., title="Inventory update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.update_location_inventory(db, location_id=location_id, product_id=product_id,
                                                          quantity=inventory_update.quantity)


@router.post("/inventory/move", response_model=schemas.InventoryMovement)
def move_inventory(
        movement: schemas.InventoryMovement,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.move_inventory(db, movement=movement)


@router.post("/inventory/adjust", response_model=schemas.InventoryAdjustment)
def adjust_inventory(
        adjustment: schemas.InventoryAdjustment,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.adjust_inventory(db, adjustment=adjustment)


