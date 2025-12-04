import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { compareBasket, fetchSupermarkets, searchProducts, refreshPrices, getScraperStatus } from '../api'

export default function ShoppingPage() {
  const [supermarkets, setSupermarkets] = useState([])
  const [selectedStores, setSelectedStores] = useState([])
  const [items, setItems] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [comparing, setComparing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  // Autocomplete state
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1)
  const inputRef = useRef(null)
  const suggestionsRef = useRef(null)

  // Refresh prices state
  const [refreshing, setRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(null)

  // Load supermarkets on mount
  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError('')

    fetchSupermarkets()
      .then((list) => {
        if (!isMounted) return
        setSupermarkets(list || [])
        if (list && list.length > 0) {
          setSelectedStores(list.slice(0, 3).map((s) => s.name))
        }
      })
      .catch((e) => {
        if (!isMounted) return
        console.error('Failed to fetch supermarkets:', e)
        setError(`Unable to connect to server. Please check if the backend is running.`)
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  // Autocomplete: fetch suggestions when input changes
  useEffect(() => {
    const query = inputValue.trim()
    if (query.length < 2) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }

    const timeoutId = setTimeout(async () => {
      try {
        const results = await searchProducts(query, 8)
        setSuggestions(results || [])
        setShowSuggestions(results && results.length > 0)
        setSelectedSuggestionIndex(-1)
      } catch (e) {
        console.error('Failed to fetch suggestions:', e)
        setSuggestions([])
      }
    }, 200) // Debounce

    return () => clearTimeout(timeoutId)
  }, [inputValue])

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target) &&
        inputRef.current &&
        !inputRef.current.contains(e.target)
      ) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleStore = (name) => {
    setSelectedStores((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name],
    )
  }

  const addItem = (itemName = null) => {
    const val = (itemName || inputValue).trim()
    if (val && !items.some((i) => i.toLowerCase() === val.toLowerCase())) {
      setItems((prev) => [...prev, val])
    }
    setInputValue('')
    setShowSuggestions(false)
    setSuggestions([])
  }

  const removeItem = (item) => {
    setItems((prev) => prev.filter((i) => i !== item))
  }

  const handleKeyDown = (e) => {
    if (showSuggestions && suggestions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedSuggestionIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedSuggestionIndex((prev) => (prev > 0 ? prev - 1 : -1))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (selectedSuggestionIndex >= 0) {
          addItem(suggestions[selectedSuggestionIndex].name)
        } else {
          addItem()
        }
      } else if (e.key === 'Escape') {
        setShowSuggestions(false)
      }
    } else if (e.key === 'Enter') {
      e.preventDefault()
      addItem()
    }
  }

  const handleSuggestionClick = (suggestion) => {
    addItem(suggestion.name)
  }

  const handleRefreshPrices = async () => {
    setRefreshing(true)
    setError('')
    try {
      // Refresh prices for items in the list, or default items if empty
      const queries = items.length > 0 ? items : null
      await refreshPrices(queries)
      setLastRefresh(new Date())
    } catch (e) {
      console.error('Failed to refresh prices:', e)
      setError(`Price refresh failed: ${e.message}`)
    } finally {
      setRefreshing(false)
    }
  }

  const handleCompare = useCallback(async () => {
    if (!items.length) {
      setError('Please add at least one item to your shopping list.')
      return
    }
    if (!selectedStores.length) {
      setError('Please select at least one supermarket.')
      return
    }
    setError('')
    setComparing(true)
    try {
      const data = await compareBasket(items, selectedStores)
      setResults(data)
    } catch (e) {
      setError(`Comparison failed: ${e.message}`)
    } finally {
      setComparing(false)
    }
  }, [items, selectedStores])

  // Transform backend response to storeBreakdown format for display
  const storeBreakdown = useMemo(() => {
    if (!results) return null

    const breakdown = {}

    if (results.storeTotals) {
      for (const st of results.storeTotals) {
        breakdown[st.store] = { items: {}, total: st.total }
      }
    }

    if (results.items) {
      for (const item of results.items) {
        if (!breakdown[item.store]) {
          breakdown[item.store] = { items: {}, total: 0 }
        }
        breakdown[item.store].items[item.name] = item.price
      }
    }

    return Object.keys(breakdown).length > 0 ? breakdown : null
  }, [results])

  // Find cheapest store
  const cheapestStore = useMemo(() => {
    if (!results?.storeTotals?.length) return null

    const sorted = [...results.storeTotals]
      .filter((st) => st.total > 0)
      .sort((a, b) => a.total - b.total)

    if (sorted.length === 0) return null

    const best = sorted[0]
    return {
      store: best.store,
      total: best.total,
      items: storeBreakdown?.[best.store]?.items || {},
    }
  }, [results, storeBreakdown])

  return (
    <div className="shopping-page">
      {/* Refresh Banner */}
      {refreshing && (
        <div className="refresh-banner">
          <div className="spinner"></div>
          <span>Fetching latest prices from Mercadona...</span>
        </div>
      )}

      <section className="card shopping-input-card">
        <div className="card-header">
          <h2>Shopping list</h2>
          <button
            type="button"
            className="btn refresh-btn"
            onClick={handleRefreshPrices}
            disabled={refreshing}
            title="Fetch latest prices from supermarkets"
          >
            {refreshing ? (
              <>
                <span className="spinner-small"></span>
                Refreshing...
              </>
            ) : (
              <>🔄 Refresh Prices</>
            )}
          </button>
        </div>

        {lastRefresh && (
          <div className="last-refresh">
            ✓ Prices updated {lastRefresh.toLocaleTimeString()}
          </div>
        )}

        {error && <div className="alert error">{error}</div>}

        <div className="input-row autocomplete-container">
          <input
            ref={inputRef}
            type="text"
            placeholder="Type to search products (e.g. leche, huevos, pan)"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            autoComplete="off"
          />
          <button type="button" className="btn primary" onClick={() => addItem()}>
            Add
          </button>

          {/* Autocomplete Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <ul ref={suggestionsRef} className="suggestions-dropdown">
              {suggestions.map((suggestion, index) => (
                <li
                  key={suggestion.id}
                  className={`suggestion-item ${index === selectedSuggestionIndex ? 'selected' : ''}`}
                  onClick={() => handleSuggestionClick(suggestion)}
                  onMouseEnter={() => setSelectedSuggestionIndex(index)}
                >
                  {suggestion.name}
                </li>
              ))}
            </ul>
          )}
        </div>

        {items.length > 0 && (
          <ul className="item-list">
            {items.map((item) => (
              <li key={item} className="item-chip">
                {item}
                <button type="button" className="remove-btn" onClick={() => removeItem(item)}>
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card store-select-card">
        <h2>Select supermarkets</h2>
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <span>Loading supermarkets...</span>
          </div>
        ) : supermarkets.length > 0 ? (
          <div className="chip-group">
            {supermarkets.map((s) => (
              <button
                key={s.id ?? s.name}
                type="button"
                className={selectedStores.includes(s.name) ? 'chip active' : 'chip'}
                onClick={() => toggleStore(s.name)}
              >
                {s.name}
              </button>
            ))}
          </div>
        ) : (
          <div className="muted">
            No supermarkets available.
            <button
              type="button"
              className="link-button"
              onClick={() => window.location.reload()}
              style={{ marginLeft: '0.5rem' }}
            >
              Retry
            </button>
          </div>
        )}

        <button
          type="button"
          className="btn primary full"
          onClick={handleCompare}
          disabled={comparing || !items.length || !selectedStores.length}
        >
          {comparing ? (
            <>
              <span className="spinner-small"></span>
              Comparing...
            </>
          ) : (
            'Compare prices'
          )}
        </button>
      </section>

      {results && (
        <>
          {/* Price Comparison Table */}
          {results.priceComparison && results.priceComparison.length > 0 && (
            <section className="card results-card">
              <h2>📊 Price Comparison</h2>
              <p className="muted" style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
                Compare prices across all supermarkets
              </p>

              <div className="comparison-table-container">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>Item</th>
                      {selectedStores.map((store) => (
                        <th key={store}>{store}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.priceComparison.map((item) => (
                      <tr key={item.name}>
                        <td className="item-name">{item.name}</td>
                        {selectedStores.map((store) => {
                          const storePrice = item.prices.find((p) => p.store === store)
                          const isCheapest = store === item.cheapestStore
                          return (
                            <td
                              key={store}
                              className={isCheapest ? 'cheapest-cell' : ''}
                            >
                              {storePrice ? (
                                <>
                                  €{storePrice.price.toFixed(2)}
                                  {isCheapest && <span className="cheapest-badge">✓</span>}
                                </>
                              ) : (
                                '—'
                              )}
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                    {/* Totals row */}
                    <tr className="totals-row">
                      <td><strong>Total</strong></td>
                      {selectedStores.map((store) => {
                        const storeTotal = results.storeTotals?.find((st) => st.store === store)
                        const total = results.priceComparison.reduce((sum, item) => {
                          const p = item.prices.find((p) => p.store === store)
                          return sum + (p ? p.price : 0)
                        }, 0)
                        return (
                          <td key={store}>
                            <strong>€{total.toFixed(2)}</strong>
                          </td>
                        )
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Optimal Basket Section */}
          <section className="card results-card">
            <h2>🏆 Optimal Basket</h2>
            <p className="muted" style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
              Best store to buy each item
            </p>

            {cheapestStore && (
              <div className="best-deal">
                <div className="best-deal-icon">🏆</div>
                <div>
                  <div className="best-deal-title">Best deal: {cheapestStore.store}</div>
                  <div className="best-deal-total">€{cheapestStore.total.toFixed(2)}</div>
                </div>
              </div>
            )}

            {results.unmatched && results.unmatched.length > 0 && (
              <div className="alert" style={{ background: 'rgba(210, 153, 34, 0.15)', color: '#d29922' }}>
                <strong>Items not found:</strong> {results.unmatched.join(', ')}
                <div style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>
                  Try clicking "Refresh Prices" to search for these items online
                </div>
              </div>
            )}

            <div className="results-grid">
              {storeBreakdown &&
                Object.entries(storeBreakdown).map(([store, data]) => (
                  <div
                    key={store}
                    className={`store-card ${store === cheapestStore?.store ? 'cheapest' : ''}`}
                  >
                    <h3>{store}</h3>
                    <ul className="price-breakdown">
                      {data.items &&
                        Object.entries(data.items).map(([product, price]) => (
                          <li key={product}>
                            <span>{product}</span>
                            <span>{price != null ? `€${price.toFixed(2)}` : '—'}</span>
                          </li>
                        ))}
                    </ul>
                    <div className="store-total">
                      Total: <strong>€{data.total.toFixed(2)}</strong>
                    </div>
                  </div>
                ))}
            </div>

            {results.overallTotal != null && (
              <div className="overall-total">
                Optimal basket total: <strong>€{results.overallTotal.toFixed(2)}</strong>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}
