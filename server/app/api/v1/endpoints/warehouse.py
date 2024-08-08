# /server/app/api/v1/endpoints/warehouse.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


# Pick List routes
@router.post("/pick-lists", response_model=schemas.PickList)
def create_pick_list(
        pick_list: schemas.PickListCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.create_with_items(db=db, obj_in=pick_list)


@router.get("/pick-lists", response_model=List[schemas.PickList])
def read_pick_lists(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.PickListFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/pick-lists/{pick_list_id}", response_model=schemas.PickList)
def read_pick_list(
        pick_list_id: int = Path(..., title="The ID of the pick list to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    pick_list = crud.pick_list.get(db, id=pick_list_id)
    if pick_list is None:
        raise HTTPException(status_code=404, detail="Pick list not found")
    return pick_list


@router.put("/pick-lists/{pick_list_id}", response_model=schemas.PickList)
def update_pick_list(
        pick_list_id: int = Path(..., title="The ID of the pick list to update"),
        pick_list_in: schemas.PickListUpdate = Body(..., title="Pick list update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    pick_list = crud.pick_list.get(db, id=pick_list_id)
    if pick_list is None:
        raise HTTPException(status_code=404, detail="Pick list not found")
    return crud.pick_list.update_with_items(db, db_obj=pick_list, obj_in=pick_list_in)


@router.delete("/pick-lists/{pick_list_id}", response_model=schemas.PickList)
def delete_pick_list(
        pick_list_id: int = Path(..., title="The ID of the pick list to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    pick_list = crud.pick_list.get(db, id=pick_list_id)
    if pick_list is None:
        raise HTTPException(status_code=404, detail="Pick list not found")
    return crud.pick_list.remove(db, id=pick_list_id)


# Receipt routes
@router.post("/receipts", response_model=schemas.Receipt)
def create_receipt(
        receipt: schemas.ReceiptCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.create_with_items(db=db, obj_in=receipt)


@router.get("/receipts", response_model=List[schemas.Receipt])
def read_receipts(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.ReceiptFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/receipts/{receipt_id}", response_model=schemas.Receipt)
def read_receipt(
        receipt_id: int = Path(..., title="The ID of the receipt to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    receipt = crud.receipt.get(db, id=receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@router.put("/receipts/{receipt_id}", response_model=schemas.Receipt)
def update_receipt(
        receipt_id: int = Path(..., title="The ID of the receipt to update"),
        receipt_in: schemas.ReceiptUpdate = Body(..., title="Receipt update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    receipt = crud.receipt.get(db, id=receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return crud.receipt.update_with_items(db, db_obj=receipt, obj_in=receipt_in)


@router.delete("/receipts/{receipt_id}", response_model=schemas.Receipt)
def delete_receipt(
        receipt_id: int = Path(..., title="The ID of the receipt to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    receipt = crud.receipt.get(db, id=receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return crud.receipt.remove(db, id=receipt_id)


# Shipment routes
@router.post("/shipments", response_model=schemas.Shipment)
def create_shipment(
        shipment: schemas.ShipmentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.create(db=db, obj_in=shipment)


@router.get("/shipments", response_model=List[schemas.Shipment])
def read_shipments(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.ShipmentFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.shipment.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/shipments/{shipment_id}", response_model=schemas.Shipment)
def read_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/shipments/{shipment_id}", response_model=schemas.Shipment)
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


@router.delete("/shipments/{shipment_id}", response_model=schemas.Shipment)
def delete_shipment(
        shipment_id: int = Path(..., title="The ID of the shipment to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    shipment = crud.shipment.get(db, id=shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return crud.shipment.remove(db, id=shipment_id)


# Carrier routes
@router.post("/carriers", response_model=schemas.Carrier)
def create_carrier(
        carrier: schemas.CarrierCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.carrier.create(db=db, obj_in=carrier)


@router.get("/carriers", response_model=List[schemas.Carrier])
def read_carriers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.carrier.get_multi(db, skip=skip, limit=limit)


@router.get("/carriers/{carrier_id}", response_model=schemas.Carrier)
def read_carrier(
        carrier_id: int = Path(..., title="The ID of the carrier to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    carrier = crud.carrier.get(db, id=carrier_id)
    if carrier is None:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return carrier


@router.put("/carriers/{carrier_id}", response_model=schemas.Carrier)
def update_carrier(
        carrier_id: int = Path(..., title="The ID of the carrier to update"),
        carrier_in: schemas.CarrierUpdate = Body(..., title="Carrier update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    carrier = crud.carrier.get(db, id=carrier_id)
    if carrier is None:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return crud.carrier.update(db, db_obj=carrier, obj_in=carrier_in)


@router.delete("/carriers/{carrier_id}", response_model=schemas.Carrier)
def delete_carrier(
        carrier_id: int = Path(..., title="The ID of the carrier to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    carrier = crud.carrier.get(db, id=carrier_id)
    if carrier is None:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return crud.carrier.remove(db, id=carrier_id)


# Additional warehouse operations
@router.get("/stats", response_model=schemas.WarehouseStats)
def get_warehouse_stats(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.warehouse.get_stats(db)


@router.get("/inventory/{location_id}", response_model=List[schemas.LocationInventory])
def get_location_inventory(
        location_id: int = Path(..., title="The ID of the location to get inventory for"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.warehouse.get_location_inventory(db, location_id=location_id)


@router.put("/inventory/{location_id}/{product_id}", response_model=schemas.LocationInventory)
def update_location_inventory(
        location_id: int = Path(..., title="The ID of the location"),
        product_id: int = Path(..., title="The ID of the product"),
        inventory_update: schemas.LocationInventoryUpdate = Body(..., title="Inventory update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.warehouse.update_location_inventory(db, location_id=location_id, product_id=product_id,
                                                    quantity=inventory_update.quantity)


@router.post("/inventory/move", response_model=schemas.InventoryMovement)
def move_inventory(
        movement: schemas.InventoryMovement,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.warehouse.move_inventory(db, movement=movement)


@router.post("/inventory/adjust", response_model=schemas.InventoryAdjustment)
def adjust_inventory(
        adjustment: schemas.InventoryAdjustment,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.warehouse.adjust_inventory(db, adjustment=adjustment)
