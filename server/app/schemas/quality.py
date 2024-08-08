# /server/app/schemas/quality.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from server.app.schemas import Product


class QualityCheckBase(BaseModel):
    product_id: int
    performed_by: int
    result: str
    notes: Optional[str] = None


class QualityCheckCreate(QualityCheckBase):
    pass


class QualityCheckUpdate(BaseModel):
    product_id: Optional[int] = None
    performed_by: Optional[int] = None
    result: Optional[str] = None
    notes: Optional[str] = None


class QualityCheck(QualityCheckBase):
    check_id: int
    check_date: datetime

    class Config:
        from_attributes = True


class QualityCheckWithProduct(QualityCheck):
    product: "Product"


class QualityCheckFilter(BaseModel):
    product_id: Optional[int] = None
    performed_by: Optional[int] = None
    result: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class QualityMetrics(BaseModel):
    total_checks: int
    pass_rate: float
    fail_rate: float


class QualityStandard(BaseModel):
    standard_id: int
    product_id: int
    criteria: str
    acceptable_range: str


class QualityStandardCreate(BaseModel):
    product_id: int
    criteria: str
    acceptable_range: str


class QualityStandardUpdate(BaseModel):
    criteria: Optional[str] = None
    acceptable_range: Optional[str] = None


class QualityAlert(BaseModel):
    alert_id: int
    product_id: int
    alert_type: str
    description: str
    created_at: datetime
    resolved_at: Optional[datetime] = None


class QualityAlertCreate(BaseModel):
    product_id: int
    alert_type: str
    description: str


class QualityAlertUpdate(BaseModel):
    resolved_at: datetime


class QualityCheckComment(BaseModel):
    comment_id: int
    check_id: int
    user_id: int
    comment: str
    created_at: datetime


class QualityCheckCommentCreate(BaseModel):
    comment: str


class ProductDefectRate(BaseModel):
    product_id: int
    product_name: str
    total_checks: int
    defect_count: int
    defect_rate: float
