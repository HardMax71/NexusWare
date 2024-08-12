# /server/app/api/v1/endpoints/suppliers.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Supplier)
def create_supplier(
        supplier: schemas.SupplierCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.supplier.create(db=db, obj_in=supplier)


@router.get("/", response_model=List[schemas.Supplier])
def read_suppliers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        supplier_filter: schemas.SupplierFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.supplier.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=supplier_filter)


@router.get("/{supplier_id}", response_model=schemas.Supplier)
def read_supplier(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/{supplier_id}", response_model=schemas.Supplier)
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


@router.delete("/{supplier_id}", response_model=schemas.Supplier)
def delete_supplier(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.supplier.remove(db, id=supplier_id)




@router.get("/{supplier_id}/purchase_orders", response_model=List[schemas.PurchaseOrder])
def read_supplier_purchase_orders(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.purchase_order.get_by_supplier(db, supplier_id=supplier_id, skip=skip, limit=limit)
