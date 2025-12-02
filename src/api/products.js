/**
 * Products API module
 * Handles all product-related API calls
 */

import { apiGet } from './client';

/**
 * Get all available products
 *
 * @param {Object} options - Query options
 * @param {string} options.q - Search query to filter products by name (case-insensitive)
 * @param {number} options.limit - Maximum number of products to return (1-1000, default: 100)
 * @param {number} options.offset - Number of products to skip (default: 0)
 * @returns {Promise<Array<{id: number, name: string}>>} List of products
 * @throws {Error} If request fails
 *
 * Example response:
 * [
 *   { id: 1, name: "milk" },
 *   { id: 2, name: "bread" },
 *   { id: 3, name: "eggs" }
 * ]
 */
export const getProducts = async (options = {}) => {
  try {
    const { q, limit, offset } = options;

    // Build query string
    const params = new URLSearchParams();
    if (q) params.append('q', q);
    if (limit !== undefined) params.append('limit', limit.toString());
    if (offset !== undefined) params.append('offset', offset.toString());

    const queryString = params.toString();
    const endpoint = queryString
      ? `/api/v1/products/?${queryString}`
      : '/api/v1/products/';

    const products = await apiGet(endpoint);
    return products;
  } catch (error) {
    throw new Error(`Failed to fetch products: ${error.message}`);
  }
};

/**
 * Get a specific product by ID
 *
 * @param {number} productId - Product ID
 * @returns {Promise<{id: number, name: string, category?: string}>} Product details
 * @throws {Error} If request fails or product not found
 */
export const getProduct = async (productId) => {
  try {
    const product = await apiGet(`/api/v1/products/${productId}`);
    return product;
  } catch (error) {
    throw new Error(`Failed to fetch product: ${error.message}`);
  }
};

/**
 * Search products by name (case-insensitive)
 * Convenience wrapper around getProducts with search query
 *
 * @param {string} query - Search query
 * @returns {Promise<Array<{id: number, name: string}>>} List of matching products
 * @throws {Error} If request fails
 */
export const searchProducts = async (query) => {
  return getProducts({ q: query });
};
