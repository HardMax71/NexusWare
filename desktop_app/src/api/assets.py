from typing import Optional

from .client import APIClient


class AssetsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_asset(self, asset_data: dict):
        return self.client.post("/assets/", json=asset_data)

    def get_assets(self, skip: int = 0, limit: int = 100, asset_filter: Optional[dict] = None):
        return self.client.get("/assets/", params={"skip": skip, "limit": limit, **(asset_filter or {})})

    def get_asset(self, asset_id: int):
        return self.client.get(f"/assets/{asset_id}")

    def update_asset(self, asset_id: int, asset_data: dict):
        return self.client.put(f"/assets/{asset_id}", json=asset_data)

    def delete_asset(self, asset_id: int):
        return self.client.delete(f"/assets/{asset_id}")

    def get_asset_types(self):
        return self.client.get("/assets/types")

    def get_asset_statuses(self):
        return self.client.get("/assets/statuses")

    def create_asset_maintenance(self, maintenance_data: dict):
        return self.client.post("/assets/maintenance", json=maintenance_data)

    def get_asset_maintenances(self, skip: int = 0, limit: int = 100, maintenance_filter: Optional[dict] = None):
        return self.client.get("/assets/maintenance",
                               params={"skip": skip, "limit": limit, **(maintenance_filter or {})})

    def get_asset_maintenance(self, maintenance_id: int):
        return self.client.get(f"/assets/maintenance/{maintenance_id}")

    def update_asset_maintenance(self, maintenance_id: int, maintenance_data: dict):
        return self.client.put(f"/assets/maintenance/{maintenance_id}", json=maintenance_data)

    def delete_asset_maintenance(self, maintenance_id: int):
        return self.client.delete(f"/assets/maintenance/{maintenance_id}")

    def get_maintenance_types(self):
        return self.client.get("/assets/maintenance/types")

    def get_asset_maintenance_history(self, asset_id: int, skip: int = 0, limit: int = 100):
        return self.client.get(f"/assets/{asset_id}/maintenance_history", params={"skip": skip, "limit": limit})

    def schedule_asset_maintenance(self, asset_id: int, maintenance_data: dict):
        return self.client.post(f"/assets/{asset_id}/schedule_maintenance", json=maintenance_data)

    def complete_asset_maintenance(self, maintenance_id: int, completion_data: dict):
        return self.client.put(f"/assets/maintenance/{maintenance_id}/complete", json=completion_data)

    def get_asset_current_location(self, asset_id: int):
        return self.client.get(f"/assets/{asset_id}/current_location")

    def transfer_asset(self, asset_id: int, transfer_data: dict):
        return self.client.post(f"/assets/{asset_id}/transfer", json=transfer_data)

    def get_assets_due_for_maintenance(self):
        return self.client.get("/assets/due_for_maintenance")
