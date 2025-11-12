# Normalization Helpers Documentation

## Overview

The normalization service provides functions to normalize item names for consistent matching and searching. It includes basic normalization (lowercase, trim, collapse whitespace) and a lightweight synonyms map for MVP.

## Functions

### `normalize_item_name(s: str) -> str`

Normalizes item names by:
1. **Trimming whitespace** - Removes leading and trailing whitespace
2. **Converting to lowercase** - Case-insensitive matching
3. **Collapsing whitespace** - Replaces multiple spaces/tabs/newlines with single space
4. **Applying synonyms map** - Normalizes alternative names to canonical form

**Parameters:**
- `s` (str): Item name to normalize

**Returns:**
- `str`: Normalized item name

**Examples:**
```python
normalize_item_name("  Bell   Pepper  ")  # Returns: "bell pepper"
normalize_item_name("Capsicum")           # Returns: "bell pepper" (synonym)
normalize_item_name("Hot\t\tDog")         # Returns: "hot dog"
normalize_item_name("Ice\n\nCream")       # Returns: "ice cream"
```

## Synonyms Map

The synonyms map (`SYNONYMS_MAP`) is a lightweight in-memory dictionary that maps alternative names to canonical names. It's kept in memory for MVP.

### Current Synonyms

| Alternative Name | Canonical Name |
|-----------------|----------------|
| capsicum | bell pepper |
| sweet pepper | bell pepper |
| aubergine | eggplant |
| courgette | zucchini |
| coriander | cilantro |
| fresh coriander | cilantro |
| rocket | arugula |
| rocket lettuce | arugula |
| scallion | green onion |
| spring onion | green onion |
| minced beef | ground beef |
| minced turkey | ground turkey |
| icecream | ice cream |
| hotdog | hot dog |
| frankfurter | hot dog |
| tomato sauce | ketchup |
| catsup | ketchup |

### Adding Synonyms

To add new synonyms, update the `SYNONYMS_MAP` dictionary in `api/app/services/normalization.py`:

```python
SYNONYMS_MAP: Dict[str, str] = {
    # Existing synonyms...
    "new_synonym": "canonical_name",
    "another_name": "canonical_name",
}
```

## Usage

### In Compare Endpoint

The `normalize_item_name` function is used in the compare endpoint to normalize item names before searching for products:

```python
from app.services.normalization import normalize_item_name

# Normalize item name before searching
normalized_item = normalize_item_name(item)
product = db.query(Product).filter(
    Product.name.ilike(f"%{normalized_item}%")
).first()
```

### Benefits

1. **Consistent Matching**: Normalizes variations in item names for better matching
2. **Synonym Support**: Handles regional differences (e.g., "capsicum" vs "bell pepper")
3. **Whitespace Handling**: Handles extra whitespace, tabs, and newlines
4. **Case Insensitive**: Converts to lowercase for case-insensitive matching

## Implementation Details

### Memory Storage

- Synonyms map is stored in memory as a dictionary
- No database or external file required for MVP
- Fast lookup O(1) for synonym mapping

### Normalization Steps

1. **Trim**: `s.strip()` - Remove leading/trailing whitespace
2. **Lowercase**: `s.lower()` - Convert to lowercase
3. **Collapse Whitespace**: `re.sub(r'\s+', ' ', s)` - Replace multiple whitespace with single space
4. **Trim Again**: `s.strip()` - Remove any remaining whitespace after collapsing
5. **Apply Synonyms**: Look up in `SYNONYMS_MAP` and replace if found

### Performance

- Fast and lightweight
- No external dependencies
- O(1) synonym lookup
- Efficient regex for whitespace collapsing

## Testing

Unit tests are available in `api/tests/unit/test_normalization.py`:

- `test_normalize_item_name_basic()` - Basic normalization tests
- `test_normalize_item_name_whitespace_collapse()` - Whitespace handling
- `test_normalize_item_name_synonyms()` - Synonym mapping
- `test_normalize_item_name_with_whitespace_and_synonyms()` - Combined tests

## Future Enhancements

For production, consider:
- Loading synonyms from database or configuration file
- Adding more synonyms based on user feedback
- Implementing fuzzy matching for similar items
- Adding support for product variants (e.g., "milk 2L" vs "milk 1L")

