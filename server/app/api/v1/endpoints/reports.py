# /server/app/api/v1/endpoints/reports.py
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.get("/inventory-summary", response_model=schemas.InventorySummaryReport)
def get_inventory_summary(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_inventory_summary(db)


@router.get("/order-summary", response_model=schemas.OrderSummaryReport)
def get_order_summary(
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_order_summary(db, start_date, end_date)


@router.get("/warehouse-performance", response_model=schemas.WarehousePerformanceReport)
def get_warehouse_performance(
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_warehouse_performance(db, start_date, end_date)


@router.get("/kpi-dashboard", response_model=schemas.KPIDashboard)
def get_kpi_dashboard(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.reports.get_kpi_dashboard(db)
