"""Seed initial data for products, supermarkets, and prices

Revision ID: b2c3d4e5f6g7
Revises: aa91ec3623ad
Create Date: 2025-12-03

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from decimal import Decimal


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "aa91ec3623ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed database with initial products, supermarkets, and prices"""
    
    # Define table references for bulk insert
    supermarkets = table(
        "supermarkets",
        column("id", sa.Integer),
        column("name", sa.String),
        column("city", sa.String),
    )
    
    products = table(
        "products",
        column("id", sa.Integer),
        column("name", sa.String),
        column("category", sa.String),
    )
    
    prices = table(
        "prices",
        column("id", sa.Integer),
        column("product_id", sa.Integer),
        column("store_id", sa.Integer),
        column("price", sa.Numeric(10, 2)),
    )
    
    # Insert supermarkets
    op.bulk_insert(supermarkets, [
        {"id": 1, "name": "Mercadona", "city": "Madrid"},
        {"id": 2, "name": "Carrefour", "city": "Madrid"},
        {"id": 3, "name": "Lidl", "city": "Madrid"},
        {"id": 4, "name": "Alcampo", "city": "Madrid"},
        {"id": 5, "name": "Dia", "city": "Madrid"},
    ])
    
    # Insert products (Spanish grocery items)
    op.bulk_insert(products, [
        # Dairy
        {"id": 1, "name": "Leche entera", "category": "Lácteos"},
        {"id": 2, "name": "Leche desnatada", "category": "Lácteos"},
        {"id": 3, "name": "Huevos (docena)", "category": "Lácteos"},
        {"id": 4, "name": "Yogur natural", "category": "Lácteos"},
        {"id": 5, "name": "Queso manchego", "category": "Lácteos"},
        # Bakery
        {"id": 6, "name": "Pan de molde", "category": "Panadería"},
        {"id": 7, "name": "Baguette", "category": "Panadería"},
        {"id": 8, "name": "Croissants", "category": "Panadería"},
        # Meat
        {"id": 9, "name": "Pollo entero", "category": "Carnes"},
        {"id": 10, "name": "Carne picada", "category": "Carnes"},
        {"id": 11, "name": "Jamón serrano", "category": "Carnes"},
        # Produce
        {"id": 12, "name": "Tomates", "category": "Frutas y Verduras"},
        {"id": 13, "name": "Patatas", "category": "Frutas y Verduras"},
        {"id": 14, "name": "Cebollas", "category": "Frutas y Verduras"},
        {"id": 15, "name": "Plátanos", "category": "Frutas y Verduras"},
        {"id": 16, "name": "Manzanas", "category": "Frutas y Verduras"},
        {"id": 17, "name": "Naranjas", "category": "Frutas y Verduras"},
        # Pantry
        {"id": 18, "name": "Arroz", "category": "Despensa"},
        {"id": 19, "name": "Pasta", "category": "Despensa"},
        {"id": 20, "name": "Aceite de oliva", "category": "Despensa"},
        {"id": 21, "name": "Azúcar", "category": "Despensa"},
        {"id": 22, "name": "Sal", "category": "Despensa"},
        # Beverages
        {"id": 23, "name": "Agua mineral", "category": "Bebidas"},
        {"id": 24, "name": "Zumo de naranja", "category": "Bebidas"},
        {"id": 25, "name": "Coca-Cola", "category": "Bebidas"},
        # English names as aliases (for search flexibility)
        {"id": 26, "name": "Milk", "category": "Dairy"},
        {"id": 27, "name": "Bread", "category": "Bakery"},
        {"id": 28, "name": "Eggs", "category": "Dairy"},
        {"id": 29, "name": "Chicken", "category": "Meat"},
        {"id": 30, "name": "Rice", "category": "Pantry"},
    ])
    
    # Insert prices (product_id, store_id, price)
    # Store IDs: 1=Mercadona, 2=Carrefour, 3=Lidl, 4=Alcampo, 5=Dia
    prices_data = [
        # Leche entera (product 1)
        {"id": 1, "product_id": 1, "store_id": 1, "price": Decimal("0.89")},
        {"id": 2, "product_id": 1, "store_id": 2, "price": Decimal("0.95")},
        {"id": 3, "product_id": 1, "store_id": 3, "price": Decimal("0.79")},
        {"id": 4, "product_id": 1, "store_id": 4, "price": Decimal("0.85")},
        {"id": 5, "product_id": 1, "store_id": 5, "price": Decimal("0.92")},
        
        # Leche desnatada (product 2)
        {"id": 6, "product_id": 2, "store_id": 1, "price": Decimal("0.85")},
        {"id": 7, "product_id": 2, "store_id": 2, "price": Decimal("0.89")},
        {"id": 8, "product_id": 2, "store_id": 3, "price": Decimal("0.75")},
        {"id": 9, "product_id": 2, "store_id": 4, "price": Decimal("0.82")},
        {"id": 10, "product_id": 2, "store_id": 5, "price": Decimal("0.88")},
        
        # Huevos docena (product 3)
        {"id": 11, "product_id": 3, "store_id": 1, "price": Decimal("2.49")},
        {"id": 12, "product_id": 3, "store_id": 2, "price": Decimal("2.65")},
        {"id": 13, "product_id": 3, "store_id": 3, "price": Decimal("2.29")},
        {"id": 14, "product_id": 3, "store_id": 4, "price": Decimal("2.45")},
        {"id": 15, "product_id": 3, "store_id": 5, "price": Decimal("2.55")},
        
        # Yogur natural (product 4)
        {"id": 16, "product_id": 4, "store_id": 1, "price": Decimal("1.25")},
        {"id": 17, "product_id": 4, "store_id": 2, "price": Decimal("1.39")},
        {"id": 18, "product_id": 4, "store_id": 3, "price": Decimal("1.15")},
        {"id": 19, "product_id": 4, "store_id": 4, "price": Decimal("1.29")},
        {"id": 20, "product_id": 4, "store_id": 5, "price": Decimal("1.35")},
        
        # Queso manchego (product 5)
        {"id": 21, "product_id": 5, "store_id": 1, "price": Decimal("8.95")},
        {"id": 22, "product_id": 5, "store_id": 2, "price": Decimal("9.25")},
        {"id": 23, "product_id": 5, "store_id": 3, "price": Decimal("8.49")},
        {"id": 24, "product_id": 5, "store_id": 4, "price": Decimal("8.75")},
        {"id": 25, "product_id": 5, "store_id": 5, "price": Decimal("9.15")},
        
        # Pan de molde (product 6)
        {"id": 26, "product_id": 6, "store_id": 1, "price": Decimal("1.45")},
        {"id": 27, "product_id": 6, "store_id": 2, "price": Decimal("1.59")},
        {"id": 28, "product_id": 6, "store_id": 3, "price": Decimal("1.29")},
        {"id": 29, "product_id": 6, "store_id": 4, "price": Decimal("1.39")},
        {"id": 30, "product_id": 6, "store_id": 5, "price": Decimal("1.55")},
        
        # Baguette (product 7)
        {"id": 31, "product_id": 7, "store_id": 1, "price": Decimal("0.65")},
        {"id": 32, "product_id": 7, "store_id": 2, "price": Decimal("0.75")},
        {"id": 33, "product_id": 7, "store_id": 3, "price": Decimal("0.55")},
        {"id": 34, "product_id": 7, "store_id": 4, "price": Decimal("0.59")},
        {"id": 35, "product_id": 7, "store_id": 5, "price": Decimal("0.69")},
        
        # Croissants (product 8)
        {"id": 36, "product_id": 8, "store_id": 1, "price": Decimal("2.25")},
        {"id": 37, "product_id": 8, "store_id": 2, "price": Decimal("2.49")},
        {"id": 38, "product_id": 8, "store_id": 3, "price": Decimal("1.99")},
        {"id": 39, "product_id": 8, "store_id": 4, "price": Decimal("2.15")},
        {"id": 40, "product_id": 8, "store_id": 5, "price": Decimal("2.35")},
        
        # Pollo entero (product 9)
        {"id": 41, "product_id": 9, "store_id": 1, "price": Decimal("5.95")},
        {"id": 42, "product_id": 9, "store_id": 2, "price": Decimal("6.25")},
        {"id": 43, "product_id": 9, "store_id": 3, "price": Decimal("5.49")},
        {"id": 44, "product_id": 9, "store_id": 4, "price": Decimal("5.75")},
        {"id": 45, "product_id": 9, "store_id": 5, "price": Decimal("6.15")},
        
        # Carne picada (product 10)
        {"id": 46, "product_id": 10, "store_id": 1, "price": Decimal("6.49")},
        {"id": 47, "product_id": 10, "store_id": 2, "price": Decimal("6.95")},
        {"id": 48, "product_id": 10, "store_id": 3, "price": Decimal("5.99")},
        {"id": 49, "product_id": 10, "store_id": 4, "price": Decimal("6.25")},
        {"id": 50, "product_id": 10, "store_id": 5, "price": Decimal("6.75")},
        
        # Jamón serrano (product 11)
        {"id": 51, "product_id": 11, "store_id": 1, "price": Decimal("12.95")},
        {"id": 52, "product_id": 11, "store_id": 2, "price": Decimal("13.49")},
        {"id": 53, "product_id": 11, "store_id": 3, "price": Decimal("11.99")},
        {"id": 54, "product_id": 11, "store_id": 4, "price": Decimal("12.25")},
        {"id": 55, "product_id": 11, "store_id": 5, "price": Decimal("13.25")},
        
        # Tomates (product 12)
        {"id": 56, "product_id": 12, "store_id": 1, "price": Decimal("2.15")},
        {"id": 57, "product_id": 12, "store_id": 2, "price": Decimal("2.35")},
        {"id": 58, "product_id": 12, "store_id": 3, "price": Decimal("1.89")},
        {"id": 59, "product_id": 12, "store_id": 4, "price": Decimal("1.99")},
        {"id": 60, "product_id": 12, "store_id": 5, "price": Decimal("2.25")},
        
        # Patatas (product 13)
        {"id": 61, "product_id": 13, "store_id": 1, "price": Decimal("1.29")},
        {"id": 62, "product_id": 13, "store_id": 2, "price": Decimal("1.45")},
        {"id": 63, "product_id": 13, "store_id": 3, "price": Decimal("1.09")},
        {"id": 64, "product_id": 13, "store_id": 4, "price": Decimal("1.19")},
        {"id": 65, "product_id": 13, "store_id": 5, "price": Decimal("1.35")},
        
        # Cebollas (product 14)
        {"id": 66, "product_id": 14, "store_id": 1, "price": Decimal("1.15")},
        {"id": 67, "product_id": 14, "store_id": 2, "price": Decimal("1.29")},
        {"id": 68, "product_id": 14, "store_id": 3, "price": Decimal("0.99")},
        {"id": 69, "product_id": 14, "store_id": 4, "price": Decimal("1.05")},
        {"id": 70, "product_id": 14, "store_id": 5, "price": Decimal("1.19")},
        
        # Plátanos (product 15)
        {"id": 71, "product_id": 15, "store_id": 1, "price": Decimal("1.69")},
        {"id": 72, "product_id": 15, "store_id": 2, "price": Decimal("1.85")},
        {"id": 73, "product_id": 15, "store_id": 3, "price": Decimal("1.49")},
        {"id": 74, "product_id": 15, "store_id": 4, "price": Decimal("1.59")},
        {"id": 75, "product_id": 15, "store_id": 5, "price": Decimal("1.75")},
        
        # Manzanas (product 16)
        {"id": 76, "product_id": 16, "store_id": 1, "price": Decimal("2.29")},
        {"id": 77, "product_id": 16, "store_id": 2, "price": Decimal("2.49")},
        {"id": 78, "product_id": 16, "store_id": 3, "price": Decimal("1.99")},
        {"id": 79, "product_id": 16, "store_id": 4, "price": Decimal("2.15")},
        {"id": 80, "product_id": 16, "store_id": 5, "price": Decimal("2.39")},
        
        # Naranjas (product 17)
        {"id": 81, "product_id": 17, "store_id": 1, "price": Decimal("1.89")},
        {"id": 82, "product_id": 17, "store_id": 2, "price": Decimal("2.05")},
        {"id": 83, "product_id": 17, "store_id": 3, "price": Decimal("1.69")},
        {"id": 84, "product_id": 17, "store_id": 4, "price": Decimal("1.79")},
        {"id": 85, "product_id": 17, "store_id": 5, "price": Decimal("1.95")},
        
        # Arroz (product 18)
        {"id": 86, "product_id": 18, "store_id": 1, "price": Decimal("1.45")},
        {"id": 87, "product_id": 18, "store_id": 2, "price": Decimal("1.59")},
        {"id": 88, "product_id": 18, "store_id": 3, "price": Decimal("1.25")},
        {"id": 89, "product_id": 18, "store_id": 4, "price": Decimal("1.35")},
        {"id": 90, "product_id": 18, "store_id": 5, "price": Decimal("1.49")},
        
        # Pasta (product 19)
        {"id": 91, "product_id": 19, "store_id": 1, "price": Decimal("0.95")},
        {"id": 92, "product_id": 19, "store_id": 2, "price": Decimal("1.09")},
        {"id": 93, "product_id": 19, "store_id": 3, "price": Decimal("0.79")},
        {"id": 94, "product_id": 19, "store_id": 4, "price": Decimal("0.85")},
        {"id": 95, "product_id": 19, "store_id": 5, "price": Decimal("0.99")},
        
        # Aceite de oliva (product 20)
        {"id": 96, "product_id": 20, "store_id": 1, "price": Decimal("6.95")},
        {"id": 97, "product_id": 20, "store_id": 2, "price": Decimal("7.25")},
        {"id": 98, "product_id": 20, "store_id": 3, "price": Decimal("6.49")},
        {"id": 99, "product_id": 20, "store_id": 4, "price": Decimal("6.75")},
        {"id": 100, "product_id": 20, "store_id": 5, "price": Decimal("7.15")},
        
        # Azúcar (product 21)
        {"id": 101, "product_id": 21, "store_id": 1, "price": Decimal("1.19")},
        {"id": 102, "product_id": 21, "store_id": 2, "price": Decimal("1.29")},
        {"id": 103, "product_id": 21, "store_id": 3, "price": Decimal("0.99")},
        {"id": 104, "product_id": 21, "store_id": 4, "price": Decimal("1.09")},
        {"id": 105, "product_id": 21, "store_id": 5, "price": Decimal("1.25")},
        
        # Sal (product 22)
        {"id": 106, "product_id": 22, "store_id": 1, "price": Decimal("0.55")},
        {"id": 107, "product_id": 22, "store_id": 2, "price": Decimal("0.65")},
        {"id": 108, "product_id": 22, "store_id": 3, "price": Decimal("0.45")},
        {"id": 109, "product_id": 22, "store_id": 4, "price": Decimal("0.49")},
        {"id": 110, "product_id": 22, "store_id": 5, "price": Decimal("0.59")},
        
        # Agua mineral (product 23)
        {"id": 111, "product_id": 23, "store_id": 1, "price": Decimal("0.35")},
        {"id": 112, "product_id": 23, "store_id": 2, "price": Decimal("0.45")},
        {"id": 113, "product_id": 23, "store_id": 3, "price": Decimal("0.25")},
        {"id": 114, "product_id": 23, "store_id": 4, "price": Decimal("0.29")},
        {"id": 115, "product_id": 23, "store_id": 5, "price": Decimal("0.39")},
        
        # Zumo de naranja (product 24)
        {"id": 116, "product_id": 24, "store_id": 1, "price": Decimal("1.79")},
        {"id": 117, "product_id": 24, "store_id": 2, "price": Decimal("1.95")},
        {"id": 118, "product_id": 24, "store_id": 3, "price": Decimal("1.59")},
        {"id": 119, "product_id": 24, "store_id": 4, "price": Decimal("1.69")},
        {"id": 120, "product_id": 24, "store_id": 5, "price": Decimal("1.85")},
        
        # Coca-Cola (product 25)
        {"id": 121, "product_id": 25, "store_id": 1, "price": Decimal("1.49")},
        {"id": 122, "product_id": 25, "store_id": 2, "price": Decimal("1.65")},
        {"id": 123, "product_id": 25, "store_id": 3, "price": Decimal("1.35")},
        {"id": 124, "product_id": 25, "store_id": 4, "price": Decimal("1.39")},
        {"id": 125, "product_id": 25, "store_id": 5, "price": Decimal("1.55")},
        
        # English name products (26-30)
        # Milk (product 26) - same prices as Leche entera
        {"id": 126, "product_id": 26, "store_id": 1, "price": Decimal("0.89")},
        {"id": 127, "product_id": 26, "store_id": 2, "price": Decimal("0.95")},
        {"id": 128, "product_id": 26, "store_id": 3, "price": Decimal("0.79")},
        {"id": 129, "product_id": 26, "store_id": 4, "price": Decimal("0.85")},
        {"id": 130, "product_id": 26, "store_id": 5, "price": Decimal("0.92")},
        
        # Bread (product 27)
        {"id": 131, "product_id": 27, "store_id": 1, "price": Decimal("1.45")},
        {"id": 132, "product_id": 27, "store_id": 2, "price": Decimal("1.59")},
        {"id": 133, "product_id": 27, "store_id": 3, "price": Decimal("1.29")},
        {"id": 134, "product_id": 27, "store_id": 4, "price": Decimal("1.39")},
        {"id": 135, "product_id": 27, "store_id": 5, "price": Decimal("1.55")},
        
        # Eggs (product 28)
        {"id": 136, "product_id": 28, "store_id": 1, "price": Decimal("2.49")},
        {"id": 137, "product_id": 28, "store_id": 2, "price": Decimal("2.65")},
        {"id": 138, "product_id": 28, "store_id": 3, "price": Decimal("2.29")},
        {"id": 139, "product_id": 28, "store_id": 4, "price": Decimal("2.45")},
        {"id": 140, "product_id": 28, "store_id": 5, "price": Decimal("2.55")},
        
        # Chicken (product 29)
        {"id": 141, "product_id": 29, "store_id": 1, "price": Decimal("5.95")},
        {"id": 142, "product_id": 29, "store_id": 2, "price": Decimal("6.25")},
        {"id": 143, "product_id": 29, "store_id": 3, "price": Decimal("5.49")},
        {"id": 144, "product_id": 29, "store_id": 4, "price": Decimal("5.75")},
        {"id": 145, "product_id": 29, "store_id": 5, "price": Decimal("6.15")},
        
        # Rice (product 30)
        {"id": 146, "product_id": 30, "store_id": 1, "price": Decimal("1.45")},
        {"id": 147, "product_id": 30, "store_id": 2, "price": Decimal("1.59")},
        {"id": 148, "product_id": 30, "store_id": 3, "price": Decimal("1.25")},
        {"id": 149, "product_id": 30, "store_id": 4, "price": Decimal("1.35")},
        {"id": 150, "product_id": 30, "store_id": 5, "price": Decimal("1.49")},
    ]
    
    op.bulk_insert(prices, prices_data)


def downgrade() -> None:
    """Remove seeded data"""
    # Delete in reverse order due to foreign keys
    op.execute("DELETE FROM prices WHERE id <= 150")
    op.execute("DELETE FROM products WHERE id <= 30")
    op.execute("DELETE FROM supermarkets WHERE id <= 5")

