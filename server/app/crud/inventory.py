# /server/app/crud/inventory.py
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from server.app.models import (
    Product, ProductCategory, Inventory, Location, Zone
)
from server.app.schemas import (
    Product as ProductSchema,
    ProductWithInventory as ProductWithInventorySchema,
    ProductCreate, ProductUpdate,
    ProductCategoryCreate, ProductCategoryUpdate,
    Inventory as InventorySchema,
    InventoryCreate, InventoryUpdate, LocationCreate,
    LocationUpdate, ZoneCreate, ZoneUpdate, InventoryAdjustment, InventoryTransfer,
    InventoryReport, LocationWithInventory as LocationWithInventorySchema, InventoryMovement,
    StocktakeCreate, StocktakeResult, ABCAnalysisResult, InventoryLocationSuggestion,
    StocktakeDiscrepancy, ABCCategory, ProductFilter, LocationFilter, ZoneWithLocations, StorageUtilization,
    BulkImportData, BulkImportResult
)
from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_with_category_and_inventory(self, db: Session, id: int) -> Optional[ProductWithInventorySchema]:
        current_product = db.query(Product).filter(Product.product_id == id).options(
            joinedload(Product.category),
            joinedload(Product.inventory_items)
        ).first()
        return ProductWithInventorySchema.model_validate(current_product) if current_product else None

    def get_multi_with_category_and_inventory(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: Optional[ProductFilter] = None) -> list[ProductWithInventorySchema]:
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.inventory_items)
        )

        if filter_params:
            if filter_params.name:
                query = query.filter(Product.name.ilike(f"%{filter_params.name}%"))
            if filter_params.category_id:
                query = query.filter(Product.category_id == filter_params.category_id)
            if filter_params.sku:
                query = query.filter(Product.sku == filter_params.sku)
            if filter_params.barcode:
                query = query.filter(Product.barcode == filter_params.barcode)

        products = query.offset(skip).limit(limit).all()
        return [ProductWithInventorySchema.model_validate(product) for product in products]

    def get_by_barcode(self, db: Session, barcode: str) -> Optional[ProductSchema]:
        current_product = db.query(Product).filter(Product.barcode == barcode).first()
        return ProductSchema.model_validate(current_product) if current_product else None


