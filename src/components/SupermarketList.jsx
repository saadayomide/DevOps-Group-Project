import React, { useState, useEffect } from 'react';
import { getSupermarkets } from '../api';

/**
 * SupermarketList Component
 * Displays checkboxes for selecting supermarkets to compare
 * Handles API calls, loading states, and errors gracefully
 */
const SupermarketList = ({ selectedStores, onStoreChange }) => {
  const [supermarkets, setSupermarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchSupermarkets() {
      try {
        setLoading(true);
        setError(null);
        const data = await getSupermarkets();
        setSupermarkets(data);
      } catch (err) {
        setError(err.message);
        // Set empty array on error to prevent crashes
        setSupermarkets([]);
      } finally {
        setLoading(false);
      }
    }

    fetchSupermarkets();
  }, []);

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
      <div className="supermarket-list loading">
        <p>Loading supermarkets...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="supermarket-list error">
        <p>Error loading supermarkets: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
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
