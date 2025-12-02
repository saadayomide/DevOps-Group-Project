# API Contract Documentation

This document defines the exact API contract between the frontend and backend, verified from the backend implementation.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Staging**: `https://shopsmart-backend-staging.azurewebsites.net` (verify with Team C)
- **Production**: TBD

All endpoints are prefixed with `/api/v1`.

## Endpoints

### 1. GET /api/v1/supermarkets/

Get all available supermarkets.

**Request:**
- Method: `GET`
- Headers: None required
- Query params: None

**Response:**
- Status: `200 OK`
- Body: `Array<SupermarketResponse>`
  ```json
  [
    {
      "id": 1,
      "name": "Mercadona"
    },
    {
      "id": 2,
      "name": "Carrefour"
    }
  ]
  ```

**Error Responses:**
- `404 Not Found`: Path resource missing (unlikely for this endpoint)
- `422 UnprocessableEntity`: Invalid query parameter types
- `500 InternalServerError`: Server error

**Error Format:**
```json
{
  "error": "ErrorType",
  "message": "Error description"
}
```

---

### 2. GET /api/v1/products/

Get all available products with optional filtering.

**Request:**
- Method: `GET`
- Headers: None required
- Query params:
  - `q` (optional, string): Search query to filter products by name (case-insensitive)
  - `limit` (optional, number): Maximum number of products to return (1-1000, default: 100)
  - `offset` (optional, number): Number of products to skip (>= 0, default: 0)

**Response:**
- Status: `200 OK`
- Body: `Array<ProductResponse>`
  ```json
  [
    {
      "id": 1,
      "name": "milk"
    },
    {
      "id": 2,
      "name": "bread"
    }
  ]
  ```

**Error Responses:**
- `422 UnprocessableEntity`: Invalid query parameter types (e.g., limit not a number, limit < 1 or > 1000, offset < 0)
- `500 InternalServerError`: Server error

**Error Format:**
```json
{
  "error": "UnprocessableEntity",
  "message": "limit: ensure this value is greater than or equal to 1"
}
```

---

### 3. POST /api/v1/compare/

Compare items across selected stores.

**Request:**
- Method: `POST`
- Headers: `Content-Type: application/json`
- Body: `CompareRequest`
  ```json
  {
    "items": ["milk", "bread", "eggs"],
    "stores": ["Mercadona", "Carrefour", "Lidl"]
  }
  ```

**Request Schema:**
- `items`: `Array<string>` (required, non-empty) - List of product names to compare
- `stores`: `Array<string>` (required, non-empty) - List of store names to compare across

**Response:**
- Status: `200 OK`
- Body: `CompareResponse`
  ```json
  {
    "items": [
      {
        "name": "milk",
        "store": "Lidl",
        "price": 1.15
      },
      {
        "name": "bread",
        "store": "Mercadona",
        "price": 0.85
      },
      {
        "name": "eggs",
        "store": "Lidl",
        "price": 2.50
      }
    ],
    "storeTotals": [
      {
        "store": "Lidl",
        "total": 3.65
      },
      {
        "store": "Mercadona",
        "total": 0.85
      }
    ],
    "overallTotal": 4.50,
    "unmatched": []
  }
  ```

**Response Schema:**
- `items`: `Array<CompareItem>` - List of compared items with prices
  - `name`: `string` - Product name
  - `store`: `string` - Store name where this item is cheapest
  - `price`: `number` (>= 0) - Price of the item at this store
- `storeTotals`: `Array<StoreTotal>` - Total price per store
  - `store`: `string` - Store name
  - `total`: `number` (>= 0) - Total price for all items at this store
- `overallTotal`: `number` (>= 0) - Overall total across all stores
- `unmatched`: `Array<string>` - List of items that couldn't be matched (product names)

**Error Responses:**
- `400 BadRequest`: Empty items or stores array
  ```json
  {
    "error": "BadRequest",
    "message": "items cannot be empty"
  }
  ```
- `422 UnprocessableEntity`: Invalid request body structure or types
  ```json
  {
    "error": "UnprocessableEntity",
    "message": "items: field required"
  }
  ```
- `500 InternalServerError`: Server error

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "ErrorType",
  "message": "Error description"
}
```

### Error Types

- `BadRequest` (400): Invalid request (e.g., empty arrays)
- `NotFound` (404): Resource not found
- `UnprocessableEntity` (422): Validation errors (wrong types, missing fields, invalid values)
- `InternalServerError` (500): Server error

### Error Message Format

- For validation errors (422): `"field_name: error message"` or `"field_name: field required"`
- For business logic errors (400): Plain error message
- For server errors (500): Error detail (only in debug mode)

---

## Data Types

### Field Naming Convention

All fields use **lowercase** with **camelCase** for multi-word fields:
- ✅ `storeTotals` (camelCase)
- ✅ `overallTotal` (camelCase)
- ✅ `product_id` (snake_case in database, but camelCase in API responses)
- ❌ `store_totals` (not used in API)
- ❌ `overall_total` (not used in API)

### Number Types

- `id`: `integer` (positive)
- `price`: `number` (float, >= 0)
- `total`: `number` (float, >= 0)
- `limit`: `integer` (1-1000)
- `offset`: `integer` (>= 0)

### String Types

- `name`: `string` (product/supermarket name)
- `store`: `string` (store name)
- `q`: `string` (search query)

### Array Types

- `items`: `Array<string>` (non-empty)
- `stores`: `Array<string>` (non-empty)
- `unmatched`: `Array<string>` (can be empty)

---

## Validation Rules

### Compare Request

1. `items` must be:
   - Present (required)
   - An array
   - Non-empty
   - Array of strings

2. `stores` must be:
   - Present (required)
   - An array
   - Non-empty
   - Array of strings

### Products Query Parameters

1. `limit` must be:
   - An integer (if provided)
   - Between 1 and 1000 (inclusive)
   - Returns 422 if invalid

2. `offset` must be:
   - An integer (if provided)
   - >= 0
   - Returns 422 if invalid

3. `q` (search query):
   - Optional
   - String type
   - Case-insensitive matching

---

## Notes

1. **API Prefix**: All endpoints use `/api/v1` prefix (configured in backend `config.py`)

2. **CORS**: Backend allows all origins (`*`) in development. Team C will tighten this for production.

3. **OpenAPI Docs**: Backend provides automatic OpenAPI documentation at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
   - OpenAPI JSON: `http://localhost:8000/openapi.json`

4. **Health Check**: Backend provides health endpoint at `/health` (not part of API contract, but useful for monitoring)

5. **Response Consistency**:
   - GET `/supermarkets/` and GET `/products/` return simplified responses with only `id` and `name`
   - Full details available via GET `/supermarkets/{id}` and GET `/products/{id}`

---

## Verification Checklist

- [x] Verified `/api/v1/supermarkets/` response structure
- [x] Verified `/api/v1/products/` response structure and query params
- [x] Verified `/api/v1/compare/` request/response structure
- [x] Verified error response format (422, 400, 404, 500)
- [x] Verified field naming (camelCase for multi-word fields)
- [x] Verified data types (numbers, strings, arrays)
- [x] Verified required fields
- [x] Verified validation rules

---

## Next Steps

1. **Get Staging URL**: Contact Team C for the live backend staging URL
2. **Test Integration**: Use the API layer to make test requests to staging
3. **Update Environment**: Update `.env` file with staging URL when available
4. **Monitor**: Watch for any API contract changes from backend team
