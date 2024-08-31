# /server/app/api/v1/endpoints/carriers.py

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas
from public_api.shared_schemas import Carrier

router = APIRouter()


@router.post("/", response_model=shared_schemas.Carrier)
def create_carrier(
        carrier: shared_schemas.CarrierCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.carrier.create(db=db, obj_in=carrier)


@router.get("/", response_model=list[Carrier])
def read_carriers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.carrier.get_multi(db, skip=skip, limit=limit)


@router.get("/{carrier_id}", response_model=shared_schemas.Carrier)
def read_carrier(
        carrier_id: int = Path(..., title="The ID of the carrier to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    carrier = crud.carrier.get(db, id=carrier_id)
    if carrier is None:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return carrier


@router.put("/{carrier_id}", response_model=shared_schemas.Carrier)
def update_carrier(
        carrier_id: int = Path(..., title="The ID of the carrier to update"),
        carrier_in: shared_schemas.CarrierUpdate = Body(..., title="Carrier update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    carrier = crud.carrier.get(db, id=carrier_id)
    if carrier is None:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return crud.carrier.update(db, db_obj=carrier, obj_in=carrier_in)


@router.delete("/{carrier_id}", status_code=204)
def delete_carrier(
        carrier_id: int = Path(..., title="The ID of the carrier to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    carrier = crud.carrier.get(db, id=carrier_id)
    if carrier is None:
        raise HTTPException(status_code=404, detail="Carrier not found")
    crud.carrier.remove(db, id=carrier_id)
