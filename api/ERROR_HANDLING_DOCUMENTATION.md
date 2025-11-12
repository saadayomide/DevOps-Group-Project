# Error Handling & Logging Documentation

## Overview
This document describes the error handling and logging implementation for the FastAPI application.

## Components

### 1. Logging Middleware (`app/middleware.py`)

The `LoggingMiddleware` class logs all HTTP requests and responses with structured payloads.

#### Structured Log Payload
Each request/response is logged with the following structure:
```json
{
    "endpoint": "/api/v1/compare",
    "method": "POST",
    "status": 200,
    "duration_ms": 123.45,
    "error": "HTTP 400"  // Only present for error responses (status >= 400)
}
```

#### Log Levels
- **INFO**: Successful requests (status < 400)
- **WARNING**: Requests with errors (status >= 400)
- **ERROR**: Unhandled exceptions (status 500)

#### Features
- Logs endpoint, method, status code, and duration in milliseconds
- Adds `X-Process-Time` header to all responses
- Catches and logs unhandled exceptions before re-raising them to exception handlers

### 2. Exception Handlers (`app/main.py`)

FastAPI exception handlers provide structured JSON error responses for all error scenarios.

#### Error Response Format
All error responses follow this structure:
```json
{
    "error": "ErrorType",
    "message": "Error message description"
}
```

#### Exception Handler Types

##### 1. RequestValidationError Handler (422)
Handles Pydantic validation errors (invalid request body, query parameters, etc.)

Example:
```json
{
    "error": "UnprocessableEntity",
    "message": "body.items: field required"
}
```

##### 2. HTTPException Handler (400, 404, etc.)
Handles HTTP exceptions raised by route handlers

Example:
```json
{
    "error": "BadRequest",
    "message": "items cannot be empty"
}
```

##### 3. General Exception Handler (500)
Handles unexpected server errors

Example (production):
```json
{
    "error": "InternalServerError",
    "message": "Internal server error"
}
```

Example (debug mode):
```json
{
    "error": "InternalServerError",
    "message": "Detailed error message with stack trace"
}
```

#### Status Code to Error Type Mapping
- `400` → `BadRequest`
- `401` → `Unauthorized`
- `403` → `Forbidden`
- `404` → `NotFound`
- `422` → `UnprocessableEntity`
- `500` → `InternalServerError`
- `502` → `BadGateway`
- `503` → `ServiceUnavailable`

### 3. Compare Endpoint Logging (`app/routes/compare.py`)

The `/compare` endpoint emits structured logs with operation metrics.

#### Log Payload
```json
{
    "endpoint": "/compare",
    "method": "POST",
    "items_requested": 5,
    "items_matched": 4,
    "items_unmatched": 1,
    "stores_count": 3
}
```

#### Metrics
- **items_requested**: Total number of items in the request
- **items_matched**: Number of items successfully matched to products in the database
- **items_unmatched**: Number of items that couldn't be matched
- **stores_count**: Number of stores included in the comparison

These metrics are logged at INFO level and can be consumed by Application Insights (Team C) for monitoring and analytics.

## Error Scenarios

### 1. Empty Items/Stores (400 BadRequest)
**Endpoint**: `POST /api/v1/compare`

**Request**:
```json
{
    "items": [],
    "stores": ["Walmart"]
}
```

**Response** (400):
```json
{
    "error": "BadRequest",
    "message": "items cannot be empty"
}
```

### 2. Invalid Request Body (422 UnprocessableEntity)
**Endpoint**: `POST /api/v1/compare`

**Request**:
```json
{
    "items": "not an array",
    "stores": ["Walmart"]
}
```

**Response** (422):
```json
{
    "error": "UnprocessableEntity",
    "message": "body.items: value is not a valid list"
}
```

### 3. Resource Not Found (404 NotFound)
**Endpoint**: `GET /api/v1/products/999`

**Response** (404):
```json
{
    "error": "NotFound",
    "message": "Product with id 999 not found"
}
```

### 4. Invalid Query Parameter Type (422 UnprocessableEntity)
**Endpoint**: `GET /api/v1/products?limit=abc`

**Response** (422):
```json
{
    "error": "UnprocessableEntity",
    "message": "query.limit: value is not a valid integer"
}
```

### 5. Internal Server Error (500 InternalServerError)
**Endpoint**: Any

**Response** (500):
```json
{
    "error": "InternalServerError",
    "message": "Internal server error"  // In production
}
```

## Logging Configuration

### Log Format
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Log Level
- Default: `INFO`
- Can be configured via environment variables or logging configuration

### Structured Logging
All logs use Python's `logging` module with structured data passed via the `extra` parameter. This allows log aggregation tools (like Application Insights) to parse and query the structured fields.

## Integration with Application Insights

The structured logging format is compatible with Azure Application Insights and other log aggregation tools. The `extra` parameter in logger calls creates structured log entries that can be queried and analyzed.

### Example Queries (Application Insights)
```
// Find all compare operations with unmatched items
traces
| where message == "Compare operation completed"
| where customDimensions.items_unmatched > 0

// Find slow requests
traces
| where customDimensions.duration_ms > 1000

// Find error responses
traces
| where customDimensions.status >= 400
```

## Testing Error Handling

### Test Empty Items
```bash
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"items": [], "stores": ["Walmart"]}'
```

Expected: 400 BadRequest with `{"error": "BadRequest", "message": "items cannot be empty"}`

### Test Invalid Request Body
```bash
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"items": "not an array", "stores": ["Walmart"]}'
```

Expected: 422 UnprocessableEntity with validation error message

### Test Resource Not Found
```bash
curl http://localhost:8000/api/v1/products/999
```

Expected: 404 NotFound with `{"error": "NotFound", "message": "Product with id 999 not found"}`

## Best Practices

1. **Use Appropriate Status Codes**
   - `400 BadRequest`: Business logic validation errors (e.g., empty items)
   - `422 UnprocessableEntity`: Request validation errors (e.g., invalid types)
   - `404 NotFound`: Resource not found
   - `500 InternalServerError`: Unexpected server errors

2. **Provide Clear Error Messages**
   - Use descriptive error messages that help clients understand what went wrong
   - Avoid exposing internal implementation details in production

3. **Log All Errors**
   - All errors are automatically logged by the middleware and exception handlers
   - Use structured logging for better queryability

4. **Monitor Error Rates**
   - Use Application Insights or similar tools to monitor error rates
   - Set up alerts for high error rates or specific error types

## Future Enhancements

1. **Request ID Tracking**: Add request IDs to logs and error responses for better traceability
2. **Error Context**: Include additional context in error responses (e.g., field names, validation rules)
3. **Rate Limiting**: Add rate limiting with appropriate error responses
4. **Authentication Errors**: Add specific error handling for authentication/authorization failures
5. **Custom Log Formatters**: Add JSON log formatters for better log aggregation tool compatibility

