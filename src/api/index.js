/**
 * Centralized API exports
 * Import all API functions from this file to maintain clean imports
 */

// Base client (exported for advanced use cases)
export { apiFetch, apiGet, apiPost, apiPut, apiDelete } from './client';

// Supermarkets API
export { getSupermarkets, getSupermarket } from './supermarkets';

// Products API
export { getProducts, getProduct, searchProducts } from './products';

// Compare API
export { compareItems } from './compare';
