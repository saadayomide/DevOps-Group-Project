"""
Pydantic schemas for request/response validation
Aligned to Team A's schema
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


# Product Schemas - Team A schema: Product(id, name, category)
class ProductBase(BaseModel):
    """Base product schema"""

    name: str
    category: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a product"""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""

    name: Optional[str] = None
    category: Optional[str] = None


class Product(ProductBase):
    """Schema for product response"""

    id: int
    model_config = ConfigDict(from_attributes=True)


# Simplified response schemas for GET endpoints (small & consistent)
class ProductResponse(BaseModel):
    """Simplified product response for GET /products - returns only id and name"""

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class SupermarketResponse(BaseModel):
    """Simplified supermarket response for GET /supermarkets - returns only id and name"""

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# Supermarket Schemas - Team A schema: Supermarket(id, name, city)
class SupermarketBase(BaseModel):
    """Base supermarket schema"""

    name: str
    city: Optional[str] = None


class SupermarketCreate(SupermarketBase):
    """Schema for creating a supermarket"""

    pass


class SupermarketUpdate(BaseModel):
    """Schema for updating a supermarket"""

    name: Optional[str] = None
    city: Optional[str] = None


class Supermarket(SupermarketBase):
    """Schema for supermarket response"""

    id: int
    model_config = ConfigDict(from_attributes=True)


# Price Schemas - Team A schema: Price(id, product_id, store_id, price)
class PriceBase(BaseModel):
    """Base price schema"""

    product_id: int
    store_id: int = Field(..., description="References supermarkets.id")
    price: float = Field(gt=0, description="Price must be greater than 0")


class PriceCreate(PriceBase):
    """Schema for creating a price"""

    pass


class PriceUpdate(BaseModel):
    """Schema for updating a price"""

    product_id: Optional[int] = None
    store_id: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)


class Price(PriceBase):
    """Schema for price response"""

    id: int
    model_config = ConfigDict(from_attributes=True)


# Comparison Schemas - Single source of truth for output format (DoD)
class CompareRequest(BaseModel):
    """Request schema for comparing items across stores"""

    items: List[str] = Field(..., description="List of product names to compare")
    stores: List[str] = Field(..., description="List of store names to compare across")


class CompareItem(BaseModel):
    """Schema for a single compared item"""

    name: str = Field(..., description="Product name")
    store: str = Field(..., description="Store name")
    price: float = Field(..., ge=0, description="Price of the item at this store")


class StoreTotal(BaseModel):
    """Schema for store total calculation"""

    store: str = Field(..., description="Store name")
    total: float = Field(..., ge=0, description="Total price for all items at this store")


class CompareResponse(BaseModel):
    """Response schema for comparison - Single source of truth for output format (DoD)"""

    items: List[CompareItem] = Field(..., description="List of compared items with prices")
    storeTotals: List[StoreTotal] = Field(..., description="Total price per store")
    overallTotal: float = Field(..., ge=0, description="Overall total across all stores")
    unmatched: List[str] = Field(
        default_factory=list, description="List of items that couldn't be matched"
    )


# Legacy comparison schemas (kept for backward compatibility if needed)
class ProductComparison(BaseModel):
    """Schema for product comparison result"""

    product_id: int
    product_name: str
    store_id: int
    store_name: str
    store_city: Optional[str] = None
    price: float


class ComparisonResult(BaseModel):
    """Schema for comparison result"""

    query: str
    normalized_query: str
    results: List[ProductComparison]
    cheapest: Optional[ProductComparison] = None
    most_expensive: Optional[ProductComparison] = None


# Shopping list schemas
class ShoppingListItemCreate(BaseModel):
    """Schema for creating a shopping list item"""
    category: str
    brand: Optional[str] = None
    variants: List[str] = Field(default_factory=list)
    quantity: float
    unit: str


class ShoppingListCreateRequest(BaseModel):
    """Schema for creating a shopping list with items"""
    name: str
    items: List[ShoppingListItemCreate]


class ShoppingListItemResponse(BaseModel):
    """Schema for shopping list item response"""
    id: int
    category: str
    brand: Optional[str]
    variants: List[str]
    quantity: float
    unit: str
    best_store: Optional[str]
    best_price: Optional[float]
    best_url: Optional[str]
    comparison: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)


class ShoppingListResponse(BaseModel):
    """Schema for shopping list response"""
    id: int
    name: str
    created_at: datetime
    last_refreshed: datetime
    items: List[ShoppingListItemResponse]
    model_config = ConfigDict(from_attributes=True)


# Catalog schemas
class CategorySummary(BaseModel):
    """Lightweight category representation"""
    code: str
    label: str


class CategoryDetail(BaseModel):
    """Detailed category representation"""
    code: str
    label: str
    units: List[str]
    variants: List[str]
    brands: List[str]
