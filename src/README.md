# Frontend Integration Guide

This document provides integration notes for the ShopSmart frontend-backend integration.

## Overview

The frontend is built with React and communicates with the FastAPI backend through a centralized API layer. All API calls are abstracted through reusable functions with comprehensive error handling, loading states, and retry logic.

## Architecture

```
Frontend (React)
  ↓
API Layer (src/api/)
  ↓
Normalization (src/utils/normalization.js)
  ↓
Backend API (FastAPI)
  ↓
Database (Azure SQL)
```

## Key Components

### API Layer (`src/api/`)

**Base Client** (`client.js`):
- Centralized fetch logic with timeout (10s default)
- Automatic JSON parsing
- Error handling for all HTTP status codes
- Network error detection
- Timeout handling

**API Modules**:
- `supermarkets.js` - Get supermarkets list
- `products.js` - Get products with search/filtering
- `compare.js` - Compare items across stores

**Request Structure**:
```javascript
// All requests automatically include:
// - Base URL from VITE_API_URL environment variable
// - Content-Type: application/json header
// - Timeout handling
```

**Response Mapping**:
- `200 OK` → Returns parsed JSON data
- `204 No Content` → Returns null
- `400 BadRequest` → Throws Error with message
- `404 NotFound` → Throws Error with message
- `422 UnprocessableEntity` → Throws Error with validation message
- `500 InternalServerError` → Throws Error with server message
- Network errors → Throws Error with network message
- Timeout → Throws Error with timeout message

### Data Normalization (`src/utils/normalization.js`)

**Purpose**: Prevents backend validation errors by cleaning data before sending.

**Normalization Steps**:
1. Convert to lowercase
2. Trim whitespace
3. Remove double/multiple spaces
4. Remove empty strings
5. Deduplicate items/stores

**Usage**:
```javascript
import { prepareCompareRequest } from '../utils/normalization';

const normalized = prepareCompareRequest(
  { items: ['  Milk  ', 'BREAD'], stores: ['Mercadona'] },
  supermarkets
);
// Returns: { items: ['milk', 'bread'], stores: ['mercadona'] }
```

### UI Components

**SupermarketList**:
- Fetches supermarkets on mount
- Displays checkboxes for selection
- Handles loading/error states
- Includes retry logic (max 3 attempts)

**ShoppingList**:
- Manages shopping list items
- Prevents duplicates
- Validates input

**CompareResults**:
- Displays comparison results
- Shows matched items, store totals, overall total
- Handles unmatched items
- Error state display

**ErrorDisplay**:
- Categorizes errors (network, timeout, validation, etc.)
- Shows appropriate icons and messages
- Provides retry functionality

**LoadingSpinner**:
- Animated loading indicator
- Customizable message

## Error Handling

### Error Categories

1. **Network Errors**: Connection failures, unreachable backend
   - Message: "Network error - please check your connection"
   - Retry: Available (up to 3 attempts)

2. **Timeout Errors**: Request exceeds 10 seconds
   - Message: "Request timeout - please try again"
   - Retry: Available

3. **Validation Errors (422)**: Invalid request data
   - Message: Parsed from backend `{error, message}` format
   - Retry: Available

4. **Bad Request (400)**: Business rule violations
   - Message: Parsed from backend
   - Retry: Available

5. **Not Found (404)**: Resource doesn't exist
   - Message: Parsed from backend
   - Retry: Available

### Error Response Format

Backend returns errors in this format:
```json
{
  "error": "ErrorType",
  "message": "Error description"
}
```

Frontend converts these to user-friendly Error objects with appropriate messages.

## Loading States

All API calls show loading states:
- SupermarketList: Shows spinner while fetching
- Compare operation: Shows spinner during comparison
- Loading messages are customizable

## Retry Logic

- Maximum 3 retry attempts for failed requests
- Retry button appears on errors
- Retry count resets on success
- After 3 failures, shows "Maximum retry attempts reached"

## Environment Configuration

### Local Development

Create `.env` file:
```bash
VITE_API_URL=http://localhost:8000
```

### Staging

```bash
VITE_API_URL=https://shopsmart-backend-staging.azurewebsites.net
```

### Production

```bash
VITE_API_URL=https://shopsmart-backend-production.azurewebsites.net
```

## API Endpoints

### GET /api/v1/supermarkets/
- **Response**: `Array<{id: number, name: string}>`
- **Error Handling**: Network errors, empty response

### GET /api/v1/products/
- **Query Params**: `q` (search), `limit`, `offset`
- **Response**: `Array<{id: number, name: string}>`
- **Error Handling**: Validation errors (422) for invalid params

