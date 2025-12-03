"""
Product name normalization service
"""

import re
from typing import List, Dict


# Lightweight synonyms map - kept in memory for MVP
# Maps alternative names to canonical names (bidirectional)
SYNONYMS_MAP: Dict[str, str] = {
    # Bell pepper / Capsicum
    "bell pepper": "bell pepper",
    "capsicum": "bell pepper",
    "sweet pepper": "bell pepper",
    # Eggplant / Aubergine
    "eggplant": "eggplant",
    "aubergine": "eggplant",
    # Zucchini / Courgette
    "zucchini": "zucchini",
    "courgette": "zucchini",
    # Cilantro / Coriander
    "cilantro": "cilantro",
    "coriander": "cilantro",
    "fresh coriander": "cilantro",
    # Arugula / Rocket
    "arugula": "arugula",
    "rocket": "arugula",
    "rocket lettuce": "arugula",
    # Scallion / Green onion / Spring onion
    "scallion": "green onion",
    "green onion": "green onion",
    "spring onion": "green onion",
    # Ground beef / Minced beef
    "ground beef": "ground beef",
    "minced beef": "ground beef",
    # Ground turkey / Minced turkey
    "ground turkey": "ground turkey",
    "minced turkey": "ground turkey",
    # Ice cream / Icecream
    "ice cream": "ice cream",
    "icecream": "ice cream",
    # Hot dog / Hotdog / Frankfurter
    "hot dog": "hot dog",
    "hotdog": "hot dog",
    "frankfurter": "hot dog",
    # Ketchup / Tomato sauce
    "ketchup": "ketchup",
    "tomato sauce": "ketchup",
    "catsup": "ketchup",
}


def normalize_item_name(s: str) -> str:
    """
    Normalize item name: lowercase, trim, collapse whitespace.
    Optionally applies synonyms map to normalize to canonical form.

    Args:
        s: Item name to normalize

    Returns:
        Normalized item name
    """
    if not s:
        return ""

    # Trim whitespace
    normalized = s.strip()

    # Convert to lowercase
    normalized = normalized.lower()

    # Collapse whitespace (replace multiple spaces/tabs/newlines with single space)
    normalized = re.sub(r"\s+", " ", normalized)

    # Trim again after collapsing whitespace
    normalized = normalized.strip()

    # Apply synonyms map if available
    if normalized in SYNONYMS_MAP:
        normalized = SYNONYMS_MAP[normalized]

    return normalized


def normalize_product_name(name: str) -> str:
    """
    Normalize product name for better search matching
    - Convert to lowercase
    - Remove extra whitespace
    - Remove special characters (optional, depending on requirements)
    - Handle common abbreviations
    """
    if not name:
        return ""

    # Convert to lowercase
    normalized = name.lower()

    # Remove extra whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Remove special characters (keep alphanumeric and spaces)
    # normalized = re.sub(r'[^a-z0-9\s]', '', normalized)

    # Normalize common abbreviations
    abbreviations = {
        "oz": "ounce",
        "lb": "pound",
        "kg": "kilogram",
        "g": "gram",
        "ml": "milliliter",
        "l": "liter",
        "pk": "pack",
        "ct": "count",
        "pcs": "pieces",
    }

    for abbrev, full in abbreviations.items():
        # Replace abbreviations with full words
        normalized = re.sub(rf"\b{abbrev}\b", full, normalized)

    return normalized


def tokenize_product_name(name: str) -> List[str]:
    """
    Tokenize product name into individual words
    """
    normalized = normalize_product_name(name)
    return normalized.split()


def calculate_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two product names (simple version)
    Returns a value between 0 and 1
    """
    tokens1 = set(tokenize_product_name(name1))
    tokens2 = set(tokenize_product_name(name2))

    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)

    if not union:
        return 0.0

    return len(intersection) / len(union)
