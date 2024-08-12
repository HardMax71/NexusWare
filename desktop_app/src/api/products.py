from typing import Optional

from .client import APIClient


class ProductsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_product(self, product_data: dict):
        return self.client.post("/products/", json=product_data)

    def get_products(self, skip: int = 0, limit: int = 100, product_filter: Optional[dict] = None):
        return self.client.get("/products/", params={"skip": skip, "limit": limit, **(product_filter or {})})

    def get_product(self, product_id: int):
        return self.client.get(f"/products/{product_id}")

    def update_product(self, product_id: int, product_data: dict):
        return self.client.put(f"/products/{product_id}", json=product_data)

    def delete_product(self, product_id: int):
        return self.client.delete(f"/products/{product_id}")

    def get_product_by_barcode(self, barcode: str):
        return self.client.post("/products/barcode", json={"barcode": barcode})

    def get_product_substitutes(self, product_id: int):
        return self.client.get(f"/products/{product_id}/substitutes")

    def add_product_substitute(self, product_id: int, substitute_id: int):
        return self.client.post(f"/products/{product_id}/substitutes", json={"substitute_id": substitute_id})
