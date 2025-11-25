# API Layer Documentation

This directory contains the frontend API abstraction layer for communicating with the ShopSmart backend.

## Structure

```
src/api/
├── client.js          # Base API client with error handling and timeouts
├── supermarkets.js    # Supermarkets API functions
├── products.js        # Products API functions
├── compare.js         # Price comparison API functions
├── index.js           # Centralized exports
└── README.md          # This file
```

## Setup

1. **Environment Variables**

   Create a `.env` file in the project root (copy from `.env.example`):
   ```bash
   VITE_API_URL=http://localhost:8000
   ```

   For staging/production, update with the actual backend URL:
   ```bash
   VITE_API_URL=https://shopsmart-backend-staging.azurewebsites.net
   ```

2. **Import API Functions**

   ```javascript
   // Import all functions
   import { getSupermarkets, getProducts, compareItems } from './api';

   // Or import specific modules
   import { getSupermarkets } from './api/supermarkets';
   ```

## API Contract

### Endpoints

All endpoints use the base URL from `VITE_API_URL` or `REACT_APP_API_URL` environment variable.

#### Supermarkets
- `GET /api/v1/supermarkets/` - Get all supermarkets
  - Response: `Array<{id: number, name: string}>`

#### Products
- `GET /api/v1/products/` - Get all products
  - Query params: `q` (search), `limit`, `offset`
  - Response: `Array<{id: number, name: string}>`

#### Compare
- `POST /api/v1/compare/` - Compare items across stores
  - Request: `{items: string[], stores: string[]}`
  - Response: `{items: CompareItem[], storeTotals: StoreTotal[], overallTotal: number, unmatched: string[]}`

### Error Handling

All API functions throw errors with user-friendly messages. The base client handles:

- **Network errors**: "Network error - please check your connection"
- **Timeouts**: "Request timeout - please try again" (default: 10 seconds)
- **HTTP errors**: Parsed from backend `{error: string, message: string}` format
- **JSON parsing errors**: "Invalid response format from server"

### Error Response Format

Backend returns errors in this format:
```json
{
  "error": "BadRequest" | "NotFound" | "UnprocessableEntity" | "InternalServerError",
  "message": "Error description"
}
```

Status codes:
- `400` - BadRequest
- `404` - NotFound
- `422` - UnprocessableEntity (validation errors)
- `500` - InternalServerError

## Usage Examples

### Get Supermarkets

```javascript
import { getSupermarkets } from './api';

try {
  const supermarkets = await getSupermarkets();
  console.log(supermarkets);
  // [{ id: 1, name: "Mercadona" }, { id: 2, name: "Carrefour" }, ...]
} catch (error) {
  console.error('Failed to load supermarkets:', error.message);
}
```

### Get Products with Search

```javascript
import { getProducts, searchProducts } from './api';

// Get all products
const allProducts = await getProducts();

// Search products
const milkProducts = await searchProducts('milk');

// Get products with pagination
const products = await getProducts({ limit: 50, offset: 0 });
```

### Compare Items

```javascript
import { compareItems } from './api';

try {
  const result = await compareItems({
    items: ['milk', 'bread', 'eggs'],
    stores: ['Mercadona', 'Carrefour', 'Lidl']
  });

  console.log('Cheapest items:', result.items);
  console.log('Store totals:', result.storeTotals);
  console.log('Overall total:', result.overallTotal);
  console.log('Unmatched items:', result.unmatched);
} catch (error) {
  console.error('Comparison failed:', error.message);
}
```

### Error Handling in Components

```javascript
import { useState, useEffect } from 'react';
import { getSupermarkets } from './api';

function SupermarketList() {
  const [supermarkets, setSupermarkets] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSupermarkets() {
      try {
        setLoading(true);
        setError(null);
        const data = await getSupermarkets();
        setSupermarkets(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchSupermarkets();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {supermarkets.map(s => (
        <li key={s.id}>{s.name}</li>
      ))}
    </ul>
  );
}
```

## Features

✅ **Centralized API layer** - No duplicated fetch logic
✅ **Error handling** - Converts backend errors to user-friendly messages
✅ **Timeout support** - Prevents hanging requests (default: 10s)
✅ **JSON parsing** - Automatic parsing with error handling
✅ **Type safety** - JSDoc comments for better IDE support
✅ **Environment-aware** - Supports both Vite and Create React App

## Testing

When testing components that use the API layer, you can mock the API functions:

```javascript
import { getSupermarkets } from './api';

jest.mock('./api', () => ({
  getSupermarkets: jest.fn(),
}));

test('renders supermarkets', async () => {
  getSupermarkets.mockResolvedValue([
    { id: 1, name: 'Mercadona' },
    { id: 2, name: 'Carrefour' }
  ]);

  // Test your component
});
```
