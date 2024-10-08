# /server/app/shared_schemas/reports.py
from enum import Enum

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
    start_date: int
    end_date: int
    summary: OrderSummary


class WarehousePerformanceMetric(BaseModel):
    name: str
    value: float
    unit: str


class WarehousePerformanceReport(BaseModel):
    start_date: int
    end_date: int
    metrics: list[WarehousePerformanceMetric]


class TrendDirection(str, Enum):
    UP = 'up'
    DOWN = 'down'
    STABLE = 'stable'


class KPIMetric(BaseModel):
    name: str
    value: float
    trend: TrendDirection


class KPIDashboard(BaseModel):
    date: int
    metrics: list[KPIMetric]


class ProductPerformance(BaseModel):
    product_id: int
    product_name: str
    total_sold: int
    revenue: float


class TopSellingProductsReport(BaseModel):
    start_date: int
    end_date: int
    products: list[ProductPerformance]


class SupplierPerformance(BaseModel):
    supplier_id: int
    supplier_name: str
    on_time_delivery_rate: float
    quality_rating: float
    total_orders: int


class SupplierPerformanceReport(BaseModel):
    start_date: int
    end_date: int
    suppliers: list[SupplierPerformance]


class StockMovement(BaseModel):
    product_id: int
    product_name: str
    quantity_change: int
    movement_type: str
    date: int


class StockMovementReport(BaseModel):
    start_date: int
    end_date: int
    movements: list[StockMovement]


class PickingEfficiency(BaseModel):
    user_id: int
    user_name: str
    total_picks: int
    average_pick_time: float
    accuracy_rate: float


class PickingEfficiencyReport(BaseModel):
    start_date: int
    end_date: int
    pickers: list[PickingEfficiency]


class StorageUtilization(BaseModel):
    zone_id: int
    zone_name: str
    total_capacity: float
    used_capacity: float
    utilization_rate: float


class StorageUtilizationReport(BaseModel):
    date: int
    zones: list[StorageUtilization]


class ReturnsAnalysis(BaseModel):
    reason: str
    count: int
    percentage: float


class ReturnsReport(BaseModel):
    start_date: int
    end_date: int
    total_returns: int
    return_rate: float
    reasons: list[ReturnsAnalysis]


class CustomReport(BaseModel):
    name: str
    description: str
    query: str
    parameters: dict
    created_at: int
    last_run: int | None


class ReportFrequency(str, Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class ReportSchedule(BaseModel):
    report_id: int
    frequency: ReportFrequency
    next_run: int
    recipients: list[str]
