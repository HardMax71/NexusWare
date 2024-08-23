# /server/app/shared_schemas/quality.py

from pydantic import BaseModel

from public_api.shared_schemas import Product


class QualityCheckBase(BaseModel):
    product_id: int
    performed_by: int
    result: str
    notes: str | None = None


class QualityCheckCreate(QualityCheckBase):
    pass


class QualityCheckUpdate(BaseModel):
    product_id: int | None = None
    performed_by: int | None = None
    result: str | None = None
    notes: str | None = None


class QualityCheck(QualityCheckBase):
    id: int
    check_date: int

    class Config:
        from_attributes = True


class QualityCheckWithProduct(QualityCheck):
    product: Product


class QualityCheckFilter(BaseModel):
    product_id: int | None = None
    performed_by: int | None = None
    result: str | None = None
    date_from: int | None = None
    date_to: int | None = None


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
    product_id: int | None = None
    criteria: str | None = None
    acceptable_range: str | None = None


class QualityStandard(QualityStandardBase):
    id: int

    class Config:
        from_attributes = True


class QualityAlertBase(BaseModel):
    product_id: int
    alert_type: str
    description: str


class QualityAlertCreate(QualityAlertBase):
    pass


class QualityAlertUpdate(BaseModel):
    product_id: int | None = None
    alert_type: str | None = None
    description: str | None = None
    resolved_at: int | None = None


class QualityAlert(QualityAlertBase):
    id: int
    created_at: int
    resolved_at: int | None = None

    class Config:
        from_attributes = True


class QualityCheckComment(BaseModel):
    id: int
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
    product_id: int | None = None


class QualityAlertFilter(BaseModel):
    product_id: int | None = None
    alert_type: str | None = None
    resolved: bool | None = None
    date_from: int | None = None
    date_to: int | None = None


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
