# /server/app/api/v1/endpoints/zones.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Zone)
def create_zone(
        zone: shared_schemas.ZoneCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.create(db=db, obj_in=zone)


@router.get("/", response_model=list[shared_schemas.ZoneWithLocations])
def read_zones(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        zone_filter: shared_schemas.ZoneFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.zone.get_multi_with_locations(db, skip=skip, limit=limit, filter_params=zone_filter)


@router.get("/{zone_id}", response_model=shared_schemas.ZoneWithLocations)
def read_zone(
        zone_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    zone = crud.zone.get_with_locations(db, id=zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.put("/{zone_id}", response_model=shared_schemas.Zone)
def update_zone(
        zone_id: int,
        zone_in: shared_schemas.ZoneUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    zone = crud.zone.get(db, id=zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return crud.zone.update(db, db_obj=zone, obj_in=zone_in)


@router.delete("/{zone_id}", status_code=204)
def delete_zone(
        zone_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    zone = crud.zone.get(db, id=zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    crud.zone.remove(db, id=zone_id)
