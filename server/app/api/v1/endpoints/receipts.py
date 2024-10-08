# /server/app/api/v1/endpoints/receipts.py

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.post("/", response_model=shared_schemas.Receipt)
def create_receipt(
        receipt: shared_schemas.ReceiptCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.create_with_items(db=db, obj_in=receipt)


@router.get("/", response_model=list[shared_schemas.Receipt])
def read_receipts(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.ReceiptFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/expected_today", response_model=list[shared_schemas.Receipt])
def get_expected_receipts_today(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.get_expected_today(db)


@router.get("/{receipt_id}", response_model=shared_schemas.Receipt)
def read_receipt(
        receipt_id: int = Path(..., title="The ID of the receipt to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    receipt = crud.receipt.get(db, id=receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@router.put("/{receipt_id}", response_model=shared_schemas.Receipt)
def update_receipt(
        receipt_id: int = Path(..., title="The ID of the receipt to update"),
        receipt_in: shared_schemas.ReceiptUpdate = Body(..., title="Receipt update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    receipt = crud.receipt.get(db, id=receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return crud.receipt.update_with_items(db, db_obj=receipt, obj_in=receipt_in)


@router.delete("/{receipt_id}", status_code=204)
def delete_receipt(
        receipt_id: int = Path(..., title="The ID of the receipt to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    receipt = crud.receipt.get(db, id=receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    crud.receipt.remove(db, id=receipt_id)


@router.post("/{receipt_id}/quality_check", response_model=shared_schemas.Receipt)
def perform_receipt_quality_check(
        receipt_id: int,
        quality_check: shared_schemas.QualityCheckCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.perform_quality_check(db, receipt_id=receipt_id, quality_check=quality_check)


@router.post("/{receipt_id}/discrepancy", response_model=shared_schemas.Receipt)
def report_receipt_discrepancy(
        receipt_id: int,
        discrepancy: shared_schemas.ReceiptDiscrepancy,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.receipt.report_discrepancy(db, receipt_id=receipt_id, discrepancy=discrepancy)
