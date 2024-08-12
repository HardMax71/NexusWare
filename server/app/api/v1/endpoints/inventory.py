# /server/app/api/v1/endpoints/inventory.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Inventory)
def create_inventory(
        inventory: schemas.InventoryCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.create(db=db, obj_in=inventory)


@router.get("/", response_model=schemas.InventoryList)
def read_inventory(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    inventory_filter: schemas.InventoryFilter = Depends(),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    items = crud.inventory.get_multi_with_products(db, skip=skip, limit=limit, filter_params=inventory_filter)
    total = len(items)
    return {"items": items, "total": total}


@router.post("/transfer", response_model=schemas.Inventory)
def transfer_inventory(
        transfer: schemas.InventoryTransfer,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.transfer(db, transfer=transfer)


@router.get("/report", response_model=schemas.InventoryReport)
def get_inventory_report(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_inventory_report(db)


@router.post("/cycle_count", response_model=List[schemas.Inventory])
def perform_cycle_count(
        location_id: int,
        counted_items: List[schemas.InventoryUpdate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.perform_cycle_count(db, location_id=location_id, counted_items=counted_items)


@router.get("/low_stock", response_model=List[schemas.ProductWithInventory])
def get_low_stock_items(
        threshold: int = Query(10, ge=0),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_low_stock_items(db, threshold=threshold)


@router.get("/out_of_stock", response_model=List[schemas.Product])
def get_out_of_stock_items(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_out_of_stock_items(db)


@router.post("/reorder", response_model=List[schemas.Product])
def create_reorder_list(
        threshold: int = Query(10, ge=0),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.create_reorder_list(db, threshold=threshold)


@router.get("/product_locations/{product_id}", response_model=List[schemas.LocationWithInventory])
def get_product_locations(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_product_locations(db, product_id=product_id)


@router.post("/batch_update", response_model=List[schemas.Inventory])
def batch_update_inventory(
        updates: List[schemas.InventoryUpdate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.batch_update(db, updates=updates)


@router.get("/movement_history/{product_id}", response_model=List[schemas.InventoryMovement])
def get_inventory_movement_history(
        product_id: int,
        start_date: datetime = Query(None),
        end_date: datetime = Query(None),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_movement_history(db, product_id=product_id, start_date=start_date, end_date=end_date)


@router.get("/summary", response_model=schemas.InventorySummary)
def get_inventory_summary(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_inventory_summary(db)


@router.post("/stocktake", response_model=schemas.StocktakeResult)
def perform_stocktake(
        stocktake: schemas.StocktakeCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.perform_stocktake(db, stocktake=stocktake)


@router.get("/abc_analysis", response_model=schemas.ABCAnalysisResult)
def perform_abc_analysis(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.perform_abc_analysis(db)


@router.post("/optimize_locations", response_model=List[schemas.InventoryLocationSuggestion])
def optimize_inventory_locations(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.optimize_locations(db)


@router.get("/expiring_soon", response_model=List[schemas.ProductWithInventory])
def get_expiring_soon_inventory(
        days: int = Query(30, description="Number of days to consider for expiration"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_expiring_soon(db, days=days)


@router.post("/bulk_import", response_model=schemas.BulkImportResult)
def bulk_import_inventory(
        import_data: schemas.BulkImportData,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.inventory.bulk_import(db, import_data=import_data)


@router.get("/storage_utilization", response_model=schemas.StorageUtilization)
def get_storage_utilization(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_storage_utilization(db)


@router.get("/{inventory_id}", response_model=schemas.Inventory)
def read_inventory_item(
        inventory_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    inventory = crud.inventory.get(db, id=inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory


@router.put("/{inventory_id}", response_model=schemas.Inventory)
def update_inventory(
        inventory_id: int,
        inventory_in: schemas.InventoryUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    inventory = crud.inventory.get(db, id=inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return crud.inventory.update(db, db_obj=inventory, obj_in=inventory_in)


@router.post("/{inventory_id}/adjust", response_model=schemas.Inventory)
def adjust_inventory(
        inventory_id: int,
        adjustment: schemas.InventoryAdjustment,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.adjust_quantity(db, inventory_id=inventory_id, adjustment=adjustment)