class CRUDProductCategory(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    pass


class CRUDInventory(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):

    def adjust_quantity(self, db: Session, inventory_id: int, adjustment: InventoryAdjustment) -> InventorySchema:
        current_inventory = self.get(db, id=inventory_id)
        if not current_inventory:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        current_inventory.quantity += adjustment.quantity
        current_inventory.last_updated = datetime.utcnow()
        db.add(current_inventory)
        db.commit()
        db.refresh(current_inventory)
        return InventorySchema.model_validate(current_inventory)

    def transfer(self, db: Session, transfer: InventoryTransfer) -> InventorySchema:
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
        return InventorySchema.model_validate(to_inventory)

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

    def perform_cycle_count(self, db: Session,
                            location_id: int, counted_items: list[InventoryUpdate]) -> list[InventorySchema]:
        updated_items = []
        for item in counted_items:
            current_inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.location_id == location_id
            ).first()
            if current_inventory:
                current_inventory.quantity = item.quantity
                current_inventory.last_updated = datetime.utcnow()
                db.add(current_inventory)
                updated_items.append(current_inventory)
        db.commit()
        return [InventorySchema.model_validate(x) for x in updated_items]

    def get_low_stock_items(self, db: Session, threshold: int) -> list[ProductWithInventorySchema]:
        products = db.query(Product).join(Inventory).filter(Inventory.quantity <= threshold).all()
        return [ProductWithInventorySchema.model_validate(x) for x in products]

    def get_out_of_stock_items(self, db: Session) -> list[ProductSchema]:
        products = db.query(Product).outerjoin(Inventory).filter(
            (Inventory.quantity == 0) | (Inventory.quantity.is_(None))
        ).all()
        return [ProductSchema.model_validate(product) for product in products]

    def create_reorder_list(self, db: Session, threshold: int) -> list[ProductSchema]:
        return self.get_low_stock_items(db, threshold)

    def get_product_locations(self, db: Session, product_id: int) -> list[LocationWithInventorySchema]:
        locations = db.query(Location).join(Inventory).filter(Inventory.product_id == product_id).all()
        return [LocationWithInventorySchema.model_validate(location) for location in locations]

    def batch_update(self, db: Session, updates: list[InventoryUpdate]) -> list[InventorySchema]:
        updated_items = []
        for update in updates:
            current_inventory = db.query(Inventory).filter(
                Inventory.product_id == update.product_id,
                Inventory.location_id == update.location_id
            ).first()
            if current_inventory:
                for key, value in update.dict(exclude_unset=True).items():
                    setattr(current_inventory, key, value)
                current_inventory.last_updated = datetime.utcnow()
                db.add(current_inventory)
                updated_items.append(current_inventory)
        db.commit()
        return [InventorySchema.model_validate(inventory) for inventory in updated_items]

    def get_movement_history(self, db: Session, product_id: int, start_date: Optional[datetime],
                             end_date: Optional[datetime]) -> list[InventoryMovement]:
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
            current_inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.location_id == stocktake.location_id
            ).first()

            if current_inventory:
                expected_quantity = current_inventory.quantity
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

                current_inventory.quantity = item.counted_quantity
                current_inventory.last_updated = datetime.utcnow()
                db.add(current_inventory)

        db.commit()

        accuracy_percentage = (accurate_items / total_items) * 100 if total_items > 0 else 100

        return StocktakeResult(
            location_id=stocktake.location_id,
            total_items=total_items,
            discrepancies=discrepancies,
            accuracy_percentage=accuracy_percentage
        )

    def perform_abc_analysis(self, db: Session) -> ABCAnalysisResult:
        product_values = db.query(
            Product.product_id,
            Product.name,
            func.sum(Inventory.quantity * Product.price).label('total_value')
        ).join(Inventory).group_by(Product.product_id).all()

        sorted_products = sorted(product_values, key=lambda x: x.total_value, reverse=True)

        total_value = sum(x.total_value for x in sorted_products)
        cumulative_value = 0
        categories = defaultdict(list)

        for current_product in sorted_products:
            cumulative_value += current_product.total_value
            percentage = cumulative_value / total_value

            if percentage <= 0.8:
                category = 'A'
            elif percentage <= 0.95:
                category = 'B'
            else:
                category = 'C'

            categories[category].append(current_product)

        result = []
        for category, products in categories.items():
            category_value = sum(p.total_value for p in products)
            result.append(ABCCategory(
                category=category,
                products=[ProductSchema.model_validate(p) for p in products],
                value_percentage=category_value / total_value * 100,
                item_percentage=len(products) / len(sorted_products) * 100
            ))

        return ABCAnalysisResult(categories=result)

    def optimize_locations(self, db: Session) -> list[InventoryLocationSuggestion]:
        product_locations = db.query(
            Product.product_id,
            Inventory.location_id,
            func.sum(Inventory.quantity).label('total_quantity')
        ).join(Inventory).group_by(Product.product_id, Inventory.location_id).all()

        locations = db.query(Location).all()
        zones = db.query(Zone).all()

        zone_locations = defaultdict(list)
        for current_location in locations:
            zone_locations[current_location.zone_id].append(current_location)

        suggestions = []

        for product_location in product_locations:
            current_location = next(loc for loc in locations if loc.location_id == product_location.location_id)
            current_zone = next(zone for zone in zones if zone.zone_id == current_location.zone_id)

            if product_location.total_quantity > 1000:
                optimal_zone = next((z for z in zones if z.name == 'High Volume'), None)
            elif product_location.total_quantity > 100:
                optimal_zone = next((z for z in zones if z.name == 'Medium Volume'), None)
            else:
                optimal_zone = next((z for z in zones if z.name == 'Low Volume'), None)

            if optimal_zone and optimal_zone.zone_id != current_zone.zone_id:
                optimal_location = min(zone_locations[optimal_zone.zone_id],
                                       key=lambda loc: (loc.aisle, loc.rack, loc.shelf, loc.bin))

                suggestions.append(InventoryLocationSuggestion(
                    product_id=product_location.product_id,
                    current_location_id=current_location.location_id,
                    suggested_location_id=optimal_location.location_id,
                    reason=f"Move from {current_zone.name} to {optimal_zone.name} zone for better inventory management"
                ))

        return suggestions

    def get_expiring_soon(self, db: Session, days: int) -> list[ProductWithInventorySchema]:
        expiration_date = datetime.utcnow() + timedelta(days=days)
        products = db.query(Product).join(Inventory).filter(Inventory.expiration_date <= expiration_date).all()
        return [ProductWithInventorySchema.model_validate(product) for product in products]

    def bulk_import(self, db: Session, import_data: BulkImportData) -> BulkImportResult:
        successful_imports = []
        failed_imports = []

        for item in import_data.items:
            try:
                product = db.query(Product).filter(Product.sku == item.sku).first()
                if not product:
                    product = Product(sku=item.sku, name=item.name, category_id=item.category_id)
                    db.add(product)
                    db.flush()

                inventory = db.query(Inventory).filter(
                    Inventory.product_id == product.product_id,
                    Inventory.location_id == item.location_id
                ).first()

                if inventory:
                    inventory.quantity += item.quantity
                else:
                    inventory = Inventory(
                        product_id=product.product_id,
                        location_id=item.location_id,
                        quantity=item.quantity
                    )
                    db.add(inventory)

                successful_imports.append(item)
            except Exception as e:
                failed_imports.append((item, str(e)))

        db.commit()
        return BulkImportResult(
            successful_imports=successful_imports,
            failed_imports=failed_imports
        )

    def get_storage_utilization(self, db: Session) -> StorageUtilization:
        # TODO: func.sum(Location.location_id) - colculate total capacity better, now placeholder
        total_capacity = db.query(func.sum(Location.location_id)).scalar() or 0
        total_used = db.query(func.sum(Inventory.quantity)).scalar() or 0
        utilization_percentage = (total_used / total_capacity * 100) if total_capacity > 0 else 0

        zone_utilization = db.query(
            Zone.name,
            func.sum(Location.location_id).label('capacity'),
            func.sum(Inventory.quantity).label('used')
        ).join(Location, Zone.zone_id == Location.zone_id) \
            .outerjoin(Inventory, Location.location_id == Inventory.location_id) \
            .group_by(Zone.zone_id).all()

        return StorageUtilization(
            total_capacity=total_capacity,
            total_used=total_used,
            utilization_percentage=utilization_percentage,
            zone_utilization=[
                {
                    "zone_name": zu.name,
                    "capacity": zu.capacity,
                    "used": zu.used,
                    "utilization_percentage": (zu.used / zu.capacity * 100) if zu.capacity > 0 else 0
                } for zu in zone_utilization
            ]
        )

    def advanced_search(
            self,
            db: Session,
            q: Optional[str] = None,
            category_id: Optional[int] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            in_stock: Optional[bool] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[str] = "asc"
    ) -> list[ProductSchema]:
        query = db.query(Product)

        # Apply search filters
        if q:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{q}%"),
                    Product.sku.ilike(f"%{q}%"),
                    Product.description.ilike(f"%{q}%")
                )
            )

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        if in_stock is not None:
            if in_stock:
                query = query.join(Inventory).filter(Inventory.quantity > 0)
            else:
                query = query.outerjoin(Inventory).filter(
                    or_(Inventory.quantity == 0, Inventory.quantity is None)
                )

        # Apply sorting
        if sort_by:
            sort_column = getattr(Product, sort_by, None)
            if sort_column is not None:
                if sort_order.lower() == "desc":
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)

        # Execute query and return results
        products = query.all()
        return [ProductSchema.model_validate(product) for product in products]


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    def get_multi_with_inventory(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: Optional[LocationFilter] = None) -> list[LocationWithInventorySchema]:
        query = db.query(Location).options(joinedload(Location.inventory_items))

        if filter_params:
            if filter_params.zone_id:
                query = query.filter(Location.zone_id == filter_params.zone_id)
            if filter_params.aisle:
                query = query.filter(Location.aisle == filter_params.aisle)
            if filter_params.rack:
                query = query.filter(Location.rack == filter_params.rack)
            if filter_params.shelf:
                query = query.filter(Location.shelf == filter_params.shelf)
            if filter_params.bin:
                query = query.filter(Location.bin == filter_params.bin)

        locations = query.offset(skip).limit(limit).all()
        return [LocationWithInventorySchema.model_validate(location) for location in locations]

    def get_with_inventory(self, db: Session, id: int) -> Optional[LocationWithInventorySchema]:
        location = db.query(Location).filter(Location.location_id == id).options(
            joinedload(Location.inventory_items)).first()
        return LocationWithInventorySchema.model_validate(location) if location else None


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    def get_warehouse_layout(self, db: Session) -> list[ZoneWithLocations]:
        zones = db.query(Zone).options(joinedload(Zone.locations)).all()
        return [ZoneWithLocations.model_validate(zone) for zone in zones]

    def get_multi_with_locations(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: Optional[LocationFilter] = None) -> list[ZoneWithLocations]:
        query = db.query(Zone).options(joinedload(Zone.locations))

        if filter_params:
            if filter_params.name:
                query = query.filter(Zone.name.ilike(f"%{filter_params.name}%"))

        zones = query.offset(skip).limit(limit).all()
        return [ZoneWithLocations.model_validate(zone) for zone in zones]

    def get_with_locations(self, db: Session, id: int) -> Optional[ZoneWithLocations]:
        zone = db.query(Zone).filter(Zone.zone_id == id).options(joinedload(Zone.locations)).first()
        return ZoneWithLocations.model_validate(zone) if zone else None


product = CRUDProduct(Product)
product_category = CRUDProductCategory(ProductCategory)
inventory = CRUDInventory(Inventory)
location = CRUDLocation(Location)
zone = CRUDZone(Zone)
