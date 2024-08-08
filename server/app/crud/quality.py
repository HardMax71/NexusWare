# /server/app/crud/quality.py
from server.app.models import QualityCheck
from server.app.schemas import QualityCheckCreate, QualityCheckUpdate

from .base import CRUDBase


class CRUDQualityCheck(CRUDBase[QualityCheck, QualityCheckCreate, QualityCheckUpdate]):
    pass


quality_check = CRUDQualityCheck(QualityCheck)
