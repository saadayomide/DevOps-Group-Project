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

  // Form state for new item
  const [newItem, setNewItem] = useState({
    productName: '',
    category: '',
    brand: '',
    variants: [],
    quantity: 1,
    unit: 'unit'
  });
  const [variantInput, setVariantInput] = useState('');
  const [categories, setCategories] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(false);

  // Available units
  const UNITS = ['unit', 'kg', 'g', 'L', 'ml', 'pack', 'dozen', 'bottle', 'can', 'box'];

  // Common variants for quick selection
  const COMMON_VARIANTS = {
    'Dairy': ['Whole', 'Semi-skimmed', 'Skimmed', 'Lactose-free', 'Organic'],
    'Bakery': ['White', 'Whole wheat', 'Multigrain', 'Sourdough', 'Gluten-free'],
    'Meat & Poultry': ['Breast', 'Thigh', 'Whole', 'Wings', 'Drumsticks', 'Organic'],
    'Fruits & Vegetables': ['Organic', 'Fresh', 'Frozen', 'Local', 'Imported'],
    'Beverages': ['Regular', 'Sugar-free', 'Diet', 'Zero', 'Organic'],
    'Snacks': ['Original', 'Low-fat', 'Baked', 'Organic', 'Family size'],
    'Frozen Foods': ['Family pack', 'Single serve', 'Organic', 'Premium'],
    'Pantry': ['Organic', 'Whole grain', 'Low sodium', 'Family size'],
    'Household': ['Regular', 'Eco-friendly', 'Concentrated', 'Bulk'],
    'Personal Care': ['Regular', 'Sensitive', 'Organic', 'Travel size'],
  };

  const DEFAULT_VARIANTS = ['Organic', 'Low-fat', 'Sugar-free', 'Gluten-free', 'Family size'];

  // Fallback categories
  const FALLBACK_CATEGORIES = [
    { id: 1, name: 'Dairy' },
    { id: 2, name: 'Bakery' },
    { id: 3, name: 'Meat & Poultry' },
    { id: 4, name: 'Fruits & Vegetables' },
    { id: 5, name: 'Beverages' },
    { id: 6, name: 'Snacks' },
    { id: 7, name: 'Frozen Foods' },
    { id: 8, name: 'Pantry' },
    { id: 9, name: 'Household' },
    { id: 10, name: 'Personal Care' },
  ];

  // Fallback stores
  const FALLBACK_STORES = [
    { id: 1, name: 'Mercadona' },
    { id: 2, name: 'Carrefour' },
    { id: 3, name: 'Lidl' },
    { id: 4, name: 'Alcampo' },
    { id: 5, name: 'Dia' },
    { id: 6, name: 'El Corte Inglés' },
  ];

  useEffect(() => {
    loadSupermarkets();
    loadCategories();
    // Load saved items from localStorage
    const savedItems = localStorage.getItem('comparisonItems');
    if (savedItems) {
      try {
        const parsed = JSON.parse(savedItems);
        // Ensure each item has required fields with defaults
        const validatedItems = parsed.map(item => ({
          id: item.id || Date.now(),
          productName: item.productName || '',
          category: item.category || '',
          brand: item.brand || null,
          variants: Array.isArray(item.variants) ? item.variants : [],
          quantity: item.quantity || 1,
          unit: item.unit || 'unit'
        }));
        setItems(validatedItems);
      } catch (e) {
        console.error('Failed to parse saved items:', e);
        localStorage.removeItem('comparisonItems');
      }
    }
  }, []);

  const loadSupermarkets = async () => {
    try {
      const data = await fetchSupermarkets();
      if (data && Array.isArray(data) && data.length > 0) {
        setStores(data);
        setSelectedStores(data.map(s => s.name));
      } else {
        // Use fallback stores
        setStores(FALLBACK_STORES);
        setSelectedStores(FALLBACK_STORES.map(s => s.name));
      }
    } catch (err) {
      console.error('Failed to load supermarkets:', err);
      // Use fallback stores
      setStores(FALLBACK_STORES);
      setSelectedStores(FALLBACK_STORES.map(s => s.name));
    }
  };

  const loadCategories = async () => {
    setLoadingCategories(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE || '/api/v1'}/catalog/categories`);
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          setCategories(data);
        } else {
          setCategories(FALLBACK_CATEGORIES);
        }
      } else {
        setCategories(FALLBACK_CATEGORIES);
      }
    } catch (err) {
      console.error('Failed to load categories:', err);
      setCategories(FALLBACK_CATEGORIES);
    } finally {
      setLoadingCategories(false);
    }
  };

  const handleInputChange = (field, value) => {
    setNewItem(prev => ({ ...prev, [field]: value }));
    if (error) setError(null);
  };

  const handleAddVariant = (variant) => {
    if (variant && !newItem.variants.includes(variant)) {
      setNewItem(prev => ({
        ...prev,
        variants: [...(prev.variants || []), variant]
      }));
      setVariantInput('');
    }
  };

  const handleRemoveVariant = (variant) => {
    setNewItem(prev => ({
      ...prev,
      variants: (prev.variants || []).filter(v => v !== variant)
    }));
  };

  const handleToggleVariant = (variant) => {
    const variants = newItem.variants || [];
    if (variants.includes(variant)) {
      handleRemoveVariant(variant);
    } else {
      handleAddVariant(variant);
    }
  };

  const getVariantSuggestions = () => {
    const category = newItem.category;
    if (!category) return DEFAULT_VARIANTS;
    return COMMON_VARIANTS[category] || DEFAULT_VARIANTS;
  };

  const validateItem = () => {
    // Either product name or category is required
    if (!newItem.productName?.trim() && !newItem.category) {
      setError('Please enter a product name or select a category');
      return false;
    }
    if (newItem.quantity < 1) {
      setError('Quantity must be at least 1');
      return false;
    }
    return true;
  };

  // Build search query from item fields
  const buildSearchQuery = (item) => {
    const parts = [];
    if (item.productName?.trim()) parts.push(item.productName.trim());
    if (item.brand?.trim()) parts.push(item.brand.trim());
    if (item.variants?.length > 0) parts.push(...item.variants);
    // If only category selected, use it as fallback
    if (parts.length === 0 && item.category) parts.push(item.category);
    return parts.join(' ');
  };

  const handleAddItem = (e) => {
    e.preventDefault();

    if (!validateItem()) return;

    const itemToAdd = {
      id: Date.now(),
      productName: newItem.productName?.trim() || '',
      category: newItem.category,
      brand: newItem.brand?.trim() || null,
      variants: newItem.variants || [],
      quantity: newItem.quantity,
      unit: newItem.unit
    };

    const updatedItems = [...items, itemToAdd];
    setItems(updatedItems);
    localStorage.setItem('comparisonItems', JSON.stringify(updatedItems));

    // Reset form
    setNewItem({
      productName: '',
      category: '',
      brand: '',
      variants: [],
      quantity: 1,
      unit: 'unit'
    });
    setVariantInput('');
    setError(null);
  };

  const handleRemoveItem = (itemId) => {
    const updatedItems = items.filter(i => i.id !== itemId);
    setItems(updatedItems);
    localStorage.setItem('comparisonItems', JSON.stringify(updatedItems));
  };

  const handleClearAll = () => {
    setItems([]);
    localStorage.removeItem('comparisonItems');
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

      // Backend expects items as a list of strings (product names/search queries)
      // Build search queries from product name, brand, and variants
      const itemsForBackend = items.map(buildSearchQuery).filter(Boolean);

      const data = await compareBasket(itemsForBackend, selectedStores);
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
    /**
     * Backend CompareResponse shape (api/app/schemas.py):
     * {
     *   items: [{ name, store, price }],
     *   storeTotals: [{ store, total }],
     *   overallTotal: number,
     *   unmatched: [string],
     *   priceComparison: [
     *     { name, prices: [{ store, price }], cheapestStore, cheapestPrice }
     *   ]
     * }
     *
     * The UI expects an array of objects shaped like:
     * {
     *   category_name: string,
     *   best_store: string,
     *   best_price: number,
     *   best_offer: { store, product_name, price } | null,
     *   comparison_json: [{ store, product_name, price }]
     * }
     */
    if (!data || !Array.isArray(data.priceComparison)) {
      return [];
    }

    return data.priceComparison.map((item) => {
      const offers = item.prices || [];
      const sortedOffers = [...offers].sort(
        (a, b) => (a.price ?? Infinity) - (b.price ?? Infinity)
      );
      const bestOffer =
        sortedOffers.find((o) => o.store === item.cheapestStore) ||
        sortedOffers[0];

      return {
        category_name: item.name || 'Unknown',
        best_store: item.cheapestStore || bestOffer?.store || 'N/A',
        best_price: item.cheapestPrice ?? bestOffer?.price ?? null,
        best_offer: bestOffer
          ? {
              store: bestOffer.store,
              product_name: item.name,
              price: bestOffer.price,
            }
          : null,
        comparison_json: sortedOffers.map((offer) => ({
          store: offer.store,
          product_name: item.name,
          price: offer.price,
        })),
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

  const selectAllStores = () => {
    setSelectedStores(stores.map(s => s.name));
  };

  const deselectAllStores = () => {
    setSelectedStores([]);
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `€${parseFloat(price).toFixed(2)}`;
  };

  const getStoreColor = (store) => {
    const colors = {
      mercadona: '#5ab630',
      carrefour: '#004e9f',
      lidl: '#0050aa',
      alcampo: '#e30613',
      dia: '#e30613',
      'el corte inglés': '#00a651',
      eroski: '#ff6600',
      aldi: '#00005f',
    };
    return colors[store?.toLowerCase()] || 'var(--accent)';
  };

  // Safe access to variants array
  const itemVariants = newItem.variants || [];

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <h1>Price Comparison</h1>
      </div>

      {error && (
        <div className="alert error">
          <span>{error}</span>
          <button className="link-button" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {/* Shopping List Input Form */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2>Add Item to Compare</h2>

        <form onSubmit={handleAddItem} className="item-form">
          {/* Product Name Input */}
          <div className="field">
            <label htmlFor="productName">Product Name</label>
            <input
              type="text"
              id="productName"
              value={newItem.productName}
              onChange={(e) => handleInputChange('productName', e.target.value)}
              placeholder="e.g., Leche entera, Huevos frescos, Pan de molde"
            />
            <small className="muted">Enter a specific product name for best results, or use category below</small>
          </div>

          {/* Category Dropdown */}
          <div className="field">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              value={newItem.category}
              onChange={(e) => handleInputChange('category', e.target.value)}
              disabled={loadingCategories}
            >
              <option value="">Select a category</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.name}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* Brand Input */}
          <div className="field">
            <label htmlFor="brand">Brand (optional)</label>
            <input
              type="text"
              id="brand"
              value={newItem.brand}
              onChange={(e) => handleInputChange('brand', e.target.value)}
              placeholder="e.g., Hacendado, Carrefour, Marca blanca"
            />
          </div>

          {/* Variants Section */}
          <div className="field">
            <label>Variants / Preferences</label>

            {/* Quick variant checkboxes */}
            {newItem.category && (
              <div className="variant-checkboxes">
                {getVariantSuggestions().map(variant => (
                  <label key={variant} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={itemVariants.includes(variant)}
                      onChange={() => handleToggleVariant(variant)}
                    />
                    <span>{variant}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Custom variant input */}
            <div className="variant-input-row">
              <input
                type="text"
                value={variantInput}
                onChange={(e) => setVariantInput(e.target.value)}
                placeholder="Add custom variant"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddVariant(variantInput.trim());
                  }
                }}
              />
              <button
                type="button"
                className="btn"
                onClick={() => handleAddVariant(variantInput.trim())}
                disabled={!variantInput.trim()}
              >
                Add
              </button>
            </div>

            {/* Selected variants display */}
            {itemVariants.length > 0 && (
              <div className="selected-variants">
                {itemVariants.map(variant => (
                  <span key={variant} className="chip active">
                    {variant}
                    <button
                      type="button"
                      onClick={() => handleRemoveVariant(variant)}
                      className="chip-remove"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Quantity and Unit */}
          <div className="field-row">
            <div className="field" style={{ flex: 1 }}>
              <label htmlFor="quantity">Quantity</label>
              <input
                type="number"
                id="quantity"
                min="1"
                value={newItem.quantity}
                onChange={(e) => handleInputChange('quantity', parseInt(e.target.value) || 1)}
              />
            </div>

            <div className="field" style={{ flex: 1 }}>
              <label htmlFor="unit">Unit</label>
              <select
                id="unit"
                value={newItem.unit}
                onChange={(e) => handleInputChange('unit', e.target.value)}
              >
                {UNITS.map(unit => (
                  <option key={unit} value={unit}>{unit}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Add Button */}
          <button type="submit" className="btn primary full">
            Add to List
          </button>
        </form>
      </div>

      {/* Shopping List Display */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <h2>Shopping List ({items.length} items)</h2>
          {items.length > 0 && (
            <button className="link-button danger" onClick={handleClearAll}>
              Clear All
            </button>
          )}
        </div>

        {items.length > 0 ? (
          <div className="shopping-list">
            {items.map((item) => (
              <div key={item.id} className="shopping-list-item">
                <div className="item-info">
                  <span className="item-category">
                    {item.productName || item.category || 'Item'}
                  </span>
                  <span className="item-details">
                    {item.category && item.productName && (
                      <span className="item-brand">{item.category}</span>
                    )}
                    {item.brand && <span className="item-brand">{item.brand}</span>}
                    {(item.variants || []).length > 0 && (
                      <span className="item-variants">({(item.variants || []).join(', ')})</span>
                    )}
                  </span>
                  <span className="item-quantity">
                    {item.quantity} {item.unit}
                  </span>
                </div>
                <button
                  className="btn-icon"
                  onClick={() => handleRemoveItem(item.id)}
                  aria-label="Remove item"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted" style={{ textAlign: 'center', padding: '1rem' }}>
            No items added yet. Use the form above to add items.
          </p>
        )}
      </div>

      {/* Store Selection */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <h2>Select Stores</h2>
          <div className="store-actions">
            <button className="link-button" onClick={selectAllStores}>Select All</button>
            <span className="separator">|</span>
            <button className="link-button" onClick={deselectAllStores}>Deselect All</button>
          </div>
        </div>

        {stores.length > 0 ? (
          <div className="chip-group">
            {stores.map((store) => (
              <button
                key={store.id}
                className={`chip ${selectedStores.includes(store.name) ? 'active' : ''}`}
                onClick={() => toggleStore(store.name)}
                style={selectedStores.includes(store.name) ? {
                  backgroundColor: getStoreColor(store.name),
                  borderColor: getStoreColor(store.name)
                } : {}}
              >
                {store.name}
              </button>
            ))}
          </div>
        ) : (
          <p className="muted" style={{ textAlign: 'center', padding: '1rem' }}>
            Loading stores...
          </p>
        )}

        {selectedStores.length > 0 && (
          <p className="muted" style={{ marginTop: '0.75rem', fontSize: '0.85rem' }}>
            {selectedStores.length} store{selectedStores.length !== 1 ? 's' : ''} selected
          </p>
        )}
      </div>

      {/* Compare Button */}
      <div style={{ marginBottom: '1.5rem' }}>
        <button
          className="btn primary full"
          onClick={handleCompare}
          disabled={loading || items.length === 0 || selectedStores.length === 0}
          style={{ padding: '1rem', fontSize: '1.1rem' }}
        >
          {loading ? (
            <>
              <span className="spinner-small"></span>
              Comparing Prices...
            </>
          ) : (
            `Compare Prices (${items.length} item${items.length !== 1 ? 's' : ''} in ${selectedStores.length} store${selectedStores.length !== 1 ? 's' : ''})`
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
    </div>
  );
}

export default ComparisonPage;
