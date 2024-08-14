from typing import List

from public_api.shared_schemas import POItem, POItemUpdate
from .client import APIClient


class POItemsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_po_item(self, po_item_id: int) -> POItem:
        response = self.client.get(f"/po_items/{po_item_id}")
        return POItem.model_validate(response)

    def update_po_item(self, po_item_id: int, po_item_data: POItemUpdate) -> POItem:
        response = self.client.put(f"/po_items/{po_item_id}",
                                   json=po_item_data.model_dump(mode="json", exclude_unset=True))
        return POItem.model_validate(response)

    def get_po_items(self, skip: int = 0, limit: int = 100) -> List[POItem]:
        response = self.client.get("/po_items", params={"skip": skip, "limit": limit})
        return [POItem.model_validate(item) for item in response]

    def get_po_items_by_product(self, product_id: int, skip: int = 0, limit: int = 100) -> List[POItem]:
        response = self.client.get(f"/po_items/by_product/{product_id}", params={"skip": skip, "limit": limit})
        return [POItem.model_validate(item) for item in response]

    def get_pending_receipt_po_items(self, skip: int = 0, limit: int = 100) -> List[POItem]:
        response = self.client.get("/po_items/pending_receipt", params={"skip": skip, "limit": limit})
        return [POItem.model_validate(item) for item in response]
