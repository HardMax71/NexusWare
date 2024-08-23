# /server/app/api/v1/endpoints/quality.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from public_api import shared_schemas
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.post("/checks", response_model=shared_schemas.QualityCheck)
def create_quality_check(
        check: shared_schemas.QualityCheckCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.create(db=db, obj_in=check)


@router.get("/checks", response_model=List[shared_schemas.QualityCheckWithProduct])
def read_quality_checks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.QualityCheckFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/checks/{check_id}", response_model=shared_schemas.QualityCheckWithProduct)
def read_quality_check(
        check_id: int = Path(..., title="The ID of the quality check to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    check = crud.quality_check.get(db, id=check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Quality check not found")
    return check


@router.put("/checks/{check_id}", response_model=shared_schemas.QualityCheck)
def update_quality_check(
        check_id: int = Path(..., title="The ID of the quality check to update"),
        check_in: shared_schemas.QualityCheckUpdate = Body(..., title="Quality check update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    check = crud.quality_check.get(db, id=check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Quality check not found")
    return crud.quality_check.update(db, db_obj=check, obj_in=check_in)


@router.delete("/checks/{check_id}", response_model=shared_schemas.QualityCheck)
def delete_quality_check(
        check_id: int = Path(..., title="The ID of the quality check to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    check = crud.quality_check.get(db, id=check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Quality check not found")
    return crud.quality_check.remove(db, id=check_id)


@router.get("/metrics", response_model=shared_schemas.QualityMetrics)
def get_quality_metrics(
        db: Session = Depends(deps.get_db),
        date_from: int = Query(None),
        date_to: int = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.get_metrics(db, date_from=date_from, date_to=date_to)


@router.post("/standards", response_model=shared_schemas.QualityStandard)
def create_quality_standard(
        standard: shared_schemas.QualityStandardCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_standard.create(db=db, obj_in=standard)


@router.get("/standards", response_model=List[shared_schemas.QualityStandard])
def read_quality_standards(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_standard.get_multi(db, skip=skip, limit=limit)


@router.get("/standards/{standard_id}", response_model=shared_schemas.QualityStandard)
def read_quality_standard(
        standard_id: int = Path(..., title="The ID of the quality standard to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    standard = crud.quality_standard.get(db, id=standard_id)
    if standard is None:
        raise HTTPException(status_code=404, detail="Quality standard not found")
    return standard


@router.put("/standards/{standard_id}", response_model=shared_schemas.QualityStandard)
def update_quality_standard(
        standard_id: int = Path(..., title="The ID of the quality standard to update"),
        standard_in: shared_schemas.QualityStandardUpdate = Body(..., title="Quality standard update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    standard = crud.quality_standard.get(db, id=standard_id)
    if standard is None:
        raise HTTPException(status_code=404, detail="Quality standard not found")
    return crud.quality_standard.update(db, db_obj=standard, obj_in=standard_in)


@router.delete("/standards/{standard_id}", response_model=shared_schemas.QualityStandard)
def delete_quality_standard(
        standard_id: int = Path(..., title="The ID of the quality standard to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    standard = crud.quality_standard.get(db, id=standard_id)
    if standard is None:
        raise HTTPException(status_code=404, detail="Quality standard not found")
    return crud.quality_standard.remove(db, id=standard_id)


@router.post("/alerts", response_model=shared_schemas.QualityAlert)
def create_quality_alert(
        alert: shared_schemas.QualityAlertCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_alert.create(db=db, obj_in=alert)


@router.get("/alerts", response_model=List[shared_schemas.QualityAlert])
def read_quality_alerts(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_alert.get_multi(db, skip=skip, limit=limit)


@router.put("/alerts/{alert_id}/resolve", response_model=shared_schemas.QualityAlert)
def resolve_quality_alert(
        alert_id: int = Path(..., title="The ID of the quality alert to resolve"),
        alert_in: shared_schemas.QualityAlertUpdate = Body(..., title="Quality alert update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    alert = crud.quality_alert.get(db, id=alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Quality alert not found")
    return crud.quality_alert.update(db, db_obj=alert, obj_in=alert_in)


@router.get("/product/{product_id}/history", response_model=List[shared_schemas.QualityCheckWithProduct])
def get_product_quality_history(
        product_id: int = Path(..., title="The ID of the product to get quality history for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.QualityCheckFilter(product_id=product_id)
    return crud.quality_check.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/checks/summary", response_model=dict[str, int])
def get_quality_check_summary(
        db: Session = Depends(deps.get_db),
        date_from: int = Query(None),
        date_to: int = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/product/{product_id}/standards", response_model=List[shared_schemas.QualityStandard])
def get_product_quality_standards(
        product_id: int = Path(..., title="The ID of the product to get quality standards for"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_standard.get_by_product(db, product_id=product_id)


@router.post("/batch_check", response_model=List[shared_schemas.QualityCheck])
def create_batch_quality_check(
        checks: List[shared_schemas.QualityCheckCreate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.create_batch(db=db, obj_in_list=checks)


@router.get("/alerts/active", response_model=List[shared_schemas.QualityAlert])
def get_active_quality_alerts(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_alert.get_active(db, skip=skip, limit=limit)


@router.post("/checks/{check_id}/comment", response_model=shared_schemas.QualityCheckComment)
def add_comment_to_quality_check(
        check_id: int = Path(..., title="The ID of the quality check to comment on"),
        comment: shared_schemas.QualityCheckCommentCreate = Body(..., title="Quality check comment data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.add_comment(db, check_id=check_id, comment=comment, user_id=current_user.id)


@router.get("/reports/defect_rate", response_model=List[shared_schemas.ProductDefectRate])
def get_product_defect_rates(
        db: Session = Depends(deps.get_db),
        date_from: int = Query(None),
        date_to: int = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.quality_check.get_product_defect_rates(db, date_from=date_from, date_to=date_to)
