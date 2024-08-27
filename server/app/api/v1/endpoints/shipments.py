# /server/app/api/v1/endpoints/shipments.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from sqlalchemy.orm import Session

from public_api.shared_schemas import ShipmentWithDetails
from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Shipment)
def create_shipment(
        shipment: shared_schemas.ShipmentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.create(db=db, obj_in=shipment)


@router.get("/", response_model=List[shared_schemas.Shipment])
def read_shipments(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.ShipmentFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/carrier_rates", response_model=List[shared_schemas.CarrierRate])
def get_carrier_rates(
        weight: float = Query(...),
        dimensions: str = Query(...),
        destination_zip: str = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.get_carrier_rates(db, weight=weight, dimensions=dimensions, destination_zip=destination_zip)


@router.get("/{shipment_id}", response_model=shared_schemas.Shipment)
def read_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/{shipment_id}", response_model=shared_schemas.Shipment)
def update_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to update"),
        shipment_in: shared_schemas.ShipmentUpdate = Body(..., title="Shipment update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return crud.shipment.update(db, db_obj=shipment, obj_in=shipment_in)


@router.delete("/{shipment_id}", status_code=204)
def delete_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    crud.shipment.remove(db, id=shipment_id)


@router.post("/{shipment_id}/generate_label", response_model=shared_schemas.ShippingLabel)
def generate_shipping_label(
        shipment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.generate_label(db, shipment_id=shipment_id)


@router.get("/{shipment_id}/details", response_model=ShipmentWithDetails)
def get_shipment_with_details(
        shipment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    order = crud.order.get(db, id=shipment.order_id) if shipment.order_id else None
    carrier = crud.carrier.get(db, id=shipment.carrier_id) if shipment.carrier_id else None

    return ShipmentWithDetails(
        **shipment.__dict__,
        order=order,
        carrier=carrier
    )

@router.post("/{shipment_id}/track", response_model=shared_schemas.ShipmentTracking)
def track_shipment(
        shipment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.track(db, shipment_id=shipment_id)