### POST /api/v1/compare/
- **Request**: `{items: string[], stores: string[]}`
- **Response**: `{items: CompareItem[], storeTotals: StoreTotal[], overallTotal: number, unmatched: string[]}`
- **Error Handling**: 400 (empty arrays), 422 (validation), network, timeout

## Integration Checklist

### Before Integration
- [ ] Backend is running and accessible
- [ ] Environment variable `VITE_API_URL` is set
- [ ] CORS is configured on backend (Team C)
- [ ] Database is seeded with test data

### During Integration
- [ ] Test supermarket loading
- [ ] Test product search
- [ ] Test compare functionality
- [ ] Test error scenarios (network, timeout, 422, 400)
- [ ] Test retry functionality
- [ ] Test data normalization
- [ ] Verify CORS works from deployed frontend

### After Integration
- [ ] All test scenarios pass (see INTEGRATION_TEST_SCENARIOS.md)
- [ ] Error handling works correctly
- [ ] Loading states display properly
- [ ] Retry logic functions
- [ ] Staging and local behave identically

## CORS Configuration

**Team C Responsibility**: Configure CORS on backend

**Required Headers**:
- `Access-Control-Allow-Origin`: Frontend URL
- `Access-Control-Allow-Methods`: GET, POST, OPTIONS
- `Access-Control-Allow-Headers`: Content-Type
- `Access-Control-Allow-Credentials`: true (if needed)

**Team B Verification**:
- Test API calls from deployed frontend
- Check browser console for CORS errors
- Verify preflight (OPTIONS) requests succeed

## Testing

See `INTEGRATION_TEST_SCENARIOS.md` for comprehensive test scenarios.

**Manual Testing**:
1. Test all happy paths
2. Test error scenarios
3. Test retry functionality
4. Test data normalization
5. Test CORS from deployed frontend

**Automated Testing** (Team C):
- Postman collection
- Playwright/Cypress E2E tests
- Azure pipeline integration tests

## Common Issues

### CORS Errors
- **Symptom**: Browser console shows CORS error
- **Solution**: Verify CORS configuration on backend (Team C)
- **Check**: `Access-Control-Allow-Origin` header includes frontend URL

### Network Errors
- **Symptom**: "Network error - please check your connection"
- **Solution**: Verify backend is running and accessible
- **Check**: `VITE_API_URL` environment variable is correct

### Timeout Errors
- **Symptom**: "Request timeout - please try again"
- **Solution**: Backend is slow or unresponsive
- **Check**: Backend performance, network latency

### 422 Validation Errors
- **Symptom**: "UnprocessableEntity" error
- **Solution**: Data normalization should prevent this
- **Check**: Normalization is applied before API calls

### Empty Results
- **Symptom**: No items in results, only unmatched
- **Solution**: Items don't exist in database
- **Check**: Database is seeded with test data

## Code Structure

```
src/
├── api/                    # API layer
│   ├── client.js          # Base fetch with error handling
│   ├── supermarkets.js    # Supermarkets API
│   ├── products.js        # Products API
│   ├── compare.js         # Compare API
│   └── index.js           # Centralized exports
├── utils/
│   └── normalization.js  # Data normalization
├── components/
│   ├── App.jsx           # Main app component
│   ├── SupermarketList.jsx
│   ├── ShoppingList.jsx
│   ├── CompareResults.jsx
│   ├── ErrorDisplay.jsx  # Error UI component
│   └── LoadingSpinner.jsx
└── README.md             # This file
```

## Dependencies

- React (UI framework)
- No external HTTP libraries (uses native fetch)
- Environment variables (Vite or Create React App)

## Notes for Team C

1. **CORS**: Must be configured to allow frontend origin
2. **Error Format**: Backend must return `{error, message}` format
3. **Response Format**: All responses must be valid JSON (except 204)
4. **Staging URL**: Provide staging backend URL for testing
5. **Monitoring**: Monitor API response times and errors

## Notes for Team A

1. **Styling**: ErrorDisplay and LoadingSpinner can be styled
2. **UI Polish**: Add animations, improve mobile experience
3. **Accessibility**: Enhance ARIA labels, keyboard navigation

## Support

For integration issues:
1. Check error messages in browser console
2. Verify environment variables
3. Test API endpoints directly (Postman)
4. Check CORS configuration
5. Review INTEGRATION_TEST_SCENARIOS.md

---

**Last Updated**: Sprint 2 - Team B Integration Phase
