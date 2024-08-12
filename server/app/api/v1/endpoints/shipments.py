# /server/app/api/v1/endpoints/shipments.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Shipment)
def create_shipment(
        shipment: schemas.ShipmentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.create(db=db, obj_in=shipment)


@router.get("/", response_model=List[schemas.Shipment])
def read_shipments(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.ShipmentFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/carrier_rates", response_model=List[schemas.CarrierRate])
def get_carrier_rates(
        weight: float = Query(...),
        dimensions: str = Query(...),
        destination_zip: str = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.get_carrier_rates(db, weight=weight, dimensions=dimensions, destination_zip=destination_zip)


@router.get("/{shipment_id}", response_model=schemas.Shipment)
def read_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/{shipment_id}", response_model=schemas.Shipment)
def update_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to update"),
        shipment_in: schemas.ShipmentUpdate = Body(..., title="Shipment update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return crud.shipment.update(db, db_obj=shipment, obj_in=shipment_in)


@router.delete("/{shipment_id}", response_model=schemas.Shipment)
def delete_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return crud.shipment.remove(db, id=shipment_id)


@router.post("/{shipment_id}/generate_label", response_model=schemas.ShippingLabel)
def generate_shipping_label(
        shipment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.generate_label(db, shipment_id=shipment_id)


@router.post("/{shipment_id}/track", response_model=schemas.ShipmentTracking)
def track_shipment(
        shipment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.track(db, shipment_id=shipment_id)
