# GET Endpoints Documentation

## Overview

Basic GET endpoints with small & consistent responses. These endpoints power the front-end and tests.

## Error Handling

- **422 Unprocessable Entity**: Returned automatically by FastAPI for invalid query parameter types
- **404 Not Found**: Returned only when path resource is missing (e.g., `/products/999` when product doesn't exist)

## Endpoints

### GET /api/v1/products

Get all products - returns only `id` and `name` (small & consistent response).

**Query Parameters:**
- `q` (optional, string): Search query to filter products by name
- `limit` (optional, int): Maximum number of products to return (1-1000, default: 100)
- `offset` (optional, int): Number of products to skip (>= 0, default: 0)

**Response:**
```json
[
  {"id": 1, "name": "Milk"},
  {"id": 2, "name": "Bread"},
  {"id": 3, "name": "Eggs"}
]
```

**Examples:**
- `GET /api/v1/products` - Get all products (default limit: 100)
- `GET /api/v1/products?q=milk` - Search for products containing "milk"
- `GET /api/v1/products?limit=10&offset=20` - Get 10 products starting from offset 20
- `GET /api/v1/products?q=bread&limit=5` - Search for "bread" and return 5 results

**Error Responses:**
- `422`: Invalid query parameter type (e.g., `limit=abc`, `offset=-1`)
- `404`: Not applicable (list endpoint always returns array, possibly empty)

### GET /api/v1/supermarkets

Get all supermarkets - returns only `id` and `name` (small & consistent response).

**Query Parameters:** None

**Response:**
```json
[
  {"id": 1, "name": "Walmart"},
  {"id": 2, "name": "Target"},
  {"id": 3, "name": "Kroger"}
]
```

**Examples:**
- `GET /api/v1/supermarkets` - Get all supermarkets

**Error Responses:**
- `404`: Not applicable (list endpoint always returns array, possibly empty)

### GET /api/v1/prices

Get prices - handy for debugging.

**Query Parameters:**
- `productId` (optional, int): Filter by product ID (>= 1)
- `storeId` (optional, int): Filter by store ID (>= 1)

**Response:**
```json
[
  {
    "id": 1,
    "product_id": 1,
    "store_id": 1,
    "price": 3.99
  },
  {
    "id": 2,
    "product_id": 1,
    "store_id": 2,
    "price": 4.29
  }
]
```

**Examples:**
- `GET /api/v1/prices` - Get all prices
- `GET /api/v1/prices?productId=1` - Get prices for product ID 1
- `GET /api/v1/prices?storeId=2` - Get prices for store ID 2
- `GET /api/v1/prices?productId=1&storeId=2` - Get price for product 1 at store 2

**Error Responses:**
- `422`: Invalid query parameter type (e.g., `productId=abc`, `storeId=0`)
- `404`: Not applicable (list endpoint always returns array, possibly empty)

## Response Schemas

### ProductResponse
```python
{
    "id": int,
    "name": str
}
```

### SupermarketResponse
```python
{
    "id": int,
    "name": str
}
```

### Price (Full Schema)
```python
{
    "id": int,
    "product_id": int,
    "store_id": int,
    "price": float
}
```

## Implementation Notes

1. **Small & Consistent Responses**: Products and supermarkets return only `id` and `name` to keep responses small and consistent
2. **Automatic Validation**: FastAPI automatically validates query parameters and returns 422 for invalid types
3. **404 Only for Missing Resources**: 404 is only returned when a specific resource (by ID) is not found, not for list endpoints
4. **Default Limits**: Products endpoint has a default limit of 100 to prevent large responses
5. **Case-Insensitive Search**: Product search (`q` parameter) is case-insensitive
6. **Query Parameter Validation**: 
   - `limit`: Must be between 1 and 1000
   - `offset`: Must be >= 0
   - `productId`: Must be >= 1
   - `storeId`: Must be >= 1

## Testing

These endpoints are designed to be:
- Fast and lightweight
- Easy to test
- Consistent in response format
- Suitable for front-end consumption

