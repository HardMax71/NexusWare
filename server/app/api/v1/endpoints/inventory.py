# /server/app/api/v1/endpoints/inventory.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


# Product routes
@router.post("/products", response_model=schemas.Product)
def create_product(
        product: schemas.ProductCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.create(db=db, obj_in=product)


@router.get("/products", response_model=List[schemas.ProductWithCategoryAndInventory])
def read_products(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        product_filter: schemas.ProductFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.get_multi_with_category_and_inventory(db, skip=skip, limit=limit, filter_params=product_filter)


@router.get("/products/{product_id}", response_model=schemas.ProductWithCategoryAndInventory)
def read_product(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    product = crud.product.get_with_category_and_inventory(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
        product_id: int,
        product_in: schemas.ProductUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.product.update(db, db_obj=product, obj_in=product_in)


@router.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.product.remove(db, id=product_id)


@router.post("/products/barcode", response_model=schemas.Product)
def get_product_by_barcode(
        barcode_data: schemas.BarcodeData,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    product = crud.product.get_by_barcode(db, barcode=barcode_data.barcode)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Product Category routes
@router.post("/categories", response_model=schemas.ProductCategory)
def create_category(
        category: schemas.ProductCategoryCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product_category.create(db=db, obj_in=category)


@router.get("/categories", response_model=List[schemas.ProductCategory])
def read_categories(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product_category.get_multi(db, skip=skip, limit=limit)


@router.get("/categories/{category_id}", response_model=schemas.ProductCategory)
def read_category(
        category_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    category = crud.product_category.get(db, id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=schemas.ProductCategory)
def update_category(
        category_id: int,
        category_in: schemas.ProductCategoryUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    category = crud.product_category.get(db, id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.product_category.update(db, db_obj=category, obj_in=category_in)


@router.delete("/categories/{category_id}", response_model=schemas.ProductCategory)
def delete_category(
        category_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    category = crud.product_category.get(db, id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.product_category.remove(db, id=category_id)


# Inventory routes
@router.post("/inventory", response_model=schemas.Inventory)
def create_inventory(
        inventory: schemas.InventoryCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.create(db=db, obj_in=inventory)


@router.get("/inventory", response_model=List[schemas.Inventory])
def read_inventory(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        inventory_filter: schemas.InventoryFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=inventory_filter)


@router.get("/inventory/{inventory_id}", response_model=schemas.Inventory)
def read_inventory_item(
        inventory_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    inventory = crud.inventory.get(db, id=inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory


@router.put("/inventory/{inventory_id}", response_model=schemas.Inventory)
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


@router.post("/inventory/{inventory_id}/adjust", response_model=schemas.Inventory)
def adjust_inventory(
        inventory_id: int,
        adjustment: schemas.InventoryAdjustment,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.adjust_quantity(db, inventory_id=inventory_id, adjustment=adjustment)


@router.post("/inventory/transfer", response_model=schemas.Inventory)
def transfer_inventory(
        transfer: schemas.InventoryTransfer,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.transfer(db, transfer=transfer)


# Location routes
@router.post("/locations", response_model=schemas.Location)
def create_location(
        location: schemas.LocationCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.location.create(db=db, obj_in=location)


@router.get("/locations", response_model=List[schemas.LocationWithInventory])
def read_locations(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        location_filter: schemas.LocationFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.location.get_multi_with_inventory(db, skip=skip, limit=limit, filter_params=location_filter)


@router.get("/locations/{location_id}", response_model=schemas.LocationWithInventory)
def read_location(
        location_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.location.get_with_inventory(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.put("/locations/{location_id}", response_model=schemas.Location)
def update_location(
        location_id: int,
        location_in: schemas.LocationUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.location.get(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return crud.location.update(db, db_obj=location, obj_in=location_in)


@router.delete("/locations/{location_id}", response_model=schemas.Location)
def delete_location(
        location_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    location = crud.location.get(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return crud.location.remove(db, id=location_id)


# Zone routes
@router.post("/zones", response_model=schemas.Zone)
def create_zone(
        zone: schemas.ZoneCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.create(db=db, obj_in=zone)


@router.get("/zones", response_model=List[schemas.ZoneWithLocations])
def read_zones(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        zone_filter: schemas.ZoneFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.get_multi_with_locations(db, skip=skip, limit=limit, filter_params=zone_filter)


@router.get("/zones/{zone_id}", response_model=schemas.ZoneWithLocations)
def read_zone(
        zone_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    zone = crud.zone.get_with_locations(db, id=zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.put("/zones/{zone_id}", response_model=schemas.Zone)
def update_zone(
        zone_id: int,
        zone_in: schemas.ZoneUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    zone = crud.zone.get(db, id=zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return crud.zone.update(db, db_obj=zone, obj_in=zone_in)


@router.delete("/zones/{zone_id}", response_model=schemas.Zone)
def delete_zone(
        zone_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    zone = crud.zone.get(db, id=zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return crud.zone.remove(db, id=zone_id)


# Additional inventory management routes
@router.get("/inventory/report", response_model=schemas.InventoryReport)
def get_inventory_report(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_inventory_report(db)


@router.get("/warehouse/layout", response_model=schemas.WarehouseLayout)
def get_warehouse_layout(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.get_warehouse_layout(db)


@router.post("/inventory/cycle-count", response_model=List[schemas.Inventory])
def perform_cycle_count(
        location_id: int,
        counted_items: List[schemas.InventoryUpdate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.perform_cycle_count(db, location_id=location_id, counted_items=counted_items)


@router.get("/inventory/low-stock", response_model=List[schemas.ProductWithInventory])
def get_low_stock_items(
        threshold: int = Query(10, ge=0),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_low_stock_items(db, threshold=threshold)


@router.get("/inventory/out-of-stock", response_model=List[schemas.Product])
def get_out_of_stock_items(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_out_of_stock_items(db)


@router.post("/inventory/reorder", response_model=List[schemas.Product])
def create_reorder_list(
        threshold: int = Query(10, ge=0),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.create_reorder_list(db, threshold=threshold)


@router.get("/inventory/product-locations/{product_id}", response_model=List[schemas.LocationWithInventory])
def get_product_locations(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_product_locations(db, product_id=product_id)


@router.post("/inventory/batch-update", response_model=List[schemas.Inventory])
def batch_update_inventory(
        updates: List[schemas.InventoryUpdate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.batch_update(db, updates=updates)


@router.get("/inventory/movement-history/{product_id}", response_model=List[schemas.InventoryMovement])
def get_inventory_movement_history(
        product_id: int,
        start_date: datetime = Query(None),
        end_date: datetime = Query(None),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_movement_history(db, product_id=product_id, start_date=start_date, end_date=end_date)


@router.post("/inventory/stocktake", response_model=schemas.StocktakeResult)
def perform_stocktake(
        stocktake: schemas.StocktakeCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.perform_stocktake(db, stocktake=stocktake)


@router.get("/inventory/abc-analysis", response_model=schemas.ABCAnalysisResult)
def perform_abc_analysis(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.perform_abc_analysis(db)


@router.post("/inventory/optimize-locations", response_model=List[schemas.InventoryLocationSuggestion])
def optimize_inventory_locations(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.optimize_locations(db)


@router.get("/products/{product_id}/substitutes", response_model=List[schemas.Product])
def get_product_substitutes(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.get_substitutes(db, product_id=product_id)


@router.post("/products/{product_id}/substitutes", response_model=schemas.Product)
def add_product_substitute(
        product_id: int,
        substitute_id: int = Body(..., embed=True),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.add_substitute(db, product_id=product_id, substitute_id=substitute_id)


@router.get("/expiring-soon", response_model=List[schemas.ProductWithInventory])
def get_expiring_soon_inventory(
        days: int = Query(30, description="Number of days to consider for expiration"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_expiring_soon(db, days=days)


@router.post("/bulk-import", response_model=schemas.BulkImportResult)
def bulk_import_inventory(
        import_data: schemas.BulkImportData,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    return crud.inventory.bulk_import(db, import_data=import_data)


@router.get("/storage-utilization", response_model=schemas.StorageUtilization)
def get_storage_utilization(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.inventory.get_storage_utilization(db)
