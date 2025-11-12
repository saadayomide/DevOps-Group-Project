# Request/Response Schemas Documentation

## Overview

The comparison schemas (`CompareRequest`, `CompareItem`, `CompareResponse`) are the **single source of truth** for the output format (Definition of Done - DoD).

## Schemas

### CompareRequest

Request schema for comparing items across stores.

```python
{
    "items": List[str],      # List of product names to compare
    "stores": List[str]      # List of store names to compare across
}
```

**Example:**
```json
{
    "items": ["milk", "bread", "eggs"],
    "stores": ["Walmart", "Target", "Kroger"]
}
```

### CompareItem

Schema for a single compared item with price information.

```python
{
    "name": str,     # Product name
    "store": str,    # Store name
    "price": float   # Price of the item at this store (>= 0)
}
```

**Example:**
```json
{
    "name": "milk",
    "store": "Walmart",
    "price": 3.99
}
```

### StoreTotal

Schema for store total calculation.

```python
{
    "store": str,    # Store name
    "total": float   # Total price for all items at this store (>= 0)
}
```

**Example:**
```json
{
    "store": "Walmart",
    "total": 15.97
}
```

### CompareResponse

Response schema for comparison - **Single source of truth for output format (DoD)**.

```python
{
    "items": List[CompareItem],           # List of compared items with prices
    "storeTotals": List[StoreTotal],      # Total price per store
    "overallTotal": float,                # Minimum total (best deal across stores)
    "unmatched": List[str]                # List of items that couldn't be matched
}
```

**Example:**
```json
{
    "items": [
        {"name": "milk", "store": "Walmart", "price": 3.99},
        {"name": "bread", "store": "Walmart", "price": 2.49},
        {"name": "milk", "store": "Target", "price": 4.29},
        {"name": "bread", "store": "Target", "price": 2.99}
    ],
    "storeTotals": [
        {"store": "Walmart", "total": 6.48},
        {"store": "Target", "total": 7.28}
    ],
    "overallTotal": 6.48,
    "unmatched": ["eggs"]
}
```

## API Endpoint

### POST /api/v1/compare/

Compare items across stores.

**Request Body:**
```json
{
    "items": ["milk", "bread", "eggs"],
    "stores": ["Walmart", "Target", "Kroger"]
}
```

**Response:**
- `items`: All items found at each store with their prices
- `storeTotals`: Total price per store for all matched items
- `overallTotal`: Minimum total across stores (best deal)
- `unmatched`: Items that couldn't be found at any store

## Implementation Details

1. **Item Matching**: Uses normalized product names for case-insensitive matching
2. **Store Matching**: Case-insensitive store name matching
3. **Price Lookup**: Finds prices for product-store combinations
4. **Total Calculation**: Calculates totals per store and finds minimum (best deal)
5. **Unmatched Items**: Tracks items that couldn't be found at any store

## Schema Location

All schemas are defined in `api/app/schemas.py`:
- `CompareRequest`
- `CompareItem`
- `StoreTotal`
- `CompareResponse`

These schemas are used by:
- `api/app/routes/compare.py` - Compare endpoint
- `api/app/services/compare_service.py` - Comparison service logic

