from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "Products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)


class Supermarket(Base):
    __tablename__ = "Supermarkets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "city"),
    )


class Price(Base):
    __tablename__ = "Prices"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("Products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("Supermarkets.id"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("product_id", "store_id"),
        CheckConstraint("price > 0"),
    )
