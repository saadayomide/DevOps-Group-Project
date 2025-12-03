/**
 * Compare API module
 * Handles price comparison across supermarkets
 */

import { apiPost } from './client';

/**
 * Compare items across selected stores
 *
 * @param {Object} request - Comparison request
 * @param {Array<string>} request.items - List of product names to compare (e.g., ["milk", "bread", "eggs"])
 * @param {Array<string>} request.stores - List of store names to compare across (e.g., ["Mercadona", "Carrefour", "Lidl"])
 * @returns {Promise<CompareResponse>} Comparison results
 * @throws {Error} If request fails or validation fails
 *
 * Example request:
 * {
 *   items: ["milk", "bread", "eggs"],
 *   stores: ["Mercadona", "Carrefour", "Lidl"]
 * }
 *
 * Example response:
 * {
 *   items: [
 *     { name: "milk", store: "Lidl", price: 1.15 },
 *     { name: "bread", store: "Mercadona", price: 0.85 },
 *     { name: "eggs", store: "Lidl", price: 2.50 }
 *   ],
 *   storeTotals: [
 *     { store: "Lidl", total: 3.65 },
 *     { store: "Mercadona", total: 0.85 }
 *   ],
 *   overallTotal: 4.50,
 *   unmatched: []
 * }
 */
export const compareItems = async (request) => {
  try {
    // Validate request
    if (!request || !request.items || !request.stores) {
      throw new Error('Request must include items and stores arrays');
    }

    if (!Array.isArray(request.items) || request.items.length === 0) {
      throw new Error('items must be a non-empty array');
    }

    if (!Array.isArray(request.stores) || request.stores.length === 0) {
      throw new Error('stores must be a non-empty array');
    }

    const response = await apiPost('/api/v1/compare/', request);
    return response;
  } catch (error) {
    // Provide more context for comparison errors
    if (error.message.includes('items cannot be empty')) {
      throw new Error('Please select at least one item to compare');
    }
    if (error.message.includes('stores cannot be empty')) {
      throw new Error('Please select at least one store to compare');
    }
    throw new Error(`Failed to compare items: ${error.message}`);
  }
};

/**
 * Type definitions for TypeScript users (JSDoc comments)
 *
 * @typedef {Object} CompareItem
 * @property {string} name - Product name
 * @property {string} store - Store name where this item is cheapest
 * @property {number} price - Price of the item at this store
 *
 * @typedef {Object} StoreTotal
 * @property {string} store - Store name
 * @property {number} total - Total price for all items at this store
 *
 * @typedef {Object} CompareResponse
 * @property {Array<CompareItem>} items - List of compared items with prices
 * @property {Array<StoreTotal>} storeTotals - Total price per store
 * @property {number} overallTotal - Overall total across all stores
 * @property {Array<string>} unmatched - List of items that couldn't be matched
 */
