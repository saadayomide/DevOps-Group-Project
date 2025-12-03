from typing import Dict, List, Set
from .normalize import normalize

# Basic Spanish stopwords to ignore as noise
STOPWORDS: Set[str] = {"de", "con", "y", "en", "para", "el", "la", "los", "las", "del", "al"}

# Category-specific rules to enforce hard filters
CATEGORY_RULES: Dict[str, Dict[str, List[str]]] = {
    "milk": {
        "base_terms": ["leche"],
        "forbidden_terms": [
            "chocolate",
            "cacao",
            "batido",
            "cappuccino",
            "espresso",
            "fruta",
            "tropical",
            "mediterraneo",
            "caribe",
            "cereales",
            "galletas",
            "rellenos",
            "facial",
            "corporal",
            "limpiadora",
            "polvo",
            "lactantes",
            "continuacion",
            "infantil",
        ],
    },
    "eggs": {
        "base_terms": ["huevo", "huevos"],
        "forbidden_terms": ["chocolate", "pascua", "mona", "caramelo", "bombon"],
    },
    "bread": {
        "base_terms": ["pan"],
        "forbidden_terms": ["galletas", "bolleria", "bizcocho", "magdalenas"],
    },
}


def get_category_rules(category_code: str) -> Dict[str, List[str]]:
    return CATEGORY_RULES.get(category_code, {"base_terms": [], "forbidden_terms": []})
