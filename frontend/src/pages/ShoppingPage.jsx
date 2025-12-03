import React, { useCallback, useEffect, useState } from 'react'
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
    setLoading(true)
    fetchSupermarkets()
      .then((list) => {
        setSupermarkets(list)
        setSelectedStores(list.slice(0, 3).map((s) => s.name))
      })
      .catch((e) => setError(`Failed to load supermarkets: ${e.message}`))
      .finally(() => setLoading(false))
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

  const cheapestStore =
    results?.storeBreakdown &&
    Object.entries(results.storeBreakdown).reduce(
      (best, [store, data]) => (!best || data.total < best.total ? { store, ...data } : best),
      null,
    )

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
        ) : (
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
            {!supermarkets.length && <span className="muted">No supermarkets available</span>}
          </div>
        )}

        <button
          type="button"
          className="btn primary full"
          onClick={handleCompare}
          disabled={comparing || !items.length}
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

          <div className="results-grid">
            {results.storeBreakdown &&
              Object.entries(results.storeBreakdown).map(([store, data]) => (
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
