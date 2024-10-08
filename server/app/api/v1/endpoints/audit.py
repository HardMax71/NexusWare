# /server/app/api/v1/endpoints/audit.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.post("/logs", response_model=shared_schemas.AuditLog)
def create_audit_log(
        log: shared_schemas.AuditLogCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.create(db=db, obj_in=log)


@router.get("/logs", response_model=list[shared_schemas.AuditLogWithUser])
def read_audit_logs(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.AuditLogFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/logs/summary", response_model=shared_schemas.AuditSummary)
def get_audit_summary(
        db: Session = Depends(deps.get_db),
        date_from: int = Query(None),
        date_to: int = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="Invalid date range: start date is after end date")
    return crud.audit_log.get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/logs/export", response_model=shared_schemas.AuditLogExport)
def export_audit_logs(
        db: Session = Depends(deps.get_db),
        date_from: int = Query(None),
        date_to: int = Query(None),
        current_user: models.User = Depends(deps.get_current_admin)
):
    filter_params = shared_schemas.AuditLogFilter(date_from=date_from, date_to=date_to)
    logs = crud.audit_log.get_multi_with_filter(db, filter_params=filter_params)
    return shared_schemas.AuditLogExport(logs=logs, export_timestamp=int(datetime.now().timestamp()))


@router.get("/logs/actions", response_model=list[str])
def get_audit_log_actions(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_distinct_actions(db)


@router.get("/logs/tables", response_model=list[str])
def get_audited_tables(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_distinct_tables(db)


@router.get("/logs/{log_id}", response_model=shared_schemas.AuditLogWithUser)
def read_audit_log(
        log_id: int = Path(..., title="The ID of the audit log to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    log = crud.audit_log.get(db, id=log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@router.get("/logs/user/{user_id}", response_model=list[shared_schemas.AuditLog])
def get_user_audit_logs(
        user_id: int = Path(..., title="The ID of the user to get audit logs for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.AuditLogFilter(user_id=user_id)
    return crud.audit_log.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/logs/table/{table_name}", response_model=list[shared_schemas.AuditLog])
def get_table_audit_logs(
        table_name: str = Path(..., title="The name of the table to get audit logs for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.AuditLogFilter(table_name=table_name)
    return crud.audit_log.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/logs/record/{table_name}/{record_id}", response_model=list[shared_schemas.AuditLog])
def get_record_audit_logs(
        table_name: str = Path(..., title="The name of the table"),
        record_id: int = Path(..., title="The ID of the record to get audit logs for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.AuditLogFilter(table_name=table_name, record_id=record_id)
    return crud.audit_log.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)
