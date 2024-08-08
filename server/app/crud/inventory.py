# /server/app/crud/inventory.py
from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.app.models import (Product, ProductCategory,
                               Inventory, Location, Zone)
from server.app.schemas import (ProductCreate, ProductUpdate,
                                ProductCategoryCreate, ProductCategoryUpdate,
                                InventoryCreate, InventoryUpdate, LocationCreate,
                                LocationUpdate, ZoneCreate, ZoneUpdate, InventoryAdjustment, InventoryTransfer,
                                InventoryReport, ProductWithInventory, LocationWithInventory, InventoryMovement,
                                StocktakeCreate, StocktakeResult, ABCAnalysisResult, InventoryLocationSuggestion,
                                StocktakeDiscrepancy, ABCCategory)
from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    pass


class CRUDProductCategory(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    pass


class CRUDInventory(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):
    def adjust_quantity(self, db: Session, inventory_id: int, adjustment: InventoryAdjustment) -> Inventory:
        inventory = self.get(db, id=inventory_id)
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        inventory.quantity += adjustment.quantity
        inventory.last_updated = datetime.utcnow()
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return inventory

    def transfer(self, db: Session, transfer: InventoryTransfer) -> Inventory:
        from_inventory = db.query(Inventory).filter(
            Inventory.product_id == transfer.product_id,
            Inventory.location_id == transfer.from_location_id
        ).first()
        if not from_inventory or from_inventory.quantity < transfer.quantity:
            raise HTTPException(status_code=400, detail="Insufficient inventory for transfer")

        to_inventory = db.query(Inventory).filter(
            Inventory.product_id == transfer.product_id,
            Inventory.location_id == transfer.to_location_id
        ).first()

        if not to_inventory:
            to_inventory = Inventory(
                product_id=transfer.product_id,
                location_id=transfer.to_location_id,
                quantity=0
            )
            db.add(to_inventory)

        from_inventory.quantity -= transfer.quantity
        to_inventory.quantity += transfer.quantity

        db.commit()
        db.refresh(from_inventory)
        db.refresh(to_inventory)
        return to_inventory

    def get_inventory_report(self, db: Session) -> InventoryReport:
        total_products = db.query(func.count(Product.product_id)).scalar()
        total_quantity = db.query(func.sum(Inventory.quantity)).scalar()
        low_stock_items = self.get_low_stock_items(db, threshold=10)
        out_of_stock_items = self.get_out_of_stock_items(db)

        return InventoryReport(
            total_products=total_products,
            total_quantity=total_quantity,
            low_stock_items=low_stock_items,
            out_of_stock_items=out_of_stock_items
        )

    def perform_cycle_count(self, db: Session, location_id: int, counted_items: List[InventoryUpdate]) -> List[
        Inventory]:
        updated_items = []
        for item in counted_items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.location_id == location_id
            ).first()
            if inventory:
                inventory.quantity = item.quantity
                inventory.last_updated = datetime.utcnow()
                db.add(inventory)
                updated_items.append(inventory)
        db.commit()
        return updated_items

    def get_low_stock_items(self, db: Session, threshold: int) -> List[ProductWithInventory]:
        return db.query(Product).join(Inventory).filter(Inventory.quantity <= threshold).all()

    def get_out_of_stock_items(self, db: Session) -> List[Product]:
        return db.query(Product).outerjoin(Inventory).filter(
            (Inventory.quantity == 0) | (Inventory.quantity is None)  # == None?
        ).all()

    def create_reorder_list(self, db: Session, threshold: int) -> List[Product]:
        return self.get_low_stock_items(db, threshold)

    def get_product_locations(self, db: Session, product_id: int) -> List[LocationWithInventory]:
        return db.query(Location).join(Inventory).filter(Inventory.product_id == product_id).all()

    def batch_update(self, db: Session, updates: List[InventoryUpdate]) -> List[Inventory]:
        updated_items = []
        for update in updates:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == update.product_id,
                Inventory.location_id == update.location_id
            ).first()
            if inventory:
                for key, value in update.dict(exclude_unset=True).items():
                    setattr(inventory, key, value)
                inventory.last_updated = datetime.utcnow()
                db.add(inventory)
                updated_items.append(inventory)
        db.commit()
        return updated_items

    def get_movement_history(self, db: Session, product_id: int, start_date: Optional[datetime],
                             end_date: Optional[datetime]) -> List[InventoryMovement]:
        query = db.query(InventoryMovement).filter(InventoryMovement.product_id == product_id)
        if start_date:
            query = query.filter(InventoryMovement.timestamp >= start_date)
        if end_date:
            query = query.filter(InventoryMovement.timestamp <= end_date)
        return query.order_by(InventoryMovement.timestamp.desc()).all()

    def perform_stocktake(self, db: Session, stocktake: StocktakeCreate) -> StocktakeResult:
        discrepancies = []
        total_items = len(stocktake.items)
        accurate_items = 0

        for item in stocktake.items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.location_id == stocktake.location_id
            ).first()

            if inventory:
                expected_quantity = inventory.quantity
                discrepancy = item.counted_quantity - expected_quantity

                if discrepancy != 0:
                    discrepancies.append(StocktakeDiscrepancy(
                        product_id=item.product_id,
                        expected_quantity=expected_quantity,
                        counted_quantity=item.counted_quantity,
                        discrepancy=discrepancy
                    ))
                else:
                    accurate_items += 1

                inventory.quantity = item.counted_quantity
                inventory.last_updated = datetime.utcnow()
                db.add(inventory)

        db.commit()

        accuracy_percentage = (accurate_items / total_items) * 100 if total_items > 0 else 100

        return StocktakeResult(
            location_id=stocktake.location_id,
            total_items=total_items,
            discrepancies=discrepancies,
            accuracy_percentage=accuracy_percentage
        )

    def perform_abc_analysis(self, db: Session) -> ABCAnalysisResult:
        # Get all products with their total value (quantity * price)
        product_values = db.query(
            Product.product_id,
            Product.name,
            func.sum(Inventory.quantity * Product.price).label('total_value')
        ).join(Inventory).group_by(Product.product_id).all()

        # Sort products by total value in descending order
        sorted_products = sorted(product_values, key=lambda x: x.total_value, reverse=True)

        total_value = sum(product.total_value for product in sorted_products)
        cumulative_value = 0
        categories = defaultdict(list)

        for product in sorted_products:
            cumulative_value += product.total_value
            percentage = cumulative_value / total_value

            if percentage <= 0.8:
                category = 'A'
            elif percentage <= 0.95:
                category = 'B'
            else:
                category = 'C'

            categories[category].append(product)

        result = []
        for category, products in categories.items():
            category_value = sum(p.total_value for p in products)
            result.append(ABCCategory(
                category=category,
                products=[Product(product_id=p.product_id, name=p.name) for p in products],
                value_percentage=category_value / total_value * 100,
                item_percentage=len(products) / len(sorted_products) * 100
            ))

        return ABCAnalysisResult(categories=result)

    def optimize_locations(self, db: Session) -> List[InventoryLocationSuggestion]:
        # Get all products with their current locations and total quantity
        product_locations = db.query(
            Product.product_id,
            Inventory.location_id,
            func.sum(Inventory.quantity).label('total_quantity')
        ).join(Inventory).group_by(Product.product_id, Inventory.location_id).all()

        # Get all locations with their zone information
        locations = db.query(Location).all()
        zones = db.query(Zone).all()

        # Create a dictionary of zones with their locations
        zone_locations = defaultdict(list)
        for location in locations:
            zone_locations[location.zone_id].append(location)

        suggestions = []

        for product_location in product_locations:
            current_location = next(loc for loc in locations if loc.location_id == product_location.location_id)
            current_zone = next(zone for zone in zones if zone.zone_id == current_location.zone_id)

            # Determine the optimal zone based on product quantity
            if product_location.total_quantity > 1000:
                optimal_zone = next((z for z in zones if z.name == 'High Volume'), None)
            elif product_location.total_quantity > 100:
                optimal_zone = next((z for z in zones if z.name == 'Medium Volume'), None)
            else:
                optimal_zone = next((z for z in zones if z.name == 'Low Volume'), None)

            if optimal_zone and optimal_zone.zone_id != current_zone.zone_id:
                # Find the best location in the optimal zone
                optimal_location = min(zone_locations[optimal_zone.zone_id],
                                       key=lambda loc: (loc.aisle, loc.rack, loc.shelf, loc.bin))

                suggestions.append(InventoryLocationSuggestion(
                    product_id=product_location.product_id,
                    current_location_id=current_location.location_id,
                    suggested_location_id=optimal_location.location_id,
                    reason=f"Move from {current_zone.name} to {optimal_zone.name} zone for better inventory management"
                ))

        return suggestions


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    pass


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    pass


product = CRUDProduct(Product)
product_category = CRUDProductCategory(ProductCategory)
inventory = CRUDInventory(Inventory)
location = CRUDLocation(Location)
zone = CRUDZone(Zone)
