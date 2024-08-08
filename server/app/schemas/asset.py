# /server/app/schemas/asset.py
from datetime import date
from typing import Optional

from pydantic import BaseModel


class AssetBase(BaseModel):
    asset_type: str
    asset_name: str
    serial_number: str
    purchase_date: date
    status: str


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_type: Optional[str] = None
    asset_name: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    status: Optional[str] = None


class Asset(AssetBase):
    asset_id: int

    class Config:
        from_attributes = True


class AssetMaintenanceBase(BaseModel):
    asset_id: int
    maintenance_type: str
    scheduled_date: date
    completed_date: Optional[date] = None
    performed_by: Optional[int] = None
    notes: Optional[str] = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    pass


class AssetMaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    performed_by: Optional[int] = None
    notes: Optional[str] = None


class AssetMaintenance(AssetMaintenanceBase):
    maintenance_id: int

    class Config:
        from_attributes = True


class AssetWithMaintenance(Asset):
    maintenance_records: list[AssetMaintenance] = []
