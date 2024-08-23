# /server/app/api/v1/endpoints/assets.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from public_api import shared_schemas
from public_api.shared_schemas import AssetMaintenanceFilter
from .... import crud, models
from ....api import deps

router = APIRouter()


# Asset routes
@router.post("/", response_model=shared_schemas.Asset)
def create_asset(
        asset: shared_schemas.AssetCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "write"))
):
    return crud.asset.create(db=db, obj_in=asset)


@router.get("/", response_model=shared_schemas.AssetWithMaintenanceList)
def read_assets(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        asset_filter: shared_schemas.AssetFilter = Depends(),
        current_user: models.User = Depends(deps.has_permission("asset", "read"))
):
    assets = crud.asset.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=asset_filter)
    total = len(assets)
    return {"assets": assets, "total": total}


@router.get("/types", response_model=list[str])
def read_asset_types(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "read"))
):
    return crud.asset.get_all_types(db)


@router.get("/statuses", response_model=list[str])
def read_asset_statuses(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "read"))
):
    return crud.asset.get_all_statuses(db)


# Asset Maintenance routes
@router.post("/maintenance", response_model=shared_schemas.AssetMaintenance)
def create_asset_maintenance(
        maintenance: shared_schemas.AssetMaintenanceCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "write"))
):
    return crud.asset_maintenance.create(db=db, obj_in=maintenance)


@router.get("/maintenance", response_model=list[shared_schemas.AssetMaintenance])
def read_asset_maintenances(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        maintenance_filter: shared_schemas.AssetMaintenanceFilter = Depends(),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "read"))
):
    return crud.asset_maintenance.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=maintenance_filter)


@router.get("/maintenance/{maintenance_id}", response_model=shared_schemas.AssetMaintenance)
def read_asset_maintenance(
        maintenance_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "read"))
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    return maintenance


@router.put("/maintenance/{maintenance_id}", response_model=shared_schemas.AssetMaintenance)
def update_asset_maintenance(
        maintenance_id: int,
        maintenance_in: shared_schemas.AssetMaintenanceUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "write"))
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    return crud.asset_maintenance.update(db, db_obj=maintenance, obj_in=maintenance_in)


@router.delete("/maintenance/{maintenance_id}", response_model=shared_schemas.AssetMaintenance)
def delete_asset_maintenance(
        maintenance_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "delete"))
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    return crud.asset_maintenance.remove(db, id=maintenance_id)


@router.get("/maintenance/types", response_model=list[str])
def read_maintenance_types(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "read"))
):
    return crud.asset_maintenance.get_all_types(db)


@router.get("/{asset_id}/maintenance_history", response_model=list[shared_schemas.AssetMaintenance])
def read_asset_maintenance_history(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "read"))
):
    filter_params = AssetMaintenanceFilter(asset_id=asset_id)
    return crud.asset_maintenance.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.post("/{asset_id}/schedule_maintenance", response_model=shared_schemas.AssetMaintenance)
def schedule_asset_maintenance(
        asset_id: int,
        maintenance: shared_schemas.AssetMaintenanceCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "create"))
):
    asset = crud.asset.get(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    maintenance.asset_id = asset_id
    return crud.asset_maintenance.create(db=db, obj_in=maintenance)


@router.put("/maintenance/{maintenance_id}/complete", response_model=shared_schemas.AssetMaintenance)
def complete_asset_maintenance(
        maintenance_id: int,
        completion_data: shared_schemas.AssetMaintenanceUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "update"))
):
    maintenance = crud.asset_maintenance.get(db, id=maintenance_id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Asset maintenance record not found")
    completion_data.completed_date = int(datetime.now().timestamp())
    completion_data.performed_by = current_user.id
    return crud.asset_maintenance.update(db, db_obj=maintenance, obj_in=completion_data)


@router.get("/due_for_maintenance", response_model=list[shared_schemas.AssetWithMaintenance])
def get_assets_due_for_maintenance(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset_maintenance", "read"))
):
    return crud.asset.get_due_for_maintenance(db)


@router.get("/{asset_id}", response_model=shared_schemas.AssetWithMaintenance)
def read_asset(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "read"))
):
    asset = crud.asset.get_with_maintenance(db, asset_id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=shared_schemas.Asset)
def update_asset(
        asset_id: int,
        asset_in: shared_schemas.AssetUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "update"))
):
    asset = crud.asset.get(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.asset.update(db, db_obj=asset, obj_in=asset_in)


@router.delete("/{asset_id}", response_model=shared_schemas.Asset)
def delete_asset(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "delete"))
):
    asset = crud.asset.get(db, id=asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.asset.remove(db, id=asset_id)


@router.get("/{asset_id}/current_location", response_model=shared_schemas.Location)
def get_asset_current_location(
        asset_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "read"))
):
    location = crud.asset.get_asset_location(db, asset_id=asset_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Asset location not found")
    return location


@router.post("/{asset_id}/transfer", response_model=shared_schemas.Asset)
def transfer_asset(
        asset_id: int,
        transfer: shared_schemas.AssetTransfer,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.has_permission("asset", "update"))
):
    asset = crud.asset.transfer(db, asset_id=asset_id, new_location_id=transfer.new_location_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
