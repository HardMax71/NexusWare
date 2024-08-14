from typing import List, Optional

from public_api.shared_schemas import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrder,
    PurchaseOrderWithDetails, PurchaseOrderFilter, POItemReceive
)
from .client import APIClient


class PurchaseOrdersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_purchase_order(self, purchase_order_data: PurchaseOrderCreate) -> PurchaseOrder:
        response = self.client.post("/purchase_orders/", json=purchase_order_data.model_dump(mode="json"))
        return PurchaseOrder.model_validate(response)

    def get_purchase_orders(self, skip: int = 0, limit: int = 100,
                            po_filter: Optional[PurchaseOrderFilter] = None) -> List[PurchaseOrderWithDetails]:
        params = {"skip": skip, "limit": limit}
        if po_filter:
            params.update(po_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/purchase_orders/", params=params)
        return [PurchaseOrderWithDetails.model_validate(item) for item in response]

    def get_purchase_order(self, po_id: int) -> PurchaseOrderWithDetails:
        response = self.client.get(f"/purchase_orders/{po_id}")
        return PurchaseOrderWithDetails.model_validate(response)

    def update_purchase_order(self, po_id: int, po_data: PurchaseOrderUpdate) -> PurchaseOrder:
        response = self.client.put(f"/purchase_orders/{po_id}",
                                   json=po_data.model_dump(mode="json", exclude_unset=True))
        return PurchaseOrder.model_validate(response)

    def delete_purchase_order(self, po_id: int) -> PurchaseOrder:
        response = self.client.delete(f"/purchase_orders/{po_id}")
        return PurchaseOrder.model_validate(response)

    def receive_purchase_order(self, po_id: int, received_items: List[POItemReceive]) -> PurchaseOrder:
        response = self.client.post(f"/purchase_orders/{po_id}/receive",
                                    json={"received_items": [item.model_dump(mode="json") for item in received_items]})
        return PurchaseOrder.model_validate(response)
