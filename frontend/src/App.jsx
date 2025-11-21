import React, { useEffect, useState } from 'react'
import { fetchSupermarkets, compareBasket } from './api'
import ShoppingList from './components/ShoppingList'
import SupermarketsList from './components/SupermarketsList'
import Results from './components/Results'

export default function App() {
  const [supermarkets, setSupermarkets] = useState([])
  const [selectedStores, setSelectedStores] = useState([])
  const [items, setItems] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    fetchSupermarkets()
      .then((list) => setSupermarkets(list))
      .catch((e) => setError(`Failed to load supermarkets: ${e.message}`))
      .finally(() => setLoading(false))
  }, [])

  async function onCompare() {
    setError(null)
    setResults(null)

    if (!items.length) {
      setError('Add at least one item.')
      return
    }
    if (!selectedStores.length) {
      setError('Select at least one supermarket.')
      return
    }

    setLoading(true)
    try {
      const resp = await compareBasket(items, selectedStores)
      setResults(resp)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app container">
      <h1>ShopSmart — Compare Prices</h1>

      <section className="panel">
        <ShoppingList items={items} setItems={setItems} />
        <SupermarketsList
          supermarkets={supermarkets}
          selected={selectedStores}
          setSelected={setSelectedStores}
          loading={loading}
        />
        <div className="actions">
          <button onClick={onCompare} className="btn primary">Compare</button>
          <button
            onClick={() => {
              setItems([])
              setSelectedStores([])
              setResults(null)
            }}
            className="btn"
          >
            Reset
          </button>
        </div>
        {loading && <div className="spinner" aria-live="polite">Loading…</div>}
        {error && <div className="error">{error}</div>}
      </section>

      <section className="panel">
        <Results results={results} />
      </section>
    </div>
  )
}
