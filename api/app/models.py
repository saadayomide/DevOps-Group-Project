"""
SQLAlchemy database models
Aligned to Team A's schema
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from app.db import Base
from sqlalchemy import DateTime, JSON


class Product(Base):
    """Product model - Team A schema: Product(id, name, category)"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True, index=True)


class Supermarket(Base):
    """Supermarket model - Team A schema: Supermarket(id, name, city)"""

    __tablename__ = "supermarkets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=True, index=True)


class Price(Base):
    """Price model - Team A schema: Price(id, product_id, store_id, price)
    Note: store_id references supermarkets.id
    Price is stored as DECIMAL for precision, cast to float only at response
    """

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False)
    # Use Numeric (DECIMAL) for monetary values to maintain precision
    # Cast to float only at response time
    price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    product = relationship("Product", backref="prices")
    supermarket = relationship("Supermarket", backref="prices")

    # Indexes on (product_id, store_id) as specified
    __table_args__ = (Index("idx_price_product_store", "product_id", "store_id"),)


class ShoppingList(Base):
    """Shopping list parent - contains metadata and timestamp for last refresh"""

    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    last_refreshed = Column(DateTime, nullable=True)


class ShoppingListItem(Base):
    """Individual shopping list item with fields to store selected offer and comparison JSON"""

    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True)
    variants = Column(String, nullable=True)  # comma-separated or free-form

    # Selected best offer
    best_store = Column(String, nullable=True)
    best_price = Column(Numeric(10, 2), nullable=True)
    best_url = Column(String, nullable=True)

    # Full comparison breakdown for debugging / frontend
    comparison_json = Column(JSON, nullable=True)

    # Relationship
    shopping_list = relationship("ShoppingList", backref="items")
