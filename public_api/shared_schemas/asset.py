# /server/app/shared_schemas/asset.py

from pydantic import BaseModel


class AssetBase(BaseModel):
    asset_type: str
    asset_name: str
    serial_number: str
    purchase_date: int
    status: str
    location_id: int | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_type: str | None = None
    asset_name: str | None = None
    serial_number: str | None = None
    purchase_date: int | None = None
    status: str | None = None
    location_id: int | None = None


class Asset(AssetBase):
    id: int

    class Config:
        from_attributes = True


class AssetMaintenanceBase(BaseModel):
    asset_id: int
    maintenance_type: str
    scheduled_date: int
    completed_date: int | None = None
    performed_by: int | None = None
    notes: str | None = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    pass


class AssetMaintenanceUpdate(BaseModel):
    maintenance_type: str | None = None
    scheduled_date: int | None = None
    completed_date: int | None = None
    performed_by: int | None = None
    notes: str | None = None


class AssetMaintenance(AssetMaintenanceBase):
    maintenance_id: int

    class Config:
        from_attributes = True


class AssetWithMaintenance(Asset):
    maintenance_records: list[AssetMaintenance] = []

    class Config:
        from_attributes = True


class AssetFilter(BaseModel):
    asset_type: str | None = None
    status: str | None = None
    purchase_date_from: int | None = None
    purchase_date_to: int | None = None
    location_id: int | None = None


class AssetMaintenanceFilter(BaseModel):
    asset_id: int | None = None
    maintenance_type: str | None = None
    scheduled_date_from: int | None = None
    scheduled_date_to: int | None = None
    completed_date_from: int | None = None
    completed_date_to: int | None = None
    performed_by: int | None = None


class AssetWithMaintenanceList(BaseModel):
    assets: list[AssetWithMaintenance]
    total: int


class AssetTransfer(BaseModel):
    new_location_id: int


class AssetLocation(BaseModel):
    asset_id: int
    location_id: int
    timestamp: int
