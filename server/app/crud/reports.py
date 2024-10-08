from datetime import timedelta, datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Product, Inventory, Order, OrderItem, Task
from public_api.shared_schemas import (
    InventorySummaryReport, InventoryItem, OrderSummaryReport, OrderSummary,
    WarehousePerformanceReport, WarehousePerformanceMetric, KPIDashboard, KPIMetric
)


class ReportsCRUD:
    def get_inventory_summary(self, db: Session) -> InventorySummaryReport:
        query = db.query(
            Product.id,
            Product.name.label("product_name"),
            func.sum(Inventory.quantity).label("quantity"),
            (func.sum(Inventory.quantity) * Product.price).label("value")
        ).join(Inventory).group_by(Product.id)

        items = [
            InventoryItem(
                product_id=row.id,
                product_name=row.product_name,
                quantity=row.quantity,
                value=float(row.value)
            )
            for row in query.all()
        ]

        total_items = sum(item.quantity for item in items)
        total_value = sum(item.value for item in items)

        return InventorySummaryReport(
            total_items=total_items,
            total_value=total_value,
            items=items
        )

    def get_order_summary(self, db: Session, start_date: int, end_date: int) -> OrderSummaryReport:
        query = db.query(
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_amount).label("total_revenue")
        ).filter(Order.order_date.between(start_date, end_date))

        result = query.first()
        total_orders = result.total_orders
        total_revenue = result.total_revenue or 0
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0

        summary = OrderSummary(
            total_orders=total_orders,
            total_revenue=float(total_revenue),
            average_order_value=float(average_order_value)
        )

        return OrderSummaryReport(
            start_date=start_date,
            end_date=end_date,
            summary=summary.model_dump()
        )

    def get_warehouse_performance(self, db: Session, start_date: int, end_date: int) -> WarehousePerformanceReport:
        # Order fulfillment rate
        total_orders = db.query(func.count(Order.id)).filter(
            Order.order_date.between(start_date, end_date)).scalar()
        fulfilled_orders = db.query(func.count(Order.id)).filter(
            Order.order_date.between(start_date, end_date),
            Order.status == "completed"
        ).scalar()
        fulfillment_rate = (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0

        # Average task completion time
        avg_task_completion_time = db.query(func.avg(Task.due_date - Task.created_at)).filter(
            Task.task_type == "picking",
            Task.created_at.between(start_date, end_date),
            Task.status == "completed"
        ).scalar()

        # Convert avg_task_completion_time to minutes
        avg_picking_time = avg_task_completion_time.total_seconds() / 60 if avg_task_completion_time else 0

        # Inventory turnover rate
        start_inventory = db.query(func.sum(Inventory.quantity)).filter(
            Inventory.last_updated <= start_date).scalar() or 0
        end_inventory = db.query(func.sum(Inventory.quantity)).filter(Inventory.last_updated <= end_date).scalar() or 0
        avg_inventory = (start_inventory + end_inventory) / 2

        cogs = db.query(func.sum(OrderItem.quantity * Product.price)).join(Product).filter(
            OrderItem.order_id == Order.id,
            Order.order_date.between(start_date, end_date)
        ).scalar() or 0

        inventory_turnover = float(cogs) / float(avg_inventory) if avg_inventory > 0 else 0

        metrics = [
            WarehousePerformanceMetric.model_validate({
                "name": "Order Fulfillment Rate",
                "value": fulfillment_rate,
                "unit": "%"
            }),
            WarehousePerformanceMetric.model_validate({
                "name": "Average Task Completion Time",
                "value": avg_picking_time,
                "unit": "minutes"
            }),
            WarehousePerformanceMetric.model_validate({
                "name": "Inventory Turnover Rate",
                "value": inventory_turnover,
                "unit": "turns"
            })
        ]

        return WarehousePerformanceReport(
            start_date=start_date,
            end_date=end_date,
            metrics=metrics
        )

    def get_kpi_dashboard(self, db: Session) -> KPIDashboard:
        today = int(datetime.utcnow().timestamp())
        yesterday = today - timedelta(days=1).total_seconds()
        last_week = today - timedelta(days=7).total_seconds()

        # Daily revenue
        today_revenue = db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.order_date) == today).scalar() or 0
        yesterday_revenue = db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.order_date) == yesterday).scalar() or 0
        revenue_trend = "up" if today_revenue > yesterday_revenue else "down" \
            if today_revenue < yesterday_revenue else "stable"

        # Weekly order count
        weekly_orders = db.query(func.count(Order.id)).filter(Order.order_date >= last_week).scalar()
        prev_week_orders = db.query(func.count(Order.id)).filter(
            Order.order_date.between(last_week - timedelta(days=7).total_seconds(), last_week)
        ).scalar()
        order_trend = "up" if weekly_orders > prev_week_orders else "down" \
            if weekly_orders < prev_week_orders else "stable"

        # Current inventory value
        inventory_value = db.query(func.sum(Inventory.quantity * Product.price)).join(Product).scalar() or 0

        # Pending shipments
        pending_shipments = db.query(func.count(Order.id)).filter(Order.status == "pending").scalar()

        metrics = [
            KPIMetric.model_validate({
                "name": "Daily Revenue",
                "value": today_revenue,
                "trend": revenue_trend
            }),
            KPIMetric.model_validate({
                "name": "Weekly Orders",
                "value": weekly_orders,
                "trend": order_trend
            }),
            KPIMetric.model_validate({
                "name": "Inventory Value",
                "value": inventory_value,
                "trend": "stable"
            }),
            KPIMetric.model_validate({
                "name": "Pending Shipments",
                "value": pending_shipments,
                "trend": "stable"
            })
        ]

        return KPIDashboard(
            date=today,
            metrics=metrics
        )


reports = ReportsCRUD()
