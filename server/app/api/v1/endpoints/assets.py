# /server/app/api/v1/endpoints/assets.py
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


# Asset routes
@router.post("/", response_model=schemas.Asset)
def create_asset(
        asset: schemas.AssetCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset.create(db=db, obj_in=asset)


@router.get("/", response_model=schemas.AssetWithMaintenanceList)
def read_assets(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        asset_filter: schemas.AssetFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    assets = crud.asset.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=asset_filter)
    total = crud.asset.count_with_filter(db, filter_params=asset_filter)
    return {"assets": assets, "total": total}


@router.get("/{asset_id}", response_model=schemas.AssetWithMaintenance)
def read_asset(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    asset = crud.asset.get_with_maintenance(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=schemas.Asset)
def update_asset(
        asset_id: int,
        asset_in: schemas.AssetUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    asset = crud.asset.get(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.asset.update(db, db_obj=asset, obj_in=asset_in)


@router.delete("/{asset_id}", response_model=schemas.Asset)
def delete_asset(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    asset = crud.asset.get(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.asset.remove(db, id=asset_id)


@router.get("/types", response_model=list[str])
def read_asset_types(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset.get_all_types(db)


@router.get("/statuses", response_model=list[str])
def read_asset_statuses(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset.get_all_statuses(db)


# Asset Maintenance routes
@router.post("/maintenance", response_model=schemas.AssetMaintenance)
def create_asset_maintenance(
        maintenance: schemas.AssetMaintenanceCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset_maintenance.create(db=db, obj_in=maintenance)


@router.get("/maintenance", response_model=list[schemas.AssetMaintenance])
def read_asset_maintenances(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        maintenance_filter: schemas.AssetMaintenanceFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset_maintenance.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=maintenance_filter)


@router.get("/maintenance/{maintenance_id}", response_model=schemas.AssetMaintenance)
def read_asset_maintenance(
        maintenance_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    return maintenance


@router.put("/maintenance/{maintenance_id}", response_model=schemas.AssetMaintenance)
def update_asset_maintenance(
        maintenance_id: int,
        maintenance_in: schemas.AssetMaintenanceUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    return crud.asset_maintenance.update(db, db_obj=maintenance, obj_in=maintenance_in)


@router.delete("/maintenance/{maintenance_id}", response_model=schemas.AssetMaintenance)
def delete_asset_maintenance(
        maintenance_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    return crud.asset_maintenance.remove(db, id=maintenance_id)


@router.get("/maintenance/types", response_model=list[str])
def read_maintenance_types(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset_maintenance.get_all_types(db)


@router.get("/{asset_id}/maintenance-history", response_model=list[schemas.AssetMaintenance])
def read_asset_maintenance_history(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset_maintenance.get_multi_by_asset(db, asset_id=asset_id, skip=skip, limit=limit)


@router.post("/{asset_id}/schedule-maintenance", response_model=schemas.AssetMaintenance)
def schedule_asset_maintenance(
        asset_id: int,
        maintenance: schemas.AssetMaintenanceCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    asset = crud.asset.get(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    maintenance.asset_id = asset_id
    return crud.asset_maintenance.create(db=db, obj_in=maintenance)


@router.put("/maintenance/{maintenance_id}/complete", response_model=schemas.AssetMaintenance)
def complete_asset_maintenance(
        maintenance_id: int,
        completion_data: schemas.AssetMaintenanceUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    completion_data.completed_date = date.today()
    completion_data.performed_by = current_user.user_id
    return crud.asset_maintenance.update(db, db_obj=maintenance, obj_in=completion_data)


@router.get("/{asset_id}/current-location", response_model=schemas.Location)
def get_asset_current_location(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.asset.get_current_location(db, asset_id=asset_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Asset location not found")
    return location


@router.post("/{asset_id}/transfer", response_model=schemas.Asset)
def transfer_asset(
        asset_id: int,
        transfer: schemas.AssetTransfer,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    asset = crud.asset.transfer(db, asset_id=asset_id, new_location_id=transfer.new_location_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/due-for-maintenance", response_model=list[schemas.AssetWithMaintenance])
def get_assets_due_for_maintenance(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.asset.get_due_for_maintenance(db)
