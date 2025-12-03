import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { compareBasket, fetchSupermarkets } from '../api'

export default function ShoppingPage() {
  const [supermarkets, setSupermarkets] = useState([])
  const [selectedStores, setSelectedStores] = useState([])
  const [items, setItems] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [comparing, setComparing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError('')

    fetchSupermarkets()
      .then((list) => {
        if (!isMounted) return
        setSupermarkets(list || [])
        // Auto-select first 3 stores if available
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

  const toggleStore = (name) => {
    setSelectedStores((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name],
    )
  }

  const addItem = () => {
    const val = inputValue.trim()
    if (val && !items.includes(val)) {
      setItems((prev) => [...prev, val])
    }
    setInputValue('')
  }

  const removeItem = (item) => {
    setItems((prev) => prev.filter((i) => i !== item))
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addItem()
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

  // Transform backend response (items, storeTotals) to storeBreakdown format for display
  const storeBreakdown = useMemo(() => {
    if (!results) return null

    // Backend returns: { items: [{name, store, price}], storeTotals: [{store, total}], overallTotal, unmatched }
    const breakdown = {}

    // Initialize from storeTotals
    if (results.storeTotals) {
      for (const st of results.storeTotals) {
        breakdown[st.store] = { items: {}, total: st.total }
      }
    }

    // Add items to their stores
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

  // Find cheapest store from storeTotals
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
      <section className="card shopping-input-card">
        <h2>Shopping list</h2>
        {error && <div className="alert error">{error}</div>}

        <div className="input-row">
          <input
            type="text"
            placeholder="Enter product name (e.g. milk, bread, eggs)"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button type="button" className="btn primary" onClick={addItem}>
            Add
          </button>
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
          <div className="muted">Loading supermarkets...</div>
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
          {comparing ? 'Comparing...' : 'Compare prices'}
        </button>
      </section>

      {results && (
        <section className="card results-card">
          <h2>Results</h2>

          {cheapestStore && (
            <div className="best-deal">
              <div className="best-deal-icon">🏆</div>
              <div>
                <div className="best-deal-title">Best deal: {cheapestStore.store}</div>
                <div className="best-deal-total">€{cheapestStore.total.toFixed(2)}</div>
              </div>
            </div>
          )}

          {/* Show unmatched items if any */}
          {results.unmatched && results.unmatched.length > 0 && (
            <div className="alert" style={{ background: 'rgba(210, 153, 34, 0.15)', color: '#d29922' }}>
              <strong>Items not found:</strong> {results.unmatched.join(', ')}
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
      )}
    </div>
  )
}
