import React, { useState, useEffect } from 'react';
import { getSupermarkets } from '../api';
import LoadingSpinner from './LoadingSpinner';
import ErrorDisplay from './ErrorDisplay';

/**
 * SupermarketList Component
 * Displays checkboxes for selecting supermarkets to compare
 * Handles API calls, loading states, and errors gracefully
 * Includes retry logic for failed requests
 */
const SupermarketList = ({ selectedStores, onStoreChange }) => {
  const [supermarkets, setSupermarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const MAX_RETRIES = 3;

  const fetchSupermarkets = async (isRetry = false) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSupermarkets();
      setSupermarkets(data);
      setRetryCount(0); // Reset retry count on success
    } catch (err) {
      setError(err.message);
      // Set empty array on error to prevent crashes
      setSupermarkets([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSupermarkets();
  }, []);

  const handleRetry = () => {
    if (retryCount < MAX_RETRIES) {
      setRetryCount(prev => prev + 1);
      fetchSupermarkets(true);
    } else {
      setError('Maximum retry attempts reached. Please refresh the page.');
    }
  };

  const handleCheckboxChange = (storeName) => {
    if (!onStoreChange) return;

    const isSelected = selectedStores.includes(storeName);
    if (isSelected) {
      // Remove store
      onStoreChange(selectedStores.filter(s => s !== storeName));
    } else {
      // Add store
      onStoreChange([...selectedStores, storeName]);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="supermarket-list">
        <h3>Select Supermarkets to Compare</h3>
        <LoadingSpinner message="Loading supermarkets..." />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="supermarket-list">
        <h3>Select Supermarkets to Compare</h3>
        <ErrorDisplay
          error={error}
          onRetry={retryCount < MAX_RETRIES ? handleRetry : null}
          errorType="network"
        />
        {retryCount >= MAX_RETRIES && (
          <p className="retry-limit-message">
            Unable to load supermarkets. Please check your connection and refresh the page.
          </p>
        )}
      </div>
    );
  }

  // Empty state
  if (supermarkets.length === 0) {
    return (
      <div className="supermarket-list empty">
        <p>No supermarkets available</p>
      </div>
    );
  }

  // Render checkboxes
  return (
    <div className="supermarket-list">
      <h3>Select Supermarkets to Compare</h3>
      <div className="supermarket-checkboxes">
        {supermarkets.map((supermarket) => (
          <label key={supermarket.id} className="supermarket-checkbox">
            <input
              type="checkbox"
              checked={selectedStores.includes(supermarket.name)}
              onChange={() => handleCheckboxChange(supermarket.name)}
            />
            <span>{supermarket.name}</span>
          </label>
        ))}
      </div>
      {selectedStores.length === 0 && (
        <p className="hint">Select at least one supermarket to compare prices</p>
      )}
    </div>
  );
};

export default SupermarketList;
