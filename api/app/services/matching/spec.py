from dataclasses import dataclass
from typing import List, Optional, Any, Dict

from app.services.catalog_service import CATEGORIES


@dataclass
class ProductSpec:
    category_code: str
    category_label: str
    brand: Optional[str]
    variants: List[str]
    quantity: float
    unit: str


def from_shopping_item(item: Any) -> "ProductSpec":
    """
    Build a ProductSpec from a ShoppingListItem ORM instance.
    Uses catalog to resolve category label if available.
    """
    cat = CATEGORIES.get(item.category, {})
    category_label = cat.get("label", item.category)
    variants = item.variants or []
    return ProductSpec(
        category_code=item.category,
        category_label=category_label,
        brand=item.brand,
        variants=variants,
        quantity=float(item.quantity),
        unit=item.unit,
    )
