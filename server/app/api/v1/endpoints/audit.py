# /server/app/api/v1/endpoints/audit.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/logs", response_model=schemas.AuditLog)
def create_audit_log(
        log: schemas.AuditLogCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.create(db=db, obj_in=log)


@router.get("/logs", response_model=List[schemas.AuditLogWithUser])
def read_audit_logs(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.AuditLogFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/logs/{log_id:int}", response_model=schemas.AuditLogWithUser)
def read_audit_log(
        log_id: int = Path(..., title="The ID of the audit log to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    log = crud.audit_log.get_with_user(db, id=log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@router.get("/logs/summary", response_model=schemas.AuditSummary)
def get_audit_summary(
        db: Session = Depends(deps.get_db),
        date_from: datetime = Query(None),
        date_to: datetime = Query(None),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/logs/user/{user_id}", response_model=List[schemas.AuditLog])
def get_user_audit_logs(
        user_id: int = Path(..., title="The ID of the user to get audit logs for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_by_user(db, user_id=user_id, skip=skip, limit=limit)


@router.get("/logs/table/{table_name}", response_model=List[schemas.AuditLog])
def get_table_audit_logs(
        table_name: str = Path(..., title="The name of the table to get audit logs for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_by_table(db, table_name=table_name, skip=skip, limit=limit)


@router.get("/logs/record/{table_name}/{record_id}", response_model=List[schemas.AuditLog])
def get_record_audit_logs(
        table_name: str = Path(..., title="The name of the table"),
        record_id: int = Path(..., title="The ID of the record to get audit logs for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_by_record(db, table_name=table_name, record_id=record_id, skip=skip, limit=limit)


@router.get("/logs/export", response_model=schemas.AuditLogExport)
def export_audit_logs(
        db: Session = Depends(deps.get_db),
        date_from: datetime = Query(None),
        date_to: datetime = Query(None),
        current_user: models.User = Depends(deps.get_current_admin)
):
    logs = crud.audit_log.get_for_export(db, date_from=date_from, date_to=date_to)
    return schemas.AuditLogExport(logs=logs, export_timestamp=datetime.utcnow())


@router.get("/logs/actions", response_model=List[str])
def get_audit_log_actions(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_distinct_actions(db)


@router.get("/logs/tables", response_model=List[str])
def get_audited_tables(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.audit_log.get_distinct_tables(db)
