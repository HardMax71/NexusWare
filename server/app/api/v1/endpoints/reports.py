# /server/app/api/v1/endpoints/reports.py


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.get("/inventory_summary", response_model=shared_schemas.InventorySummaryReport)
def get_inventory_summary(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_inventory_summary(db)


@router.get("/order_summary", response_model=shared_schemas.OrderSummaryReport)
def get_order_summary(
        start_date: int = Query(...),
        end_date: int = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_order_summary(db, start_date, end_date)


@router.get("/warehouse_performance", response_model=shared_schemas.WarehousePerformanceReport)
def get_warehouse_performance(
        start_date: int = Query(...),
        end_date: int = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_warehouse_performance(db, start_date, end_date)


@router.get("/kpi_dashboard", response_model=shared_schemas.KPIDashboard)
def get_kpi_dashboard(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_kpi_dashboard(db)
