# /server/app/api/v1/endpoints/purchase_orders.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.PurchaseOrder)
def create_purchase_order(
        purchase_order: shared_schemas.PurchaseOrderCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.purchase_order.create(db=db, obj_in=purchase_order)


@router.get("/", response_model=List[shared_schemas.PurchaseOrderWithDetails])
def read_purchase_orders(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        po_filter: shared_schemas.PurchaseOrderFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.purchase_order.get_multi_with_products(db, skip=skip, limit=limit, filter_params=po_filter)


@router.get("/{po_id}", response_model=shared_schemas.PurchaseOrderWithDetails)
def read_purchase_order(
        po_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.PurchaseOrderFilter(id=po_id)
    po = crud.purchase_order.get_multi_with_details(db, filter_params=filter_params)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return po


@router.put("/{po_id}", response_model=shared_schemas.PurchaseOrder)
def update_purchase_order(
        po_id: int,
        po_in: shared_schemas.PurchaseOrderUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po = crud.purchase_order.get(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.purchase_order.update(db, db_obj=po, obj_in=po_in)


@router.delete("/{po_id}", response_model=shared_schemas.PurchaseOrder)
def delete_purchase_order(
        po_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    po = crud.purchase_order.get(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.purchase_order.remove(db, id=po_id)


@router.post("/{po_id}/receive", response_model=shared_schemas.PurchaseOrder)
def receive_purchase_order(
        po_id: int,
        received_items: List[shared_schemas.POItemReceive],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po = crud.purchase_order.get(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.purchase_order.receive(db, db_obj=po, received_items=received_items)