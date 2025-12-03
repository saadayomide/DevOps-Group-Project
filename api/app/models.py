"""
SQLAlchemy database models
Aligned to Team A's schema
"""
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    JSON,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.db import Base


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
    __table_args__ = (
        Index('idx_price_product_store', 'product_id', 'store_id'),
    )


class ShoppingList(Base):
    """Shopping list header"""
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_refreshed = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items = relationship(
        "ShoppingListItem",
        back_populates="list",
        cascade="all, delete-orphan",
    )


class ShoppingListItem(Base):
    """Shopping list items"""
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False)

    category = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    variants = Column(ARRAY(String).with_variant(JSON, "sqlite"), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(String, nullable=False)

    spec_json = Column(JSONB().with_variant(JSON, "sqlite"), nullable=True)

    best_store = Column(String, nullable=True)
    best_price = Column(Numeric(10, 2), nullable=True)
    best_url = Column(String, nullable=True)
    comparison_json = Column(JSONB().with_variant(JSON, "sqlite"), nullable=True)

    list = relationship("ShoppingList", back_populates="items")

