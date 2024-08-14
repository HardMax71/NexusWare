# /server/app/api/v1/router.py
from fastapi import APIRouter

from .endpoints import (users, inventory, orders, warehouse, yard, assets, quality, tasks, audit, reports, search, \
    products, customers, purchase_orders, suppliers, po_items, locations, zones, product_categories, roles,
                        permissions, pick_lists, receipts, shipments, carriers)

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(warehouse.router, prefix="/warehouse", tags=["warehouse"])
api_router.include_router(yard.router, prefix="/yard", tags=["yard"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(search.router, prefix="/search", tags=["search"])

api_router.include_router(products.router, prefix="/products", tags=["products"])

api_router.include_router(customers.router, prefix="/customers", tags=["customers"])

api_router.include_router(purchase_orders.router, prefix="/purchase_orders", tags=["purchase_orders"])

api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])

api_router.include_router(po_items.router, prefix="/po_items", tags=["po_items"])

api_router.include_router(carriers.router, prefix="/carriers", tags=["carriers"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])

api_router.include_router(zones.router, prefix="/zones", tags=["zones"])

api_router.include_router(roles.router, prefix="/roles", tags=["roles"])

api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(pick_lists.router, prefix="/pick_lists", tags=["pick_lists"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])

api_router.include_router(product_categories.router, prefix="/product_categories", tags=["product_categories"])
