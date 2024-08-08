# /server/app/schemas/reports.py
from datetime import date

from pydantic import BaseModel


class InventoryItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    value: float


class InventorySummaryReport(BaseModel):
    total_items: int
    total_value: float
    items: list[InventoryItem]


class OrderSummary(BaseModel):
    total_orders: int
    total_revenue: float
    average_order_value: float


class OrderSummaryReport(BaseModel):
    start_date: date
    end_date: date
    summary: OrderSummary


class WarehousePerformanceMetric(BaseModel):
    name: str
    value: float
    unit: str


class WarehousePerformanceReport(BaseModel):
    start_date: date
    end_date: date
    metrics: list[WarehousePerformanceMetric]


class KPIMetric(BaseModel):
    name: str
    value: float
    trend: str  # 'up', 'down', or 'stable'


class KPIDashboard(BaseModel):
    date: date
    metrics: list[KPIMetric]
