# /server/app/crud/asset.py
from server.app.models import Asset, AssetMaintenance
from server.app.schemas import (AssetCreate, AssetUpdate,
                                AssetMaintenanceCreate, AssetMaintenanceUpdate)
from .base import CRUDBase


class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    pass


class CRUDAssetMaintenance(CRUDBase[AssetMaintenance, AssetMaintenanceCreate,
                                    AssetMaintenanceUpdate]):
    pass


asset = CRUDAsset(Asset)
asset_maintenance = CRUDAssetMaintenance(AssetMaintenance)
