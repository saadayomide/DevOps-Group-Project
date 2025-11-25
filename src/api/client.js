/**
 * Base API client with error handling, timeouts, and JSON parsing
 * Centralized fetch logic to avoid duplication across components
 */

const DEFAULT_TIMEOUT = 10000; // 10 seconds

/**
 * Get the base API URL from environment variables
 * Supports both Vite (VITE_API_URL) and Create React App (REACT_APP_API_URL)
 *
 * Note: Environment variables are replaced at build time by the bundler.
 * For Vite: Set VITE_API_URL in .env file - Vite replaces import.meta.env at build time
 * For Create React App: Set REACT_APP_API_URL in .env file - CRA replaces process.env at build time
 *
 * In Vite projects, you can also access via: import.meta.env.VITE_API_URL directly
 * This function provides a runtime fallback for both environments.
 */
const getApiUrl = () => {
  // Create React App: process.env.REACT_APP_API_URL
  // This is replaced at build time, so it's safe to access
  if (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }

  // Vite: Check for VITE_API_URL via window (set by Vite in dev mode)
  // In production builds, Vite replaces import.meta.env at build time
  // For runtime access, we check window.__VITE_API_URL__ or use a global
  if (typeof window !== 'undefined') {
    // Check if Vite injected the env var (dev mode)
    if (window.__VITE_API_URL__) {
      return window.__VITE_API_URL__;
    }
  }

  // Default to local development
  // In actual Vite projects, replace this file or configure VITE_API_URL in .env
  // The bundler will replace import.meta.env.VITE_API_URL at build time
  return 'http://localhost:8000';
};

/**
 * Convert backend error response to user-friendly error message
 * Backend returns: { error: "ErrorType", message: "Error message" }
 */
const parseError = async (response) => {
  try {
    const errorData = await response.json();
    // Backend error structure: { error: string, message: string }
    if (errorData.message) {
      return errorData.message;
    }
    if (errorData.error) {
      return errorData.error;
    }
    return `Error ${response.status}: ${response.statusText}`;
  } catch (e) {
    // If JSON parsing fails, return status text
    return `Error ${response.status}: ${response.statusText}`;
  }
};

/**
 * Create a timeout promise that rejects after specified milliseconds
 */
const createTimeout = (ms) => {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), ms);
  });
};

/**
 * Base fetch function with error handling, timeout, and JSON parsing
 *
 * @param {string} endpoint - API endpoint (e.g., '/api/v1/products')
 * @param {RequestInit} options - Fetch options (method, body, headers, etc.)
 * @param {number} timeout - Request timeout in milliseconds (default: 10000)
 * @returns {Promise<any>} Parsed JSON response
 * @throws {Error} User-friendly error message
 */
export const apiFetch = async (endpoint, options = {}, timeout = DEFAULT_TIMEOUT) => {
  const baseUrl = getApiUrl();
  const url = `${baseUrl}${endpoint}`;

  // Default headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Prepare fetch options
  const fetchOptions = {
    ...options,
    headers,
  };

  try {
    // Race between fetch and timeout
    const response = await Promise.race([
      fetch(url, fetchOptions),
      createTimeout(timeout),
    ]);

    // Handle timeout (response will be undefined if timeout wins)
    if (!response) {
      throw new Error('Request timeout - please try again');
    }

    // Handle non-OK responses
    if (!response.ok) {
      const errorMessage = await parseError(response);
      throw new Error(errorMessage);
    }

    // Parse JSON response
    try {
      const data = await response.json();
      return data;
    } catch (e) {
      // If response is not JSON, return empty object
      // Some endpoints might return 204 No Content
      if (response.status === 204) {
        return null;
      }
      throw new Error('Invalid response format from server');
    }
  } catch (error) {
    // Re-throw if it's already an Error with a message
    if (error instanceof Error) {
      throw error;
    }
    // Handle network errors
    throw new Error('Network error - please check your connection');
  }
};

/**
 * GET request helper
 */
export const apiGet = (endpoint, timeout = DEFAULT_TIMEOUT) => {
  return apiFetch(endpoint, { method: 'GET' }, timeout);
};

/**
 * POST request helper
 */
export const apiPost = (endpoint, data, timeout = DEFAULT_TIMEOUT) => {
  return apiFetch(
    endpoint,
    {
      method: 'POST',
      body: JSON.stringify(data),
    },
    timeout
  );
};

/**
 * PUT request helper
 */
export const apiPut = (endpoint, data, timeout = DEFAULT_TIMEOUT) => {
  return apiFetch(
    endpoint,
    {
      method: 'PUT',
      body: JSON.stringify(data),
    },
    timeout
  );
};

/**
 * DELETE request helper
 */
export const apiDelete = (endpoint, timeout = DEFAULT_TIMEOUT) => {
  return apiFetch(endpoint, { method: 'DELETE' }, timeout);
};
