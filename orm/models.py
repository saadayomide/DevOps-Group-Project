from typing import List, Optional, Sequence

from sqlalchemy import (
    CheckConstraint,
    Column,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "Products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    category = Column(String(255), nullable=True)


class Supermarket(Base):
    __tablename__ = "Supermarkets"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "city"),
    )


class Price(Base):
    __tablename__ = "Prices"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("Products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("Supermarkets.id"), nullable=False)
    price = Column(DECIMAL(6, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("product_id", "store_id"),
        CheckConstraint("price >= 0.01"),
        Index("ix_prices_product_store", "product_id", "store_id"),
    )


def get_all_products(session: Session) -> List[Product]:
    """Return all products ordered by name."""
    return session.query(Product).order_by(Product.name).all()


def get_all_supermarkets(session: Session) -> List[Supermarket]:
    """Return all supermarkets ordered by name."""
    return session.query(Supermarket).order_by(Supermarket.name).all()


def get_prices_for(
    session: Session,
    product_ids: Optional[Sequence[int]] = None,
    store_ids: Optional[Sequence[int]] = None,
) -> List[Price]:
    """Return prices filtered by the provided product/store identifiers."""

    query = session.query(Price)

    if product_ids:
        query = query.filter(Price.product_id.in_(list(product_ids)))

    if store_ids:
        query = query.filter(Price.store_id.in_(list(store_ids)))

    return query.order_by(Price.product_id, Price.store_id).all()
