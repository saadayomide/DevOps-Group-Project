import { useState, useEffect } from 'react';
import { compareBasket, fetchSupermarkets } from '../api';

function ComparisonPage() {
  const [comparisonData, setComparisonData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [expandedItems, setExpandedItems] = useState({});
  const [stores, setStores] = useState([]);
  const [selectedStores, setSelectedStores] = useState([]);
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState('');

  useEffect(() => {
    loadSupermarkets();
    // Load saved items from localStorage
    const savedItems = localStorage.getItem('comparisonItems');
    if (savedItems) {
      setItems(JSON.parse(savedItems));
    }
  }, []);

  const loadSupermarkets = async () => {
    try {
      const data = await fetchSupermarkets();
      setStores(data);
      // Select all stores by default
      setSelectedStores(data.map(s => s.name));
    } catch (err) {
      console.error('Failed to load supermarkets:', err);
    }
  };

  const handleAddItem = (e) => {
    e.preventDefault();
    if (newItem.trim() && !items.includes(newItem.trim())) {
      const updatedItems = [...items, newItem.trim()];
      setItems(updatedItems);
      localStorage.setItem('comparisonItems', JSON.stringify(updatedItems));
      setNewItem('');
    }
  };

  const handleRemoveItem = (item) => {
    const updatedItems = items.filter(i => i !== item);
    setItems(updatedItems);
    localStorage.setItem('comparisonItems', JSON.stringify(updatedItems));
  };

  const handleCompare = async () => {
    if (items.length === 0) {
      setError('Please add items to compare');
      return;
    }
    if (selectedStores.length === 0) {
      setError('Please select at least one store');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await compareBasket(items, selectedStores);
      
      // Transform the compare response to comparison format
      const comparisons = transformCompareResponse(data);
      setComparisonData(comparisons);
    } catch (err) {
      setError('Failed to compare prices. Please try again.');
      console.error('Error comparing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await handleCompare();
    setRefreshing(false);
  };

  const transformCompareResponse = (data) => {
    // Transform the backend response to our comparison format
    // Adjust this based on actual backend response structure
    if (!data || !data.results) return [];
    
    return data.results.map(result => {
      const offers = result.prices || [];
      const sortedOffers = [...offers].sort((a, b) => (a.price || Infinity) - (b.price || Infinity));
      const bestOffer = sortedOffers[0];
      
      return {
        category_name: result.item || result.product_name || 'Unknown',
        best_store: bestOffer?.store || 'N/A',
        best_price: bestOffer?.price || null,
        best_offer: bestOffer ? {
          store: bestOffer.store,
          product_name: bestOffer.product_name || result.item,
          price: bestOffer.price
        } : null,
        comparison_json: sortedOffers.map(offer => ({
          store: offer.store || offer.supermarket,
          product_name: offer.product_name || result.item,
          price: offer.price
        }))
      };
    });
  };

  const toggleExpand = (index) => {
    setExpandedItems((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const toggleStore = (storeName) => {
    setSelectedStores(prev => 
      prev.includes(storeName) 
        ? prev.filter(s => s !== storeName)
        : [...prev, storeName]
    );
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const getStoreColor = (store) => {
    const colors = {
      walmart: '#0071ce',
      target: '#cc0000',
      amazon: '#ff9900',
      costco: '#e31837',
      kroger: '#0068b5',
      aldi: '#00005f',
      mercadona: '#5ab630',
      carrefour: '#004e9f',
      lidl: '#0050aa',
    };
    return colors[store?.toLowerCase()] || 'var(--accent)';
  };

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <h1>Price Comparison</h1>
      </div>

      {error && (
        <div className="alert error" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>{error}</span>
          <button className="link-button" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {/* Items Input Section */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2>Items to Compare</h2>
        <form onSubmit={handleAddItem} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Enter item (e.g., Milk, Eggs, Bread)"
            style={{ flex: 1, padding: '0.75rem', borderRadius: 'var(--radius)', border: '1px solid var(--border)', background: 'var(--bg-input)' }}
          />
          <button type="submit" className="btn primary">Add</button>
        </form>
        
        {items.length > 0 && (
          <div className="chip-group">
            {items.map((item, index) => (
              <span key={index} className="chip active" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                {item}
                <button 
                  onClick={() => handleRemoveItem(item)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, fontSize: '1rem' }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Store Selection */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2>Select Stores</h2>
        <div className="chip-group">
          {stores.map((store) => (
            <button
              key={store.id}
              className={`chip ${selectedStores.includes(store.name) ? 'active' : ''}`}
              onClick={() => toggleStore(store.name)}
            >
              {store.name}
            </button>
          ))}
        </div>
      </div>

      {/* Compare Button */}
      <div style={{ marginBottom: '1.5rem' }}>
        <button
          className="btn primary"
          onClick={handleCompare}
          disabled={loading || items.length === 0}
          style={{ width: '100%', padding: '1rem' }}
        >
          {loading ? (
            <>
              <span className="spinner-small" style={{ marginRight: '0.5rem' }}></span>
              Comparing Prices...
            </>
          ) : (
            'Compare Prices'
          )}
        </button>
      </div>

      {/* Results */}
      {comparisonData.length > 0 && (
        <>
          <div className="comparison-header" style={{ marginBottom: '1rem' }}>
            <h2>Results</h2>
            <button
              className="btn"
              onClick={handleRefresh}
              disabled={refreshing}
              style={{ background: 'var(--bg-input)' }}
            >
              {refreshing ? 'Refreshing...' : '↻ Refresh'}
            </button>
          </div>

          <div className="comparison-grid">
            {comparisonData.map((item, index) => (
              <div key={index} className="card comparison-card-item">
                <div className="comparison-card-header">
                  <span className="category-badge">{item.category_name}</span>
                  {item.best_store && (
                    <span
                      className="best-store-badge"
                      style={{ backgroundColor: getStoreColor(item.best_store) }}
                    >
                      ✓ Best: {item.best_store}
                    </span>
                  )}
                </div>

                <div className="comparison-card-body">
                  <h3 className="product-name">
                    {item.best_offer?.product_name || item.category_name}
                  </h3>
                  <div className="best-price-display">
                    <span className="price-label">Best Price</span>
                    <span className="price-value">{formatPrice(item.best_price)}</span>
                  </div>
                </div>

                {item.comparison_json && item.comparison_json.length > 1 && (
                  <div className="comparison-card-footer">
                    <button
                      className="expand-btn"
                      onClick={() => toggleExpand(index)}
                    >
                      <span>
                        {expandedItems[index] ? 'Hide' : 'Show'} all {item.comparison_json.length} offers
                      </span>
                      <span className={`expand-icon ${expandedItems[index] ? 'expanded' : ''}`}>
                        ▼
                      </span>
                    </button>

                    {expandedItems[index] && (
                      <div className="offers-list">
                        {item.comparison_json.map((offer, offerIndex) => {
                          const isBest = offer.store?.toLowerCase() === item.best_store?.toLowerCase();
                          return (
                            <div
                              key={offerIndex}
                              className={`offer-item ${isBest ? 'best-offer' : ''}`}
                            >
                              <div className="offer-rank">#{offerIndex + 1}</div>
                              <div className="offer-details">
                                <span
                                  className="offer-store"
                                  style={{ color: getStoreColor(offer.store) }}
                                >
                                  {offer.store}
                                </span>
                                <span className="offer-product">
                                  {offer.product_name}
                                </span>
                              </div>
                              <div className="offer-price">
                                {formatPrice(offer.price)}
                                {isBest && <span className="cheapest-tag">Cheapest</span>}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {comparisonData.length === 0 && !loading && items.length > 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
          <h2 style={{ marginBottom: '0.5rem' }}>Ready to Compare</h2>
          <p className="muted">Click "Compare Prices" to find the best deals.</p>
        </div>
      )}

      {items.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🛒</div>
          <h2 style={{ marginBottom: '0.5rem' }}>No items added</h2>
          <p className="muted">Add items above to start comparing prices.</p>
        </div>
      )}
    </div>
  );
}

export default ComparisonPage;