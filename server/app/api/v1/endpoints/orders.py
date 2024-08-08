# /server/app/api/v1/endpoints/orders.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


# Order routes
@router.post("/orders", response_model=schemas.Order)
def create_order(
        order: schemas.OrderCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.create(db=db, obj_in=order)


@router.get("/orders", response_model=List[schemas.OrderWithDetails])
def read_orders(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        order_filter: schemas.OrderFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_multi_with_details(db, skip=skip, limit=limit, filter_params=order_filter)


@router.get("/orders/{order_id}", response_model=schemas.OrderWithDetails)
def read_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get_with_details(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/orders/{order_id}", response_model=schemas.Order)
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


@router.delete("/orders/{order_id}", response_model=schemas.Order)
def delete_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.remove(db, id=order_id)


@router.get("/orders/summary", response_model=schemas.OrderSummary)
def get_order_summary(
        db: Session = Depends(deps.get_db),
        date_from: datetime = Query(None),
        date_to: datetime = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_summary(db, date_from=date_from, date_to=date_to)


# Customer routes
@router.post("/customers", response_model=schemas.Customer)
def create_customer(
        customer: schemas.CustomerCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.customer.create(db=db, obj_in=customer)


@router.get("/customers", response_model=List[schemas.Customer])
def read_customers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        customer_filter: schemas.CustomerFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.customer.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=customer_filter)


@router.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(
        customer_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    customer = crud.customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(
        customer_id: int,
        customer_in: schemas.CustomerUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    customer = crud.customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.customer.update(db, db_obj=customer, obj_in=customer_in)


@router.delete("/customers/{customer_id}", response_model=schemas.Customer)
def delete_customer(
        customer_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    customer = crud.customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.customer.remove(db, id=customer_id)


# Purchase Order routes
@router.post("/purchase-orders", response_model=schemas.PurchaseOrder)
def create_purchase_order(
        purchase_order: schemas.PurchaseOrderCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.purchase_order.create(db=db, obj_in=purchase_order)


@router.get("/purchase-orders", response_model=List[schemas.PurchaseOrderWithDetails])
def read_purchase_orders(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        po_filter: schemas.PurchaseOrderFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.purchase_order.get_multi_with_details(db, skip=skip, limit=limit, filter_params=po_filter)


@router.get("/purchase-orders/{po_id}", response_model=schemas.PurchaseOrderWithDetails)
def read_purchase_order(
        po_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po = crud.purchase_order.get_with_details(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return po


@router.put("/purchase-orders/{po_id}", response_model=schemas.PurchaseOrder)
def update_purchase_order(
        po_id: int,
        po_in: schemas.PurchaseOrderUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po = crud.purchase_order.get(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.purchase_order.update(db, db_obj=po, obj_in=po_in)


@router.delete("/purchase-orders/{po_id}", response_model=schemas.PurchaseOrder)
def delete_purchase_order(
        po_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    po = crud.purchase_order.get(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.purchase_order.remove(db, id=po_id)


# Supplier routes
@router.post("/suppliers", response_model=schemas.Supplier)
def create_supplier(
        supplier: schemas.SupplierCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.supplier.create(db=db, obj_in=supplier)


@router.get("/suppliers", response_model=List[schemas.Supplier])
def read_suppliers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        supplier_filter: schemas.SupplierFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.supplier.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=supplier_filter)


@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def read_supplier(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def update_supplier(
        supplier_id: int,
        supplier_in: schemas.SupplierUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.supplier.update(db, db_obj=supplier, obj_in=supplier_in)


@router.delete("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def delete_supplier(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.supplier.remove(db, id=supplier_id)


@router.post("/orders/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    order = crud.order.get(db, id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.cancel(db, db_obj=order)


@router.post("/orders/{order_id}/ship", response_model=schemas.Order)
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


@router.get("/customers/{customer_id}/orders", response_model=List[schemas.Order])
def read_customer_orders(
        customer_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.get_by_customer(db, customer_id=customer_id, skip=skip, limit=limit)


@router.post("/purchase-orders/{po_id}/receive", response_model=schemas.PurchaseOrder)
def receive_purchase_order(
        po_id: int,
        received_items: List[schemas.POItemReceive],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po = crud.purchase_order.get(db, id=po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return crud.purchase_order.receive(db, db_obj=po, received_items=received_items)


@router.get("/suppliers/{supplier_id}/purchase-orders", response_model=List[schemas.PurchaseOrder])
def read_supplier_purchase_orders(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.purchase_order.get_by_supplier(db, supplier_id=supplier_id, skip=skip, limit=limit)


# POItem routes
@router.get("/po-items/{po_item_id}", response_model=schemas.POItem)
def read_po_item(
        po_item_id: int = Path(..., title="The ID of the PO item to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_item = crud.po_item.get(db, id=po_item_id)
    if po_item is None:
        raise HTTPException(status_code=404, detail="PO Item not found")
    return po_item


@router.put("/po-items/{po_item_id}", response_model=schemas.POItem)
def update_po_item(
        po_item_id: int = Path(..., title="The ID of the PO item to update"),
        po_item_in: schemas.POItemUpdate = Body(..., title="PO Item update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_item = crud.po_item.get(db, id=po_item_id)
    if po_item is None:
        raise HTTPException(status_code=404, detail="PO Item not found")
    return crud.po_item.update(db, db_obj=po_item, obj_in=po_item_in)


@router.get("/po-items", response_model=List[schemas.POItem])
def read_po_items(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_items = crud.po_item.get_multi(db, skip=skip, limit=limit)
    return po_items


@router.get("/po-items/by-product/{product_id}", response_model=List[schemas.POItem])
def read_po_items_by_product(
        product_id: int = Path(..., title="The ID of the product to filter by"),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_items = crud.po_item.get_by_product(db, product_id=product_id, skip=skip, limit=limit)
    return po_items


@router.get("/po-items/pending-receipt", response_model=List[schemas.POItem])
def read_pending_receipt_po_items(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_items = crud.po_item.get_pending_receipt(db, skip=skip, limit=limit)
    return po_items
