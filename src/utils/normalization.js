/**
 * Client-side data normalization utilities
 * Prevents unnecessary backend errors by cleaning and normalizing data before sending to API
 */

/**
 * Normalize a string: lowercase, trim, and remove double spaces
 *
 * @param {string} str - String to normalize
 * @returns {string} Normalized string
 */
export const normalizeString = (str) => {
  if (typeof str !== 'string') {
    return '';
  }

  return str
    .toLowerCase()           // Convert to lowercase
    .trim()                  // Remove leading/trailing whitespace
    .replace(/\s+/g, ' ');   // Replace multiple spaces with single space
};

/**
 * Normalize an array of strings
 *
 * @param {Array<string>} items - Array of strings to normalize
 * @returns {Array<string>} Array of normalized, non-empty strings
 */
export const normalizeItems = (items) => {
  if (!Array.isArray(items)) {
    return [];
  }

  return items
    .map(normalizeString)           // Normalize each item
    .filter(item => item.length > 0) // Remove empty strings
    .filter((item, index, self) => self.indexOf(item) === index); // Deduplicate
};

/**
 * Normalize store names
 * Converts store labels/identifiers to backend-expected format
 *
 * @param {Array<string>} stores - Array of store names/identifiers
 * @returns {Array<string>} Array of normalized, deduplicated store names
 */
export const normalizeStores = (stores) => {
  if (!Array.isArray(stores)) {
    return [];
  }

  return stores
    .map(store => {
      // Normalize the string
      const normalized = normalizeString(store);
      // Backend expects store names (not IDs), so we return the normalized name
      // If stores come as IDs, they should be converted to names first
      return normalized;
    })
    .filter(store => store.length > 0) // Remove empty strings
    .filter((store, index, self) => self.indexOf(store) === index); // Deduplicate
};

/**
 * Prepare items for API request
 * Applies all normalization steps to items array
 *
 * @param {Array<string>} items - Raw items from UI
 * @returns {Array<string>} Normalized items ready for API
 */
export const prepareItemsForAPI = (items) => {
  return normalizeItems(items);
};

/**
 * Prepare stores for API request
 * Applies all normalization steps to stores array
 *
 * @param {Array<string>} stores - Raw store selections from UI
 * @returns {Array<string>} Normalized stores ready for API
 */
export const prepareStoresForAPI = (stores) => {
  return normalizeStores(stores);
};

/**
 * Convert store IDs to store names
 * Useful when UI uses store IDs but backend expects names
 *
 * @param {Array<number|string>} storeIds - Array of store IDs
 * @param {Array<{id: number, name: string}>} supermarkets - Array of supermarket objects
 * @returns {Array<string>} Array of store names
 */
export const convertStoreIdsToNames = (storeIds, supermarkets) => {
  if (!Array.isArray(storeIds) || !Array.isArray(supermarkets)) {
    return [];
  }

  const storeMap = new Map(
    supermarkets.map(s => [String(s.id), s.name])
  );

  return storeIds
    .map(id => storeMap.get(String(id)))
    .filter(name => name !== undefined)
    .map(normalizeString);
};

/**
 * Validate and prepare compare request
 * Combines all normalization steps and validates the request
 *
 * @param {Object} request - Raw request from UI
 * @param {Array<string>} request.items - Items to compare
 * @param {Array<string|number>} request.stores - Store selections (names or IDs)
 * @param {Array<{id: number, name: string}>} supermarkets - Available supermarkets (for ID conversion)
 * @returns {Object} Normalized and validated request
 * @throws {Error} If validation fails
 */
export const prepareCompareRequest = (request, supermarkets = []) => {
  if (!request) {
    throw new Error('Request is required');
  }

  let { items, stores } = request;

  // Normalize items
  const normalizedItems = prepareItemsForAPI(items);

  // Check if items are provided
  if (normalizedItems.length === 0) {
    throw new Error('At least one item is required');
  }

  // Handle stores - check if they're IDs or names
  let normalizedStores;
  if (stores && stores.length > 0) {
    // Check if first store is a number (ID) or string (name)
    const firstStore = stores[0];
    if (typeof firstStore === 'number' || (typeof firstStore === 'string' && /^\d+$/.test(firstStore))) {
      // Convert IDs to names
      normalizedStores = convertStoreIdsToNames(stores, supermarkets);
    } else {
      // Already names, just normalize
      normalizedStores = prepareStoresForAPI(stores);
    }
  } else {
    normalizedStores = [];
  }

  // Check if stores are provided
  if (normalizedStores.length === 0) {
    throw new Error('At least one store is required');
  }

  return {
    items: normalizedItems,
    stores: normalizedStores,
  };
};
