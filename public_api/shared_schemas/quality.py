# /server/app/shared_schemas/quality.py
from typing import Optional

from pydantic import BaseModel

from public_api.shared_schemas import Product


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
    check_date: int

    class Config:
        from_attributes = True


class QualityCheckWithProduct(QualityCheck):
    product: Product


class QualityCheckFilter(BaseModel):
    product_id: Optional[int] = None
    performed_by: Optional[int] = None
    result: Optional[str] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None


class QualityMetrics(BaseModel):
    total_checks: int
    pass_rate: float
    fail_rate: float


class QualityStandardBase(BaseModel):
    product_id: int
    criteria: str
    acceptable_range: str


class QualityStandardCreate(QualityStandardBase):
    pass


class QualityStandardUpdate(BaseModel):
    product_id: Optional[int] = None
    criteria: Optional[str] = None
    acceptable_range: Optional[str] = None


class QualityStandard(QualityStandardBase):
    standard_id: int

    class Config:
        from_attributes = True


class QualityAlertBase(BaseModel):
    product_id: int
    alert_type: str
    description: str


class QualityAlertCreate(QualityAlertBase):
    pass


class QualityAlertUpdate(BaseModel):
    product_id: Optional[int] = None
    alert_type: Optional[str] = None
    description: Optional[str] = None
    resolved_at: Optional[int] = None


class QualityAlert(QualityAlertBase):
    alert_id: int
    created_at: int
    resolved_at: Optional[int] = None

    class Config:
        from_attributes = True


class QualityCheckComment(BaseModel):
    comment_id: int
    check_id: int
    user_id: int
    comment: str
    created_at: int


class QualityCheckCommentCreate(BaseModel):
    check_id: int
    user_id: int
    comment: str


class ProductDefectRate(BaseModel):
    product_id: int
    product_name: str
    total_checks: int
    defect_count: int
    defect_rate: float


class QualityStandardFilter(BaseModel):
    product_id: Optional[int] = None


class QualityAlertFilter(BaseModel):
    product_id: Optional[int] = None
    alert_type: Optional[str] = None
    resolved: Optional[bool] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None


class QualityCheckSummary(BaseModel):
    total_checks: int
    pass_count: int
    fail_count: int
    pass_rate: float


class QualityTrend(BaseModel):
    date: int
    pass_rate: float


class QualityPerformanceByProduct(BaseModel):
    product_id: int
    product_name: str
    total_checks: int
    pass_rate: float


class QualityAlertSummary(BaseModel):
    total_alerts: int
    open_alerts: int
    resolved_alerts: int
    most_common_type: str
