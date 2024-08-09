# /server/app/api/v1/router.py
from fastapi import APIRouter

from .endpoints import users, inventory, orders, warehouse, yard, assets, quality, tasks, audit, reports, search

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
