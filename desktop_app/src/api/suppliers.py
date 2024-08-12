from .client import APIClient

class SuppliersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_suppliers(self, skip=0, limit=100, filter_params=None):
        if filter_params is None:
            filter_params = {}
        return self.client.get("/suppliers/", params={"skip": skip, "limit": limit, **filter_params})

    def get_supplier(self, supplier_id):
        return self.client.get(f"/suppliers/{supplier_id}")

    def create_supplier(self, supplier_data):
        return self.client.post("/suppliers/", json=supplier_data)

    def update_supplier(self, supplier_id, supplier_data):
        return self.client.put(f"/suppliers/{supplier_id}", json=supplier_data)

    def delete_supplier(self, supplier_id):
        return self.client.delete(f"/suppliers/{supplier_id}")

    def get_supplier_purchase_orders(self, supplier_id, skip=0, limit=100):
        return self.client.get(f"/suppliers/{supplier_id}/purchase_orders", params={"skip": skip, "limit": limit})