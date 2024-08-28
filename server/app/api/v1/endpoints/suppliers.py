# /server/app/api/v1/endpoints/suppliers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Supplier)
def create_supplier(
        supplier: shared_schemas.SupplierCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.supplier.create(db=db, obj_in=supplier)


@router.get("/", response_model=list[shared_schemas.Supplier])
def read_suppliers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        supplier_filter: shared_schemas.SupplierFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.supplier.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=supplier_filter)


@router.get("/{supplier_id}", response_model=shared_schemas.Supplier)
def read_supplier(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/{supplier_id}", response_model=shared_schemas.Supplier)
def update_supplier(
        supplier_id: int,
        supplier_in: shared_schemas.SupplierUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.supplier.update(db, db_obj=supplier, obj_in=supplier_in)


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    supplier = crud.supplier.get(db, id=supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    crud.supplier.remove(db, id=supplier_id)




@router.get("/{supplier_id}/purchase_orders", response_model=list[shared_schemas.PurchaseOrder])
def read_supplier_purchase_orders(
        supplier_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.PurchaseOrderFilter(supplier_id=supplier_id)
    return crud.purchase_order.get_multi_with_details(db, skip=skip, limit=limit, filter_params=filter_params)
