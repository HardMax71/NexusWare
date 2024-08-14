# /server/app/shared_schemas/asset.py
from typing import Optional, List

from pydantic import BaseModel


class AssetBase(BaseModel):
    asset_type: str
    asset_name: str
    serial_number: str
    purchase_date: int
    status: str
    location_id: Optional[int] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_type: Optional[str] = None
    asset_name: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[int] = None
    status: Optional[str] = None
    location_id: Optional[int] = None


class Asset(AssetBase):
    id: int

    class Config:
        from_attributes = True


class AssetMaintenanceBase(BaseModel):
    asset_id: int
    maintenance_type: str
    scheduled_date: int
    completed_date: Optional[int] = None
    performed_by: Optional[int] = None
    notes: Optional[str] = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    pass


class AssetMaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    scheduled_date: Optional[int] = None
    completed_date: Optional[int] = None
    performed_by: Optional[int] = None
    notes: Optional[str] = None


class AssetMaintenance(AssetMaintenanceBase):
    maintenance_id: int

    class Config:
        from_attributes = True


class AssetWithMaintenance(Asset):
    maintenance_records: List[AssetMaintenance] = []

    class Config:
        from_attributes = True


class AssetFilter(BaseModel):
    asset_type: Optional[str] = None
    status: Optional[str] = None
    purchase_date_from: Optional[int] = None
    purchase_date_to: Optional[int] = None
    location_id: Optional[int] = None


class AssetMaintenanceFilter(BaseModel):
    asset_id: Optional[int] = None
    maintenance_type: Optional[str] = None
    scheduled_date_from: Optional[int] = None
    scheduled_date_to: Optional[int] = None
    completed_date_from: Optional[int] = None
    completed_date_to: Optional[int] = None
    performed_by: Optional[int] = None


class AssetWithMaintenanceList(BaseModel):
    assets: List[AssetWithMaintenance]
    total: int


class AssetTransfer(BaseModel):
    new_location_id: int


class AssetLocation(BaseModel):
    asset_id: int
    location_id: int
    timestamp: int