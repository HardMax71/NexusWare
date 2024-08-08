# /server/app/schemas/quality.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
