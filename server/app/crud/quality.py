# /server/app/crud/quality.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from server.app.models import QualityCheck, QualityStandard, QualityAlert, Product
from server.app.schemas import (QualityCheckCreate, QualityCheckUpdate, QualityCheckFilter,
                                QualityStandardCreate, QualityStandardUpdate,
                                QualityAlertCreate, QualityAlertUpdate,
                                QualityMetrics)
from .base import CRUDBase
from ..schemas.quality import ProductDefectRate, QualityCheckCommentCreate, QualityCheckComment


class CRUDQualityCheck(CRUDBase[QualityCheck, QualityCheckCreate, QualityCheckUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100,
                              filter_params: QualityCheckFilter) -> List[QualityCheck]:
        query = db.query(self.model).join(Product)
        if filter_params.product_id:
            query = query.filter(QualityCheck.product_id == filter_params.product_id)
        if filter_params.performed_by:
            query = query.filter(QualityCheck.performed_by == filter_params.performed_by)
        if filter_params.result:
            query = query.filter(QualityCheck.result == filter_params.result)
        if filter_params.date_from:
            query = query.filter(QualityCheck.check_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(QualityCheck.check_date <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()

    def get_with_product(self, db: Session, id: int) -> Optional[QualityCheck]:
        return db.query(self.model).filter(self.model.check_id == id).join(Product).first()

    def get_metrics(self, db: Session, date_from: Optional[datetime], date_to: Optional[datetime]) -> QualityMetrics:
        query = db.query(func.count(QualityCheck.check_id).label("total_checks"),
                         func.sum(case((QualityCheck.result == "pass", 1), else_=0)).label("passes"),
                         func.sum(case((QualityCheck.result == "fail", 1), else_=0)).label("fails"))
        if date_from:
            query = query.filter(QualityCheck.check_date >= date_from)
        if date_to:
            query = query.filter(QualityCheck.check_date <= date_to)
        result = query.first()
        total = result.total_checks
        passes = result.passes
        fails = result.fails
        return QualityMetrics(
            total_checks=total,
            pass_rate=passes / total if total > 0 else 0,
            fail_rate=fails / total if total > 0 else 0
        )

    def get_product_history(self, db: Session, *, product_id: int, skip: int = 0, limit: int = 100) -> List[
        QualityCheck]:
        return db.query(self.model).filter(QualityCheck.product_id == product_id).order_by(
            QualityCheck.check_date.desc()).offset(skip).limit(limit).all()

    def get_summary(self, db: Session, date_from: Optional[datetime], date_to: Optional[datetime]) -> dict[str, int]:
        query = db.query(QualityCheck.result, func.count(QualityCheck.check_id))
        if date_from:
            query = query.filter(QualityCheck.check_date >= date_from)
        if date_to:
            query = query.filter(QualityCheck.check_date <= date_to)
        summary = dict(query.group_by(QualityCheck.result).all())
        return {
            "total": sum(summary.values()),
            "pass": summary.get("pass", 0),
            "fail": summary.get("fail", 0)
        }

    def create_batch(self, db: Session, *, obj_in_list: List[QualityCheckCreate]) -> List[QualityCheck]:
        db_objs = [QualityCheck(**obj_in.dict()) for obj_in in obj_in_list]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

    def add_comment(self, db: Session, *, check_id: int, comment: QualityCheckCommentCreate,
                    user_id: int) -> QualityCheckComment:
        db_comment = QualityCheckComment(
            check_id=check_id,
            user_id=user_id,
            comment=comment.comment
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def get_product_defect_rates(self, db: Session, date_from: Optional[datetime], date_to: Optional[datetime]) -> List[
        ProductDefectRate]:
        query = db.query(
            Product.product_id,
            Product.name.label("product_name"),
            func.count(QualityCheck.check_id).label("total_checks"),
            func.sum(case((QualityCheck.result == "fail", 1), else_=0)).label("defect_count")
        ).join(QualityCheck)
        if date_from:
            query = query.filter(QualityCheck.check_date >= date_from)
        if date_to:
            query = query.filter(QualityCheck.check_date <= date_to)
        results = query.group_by(Product.product_id).all()
        return [
            ProductDefectRate(
                product_id=r.product_id,
                product_name=r.product_name,
                total_checks=r.total_checks,
                defect_count=r.defect_count,
                defect_rate=r.defect_count / r.total_checks if r.total_checks > 0 else 0
            )
            for r in results
        ]


class CRUDQualityStandard(CRUDBase[QualityStandard, QualityStandardCreate, QualityStandardUpdate]):
    def get_by_product(self, db: Session, *, product_id: int) -> List[QualityStandard]:
        return db.query(self.model).filter(QualityStandard.product_id == product_id).all()


class CRUDQualityAlert(CRUDBase[QualityAlert, QualityAlertCreate, QualityAlertUpdate]):
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[QualityAlert]:
        return db.query(self.model).filter(QualityAlert.resolved_at.is_(None)).offset(skip).limit(limit).all()


quality_check = CRUDQualityCheck(QualityCheck)
quality_standard = CRUDQualityStandard(QualityStandard)
quality_alert = CRUDQualityAlert(QualityAlert)
