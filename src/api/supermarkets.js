/**
 * Supermarkets API module
 * Handles all supermarket-related API calls
 */

import { apiGet } from './client';

/**
 * Get all available supermarkets
 *
 * @returns {Promise<Array<{id: number, name: string}>>} List of supermarkets
 * @throws {Error} If request fails
 *
 * Example response:
 * [
 *   { id: 1, name: "Mercadona" },
 *   { id: 2, name: "Carrefour" },
 *   { id: 3, name: "Lidl" }
 * ]
 */
export const getSupermarkets = async () => {
  try {
    const supermarkets = await apiGet('/api/v1/supermarkets/');
    return supermarkets;
  } catch (error) {
    // Re-throw with context for better error messages
    throw new Error(`Failed to fetch supermarkets: ${error.message}`);
  }
};

/**
 * Get a specific supermarket by ID
 *
 * @param {number} supermarketId - Supermarket ID
 * @returns {Promise<{id: number, name: string, city?: string}>} Supermarket details
 * @throws {Error} If request fails or supermarket not found
 */
export const getSupermarket = async (supermarketId) => {
  try {
    const supermarket = await apiGet(`/api/v1/supermarkets/${supermarketId}`);
    return supermarket;
  } catch (error) {
    throw new Error(`Failed to fetch supermarket: ${error.message}`);
  }
};
