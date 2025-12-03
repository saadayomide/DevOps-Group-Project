"""
Static catalog service for product categories.
"""
from typing import Dict, List, Optional

CATEGORIES: Dict[str, Dict[str, object]] = {
    "milk": {
        "label": "Leche",
        "units": ["unit", "L"],
        "variants": ["entera", "semidesnatada", "desnatada", "sin lactosa"],
        "brands": ["Hacendado", "Carrefour", "Alcampo", "Ahorramás", "El Corte Inglés", "Mercadona"],
    },
    "eggs": {
        "label": "Huevos",
        "units": ["unit", "dozen"],
        "variants": ["M", "L", "XL", "camperos", "eco"],
        "brands": [],
    },
    "bread": {
        "label": "Pan",
        "units": ["unit", "kg"],
        "variants": ["blanco", "integral", "centeno"],
        "brands": ["Bimbo", "Panrico"],
    },
}


def list_categories() -> List[Dict]:
    """Return a list of dicts with 'code' and 'label' for all categories."""
    return [{"code": code, "label": data.get("label", code)} for code, data in CATEGORIES.items()]


def get_category(code: str) -> Optional[Dict]:
    """Return the dict for a category code, or None if it does not exist."""
    return CATEGORIES.get(code)
