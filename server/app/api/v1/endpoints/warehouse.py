# /server/app/api/v1/endpoints/warehouse.py

from fastapi import APIRouter, Depends, Path, Body
from sqlalchemy.orm import Session

from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.get("/layout", response_model=shared_schemas.WarehouseLayout)
def get_warehouse_layout(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.get_warehouse_layout(db)

@router.get("/stats", response_model=shared_schemas.WarehouseStats)
def get_warehouse_stats(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.get_stats(db)


@router.get("/inventory/{location_id}", response_model=list[shared_schemas.LocationInventory])
def get_location_inventory(
        location_id: int = Path(..., title="The ID of the location to get inventory for"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.get_location_inventory(db, location_id=location_id)


@router.put("/inventory/{location_id}/{product_id}", response_model=shared_schemas.LocationInventory)
def update_location_inventory(
        location_id: int = Path(..., title="The ID of the location"),
        product_id: int = Path(..., title="The ID of the product"),
        inventory_update: shared_schemas.LocationInventoryUpdate = Body(..., title="Inventory update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.update_location_inventory(db, location_id=location_id, product_id=product_id,
                                                          quantity=inventory_update.quantity)


@router.post("/inventory/move", response_model=shared_schemas.InventoryMovement)
def move_inventory(
        movement: shared_schemas.InventoryMovement,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.move_inventory(db, movement=movement)


@router.post("/inventory/adjust", response_model=shared_schemas.InventoryAdjustment)
def adjust_inventory(
        adjustment: shared_schemas.InventoryAdjustment,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.whole_warehouse.adjust_inventory(db, adjustment=adjustment)


