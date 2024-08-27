# /server/app/api/v1/endpoints/orders.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from public_api import shared_schemas
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Order)
def create_order(
        order: shared_schemas.OrderCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.create(db=db, obj_in=order)


@router.get("/", response_model=List[shared_schemas.OrderWithDetails])
def read_orders(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.OrderFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_multi_with_details(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/summary", response_model=shared_schemas.OrderSummary)
def get_order_summary(
        db: Session = Depends(deps.get_db),
        date_from: int = Query(None),
        date_to: int = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/backorders", response_model=List[shared_schemas.Order])
def get_backorders(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_backorders(db)


@router.post("/bulk_import", response_model=shared_schemas.BulkImportResult)
def bulk_import_orders(
        import_data: shared_schemas.BulkImportData,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.order.bulk_import(db, import_data=import_data)


@router.get("/processing_times", response_model=shared_schemas.OrderProcessingTimes)
def get_order_processing_times(
        start_date: int = Query(...),
        end_date: int = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_processing_times(db, start_date=start_date, end_date=end_date)


@router.put("/{order_id}/items", response_model=shared_schemas.Order)
def update_order_items(
        order_id: int,
        items: List[shared_schemas.OrderItemUpdate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.update_items(db, order_id=order_id, items=items)


@router.get("/{order_id}", response_model=shared_schemas.OrderWithDetails)
def read_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=shared_schemas.Order)
def update_order(
        order_id: int,
        order_in: shared_schemas.OrderUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.update(db, db_obj=order, obj_in=order_in)


@router.delete("/{order_id}", status_code=204)
def delete_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    crud.order.remove(db, id=order_id)


@router.post("/{order_id}/cancel", response_model=shared_schemas.Order)
def cancel_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.cancel(db, db_obj=order)


@router.post("/{order_id}/ship", response_model=shared_schemas.Order)
def ship_order(
        order_id: int,
        shipping_info: shared_schemas.ShippingInfo,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.ship(db, db_obj=order, shipping_info=shipping_info)


@router.post("/{order_id}/cancel_item", response_model=shared_schemas.Order)
def cancel_order_item(
        order_id: int,
        item_id: int = Body(..., embed=True),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.cancel_item(db, order_id=order_id, item_id=item_id)


@router.post("/{order_id}/add_item", response_model=shared_schemas.Order)
def add_order_item(
        order_id: int,
        item: shared_schemas.OrderItemCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.add_item(db, order_id=order_id, item=item)
