# /server/app/api/v1/endpoints/orders.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Order)
def create_order(
        order: schemas.OrderCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.create(db=db, obj_in=order)


@router.get("/", response_model=List[schemas.OrderWithDetails])
def read_orders(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.OrderFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_multi_with_details(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/summary", response_model=schemas.OrderSummary)
def get_order_summary(
        db: Session = Depends(deps.get_db),
        date_from: datetime = Query(None),
        date_to: datetime = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/backorders", response_model=List[schemas.Order])
def get_backorders(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_backorders(db)


@router.post("/bulk_import", response_model=schemas.BulkImportResult)
def bulk_import_orders(
        import_data: schemas.BulkImportData,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.order.bulk_import(db, import_data=import_data)


@router.get("/processing_times", response_model=schemas.OrderProcessingTimes)
def get_order_processing_times(
        start_date: datetime = Query(...),
        end_date: datetime = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_processing_times(db, start_date=start_date, end_date=end_date)


@router.get("/{order_id}", response_model=schemas.OrderWithDetails)
def read_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get_with_details(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
        order_id: int,
        order_in: schemas.OrderUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.update(db, db_obj=order, obj_in=order_in)


@router.delete("/{order_id}", response_model=schemas.Order)
def delete_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.remove(db, id=order_id)


@router.post("/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.cancel(db, db_obj=order)


@router.post("/{order_id}/ship", response_model=schemas.Order)
def ship_order(
        order_id: int,
        shipping_info: schemas.ShippingInfo,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.ship(db, db_obj=order, shipping_info=shipping_info)


@router.post("/{order_id}/cancel_item", response_model=schemas.Order)
def cancel_order_item(
        order_id: int,
        item_id: int = Body(..., embed=True),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.cancel_item(db, order_id=order_id, item_id=item_id)


@router.post("/{order_id}/add_item", response_model=schemas.Order)
def add_order_item(
        order_id: int,
        item: schemas.OrderItemCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.add_item(db, order_id=order_id, item=item)