from .client import APIClient


class POItemsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_po_item(self, po_item_id: int):
        return self.client.get(f"/po_items/{po_item_id}")

    def update_po_item(self, po_item_id: int, po_item_data: dict):
        return self.client.put(f"/po_items/{po_item_id}", json=po_item_data)

    def get_po_items(self, skip: int = 0, limit: int = 100):
        return self.client.get("/po_items", params={"skip": skip, "limit": limit})

    def get_po_items_by_product(self, product_id: int, skip: int = 0, limit: int = 100):
        return self.client.get(f"/po_items/by_product/{product_id}", params={"skip": skip, "limit": limit})

    def get_pending_receipt_po_items(self, skip: int = 0, limit: int = 100):
        return self.client.get("/po_items/pending_receipt", params={"skip": skip, "limit": limit})
