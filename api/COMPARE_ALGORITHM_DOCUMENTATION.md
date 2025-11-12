# Compare Algorithm Documentation

## Overview

Core algorithm for the `/compare` endpoint: **For each requested item, choose the cheapest price across the selected stores.**

## Algorithm Steps (MVP, Deterministic)

### Step 1: Normalize items and stores. Reject if empty → 422

- Normalize item names using `normalize_item_name()` (lowercase, trim, collapse whitespace, apply synonyms)
- Normalize store names (lowercase, trim)
- If items list is empty → return 422
- If stores list is empty → return 422

### Step 2: Resolve product IDs by exact name match

- For each normalized item name, find matching product by exact normalized name match
- Normalize product names in database using the same normalization (includes synonyms)
- Match normalized item name to normalized product name
- If product not found → add to `unmatched` list, continue to next item
- Build `item_to_product` mapping: `item_name -> Product`

### Step 3: Query all prices in one query

- Query all prices for `product_id IN (...) AND store_id IN (...)` in **one SQL query**
- Map to `prices_map[(product_id, store_id)] = price` (as Decimal)
- If multiple prices exist for same product-store combination, take the **minimum price**
- Performance: One round-trip SQL query (avoids N+1 queries)

### Step 4: For each requested item: pick min price with tie-breaker

For each item in order:
1. Find all candidate stores with a price for this product
2. Pick the store with **minimum price**
3. **Tie-breaker**: If two stores have the same price, pick the one with **lower current basket subtotal**
   - Maintain running `store_totals` during selection
   - This reduces store-hopping by favoring stores where we're already shopping
4. Add selected item to `compare_items` list
5. Update running `store_totals` for the selected store

### Step 5: Build response arrays

- `items[]`: List of CompareItem (one per requested item with cheapest price)
- `storeTotals[]`: Total price per store for all selected items
- `overallTotal`: Minimum total across all stores (best deal)
- `unmatched[]`: Items that couldn't be found or had no prices

## Key Features

### Deterministic Selection

- Items are processed in order
- Tie-breaking is deterministic (lower basket subtotal, then lower store_id)
- Same input always produces same output

### Performance Optimizations

- **One SQL query** for all prices (no N+1 queries)
- Convert to dictionaries in memory for O(1) lookups
- Single round-trip to database for price data

### Monetary Precision

- Prices stored as **DECIMAL** in database (Numeric(10, 2))
- Cast to **float** only at response time
- Maintains precision during calculations

### Tie-Breaking Logic

When two stores have the same price for an item:
1. Pick the store with **lower current basket subtotal** (reduces store-hopping)
2. If basket subtotals are equal, pick store with **lower store_id** (deterministic)

## Example

### Request
```json
{
    "items": ["milk", "bread", "eggs"],
    "stores": ["Walmart", "Target", "Kroger"]
}
```

### Processing

1. **Normalize items**: ["milk", "bread", "eggs"]
2. **Resolve products**: 
   - "milk" → Product(id=1, name="Milk")
   - "bread" → Product(id=2, name="Bread")
   - "eggs" → Product(id=3, name="Eggs")
3. **Query prices**: One query for all (product_id, store_id) combinations
4. **Select cheapest**:
   - "milk": Walmart ($2.99) < Target ($3.29) < Kroger ($3.49) → Select Walmart
   - "bread": Target ($1.99) < Walmart ($2.49) = Kroger ($2.49) → Select Target
   - "eggs": Walmart ($2.99) = Target ($2.99), but Walmart basket=$2.99 < Target basket=$1.99 → Select Target (lower basket)

### Response
```json
{
    "items": [
        {"name": "milk", "store": "Walmart", "price": 2.99},
        {"name": "bread", "store": "Target", "price": 1.99},
        {"name": "eggs", "store": "Target", "price": 2.99}
    ],
    "storeTotals": [
        {"store": "Walmart", "total": 2.99},
        {"store": "Target", "total": 4.98},
        {"store": "Kroger", "total": 0.00}
    ],
    "overallTotal": 2.99,
    "unmatched": []
}
```

## Error Handling

- **422 Unprocessable Entity**: Empty items or stores list
- **404 Not Found**: Not used (list endpoints return empty arrays)
- Items without matching products → added to `unmatched[]`
- Items without prices → added to `unmatched[]`

## Performance Characteristics

- **Time Complexity**: O(n * m) where n = items, m = stores
- **Space Complexity**: O(n * m) for prices_map
- **Database Queries**: 
  - 1 query for all products (MVP scale)
  - 1 query for all stores (MVP scale)
  - 1 query for all prices (optimized)
- **Total**: 3 queries regardless of input size

## Future Enhancements

- Cache normalized product names
- Use database indexes for faster lookups
- Implement fuzzy matching for similar product names
- Add support for product variants (e.g., "milk 2L" vs "milk 1L")

