# /server/app/models/product.py
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    unit_of_measure = Column(String(20))
    weight = Column(Numeric(10, 2))
    dimensions = Column(String(50))
    barcode = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False)

    category = relationship("ProductCategory", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    po_items = relationship("POItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")
    inventory_adjustments = relationship("InventoryAdjustment", back_populates="product")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    parent_category_id = Column(Integer, ForeignKey("product_categories.id"))

    products = relationship("Product", back_populates="category")
    subcategories = relationship("ProductCategory")
