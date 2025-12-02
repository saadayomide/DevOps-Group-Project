import React from 'react';
import LoadingSpinner from './LoadingSpinner';
import ErrorDisplay from './ErrorDisplay';

/**
 * CompareResults Component
 * Displays the comparison results from the backend
 * Handles empty results, unmatched items, and error states
 */
const CompareResults = ({ results, error, loading, onRetry }) => {
  // Loading state
  if (loading) {
    return (
      <div className="compare-results">
        <LoadingSpinner message="Comparing prices across stores..." />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="compare-results">
        <ErrorDisplay
          error={error}
          onRetry={onRetry}
          errorType="general"
        />
      </div>
    );
  }

  // No results state
  if (!results) {
    return null;
  }

  const { items, storeTotals, overallTotal, unmatched } = results;

  // Empty items array (all unmatched)
  if (!items || items.length === 0) {
    return (
      <div className="compare-results empty">
        <h3>No Results</h3>
        {unmatched && unmatched.length > 0 ? (
          <div>
            <p>Could not find prices for the following items:</p>
            <ul>
              {unmatched.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p>No matching products found. Please check your item names and try again.</p>
        )}
      </div>
    );
  }

  // Display results
  return (
    <div className="compare-results">
      <h3>Price Comparison Results</h3>

      {/* Matched items */}
      <div className="results-section">
        <h4>Recommended Purchases</h4>
        <table className="results-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Store</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => (
              <tr key={index}>
                <td>{item.name}</td>
                <td>{item.store}</td>
                <td>€{item.price.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Store totals */}
      {storeTotals && storeTotals.length > 0 && (
        <div className="results-section">
          <h4>Store Totals</h4>
          <ul className="store-totals">
            {storeTotals.map((storeTotal, index) => (
              <li key={index}>
                <strong>{storeTotal.store}:</strong> €{storeTotal.total.toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Overall total */}
      {overallTotal !== undefined && (
        <div className="results-section total">
          <h4>Total Cost</h4>
          <p className="overall-total">€{overallTotal.toFixed(2)}</p>
        </div>
      )}

      {/* Unmatched items */}
      {unmatched && unmatched.length > 0 && (
        <div className="results-section unmatched">
          <h4>Items Not Found</h4>
          <p>The following items could not be found in the selected stores:</p>
          <ul>
            {unmatched.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CompareResults;
