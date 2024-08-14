from typing import Optional

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from public_api.shared_schemas import AuditLog as AuditLogSchema, AuditLogCreate, AuditLogFilter, AuditSummary, \
    UserActivitySummary
from server.app.models import AuditLog, User
from .base import CRUDBase


class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, AuditLogCreate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: AuditLogFilter) -> list[AuditLogSchema]:
        query = db.query(self.model).join(User)
        if filter_params.user_id:
            query = query.filter(AuditLog.user_id == filter_params.user_id)
        if filter_params.action_type:
            query = query.filter(AuditLog.action_type == filter_params.action_type)
        if filter_params.table_name:
            query = query.filter(AuditLog.table_name == filter_params.table_name)
        if filter_params.record_id:
            query = query.filter(AuditLog.record_id == filter_params.record_id)
        if filter_params.date_from:
            query = query.filter(AuditLog.timestamp >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(AuditLog.timestamp <= filter_params.date_to)

        audit_logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        return [AuditLogSchema.model_validate(audit_log) for audit_log in audit_logs]

    def get_with_user(self, db: Session, id: int) -> Optional[AuditLogSchema]:
        audit_log = db.query(self.model).filter(self.model.id == id).join(User).first()
        return AuditLogSchema.model_validate(audit_log) if audit_log else None

    def get_summary(self, db: Session, date_from: Optional[int], date_to: Optional[int]) -> AuditSummary:
        query = db.query(self.model)
        if date_from:
            query = query.filter(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.filter(AuditLog.timestamp <= date_to)

        total_logs = query.count()
        logs_by_action = dict(
            query.with_entities(AuditLog.action_type, func.count()).group_by(AuditLog.action_type).all())
        logs_by_table = dict(query.with_entities(AuditLog.table_name, func.count()).group_by(AuditLog.table_name).all())

        user_activity = (
            db.query(User.id, User.username, func.count(AuditLog.id).label('total_actions'))
            .join(AuditLog)
            .group_by(User.id)
            .order_by(desc('total_actions'))
            .limit(5)
            .all()
        )

        most_active_users = [
            UserActivitySummary(user_id=user.id, username=user.username, total_actions=user.total_actions)
            for user in user_activity
        ]

        return AuditSummary(
            total_logs=total_logs,
            logs_by_action=logs_by_action,
            logs_by_table=logs_by_table,
            most_active_users=most_active_users
        )

    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> list[AuditLogSchema]:
        audit_logs = (db.query(self.model)
                      .filter(AuditLog.user_id == user_id)
                      .order_by(desc(AuditLog.timestamp))
                      .offset(skip).limit(limit)
                      .all())
        return [AuditLogSchema.model_validate(audit_log) for audit_log in audit_logs]

    def get_by_table(self, db: Session, *, table_name: str, skip: int = 0, limit: int = 100) -> list[AuditLogSchema]:
        audit_logs = (db.query(self.model)
                      .filter(AuditLog.table_name == table_name)
                      .order_by(desc(AuditLog.timestamp))
                      .offset(skip).limit(limit)
                      .all())
        return [AuditLogSchema.model_validate(audit_log) for audit_log in audit_logs]

    def get_by_record(self, db: Session, *, table_name: str,
                      record_id: int, skip: int = 0, limit: int = 100) -> list[AuditLogSchema]:
        audit_logs = (db.query(self.model)
                      .filter(AuditLog.table_name == table_name, AuditLog.record_id == record_id)
                      .order_by(desc(AuditLog.timestamp))
                      .offset(skip).limit(limit)
                      .all())
        return [AuditLogSchema.model_validate(audit_log) for audit_log in audit_logs]

    def get_for_export(self, db: Session, *,
                       date_from: Optional[int], date_to: Optional[int]) -> list[AuditLogSchema]:
        query = db.query(self.model)
        if date_from:
            query = query.filter(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.filter(AuditLog.timestamp <= date_to)
        audit_logs = query.order_by(desc(AuditLog.timestamp)).all()
        return [AuditLogSchema.model_validate(audit_log) for audit_log in audit_logs]

    def get_distinct_actions(self, db: Session) -> list[str]:
        return [action for (action,) in db.query(AuditLog.action_type).distinct().all()]

    def get_distinct_tables(self, db: Session) -> list[str]:
        return [table for (table,) in db.query(AuditLog.table_name).distinct().all()]


audit_log = CRUDAuditLog(AuditLog)
