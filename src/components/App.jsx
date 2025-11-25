import React, { useState } from 'react';
import { compareItems, getSupermarkets } from '../api';
import { prepareCompareRequest } from '../utils/normalization';
import SupermarketList from './SupermarketList';
import ShoppingList from './ShoppingList';
import CompareResults from './CompareResults';
import './App.css';

/**
 * Main App Component
 * Wires together all components and handles the compare flow
 */
const App = () => {
  // State management
  const [items, setItems] = useState([]);
  const [selectedStores, setSelectedStores] = useState([]);
  const [supermarkets, setSupermarkets] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load supermarkets on mount (needed for normalization)
  React.useEffect(() => {
    async function loadSupermarkets() {
      try {
        const data = await getSupermarkets();
        setSupermarkets(data);
      } catch (err) {
        console.error('Failed to load supermarkets:', err);
        // Continue without supermarkets - normalization will still work
      }
    }
    loadSupermarkets();
  }, []);

  /**
   * Handle compare button click
   * Validates input, normalizes data, and calls API
   */
  const handleCompare = async () => {
    // Reset previous results and errors
    setResults(null);
    setError(null);

    // Client-side validation
    if (items.length === 0) {
      setError('Please add at least one item to your shopping list');
      return;
    }

    if (selectedStores.length === 0) {
      setError('Please select at least one supermarket to compare');
      return;
    }

    try {
      setLoading(true);

      // Normalize and prepare request
      const normalizedRequest = prepareCompareRequest(
        {
          items,
          stores: selectedStores,
        },
        supermarkets
      );

      // Call API
      const response = await compareItems(normalizedRequest);

      // Handle response
      setResults(response);
      setError(null);
    } catch (err) {
      // Handle errors from API or normalization
      setError(err.message || 'Failed to compare items. Please try again.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>ShopSmart</h1>
        <p>Find the cheapest combination of supermarkets for your shopping list</p>
      </header>

      <main className="app-main">
        {/* Shopping List Section */}
        <section className="section">
          <ShoppingList items={items} onItemsChange={setItems} />
        </section>

        {/* Supermarket Selection Section */}
        <section className="section">
          <SupermarketList
            selectedStores={selectedStores}
            onStoreChange={setSelectedStores}
          />
        </section>

        {/* Compare Button */}
        <section className="section">
          <button
            onClick={handleCompare}
            disabled={loading || items.length === 0 || selectedStores.length === 0}
            className="compare-button"
          >
            {loading ? 'Comparing...' : 'Compare Prices'}
          </button>

          {/* Validation hints */}
          {items.length === 0 && (
            <p className="validation-hint">Add items to your shopping list first</p>
          )}
          {items.length > 0 && selectedStores.length === 0 && (
            <p className="validation-hint">Select at least one supermarket</p>
          )}
        </section>

        {/* Results Section */}
        {(results || error || loading) && (
          <section className="section">
            <CompareResults
              results={results}
              error={error}
              loading={loading}
            />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>ShopSmart - Smart Shopping List Optimizer</p>
      </footer>
    </div>
  );
};

export default App;
