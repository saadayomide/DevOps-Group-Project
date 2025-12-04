import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { compareBasket, fetchSupermarkets, searchProducts } from '../api'

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
  // Shows ALL prices for ALL items at each store (not just optimal basket)
  const storeBreakdown = useMemo(() => {
    if (!results) return null

    const breakdown = {}

    // Initialize all selected stores
    selectedStores.forEach((store) => {
      breakdown[store] = { items: {}, total: 0 }
    })

    // Use priceComparison if available (shows all prices)
    if (results.priceComparison && results.priceComparison.length > 0) {
      results.priceComparison.forEach((item) => {
        item.prices.forEach((storePrice) => {
          if (selectedStores.includes(storePrice.store)) {
            if (!breakdown[storePrice.store]) {
              breakdown[storePrice.store] = { items: {}, total: 0 }
            }
            breakdown[storePrice.store].items[item.name] = storePrice.price
            breakdown[storePrice.store].total += storePrice.price
          }
        })
      })
    } else {
      // Fallback: use optimal basket data (only cheapest items)
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
    }

    return Object.keys(breakdown).length > 0 ? breakdown : null
  }, [results, selectedStores])

  // Find cheapest store (based on total if buying ALL items at that store)
  const cheapestStore = useMemo(() => {
    if (!storeBreakdown) return null

    // Calculate totals for all stores (buying all items at each store)
    const storeTotals = Object.entries(storeBreakdown).map(([store, data]) => ({
      store,
      total: data.total,
    }))

    const sorted = storeTotals.filter((st) => st.total > 0).sort((a, b) => a.total - b.total)

    if (sorted.length === 0) return null

    const best = sorted[0]
    return {
      store: best.store,
      total: best.total,
      items: storeBreakdown[best.store]?.items || {},
    }
  }, [storeBreakdown])

  return (
    <div className="shopping-page">
      <section className="card shopping-input-card">
        <h2>Shopping list</h2>
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
          <>
            <div className="chip-group">
              {supermarkets.map((s) => {
                const isLive = s.name === 'Mercadona' // Only Mercadona has live scraping
                return (
                  <button
                    key={s.id ?? s.name}
                    type="button"
                    className={selectedStores.includes(s.name) ? 'chip active' : 'chip'}
                    onClick={() => toggleStore(s.name)}
                    title={isLive ? 'Live prices (scraped)' : 'Static prices (seed data)'}
                  >
                    {s.name}
                    {isLive && <span className="live-badge">🟢</span>}
                  </button>
                )
              })}
            </div>
            <div className="muted" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
              🟢 = Live prices (scraped) | Others = Static prices (seed data)
            </div>
          </>
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
        <section className="card results-card">
          <h2>Price Comparison</h2>
          <p className="muted" style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
            Compare prices across all supermarkets. Green border indicates cheapest total.
          </p>

            {cheapestStore && (
              <div className="best-deal">
                <div className="best-deal-icon">🏆</div>
                <div>
                  <div className="best-deal-title">Cheapest total: {cheapestStore.store}</div>
                  <div className="best-deal-total">€{cheapestStore.total.toFixed(2)}</div>
                  <div style={{ fontSize: '0.85rem', marginTop: '0.25rem', opacity: 0.8 }}>
                    (Buy all items at {cheapestStore.store})
                  </div>
                </div>
              </div>
            )}

            {results.unmatched && results.unmatched.length > 0 && (
              <div className="alert" style={{ background: 'rgba(210, 153, 34, 0.15)', color: '#d29922' }}>
                <strong>Items not found:</strong> {results.unmatched.join(', ')}
                <div style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>
                  These items are not in the database. Try using product names from the autocomplete suggestions.
                </div>
              </div>
            )}

            <div className="results-grid">
              {storeBreakdown &&
                Object.entries(storeBreakdown).map(([store, data]) => {
                  // Find cheapest price for each item across all stores
                  const cheapestPrices = {}
                  if (results.priceComparison) {
                    results.priceComparison.forEach((item) => {
                      cheapestPrices[item.name] = item.cheapestPrice
                    })
                  }

                  return (
                    <div
                      key={store}
                      className={`store-card ${store === cheapestStore?.store ? 'cheapest' : ''}`}
                    >
                      <h3>{store}</h3>
                      <ul className="price-breakdown">
                        {data.items &&
                          Object.entries(data.items).map(([product, price]) => {
                            const isCheapest = results.priceComparison
                              ? results.priceComparison
                                  .find((item) => item.name === product)
                                  ?.cheapestStore === store
                              : false
                            return (
                              <li key={product} className={isCheapest ? 'cheapest-item' : ''}>
                                <span>{product}</span>
                                <span>
                                  {price != null ? (
                                    <>
                                      €{price.toFixed(2)}
                                      {isCheapest && <span className="cheapest-badge">✓</span>}
                                    </>
                                  ) : (
                                    '—'
                                  )}
                                </span>
                              </li>
                            )
                          })}
                      </ul>
                      <div className="store-total">
                        Total: <strong>€{data.total.toFixed(2)}</strong>
                      </div>
                    </div>
                  )
                })}
            </div>

            {results.overallTotal != null && cheapestStore && (
              <div className="overall-total">
                Best single-store total: <strong>€{results.overallTotal.toFixed(2)}</strong> at{' '}
                <strong>{cheapestStore.store}</strong>
              </div>
            )}
        </section>
      )}
    </div>
  )
}
