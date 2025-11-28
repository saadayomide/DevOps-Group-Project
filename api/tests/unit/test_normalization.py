"""
Unit tests for normalization service
"""

from app.services.normalization import (
    normalize_item_name,
    normalize_product_name,
    tokenize_product_name,
    calculate_similarity,
    SYNONYMS_MAP,
)


def test_normalize_item_name_basic():
    """Test basic item name normalization: lowercase, trim, collapse whitespace"""
    assert normalize_item_name("Milk") == "milk"
    assert normalize_item_name("  Bread   ") == "bread"
    assert normalize_item_name("  Fresh   Milk  ") == "fresh milk"
    assert normalize_item_name("Hot\tDog\n\n") == "hot dog"
    assert normalize_item_name("") == ""
    assert normalize_item_name("   ") == ""


def test_normalize_item_name_whitespace_collapse():
    """Test whitespace collapsing"""
    assert normalize_item_name("Bell    Pepper") == "bell pepper"
    assert normalize_item_name("Ice\n\nCream") == "ice cream"
    assert normalize_item_name("Hot\t\tDog") == "hot dog"


def test_normalize_item_name_synonyms():
    """Test synonyms map application"""
    # Bell pepper / Capsicum
    assert normalize_item_name("capsicum") == "bell pepper"
    assert normalize_item_name("sweet pepper") == "bell pepper"
    assert normalize_item_name("bell pepper") == "bell pepper"

    # Eggplant / Aubergine
    assert normalize_item_name("aubergine") == "eggplant"
    assert normalize_item_name("eggplant") == "eggplant"

    # Zucchini / Courgette
    assert normalize_item_name("courgette") == "zucchini"
    assert normalize_item_name("zucchini") == "zucchini"

    # Cilantro / Coriander
    assert normalize_item_name("coriander") == "cilantro"
    assert normalize_item_name("fresh coriander") == "cilantro"
    assert normalize_item_name("cilantro") == "cilantro"

    # Arugula / Rocket
    assert normalize_item_name("rocket") == "arugula"
    assert normalize_item_name("rocket lettuce") == "arugula"
    assert normalize_item_name("arugula") == "arugula"

    # Scallion / Green onion
    assert normalize_item_name("scallion") == "green onion"
    assert normalize_item_name("spring onion") == "green onion"
    assert normalize_item_name("green onion") == "green onion"

    # Ground beef / Minced beef
    assert normalize_item_name("minced beef") == "ground beef"
    assert normalize_item_name("ground beef") == "ground beef"

    # Ice cream
    assert normalize_item_name("icecream") == "ice cream"
    assert normalize_item_name("ice cream") == "ice cream"

    # Hot dog
    assert normalize_item_name("hotdog") == "hot dog"
    assert normalize_item_name("frankfurter") == "hot dog"
    assert normalize_item_name("hot dog") == "hot dog"

    # Ketchup
    assert normalize_item_name("tomato sauce") == "ketchup"
    assert normalize_item_name("catsup") == "ketchup"
    assert normalize_item_name("ketchup") == "ketchup"


def test_normalize_item_name_with_whitespace_and_synonyms():
    """Test normalization with whitespace and synonyms"""
    assert normalize_item_name("  Capsicum  ") == "bell pepper"
    assert normalize_item_name("  Ice   Cream  ") == "ice cream"
    assert normalize_item_name("Hot\t\tDog") == "hot dog"
    assert normalize_item_name("  Minced   Beef  ") == "ground beef"


def test_normalize_product_name():
    """Test product name normalization"""
    assert normalize_product_name("Milk 2L") == "milk 2l"
    assert normalize_product_name("  Bread   White  ") == "bread white"
    assert normalize_product_name("") == ""


def test_tokenize_product_name():
    """Test product name tokenization"""
    tokens = tokenize_product_name("Fresh Milk 2L")
    assert tokens == ["fresh", "milk", "2l"]


def test_calculate_similarity():
    """Test similarity calculation"""
    similarity = calculate_similarity("milk", "milk 2l")
    assert 0 < similarity <= 1

    similarity_exact = calculate_similarity("milk", "milk")
    assert similarity_exact == 1.0

    similarity_different = calculate_similarity("milk", "bread")
    assert similarity_different == 0.0


def test_synonyms_map_coverage():
    """Test that synonyms map has expected entries"""
    assert "capsicum" in SYNONYMS_MAP
    assert "bell pepper" in SYNONYMS_MAP
    assert "aubergine" in SYNONYMS_MAP
    assert "eggplant" in SYNONYMS_MAP
    assert "courgette" in SYNONYMS_MAP
    assert "zucchini" in SYNONYMS_MAP
    assert len(SYNONYMS_MAP) > 0
