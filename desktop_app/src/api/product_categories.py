from .client import APIClient


class ProductCategoriesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_category(self, category_data: dict):
        return self.client.post("/product_categories/", json=category_data)

    def get_categories(self, skip: int = 0, limit: int = 100):
        return self.client.get("/product_categories/", params={"skip": skip, "limit": limit})

    def get_category(self, category_id: int):
        return self.client.get(f"/product_categories/{category_id}")

    def update_category(self, category_id: int, category_data: dict):
        return self.client.put(f"/product_categories/{category_id}", json=category_data)

    def delete_category(self, category_id: int):
        return self.client.delete(f"/product_categories/{category_id}")
