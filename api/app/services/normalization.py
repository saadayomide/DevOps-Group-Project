"""
Product name normalization service

Phase 1 enhancements:
- Load deterministic category rules from YAML (`category_rules.yml`).
- Provide robust string normalization (accents removal, punctuation stripping).
- Provide `ProductSpec` builder that returns tokens, brand, variants, and matched rule hints.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

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


def _load_category_rules() -> Dict[str, Dict[str, List[str]]]:
    """Load category rules from YAML file next to this module.

    Returns a dict keyed by category with keys: base_terms, optional_terms, forbidden_terms
    """
    rules_path = Path(__file__).parent / "category_rules.yml"
    if not rules_path.exists() or yaml is None:
        return {}
    try:
        with open(rules_path, "r", encoding="utf-8") as fh:
            rules = yaml.safe_load(fh) or {}
            # Normalize lists to lower-case tokens
            normalized = {}
            for cat, data in rules.items():
                normalized[cat] = {
                    "base_terms": [t.lower() for t in (data.get("base_terms") or [])],
                    "optional_terms": [t.lower() for t in (data.get("optional_terms") or [])],
                    "forbidden_terms": [t.lower() for t in (data.get("forbidden_terms") or [])],
                }
            return normalized
    except Exception:
        return {}


CATEGORY_RULES = _load_category_rules()


def remove_accents(s: str) -> str:
    if not s:
        return ""
    nkfd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nkfd if not unicodedata.combining(c)])


def normalize_string(s: str) -> str:
    """Deterministic normalization: lowercase, remove accents, collapse whitespace."""
    if not s:
        return ""
    s = s.strip().lower()
    s = remove_accents(s)
    # replace punctuation with space (keep alnum and %)
    s = re.sub(r"[^a-z0-9%\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_item_name(s: str) -> str:
    """Backward-compatible wrapper that also applies synonyms map."""
    base = normalize_string(s)
    if not base:
        return ""
    # map synonyms using original function mapping
    if base in SYNONYMS_MAP:
        return SYNONYMS_MAP[base]
    return base


def normalize_product_name(name: str) -> str:
    """Keep older API but use normalize_string and expand abbreviations."""
    if not name:
        return ""
    normalized = normalize_string(name)
    abbreviations = {
        " oz ": " ounce ",
        " lb ": " pound ",
        " kg ": " kilogram ",
        " g ": " gram ",
        " ml ": " milliliter ",
        " l ": " liter ",
        " pk ": " pack ",
        " ct ": " count ",
        " pcs ": " pieces ",
    }
    # pad and replace to avoid matching inside words
    padded = f" {normalized} "
    for k, v in abbreviations.items():
        padded = padded.replace(k, v)
    return padded.strip()


def tokenize_product_name(name: str) -> List[str]:
    normalized = normalize_product_name(name)
    if not normalized:
        return []
    return normalized.split()


def calculate_similarity(name1: str, name2: str) -> float:
    tokens1 = set(tokenize_product_name(name1))
    tokens2 = set(tokenize_product_name(name2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    if not union:
        return 0.0
    return len(intersection) / len(union)


@dataclass
class ProductSpec:
    name: str
    tokens: List[str] = field(default_factory=list)
    brand: Optional[str] = None
    category: Optional[str] = None
    variants: List[str] = field(default_factory=list)
    matched_rules: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)


def _match_category_by_rules(tokens: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """Return categories that match base_terms and any matched optional/forbidden tokens."""
    # Returns: category -> {matched_base, matched_optional, matched_forbidden}
    matches = {}
    token_set = set(tokens)
    for cat, data in CATEGORY_RULES.items():
        base_hits = [t for t in data.get("base_terms", []) if t in token_set]
        if not base_hits:
            continue
        opt_hits = [t for t in data.get("optional_terms", []) if t in token_set]
        forb_hits = [t for t in data.get("forbidden_terms", []) if t in token_set]
        matches[cat] = {
            "matched_base": base_hits,
            "matched_optional": opt_hits,
            "matched_forbidden": forb_hits,
        }
    return matches


def build_product_spec(
    name: str,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    variants: Optional[List[str]] = None,
) -> ProductSpec:
    """Construct a ProductSpec from input attributes and rule hints."""
    name_norm = normalize_string(name or "")
    tokens = name_norm.split() if name_norm else []
    if variants:
        # normalize variants too
        for v in variants:
            vt = normalize_string(v)
            if vt:
                tokens.extend(vt.split())
    # dedupe while preserving order
    seen = set()
    dedup_tokens = []
    for t in tokens:
        if t not in seen:
            dedup_tokens.append(t)
            seen.add(t)

    matched_rules = _match_category_by_rules(dedup_tokens)
    spec = ProductSpec(
        name=name,
        tokens=dedup_tokens,
        brand=normalize_string(brand) if brand else None,
        category=category,
        variants=[normalize_string(v) for v in (variants or [])],
        matched_rules=matched_rules,
    )
    return spec


def summarize_spec(spec: ProductSpec) -> Dict:
    return {
        "name": spec.name,
        "tokens": spec.tokens,
        "brand": spec.brand,
        "category": spec.category,
        "variants": spec.variants,
        "matched_rules": spec.matched_rules,
    }


__all__ = [
    "normalize_item_name",
    "normalize_product_name",
    "tokenize_product_name",
    "calculate_similarity",
    "SYNONYMS_MAP",
    "ProductSpec",
    "build_product_spec",
    "normalize_string",
    "CATEGORY_RULES",
]
