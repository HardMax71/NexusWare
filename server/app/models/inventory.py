from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("product_categories.category_id"))
    unit_of_measure = Column(String(20))
    weight = Column(Numeric(10, 2))
    dimensions = Column(String(50))
    barcode = Column(String(50))

    category = relationship("ProductCategory", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    parent_category_id = Column(Integer, ForeignKey("product_categories.category_id"))

    products = relationship("Product", back_populates="category")
    subcategories = relationship("ProductCategory")


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.zone_id"))
    aisle = Column(String(10))
    rack = Column(String(10))
    shelf = Column(String(10))
    bin = Column(String(10))

    zone = relationship("Zone", back_populates="locations")
    inventory_items = relationship("Inventory", back_populates="location")


class Zone(Base):
    __tablename__ = "zones"

    zone_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)

    locations = relationship("Location", back_populates="zone")
