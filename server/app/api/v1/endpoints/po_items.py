# /server/app/api/v1/endpoints/po_items.py

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.get("/", response_model=list[shared_schemas.POItem])
def read_po_items(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.po_item.get_multi(db, skip=skip, limit=limit)


@router.get("/by_product/{product_id}", response_model=list[shared_schemas.POItem])
def read_po_items_by_product(
        product_id: int = Path(..., title="The ID of the product to filter by"),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.po_item.get_by_product(db, product_id=product_id, skip=skip, limit=limit)


@router.get("/pending_receipt", response_model=list[shared_schemas.POItem])
def read_pending_receipt_po_items(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.po_item.get_pending_receipt(db, skip=skip, limit=limit)


@router.get("/{po_item_id}", response_model=shared_schemas.POItem)
def read_po_item(
        po_item_id: int = Path(..., title="The ID of the PO item to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_item = crud.po_item.get(db, id=po_item_id)
    if po_item is None:
        raise HTTPException(status_code=404, detail="PO Item not found")
    return po_item


@router.put("/{po_item_id}", response_model=shared_schemas.POItem)
def update_po_item(
        po_item_id: int = Path(..., title="The ID of the PO item to update"),
        po_item_in: shared_schemas.POItemUpdate = Body(..., title="PO Item update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    po_item = crud.po_item.get(db, id=po_item_id)
    if po_item is None:
        raise HTTPException(status_code=404, detail="PO Item not found")
    return crud.po_item.update(db, db_obj=po_item, obj_in=po_item_in)
