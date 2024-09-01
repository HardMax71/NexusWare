# /server/app/api/v1/endpoints/locations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.post("/", response_model=shared_schemas.Location)
def create_location(
        location: shared_schemas.LocationCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.location.create(db=db, obj_in=location)


@router.get("/", response_model=list[shared_schemas.LocationWithInventory])
def read_locations(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        location_filter: shared_schemas.LocationFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.location.get_multi_with_inventory(db, skip=skip, limit=limit, filter_params=location_filter)


@router.get("/{location_id}", response_model=shared_schemas.LocationWithInventory)
def read_location(
        location_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.location.get_with_inventory(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.put("/{location_id}", response_model=shared_schemas.Location)
def update_location(
        location_id: int,
        location_in: shared_schemas.LocationUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    location = crud.location.get(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return crud.location.update(db, db_obj=location, obj_in=location_in)


@router.delete("/{location_id}", status_code=204)
def delete_location(
        location_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    location = crud.location.get(db, id=location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    crud.location.remove(db, id=location_id)
