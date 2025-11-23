from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    items: List[str] = Field(..., description="List of product names to compare")
    stores: Optional[List[str]] = Field(None, description="Optional list of store names to restrict comparison")


class Recommendation(BaseModel):
    product: str
    cheapest_store: str
    price: float
    all_prices: Dict[str, float]


class CompareResponse(BaseModel):
    recommendations: List[Recommendation]
    total_cost: float
    savings: float = 0.0
    store_totals: Dict[str, float] = {}