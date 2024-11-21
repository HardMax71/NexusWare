from public_api.api.client import APIClient
from public_api.shared_schemas import (
    AssetCreate, AssetUpdate, Asset, AssetWithMaintenance, AssetFilter,
    AssetMaintenanceCreate, AssetMaintenanceUpdate, AssetMaintenance,
    AssetMaintenanceFilter, AssetWithMaintenanceList, AssetTransfer,
    Location
)


class AssetsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_asset(self, asset_data: AssetCreate) -> Asset:
        response = self.client.post("/assets/", json=asset_data.model_dump(mode="json"))
        return Asset.model_validate(response)

    def get_assets(self, skip: int = 0, limit: int = 100,
                   asset_filter: AssetFilter | None = None) -> AssetWithMaintenanceList:
        params = {"skip": skip, "limit": limit}
        if asset_filter:
            params.update(asset_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/assets/", params=params)
        return AssetWithMaintenanceList.model_validate(response)

    def get_asset(self, asset_id: int) -> AssetWithMaintenance:
        response = self.client.get(f"/assets/{asset_id}")
        return AssetWithMaintenance.model_validate(response)

    def update_asset(self, asset_id: int, asset_data: AssetUpdate) -> Asset:
        response = self.client.put(f"/assets/{asset_id}", json=asset_data.model_dump(mode="json", exclude_unset=True))
        return Asset.model_validate(response)

    def delete_asset(self, asset_id: int) -> None:
        self.client.delete(f"/assets/{asset_id}")

    def get_asset_types(self) -> list[str]:
        response = self.client.get("/assets/types")
        return [str(item) for item in response]

    def get_asset_statuses(self) -> list[str]:
        response = self.client.get("/assets/statuses")
        return [str(item) for item in response]

    def create_asset_maintenance(self, maintenance_data: AssetMaintenanceCreate) -> AssetMaintenance:
        response = self.client.post("/assets/maintenance", json=maintenance_data.model_dump(mode="json"))
        return AssetMaintenance.model_validate(response)

    def get_asset_maintenances(self, skip: int = 0, limit: int = 100,
                               maintenance_filter: AssetMaintenanceFilter | None = None) -> list[AssetMaintenance]:
        params = {"skip": skip, "limit": limit}
        if maintenance_filter:
            params.update(maintenance_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/assets/maintenance", params=params)
        return [AssetMaintenance.model_validate(item) for item in response]

    def get_asset_maintenance(self, maintenance_id: int) -> AssetMaintenance:
        response = self.client.get(f"/assets/maintenance/{maintenance_id}")
        return AssetMaintenance.model_validate(response)

    def update_asset_maintenance(self, maintenance_id: int,
                                 maintenance_data: AssetMaintenanceUpdate) -> AssetMaintenance:
        response = self.client.put(f"/assets/maintenance/{maintenance_id}",
                                   json=maintenance_data.model_dump(mode="json", exclude_unset=True))
        return AssetMaintenance.model_validate(response)

    def delete_asset_maintenance(self, maintenance_id: int) -> None:
        self.client.delete(f"/assets/maintenance/{maintenance_id}")

    def get_maintenance_types(self) -> list[str]:
        response = self.client.get("/assets/maintenance/types")
        return [str(item) for item in response]

    def get_asset_maintenance_history(self, asset_id: int, skip: int = 0, limit: int = 100) -> list[AssetMaintenance]:
        response = self.client.get(f"/assets/{asset_id}/maintenance_history", params={"skip": skip, "limit": limit})
        return [AssetMaintenance.model_validate(item) for item in response]

    def schedule_asset_maintenance(self, asset_id: int, maintenance_data: AssetMaintenanceCreate) -> AssetMaintenance:
        response = self.client.post(f"/assets/{asset_id}/schedule_maintenance",
                                    json=maintenance_data.model_dump(mode="json"))
        return AssetMaintenance.model_validate(response)

    def complete_asset_maintenance(self, maintenance_id: int,
                                   completion_data: AssetMaintenanceUpdate) -> AssetMaintenance:
        response = self.client.put(f"/assets/maintenance/{maintenance_id}/complete",
                                   json=completion_data.model_dump(mode="json", exclude_unset=True))
        return AssetMaintenance.model_validate(response)

    def get_asset_current_location(self, asset_id: int) -> Location:
        response = self.client.get(f"/assets/{asset_id}/current_location")
        return Location.model_validate(response)

    def transfer_asset(self, asset_id: int, transfer_data: AssetTransfer) -> Asset:
        response = self.client.post(f"/assets/{asset_id}/transfer", json=transfer_data.model_dump(mode="json"))
        return Asset.model_validate(response)

    def get_assets_due_for_maintenance(self) -> list[AssetWithMaintenance]:
        response = self.client.get("/assets/due_for_maintenance")
        return [AssetWithMaintenance.model_validate(item) for item in response]
