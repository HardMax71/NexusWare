from typing import Optional, List

from public_api.shared_schemas.quality import (
    QualityCheckCreate, QualityCheckUpdate, QualityCheckWithProduct, QualityCheckFilter,
    QualityMetrics, QualityStandardCreate, QualityStandardUpdate, QualityStandard,
    QualityAlertCreate, QualityAlertUpdate, QualityAlert, ProductDefectRate,
    QualityCheckComment, QualityCheckCommentCreate, QualityCheckSummary
)
from .client import APIClient


class QualityAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_quality_check(self, check_data: QualityCheckCreate) -> QualityCheckWithProduct:
        response = self.client.post("/quality/checks", json=check_data.model_dump(mode="json"))
        return QualityCheckWithProduct.model_validate(response)

    def get_quality_checks(self, skip: int = 0, limit: int = 100,
                           filter_params: Optional[QualityCheckFilter] = None) -> List[QualityCheckWithProduct]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/quality/checks", params=params)
        return [QualityCheckWithProduct.model_validate(item) for item in response]

    def get_quality_check(self, check_id: int) -> QualityCheckWithProduct:
        response = self.client.get(f"/quality/checks/{check_id}")
        return QualityCheckWithProduct.model_validate(response)

    def update_quality_check(self, check_id: int, check_data: QualityCheckUpdate) -> QualityCheckWithProduct:
        response = self.client.put(f"/quality/checks/{check_id}",
                                   json=check_data.model_dump(mode="json", exclude_unset=True))
        return QualityCheckWithProduct.model_validate(response)

    def delete_quality_check(self, check_id: int) -> QualityCheckWithProduct:
        response = self.client.delete(f"/quality/checks/{check_id}")
        return QualityCheckWithProduct.model_validate(response)

    def get_quality_metrics(self, date_from: Optional[int] = None,
                            date_to: Optional[int] = None) -> QualityMetrics:
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        response = self.client.get("/quality/metrics", params=params)
        return QualityMetrics.model_validate(response)

    def create_quality_standard(self, standard_data: QualityStandardCreate) -> QualityStandard:
        response = self.client.post("/quality/standards", json=standard_data.model_dump(mode="json"))
        return QualityStandard.model_validate(response)

    def get_quality_standards(self, skip: int = 0, limit: int = 100) -> List[QualityStandard]:
        response = self.client.get("/quality/standards", params={"skip": skip, "limit": limit})
        return [QualityStandard.model_validate(item) for item in response]

    def get_quality_standard(self, standard_id: int) -> QualityStandard:
        response = self.client.get(f"/quality/standards/{standard_id}")
        return QualityStandard.model_validate(response)

    def update_quality_standard(self, standard_id: int, standard_data: QualityStandardUpdate) -> QualityStandard:
        response = self.client.put(f"/quality/standards/{standard_id}",
                                   json=standard_data.model_dump(mode="json", exclude_unset=True))
        return QualityStandard.model_validate(response)

    def delete_quality_standard(self, standard_id: int) -> QualityStandard:
        response = self.client.delete(f"/quality/standards/{standard_id}")
        return QualityStandard.model_validate(response)

    def create_quality_alert(self, alert_data: QualityAlertCreate) -> QualityAlert:
        response = self.client.post("/quality/alerts", json=alert_data.model_dump(mode="json"))
        return QualityAlert.model_validate(response)

    def get_quality_alerts(self, skip: int = 0, limit: int = 100) -> List[QualityAlert]:
        response = self.client.get("/quality/alerts", params={"skip": skip, "limit": limit})
        return [QualityAlert.model_validate(item) for item in response]

    def resolve_quality_alert(self, alert_id: int, resolution_data: QualityAlertUpdate) -> QualityAlert:
        response = self.client.put(f"/quality/alerts/{alert_id}/resolve",
                                   json=resolution_data.model_dump(mode="json", exclude_unset=True))
        return QualityAlert.model_validate(response)

    def get_product_quality_history(self, product_id: int,
                                    skip: int = 0, limit: int = 100) -> List[QualityCheckWithProduct]:
        response = self.client.get(f"/quality/product/{product_id}/history",
                                   params={"skip": skip, "limit": limit})
        return [QualityCheckWithProduct.model_validate(item) for item in response]

    def get_quality_check_summary(self, date_from: Optional[int] = None,
                                  date_to: Optional[int] = None) -> QualityCheckSummary:
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        response = self.client.get("/quality/checks/summary", params=params)
        return QualityCheckSummary.model_validate(response)

    def get_product_quality_standards(self, product_id: int) -> List[QualityStandard]:
        response = self.client.get(f"/quality/product/{product_id}/standards")
        return [QualityStandard.model_validate(item) for item in response]

    def create_batch_quality_check(self, checks: List[QualityCheckCreate]) -> List[QualityCheckWithProduct]:
        response = self.client.post("/quality/batch_check",
                                    json=[check.model_dump(mode="json") for check in checks])
        return [QualityCheckWithProduct.model_validate(item) for item in response]

    def get_active_quality_alerts(self, skip: int = 0, limit: int = 100) -> List[QualityAlert]:
        response = self.client.get("/quality/alerts/active", params={"skip": skip, "limit": limit})
        return [QualityAlert.model_validate(item) for item in response]

    def add_comment_to_quality_check(self, check_id: int,
                                     comment_data: QualityCheckCommentCreate) -> QualityCheckComment:
        response = self.client.post(f"/quality/checks/{check_id}/comment",
                                    json=comment_data.model_dump(mode="json"))
        return QualityCheckComment.model_validate(response)

    def get_product_defect_rates(self,
                                 date_from: Optional[int] = None,
                                 date_to: Optional[int] = None) -> List[ProductDefectRate]:
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        response = self.client.get("/quality/reports/defect_rate", params=params)
        return [ProductDefectRate.model_validate(item) for item in response]
